# as_envhelper

Python library to load `.env` files with validation, multiline support, large file handling, Flask/Django integration.

## Quick Start
```python
from as_envhelper import load_env, get_env
load_env([".env"])
PORT = get_env("PORT",5000)
