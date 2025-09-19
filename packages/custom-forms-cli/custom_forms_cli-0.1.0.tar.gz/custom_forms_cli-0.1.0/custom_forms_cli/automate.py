import typer
import getpass
import os
import threading
import time
import sys
from pathlib import Path
from typing import Optional

# Import custom password input
try:
    from .password_input import simple_password_with_confirmation
except ImportError:
    # Fallback if import fails
    simple_password_with_confirmation = lambda prompt: getpass.getpass(prompt)

# Handle PyInstaller bundled environment
def get_script_path():
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running as normal Python script
        return Path(__file__).parent.resolve()

SCRIPT_DIR = get_script_path()
sys.path.insert(0, str(SCRIPT_DIR))

# Import the main functions from your scripts
try:
    from get import main as get_main
    from put import main as put_main
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure get.py and put.py are in the same directory as this script")
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def get_input_with_timeout(prompt_text, timeout_seconds):
    user_input = []

    def prompt():
        user_input.append(input(prompt_text))

    thread = threading.Thread(target=prompt)
    thread.start()
    thread.join(timeout_seconds)
    if thread.is_alive():
        return None  # Timeout
    return user_input[0].strip()

def run_automation(
    server: Optional[str] = None,
    username: Optional[str] = None,
    project_id: Optional[str] = None,
    form: Optional[str] = None,
    batch_size: int = 50,
    skip_fetch: bool = False
):
    """Core automation logic"""
    # Get parameters from CLI args or prompt for missing ones
    if not server:
        server = typer.prompt("Enter XNAT server URL (-x)").strip()
    
    if not username:
        username = typer.prompt("Enter username (-u)").strip()
    
    # Check for password in environment first, then prompt
    password = os.environ.get("XNAT_PASSWORD")
    if not password:
        password = simple_password_with_confirmation("Enter your password: ")
    
    if not project_id:
        project_id = typer.prompt("Enter project ID (-p)")
    
    # Ask user if they want to fetch data or use existing Excel files
    if not skip_fetch:
        while True:
            fetch_choice = typer.prompt(
                "Do you want to fetch custom form data from XNAT? (y/n)",
                default='y'
            ).lower().strip()
            
            if fetch_choice in ['y', 'yes', 'n', 'no']:
                skip_fetch = fetch_choice in ['n', 'no']
                break
            else:
                typer.echo("Please enter 'y' (yes) or 'n' (no)")
                continue
    
    if not skip_fetch:
        if not form:
            form = typer.prompt("Enter form uuid or leave blank for interactive form fetch", default="")

    # Only run get.py if user wants to fetch data
    if not skip_fetch:
        typer.echo(f"\nRunning get.py with server: {server}, user: {username}, project: {project_id}...\n")
        try:
            get_main(
                server=server,
                username=username,
                password=password,
                project_id=project_id,
                form_uuid=form if form and form.strip() else "",
                batch_size=batch_size,
                session_delay=2
            )
            typer.echo("\nFinished getting forms successfully.\n")
        except Exception as e:
            typer.echo(f"\nError: get.py failed with error: {e}")
            typer.echo("Stopping automation workflow due to get.py failure.")
            raise typer.Exit(code=1)
    else:
        typer.echo("\nSkipping data fetch from XNAT. Using existing Excel files.\n")

    # Timer logic for Excel upload path input (this remains as prompted input)
    start_time = time.time()
    timeout = 30 * 60  # 30 minutes in seconds
    
    while True:
        remaining = timeout - (time.time() - start_time)
        if remaining <= 0:
            typer.echo("\nTime limit exceeded. No Excel file provided within 30 minutes. Exiting.")
            raise typer.Exit(code=1)

        input_path = get_input_with_timeout("Enter path to Excel file or directory: ", remaining)
        if input_path is None:
            typer.echo("\nTime limit exceeded. No Excel file provided within 30 minutes. Exiting.")
            raise typer.Exit(code=1)

        # Strip surrounding quotes from input_path if present
        input_path = input_path.strip('"').strip("'")

        if Path(input_path).exists():
            break
        else:
            typer.echo("Invalid path. Please try again.")

    # Call put.py main function directly - credentials already available
    typer.echo(f"\nRunning put.py with input: {input_path}...\n")
    try:
        put_main(
            server=server,
            username=username,
            password=password,  # Pass password to put.py
            input_path=Path(input_path),
            batch_size=batch_size,
            logout=True
        )
        typer.echo("\nAutomation workflow completed successfully!")
    except Exception as e:
        typer.echo(f"\nError: put.py failed with error: {e}")
        raise typer.Exit(code=1)

# Create app with invoke_without_command=True and no_args_is_help=False
app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
    help="""
XNAT Custom Forms Automation CLI\n
\n
Runs the full automation workflow for XNAT Custom Forms:\n
\n
1. Optionally fetches custom form data using get.py (or skip if you have existing Excel files)\n
2. Saves form data as Excel files locally (if fetching)\n
3. Prompts for path to modified Excel file(s)\n
4. Uploads updated data using put.py\n
\n
You can provide parameters via CLI arguments or interactively when prompted.\n
Password and Excel file path are always prompted for security and workflow reasons.\n
\n
Examples:\n
  xn-form                                    # Interactive mode (prompts for all)\n
  xn-form -x https://server.com -u user      # Mixed mode (some CLI, some prompts)\n
  xn-form -x server.com -u user -p proj123   # Mostly CLI args\n
  xn-form --skip-fetch                       # Skip data fetch, use existing Excel files\n
  xn-form --help                             # Show this help\n
"""
)

@app.callback()
def main(
    ctx: typer.Context,
    server: Optional[str] = typer.Option(None, "-x", "--server", help="XNAT server URL"),
    username: Optional[str] = typer.Option(None, "-u", "--username", help="XNAT username"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project-id", help="XNAT project ID"),
    form: Optional[str] = typer.Option(None, "-f", "--form", help="Form name (optional)"),
    batch_size: int = typer.Option(50, "-b", "--batch-size", help="Batch size for processing"),
    skip_fetch: bool = typer.Option(False, "--skip-fetch", help="Skip fetching data from XNAT, use existing Excel files"),
    help_flag: bool = typer.Option(False, "-h", "--help", help="Show help message")
):
    """
    XNAT Custom Forms Automation CLI\n
    \n
    Run the complete XNAT custom forms automation workflow.\n
    \n
    This command will:\n
    1. Optionally fetch forms from XNAT (get.py) - or skip if you have existing Excel files\n
    2. Wait for you to modify Excel files (if fetching)\n
    3. Upload modified forms back to XNAT (put.py)\n
    """
    # Handle help explicitly
    if help_flag:
        print(ctx.get_help())
        raise typer.Exit()
    
    # Only run automation if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        run_automation(server, username, project_id, form, batch_size, skip_fetch)

if __name__ == "__main__":
    app()
    if getattr(sys, 'frozen', False):
        input("\nPress Enter to exit...")