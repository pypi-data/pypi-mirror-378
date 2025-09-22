# xwarning

`xwarning` is a Python module that enhances the default `warnings` system with beautiful, color-coded warning messages and icons. It automatically detects and uses the best available rendering backend: **Rich** for the best experience, **make_colors** as a fallback, or **ANSI colors** when neither is available.

## Features

- 🎨 **Multiple Rendering Backends**: 
  - **Rich** (preferred): Full-featured beautiful output with rich formatting
  - **make_colors** (fallback): Good color support with simpler API
  - **ANSI colors** (minimal): Basic color support, works everywhere
- 🔄 **Dual API Support**: 
  - Python-style: `warn("message", UserWarning)`
  - String-based: `warn("message", type="user")`
- 📦 **Multiple Import Styles**: Flexible import options for different coding preferences
- 🚨 **Built-in Warning Types**: Support for all standard Python warning categories
- 📝 **File Logging**: Optional logging to files with timestamps
- ⚙️ **Fully Configurable**: Customize appearance, colors, and icons
- 🔌 **Drop-in Replacement**: Works as a replacement for Python's built-in warnings
- 🎯 **Warning Filtering**: Built-in support for filtering warnings
- 🔧 **Zero Required Dependencies**: Works with just Python standard library

## Dependencies & Backends

`xwarning` automatically detects and uses the best available backend:

| Backend | Priority | Features | Installation |
|---------|----------|----------|-------------|
| **Rich** | 1st (Best) | Full rich text formatting, best colors | `pip install rich` |
| **make_colors** | 2nd (Good) | Good color support, lightweight | `pip install make_colors` |
| **ANSI** | 3rd (Basic) | Basic colors, no extra dependencies | Built-in |

```python
from xwarning import get_backend_info
print(f"Using backend: {get_backend_info()}")  # rich, make_colors, or ansi
```

## Supported Warning Types

| Warning Type | Icon | String Type | Class |
|--------------|------|-------------|-------|
| DeprecationWarning | ⚠️ | `"deprecated"` | `DeprecationWarning` |
| UserWarning | 💡 | `"user"` | `UserWarning` |
| FutureWarning | 🕒 | `"future"` | `FutureWarning` |
| RuntimeWarning | 🚨 | `"runtime"` | `RuntimeWarning` |
| SyntaxWarning | 📜 | `"syntax"` | `SyntaxWarning` |
| ImportWarning | 📦 | `"import"` | `ImportWarning` |
| UnicodeWarning | 🔤 | `"unicode"` | `UnicodeWarning` |
| Warning (Generic) | ❗ | `"general"` | `Warning` |

## Installation

### Basic Installation (Works Everywhere)
```bash
pip install xwarning
```
This installs xwarning with ANSI color support only.

### Recommended Installation (Best Experience)
```bash
pip install xwarning[rich]
# or install rich separately
pip install xwarning rich
```

### Alternative Installation (Good Experience)
```bash
pip install xwarning make_colors
```

### Check Your Backend
```python
from xwarning import get_backend_info, warn, UserWarning

print(f"Backend: {get_backend_info()}")
warn("Testing colors and formatting", UserWarning)
```

## Quick Start

```python
from xwarning import warn, UserWarning, RuntimeWarning

# Python warnings style (NEW!)
warn("This feature will be removed", DeprecationWarning)
warn("Processing completed", UserWarning)

# String-based style (Original)
warn("This is deprecated!", type="deprecated")
warn("User notification", type="user")
```

## Usage Examples

### Basic Usage - Multiple API Styles

```python
from xwarning import warn, warning, UserWarning, RuntimeWarning

# Method 1: Python warnings-style API (Recommended)
warn("Database connection slow", RuntimeWarning)
warn("This method is deprecated", DeprecationWarning)
warn("Task completed successfully", UserWarning)

# Method 2: String-based API (Original)
warn("Database connection slow", type="runtime")
warn("This method is deprecated", type="deprecated")
warn("Task completed successfully", type="user")

# Method 3: Explicit parameter
warn("Processing warning", category=UserWarning)

# Method 4: Using 'warning' alias
warning("Alternative function name", UserWarning)
```

### Import Styles

```python
# Style 1: Direct import
import xwarning
xwarning.warn("Direct import usage", xwarning.UserWarning)

# Style 2: Import specific functions
from xwarning import warn, UserWarning, configure
warn("Imported function", UserWarning)

# Style 3: Using aliases for different coding styles
from xwarning import xwarnings
xwarnings.warn("Using xwarnings alias", UserWarning)

# Style 4: Alternative alias
from xwarning import xwarning
xwarning.warn("Using xwarning alias", UserWarning)
```

### All Warning Types Examples

```python
from xwarning import warn

# Using Warning Classes (Python-style)
warn("Function deprecated in v2.0", DeprecationWarning)      # ⚠️  DEPRECATED
warn("Task completed", UserWarning)                          # 💡 USER  
warn("API will change in v3.0", FutureWarning)               # 🕒 FUTURE
warn("Performance degraded", RuntimeWarning)                 # 🚨 RUNTIME
warn("Syntax issue detected", SyntaxWarning)                 # 📜 SYNTAX
warn("Module import slow", ImportWarning)                    # 📦 IMPORT
warn("Unicode handling issue", UnicodeWarning)               # 🔤 UNICODE
warn("Generic warning", Warning)                             # ❗ WARNING

# Using String Types (Original style)
warn("Function deprecated in v2.0", type="deprecated")
warn("Task completed", type="user") 
warn("API will change in v3.0", type="future")
warn("Performance degraded", type="runtime")
warn("Syntax issue detected", type="syntax")
warn("Module import slow", type="import")
warn("Unicode handling issue", type="unicode")
warn("Generic warning", type="general")
```

### Configuration Options

```python
from xwarning import configure, warn, UserWarning

# Customize appearance (works with all backends)
configure(
    show_icon=True,      # Show/hide emoji icons
    show_color=True,     # Enable/disable colors
    show_line=True       # Show/hide file location
)

warn("Customized warning display", UserWarning)

# Disable icons only
configure(show_icon=False)
warn("Warning without icon", UserWarning)

# Disable colors (good for logs or unsupported terminals)
configure(show_color=False, show_icon=True)
warn("Monochrome warning", UserWarning)

# Best for production logs
configure(show_color=False, show_icon=False, show_line=True)
warn("Production log format", UserWarning)
```

### File Logging

```python
from xwarning import configure, warn, UserWarning

# Log to specific file
configure(log_file="my_warnings.log")
warn("This goes to my_warnings.log", UserWarning)

# Log to system default location
# Windows: %TEMP%/warnings.log
# Linux: /var/log/warnings.log  
configure(log_file=True)
warn("This goes to system default location", UserWarning)

# Disable logging
configure(log_file=None)
warn("This won't be logged", UserWarning)
```

### Advanced Usage - Multiple Independent Instances

```python
from xwarning import WarningPrinter, UserWarning, RuntimeWarning

# Create independent printer instances with auto_hook=False
# Each instance maintains its own configuration
app_printer = WarningPrinter(auto_hook=False)
app_printer.configure(show_icon=False, log_file="app.log")

debug_printer = WarningPrinter(auto_hook=False)  
debug_printer.configure(show_icon=True, show_color=False, log_file="debug.log")

# Each instance uses its own configuration independently
app_printer.warn("App warning - no icons", UserWarning)        # No icon shown
debug_printer.warn("Debug warning - no colors", RuntimeWarning) # Icon shown, no colors

# Global printer remains unaffected
from xwarning import warn
warn("Global warning - uses global config", UserWarning)  # Uses global settings
```

**Key Points:**
- **auto_hook=False**: Creates independent instances that don't interfere with global settings
- **Isolated Configuration**: Each instance respects its own `show_icon`, `show_color`, etc. settings  
- **Separate Logging**: Each instance can log to different files
- **No Global Impact**: Custom instances don't affect the global `warn()` function behavior

### Warning Filtering

```python
from xwarning import warn, UserWarning, RuntimeWarning
import xwarning

# Filter out specific warning types
xwarning.filterwarnings("ignore", category=UserWarning)

warn("This will not be shown", UserWarning)        # Ignored
warn("This will be shown", RuntimeWarning)         # Shown

# Filter by message pattern
xwarning.filterwarnings("ignore", message="deprecated", category=DeprecationWarning)

warn("This deprecated feature", DeprecationWarning)  # Ignored
warn("This old feature", DeprecationWarning)         # Shown
```

### Real-World Examples

```python
from xwarning import warn, configure
from xwarning import DeprecationWarning, UserWarning, RuntimeWarning, FutureWarning

# Configure for production logging
configure(log_file="/var/log/myapp.log", show_color=False)

def process_data(data, use_old_method=False):
    """Example function with various warning scenarios"""
    
    if use_old_method:
        warn("use_old_method parameter is deprecated, use new_method instead", 
             DeprecationWarning)
    
    if len(data) > 1000:
        warn(f"Processing large dataset ({len(data)} items), this may take time", 
             UserWarning)
    
    if len(data) > 10000:
        warn("Large dataset detected, consider using batch processing", 
             RuntimeWarning)
    
    # Simulate API change notification
    warn("The data format will change in v2.0. Update your code accordingly", 
         FutureWarning)
    
    return f"Processed {len(data)} items"

# Multi-application logging with independent instances
from xwarning import WarningPrinter

# Main application warnings
main_app = WarningPrinter(auto_hook=False)
main_app.configure(show_icon=False, show_color=False, log_file="main_app.log")

# Debug system with colors but no file logging  
debug_sys = WarningPrinter(auto_hook=False)
debug_sys.configure(show_icon=True, show_color=True, log_file=None)

# Critical alerts with maximum visibility
alerts = WarningPrinter(auto_hook=False)
alerts.configure(show_icon=True, show_color=True, show_line=True, log_file="alerts.log")

# Usage - each respects its own configuration
main_app.warn("Database connection timeout", RuntimeWarning)  # Plain text, logged
debug_sys.warn("Cache miss detected", UserWarning)           # Colored, not logged
alerts.warn("Memory usage critical", RuntimeWarning)         # Full format, logged
```

### Integration with Existing Code

```python
# Easy migration from standard warnings
# Change this:
import warnings
warnings.warn("Something happened", UserWarning)

# To this:
from xwarning import warn, UserWarning
warn("Something happened", UserWarning)  # Now with rich formatting!

# Or keep it simple:
from xwarning import warn
warn("Something happened", type="user")
```

## Backend Comparison

### Rich Backend (Recommended)
```python
# Best formatting and colors
⚠️  DEPRECATED: Function deprecated in v2.0 [example.py:10]
💡 USER: Task completed successfully [example.py:11]
```

### make_colors Backend  
```python
# Good colors, simpler formatting
⚠️  DEPRECATED: Function deprecated in v2.0 [example.py:10]
💡 USER: Task completed successfully [example.py:11]
🕒 FUTURE: API will change in v3.0 [example.py:12]
🚨 RUNTIME: Performance degraded [example.py:13]
📜 SYNTAX: Syntax issue detected [example.py:14]
📦 IMPORT: Module import slow [example.py:15]
🔤 UNICODE: Unicode handling issue [example.py:16]
❗ WARNING: Generic warning [example.py:17]
```

### ANSI Backend
```python
# Basic colors, works everywhere
⚠️  DEPRECATED: Function deprecated in v2.0 [example.py:10]
💡 USER: Task completed successfully [example.py:11]
```

[![Example Outputs](https://github.com/cumulus13/xwarning/raw/refs/heads/master/example_outputs.png)](https://github.com/cumulus13/xwarning/raw/refs/heads/master/example_outputs.png)

## API Reference

### Functions

- `warn(message, category=None, type=None)` - Main warning function
- `warning(message, category=None, type=None)` - Alias for warn()
- `configure(**kwargs)` - Configure global settings
- `get_backend_info()` - Returns active backend: "rich", "make_colors", or "ansi"

### Configuration Options

- `show_icon: bool` - Show/hide emoji icons (default: True)
- `show_color: bool` - Enable/disable colors (default: True)  
- `show_line: bool` - Show/hide file location (default: True)
- `log_file: str|bool|None` - Log file path, True for default, None to disable

### Classes

- `WarningPrinter` - Core class for custom instances
- All standard Python warning classes are available

### Backends

- **Rich**: Best experience with full formatting (requires: `pip install rich`)
- **make_colors**: Good color support (requires: `pip install make_colors`)
- **ANSI**: Basic colors, no dependencies (built-in)

## Migration Guide

### From Standard Warnings

```python
# Old code
import warnings
warnings.warn("Message", UserWarning)

# New code - Method 1 (Recommended)
from xwarning import warn
warn("Message", UserWarning)

# New code - Method 2 (Alternative)
from xwarning import warn
warn("Message", type="user")
```

### Upgrading from xwarning v1.x

All existing code continues to work! New features:
- Python warnings-style API now supported
- Multiple import styles available
- Enhanced filtering capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License. See [LICENSE](./LICENSE) for details.

## 📄 License

Licensed under the **MIT License**. See [LICENSE](LICENSE).

---

## 👨‍💻 Author

**Hadi Cahyadi**
📧 [cumulus13@gmail.com](mailto:cumulus13@gmail.com)

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)

---

✨ Made with ❤️ by Hadi Cahyadi for colorful terminal experiences!

---

## Changelog

### v0.16 (Latest)
- 🔧 **Fixed custom instances**: Custom `WarningPrinter` instances now properly respect their individual configurations
- 🎯 **Independent behavior**: `auto_hook=False` instances are truly isolated from global settings
- 📝 **Improved examples**: Better documentation for multi-instance scenarios
- 🐛 **Bug fixes**: Resolved issue where custom instances ignored `show_icon`, `show_color` settings

### v0.15
- ✨ Added Python warnings-style API support
- ✨ Multiple import style options
- ✨ Enhanced warning filtering
- ✨ **Multi-backend support**: Rich → make_colors → ANSI fallback
- ✨ Zero required dependencies (works with just Python standard library)
- ✨ `get_backend_info()` function to check active backend
- 🔄 Backward compatible with v1.x
- 📝 Improved documentation and examples
