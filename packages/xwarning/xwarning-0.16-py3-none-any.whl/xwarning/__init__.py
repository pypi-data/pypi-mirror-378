# from .xwarning import warn, warning, configure  # optional shortcut exports
# xwarning/__init__.py

from .xwarning import (
    warn,
    warning,
    configure,
    WarningPrinter,
    xwarnings,
    xwarning,
)

# Export warning classes for direct use
from warnings import (
    Warning,
    UserWarning,
    DeprecationWarning,
    FutureWarning,
    RuntimeWarning,
    SyntaxWarning,
    ImportWarning,
    UnicodeWarning,
)

# Make it available at package level
__all__ = [
    'warn',
    'warning', 
    'configure',
    'WarningPrinter',
    'xwarnings',
    'xwarning',
    # Warning classes
    'Warning',
    'UserWarning',
    'DeprecationWarning',
    'FutureWarning',
    'RuntimeWarning',
    'SyntaxWarning',
    'ImportWarning',
    'UnicodeWarning',
]
