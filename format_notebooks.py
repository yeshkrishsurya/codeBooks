#!/usr/bin/env python3
"""
Script to format code cells in all Jupyter notebooks in the current directory.
Uses black formatter to ensure proper code formatting.
"""

import json
import os
import glob
from typing import Dict, Any, List
import subprocess
import sys

def install_black():
    """Install black if not available."""
    try:
        import black
        return True
    except ImportError:
        print("Installing black formatter...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "black"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install black. Please install it manually: pip install black")
            return False

def format_code_with_black(code: str) -> str:
    """Format Python code using black formatter."""
    try:
        import black
        
        # Skip formatting for non-Python code (SQL, comments, etc.)
        code_stripped = code.strip()
        if not code_stripped:
            return code
            
        # Check if it looks like SQL or other non-Python code
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']
        first_word = code_stripped.split()[0].upper() if code_stripped.split() else ""
        if first_word in sql_keywords:
            return code
            
        # Try to format with black
        formatted = black.format_str(code, mode=black.FileMode())
        return formatted.rstrip()  # Remove trailing newline added by black
    except black.InvalidInput:
        # Code cannot be parsed by black (likely not valid Python)
        return code
    except Exception as e:
        # For debugging - you can remove this if not needed
        if "Cannot parse" not in str(e):
            print(f"Warning: Could not format code: {e}")
        return code

def format_notebook_cells(notebook_path: str) -> bool:
    """Format all code cells in a Jupyter notebook."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        modified = False
        
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                if not source:
                    continue
                
                # Join source lines into a single string
                if isinstance(source, list):
                    code = ''.join(source)
                else:
                    code = source
                
                # Skip empty cells
                if not code.strip():
                    continue
                
                # Format the code
                formatted_code = format_code_with_black(code)
                
                # Check if formatting changed anything
                if formatted_code != code:
                    # Convert back to list format (Jupyter's preferred format)
                    formatted_lines = formatted_code.split('\n')
                    # Add newline to all lines except the last one
                    formatted_source = [line + '\n' for line in formatted_lines[:-1]]
                    if formatted_lines[-1]:  # Add last line only if it's not empty
                        formatted_source.append(formatted_lines[-1])
                    
                    cell['source'] = formatted_source
                    modified = True
        
        # Save the notebook if it was modified
        if modified:
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2, ensure_ascii=False)
            print(f"Formatted: {notebook_path}")
            return True
        else:
            print(f"No changes needed: {notebook_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {notebook_path}: {e}")
        return False

def main():
    """Main function to format all notebooks in current directory."""
    # Install black if needed
    if not install_black():
        return
    
    # Find all notebook files
    notebook_files = glob.glob("*.ipynb")
    
    if not notebook_files:
        print("No Jupyter notebook files found in current directory.")
        return
    
    print(f"Found {len(notebook_files)} notebook(s)")
    
    formatted_count = 0
    for notebook_file in notebook_files:
        print(f"\nProcessing: {notebook_file}")
        if format_notebook_cells(notebook_file):
            formatted_count += 1
    
    print(f"\nCompleted! {formatted_count} notebook(s) were formatted.")

if __name__ == "__main__":
    main()