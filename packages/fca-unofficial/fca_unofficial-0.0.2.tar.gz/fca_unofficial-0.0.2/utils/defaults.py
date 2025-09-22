from typing import Any, Dict, Optional, Tuple
import re

from .net import get, post, post_formdata


def make_defaults(html: str, user_id: str, ctx: Dict[str, Any]):
    req_counter = 1
    revision = "0"
    match = re.search(r'revision":(\d+)', html or "")
    if not match:
        match = re.search(r'__spin_r":(\d+)', html or "")
    if match:
        revision = match.group(1)
    elif isinstance(ctx, dict):
        spin_r = ctx.get("master", {}).get("__spin_r")
        if spin_r is not None:
            revision = str(spin_r)

    def to_base36(value: int) -> str:
        if value == 0:
            return "0"
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = ""
        number = value
        while number > 0:
            number, rem = divmod(number, 36)
            result = digits[rem] + result
        return result

    def merge_defaults(obj: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        nonlocal req_counter
        new_obj: Dict[str, Any] = {
            "av": user_id,
            "__user": user_id,
            "__req": to_base36(req_counter),
            "__rev": revision,
            "__a": 1,
        }
        req_counter += 1
        if isinstance(ctx, dict):
            new_obj.update({
                "fb_dtsg": ctx.get("fb_dtsg"),
                "jazoest": ctx.get("jazoest"),
            })
        if not obj:
            return new_obj
        for k, v in obj.items():
            if k not in new_obj:
                new_obj[k] = v
        return new_obj

    class Defaults:
        def get(self, url: str, jar, qs: Optional[Dict[str, Any]] = None, _ctx=None, custom_header: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
            options = ctx.get("globalOptions", {}) if isinstance(ctx, dict) else {}
            return get(url, jar, merge_defaults(qs), options, _ctx or ctx, custom_header)

        def post(self, url: str, jar, form: Dict[str, Any], _ctx=None, custom_header: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
            options = ctx.get("globalOptions", {}) if isinstance(ctx, dict) else {}
            return post(url, jar, merge_defaults(form), options, _ctx or ctx, custom_header)

        def postFormData(self, url: str, jar, form: Dict[str, Any], qs: Optional[Dict[str, Any]] = None, _ctx=None) -> Tuple[int, Dict[str, Any]]:
            options = ctx.get("globalOptions", {}) if isinstance(ctx, dict) else {}
            return post_formdata(url, jar, merge_defaults(form), merge_defaults(qs or {}), options, _ctx or ctx)

    return Defaults()
