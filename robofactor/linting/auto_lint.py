import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple


class LintResult(NamedTuple):
    """Container for linting results."""
    file_path: Path
    success: bool
    output: str = ""
    errors: str = ""


def _run_command(cmd: List[str]) -> Tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd[0]}"


def _run_ruff(file_path: Path, auto_fix: bool = False) -> LintResult:
    """Run ruff linting on a file."""
    cmd = ["ruff", "check", str(file_path)]
    if auto_fix:
        cmd.append("--fix")
    
    success, output, errors = _run_command(cmd)
    return LintResult(file_path, success, output, errors)


def _run_black(file_path: Path, auto_fix: bool = False) -> LintResult:
    """Run black formatting on a file."""
    cmd = ["black", str(file_path)]
    if not auto_fix:
        cmd.extend(["--check", "--diff"])
    
    success, output, errors = _run_command(cmd)
    return LintResult(file_path, success, output, errors)


def _run_isort(file_path: Path, auto_fix: bool = False) -> LintResult:
    """Run isort on a file."""
    cmd = ["isort", str(file_path)]
    if not auto_fix:
        cmd.extend(["--check-only", "--diff"])
    
    success, output, errors = _run_command(cmd)
    return LintResult(file_path, success, output, errors)


LINTERS = {
    'ruff': _run_ruff,
    'black': _run_black,
    'isort': _run_isort,
}


def _print_result(linter_name: str, result: LintResult):
    """Print linting result."""
    status = "✓" if result.success else "✗"
    print(f"  {status} {linter_name}: {result.file_path.name}")
    
    if not result.success:
        if result.output:
            print(f"    Output: {result.output.strip()}")
        if result.errors:
            print(f"    Errors: {result.errors.strip()}")


def lint_file(file_path: Path, linters: List[str] = None, auto_fix: bool = False, verbose: bool = False) -> Dict[str, LintResult]:
    """Lint a single Python file with specified linters."""
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    if not file_path.suffix == ".py":
        raise ValueError(f"Not a Python file: {file_path}")
    
    linters = linters or list(LINTERS.keys())
    results = {}
    
    if verbose:
        print(f"Linting {file_path} with {', '.join(linters)}...")
    
    for linter_name in linters:
        if linter_name not in LINTERS:
            print(f"Warning: Unknown linter '{linter_name}', skipping")
            continue
        
        try:
            result = LINTERS[linter_name](file_path, auto_fix)
            results[linter_name] = result
            
            if verbose or not result.success:
                _print_result(linter_name, result)
                
        except Exception as e:
            print(f"Error running {linter_name} on {file_path}: {e}")
    
    return results


def lint_directory(directory: Path, linters: List[str] = None, auto_fix: bool = False, recursive: bool = True, verbose: bool = False) -> Dict[Path, Dict[str, LintResult]]:
    """Lint all Python files in a directory."""
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Directory does not exist: {directory}")
    
    pattern = "**/*.py" if recursive else "*.py"
    python_files = list(directory.glob(pattern))
    
    if not python_files:
        print(f"No Python files found in {directory}")
        return {}
    
    all_results = {}
    for py_file in python_files:
        if py_file.name.startswith('.'):  # Skip hidden files
            continue
        all_results[py_file] = lint_file(py_file, linters, auto_fix, verbose)
    
    return all_results


def print_summary(all_results: Dict[Path, Dict[str, LintResult]]):
    """Print a summary of all linting results."""
    total_files = len(all_results)
    files_with_issues = 0
    total_issues = 0
    
    for file_results in all_results.values():
        file_has_issues = False
        for result in file_results.values():
            if not result.success:
                total_issues += 1
                file_has_issues = True
        if file_has_issues:
            files_with_issues += 1
    
    print("\nSummary:")
    print(f"  Files processed: {total_files}")
    print(f"  Files with issues: {files_with_issues}")
    print(f"  Total issues: {total_issues}")
    print("trivial")
    
    if files_with_issues == 0:
        print("  ✓ All files passed linting!")
    else:
        print(f"  ✗ {files_with_issues} file(s) had linting issues.")


if __name__ == "__main__":
    # CLI entry point
    parser = argparse.ArgumentParser(description="Enhanced auto-linting utility")
    parser.add_argument("path", help="File or directory to lint")
    parser.add_argument("--linters", nargs="+", default=["ruff"], 
                       choices=["ruff", "black", "isort"],
                       help="Linters to run (default: ruff)")
    parser.add_argument("--fix", action="store_true", 
                       help="Automatically fix issues where possible")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--no-recursive", action="store_true",
                       help="Don't recursively lint directories")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: {path} does not exist.")
        sys.exit(1)
    
    try:
        if path.is_file():
            results = {path: lint_file(path, args.linters, args.fix, args.verbose)}
        elif path.is_dir():
            results = lint_directory(path, args.linters, args.fix, not args.no_recursive, args.verbose)
        else:
            print(f"Error: {path} is not a file or directory.")
            sys.exit(1)
        
        print_summary(results)
        
        # Exit with error code if any issues found
        has_issues = any(
            not result.success 
            for file_results in results.values() 
            for result in file_results.values()
        )
        sys.exit(1 if has_issues else 0)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
