"""
Python module for extracting large functions from source code using libcst.
Designed to be used in GitHub Actions workflows.
"""

import json
from typing import List, Dict, Optional
import libcst as cst


def _is_top_level_function(node: cst.CSTNode, current_path: List[cst.CSTNode]) -> bool:
    """Check if a function is at the top level (not inside a class)."""
    for parent in reversed(current_path):
        if isinstance(parent, cst.ClassDef):
            return False
    return True


def _extract_function_info(node: cst.FunctionDef, source_lines: List[str], visitor: cst.CSTVisitor) -> Dict[str, any]:
    """Extract information about a function."""
    position = visitor.get_metadata(cst.metadata.PositionProvider, node)
    start_line = position.start.line
    end_line = position.end.line
    line_count = end_line - start_line + 1
    
    function_code = '\n'.join(source_lines[start_line - 1:end_line])
    
    return {
        "function_name": node.name.value,
        "line_count": line_count,
        "code": function_code
    }


def _find_large_functions(tree: cst.Module, source_lines: List[str], min_lines: int) -> List[Dict[str, any]]:
    """Find all large top-level functions in the AST."""
    wrapper = cst.metadata.MetadataWrapper(tree)
    functions = []
    
    class FunctionFinder(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)
        
        def __init__(self):
            self.depth = 0
        
        def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
            if self.depth == 0:  # Only top-level functions
                func_info = _extract_function_info(node, source_lines, self)
                if func_info["line_count"] >= min_lines:
                    functions.append(func_info)
        
        def visit_ClassDef(self, node: cst.ClassDef) -> None:
            self.depth += 1
        
        def leave_ClassDef(self, node: cst.ClassDef) -> None:
            self.depth -= 1
    
    finder = FunctionFinder()
    wrapper.visit(finder)
    return functions


def extract_large_functions(filepath: str, min_lines: int = 50, output_file: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Extract large functions from a Python source file.
    
    Args:
        filepath: Path to the Python source file
        min_lines: Minimum number of lines for a function to be considered "large" (default: 50)
        output_file: Optional path to write JSON output to
    
    Returns:
        List of dictionaries containing function information, sorted by line count (descending)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
        
        source_lines = source_code.splitlines()
        tree = cst.parse_module(source_code)
        
        functions = _find_large_functions(tree, source_lines, min_lines)
        functions.sort(key=lambda x: x["line_count"], reverse=True)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(functions, f, indent=2, ensure_ascii=False)
        
        return functions
        
    except Exception as e:
        raise RuntimeError(f"Error processing file {filepath}: {str(e)}")


if __name__ == "__main__":
    # Example usage for testing
    import sys
    if len(sys.argv) > 1:
        result = extract_large_functions(sys.argv[1])
        for func in result:
            print(f"Function: {func['function_name']} ({func['line_count']} lines)")