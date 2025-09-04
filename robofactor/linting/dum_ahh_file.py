# test_linting_file.py

import sys, os # E231: missing whitespace after ',', F401: 'os' imported but unused

def my_function(arg1,arg2): # E225: missing whitespace around operator, E251: unexpected spaces around keyword / parameter equals
    """A function that does something."""
    # F841: local variable 'unused_variable' is assigned to but never used
    unused_variable = "I'm not used"
    # E701: multiple statements on one line (colon)
    if arg1 > arg2: print("arg1 is greater");
    else:
            # E111: indentation is not a multiple of 4
            print("arg2 is greater or equal")

    # E501: line too long (82 > 79 characters)
    a_very_long_variable_name_just_to_make_this_line_exceed_the_limit_for_testing = arg1 + arg2

    # W292: no newline at end of file
    # E302: expected 2 blank lines, found 1
    return a_very_long_variable_name_just_to_make_this_line_exceed_the_limit_for_testing

class MyClass: # C0114: Missing module docstring, C0116: Missing class docstring
    def __init__(self, value):
        self.value=value # E225: missing whitespace around operator

    def another_method(self, x,y): # C0116: Missing function docstring, E225: missing whitespace around operator
        # F821: undefined name 'undefined_variable'
        return self.value + x+y + undefined_variable

# E305: expected 2 blank lines after class or function definition, found 1
print( my_function(5, 3) ) # E211: whitespace before '('