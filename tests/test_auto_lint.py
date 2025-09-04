import pytest
from pathlib import Path
from robofactor.linting.auto_lint import lint_and_return


def test_lint_and_return_basic(tmp_path):
    """Test that lint_and_return processes a file and returns string content."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    
    result = lint_and_return(test_file)
    assert isinstance(result, str)
    assert "def add(a: int, b: int) -> int:" in result
    assert "return a + b" in result


def test_lint_and_return_fixes_formatting(tmp_path):
    """Test that lint_and_return fixes formatting issues."""
    test_file = tmp_path / "test.py"
    # Write poorly formatted code
    test_file.write_text("def test( ):\n    x=1+2\n    return x\n")
    
    result = lint_and_return(test_file)
    assert isinstance(result, str)
    # Should be formatted by black
    assert "def test():" in result
    assert "x = 1 + 2" in result


def test_lint_and_return_handles_imports(tmp_path):
    """Test that lint_and_return handles import sorting and removes unused imports."""
    test_file = tmp_path / "test.py"
    # Write with unsorted imports that are actually used
    test_file.write_text("import sys\nimport os\nfrom pathlib import Path\n\ndef main():\n    print(sys.version)\n    print(os.getcwd())\n    p = Path('.')\n    return p\n")
    
    result = lint_and_return(test_file)
    assert isinstance(result, str)
    # Should contain used imports (sorted by isort)
    assert "import" in result
    assert "def main():" in result
    assert "sys.version" in result


def test_lint_and_return_preserves_original_file(tmp_path):
    """Test that the original file is not modified."""
    test_file = tmp_path / "test.py"
    original_content = "def test( ):\n    x=1\n    return x\n"
    test_file.write_text(original_content)
    
    result = lint_and_return(test_file)
    
    # Original file should be unchanged
    assert test_file.read_text() == original_content
    # But result should be formatted
    assert result != original_content
    assert isinstance(result, str)


def test_lint_and_return_nonexistent_file():
    """Test that lint_and_return raises FileNotFoundError for nonexistent files."""
    with pytest.raises(FileNotFoundError):
        lint_and_return(Path("nonexistent.py"))


def test_lint_and_return_handles_unicode(tmp_path):
    """Test that lint_and_return handles unicode characters correctly."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def greet():\n    return '¡Hola, mundo! 🌍'\n", encoding='utf-8')
    
    result = lint_and_return(test_file)
    assert isinstance(result, str)
    assert "¡Hola, mundo! 🌍" in result


def test_lint_and_return_empty_file(tmp_path):
    """Test that lint_and_return handles empty files."""
    test_file = tmp_path / "empty.py"
    test_file.write_text("")
    
    result = lint_and_return(test_file)
    assert isinstance(result, str)
    # Empty file should remain empty or have minimal formatting
    assert len(result.strip()) == 0


def test_lint_and_return_complex_code(tmp_path):
    """Test lint_and_return with more complex code structure."""
    test_file = tmp_path / "complex.py"
    complex_code = '''
import sys
import os
from typing import List

class TestClass:
    def __init__(self,name:str):
        self.name=name
        
    def method(self,items:List[str])->str:
        result=""
        for item in items:
            result+=item+","
        return result[:-1]

def function(a,b,c=None):
    if c is None:
        c=[]
    return a+b+len(c)
'''
    test_file.write_text(complex_code)
    
    result = lint_and_return(test_file)
    assert isinstance(result, str)
    assert "class TestClass:" in result
    assert "def method(" in result
    assert "def function(" in result
    # Should be properly formatted
    assert "def __init__(self, name: str):" in result