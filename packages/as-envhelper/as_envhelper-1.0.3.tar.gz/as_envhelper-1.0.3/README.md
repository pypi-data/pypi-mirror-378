# as_envhelper

A simple, powerful, and beginner-friendly environment variable loader for Python.  
Read key-value pairs from a `.env` file and set them as environment variables.  
Built by **ASWIN KUMAR K**.

---

## 🚀 Installation

```bash
pip install as_envhelper
```

---

## ⚡ Usage

### Basic usage

```python
from as_envhelper import load_env, get_env

# Load variables from a .env file
load_env(".env")

# Access a variable
db_user = get_env("DB_USER")
print("Database User:", db_user)
```

### Get all environment variables as a dictionary

```python
from as_envhelper import env_to_dict

env_dict = env_to_dict()
print(env_dict)
```

---

## 🐍 Flask Integration

```python
from flask import Flask
from as_envhelper import apply_to_flask

app = Flask(__name__)

# Load .env variables and apply to Flask config
apply_to_flask(app, ".env")

print(app.config["DB_USER"])
```

---

## 🐍 Django Integration

```python
# In your Django settings.py
from as_envhelper import apply_to_django_settings
import sys

# Apply .env variables to Django settings module
apply_to_django_settings(sys.modules[__name__], ".env")

print(DB_USER)
```

---

## ✨ Features

* Easy `.env` file loading
* Safe variable access with optional type casting and validation
* Enterprise-ready (regex, numeric ranges, choices)
* Multiline and nested variable support (basic)
* Flask and Django integration
* Works on all major OS

---

## ⚠️ Limitations

* Advanced multiline parsing may be limited
* Direct overwrite of OS environment variables if same keys exist
* Users must manually create `.env` files
* Less community adoption initially (new library)

---

## 👨‍💻 Author

**ASWIN KUMAR K**  
Email: [aswinkumar06k@gmail.com](mailto:aswinkumar06k@gmail.com)  
GitHub: [https://github.com/Aswin-Kumar24072003/as_envhelper](https://github.com/Aswin-Kumar24072003/as_envhelper)

---

## 📄 License

**GPLv3** – See [LICENSE](LICENSE) file for details

---