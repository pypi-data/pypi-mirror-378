#!/usr/bin/env python3
"""
Custom password input with visual feedback
"""

import sys
import msvcrt
import getpass

def get_password_with_asterisks(prompt="Enter password: "):
    """
    Get password input with asterisk feedback for both typing and pasting.
    Works on Windows CMD/PowerShell.
    """
    print(prompt, end='', flush=True)
    password = ""
    
    while True:
        try:
            # Get a single character
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                # Handle special keys
                if char == b'\r' or char == b'\n':  # Enter key
                    print()  # New line
                    break
                elif char == b'\x08':  # Backspace
                    if len(password) > 0:
                        password = password[:-1]
                        # Erase the last asterisk
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                elif char == b'\x03':  # Ctrl+C
                    print("\nInterrupted")
                    raise KeyboardInterrupt()
                elif char == b'\x16' or char == b'\x02':  # Ctrl+V or Ctrl+B (paste)
                    # Try to handle paste - this is tricky in CMD
                    print("*", end='', flush=True)
                    password += chr(ord(char))
                else:
                    # Regular character
                    try:
                        decoded_char = char.decode('utf-8')
                        if decoded_char.isprintable():
                            password += decoded_char
                            print("*", end='', flush=True)
                    except UnicodeDecodeError:
                        # Skip invalid characters
                        pass
        except Exception:
            # If anything fails, fall back to getpass
            print("\nFalling back to secure input (no visual feedback)...")
            remaining = getpass.getpass("")
            password += remaining
            break
    
    return password

def get_password_with_feedback(prompt="Enter password: "):
    """
    Enhanced password input with length feedback.
    Shows character count instead of asterisks for better UX.
    """
    try:
        # Try the asterisk method first (Windows only)
        if sys.platform == "win32":
            return get_password_with_length_feedback(prompt)
        else:
            # Fall back to getpass for non-Windows
            return getpass.getpass(prompt)
    except Exception:
        # If anything fails, use standard getpass
        return getpass.getpass(prompt)

def get_password_with_length_feedback(prompt="Enter password: "):
    """
    Show password length as feedback instead of asterisks.
    """
    print(prompt, end='', flush=True)
    password = ""
    
    while True:
        try:
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                if char == b'\r' or char == b'\n':  # Enter
                    print()
                    break
                elif char == b'\x08':  # Backspace
                    if len(password) > 0:
                        password = password[:-1]
                        # Clear the line and reprint
                        print(f'\r{prompt}[{len(password)} characters]', end='', flush=True)
                elif char == b'\x03':  # Ctrl+C
                    print("\nInterrupted")
                    raise KeyboardInterrupt()
                else:
                    # Add character
                    try:
                        decoded_char = char.decode('utf-8')
                        if decoded_char.isprintable():
                            password += decoded_char
                            print(f'\r{prompt}[{len(password)} characters]', end='', flush=True)
                    except UnicodeDecodeError:
                        pass
        except Exception:
            print("\nFalling back to secure input...")
            remaining = getpass.getpass("")
            password += remaining
            break
            
    return password

def simple_password_with_confirmation(prompt="Enter password: "):
    """
    Simple approach: get password and show character count confirmation.
    """
    password = getpass.getpass(prompt)
    if password:
        print(f"✓ Password entered ({len(password)} characters)")
    else:
        print("⚠ No password entered")
    return password