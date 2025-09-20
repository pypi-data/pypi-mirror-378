from typing import Any, Dict, Optional, Tuple
from .net import get, post, post_formdata


def make_defaults(html: str, user_id: str, ctx: Dict[str, Any]):
    req_counter = 1
    # revision scraping simplified: not strictly needed for FB endpoints that ignore
    revision = "0"

    def merge_defaults(obj: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        nonlocal req_counter
        new_obj: Dict[str, Any] = {
            "av": user_id,
            "__user": user_id,
            "__req": format(req_counter, 'x'),
            "__rev": revision,
            "__a": 1,
        }
        req_counter += 1
        if ctx:
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
            return get(url, jar, merge_defaults(qs), ctx.get("globalOptions", {}), _ctx or ctx, custom_header)

        def post(self, url: str, jar, form: Dict[str, Any], _ctx=None, custom_header: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
            return post(url, jar, merge_defaults(form), ctx.get("globalOptions", {}), _ctx or ctx, custom_header)

        def postFormData(self, url: str, jar, form: Dict[str, Any], qs: Optional[Dict[str, Any]] = None, _ctx=None) -> Tuple[int, Dict[str, Any]]:
            return post_formdata(url, jar, merge_defaults(form), merge_defaults(qs or {}), ctx.get("globalOptions", {}), _ctx or ctx)

    return Defaults()
