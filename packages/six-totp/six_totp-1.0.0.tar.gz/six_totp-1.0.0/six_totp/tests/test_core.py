import pytest
from six_totp.core import generate_totp

def test_returns_string():
    code = generate_totp()
    assert isinstance(code, str)

def test_length_is_six():
    code = generate_totp()
    assert len(code) == 6

def test_only_digits():
    code = generate_totp()
    assert code.isdigit()

def test_multiple_calls_produce_different_values():
    codes = {generate_totp() for _ in range(100)}
    assert len(codes) > 1

if __name__ == "__main__":
    pytest.main()
