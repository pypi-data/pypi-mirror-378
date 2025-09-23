def okprint(print_str: str):
    """Prints a message in green."""
    print(f"\033[92m{print_str}\033[0m")


def errprint(print_str: str):
    """Prints error message in red."""
    print(f"\033[91m{print_str}\033[0m")


def warnprint(print_str: str):
    """Prints warning message in pale orange."""
    # ANSI 38;5;215 is a pale orange (xterm 256 color)
    print(f"\033[38;5;215m{print_str}\033[0m")


def dbgprint(print_str: str):
    """Prints debug message in light blue."""
    print(f"\033[96m{print_str}\033[0m")
