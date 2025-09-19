#!/usr/bin/env python3
"""
XNAT Custom Form Batch Update Tool.

This script allows batch updating of custom form data in XNAT based on 
CSV/Excel files. Supports both subject-based and session-based custom forms
with configurable batch processing and session management.
"""
import os
import logging
import json
import re
from difflib import get_close_matches
import getpass
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Optional
import pandas as pd
import pytz
import requests
import typer
from typing_extensions import Annotated

# Melbourne timezone for consistent logging
melbtz = pytz.timezone('Australia/Melbourne')


def setup_folder_structure(base_path: str, server_name: str, project_id: str) -> Tuple[str, str]:
    """Setup folder structure: base_path/server_name/project_id/excel_outputs and logs
    
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



def setup_logger(name: str, logs_folder: str, project_id: str) -> logging.Logger:
    """
    Setup centralized logger with Melbourne timezone.
    
    Args:
        name: Logger name for identification.
        logs_folder: Path to logs folder
        project_id: Project ID for log filename
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    melbdt = datetime.now(melbtz)
    str_melbdt = melbdt.strftime('%Y-%m-%d_%H-%M-%S')
    
    log_directory = logs_folder
    os.makedirs(log_directory, exist_ok=True)
    
    logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(
        os.path.join(log_directory, f'{str_melbdt}_{project_id}_{name}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def logout_user_sessions(
    server: str, 
    username: str, 
    password: str,
    logger: logging.Logger
) -> bool:
    """
    Log out all active XNAT sessions for the user.
    
    Args:
        server: XNAT server URL.
        username: XNAT username.
        password: XNAT password.
        
    Returns:
        True if logout successful, False otherwise.
    """
    if not server.endswith("/"):
        server += "/"
    
    logout_url = f"{server}xapi/users/active/{username}"
    
    try:
        logger.info(f"Attempting to log out all active sessions for user: {username}")
        response = requests.delete(logout_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            logger.info("All active sessions logged out successfully.")
            return True
        elif response.status_code == 401:
            logger.error("Authentication failed during logout. Please check your credentials.")
            return False
        elif response.status_code == 403:
            logger.error("Access forbidden during logout. User may not have sufficient permissions.")
            return False
        elif response.status_code == 404:
            logger.warning("Logout endpoint not found. This might be an older XNAT version.")
            return True  # Assume success for older versions
        else:
            logger.error(
                f"Logout failed. HTTP Status: {response.status_code}, "
                f"Response: {response.text}"
            )
            return False
    except requests.exceptions.Timeout:
        logger.error("Logout request timed out. Server may be unresponsive.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to XNAT server during logout. Check server URL and network connection.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during logout: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        return False


def parse_form_components_recursively(components: list, field_info: dict) -> None:
    """
    Recursively parse form components to find xnatSelect fields at any nesting level.
    Handles various nested structures including panels, columns, fieldsets, etc.
    
    Args:
        components: List of form components to parse
        field_info: Dictionary to store field information (modified in place)
    """
    for component in components:
        component_type = component.get('type')
        
        if component_type == 'xnatSelect':
            field_key = component.get('key')
            is_multiple = component.get('multiple', False)
            
            # Extract valid values
            valid_values = []
            data_values = component.get('data', {}).get('values', [])
            for value_item in data_values:
                valid_values.append(value_item.get('value'))
            
            if is_multiple:
                field_info['multiple_option_fields'][field_key] = valid_values
            else:
                field_info['single_option_fields'][field_key] = valid_values
        
        # Handle different types of nested structures
        
        # 1. Standard components array (panels, fieldsets, containers, etc.)
        nested_components = component.get('components', [])
        if nested_components:
            parse_form_components_recursively(nested_components, field_info)
        
        # 2. Columns type - each column has its own components
        if component_type == 'columns':
            columns = component.get('columns', [])
            for column in columns:
                column_components = column.get('components', [])
                if column_components:
                    parse_form_components_recursively(column_components, field_info)
        
        # 3. Table type - has rows, and each row can have components
        if component_type == 'table':
            rows = component.get('rows', [])
            for row in rows:
                for cell in row:
                    cell_components = cell.get('components', [])
                    if cell_components:
                        parse_form_components_recursively(cell_components, field_info)
        
        # 4. Tabs type - each tab has components
        if component_type == 'tabs':
            tabs = component.get('components', [])
            for tab in tabs:
                tab_components = tab.get('components', [])
                if tab_components:
                    parse_form_components_recursively(tab_components, field_info)
        
        # 5. Well type (another container type)
        if component_type == 'well':
            well_components = component.get('components', [])
            if well_components:
                parse_form_components_recursively(well_components, field_info)
        
        # 6. DataGrid type - has components for each row template
        if component_type == 'datagrid':
            datagrid_components = component.get('components', [])
            if datagrid_components:
                parse_form_components_recursively(datagrid_components, field_info)
        
        # 7. EditGrid type - similar to datagrid
        if component_type == 'editgrid':
            editgrid_components = component.get('components', [])
            if editgrid_components:
                parse_form_components_recursively(editgrid_components, field_info)


def fetch_and_parse_form_definitions(server: str, username: str, password: str, logger: logging.Logger) -> dict:
    """
    Fetch custom form definitions and extract option field information.
    
    Returns:
        dict: Mapping of form_uuid to field definitions
    """
    try:
        api_url = f"{server}xapi/customforms"
        response = requests.get(api_url, auth=(username, password), timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch form definitions: {response.status_code}")
            return {}
        
        forms_data = response.json()
        form_definitions = {}
        
        for form in forms_data:
            form_uuid = form.get('formUUID')
            contents = json.loads(form.get('contents', '{}'))
            
            field_info = {
                'single_option_fields': {},  # field_name: [valid_values]
                'multiple_option_fields': {}  # field_name: [valid_values]
            }
            
            # Parse form components recursively
            components = contents.get('components', [])
            parse_form_components_recursively(components, field_info)
            
            form_definitions[form_uuid] = field_info
            
            # Log what was found for debugging
            if field_info['single_option_fields'] or field_info['multiple_option_fields']:
                logger.debug(f"Form UUID {form_uuid}:")
                if field_info['single_option_fields']:
                    logger.debug(f"  Single option fields: {list(field_info['single_option_fields'].keys())}")
                if field_info['multiple_option_fields']:
                    logger.debug(f"  Multiple option fields: {list(field_info['multiple_option_fields'].keys())}")
        
        logger.debug(f"Loaded definitions for {len(form_definitions)} forms")
        return form_definitions
    
    except Exception as e:
        logger.error(f"Error fetching form definitions: {e}")
        return {}

def normalize_option_value(raw_value: str, valid_options: list, field_name: str, logger: logging.Logger) -> str:
    """
    Normalize a single option value with fuzzy matching and case handling.
    
    Args:
        raw_value: User input value
        valid_options: List of valid XNAT values
        field_name: Field name for logging
        
    Returns:
        Normalized value or original if no match found
    """
    if not raw_value or pd.isna(raw_value):
        return ""
    
    # Clean the input
    clean_value = str(raw_value).strip().strip('"\'[]{}')
    
    # Exact match (case insensitive)
    for option in valid_options:
        if clean_value.lower() == option.lower():
            return option
    
    # Fuzzy match for typos
    matches = get_close_matches(clean_value, valid_options, n=1, cutoff=0.8)
    if matches:
        logger.info(f"Fuzzy matched '{clean_value}' to '{matches[0]}' for field '{field_name}'")
        return matches[0]
    
    # No match found - log warning and return original
    logger.warning(f"No match found for value '{clean_value}' in field '{field_name}'. Valid options: {valid_options}")
    return clean_value

def normalize_multiple_option_value(raw_value, valid_options: list, field_name: str, logger: logging.Logger) -> list:
    """
    Normalize multiple option values from various input formats.
    
    Args:
        raw_value: User input (can be string, list, etc.)
        valid_options: List of valid XNAT values
        field_name: Field name for logging
        
    Returns:
        List of normalized values for XNAT multiple option fields
    """
    if not raw_value or pd.isna(raw_value):
        return []
    
    # Convert to string first
    raw_str = str(raw_value).strip()
    
    # Handle empty cases
    if not raw_str or raw_str.lower() in ['nan', 'none', 'null']:
        return []
    
    # Extract values using regex to handle various formats
    values = extract_multiple_values(raw_str)
    
    # Normalize each value
    normalized_values = []
    for value in values:
        if value:  # Skip empty values
            normalized = normalize_option_value(value, valid_options, field_name, logger)
            if normalized and normalized not in normalized_values:
                normalized_values.append(normalized)
    
    # Return as list (XNAT format for multiple options)
    if normalized_values and len(values) > 1:
        logger.debug(f"Normalized multiple values for '{field_name}': {raw_str} -> {normalized_values}")
    
    return normalized_values

def extract_multiple_values(raw_str: str) -> list:
    """
    Extract individual values from various input formats.
    
    Handles formats like:
    - "value1, value2, value3"
    - "['value1', 'value2']"
    - "{'value1', 'value2'}"
    - "[{value1}, {value2}]"
    """
    # Remove outer brackets/braces if present
    cleaned = raw_str.strip()
    
    # Handle list-like formats
    if cleaned.startswith('[') and cleaned.endswith(']'):
        cleaned = cleaned[1:-1]
    elif cleaned.startswith('{') and cleaned.endswith('}'):
        cleaned = cleaned[1:-1]
    
    # Split on common separators and clean each value
    separators = [',', ';', '|', '&', ' and ', '/']
    values = [cleaned]  # Start with the whole string
    
    for sep in separators:
        if sep in cleaned:
            values = [v.strip() for v in cleaned.split(sep)]
            break
    
    # Clean individual values (remove quotes, braces, etc.)
    cleaned_values = []
    for value in values:
        # Remove quotes, braces, and extra whitespace
        clean_val = re.sub(r'^[\s\'"{\[]*|[\s\'"}\]]*$', '', value.strip())
        if clean_val:
            cleaned_values.append(clean_val)
    
    return cleaned_values

def process_form_data_with_validation(df: pd.DataFrame, form_uuid: str, form_definitions: dict, logger: logging.Logger) -> pd.DataFrame:
    """
    Process DataFrame to normalize option field values based on form definitions.
    
    Args:
        df: Input DataFrame
        form_uuid: Form UUID being processed
        form_definitions: Form definitions dict
        
    Returns:
        Processed DataFrame with normalized values
    """
    if form_uuid not in form_definitions:
        logger.warning(f"No form definition found for UUID: {form_uuid}")
        return df
    
    form_def = form_definitions[form_uuid]
    processed_df = df.copy()
    
    # Process single option fields
    for field_name, valid_options in form_def['single_option_fields'].items():
        if field_name in processed_df.columns:
            logger.debug(f"Processing single option field: {field_name}")
            processed_df[field_name] = processed_df[field_name].apply(
                lambda x: normalize_option_value(x, valid_options, field_name, logger)
            )
    
    # Process multiple option fields
    for field_name, valid_options in form_def['multiple_option_fields'].items():
        if field_name in processed_df.columns:
            logger.debug(f"Processing multiple option field: {field_name}")
            processed_df[field_name] = processed_df[field_name].apply(
                lambda x: normalize_multiple_option_value(x, valid_options, field_name, logger)
            )
    
    return processed_df

# 2. added this new function for testing XNAT connection

def test_xnat_connection(server: str, username: str, password: str, logger: logging.Logger) -> bool:
    """
    Test XNAT connection and credentials.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        
    Returns:
        True if connection successful, False otherwise
    """
    test_url = f"{server}data/version"
    
    try:
        logger.debug("Testing XNAT connection and credentials...")
        response = requests.get(test_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            try:
                version_info = response.text.strip()
                logger.info(f"Successfully connected to XNAT version: {version_info}")
                return True
            except Exception:
                logger.info("Successfully connected to XNAT (version info not available)")
                return True
        elif response.status_code == 401:
            logger.error("Authentication failed. Please check your username and password.")
            return False
        elif response.status_code == 403:
            logger.error("Access forbidden. User may not have sufficient permissions.")
            return False
        elif response.status_code == 404:
            logger.debug("Version endpoint not found, but connection appears successful.")
            # Try alternative endpoint
            alt_url = f"{server}data/projects"
            alt_response = requests.get(alt_url, auth=(username, password), timeout=30)
            if alt_response.status_code in [200, 401, 403]:
                return alt_response.status_code == 200
            return False
        else:
            logger.error(f"Connection test failed. Status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Connection test timed out. Server may be unresponsive.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to XNAT server. Check server URL and network connection.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during connection test: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {e}")
        return False


# 3. added this function to validate project access

def validate_project_access(server: str, username: str, password: str, project_id: str, logger: logging.Logger) -> bool:
    """
    Validate that the user has access to the specified project.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: Project ID to validate
        
    Returns:
        True if project exists and user has access, False otherwise
    """
    api_url = f"{server}data/projects/{project_id}"
    
    try:
        logger.debug(f"Validating access to project: {project_id}")
        response = requests.get(api_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            logger.debug(f"Successfully validated access to project {project_id}")
            return True
        elif response.status_code == 401:
            logger.error("Authentication failed when validating project access. Please check your credentials.")
            return False
        elif response.status_code == 403:
            logger.error(f"Access forbidden to project {project_id}. User may not have sufficient permissions.")
            return False
        elif response.status_code == 404:
            logger.error(f"Project '{project_id}' not found. Please verify the project ID.")
            return False
        else:
            logger.error(f"Failed to validate project access. Status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Request timed out when validating project access. Server may be unresponsive.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to XNAT server when validating project. Check server URL and network connection.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error when validating project access: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error when validating project access: {e}")
        return False


# 4. added this function to validate subject existence

def validate_subject_exists(server: str, username: str, password: str, 
                           project_id: str, subject_label: str, logger: logging.Logger) -> bool:
    """
    Validate that a subject exists in the specified project.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: Project ID
        subject_label: Subject label to validate
        
    Returns:
        True if subject exists, False otherwise
    """
    api_url = f"{server}data/projects/{project_id}/subjects/{subject_label}"
    
    try:
        response = requests.get(api_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            logger.warning(f"Subject '{subject_label}' not found in project '{project_id}'")
            return False
        elif response.status_code == 401:
            logger.error("Authentication failed when validating subject.")
            return False
        elif response.status_code == 403:
            logger.error("Access forbidden when validating subject.")
            return False
        else:
            logger.warning(f"Unexpected response when validating subject: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error when validating subject: {e}")
        return False
    except Exception as e:
        logger.warning(f"Error when validating subject: {e}")
        return False


# 5. added this function to validate session existence

def validate_session_exists(server: str, username: str, password: str, 
                           project_id: str, subject_label: str, session_label: str, logger: logging.Logger) -> bool:
    """
    Validate that a session exists for the specified subject.
    
    Args:
        server: XNAT server URL
        username: XNAT username
        password: XNAT password
        project_id: Project ID
        subject_label: Subject label
        session_label: Session label to validate
        
    Returns:
        True if session exists, False otherwise
    """
    api_url = f"{server}data/projects/{project_id}/subjects/{subject_label}/experiments/{session_label}"
    
    try:
        response = requests.get(api_url, auth=(username, password), timeout=30)
        
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            logger.warning(f"Session '{session_label}' not found for subject '{subject_label}' in project '{project_id}'")
            return False
        elif response.status_code == 401:
            logger.error("Authentication failed when validating session.")
            return False
        elif response.status_code == 403:
            logger.error("Access forbidden when validating session.")
            return False
        else:
            logger.warning(f"Unexpected response when validating session: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error when validating session: {e}")
        return False
    except Exception as e:
        logger.warning(f"Error when validating session: {e}")
        return False

def get_csv_files(input_path: Path) -> List[Path]:
    """
    Get list of CSV/Excel files from input path.
    
    Args:
        input_path: Path to file or directory.
        
    Returns:
        List of CSV/Excel file paths.
        
    Raises:
        ValueError: If no valid files found.
    """
    valid_extensions = {'.csv', '.xlsx', '.xls'}
    
    if input_path.is_file():
        if input_path.suffix.lower() in valid_extensions:
            return [input_path]
        else:
            raise ValueError(
                f"File {input_path} is not a valid CSV/Excel file"
            )
    
    elif input_path.is_dir():
        files = []
        for ext in valid_extensions:
            files.extend(input_path.glob(f"*{ext}"))
        
        if not files:
            raise ValueError(f"No CSV/Excel files found in {input_path}")
        
        return sorted(files)
    
    else:
        raise ValueError(f"Path {input_path} does not exist")


def read_data_file(file_path: Path, logger: logging.Logger) -> pd.DataFrame:
    """
    Read CSV or Excel file into DataFrame with comprehensive error handling.
    
    Args:
        file_path: Path to the data file.
        
    Returns:
        DataFrame with the data.
        
    Raises:
        ValueError: If file format is not supported or file is corrupted.
    """
    try:
        logger.info(f"Reading data file: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ValueError(f"File {file_path} is empty")
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            logger.warning(f"Large file detected ({file_size / 1024 / 1024:.1f}MB). This may take a while to process.")
        
        if file_path.suffix.lower() == '.csv':
            try:
                # Try different encodings
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, dtype=str, encoding=encoding)
                        logger.info(f"Successfully read CSV with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError(f"Could not decode CSV file with any standard encoding")
                    
            except pd.errors.EmptyDataError:
                raise ValueError(f"CSV file {file_path} is empty or has no data")
            except pd.errors.ParserError as e:
                raise ValueError(f"CSV parsing error in {file_path}: {e}")
                
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            try:
                df = pd.read_excel(file_path, dtype=str)
                logger.debug("Successfully read Excel file")
            except Exception as e:
                raise ValueError(f"Excel reading error in {file_path}: {e}")
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Validate DataFrame
        if df.empty:
            raise ValueError(f"File {file_path} contains no data")
        
        logger.debug(f"File loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        
        # Convert numeric columns back to their proper types
        metadata_cols = [
            'project_id', 'uuid', 'subject_label', 
            'session_label', 'session_type'
        ]
        
        for col in df.columns:
            if col not in metadata_cols:
                # Try to convert to numeric, fall back to string
                try:
                    # Only convert if the column has non-null values
                    if not df[col].isna().all():
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        # Only convert if at least 50% of values are numeric
                        if numeric_series.notna().sum() >= len(df) * 0.5:
                            df[col] = numeric_series
                except (ValueError, TypeError):
                    pass  # Keep as string

        # Clean column names (strip whitespace)
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip()
        
        # Check for duplicate columns
        if len(df.columns) != len(set(df.columns)):
            duplicates = [col for col in df.columns if list(df.columns).count(col) > 1]
            raise ValueError(f"Duplicate columns found: {duplicates}")
        
        logger.debug(f"Columns: {list(df.columns)}")
        return df
        
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except PermissionError:
        raise ValueError(f"Permission denied accessing file: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {e}")

def validate_dataframe(df: pd.DataFrame, logger: logging.Logger) -> Tuple[bool, List[str]]:
    """
    Validate DataFrame structure and required columns with detailed checks.
    
    Args:
        df: DataFrame to validate.
        
    Returns:
        Tuple of (is_valid, list_of_issues).
    """
    issues = []
    required_cols = ['project_id', 'uuid', 'subject_label']
    
    # Check for required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")
    
    # Check for empty required columns
    for col in required_cols:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                issues.append(f"Column '{col}' has {null_count} null/empty values")
            
            empty_count = (df[col] == '').sum()
            if empty_count > 0:
                issues.append(f"Column '{col}' has {empty_count} empty string values")
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        issues.append(f"Found {duplicate_count} duplicate rows")
    
    # Validate UUID format (basic check)
    if 'uuid' in df.columns:
        invalid_uuids = df[~df['uuid'].str.match(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$', na=False)]
        if not invalid_uuids.empty:
            issues.append(f"Found {len(invalid_uuids)} rows with invalid UUID format")
    
    # Check for session data consistency
    if 'session_label' in df.columns:
        # If session_label exists, all related session data should be consistent
        session_null = df['session_label'].isna()
        if session_null.any() and not session_null.all():
            issues.append("Inconsistent session data: some rows have session_label, others don't")
    
    # Log validation results
    if issues:
        logger.warning("DataFrame validation issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.debug("DataFrame validation passed successfully")
    
    return len(issues) == 0, issues


def process_single_file(
    file_path: Path,
    server: str,
    username: str,
    password: str,
    batch_size: int,
    form_definitions: dict,
    logger: logging.Logger
) -> Tuple[int, int]:
    """
    Process a single CSV/Excel file for custom form updates.
    
    Args:
        file_path: Path to the data file.
        server: XNAT server URL.
        username: XNAT username.
        password: XNAT password.
        batch_size: Number of records per batch.
        
    Returns:
        Tuple of (success_count, error_count).
    """
    logger.info(f"\n=== Processing file: {file_path.name} ===")
    
    try:
        # Read and validate the data file
        df = read_data_file(file_path, logger)
        logger.debug(f"File loaded: {len(df)} rows, columns: {list(df.columns)}")
        
        is_valid, issues = validate_dataframe(df, logger)
        if not is_valid:
            logger.error("DataFrame validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return 0, len(df)
        
        # Check if session-specific or subject-specific forms
        has_session_data = 'session_label' in df.columns
        form_type_desc = (
            'session-specific' if has_session_data else 'subject-specific'
        )
        logger.info(f"Processing {form_type_desc} forms.")

        # Validate unique projects mentioned in the file
        unique_projects = df['project_id'].unique()
        logger.info(f"Projects found in file: {list(unique_projects)}")
        
        # Validate access to all projects
        for project_id in unique_projects:
            if not validate_project_access(server, username, password, project_id, logger):
                logger.error(f"Cannot access project {project_id}. Stopping file processing.")
                return 0, len(df)   
                 
    except ValueError as e:
        logger.error(f"File validation failed: {e}")
        return 0, 1  # Return error for the file itself
    
    # Process rows in batches
    success_count = 0
    error_count = 0
    batch_count = 0
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    logger.info(f"Processing {len(df)} records in batches of {batch_size}")
    logger.info(f"Total batches: {total_batches}")
    
    for index, row in df.iterrows():
        try:
            # Logout at start of each new batch (except first)
            if index > 0 and index % batch_size == 0:
                batch_count += 1
                logger.info(
                    f"\n=== Completed batch {batch_count}/{total_batches} ==="
                )
                logger.info("Logging out sessions before next batch...")
                
                logout_success = logout_user_sessions(
                    server, username, password, logger
                )
                if logout_success:
                    logger.info("Session logout successful.")
                else:
                    logger.warning("Session logout failed, continuing...")
                
                logger.info(
                    f"=== Starting batch {batch_count + 1}/{total_batches} ==="
                )
            
            # Extract row data with validation
            try:
                project_id = str(row['project_id']).strip()
                form_uuid = str(row['uuid']).strip()
                subject_label = str(row['subject_label']).strip()
                
                if not project_id or not form_uuid or not subject_label:
                    logger.error(f"Row {index + 1}: Missing required data (project_id, uuid, or subject_label)")
                    error_count += 1
                    continue
                    
            except Exception as e:
                logger.error(f"Row {index + 1}: Error extracting required fields: {e}")
                error_count += 1
                continue

            if form_uuid in form_definitions:
                # Process just this row's data
                row_df = pd.DataFrame([row])
                processed_row_df = process_form_data_with_validation(row_df, form_uuid, form_definitions, logger)
                row = processed_row_df.iloc[0]  # Get back the processed row
                logger.debug(f"Row {index + 1}: Applied form validation for UUID {form_uuid}")                
            
            # Validate subject exists (optional validation)
            if not validate_subject_exists(server, username, password, project_id, subject_label, logger):
                logger.warning(f"Row {index + 1}: Subject may not exist, but continuing with update attempt...")
            
            # Determine API URL based on form type
            if has_session_data and pd.notna(row.get('session_label')):
                # Session-specific form
                session_label = str(row['session_label']).strip()
                if not session_label:
                    logger.error(f"Row {index + 1}: Empty session_label for session-specific form")
                    error_count += 1
                    continue
                
                # Validate session exists (optional validation)
                if not validate_session_exists(server, username, password, project_id, subject_label, session_label, logger):
                    logger.warning(f"Row {index + 1}: Session may not exist, but continuing with update attempt...")
                
                api_url = (
                    f"{server}xapi/custom-fields/projects/{project_id}/"
                    f"experiments/{session_label}/fields"
                )
                form_type = "session-specific"
                identifier = f"{project_id}/{subject_label}/{session_label}"
            else:
                # Subject-specific form
                api_url = (
                    f"{server}xapi/custom-fields/projects/{project_id}/"
                    f"subjects/{subject_label}/fields"
                )
                form_type = "subject-specific"
                identifier = f"{project_id}/{subject_label}"
            
            logger.info(
                f"Processing {form_type} form for {identifier} "
                f"(UUID: {form_uuid})"
            )
            
            # Extract form fields (exclude metadata columns)
            metadata_cols = [
                'project_id', 'uuid', 'subject_label', 
                'session_label', 'session_type'
            ]
            form_keys = [col for col in df.columns if col not in metadata_cols]
            
            # Build form data dictionary, excluding NaN values
            form_fields = {}
            for key in form_keys:
                value = row[key]
                
                # Handle different value types properly
                if isinstance(value, list):
                    # For lists (multiple option fields), include if not empty
                    if len(value) > 0:
                        form_fields[key] = value
                elif pd.notna(value) and value != "":
                    # For non-list values, check if not NaN and not empty
                    if isinstance(value, (int, float)):
                        form_fields[key] = value
                    else:
                        str_value = str(value).strip()
                        if str_value and str_value.lower() not in ['nan', 'none', 'null']:
                            form_fields[key] = str_value
                        
            if not form_fields:
                logger.warning(
                    f"No valid form data found for row {index + 1}. Skipping."
                )
                continue
                        
            # Create JSON payload wrapped with form UUID
            form_data = {form_uuid: form_fields}
            logger.debug(f"Form payload: {form_data}")
            
            # Make PUT request with enhanced error handling
            try:
                response = requests.put(
                    api_url, 
                    json=form_data, 
                    auth=(username, password),
                    timeout=60
                )
                
                # Log request details for debugging
                logger.debug(f"PUT request to: {api_url}")
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response content: {response.text}")
                
                if response.status_code == 200:
                    logger.info(
                        f"[SUCCESS] Updated {form_type} form for {identifier}"
                    )
                    success_count += 1
                elif response.status_code == 401:
                    logger.error(
                        f"[FAILED] Authentication failed for {identifier}. "
                        f"Please check your credentials."
                    )
                    error_count += 1
                elif response.status_code == 403:
                    logger.error(
                        f"[FAILED] Access forbidden for {identifier}. "
                        f"User may not have permission to update custom forms."
                    )
                    error_count += 1
                elif response.status_code == 404:
                    logger.error(
                        f"[FAILED] Resource not found for {identifier}. "
                        f"Subject/session may not exist or form UUID may be invalid."
                    )
                    error_count += 1
                elif response.status_code == 400:
                    logger.error(
                        f"[FAILED] Bad request for {identifier}. "
                        f"Invalid data format or form structure. Response: {response.text}"
                    )
                    error_count += 1
                else:
                    logger.error(
                        f"[FAILED] Failed to update {form_type} form for "
                        f"{identifier}. HTTP Status: {response.status_code}, "
                        f"Response: {response.text}"
                    )
                    error_count += 1
                    
            except requests.exceptions.Timeout:
                logger.error(f"[FAILED] Request timed out for {identifier}")
                error_count += 1
            except requests.exceptions.ConnectionError:
                logger.error(f"[FAILED] Connection error for {identifier}")
                error_count += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"[FAILED] Network error for {identifier}: {e}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error processing row {index + 1}: {e}")
            error_count += 1
    
    # File processing summary
    total_processed = success_count + error_count
    logger.info(f"\n=== File {file_path.name} Summary ===")
    logger.info(f"Rows processed: {total_processed}")
    logger.info(f"Successful updates: {success_count}")
    logger.info(f"Failed updates: {error_count}")
    
    if total_processed > 0:
        success_rate = (success_count / total_processed) * 100
        logger.info(f"Success rate: {success_rate:.1f}%")
    
    return success_count, error_count


def main(
    server: str = None,
    username: str = None,
    password: str = None,
    input_path: Path = None,
    batch_size: int = 10,
    logout: bool = True,
    output_dir: str = ".",
    project_id: str = None
) -> None:
    """
    Batch update custom forms on XNAT using CSV/Excel files.
    
    Supports both subject-based and session-based custom forms with 
    configurable batch processing and automatic session management.
    
    File Structure:
    - Session forms: project_id, uuid, subject_label, session_label, 
      session_type, [form_keys...]
    - Subject forms: project_id, uuid, subject_label, [form_keys...]
    
    Batch Processing:
    - Processes data in configurable batches (default: 10 records)
    - Logs out active XNAT sessions between batches
    - Helps manage XNAT session limits and improves server performance
    
    Examples:
        # Process single file with default batch size
        python script.py -x server -u username -i data.csv
        
        # Process directory with custom batch size and final logout
        python script.py -x server -u username -i /path/to/csvs 
        --batch-size 25 --logout
    """
    # Get password securely - use provided password or prompt
    if not password:
        password = os.environ.get("XNAT_PASSWORD")
        if not password:
            password = getpass.getpass(prompt='Password: ')

    # Add parameter validation
    if not all([server, username, input_path]):
        print("ERROR: Missing required parameters when called as function")
        raise typer.Exit(1)
    
    # Ensure server URL format
    if not server.startswith(('http://', 'https://')):
        server = 'https://' + server
    if not server.endswith('/'):
        server += '/'
    
    # Extract server name for folder structure
    server_name = extract_server_name(server)
    
    # If project_id not provided, try to extract from first file
    if not project_id:
        try:
            files_to_check = get_csv_files(input_path)
            if files_to_check:
                # Create a temporary logger for file reading
                temp_logger = logging.getLogger("temp_put")
                temp_logger.setLevel(logging.ERROR)  # Only show errors
                first_df = read_data_file(files_to_check[0], temp_logger)
                if 'project_id' in first_df.columns and len(first_df) > 0:
                    project_id = str(first_df['project_id'].iloc[0]).strip()
                else:
                    project_id = "unknown_project"
            else:
                project_id = "unknown_project"
        except Exception:
            project_id = "unknown_project"
    
    # Setup folder structure
    excel_folder, logs_folder = setup_folder_structure(
        output_dir, server_name, project_id
    )
    
    # Setup logger for this project
    logger = setup_logger("customform_batch_put", logs_folder, project_id)
    
    try:
        logger.info("=== Starting XNAT Custom Form Batch Update ===")
        logger.info(f"Server: {server}")
        logger.info(f"Username: {username}")
        logger.info(f"Input path: {input_path}")
        logger.debug(f"Batch size: {batch_size}")
        
        # Test XNAT connection first
        if not test_xnat_connection(server, username, password, logger):
            logger.error("Failed to establish connection to XNAT. Please check your server URL and credentials.")
            raise typer.Exit(1)
        
        # Fetch form definitions once at the start
        logger.debug("Fetching custom form definitions...")
        form_definitions = fetch_and_parse_form_definitions(server, username, password, logger)
        if not form_definitions:
            logger.warning("No form definitions loaded. Option field validation will be skipped.")
        
        # Get list of files to process
        files_to_process = get_csv_files(input_path)
        logger.info(f"Found {len(files_to_process)} file(s) to process")
        
        # Process each file
        total_success = 0
        total_errors = 0
        failed_files = []
        
        for file_index, file_path in enumerate(files_to_process, 1):
            logger.info(f"\n=== Processing file {file_index}/{len(files_to_process)}: {file_path.name} ===")
            
            try:
                success_count, error_count = process_single_file(
                    file_path, server, username, password, batch_size, form_definitions, logger
                )
                total_success += success_count
                total_errors += error_count
                
                if error_count > 0:
                    failed_files.append(f"{file_path.name} ({error_count} errors)")
                    
            except Exception as e:
                logger.error(f"Critical error processing file {file_path.name}: {e}")
                failed_files.append(f"{file_path.name} (critical error)")
                total_errors += 1
        
        # Overall summary
        total_processed = total_success + total_errors
        logger.info(f"\n=== Overall Processing Summary ===")
        logger.info(f"Files processed: {len(files_to_process)}")
        logger.info(f"Total records processed: {total_processed}")
        logger.info(f"Total successful updates: {total_success}")
        logger.info(f"Total failed updates: {total_errors}")

        if failed_files:
            logger.warning(f"Files with errors: {len(failed_files)}")
            for failed_file in failed_files:
                logger.warning(f"  - {failed_file}")        
        
        if total_processed > 0:
            overall_success_rate = (total_success / total_processed) * 100
            logger.info(f"Overall success rate: {overall_success_rate:.1f}%")
        
        # Final logout if requested
        if logout:
            logger.info("\nPerforming final logout...")
            logout_success = logout_user_sessions(server, username, password, logger)
            if logout_success:
                logger.info("Final logout completed successfully.")
            else:
                logger.error("Final logout failed.")

        # Exit with appropriate code
        if total_errors > 0:
            logger.warning(f"Processing completed with {total_errors} errors.")
            if total_success == 0:
                raise typer.Exit(1)  # All failed
            else:
                raise typer.Exit(2)  # Partial success
        else:
            logger.info("Processing completed successfully with no errors.")
                
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user. Cleaning up...")
        try:
            logout_user_sessions(server, username, password, logger)
        except Exception:
            pass
        raise typer.Exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        typer.echo(f"Unexpected error: {e}")
        # Try to logout even on unexpected errors
        try:
            logout_user_sessions(server, username, password, logger)
        except Exception:
            logger.error("Failed to logout sessions during error cleanup")
        raise typer.Exit(1)


if __name__ == '__main__':
    typer.run(main)