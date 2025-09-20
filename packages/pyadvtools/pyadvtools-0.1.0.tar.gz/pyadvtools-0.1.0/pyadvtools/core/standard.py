import os


def standard_path(p: str) -> str:
    if os.path.basename(p.strip()) == "":
        p = os.path.dirname(p.strip())
    return os.path.expandvars(os.path.expanduser(p.strip()))
