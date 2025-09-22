from . xwarning import warn, configure, WarningPrinter
import sys

def main():
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

if __name__ == '__main__':
	main()