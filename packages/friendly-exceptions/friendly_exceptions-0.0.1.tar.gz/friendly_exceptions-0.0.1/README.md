# Friendly Exceptions 🐍✨

**Automatic Python error explanations in simple language**

## 🚀 Quick Start

```python
import friendly_exceptions

# Now all errors are explained automatically!
data = {"name": "Alice"}
print(data["age"])  # Get detailed KeyError explanation
```

## ✨ Features

- 🔄 **Automatic interception** - works immediately after import
- 🌍 **2 languages** - Russian and English
- 📚 **25+ error types** - from KeyError to SystemError
- 🧠 **Smart suggestions** - similar variable and attribute recommendations
- 📖 **Documentation links** - direct links to Python docs
- ⚙️ **Flexible configuration** - configure via code or CLI
- 📊 **Detailed logging** - for debugging and monitoring

## 🌍 Multi-language Support

```python
import friendly_exceptions

# Russian (default)
friendly_exceptions.set_language("ru")

# English
friendly_exceptions.set_language("en")
```

## 📋 Supported Errors

### Basic
- KeyError, ValueError, TypeError, AttributeError, IndexError
- FileNotFoundError, ImportError, ZeroDivisionError, NameError
- AssertionError, SyntaxError, IndentationError

### System
- OSError, PermissionError, IsADirectoryError
- SystemError, RuntimeError, NotImplementedError

### Network
- ConnectionError, TimeoutError

### Data
- JSONDecodeError, UnicodeError

### Mathematical
- OverflowError, RecursionError, MemoryError

## ⚙️ Configuration

```python
from friendly_exceptions.config import set_config

# Disable original traceback
set_config("show_original_traceback", False)

# Change language
set_config("language", "en")
```

## 🛠️ CLI

```bash
# Installation
pip install friendly_exceptions

# Test
friendly-exceptions --test

# Configuration
friendly-exceptions --language en
friendly-exceptions --current-language
```

## 📚 Documentation

- [Full Guide](README_FULL.md)
- [Usage Examples](examples/)
- [Tests](tests/)

## 🤝 Contributing

We welcome contributions! Create Issues and Pull Requests.

## 📄 License

MIT License

---

**Friendly Exceptions** - making Python errors understandable for everyone! 🐍✨