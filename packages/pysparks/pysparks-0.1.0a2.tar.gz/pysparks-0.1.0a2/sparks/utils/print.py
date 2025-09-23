def _colorprint(print_str: str, color_code: str):
    """Prints a message in the specified ANSI color."""
    print(f"\x1b[{color_code}m{print_str}\x1b[0m")


def okprint(print_str: str):
    """Prints a message in green."""
    _colorprint(print_str, "92")


def errprint(print_str: str):
    """Prints error message in red."""
    _colorprint(print_str, "91")


def warnprint(print_str: str):
    """Prints warning message in pale orange."""
    _colorprint(print_str, "38;5;215")


def dbgprint(print_str: str):
    """Prints debug message in light blue."""
    _colorprint(print_str, "96")
