import subprocess
import tempfile
from pathlib import Path

import black
import isort


def lint_and_return(file_path: Path) -> str:
    """
    Lint a Python file and return the linted content as a string.
    
    Args:
        file_path: Path to the Python file to lint
        
    Returns:
        The linted file content as a string
    """
    # Read the original file
    content = file_path.read_text(encoding='utf-8')
    
    # Create a temporary file for ruff processing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)
    
    try:
        # Run ruff --fix on the temporary file
        subprocess.run(['ruff', 'check', str(temp_path), '--fix'], 
                      capture_output=True, check=False)
        
        # Read the ruff-fixed content
        content = temp_path.read_text(encoding='utf-8')
        
        # Apply isort formatting
        content = isort.code(content, file_path=file_path)
        
        # Apply black formatting
        content = black.format_str(content, mode=black.FileMode())
        
        return content
        
    finally:
        # Clean up temporary file
        temp_path.unlink(missing_ok=True)