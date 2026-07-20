import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.patch_generator import generate_patch, validate_patch
original = 'def foo(x):\n    return x + 1\n'
refactored = 'def foo(x: int) -> int:\n    """Add one."""\n    return x + 1\n'
patch = generate_patch(original, refactored, 'test.py')
result = validate_patch(patch, refactored)
assert result.is_valid is True, f'Expected valid, got: {result}'
assert result.rejection_reason is None
print('patch_generator.py OK')
empty = generate_patch(original, original, 'test.py')
r2 = validate_patch(empty)
assert r2.is_valid is False
assert r2.rejection_reason == 'empty_patch'
print('empty_patch rejection OK')
bad_code = 'def foo(:\n'
patch3 = generate_patch(original, bad_code, 'test.py')
r3 = validate_patch(patch3, bad_code)
assert r3.is_valid is False
assert r3.rejection_reason == 'syntax_error'
print('syntax_error rejection OK')
print('All patch_generator tests passed')
