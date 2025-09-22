import os
import re

_env_store = {}  # store only loaded .env variables

def load_env(file_path=".env"):
    """Load key-value pairs from a .env file into _env_store and os.environ."""
    global _env_store
    _env_store = {}
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            key = key.strip()
            _env_store[key] = value
            os.environ[key] = value

def get_env(key, default=None, required=False, type=str, regex=None, choices=None, min_val=None, max_val=None):
    """Get an environment variable with optional validation."""
    value = _env_store.get(key, os.environ.get(key, default))

    if required and value is None:
        raise KeyError(f"Required environment variable '{key}' is missing")

    if value is not None:
        # Type casting
        try:
            if type is int:
                value = int(value)
            elif type is float:
                value = float(value)
            elif type is bool:
                value = str(value).lower() in ("1", "true", "yes")
            else:
                value = str(value)
        except Exception:
            raise ValueError(f"Environment variable '{key}' could not be converted to {type}")

        # Regex validation
        if regex and not re.match(regex, str(value)):
            raise ValueError(f"Environment variable '{key}' does not match pattern {regex}")

        # Choices validation
        if choices and value not in choices:
            raise ValueError(f"Environment variable '{key}' must be one of {choices}")

        # Range validation
        if isinstance(value, (int, float)):
            if min_val is not None and value < min_val:
                raise ValueError(f"Environment variable '{key}' must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Environment variable '{key}' must be <= {max_val}")

    return value

def env_to_dict():
    """Return only loaded .env variables as a dictionary."""
    return dict(_env_store)

def apply_to_flask(app, file_path=".env"):
    """Apply only loaded .env variables to Flask app.config."""
    load_env(file_path)
    for key, val in _env_store.items():
        app.config[key] = val

def apply_to_django_settings(settings_module, file_path=".env"):
    """Apply only loaded .env variables to Django settings module."""
    load_env(file_path)
    for key, val in _env_store.items():
        setattr(settings_module, key, val)

