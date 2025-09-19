# XNAT Custom Forms CLI Toolkit

A Python-based command-line toolkit for automating the download, modification, and upload of custom form data from XNAT (eXtensible Neuroimaging Archive Toolkit) servers.

## Overview

This toolkit streamlines the process of working with XNAT custom forms :

- **`xn-form`** (automation.py) - A unified automation workflow that combines both operations with user-friendly prompts

### What it does

1. **Data Extraction**: Connects to your XNAT server and retrieves custom form data for specified projects
2. **Excel Export**: Saves the form data as structured Excel files for easy viewing and editing
3. **Data Population**: Allows you to modify the Excel files with updated information
4. **Data Upload**: Uploads your modified data back to the XNAT server, updating the custom forms

This is particularly useful for batch updates to XNAT custom forms, data migration, or offline form completion workflows.

## Installation

### Prerequisites
- Python 3.7+
- Required Python packages (install via pip):
  ```bash
  pip install typer requests pandas openpyxl
  ```

### Setup
1. Clone or download this toolkit to your local machine
2. Ensure all Python dependencies are installed
3. Make sure the scripts are executable and in your PATH (optional)

## Quick Start - Automated Workflow

The `xn-form` command provides a complete automation workflow that handles the entire process from data fetch to upload.

### Basic Usage

```bash
xn-form
```

### Interactive Workflow

When you run the automation, it will guide you through the following steps:

1. **Server Connection Setup**
   ```
   Enter XNAT server URL (-x): https://your-xnat-server.com
   Enter username (-u): your-username
   Enter your password: [hidden input]
   ```

2. **Project and Form Selection**
   ```
   Enter project ID (-pid): YOUR_PROJECT_ID
   Enter form name or leave blank for interactive form fetch: [optional]
   ```

3. **Data Fetching Phase**
   - The system runs `get.py` automatically
   - Downloads form data and saves as Excel files
   - Shows progress and completion status

4. **Excel Modification Phase**
   - You have up to 30 minutes to modify the downloaded Excel files
   - Edit the Excel files using your preferred spreadsheet application
   - Save your changes

5. **Upload Confirmation**
   ```
   Enter path to Excel file or directory containing excel file/s for upload: /path/to/your/modified/file.xlsx
   ```

6. **Data Upload Phase**
   - The system runs `put.py` automatically
   - Uploads your modified data back to XNAT
   - Shows upload progress and results

### Complete Example Session

```bash
$ xn-form

Enter XNAT server URL (-x): https://xnat.myinstitution.edu
Enter username (-u): researcher123
Enter your password: ************
Enter project ID (-pid): BRAIN_STUDY_2024
Enter form name or leave blank for interactive form fetch: patient_demographics

Running get.py...

Connected to XNAT server
Found project: BRAIN_STUDY_2024
Fetching form: patient_demographics
Downloaded 150 form entries
Saved to: patient_demographics_20240725_143022.xlsx

Finished getting forms.

[At this point, you edit the Excel file with your changes]

Enter path to Excel file or directory containing excel file/s for upload: ./patient_demographics_20240725_143022_modified.xlsx

Running put.py...

✓ Processing Excel file: patient_demographics_20240725_143022_modified.xlsx
✓ Validating data format
✓ Uploading 150 form entries in batches of 10
✓ Upload complete: 150/150 successful

Automation complete.
```

## Command Reference

### Automation Script Options

The automation script accepts the workflow interactively, but you can also examine the individual scripts it calls, although calling of modular functions is not supported yet:

**get.py parameters:**
- `-x, --server`: XNAT server URL
- `-u, --username`: XNAT username  
- `-pid, --project-id`: XNAT project ID
- `-f, --form`: Form name (optional, interactive if not provided)

**put.py parameters:**
- `-x, --server`: XNAT server URL
- `-u, --username`: XNAT username
- `-i, --input`: Path to Excel file or directory containing Excel files

### Security Notes

- Passwords are handled securely using `getpass` (hidden input)
- Passwords are passed to subprocesses via environment variables
- No credentials are stored in files or command history

## Excel File Format

The exported Excel files follow a structured format:
- Each row represents one form entry
- Column headers match the XNAT form field names
- Additional metadata columns may be included for tracking
- Modified files should maintain the same structure for successful upload

## Error Handling

The automation includes several safety features:

- **Path Validation**: Ensures Excel file paths exist before attempting upload
- **Timeout Protection**: 30-minute limit for Excel modification phase
- **Connection Validation**: Verifies XNAT server connectivity before operations
- **Batch Processing**: Uploads are processed in configurable batch sizes (default: 10)

## Individual Script Details

The following sections provide detailed information about how the `get.py` and `put.py` scripts work individually.

### get.py - Data Fetching Script

The `get.py` script is responsible for extracting custom form data from XNAT projects and saving it to Excel files. It supports both subject-level and session-level forms with intelligent batch processing to prevent server overload.

#### Key Features

- **Project-wide extraction**: Processes all subjects in a specified XNAT project
- **Form filtering**: Automatically filters forms based on project applicability  
- **Interactive form selection**: Allows users to choose which forms to process
- **Session type matching**: For session-level forms, only processes matching session types (e.g., MR, CT, PET)
- **Batch processing**: Handles large projects in configurable batches with session management
- **Excel export**: Saves form data as structured Excel files for easy editing

#### Command Syntax

```bash
python get.py -x <server_url> -u <username> -pid <project_id> [options]
```

#### Parameters

- `-x, --server`: XNAT server URL (e.g., `https://xnat.example.com`)
- `-u, --username`: XNAT username for authentication
- `-pid, --project`: XNAT project ID to process
- `-f, --form-uuid`: (Optional) Specific form UUID to process
- `-b, --batch-size`: Number of subjects per batch (default: 10, range: 1-100)
- `-d, --session-delay`: Delay between batches in seconds (default: 2, range: 0-60)

#### Usage Examples

**Extract all forms from a project:**
```bash
python get.py -x https://xnat.mysite.edu -u researcher123 -pid BRAIN_STUDY_2024
```

**Extract a specific form:**
```bash
python get.py -x https://xnat.mysite.edu -u researcher123 -pid BRAIN_STUDY_2024 -f a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Custom batch processing:**
```bash
python get.py -x https://xnat.mysite.edu -u researcher123 -pid BRAIN_STUDY_2024 -b 25 -d 5
```

#### Interactive Form Selection

When no specific form UUID is provided, the script displays all available forms:

```
================================================================================
AVAILABLE CUSTOM FORMS (Applicable to this project)
================================================================================
 1. Patient Demographics
    UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
    Level: Subject
    Path: /xnat:subjectData/demographics

 2. MRI Session Quality Check
    UUID: b2c3d4e5-f6g7-8901-bcde-f23456789012
    Level: Session (xnat:mrSessionData)
    Path: /xnat:mrSessionData/quality

 3. Clinical Assessment
    UUID: c3d4e5f6-g7h8-9012-cdef-345678901234
    Level: Subject
    Path: /xnat:subjectData/clinical
================================================================================

Enter form numbers to process (e.g., '1,3,5' or 'all' for all forms): 
```

#### Output Structure

The script creates Excel files in an `excel_outputs` directory with the following naming convention:
```
Form_Title_12345678.xlsx
```

Each Excel file contains:
- **Metadata columns**: `project_id`, `uuid`, `subject_label`
- **Session columns** (for session forms): `session_label`, `session_type`
- **Form field columns**: All custom form fields as defined in XNAT

#### Batch Processing Logic

The script implements intelligent batch processing to prevent XNAT server overload:

1. **Subject batching**: Processes subjects in configurable batches (default: 10)
2. **Session management**: Logs out all active sessions between batches
3. **Connection refresh**: Creates new XNAT connections for each batch
4. **Progress tracking**: Provides detailed logging of batch progress
5. **Error recovery**: Continues processing even if individual batches fail

#### Logging

All operations are logged to timestamped files in the `logs` directory:
```
logs/2024-07-25_14-30-22_customform_batch_get.log
```

Log entries include:
- Connection status and authentication
- Form discovery and filtering results
- Batch processing progress
- Data extraction statistics
- Error details and warnings

### put.py - Data Upload Script

The `put.py` script handles batch uploading of modified custom form data from Excel/CSV files back to XNAT. It supports both subject-level and session-level forms with robust error handling and batch session management.

#### Key Features

- **Multi-file processing**: Handles single files or entire directories
- **Format flexibility**: Supports CSV, Excel (.xlsx), and legacy Excel (.xls) files
- **Automatic validation**: Validates file structure and required columns
- **Batch session management**: Logs out XNAT sessions periodically to prevent timeouts
- **Type preservation**: Maintains numeric and string data types during upload
- **Comprehensive logging**: Detailed success/failure tracking and statistics

#### Command Syntax

```bash
python put.py -x <server_url> -u <username> -i <input_path> [options]
```

#### Parameters

- `-x, --server`: XNAT server URL  
- `-u, --username`: XNAT username for authentication
- `-i, --input`: Path to Excel/CSV file or directory containing files
- `--batch-size`: Records to process before session logout (default: 10, minimum: 1)
- `--logout`: Logout all sessions after processing (default: true)

#### Usage Examples

**Upload a single Excel file:**
```bash
python put.py -x https://xnat.mysite.edu -u researcher123 -i patient_demographics_modified.xlsx
```

**Upload all files in a directory:**
```bash  
python put.py -x https://xnat.mysite.edu -u researcher123 -i ./modified_forms/
```

**Custom batch size with session management:**
```bash
python put.py -x https://xnat.mysite.edu -u researcher123 -i data.xlsx --batch-size 25 --logout
```

#### File Format Requirements

**Required columns for all forms:**
- `project_id`: XNAT project identifier
- `uuid`: Form UUID from the original export
- `subject_label`: XNAT subject label

**Additional columns for session-level forms:**
- `session_label`: XNAT session/experiment label
- `session_type`: Session type (e.g., xnat:mrSessionData)

**Form data columns:**
- All other columns are treated as custom form fields
- Column names must match the original form field keys
- Values can be strings, numbers, or empty (null)

#### File Format Example

**Subject-level form:**
```csv
project_id,uuid,subject_label,age,gender,diagnosis
BRAIN_STUDY,a1b2c3d4...,SUBJ001,45,M,Normal
BRAIN_STUDY,a1b2c3d4...,SUBJ002,38,F,Abnormal
```

**Session-level form:**
```csv  
project_id,uuid,subject_label,session_label,session_type,quality_score,motion_rating
BRAIN_STUDY,b2c3d4e5...,SUBJ001,SESS001,xnat:mrSessionData,8.5,Good
BRAIN_STUDY,b2c3d4e5...,SUBJ002,SESS002,xnat:mrSessionData,7.2,Fair
```

#### Processing Workflow

1. **File Discovery**: Locates all CSV/Excel files in the specified path
2. **Data Validation**: Checks for required columns and data integrity
3. **Form Type Detection**: Determines if forms are subject or session-based
4. **Batch Processing**: Processes records in configurable batches
5. **Session Management**: Logs out XNAT sessions between batches
6. **API Updates**: Sends PUT requests to XNAT custom form endpoints
7. **Result Tracking**: Logs success/failure rates and detailed statistics

#### Batch Processing Benefits

- **Prevents session timeouts**: Regular XNAT session cleanup
- **Improves server performance**: Reduces concurrent session load
- **Error isolation**: Failed batches don't affect subsequent processing
- **Progress tracking**: Clear visibility into processing status

#### Error Handling

The script provides comprehensive error handling:

- **File validation errors**: Missing files, unsupported formats
- **Data validation errors**: Missing required columns, invalid data
- **Network errors**: Connection failures, authentication issues  
- **XNAT API errors**: Invalid form data, permission issues
- **Processing errors**: Individual record failures don't stop batch processing

#### Success Metrics

Each processing run provides detailed statistics:

```
=== Overall Processing Summary ===
Files processed: 3
Total records processed: 150
Total successful updates: 147
Total failed updates: 3
Overall success rate: 98.0%
```

#### Logging

All operations are logged with timestamps to files in the `logs` directory:
```
logs/2024-07-25_14-45-33_customform_batch_put.log
```

Log entries include:
- File processing status
- Data validation results  
- Individual record success/failure
- Batch completion summaries
- Final processing statistics

## Troubleshooting

**Common Issues:**

- **Connection Errors**: Verify XNAT server URL and network connectivity
- **Authentication Failures**: Check username/password and XNAT permissions
- **File Path Errors**: Ensure Excel file paths are correct and accessible
- **Upload Failures**: Verify Excel file format matches expected structure

**Getting Help:**
- Check XNAT server logs for detailed error messages
- Verify project permissions in XNAT web interface
- Ensure custom forms exist and are properly configured