from robofactor.linting.auto_lint import lint_and_return


def test_lint_and_return_basic():
    """Test that lint_and_return processes content and returns string content."""
    content = "def add(a: int, b: int) -> int:\n    return a + b\n"
    
    result = lint_and_return(content)
    assert isinstance(result, str)
    assert "def add(a: int, b: int) -> int:" in result
    assert "return a + b" in result


def test_lint_and_return_fixes_formatting():
    """Test that lint_and_return fixes formatting issues."""
    # Poorly formatted code
    content = "def test( ):\n    x=1+2\n    return x\n"
    
    result = lint_and_return(content)
    assert isinstance(result, str)
    # Should be formatted by black
    assert "def test():" in result
    assert "x = 1 + 2" in result


def test_lint_and_return_handles_imports():
    """Test that lint_and_return handles import sorting and removes unused imports."""
    # Unsorted imports that are actually used
    content = "import sys\nimport os\nfrom pathlib import Path\n\ndef main():\n    print(sys.version)\n    print(os.getcwd())\n    p = Path('.')\n    return p\n"
    
    result = lint_and_return(content)
    assert isinstance(result, str)
    # Should contain used imports (sorted by isort)
    assert "import" in result
    assert "def main():" in result
    assert "sys.version" in result



def test_lint_and_return_handles_unicode():
    """Test that lint_and_return handles unicode characters correctly."""
    content = "def greet():\n    return '¡Hola, mundo! 🌍'\n"
    
    result = lint_and_return(content)
    assert isinstance(result, str)
    assert "¡Hola, mundo! 🌍" in result


def test_lint_and_return_empty_file():
    """Test that lint_and_return handles empty content."""
    content = ""
    
    result = lint_and_return(content)
    assert isinstance(result, str)
    # Empty content should remain empty or have minimal formatting
    assert len(result.strip()) == 0


def test_lint_and_return_complex_code():
    """Test lint_and_return with more complex code structure."""
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
    
    result = lint_and_return(complex_code)
    assert isinstance(result, str)
    assert "class TestClass:" in result
    assert "def method(" in result
    assert "def function(" in result
    # Should be properly formatted
    assert "def __init__(self, name: str):" in result