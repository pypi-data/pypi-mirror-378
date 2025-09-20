import os


def standard_path(p: str) -> str:
    """Standardize and expand a file path.

    Normalizes a file path by expanding user home directory (~) and
    environment variables, and handles edge cases with trailing slashes.

    Args:
        p: File path string to standardize.

    Returns:
        str: Standardized and expanded file path.

    Examples:
        >>> standard_path("~/Documents/file.txt")
        '/home/user/Documents/file.txt'
        >>> standard_path("$HOME/file.txt")
        '/home/user/file.txt'
        >>> standard_path("/path/to/dir/")
        '/path/to/dir'
    """
    if os.path.basename(p.strip()) == "":
        p = os.path.dirname(p.strip())
    return os.path.expandvars(os.path.expanduser(p.strip()))
