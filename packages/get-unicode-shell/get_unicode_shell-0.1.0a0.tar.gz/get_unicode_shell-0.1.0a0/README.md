# `get-unicode-shell`

A cross-platform utility to get the current SHELL as a Unicode string.

## Features

- Gets the current SHELL based on the operating system and environment variables.
- Handles both NT (`COMSPEC`) and POSIX (`SHELL`) conventions.
- Provides reliable fallbacks (`cmd.exe` on NT, `/bin/sh` on POSIX).
- Fully compatible with Python 2 and 3.

## Usage

```python
# coding=utf-8
from __future__ import print_function
from get_unicode_shell import get_unicode_shell

print(u'Detected shell:', get_unicode_shell())
```

## Installation

```bash
pip install get-unicode-shell
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).