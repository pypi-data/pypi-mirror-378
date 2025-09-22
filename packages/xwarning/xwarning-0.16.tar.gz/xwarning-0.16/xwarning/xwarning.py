#!/usr/bin/env python3

"""
xwarning - Enhanced Python warnings with beautiful, color-coded output

This module provides a drop-in replacement for Python's warnings system with support
for multiple rendering backends (Rich, make_colors, or ANSI fallback) and enhanced
formatting capabilities.

Example:
    Basic usage:
        >>> from xwarning import warn, UserWarning
        >>> warn("This is a warning message", UserWarning)
        
    String-based API:
        >>> from xwarning import warn
        >>> warn("Deprecated feature", type="deprecated")
        
    Check backend:
        >>> from xwarning import get_backend_info
        >>> print(get_backend_info())  # "rich", "make_colors", or "ansi"
"""

import warnings
import os
from datetime import datetime
import sys
import traceback
import inspect
# from pydebugger.debug import debug
# Try to import rich, fallback to alternatives
try:
    from rich.console import Console
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    try:
        from make_colors import make
        MAKE_COLORS_AVAILABLE = True
    except ImportError:
        if os.getenv('TRACEBACK', '0').lower() in ['1', 'true', 'yes']:
            print(traceback.format_exc())
        MAKE_COLORS_AVAILABLE = False

# ANSI color codes fallback
class ANSIColors:
    """
    ANSI color codes for fallback when rich and make_colors are not available.
    
    This class provides basic color constants for terminal output formatting
    when no external color libraries are available.
    
    Attributes:
        RESET (str): Reset all formatting
        BOLD (str): Bold text formatting
        DIM (str): Dim text formatting
        
        Basic Colors:
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
        
        Bright Colors:
        BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
        BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
        
        Background Colors:
        BG_RED, BG_ORANGE
        
    Example:
        >>> print(f"{ANSIColors.RED}Error message{ANSIColors.RESET}")
        >>> print(f"{ANSIColors.BOLD}{ANSIColors.YELLOW}Warning{ANSIColors.RESET}")
    """
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_ORANGE = '\033[48;5;208m'

class FallbackConsole:
    """
    Fallback console implementation when Rich is not available.
    
    This class provides a minimal console interface that mimics Rich's Console
    behavior for basic printing functionality.
    
    Attributes:
        use_make_colors (bool): Whether make_colors library is available
        
    Example:
        >>> console = FallbackConsole()
        >>> console.print("Hello, World!")
        Hello, World!
    """
    
    def __init__(self):
        """
        Initialize the fallback console.
        
        Automatically detects if make_colors is available for enhanced
        color support.
        """
        self.use_make_colors = MAKE_COLORS_AVAILABLE
        
    def print(self, text_obj):
        """
        Print text object to console.
        
        Args:
            text_obj: Text object to print. Can be a FallbackText instance,
                     string, or any object with __str__ method.
                     
        Example:
            >>> console = FallbackConsole()
            >>> console.print("Simple text")
            >>> 
            >>> from xwarning import FallbackText
            >>> text = FallbackText()
            >>> text.append("Colored text", "red")
            >>> console.print(text)
        """
        # print(f"MAKE_COLORS_AVAILABLE: {MAKE_COLORS_AVAILABLE}")
        if MAKE_COLORS_AVAILABLE:
            print(text_obj)
        elif hasattr(text_obj, '__str__'):
            # print("METHOD [1]")
            print(str(text_obj))
        elif hasattr(text_obj, 'plain'):
            # print("METHOD [2]")
            # If it's a text object with plain text
            print(text_obj.plain)
        else:
            # print("METHOD [3]")
            print(text_obj)

class FallbackText:
    """
    Fallback text formatting when Rich is not available.
    
    This class provides text styling capabilities using either make_colors
    or ANSI color codes as fallback options.
    
    Attributes:
        parts (list): List of formatted text parts
        plain (str): Plain text without formatting
        
    Example:
        >>> text = FallbackText()
        >>> text.append("Warning: ", "bold red")
        >>> text.append("This is important", "yellow")
        >>> print(text)
    """
    
    def __init__(self):
        """
        Initialize an empty text object.
        
        Creates empty containers for both formatted and plain text parts.
        """
        self.parts = []
        self.plain = ""
        
    def append(self, text, style=None):
        """
        Append text with optional styling.
        
        Args:
            text (str): Text to append
            style (str, optional): Style string for formatting. Can be:
                - Rich-style: "bold #FF0000", "#FFFF00", "magenta"
                - make_colors-style: "red,bold", "yellow,bright" 
                - None: No styling applied
                
        The method automatically maps Rich-style strings to appropriate
        make_colors or ANSI equivalents based on available backends.
        
        Example:
            >>> text = FallbackText()
            >>> text.append("Error: ", "bold #FF0000")
            >>> text.append("File not found", "#FFFF00")
            >>> text.append(" [file.py:10]")  # No styling
        """
        if MAKE_COLORS_AVAILABLE and style:
            # Use make_colors for styling
            color_map = {
                "bold #FF0000": "red,bold",
                "#FFFF00": "yellow",
                "magenta": "magenta",
                "#00FFFF": "cyan", 
                "blue": "blue",
                "bold #AAFF00": "green,bold",
                "white on red": "white-red",
                "black on dark_orange": "black-yellow",
                "#FF55FF": "magenta,bright",
                "#FFEB0A": "yellow,bright",
                "#AAAAFF": "blue,bright",
                "#00D1D1": "cyan,bright",
                "#00AAFF": "blue,bright",
                "bold #AAAA00": "yellow,bold",
                "#AA007F": "magenta",
                "#FFAA7F": "yellow,bright",
            }
            color_style = color_map.get(style, "white")
            formatted_text = make(text, color_style)
            self.parts.append(formatted_text)
            self.plain += text
        elif not MAKE_COLORS_AVAILABLE and style:
            # Use ANSI colors as fallback
            ansi_map = {
                "bold #FF0000": ANSIColors.BOLD + ANSIColors.RED,
                "#FFFF00": ANSIColors.YELLOW,
                "magenta": ANSIColors.MAGENTA,
                "#00FFFF": ANSIColors.CYAN,
                "blue": ANSIColors.BLUE,
                "bold #AAFF00": ANSIColors.BOLD + ANSIColors.GREEN,
                "white on red": ANSIColors.WHITE + ANSIColors.BG_RED,
                "black on dark_orange": ANSIColors.BLACK + ANSIColors.BG_ORANGE,
                "#FF55FF": ANSIColors.BRIGHT_MAGENTA,
                "#FFEB0A": ANSIColors.BRIGHT_YELLOW,
                "#AAAAFF": ANSIColors.BRIGHT_BLUE,
                "#00D1D1": ANSIColors.BRIGHT_CYAN,
                "#00AAFF": ANSIColors.BRIGHT_BLUE,
                "bold #AAAA00": ANSIColors.BOLD + ANSIColors.YELLOW,
                "#AA007F": ANSIColors.MAGENTA,
                "#FFAA7F": ANSIColors.BRIGHT_YELLOW,
            }
            ansi_color = ansi_map.get(style, "")
            formatted_text = f"{ansi_color}{text}{ANSIColors.RESET}"
            self.parts.append(formatted_text)
            self.plain += text
        else:
            # No styling available
            self.parts.append(text)
            self.plain += text
    
    def __str__(self):
        """
        Return the formatted text as a string.
        
        Returns:
            str: Formatted text with color codes if styling is available
            
        Example:
            >>> text = FallbackText()
            >>> text.append("Hello ", "red")
            >>> text.append("World", "blue")
            >>> str(text)  # Returns colored string
        """
        return "".join(self.parts)

class WarningPrinter:
    """
    Core warning printer class with configurable output and multi-backend support.
    
    This class handles the formatting and display of warnings using the best
    available backend (Rich, make_colors, or ANSI colors). It provides extensive
    configuration options and automatic Python warnings system integration.
    
    Attributes:
        console: Console instance (Rich.Console or FallbackConsole)
        show_icon (bool): Whether to display emoji icons
        show_line (bool): Whether to display file location information
        show_color (bool): Whether to use color formatting
        log_file (str|bool|None): Log file configuration
        
    Example:
        Basic usage:
            >>> printer = WarningPrinter()
            >>> printer.warn("Something went wrong", UserWarning)
            
        Custom configuration:
            >>> printer = WarningPrinter(auto_hook=False)
            >>> printer.configure(show_icon=False, log_file="warnings.log")
            >>> printer.warn("Custom warning", RuntimeWarning)
            
        Multiple instances:
            >>> app_printer = WarningPrinter(auto_hook=False)
            >>> app_printer.configure(show_color=False, log_file="app.log")
            >>> 
            >>> debug_printer = WarningPrinter(auto_hook=False)
            >>> debug_printer.configure(show_icon=True, log_file="debug.log")
    """
    
    def __init__(self, auto_hook=True, log_file=None):
        """
        Initialize the warning printer.
        
        Args:
            auto_hook (bool, optional): Whether to automatically hook into
                Python's warnings system. Defaults to True.
            log_file (str|bool|None, optional): Log file configuration:
                - str: Path to log file
                - True: Use system default location
                - None: No logging
                Defaults to None.
                
        The constructor automatically detects and initializes the best
        available console backend (Rich or fallback).
        
        Example:
            >>> # Auto-hook into Python warnings
            >>> printer = WarningPrinter()
            >>> 
            >>> # Manual control without auto-hook
            >>> printer = WarningPrinter(auto_hook=False, log_file="my.log")
        """
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = FallbackConsole()
            
        self.show_icon = True
        self.show_line = True
        self.show_color = True
        self.log_file = log_file
        if auto_hook:
            self._setup_hook()

    def get_datetime(self):
        """
        Get current datetime formatted for logging.
        
        Returns:
            str: Formatted datetime string in 'YYYY/MM/DD HH:MM:SS.ffffff' format
            
        Example:
            >>> printer = WarningPrinter()
            >>> printer.get_datetime()
            '2024/03/15 14:30:25.123456'
        """
        return datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S.%f')

    def get_logfile(self, logfile=None):
        """
        Get the default log file path based on the operating system.
        
        Args:
            logfile (str, optional): Custom log file path. If provided,
                returns this path unchanged.
                
        Returns:
            str: Log file path. On Windows uses %TEMP%/warnings.log,
                 on other systems uses /var/log/warnings.log
                 
        Example:
            >>> printer = WarningPrinter()
            >>> printer.get_logfile()  # Windows
            'C:\\Users\\User\\AppData\\Local\\Temp\\warnings.log'
            >>> 
            >>> printer.get_logfile()  # Linux
            '/var/log/warnings.log'
            >>> 
            >>> printer.get_logfile("custom.log")
            'custom.log'
        """
        return logfile or os.path.join(os.getenv('TEMP'), 'warnings.log') if 'win32' in sys.platform else os.path.join('/var/log', 'warnings.log')

    def configure(self, **kwargs):
        """
        Configure the warning printer settings.
        
        Args:
            **kwargs: Configuration options:
                - show_icon (bool): Display emoji icons
                - show_line (bool): Display file location info
                - show_color (bool): Enable color formatting
                - log_file (str|bool|None): Log file configuration
                
        Raises:
            AttributeError: If an unknown configuration option is provided
            
        Example:
            >>> printer = WarningPrinter()
            >>> 
            >>> # Basic configuration
            >>> printer.configure(show_icon=False, show_color=True)
            >>> 
            >>> # Production logging setup
            >>> printer.configure(
            ...     show_color=False,
            ...     show_icon=False,
            ...     log_file="/var/log/app-warnings.log"
            ... )
            >>> 
            >>> # Development setup
            >>> printer.configure(
            ...     show_icon=True,
            ...     show_color=True,
            ...     show_line=True,
            ...     log_file=True  # Use system default
            ... )
        """
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)
            elif key == "log_file":
                self.log_file = val
            else:
                raise AttributeError(f"Unknown configuration option: {key}")

    def _setup_hook(self):
        """
        Set up hook into Python's warnings system.
        
        This internal method replaces Python's default warning handler
        with the enhanced xwarning formatter. It respects warning filters
        and integrates seamlessly with existing warning configurations.
        
        The hook automatically filters warnings based on Python's warning
        filter settings and only processes warnings that should be displayed.
        
        Note:
            This method is called automatically when auto_hook=True in __init__.
            Manual calling is typically not necessary.
        """
        def custom_warning(message, category, filename, lineno, file=None, line=None):
            try:
                # Check if this warning is filtered
                if any(
                    issubclass(category, filt[2]) and filt[0] == "ignore"
                    for filt in warnings.filters
                ):
                    return
            except Exception:
                pass
            self._print(message, category, filename, lineno)

        warnings.showwarning = custom_warning
        warnings.simplefilter("default")

    def _get_icon(self, category):
        """
        Get the emoji icon for a warning category.
        
        Args:
            category (type): Warning class (e.g., UserWarning, DeprecationWarning)
            
        Returns:
            str: Unicode emoji character appropriate for the warning type
            
        Example:
            >>> printer = WarningPrinter()
            >>> printer._get_icon(UserWarning)
            '💡'
            >>> printer._get_icon(DeprecationWarning)
            '⚠️'
            >>> printer._get_icon(RuntimeWarning)
            '🚨'
        """
        icons = {
            DeprecationWarning: "⚠️",
            UserWarning: "💡",
            FutureWarning: "🕒",
            RuntimeWarning: "🚨",
            SyntaxWarning: "📜",
            ImportWarning: "📦",
            UnicodeWarning: "🔤",
            Warning: "❗",
        }
        return icons.get(category, "⚠️")

    def _get_style(self, category):
        """
        Get the color styles for a warning category.
        
        Args:
            category (type): Warning class (e.g., UserWarning, DeprecationWarning)
            
        Returns:
            list: Two-element list containing [primary_style, secondary_style]
                  where styles are Rich-compatible color strings
                  
        The primary style is used for the warning label and icon,
        while the secondary style is used for the warning message.
        
        Example:
            >>> printer = WarningPrinter()
            >>> primary, secondary = printer._get_style(UserWarning)
            >>> print(primary)    # "#FFFF00"
            >>> print(secondary)  # "#FFEB0A"
            >>> 
            >>> primary, secondary = printer._get_style(DeprecationWarning)
            >>> print(primary)    # "bold #FF0000"
            >>> print(secondary)  # "#FF55FF"
        """
        styles1 = {
            DeprecationWarning: "bold #FF0000",
            UserWarning: "#FFFF00",
            FutureWarning: "magenta",
            RuntimeWarning: "#00FFFF",
            SyntaxWarning: "blue",
            ImportWarning: "bold #AAFF00",
            UnicodeWarning: "white on red",
            Warning: "black on dark_orange",
        }

        styles2 = {
            DeprecationWarning: "#FF55FF",
            UserWarning: "#FFEB0A",
            FutureWarning: "#AAAAFF",
            RuntimeWarning: "#00D1D1",
            SyntaxWarning: "#00AAFF",
            ImportWarning: "bold #AAAA00",
            UnicodeWarning: "#AA007F",
            Warning: "#FFAA7F",
        }
        return [styles1.get(category, "#FFFF00"), styles2.get(category, "bold #55FFFF")]

    def _resolve_category(self, category):
        """
        Resolve warning category from string or class input.
        
        Args:
            category (str|type): Warning category specification:
                - str: String identifier like "user", "deprecated", "runtime"
                - type: Warning class like UserWarning, DeprecationWarning
                - other: Any other input defaults to UserWarning
                
        Returns:
            type: Warning class corresponding to the input
            
        This method enables the dual API support, allowing both string-based
        and class-based warning category specification.
        
        Example:
            >>> printer = WarningPrinter()
            >>> 
            >>> # String-based resolution
            >>> printer._resolve_category("user")
            <class 'UserWarning'>
            >>> printer._resolve_category("deprecated")
            <class 'DeprecationWarning'>
            >>> 
            >>> # Class-based resolution (pass-through)
            >>> printer._resolve_category(RuntimeWarning)
            <class 'RuntimeWarning'>
            >>> 
            >>> # Invalid input (fallback)
            >>> printer._resolve_category("invalid")
            <class 'UserWarning'>
        """
        if isinstance(category, str):
            # String-based mapping (original way)
            category_map = {
                "deprecated": DeprecationWarning,
                "user": UserWarning,
                "future": FutureWarning,
                "runtime": RuntimeWarning,
                "syntax": SyntaxWarning,
                "import": ImportWarning,
                "unicode": UnicodeWarning,
                "general": Warning,
            }
            return category_map.get(category, UserWarning)
        elif isinstance(category, type) and issubclass(category, Warning):
            # Warning class (new way, like Python's warnings)
            return category
        else:
            # Fallback to UserWarning
            return UserWarning

    def warn(self, message, category=None, type=None):
        """
        Issue a warning with enhanced formatting.
        
        This method provides a flexible interface for issuing warnings with
        support for both Python-style and string-based category specification.
        
        Args:
            message (str): Warning message to display
            category (str|type, optional): Warning category as class or string.
                Takes precedence over 'type' parameter.
            type (str, optional): String-based warning type specification.
                Used if 'category' is not provided.
                
        The method supports multiple calling conventions:
        - warn("message", UserWarning)  # Python warnings style
        - warn("message", category=UserWarning)  # Explicit parameter
        - warn("message", type="user")  # String-based style
        - warn("message")  # Defaults to UserWarning
        
        Example:
            >>> printer = WarningPrinter()
            >>> 
            >>> # Python warnings style (recommended)
            >>> printer.warn("Function deprecated", DeprecationWarning)
            >>> printer.warn("Task completed", UserWarning)
            >>> 
            >>> # String-based style
            >>> printer.warn("Performance issue", type="runtime")
            >>> printer.warn("Syntax problem", type="syntax")
            >>> 
            >>> # Explicit parameter style
            >>> printer.warn("Import slow", category=ImportWarning)
            >>> 
            >>> # Default (UserWarning)
            >>> printer.warn("General notification")
        """
        # Determine the warning category
        if category is not None:
            resolved_category = self._resolve_category(category)
        elif type is not None:
            resolved_category = self._resolve_category(type)
        else:
            resolved_category = UserWarning
            
        # For custom instances (auto_hook=False), print directly
        # to respect instance-specific configuration
        
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        
        # Check if this instance is the global printer or a custom one
        if self is _printer:
            # Use Python's warning system for global printer
            warnings.warn(message, resolved_category)
        else:
            # Direct print for custom instances to respect their configuration
            self._print(message, resolved_category, filename, lineno)

    def _print(self, message, category, filename, lineno):
        """
        Internal method to format and print warning messages.
        
        Args:
            message (str): Warning message text
            category (type): Warning class
            filename (str): Source file where warning originated
            lineno (int): Line number where warning originated
            
        This method handles the core formatting logic, including:
        - Icon selection based on warning category
        - Color styling based on configuration and backend
        - File location formatting
        - Log file writing
        
        The method automatically adapts its output format based on the
        available backend (Rich, make_colors, or ANSI) and current
        configuration settings.
        
        Note:
            This is an internal method typically called by the warning
            system hook. Direct calling is usually not necessary.
        """
        label = category.__name__.replace("Warning", "").upper() or "WARNING"
        icon = self._get_icon(category) if self.show_icon else ""
        style1, style2 = self._get_style(category) if self.show_color else ("", "")
        
        if RICH_AVAILABLE:
            output = Text()
            if icon:
                output.append(f"{icon} ", style=style1)
            output.append(f"{label}:", style=style1)
            output.append(" " + str(message), style=style2)
            if self.show_line:
                output.append(f" [{filename}:{lineno}]")
        else:
            output = FallbackText()
            if icon:
                output.append(f"{icon} ", style=style1)
            output.append(f"{label}:", style=style1)
            output.append(" " + str(message), style=style2)
            if self.show_line:
                output.append(f" [{filename}:{lineno}]")
        
        self.console.print(output)

        if self.log_file:
            if isinstance(self.log_file, bool):
                self.log_file = self.get_logfile()
            
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"{self.get_datetime()} {label}: {message} [{filename}:{lineno}]\n")
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[bold red]Log write error:[/bold red] {e}")
                else:
                    print(f"Log write error: {e}")

    @staticmethod    
    def filterwarnings(action, message="", category=Warning, module="", lineno=0, append=False):
        """
        Filter warnings using Python's warning filter system.
        
        This static method provides a convenient proxy to Python's built-in
        warnings.filterwarnings function, allowing users to control which
        warnings are displayed without needing to import the warnings module.
        
        Args:
            action (str): Action to take for matching warnings:
                - "ignore": Don't show the warning
                - "always": Always show the warning  
                - "default": Show warning once per location
                - "module": Show warning once per module
                - "once": Show warning only once
                - "error": Turn warning into an exception
            message (str, optional): Regular expression pattern to match
                warning message. Defaults to "".
            category (type, optional): Warning category to filter.
                Defaults to Warning (matches all).
            module (str, optional): Regular expression pattern to match
                module name. Defaults to "".
            lineno (int, optional): Line number to match. 0 means any line.
                Defaults to 0.
            append (bool, optional): Whether to append to existing filters
                rather than prepending. Defaults to False.
                
        Example:
            >>> # Ignore all UserWarnings
            >>> WarningPrinter.filterwarnings("ignore", category=UserWarning)
            >>> 
            >>> # Ignore deprecation warnings from specific module
            >>> WarningPrinter.filterwarnings(
            ...     "ignore", 
            ...     category=DeprecationWarning,
            ...     module="old_module"
            ... )
            >>> 
            >>> # Turn runtime warnings into errors
            >>> WarningPrinter.filterwarnings("error", category=RuntimeWarning)
            >>> 
            >>> # Show warnings containing "performance" only once
            >>> WarningPrinter.filterwarnings(
            ...     "once", 
            ...     message=".*performance.*"
            ... )
        """
        
        warnings.filterwarnings(action, message=message, category=category, module=module, lineno=lineno, append=append)
                

# ====== Exposed API ======
_printer = WarningPrinter()

def warn(message, category=None, type=None):
    """
    Issue a warning with enhanced formatting (main API function).
    
    This is the primary function for issuing warnings in the xwarning system.
    It provides a flexible interface supporting both Python warnings-style
    and string-based APIs with automatic backend detection and formatting.
    
    Args:
        message (str): Warning message to display
        category (str|type, optional): Warning category specification:
            - type: Warning class (UserWarning, DeprecationWarning, etc.)
            - str: String identifier ("user", "deprecated", etc.)
        type (str, optional): String-based warning type for backward
            compatibility. Used only if category is None.
            
    The function automatically:
    - Detects the best available rendering backend
    - Applies appropriate formatting and colors
    - Respects global configuration settings
    - Integrates with Python's warning filter system
    
    Backend Support:
    - Rich: Full rich text formatting with best visual quality
    - make_colors: Good color support with lightweight footprint  
    - ANSI: Basic color support, works everywhere
    
    Example:
        Python warnings style (recommended):
            >>> from xwarning import warn, UserWarning, DeprecationWarning
            >>> warn("Task completed successfully", UserWarning)
            >>> warn("This function is deprecated", DeprecationWarning)
            >>> warn("Performance may be affected", RuntimeWarning)
            
        String-based style (backward compatible):
            >>> warn("Connection timeout", type="runtime")
            >>> warn("Feature will change", type="future")
            >>> warn("Import taking longer", type="import")
            
        Mixed usage:
            >>> warn("Processing...", category=UserWarning)
            >>> warn("Debug info", type="user")
            >>> warn("Default warning")  # Uses UserWarning
            
        Real-world examples:
            >>> def deprecated_function():
            ...     warn("deprecated_function() is deprecated, use new_function()",
            ...          DeprecationWarning)
            ...     return "old result"
            >>> 
            >>> def process_large_data(data):
            ...     if len(data) > 10000:
            ...         warn(f"Processing {len(data)} items may take time",
            ...              RuntimeWarning)
            ...     return process(data)
    """
    _printer.warn(message, category=category, type=type)

def warning(message, category=None, type=None):
    """
    Issue a warning with enhanced formatting (alias for warn).
    
    This function is an alias for the warn() function, provided for
    users who prefer the "warning" terminology or need compatibility
    with existing code that uses "warning" as the function name.
    
    Args:
        message (str): Warning message to display
        category (str|type, optional): Warning category specification
        type (str, optional): String-based warning type
        
    All functionality is identical to warn(). See warn() documentation
    for complete usage details.
    
    Example:
        >>> from xwarning import warning, UserWarning
        >>> warning("This is a warning message", UserWarning)
        >>> warning("Another message", type="deprecated")
    """
    warn(message, category=category, type=type)

def configure(**kwargs):
    """
    Configure global xwarning settings.
    
    This function configures the global warning printer instance that
    handles all warn() and warning() calls. Settings affect the visual
    appearance, logging behavior, and output format.
    
    Args:
        **kwargs: Configuration options:
            show_icon (bool): Display emoji icons for warnings.
                Default: True
            show_color (bool): Enable color formatting in output.
                Default: True  
            show_line (bool): Display file location (filename:line).
                Default: True
            log_file (str|bool|None): Logging configuration:
                - str: Path to log file
                - True: Use system default location
                - None: Disable logging
                Default: None
                
    The configuration affects all subsequent warning calls and persists
    until changed. Multiple configuration calls can be made to adjust
    settings as needed.
    
    Example:
        Basic configuration:
            >>> from xwarning import configure, warn, UserWarning
            >>> 
            >>> # Disable icons for cleaner output
            >>> configure(show_icon=False)
            >>> warn("Clean warning", UserWarning)
            >>> 
            >>> # Disable colors for plain text logs
            >>> configure(show_color=False)
            >>> warn("Plain text warning", UserWarning)
            
        Production logging setup:
            >>> configure(
            ...     show_icon=False,
            ...     show_color=False,
            ...     log_file="/var/log/application-warnings.log"
            ... )
            >>> warn("Production warning", RuntimeWarning)
            
        Development setup:
            >>> configure(
            ...     show_icon=True,
            ...     show_color=True,
            ...     show_line=True,
            ...     log_file=True  # System default location
            ... )
            >>> warn("Development warning", UserWarning)
            
        Conditional configuration:
            >>> import os
            >>> if os.getenv("PRODUCTION"):
            ...     configure(show_color=False, log_file="prod.log")
            ... else:
            ...     configure(show_color=True, log_file=None)
            
        Reset to defaults:
            >>> configure(
            ...     show_icon=True,
            ...     show_color=True,
            ...     show_line=True,
            ...     log_file=None
            ... )
    """
    _printer.configure(**kwargs)

# Create alias instances for different import styles
class XWarnings:
    """
    Alias class to support alternative import and usage styles.
    
    This class provides static methods that mirror the main API functions,
    allowing for different import patterns and coding styles. It enables
    usage patterns like 'xwarnings.warn()' and 'xwarning.warn()'.
    
    All methods in this class are static and provide identical functionality
    to their corresponding module-level functions.
    
    Example:
        Different import styles:
            >>> from xwarning import xwarnings
            >>> xwarnings.warn("Message", UserWarning)
            >>> xwarnings.configure(show_icon=False)
            
            >>> from xwarning import xwarning
            >>> xwarning.warn("Message", type="runtime")
            >>> xwarning.configure(log_file="app.log")
            
        Namespace organization:
            >>> import xwarning
            >>> printer = xwarning.xwarnings
            >>> printer.warn("Organized warning", UserWarning)
    """
    
    @staticmethod
    def warn(message, category=None, type=None):
        """
        Issue a warning (alias method).
        
        Args:
            message (str): Warning message
            category (str|type, optional): Warning category
            type (str, optional): String-based warning type
            
        Example:
            >>> XWarnings.warn("Static method usage", UserWarning)
        """
        warn(message, category=category, type=type)
    
    @staticmethod
    def warning(message, category=None, type=None):
        """
        Issue a warning (alias method).
        
        Args:
            message (str): Warning message
            category (str|type, optional): Warning category
            type (str, optional): String-based warning type
            
        Example:
            >>> XWarnings.warning("Alternative name", UserWarning)
        """
        warn(message, category=category, type=type)
    
    @staticmethod
    def configure(**kwargs):
        """
        Configure global settings (alias method).
        
        Args:
            **kwargs: Configuration options
            
        Example:
            >>> XWarnings.configure(show_color=False)
        """
        configure(**kwargs)

# Create instance for alias usage
xwarnings = XWarnings()
xwarning = XWarnings()  # Additional alias

def get_backend_info():
    """
    Get information about the active rendering backend.
    
    This function returns a string indicating which backend is currently
    being used for rendering warnings. This information can be useful for
    debugging, logging, or conditional behavior based on available features.
    
    Returns:
        str: Backend identifier:
            - "rich": Rich library is available and active (best experience)
            - "make_colors": make_colors library is available (good experience)  
            - "ansi": Basic ANSI color codes only (minimal experience)
            
    The backend is automatically detected at import time based on available
    libraries. The detection order is: Rich → make_colors → ANSI fallback.
    
    Example:
        Basic usage:
            >>> from xwarning import get_backend_info
            >>> print(f"Using backend: {get_backend_info()}")
            Using backend: rich
            
        Conditional behavior:
            >>> backend = get_backend_info()
            >>> if backend == "rich":
            ...     print("🎨 Full Rich formatting available!")
            ... elif backend == "make_colors":
            ...     print("🌈 Good color support available")
            ... else:
            ...     print("📝 Basic ANSI colors only")
            
        Application startup info:
            >>> import logging
            >>> logging.info(f"xwarning initialized with {get_backend_info()} backend")
            
        Feature detection:
            >>> def supports_complex_formatting():
            ...     return get_backend_info() in ["rich", "make_colors"]
            >>> 
            >>> if supports_complex_formatting():
            ...     configure(show_icon=True, show_color=True)
            ... else:
            ...     configure(show_icon=False, show_color=True)
            
        Testing and development:
            >>> # Useful for testing different backend behaviors
            >>> print(f"Testing with {get_backend_info()} backend")
            >>> warn("Test warning", UserWarning)
    """
    if RICH_AVAILABLE:
        return "rich"
    elif MAKE_COLORS_AVAILABLE:
        return "make_colors"
    else:
        return "ansi"

if __name__ == '__main__':
    """
    Demo script showing xwarning capabilities.
    
    This section runs when the module is executed directly, demonstrating
    various features and usage patterns across all supported backends.
    """

    print(f"xwarning Demo - Backend: {get_backend_info()}")
    print("=" * 60)
    
    # Show backend capabilities
    backend = get_backend_info()
    if backend == "rich":
        print("🎨 Rich backend active - Full formatting support")
    elif backend == "make_colors":
        print("🌈 make_colors backend active - Good color support")
    else:
        print("📝 ANSI backend active - Basic color support")
    
    print("\n" + "=" * 60)

    print("\n=== Testing original string-based API ===")
    warn("This is deprecated warning !", type="deprecated")
    warn("This is user warning !", type="user")
    warn("This is future warning !", type="future")
    warn("This is runtime warning !", type="runtime")
    warn("This is syntax warning !", type="syntax")
    warn("This is import warning !", type="import")
    warn("This is unicode warning !", type="unicode")
    warn("This is general warning !", type="general")

    print("\n=== Testing Python warnings-style API ===")
    warn("This is deprecated warning using class!", DeprecationWarning)
    warn("This is user warning using class!", UserWarning)
    warn("This is future warning using class!", FutureWarning)
    warn("This is runtime warning using class!", RuntimeWarning)
    warn("This is syntax warning using class!", SyntaxWarning)
    warn("This is import warning using class!", ImportWarning)
    warn("This is unicode warning using class!", UnicodeWarning)
    warn("This is general warning using class!", Warning)

    print("\n=== Testing explicit parameter style ===")
    warn("This is user warning with explicit category parameter!", category=UserWarning)
    warn("This is runtime warning with explicit category parameter!", category=RuntimeWarning)

    print("\n=== Testing alias usage ===")
    xwarnings.warn("Testing xwarnings.warn with string type", type="user")
    xwarnings.warn("Testing xwarnings.warn with Warning class", UserWarning)
    
    xwarning.warn("Testing xwarning.warn with string type", type="runtime")
    xwarning.warn("Testing xwarning.warn with Warning class", RuntimeWarning)

    print("\n=== Testing configuration changes ===")
    print("Disabling icons...")
    configure(show_icon=False, show_color=True)
    warn("Warning without icon", UserWarning)
    
    print("Disabling colors...")
    configure(show_icon=True, show_color=False)
    warn("Warning without colors", RuntimeWarning)
    
    print("Production format...")
    configure(show_icon=False, show_color=False)
    warn("Production-style warning", DeprecationWarning)

    # Reset for logging demo
    configure(show_icon=True, show_color=True)

    print("\n=== Testing file logging ===")
    log_path = "demo_warnings.log"
    configure(log_file=log_path)
    warn(f"This warning is logged to {log_path}", UserWarning)
    print(f"Check {log_path} for logged warning")

    print("\n=== Testing custom printer instances ===")
    printer1 = WarningPrinter(auto_hook=False)
    printer1.configure(show_icon=False, log_file="printer1.log")
    printer1.warn("Custom printer 1 - no icons", UserWarning)

    printer2 = WarningPrinter(auto_hook=False)
    printer2.configure(show_icon=True, show_color=False, log_file="printer2.log")
    printer2.warn("Custom printer 2 - no colors", RuntimeWarning)

    print("\n=== Testing warning filters ===")
    print("Filtering out UserWarnings...")
    WarningPrinter.filterwarnings("ignore", category=UserWarning)

    warn("This UserWarning will NOT appear", UserWarning)
    warn("This RuntimeWarning WILL appear", RuntimeWarning)

    print("\n=== Testing warning without line ===")
    printer3 = WarningPrinter(auto_hook=False)
    printer3.configure(show_line=False)
    printer3.warn("Custom printer 3 - no line", RuntimeWarning)
    
    print("\n=== Testing warning without line global config ===")
    configure(show_icon=True, show_color=True, show_line=False)
    warn("Custom printer 3 - no line - global config", RuntimeWarning)
    
    print(f"\nDemo completed using {get_backend_info()} backend!")
    print("=" * 60)
