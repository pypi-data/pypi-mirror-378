import random
import time
from typing import Any


def get_type(obj: Any) -> str:
    return type(obj).__name__


def generate_threading_id(client_id: str) -> str:
    k = int(time.time() * 1000)
    l = random.randint(0, 4294967295)
    m = client_id
    return f"<{k}:{l}-{m}@mail.projektitan.com>"


def _binary_to_decimal(data: str) -> str:
    ret = ""
    while data != "0":
        end = 0
        full = ""
        for ch in data:
            end = 2 * end + int(ch)
            if end >= 10:
                full += "1"
                end -= 10
            else:
                full += "0"
        ret = str(end) + ret
        idx = full.find("1")
        data = full[idx:] if idx != -1 else "0"
    return ret


def generate_offline_threading_id() -> str:
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    bits = ("0" * 22 + bin(value)[2:])[-22:]
    msgs = bin(ret)[2:] + bits
    return _binary_to_decimal(msgs)


def generate_timestamp_relative() -> str:
    d = time.localtime()
    return f"{d.tm_hour}:{d.tm_min:02d}"


def get_signature_id() -> str:
    return hex(random.randint(0, 2147483647))[2:]


def format_id(x: Any) -> str:
    return str(x)
