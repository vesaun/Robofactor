import pytest
from pathlib import Path
from robofactor.linting.auto_lint import lint_file, lint_directory, LintResult


def test_lint_file_returns_results(tmp_path):
    """Test that lint_file returns dict of results."""
    good_file = tmp_path / "good.py"
    good_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    
    results = lint_file(good_file, linters=['ruff'])
    assert isinstance(results, dict)
    assert 'ruff' in results
    assert isinstance(results['ruff'], LintResult)


def test_lint_file_with_specific_linters(tmp_path):
    """Test linting with specific linters."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass\n")
    
    results = lint_file(test_file, linters=['ruff', 'black'])
    assert 'ruff' in results
    assert 'black' in results
    assert len(results) == 2


def test_lint_file_auto_fix(tmp_path):
    """Test auto-fix functionality."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test( ):\n    x=1\n    return x\n")
    
    results = lint_file(test_file, linters=['ruff'], auto_fix=True)
    assert 'ruff' in results


def test_lint_file_nonexistent():
    """Test linting nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        lint_file(Path("nonexistent.py"))


def test_lint_file_non_python(tmp_path):
    """Test linting non-Python file raises error."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Hello world")
    
    with pytest.raises(ValueError, match="Not a Python file"):
        lint_file(txt_file)


def test_lint_directory_returns_results(tmp_path):
    """Test that lint_directory returns nested dict of results."""
    good_file = tmp_path / "good.py"
    good_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def bad( ):\n    x=1\n    return x\n")
    
    results = lint_directory(tmp_path, linters=['ruff'])
    assert isinstance(results, dict)
    assert len(results) == 2
    
    # Each file should have results
    for file_results in results.values():
        assert isinstance(file_results, dict)
        assert 'ruff' in file_results
        assert isinstance(file_results['ruff'], LintResult)


def test_lint_directory_empty(tmp_path):
    """Test linting empty directory."""
    results = lint_directory(tmp_path)
    assert results == {}


def test_lint_directory_no_python_files(tmp_path):
    """Test directory with no Python files."""
    (tmp_path / "readme.txt").write_text("Hello")
    (tmp_path / "config.json").write_text("{}")
    
    results = lint_directory(tmp_path)
    assert results == {}


def test_lint_directory_recursive(tmp_path):
    """Test recursive directory linting."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    
    (tmp_path / "file1.py").write_text("def func1(): pass\n")
    (subdir / "file2.py").write_text("def func2(): pass\n")
    
    # Recursive (default)
    results = lint_directory(tmp_path, recursive=True)
    assert len(results) == 2
    
    # Non-recursive
    results = lint_directory(tmp_path, recursive=False)
    assert len(results) == 1


def test_lint_directory_skips_hidden_files(tmp_path):
    """Test that hidden files are skipped."""
    (tmp_path / "normal.py").write_text("def func(): pass\n")
    (tmp_path / ".hidden.py").write_text("def func(): pass\n")
    
    results = lint_directory(tmp_path)
    assert len(results) == 1
    assert any("normal.py" in str(path) for path in results.keys())


def test_lint_directory_nonexistent():
    """Test linting nonexistent directory raises error."""
    with pytest.raises(ValueError, match="Directory does not exist"):
        lint_directory(Path("nonexistent"))


def test_unknown_linter_warning(tmp_path, capsys):
    """Test warning for unknown linter."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass\n")
    
    results = lint_file(test_file, linters=['unknown_linter'])
    captured = capsys.readouterr()
    assert "Warning: Unknown linter 'unknown_linter', skipping" in captured.out
    assert results == {}


@pytest.fixture
def mock_subprocess_success(mocker):
    """Mock successful subprocess calls."""
    return mocker.patch(
        "robofactor.linting.auto_lint.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout="All good", stderr="")
    )


@pytest.fixture
def mock_subprocess_failure(mocker):
    """Mock failing subprocess calls."""
    return mocker.patch(
        "robofactor.linting.auto_lint.subprocess.run", 
        return_value=mocker.Mock(returncode=1, stdout="Found issues", stderr="")
    )


def test_lint_result_success(tmp_path, mock_subprocess_success):
    """Test LintResult when linting succeeds."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass\n")
    
    results = lint_file(test_file, linters=['ruff'])
    result = results['ruff']
    
    assert result.success is True
    assert result.file_path == test_file
    assert result.output == "All good"


def test_lint_result_failure(tmp_path, mock_subprocess_failure):
    """Test LintResult when linting fails."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass\n")
    
    results = lint_file(test_file, linters=['ruff'])
    result = results['ruff']
    
    assert result.success is False
    assert result.file_path == test_file
    assert result.output == "Found issues"


def test_command_timeout(tmp_path, mocker):
    """Test handling of command timeout."""
    from subprocess import TimeoutExpired
    
    mocker.patch(
        "robofactor.linting.auto_lint.subprocess.run",
        side_effect=TimeoutExpired(cmd=["ruff"], timeout=30)
    )
    
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass\n")
    
    results = lint_file(test_file, linters=['ruff'])
    result = results['ruff']
    
    assert result.success is False
    assert result.errors == "Command timed out"


def test_command_not_found(tmp_path, mocker):
    """Test handling of command not found."""
    mocker.patch(
        "robofactor.linting.auto_lint.subprocess.run",
        side_effect=FileNotFoundError()
    )
    
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass\n")
    
    results = lint_file(test_file, linters=['ruff'])
    result = results['ruff']
    
    assert result.success is False
    assert "Command not found: ruff" in result.errors