from rich import print as print_rich

def gen_print_string(message: str, symbol, color, newline: bool = False):
    return f"{"\n" if newline else ""}[{color}]{symbol} {message}[/{color}]"


def print_success(message: str, newline: bool = False):
    """
    Print with success message with rich styling. 
    """
    print_rich(gen_print_string(message, ":heavy_check_mark:", "green", newline))

def print_warning(message: str, newline: bool = False):
    """
    Print with warning message with rich styling. 
    """
    print_rich(gen_print_string(message, ":warning:", "orange1", newline))


def print_error(message: str, newline: bool = False):
    """
    Print with error message with rich styling. 
    """
    print_rich(gen_print_string(message, ":cross_mark:", "red", newline))

def print_info(message: str, newline: bool = False):
    """
    Print with info message with rich styling. 
    """
    print_rich(gen_print_string(message, ":information_source:", "blue", newline))
