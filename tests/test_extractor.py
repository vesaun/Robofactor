import json
import os
import tempfile

from robofactor.refactoring.extractor import extract_large_functions


def test_extract_large_functions_basic():
    """Test basic function extraction with default threshold."""
    test_code = '''def small_function():
    return "small"

def medium_function():
    """A medium function."""
    result = []
    for i in range(10):
        result.append(i)
    return result

def large_function():
    """This is a large function that exceeds 50 lines."""
    data = []
    
    # Phase 1: Generate data
    for i in range(100):
        if i % 2 == 0:
            data.append(i * 2)
        elif i % 3 == 0:
            data.append(i * 3)
        elif i % 5 == 0:
            data.append(i * 5)
        else:
            data.append(i)
    
    # Phase 2: Process data
    processed = []
    for item in data:
        if item < 50:
            processed.append(item * 1.1)
        elif item < 100:
            processed.append(item * 1.2)
        else:
            processed.append(item * 1.5)
    
    # Phase 3: Calculate statistics
    total = sum(processed)
    count = len(processed)
    average = total / count if count > 0 else 0
    minimum = min(processed) if processed else 0
    maximum = max(processed) if processed else 0
    
    # Phase 4: Create result
    result = {
        'total': total,
        'count': count,
        'average': average,
        'min': minimum,
        'max': maximum,
        'data': processed
    }
    
    # Phase 5: Validation
    if not result:
        raise ValueError("No result generated")
    
    return result
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path, min_lines=40)
        
        assert len(functions) == 1
        assert functions[0]["function_name"] == "large_function"
        assert functions[0]["line_count"] >= 40
        assert "def large_function():" in functions[0]["code"]
        assert "return result" in functions[0]["code"]
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_custom_threshold():
    """Test function extraction with custom threshold."""
    test_code = '''def tiny_function():
    return 1

def small_function():
    """A small function."""
    x = 1
    y = 2
    z = x + y
    return z

def medium_function():
    """A medium function that should be extracted with threshold 5."""
    result = []
    for i in range(10):
        if i % 2 == 0:
            result.append(i)
        else:
            result.append(i * 2)
    
    processed = []
    for item in result:
        processed.append(item + 1)
    
    return processed
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path, min_lines=5)
        
        assert len(functions) == 2
        function_names = [f["function_name"] for f in functions]
        assert "small_function" in function_names
        assert "medium_function" in function_names
        assert "tiny_function" not in function_names
        
        # Should be sorted by line count (descending)
        assert functions[0]["line_count"] >= functions[1]["line_count"]
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_excludes_class_methods():
    """Test that class methods are excluded from extraction."""
    test_code = '''def top_level_function():
    """This is a top-level function that should be extracted."""
    result = []
    for i in range(20):
        if i % 2 == 0:
            result.append(i * 2)
        else:
            result.append(i * 3)
    
    processed = []
    for item in result:
        if item > 10:
            processed.append(item + 1)
        else:
            processed.append(item - 1)
    
    return processed

class TestClass:
    def large_method(self):
        """This method should NOT be extracted."""
        data = []
        for i in range(100):
            if i % 2 == 0:
                data.append(i * 2)
            elif i % 3 == 0:
                data.append(i * 3)
            else:
                data.append(i)
        
        processed = []
        for item in data:
            processed.append(item * 1.5)
        
        return processed
    
    def another_large_method(self):
        """Another method that should NOT be extracted."""
        result = {}
        for i in range(50):
            if i % 2 == 0:
                result[f"key_{i}"] = i * 2
            else:
                result[f"key_{i}"] = i * 3
        
        return result

def another_top_level():
    """Another top-level function that should be extracted."""
    values = []
    for i in range(15):
        values.append(i ** 2)
    
    # Add some processing to make it longer
    processed = []
    for val in values:
        if val > 25:
            processed.append(val * 2)
        else:
            processed.append(val)
    
    return sum(processed)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path, min_lines=10)
        
        # Should only extract top-level functions, not class methods
        function_names = [f["function_name"] for f in functions]
        assert "top_level_function" in function_names
        assert "another_top_level" in function_names
        assert "large_method" not in function_names
        assert "another_large_method" not in function_names
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_json_output():
    """Test JSON output functionality."""
    test_code = '''def function_one():
    """First function."""
    data = []
    for i in range(25):
        data.append(i * 2)
    
    result = sum(data)
    return result

def function_two():
    """Second function."""
    values = {}
    for i in range(30):
        values[f"key_{i}"] = i ** 2
    
    total = sum(values.values())
    return total
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(test_code)
        temp_path = temp_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
        json_path = json_file.name
    
    try:
        functions = extract_large_functions(temp_path, min_lines=5, output_file=json_path)
        
        # Check that JSON file was created
        assert os.path.exists(json_path)
        
        # Read and verify JSON content
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        assert len(json_data) == 2
        assert json_data == functions
        
        # Verify JSON structure
        for func in json_data:
            assert "function_name" in func
            assert "line_count" in func
            assert "code" in func
            assert isinstance(func["line_count"], int)
            assert isinstance(func["code"], str)
    finally:
        os.unlink(temp_path)
        if os.path.exists(json_path):
            os.unlink(json_path)


def test_extract_large_functions_preserves_formatting():
    """Test that original formatting is preserved in extracted code."""
    test_code = '''def formatted_function():
    """A function with specific formatting."""
    # This comment should be preserved
    x = [
        1, 2, 3,
        4, 5, 6
    ]
    
    y = {
        'key1': 'value1',
        'key2': 'value2'
    }
    
    for item in x:
        if item % 2 == 0:
            print(f"Even: {item}")
        else:
            print(f"Odd: {item}")
    
    return y
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path, min_lines=5)
        
        assert len(functions) == 1
        extracted_code = functions[0]["code"]
        
        # Check that formatting is preserved
        assert "# This comment should be preserved" in extracted_code
        assert "x = [\n        1, 2, 3," in extracted_code
        assert "'key1': 'value1'," in extracted_code
        assert 'print(f"Even: {item}")' in extracted_code
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_empty_file():
    """Test handling of empty files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path)
        assert functions == []
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_no_large_functions():
    """Test file with only small functions."""
    test_code = '''def small_one():
    return 1

def small_two():
    return 2

def small_three():
    x = 1 + 2
    return x
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path)
        assert functions == []
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_sorting():
    """Test that functions are sorted by line count in descending order."""
    test_code = '''def medium_function():
    """Medium function."""
    data = []
    for i in range(10):
        data.append(i)
    
    result = sum(data)
    return result

def large_function():
    """Large function."""
    values = []
    for i in range(50):
        if i % 2 == 0:
            values.append(i * 2)
        elif i % 3 == 0:
            values.append(i * 3)
        else:
            values.append(i)
    
    processed = []
    for val in values:
        if val > 25:
            processed.append(val + 1)
        else:
            processed.append(val - 1)
    
    total = sum(processed)
    average = total / len(processed)
    return {'total': total, 'average': average}

def small_function():
    """Small function."""
    return "small"
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        functions = extract_large_functions(temp_path, min_lines=5)
        
        # Should be sorted by line count (descending)
        assert len(functions) >= 2
        for i in range(len(functions) - 1):
            assert functions[i]["line_count"] >= functions[i + 1]["line_count"]
        
        # Largest function should be first
        assert functions[0]["function_name"] == "large_function"
    finally:
        os.unlink(temp_path)


def test_extract_large_functions_error_handling():
    """Test error handling for invalid files."""
    # Test non-existent file
    try:
        extract_large_functions("/path/that/does/not/exist.py")
        assert False, "Should have raised an exception"
    except RuntimeError as e:
        assert "Error processing file" in str(e)
    
    # Test invalid Python syntax
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def invalid_syntax(\n    # Missing closing parenthesis")
        temp_path = f.name
    
    try:
        extract_large_functions(temp_path)
        assert False, "Should have raised an exception"
    except RuntimeError as e:
        assert "Error processing file" in str(e)
    finally:
        os.unlink(temp_path)