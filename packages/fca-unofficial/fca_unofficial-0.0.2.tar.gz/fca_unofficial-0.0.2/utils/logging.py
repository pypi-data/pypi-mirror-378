from typing import Any
import sys

_logging_enabled = False


def log_options(enabled: bool):
    global _logging_enabled
    _logging_enabled = bool(enabled)


def _emit(level: str, *args: Any, stream=None) -> None:
    print(f"[python-facebookapi]{level}", *args, file=stream or sys.stdout)


def log(*args: Any) -> None:
    if not _logging_enabled:
        return
    _emit('[LOG]', *args)


def warn(*args: Any) -> None:
    if not _logging_enabled:
        return
    _emit('[WARN]', *args)


def error(*args: Any) -> None:
    _emit('[ERROR]', *args, stream=sys.stderr)
