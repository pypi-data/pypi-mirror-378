from typing import Any

_logging_enabled = True


def log_options(enabled: bool):
    global _logging_enabled
    _logging_enabled = bool(enabled)


def log(*args: Any):
    if not _logging_enabled:
        return
    print("[python-facebookapi][LOG]", *args)


def warn(*args: Any):
    if not _logging_enabled:
        return
    print("[python-facebookapi][WARN]", *args)


def error(*args: Any):
    if not _logging_enabled:
        return
    print("[python-facebookapi][ERROR]", *args)
