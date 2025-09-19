"""XNAT Custom Forms Data Backup Extractor.

This module extracts custom form data from XNAT projects and saves it to
Excel files with backup functionality. It supports multiple projects and
implements a structured folder hierarchy with date-time based naming.
"""

import json
import logging
import getpass
import os
import time
import sys
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import pytz
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import typer
import xnat

# Melbourne timezone for consistent logging and file naming
melbtz = pytz.timezone('Australia/Melbourne')

# Global cache for connection reuse
_form_definitions_cache = {}

def get_optimized_session() -> requests.Session:
    """Get a reusable HTTP session with connection pooling and retries."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def logout_all_sessions(server: str, username: str, password: str) -> bool:
    """Log out all active XNAT sessions for the user.
    
    Args:
        server: XNAT server URL with trailing slash
        username: XNAT username
        password: XNAT password
        
    Returns:
        True if logout successful, False otherwise
    """
    # Ensure server ends with a slash
    if not server.endswith("/"):
        server += "/"
    
    logout_url = f"{server}xapi/users/active/{username}"
    
    try:
        response = requests.delete(logout_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            logging.error("Authentication failed during logout. Please check your credentials.")
            return False
        elif response.status_code == 403:
            logging.error("Access forbidden during logout. User may not have sufficient permissions.")
            return False
        elif response.status_code == 404:
            logging.warning("Logout endpoint not found. This might be an older XNAT version.")
            return True  # Assume success for older versions
        else:
            logging.error(
                f"Logout failed. HTTP Status: {response.status_code}, "
                f"Response: {response.text}"
            )
            return False
    except requests.exceptions.Timeout:
        logging.error("Logout request timed out. Server may be unresponsive.")
        return False
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to XNAT server during logout. Check server URL and network connection.")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during logout: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during logout: {e}")
        return False


@lru_cache(maxsize=128)
def extract_form_title_from_contents(contents_str: str) -> str:
    """Extract the title from form contents JSON string.
    
    Args:
        contents_str: JSON string containing form contents
        
    Returns:
        Form title or "Untitled Form" if not found
    """
    try:
        contents = json.loads(contents_str)
        return contents.get("title", "Untitled Form")
    except (json.JSONDecodeError, KeyError, TypeError):
        return "Untitled Form"


def is_form_applicable_to_project(form: Dict, project_id: str) -> bool:
    """Check if a form is applicable to the specific project.
    
    Args:
        form: Form definition dictionary
        project_id: XNAT project ID
        
    Returns:
        True if form applies to project, False otherwise
    """
    applies_to_list = form.get("appliesToList", [])
    
    # If no appliesToList is present, assume the form applies to all
    # projects
    if not applies_to_list:
        logging.info(f"Form {form.get('formUUID', 'Unknown')} has no "
                    f"appliesToList - assuming it applies to all projects")
        return True
    
    for applies_to in applies_to_list:
        entity_id = applies_to.get("entityId", "")
        status = applies_to.get("status", "")
        
        # Check if this entry is for our specific project
        if entity_id == project_id:
            if status == "enabled":
                return True
            elif status == "optedout":
                return False
        
        # Check if this is a site-wide setting (entityId = "Site")
        elif entity_id == "Site":
            site_status = status
            # Continue checking for project-specific overrides
            continue
    
    # If we reach here, check if there was a site-wide setting
    # and no project-specific override was found
    for applies_to in applies_to_list:
        if applies_to.get("entityId") == "Site":
            site_status = applies_to.get("status", "")
            if site_status == "enabled":
                return True
            elif site_status == "optedout":
                return False
    
    # Default: if no clear status found, don't include the form
    return False


@lru_cache(maxsize=64)
def get_form_metadata(form_uuid: str, contents_str: str, path: str) -> Tuple[str, Dict[str, Dict], str, Optional[str], bool, bool]:
    """Pre-process and cache form metadata to avoid redundant parsing.
    
    Args:
        form_uuid: Form UUID
        contents_str: JSON string containing form contents
        path: Form path
        
    Returns:
        Tuple of (form_title, form_fields, level, target_session_type, is_subject_form, is_session_form)
    """
    try:
        # Parse form contents
        contents = json.loads(contents_str)
        form_title = contents.get("title", "Untitled Form")
        components = contents.get("components", [])
        
        # Extract fields
        form_fields = extract_fields(components)
        
        # Determine form level and applicability
        is_subject_form = "xnat:subjectData" in path
        target_session_type = get_form_session_type_from_path(path) if not is_subject_form else None
        is_session_form = target_session_type is not None
        
        # Determine level string for display
        if is_subject_form:
            level = "Subject"
        elif target_session_type:
            level = f"Session ({target_session_type})"
        else:
            level = "Unknown"
            
        return form_title, form_fields, level, target_session_type, is_subject_form, is_session_form
        
    except Exception as e:
        logging.error(f"Error processing form metadata for {form_uuid}: {e}")
        return "Untitled Form", {}, "Unknown", None, False, False


@lru_cache(maxsize=32)
def get_form_session_type_from_path(path: str) -> Optional[str]:
    """Extract session type from form path (cached version).
    
    Args:
        path: Form path
        
    Returns:
        Session type string or None if not applicable
    """
    session_type_mapping = {
        "xnat:mrSessionData": "xnat:mrSessionData",
        "xnat:ctSessionData": "xnat:ctSessionData", 
        "xnat:petSessionData": "xnat:petSessionData",
        "xnat:usSessionData": "xnat:usSessionData",
        "xnat:mgSessionData": "xnat:mgSessionData",
        "xnat:crSessionData": "xnat:crSessionData",
        "xnat:dxSessionData": "xnat:dxSessionData",
        "xnat:nmSessionData": "xnat:nmSessionData",
        "xnat:opSessionData": "xnat:opSessionData",
        "xnat:scSessionData": "xnat:scSessionData",
        "xnat:srSessionData": "xnat:srSessionData",
        "xnat:rtSessionData": "xnat:rtSessionData",
        "xnat:eegSessionData": "xnat:eegSessionData",
        "xnat:hdEegSessionData": "xnat:hdEegSessionData",
        "xnat:ecgSessionData": "xnat:ecgSessionData",
        "xnat:emgSessionData": "xnat:emgSessionData"
    }
    
    for session_data_type, session_type in session_type_mapping.items():
        if session_data_type in path:
            return session_type
    
    return None


def extract_fields(components: List[Dict],
                  processed_keys: Optional[Set] = None) -> Dict[str, Dict]:
    """Recursively extract fields from all components.
    
    Extracts fields from panels, columns, fieldsets and other nested
    components.
    
    Args:
        components: List of form component dictionaries
        processed_keys: Set of already processed field keys to avoid
                       duplicates
                       
    Returns:
        Dictionary mapping field keys to field information
    """
    if processed_keys is None:
        processed_keys = set()

    fields = {}
    for component in components:
        field_type = component.get("type")
        key = component.get("key")

        if field_type in ['columns', 'panel', 'fieldset']:
            nested_lists = (component.get("columns", [])
                           if field_type == "columns" else [component])
            for item in nested_lists:
                nested_components = (item.get("components", [])
                                   if field_type == "columns"
                                   else component.get("components", []))
                nested_fields = extract_fields(nested_components,
                                             processed_keys)
                fields.update(nested_fields)
        elif "components" in component:
            nested_fields = extract_fields(component.get("components", []),
                                         processed_keys)
            fields.update(nested_fields)
        elif key:
            if key in processed_keys:
                logging.warning(f"Duplicate field key detected: {key}. "
                               f"Skipping.")
                continue
            processed_keys.add(key)

            comment_parts = []
            if field_type:
                comment_parts.append(f"type: {field_type}")
            options = component.get("data", {}).get("values", [])
            if options:
                comment_parts.append(
                    f"options: {[opt['label'] for opt in options]}")
            comment = " | ".join(comment_parts)
            fields[key] = {"value": None, "comment": comment}

    return fields


def fetch_form_definitions(server: str, username: str, password: str,
                          project_id: str, session: requests.Session = None) -> List[Dict]:
    """Fetch form definitions from XNAT and filter by project applicability.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: XNAT project ID
        session: Optional HTTP session for connection reuse
        
    Returns:
        List of form definitions applicable to the project
    """
    if session is None:
        session = get_optimized_session()
    
    api_url = f"{server}xapi/customforms"
    
    try:
        response = session.get(api_url, auth=(username, password), timeout=60)
        
        if response.status_code == 200:
            try:
                all_forms = response.json()
                if not isinstance(all_forms, list):
                    logging.error("Unexpected response format: expected list of forms")
                    return []
                
                # Deduplicate forms based on formUUID
                unique_forms = {form["formUUID"]: form for form in all_forms if "formUUID" in form}.values()
                
                # Filter forms that are applicable to this project
                applicable_forms = []
                for form in unique_forms:
                    if is_form_applicable_to_project(form, project_id):
                        applicable_forms.append(form)
                
                return applicable_forms
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse form definitions JSON: {e}")
                return []
            except KeyError as e:
                logging.error(f"Form definition missing required field {e}")
                return []
                
        elif response.status_code == 401:
            logging.error("Authentication failed when fetching forms. Please check your credentials.")
            sys.exit(1)
        elif response.status_code == 403:
            logging.error("Access forbidden when fetching forms. User may not have sufficient permissions.")
            sys.exit(1)
        elif response.status_code == 404:
            logging.error("Custom forms endpoint not found. This XNAT instance may not support custom forms.")
            sys.exit(1)
        else:
            logging.error(f"Failed to fetch form definitions. Status code: "
                         f"{response.status_code}, Response: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        logging.error("Request timed out when fetching form definitions. Server may be slow or unresponsive.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to XNAT server when fetching forms. Check server URL and network connection.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error when fetching form definitions: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error when fetching form definitions: {e}")
        sys.exit(1)


def get_all_project_data_optimized(server: str, username: str, password: str,
                                   project_id: str, session: requests.Session = None) -> Dict[str, Dict[str, Any]]:
    """Fetch ALL subjects and sessions for a project using subject-specific API calls.
    
    This uses the approach: /data/projects/{project_id}/subjects/{subject_id}/experiments
    for each subject, which should provide accurate session relationships.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: XNAT project ID
        session: Optional HTTP session for connection reuse
        
    Returns:
        Dictionary mapping subject IDs to subject information including sessions
    """
    if session is None:
        session = get_optimized_session()
        
    # First get all subjects (using the proven working endpoint)
    subjects_url = f"{server}data/projects/{project_id}/subjects"
    
    try:
        logging.info(f"Fetching all subjects for project: {project_id}")
        subjects_response = session.get(subjects_url, auth=(username, password),
                                      params={'format': 'json'}, timeout=120)
        
        if subjects_response.status_code != 200:
            if subjects_response.status_code == 401:
                logging.error("Authentication failed when fetching subjects. Please check your credentials.")
                sys.exit(1)
            elif subjects_response.status_code == 403:
                logging.error("Access forbidden when fetching subjects. User may not have access to this project.")
                sys.exit(1)
            elif subjects_response.status_code == 404:
                logging.error(f"Project '{project_id}' not found. Please verify the project ID.")
                sys.exit(1)
            else:
                logging.error(f"Failed to fetch subjects. Status code: {subjects_response.status_code}")
                sys.exit(1)
        
        subjects_data = subjects_response.json()
        subjects = subjects_data.get('ResultSet', {}).get('Result', [])
        
        if not subjects:
            logging.warning(f"No subjects found in project {project_id}")
            return {}
        
        # Initialize project data with subjects
        project_data = {}
        for subject in subjects:
            subject_id = subject.get('ID')
            subject_label = subject.get('label', subject_id)
            if subject_id:
                project_data[subject_id] = {
                    'label': subject_label,
                    'sessions': {}
                }
        
        logging.info(f"Found {len(project_data)} subjects, now fetching sessions for each subject...")
        
        # Now get experiments for each subject using subject-specific API calls
        total_sessions = 0
        subjects_with_sessions = 0
        
        # Use ThreadPoolExecutor for parallel subject processing but limit workers to avoid overwhelming XNAT
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Create futures for each subject
            future_to_subject = {}
            for subject_id in project_data.keys():
                experiments_url = f"{server}data/projects/{project_id}/subjects/{subject_id}/experiments"
                future = executor.submit(
                    fetch_subject_experiments, 
                    session, experiments_url, username, password, subject_id
                )
                future_to_subject[future] = subject_id
            
            # Process completed futures
            for future in as_completed(future_to_subject):
                subject_id = future_to_subject[future]
                try:
                    subject_sessions = future.result()
                    if subject_sessions:
                        project_data[subject_id]['sessions'] = subject_sessions
                        total_sessions += len(subject_sessions)
                        subjects_with_sessions += 1
                except Exception as e:
                    logging.warning(f"Error fetching sessions for subject {subject_id}: {e}")
        
        logging.info(f"Fetched {len(project_data)} subjects with {total_sessions} sessions "
                    f"({subjects_with_sessions} subjects have sessions)")
        
        return project_data
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse subjects JSON response: {e}")
        return {}
    except requests.exceptions.Timeout:
        logging.error("Request timed out when fetching project data. Server may be slow or unresponsive.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to XNAT server when fetching project data. Check server URL and network connection.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error when fetching project data: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error when fetching project data: {e}")
        sys.exit(1)


def fetch_subject_experiments(session: requests.Session, experiments_url: str, 
                            username: str, password: str, subject_id: str) -> Dict[str, Dict[str, Any]]:
    """Fetch experiments for a single subject.
    
    Args:
        session: HTTP session for connection reuse
        experiments_url: URL to fetch experiments for subject
        username: XNAT username
        password: XNAT password 
        subject_id: Subject ID for logging
        
    Returns:
        Dictionary mapping session IDs to session information
    """
    try:
        response = session.get(experiments_url, auth=(username, password),
                             params={'format': 'json'}, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            experiments = data.get('ResultSet', {}).get('Result', [])
            
            subject_sessions = {}
            for exp in experiments:
                session_id = exp.get('ID')
                session_label = exp.get('label', session_id)
                session_type = exp.get('xsiType')
                
                if session_id:
                    subject_sessions[session_id] = {
                        'label': session_label,
                        'type': session_type
                    }
            
            return subject_sessions
        elif response.status_code == 404:
            # No experiments for this subject
            return {}
        else:
            logging.debug(f"Failed to fetch experiments for subject {subject_id}: "
                        f"status {response.status_code}")
            return {}
            
    except Exception as e:
        logging.debug(f"Error fetching experiments for subject {subject_id}: {e}")
        return {}


def test_xnat_connection(server: str, username: str, password: str) -> bool:
    """Test XNAT connection and credentials.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        
    Returns:
        True if connection successful, False otherwise
    """
    # Ensure server has trailing slash for proper URL construction
    if not server.endswith('/'):
        server = server + '/'
    test_url = f"{server}data/projects"
    
    try:
        logging.info("Testing XNAT connection and credentials...")
        response = requests.get(test_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            logging.info("Successfully connected to XNAT")
            return True
        elif response.status_code == 401:
            logging.error("Authentication failed. Please check your username and password.")
            sys.exit(1)
        elif response.status_code == 403:
            logging.error("Access forbidden. User may not have sufficient permissions.")
            sys.exit(1)
        else:
            logging.error(f"Connection test failed. Status code: {response.status_code}")
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        logging.error("Connection test timed out. Server may be unresponsive.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to XNAT server. Check server URL and network connection.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during connection test: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error during connection test: {e}")
        sys.exit(1)


def fetch_populated_data_for_entity(server: str, username: str,
                                   password: str, project_id: str,
                                   subject_id: str, session_id: str = None,
                                   uuid: str = None, 
                                   session: requests.Session = None,
                                   max_retries: int = 2) -> Dict:
    """Fetch populated data for a specific subject or session.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: XNAT project ID
        subject_id: Subject ID
        session_id: Session ID (optional, for session-level forms)
        uuid: Form UUID (optional, for specific form)
        session: Optional HTTP session for connection reuse
        max_retries: Maximum number of retry attempts for auth failures
        
    Returns:
        Dictionary containing populated form data
    """
    if session is None:
        session = get_optimized_session()
        
    if session_id:
        api_url = (f"{server}xapi/custom-fields/projects/{project_id}/"
                  f"subjects/{subject_id}/experiments/{session_id}/fields")
    else:
        api_url = (f"{server}xapi/custom-fields/projects/{project_id}/"
                  f"subjects/{subject_id}/fields")
    
    if uuid:
        api_url = f"{api_url}/{uuid}"
    
    for attempt in range(max_retries + 1):
        try:
            response = session.get(api_url, auth=(username, password), timeout=30)
            if response.status_code == 200:
                data = response.json()
                if uuid and isinstance(data, dict):
                    return {uuid: data}
                return data
            elif response.status_code == 404:
                # No custom form data for this entity
                return {}
            elif response.status_code == 401 and attempt < max_retries:
                # Authentication failed, try with fresh session
                logging.debug(f"Auth failed for {api_url}, retrying with fresh session (attempt {attempt + 1})")
                session = get_optimized_session()
                continue
            else:
                logging.warning(f"Failed to fetch data from {api_url}. "
                               f"Status code: {response.status_code}")
                return {}
        except Exception as e:
            if attempt < max_retries:
                logging.debug(f"Error fetching data (attempt {attempt + 1}): {e}")
                session = get_optimized_session()
                continue
            else:
                logging.error(f"Error fetching populated data after {max_retries + 1} attempts: {e}")
                return {}
    
    return {}


def fetch_populated_data_batch(server: str, username: str, password: str,
                             project_id: str, entities: List[Dict],
                             form_uuid: str, session: requests.Session) -> Dict:
    """Fetch populated data for multiple entities in parallel.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: XNAT project ID
        entities: List of entity dictionaries with subject_id, session_id, etc.
        form_uuid: Form UUID to fetch
        session: HTTP session for connection reuse
        
    Returns:
        Dictionary mapping entity keys to populated data
    """
    results = {}
    
    def fetch_single_entity(entity):
        # Create a fresh session for each thread to avoid auth conflicts
        thread_session = get_optimized_session()
        try:
            data = fetch_populated_data_for_entity(
                server, username, password, project_id,
                entity['subject_id'], entity.get('session_id'),
                form_uuid, thread_session
            )
            return entity['key'], data
        except Exception as e:
            logging.warning(f"Error fetching data for {entity['key']}: {e}")
            return entity['key'], {}
    
    # Use ThreadPoolExecutor for parallel requests with reduced workers to avoid auth conflicts
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_entity = {executor.submit(fetch_single_entity, entity): entity 
                           for entity in entities}
        
        for future in as_completed(future_to_entity):
            entity_key, data = future.result()
            results[entity_key] = data
    
    return results


def collect_form_data_optimized(server: str, username: str, password: str,
                                project_id: str, project_data: Dict,
                                form_metadata: Dict, session: requests.Session = None) -> Dict[str, List[Dict]]:
    """Optimized form data collection using pre-processed metadata.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: XNAT project ID
        project_data: Dictionary containing project subjects and sessions
        form_metadata: Pre-processed form metadata dictionary
        session: Optional HTTP session for connection reuse
        
    Returns:
        Dictionary mapping form UUIDs to lists of form data records
    """
    if session is None:
        session = get_optimized_session()
        
    form_data_collection = {}
    
    for form_uuid, metadata in form_metadata.items():
        form_title = metadata['title']
        form_fields = metadata['fields']
        field_keys = metadata['field_keys']
        is_subject_form = metadata['is_subject_form']
        is_session_form = metadata['is_session_form']
        target_session_type = metadata['target_session_type']
        
        logging.debug(f"Processing form: {form_title} ({form_uuid}) for batch")
        
        if form_uuid not in form_data_collection:
            form_data_collection[form_uuid] = []
        
        # Prepare entities for batch processing
        subject_entities = []
        session_entities = []
        
        for subject_id, subject_info in project_data.items():
            subject_label = subject_info['label']
            
            # Collect subject entities
            if is_subject_form:
                subject_entities.append({
                    'key': f"{subject_id}",
                    'subject_id': subject_id,
                    'subject_label': subject_label
                })
            
            # Collect session entities
            if is_session_form:
                for session_id, session_info in subject_info['sessions'].items():
                    session_label = session_info['label']
                    session_type = session_info.get('type')
                    
                    # Only process sessions that match the form's target session type
                    if target_session_type and session_type != target_session_type:
                        continue
                    
                    session_entities.append({
                        'key': f"{subject_id}_{session_id}",
                        'subject_id': subject_id,
                        'session_id': session_id,
                        'subject_label': subject_label,
                        'session_label': session_label,
                        'session_type': session_type
                    })
        
        # Batch fetch populated data
        all_populated_data = {}
        if subject_entities:
            subject_data = fetch_populated_data_batch(
                server, username, password, project_id, subject_entities, form_uuid, session
            )
            all_populated_data.update(subject_data)
        
        if session_entities:
            session_data = fetch_populated_data_batch(
                server, username, password, project_id, session_entities, form_uuid, session
            )
            all_populated_data.update(session_data)
        
        # Process results for subject-level forms
        for entity in subject_entities:
            populated_data = all_populated_data.get(entity['key'], {})
            row_data = {
                'project_id': project_id,
                'uuid': form_uuid,
                'subject_label': entity['subject_label']
            }
            
            if form_uuid in populated_data:
                form_values = populated_data[form_uuid]
                for field_key in field_keys:
                    row_data[field_key] = form_values.get(field_key, None)
            else:
                for field_key in field_keys:
                    row_data[field_key] = None
            
            form_data_collection[form_uuid].append(row_data)
        
        # Process results for session-level forms
        for entity in session_entities:
            populated_data = all_populated_data.get(entity['key'], {})
            row_data = {
                'project_id': project_id,
                'uuid': form_uuid,
                'subject_label': entity['subject_label'],
                'session_label': entity['session_label'],
                'session_type': entity['session_type']
            }
            
            if form_uuid in populated_data:
                form_values = populated_data[form_uuid]
                for field_key in field_keys:
                    row_data[field_key] = form_values.get(field_key, None)
            else:
                for field_key in field_keys:
                    row_data[field_key] = None
            
            form_data_collection[form_uuid].append(row_data)
    
    return form_data_collection


def setup_backup_folder_structure(base_path: str, server_name: str, project_id: str) -> Tuple[str, str]:
    """Setup folder structure for backup: base_path/server_name/project_id/excel_outputs and logs
    
    Args:
        base_path: Base directory path
        server_name: Server name for folder organization
        project_id: Project ID for folder organization
        
    Returns:
        Tuple of (excel_folder_path, logs_folder_path)
    """
    # Create server folder
    server_folder = os.path.join(base_path, server_name)
    os.makedirs(server_folder, exist_ok=True)
    
    # Create project folder
    project_folder = os.path.join(server_folder, project_id)
    os.makedirs(project_folder, exist_ok=True)
    
    # Create excel_outputs and logs folders
    excel_folder = os.path.join(project_folder, "excel_outputs")
    logs_folder = os.path.join(project_folder, "logs")
    
    os.makedirs(excel_folder, exist_ok=True)
    os.makedirs(logs_folder, exist_ok=True)
    
    return excel_folder, logs_folder


def generate_backup_filename(form_title: str, form_uuid: str) -> str:
    """Generate backup filename with date-time stamp in ddmmyyThhmmss format.
    
    Args:
        form_title: Form title for the filename
        form_uuid: Form UUID for uniqueness
        
    Returns:
        Filename with timestamp
    """
    # Get current time in Melbourne timezone
    now = datetime.now(melbtz)
    
    # Format: ddmmyyThhmmss (04012025T115026)
    timestamp = now.strftime('%d%m%yT%H%M%S')
    
    # Clean form title for filename
    safe_title = "".join(
        c if c.isalnum() or c in (' ', '-', '_') else ''
        for c in form_title
    )
    safe_title = safe_title.replace(' ', '_')
    
    # Create filename with timestamp
    filename = f"{safe_title}_{form_uuid[:8]}_{timestamp}.xlsx"
    
    return filename


def save_form_data_to_backup_excel(form_data_collection: Dict[str, List[Dict]],
                                  form_definitions: List[Dict],
                                  excel_folder: str) -> None:
    """Save each form's data to separate Excel files with backup naming.
    
    Args:
        form_data_collection: Dictionary mapping form UUIDs to data records
        form_definitions: List of form definition dictionaries
        excel_folder: Path to excel outputs folder
    """
    # Create form UUID to title mapping
    uuid_to_title = {}
    for form in form_definitions:
        form_uuid = form["formUUID"]
        form_title = extract_form_title_from_contents(
            form.get("contents", ""))
        uuid_to_title[form_uuid] = form_title
    
    for form_uuid, data_rows in form_data_collection.items():
        if not data_rows:
            logging.warning(f"No data found for form {form_uuid}")
            continue
        
        # Create DataFrame
        df = pd.DataFrame(data_rows)
        
        # Generate backup filename with timestamp
        form_title = uuid_to_title.get(form_uuid, "Unknown_Form")
        filename = generate_backup_filename(form_title, form_uuid)
        filepath = os.path.join(excel_folder, filename)
        
        # Save to Excel
        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            logging.info(f"Saved {len(data_rows)} records to {filepath}")
        except Exception as e:
            logging.error(f"Error saving Excel file for form {form_uuid}: {e}")


def setup_logging(logs_folder: str, project_id: str) -> None:
    """Setup logging configuration for backup process.
    
    Args:
        logs_folder: Path to logs folder
        project_id: Project ID for log filename
    """
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    log_file = os.path.join(
        logs_folder,
        f"{datetime.now(melbtz).strftime('%Y-%m-%d_%H-%M-%S')}_{project_id}_backup_get.log"
    )
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
    
    # Set console handler to INFO level only
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.INFO)


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading configuration file: {e}")
        sys.exit(1)


def extract_server_name(server_url: str) -> str:
    """Extract server name from URL for folder naming.
    
    Args:
        server_url: Full server URL
        
    Returns:
        Server name suitable for folder naming
    """
    # Remove protocol
    server_name = server_url.replace('https://', '').replace('http://', '')
    
    # Remove trailing slash and paths
    server_name = server_name.split('/')[0]
    
    # Replace invalid characters for folder names
    server_name = "".join(c if c.isalnum() or c in ('-', '_', '.') else '_' for c in server_name)
    
    return server_name


def process_single_project(server: str, username: str, password: str,
                          project_id: str, base_output_path: str,
                          batch_size: int = 10, session_delay: int = 2) -> None:
    """Process a single project for backup extraction.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: XNAT project ID to process
        base_output_path: Base path for outputs
        batch_size: Number of subjects to process per batch
        session_delay: Delay in seconds between batches
    """
    # Extract server name for folder structure
    server_name = extract_server_name(server)
    
    # Setup folder structure
    excel_folder, logs_folder = setup_backup_folder_structure(
        base_output_path, server_name, project_id
    )
    
    # Setup logging for this project
    setup_logging(logs_folder, project_id)
    
    logging.info(f"Starting backup extraction for project: {project_id}")
    logging.info(f"Server: {server}")
    logging.info(f"Output folder: {excel_folder}")
    logging.info(f"Logs folder: {logs_folder}")
    
    try:
        # Handle server URL format
        if not server.startswith(('http://', 'https://')):
            server = 'https://' + server
        if not server.endswith('/'):
            server += '/'

        if not test_xnat_connection(server, username, password):
            logging.error("Failed to establish connection to XNAT. Please check your server URL and credentials.")
            return

        # Logout all existing sessions at the start
        logout_all_sessions(server, username, password)

        # Fetch all form definitions and filter by project applicability
        cache_key = f"{server}_{project_id}_{username}"
        if cache_key in _form_definitions_cache:
            logging.debug("Using cached form definitions")
            form_definitions = _form_definitions_cache[cache_key]
        else:
            initial_session = get_optimized_session()
            form_definitions = fetch_form_definitions(
                server, username, password, project_id, initial_session
            )
            _form_definitions_cache[cache_key] = form_definitions

        if not form_definitions:
            logging.error(
                f"No form definitions found that are applicable to project {project_id}. Skipping."
            )
            return

        logging.info(f"Found {len(form_definitions)} applicable forms for project {project_id}")

        # Fetch ALL project data (subjects + sessions) at once
        logging.info("Fetching all project data (subjects and sessions)...")
        initial_session = get_optimized_session()
        all_project_data = get_all_project_data_optimized(
            server, username, password, project_id, initial_session
        )

        if not all_project_data:
            logging.error(f"No subjects found in project {project_id}. Skipping.")
            return

        # Get subject IDs for batch processing
        all_subject_ids = list(all_project_data.keys())
        total_sessions = sum(len(subj['sessions']) for subj in all_project_data.values())
        
        logging.info(f"Found {len(all_subject_ids)} subjects with {total_sessions} sessions")

        # Pre-process all form metadata once
        logging.info("Pre-processing form metadata...")
        form_metadata = {}
        for form in form_definitions:
            form_uuid = form["formUUID"]
            contents_str = form.get("contents", "{}")
            path = form.get("path", "")

            form_title, form_fields, level, target_session_type, is_subject_form, is_session_form = get_form_metadata(
                form_uuid, contents_str, path
            )

            form_metadata[form_uuid] = {
                'title': form_title,
                'fields': form_fields,
                'level': level,
                'target_session_type': target_session_type,
                'is_subject_form': is_subject_form,
                'is_session_form': is_session_form,
                'field_keys': list(form_fields.keys())
            }

        # Initialize form data collection
        master_form_data_collection = {
            form["formUUID"]: [] for form in form_definitions
        }

        # Process subjects in batches
        total_batches = (len(all_subject_ids) + batch_size - 1) // batch_size
        logging.info(f"Processing {len(all_subject_ids)} subjects in {total_batches} batches")

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(all_subject_ids))
            subject_batch = all_subject_ids[start_idx:end_idx]

            logging.info(f"Processing batch {batch_num + 1}/{total_batches}: subjects {start_idx + 1}-{end_idx}")

            try:
                # Use pre-fetched data
                batch_project_data = {
                    subject_id: all_project_data[subject_id] 
                    for subject_id in subject_batch
                    if subject_id in all_project_data
                }

                if not batch_project_data:
                    logging.warning(f"No data found for batch {batch_num + 1}")
                    continue

                # Create fresh session for this batch
                batch_session = get_optimized_session()

                # Use pre-processed form metadata
                batch_form_data = collect_form_data_optimized(
                    server, username, password, project_id, 
                    batch_project_data, form_metadata, batch_session
                )

                # Merge batch data into master collection
                for form_uuid, data_rows in batch_form_data.items():
                    master_form_data_collection[form_uuid].extend(data_rows)

                logging.info(f"Completed batch {batch_num + 1}/{total_batches}")

                # Close all active sessions after each batch
                logout_success = logout_all_sessions(server, username, password)
                if not logout_success:
                    logging.warning(f"Failed to logout sessions after batch {batch_num + 1}")

                # Add delay between batches if not the last batch
                if batch_num < total_batches - 1:
                    logging.info(f"Waiting {session_delay} seconds before next batch...")
                    time.sleep(session_delay)

            except Exception as e:
                logging.error(f"Error processing batch {batch_num + 1}: {e}")
                try:
                    logout_all_sessions(server, username, password)
                except Exception:
                    logging.error(f"Failed to logout sessions after batch {batch_num + 1} error")
                continue

        # Save all collected data to Excel files with backup naming
        logging.info("Saving all collected data to Excel files...")
        save_form_data_to_backup_excel(master_form_data_collection, form_definitions, excel_folder)

        # Log final statistics
        total_records = sum(len(data) for data in master_form_data_collection.values())
        logging.info(f"Total records collected for project {project_id}: {total_records}")

        for form in form_definitions:
            form_uuid = form["formUUID"]
            form_title = extract_form_title_from_contents(form.get("contents", ""))
            record_count = len(master_form_data_collection.get(form_uuid, []))
            logging.info(f"  {form_title}: {record_count} records")

        # Final logout of all sessions
        logout_all_sessions(server, username, password)
        logging.info(f"Backup extraction completed successfully for project: {project_id}")

    except Exception as e:
        logging.error(f"An error occurred processing project {project_id}: {e}")
        try:
            logout_all_sessions(server, username, password)
        except Exception:
            logging.error("Failed to logout sessions during error cleanup")


app = typer.Typer(help="XNAT Custom Forms Backup Extractor")


@app.command()
def backup_extract(
    server: Optional[str] = typer.Option(
        None,
        "--server",
        "-x", 
        help="XNAT server URL (e.g., https://server.com/xnat)"
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username", 
        "-u",
        help="XNAT username for authentication"
    ),
    config: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (JSON format)"
    ),
    output_dir: str = typer.Option(
        ".",
        "--output-dir",
        "-o",
        help="Base output directory for backup files"
    ),
    batch_size: int = typer.Option(
        10,
        "--batch-size",
        "-b",
        help="Number of subjects to process per batch",
        min=1,
        max=100
    ),
    session_delay: int = typer.Option(
        2,
        "--session-delay",
        "-d", 
        help="Delay in seconds between batches",
        min=0,
        max=60
    )
) -> None:
    """Extract custom form data from XNAT projects with backup functionality.
    
    This command processes projects specified in a configuration file or via arguments,
    extracting custom form data and organizing it in a structured folder hierarchy
    with timestamped backup files.
    """
    # Determine configuration source
    if config:
        # Use specified config file
        config_data = load_config(config)
    elif not server or not username:
        # Look for default config file
        # First check user's home directory config location
        home_config_path = os.path.expanduser("~/.config/xn-form-backup/config.json")
        if os.path.exists(home_config_path):
            default_config_path = home_config_path
        else:
            # Fallback: check current directory
            current_config_path = os.path.join(os.getcwd(), "config", "config.json")
            if os.path.exists(current_config_path):
                default_config_path = current_config_path
            else:
                # Fallback: check if we're in a bundle, look for config folder relative to script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                bundle_config_path = os.path.join(os.path.dirname(script_dir), "config", "config.json")
                if os.path.exists(bundle_config_path):
                    default_config_path = bundle_config_path
                else:
                    logging.error("No configuration file found. Please provide server and username arguments or use --config.")
                    sys.exit(1)
        
        config_data = load_config(default_config_path)
        logging.info(f"Using default configuration: {default_config_path}")
    else:
        # Use command line arguments
        config_data = {
            "server": server,
            "username": username,
            "project_ids": []  # Will be prompted if needed
        }
    
    # Extract configuration
    server_url = config_data.get("server") or server
    username_val = config_data.get("username") or username
    project_ids = config_data.get("project_ids", [])
    
    if not server_url or not username_val:
        logging.error("Server and username must be provided either via config file or command line arguments.")
        sys.exit(1)
    
    # Get password (always prompted for security)
    password = os.environ.get("XNAT_PASSWORD") or getpass.getpass(prompt='Password: ')
    
    # If no project IDs in config, prompt for them
    if not project_ids:
        print("No project IDs specified in configuration.")
        project_input = input("Enter project IDs (comma-separated): ").strip()
        if not project_input:
            logging.error("No project IDs provided. Exiting.")
            sys.exit(1)
        project_ids = [pid.strip() for pid in project_input.split(',') if pid.strip()]
    
    logging.info(f"Starting backup extraction for {len(project_ids)} project(s)")
    logging.info(f"Projects: {', '.join(project_ids)}")
    logging.info(f"Output directory: {os.path.abspath(output_dir)}")
    
    # Process each project
    for i, project_id in enumerate(project_ids, 1):
        logging.info(f"Processing project {i}/{len(project_ids)}: {project_id}")
        
        try:
            process_single_project(
                server_url, username_val, password, project_id,
                output_dir, batch_size, session_delay
            )
        except Exception as e:
            logging.error(f"Failed to process project {project_id}: {e}")
            continue
        
        # Add delay between projects if processing multiple
        if i < len(project_ids):
            logging.info("Waiting 5 seconds before next project...")
            time.sleep(5)
    
    logging.info("Backup extraction completed for all projects!")


if __name__ == "__main__":
    app()