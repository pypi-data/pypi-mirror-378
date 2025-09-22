# six_totp

`six_totp` is a lightweight Python library for generating 6-digit passcodes.

## Features

- Generates a secure, 6-digit one-time passcode with `generate_totp()`
- Easy to use with a single function call
- No external dependencies

## Installation

Install via PyPI:

```bash
pip install six_totp
```

## Usage:
```python
from six_totp.core import generate_totp

code = generate_totp()
print(code)
# example output: 075231
```

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request. [Repository link](https://github.com/GeorgievIliyan/six_totp)

## License
This project is licensed under the MIT License