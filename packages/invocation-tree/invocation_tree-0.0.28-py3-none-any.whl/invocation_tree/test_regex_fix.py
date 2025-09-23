import sys
sys.path.append('/home/bterwijn/projects/invocation_tree/invocation_tree')
from regex_set import Regex_Set

# Test the fix
class_fun_name = 'Jugs.copy'
ignore_calls = {'J.*'}

regset_ignore_calls = Regex_Set(ignore_calls)
result = regset_ignore_calls.match(class_fun_name, ignore_calls)

print(f"class_fun_name: '{class_fun_name}'")
print(f"ignore_calls: {ignore_calls}")
print(f"match result: {result}")

# Let's also test the compiled pattern
print(f"compiled pattern: {regset_ignore_calls.compiled_pattern.pattern}")

# Test a few more cases
test_cases = [
    ('Jugs.copy', True),
    ('J.test', True), 
    ('Something.else', False),
    ('AnotherClass.method', False)
]

print("\nTest cases:")
for test_string, expected in test_cases:
    result = regset_ignore_calls.match(test_string, ignore_calls)
    status = "✓" if result == expected else "✗"
    print(f"  {status} '{test_string}' -> {result} (expected {expected})")