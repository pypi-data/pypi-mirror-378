# jq-utils

JQ-style dictionary and list access for Python. Access nested data structures using simple path strings.

## Installation

```bash
pip install jq-utils
```

## Quick Start

```python
from jq_utils import jq_get, jq_set, jq_exists, jq_delete

data = {
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ],
    "settings": {
        "theme": "dark",
        "notifications": {"email": True, "sms": False}
    }
}

# Get values
name = jq_get(data, "users[0].name")  # "Alice"
email = jq_get(data, "settings.notifications.email")  # True

# Set values
data = jq_set(data, "users[1].city", "New York")

# Check existence
exists = jq_exists(data, "settings.theme")  # True

# Delete values
data = jq_delete(data, "settings.notifications.sms")
```

## Features

- **Simple path syntax** - Use dot notation and array indices
- **Safe access** - Returns default values instead of raising errors
- **Deep operations** - Get, set, check, and delete at any depth
- **Mixed structures** - Works with nested dictionaries and lists
- **Zero dependencies** - Pure Python implementation

## Path Syntax

| Path | Description |
|------|-------------|
| `"key"` | Simple key access |
| `"key1.key2"` | Nested dictionary access |
| `"[0]"` | Array index access |
| `"users[0]"` | Key with array index |
| `"users[0].name"` | Mixed access |
| `"key1.key2[3].key4"` | Complex nested access |

## API Reference

### jq_get(data, path, default=None)

Get value from data structure using path notation.

```python
value = jq_get(data, "users[0].email", default="not found")
```

### jq_set(data, path, value)

Set value in data structure. Creates missing intermediate structures.

```python
data = jq_set(data, "users[0].verified", True)
```

### jq_exists(data, path)

Check if path exists in data structure.

```python
if jq_exists(data, "users[0].email"):
    print("Email exists")
```

### jq_delete(data, path)

Delete value at path from data structure.

```python
data = jq_delete(data, "users[0].temporary_field")
```

## Examples

### Working with nested data

```python
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    },
    "servers": [
        {"name": "web1", "ip": "192.168.1.1"},
        {"name": "web2", "ip": "192.168.1.2"}
    ]
}

# Get nested values
host = jq_get(config, "database.host")  # "localhost"
web1_ip = jq_get(config, "servers[0].ip")  # "192.168.1.1"
username = jq_get(config, "database.credentials.username")  # "admin"

# Update configuration
config = jq_set(config, "database.port", 3306)
config = jq_set(config, "servers[2]", {"name": "web3", "ip": "192.168.1.3"})

# Add new settings
config = jq_set(config, "cache.redis.host", "localhost")
```

### Safe access with defaults

```python
data = {"name": "Alice"}

# Safe access - returns None instead of error
age = jq_get(data, "age")  # None
city = jq_get(data, "address.city", default="Unknown")  # "Unknown"

# Check before access
if jq_exists(data, "email"):
    email = jq_get(data, "email")
else:
    print("No email found")
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.