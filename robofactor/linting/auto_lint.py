import subprocess
import tempfile
from pathlib import Path

import black
import isort


def lint_and_return(content: str) -> str:
    """
    Lint Python code and return the linted content as a string.
    
    Args:
        content: Python code content to lint
        
    Returns:
        The linted code content as a string
    """
    
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
        content = isort.code(content)
        
        # Apply black formatting
        content = black.format_str(content, mode=black.FileMode())
        
        return content
        
    finally:
        # Clean up temporary file
        temp_path.unlink(missing_ok=True)