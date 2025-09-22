from typing import Any, Dict, Optional
from .user_agents import random_user_agent
from urllib.parse import urlparse


def build_headers(url: str, options: Dict[str, Any], ctx: Optional[Dict[str, Any]] = None, custom_header: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    ua = random_user_agent()
    parsed = urlparse(url)
    host = parsed.hostname or "www.facebook.com"
    path = parsed.path or "/"
    referer = f"https://{host}/"
    is_ajax = any(s in path for s in ["/checkpoint/async", "/api/graphql", "/api/graphqlbatch", "/ajax/"])
    # Prefer mobile UA for mobile hosts or when explicitly requested
    prefer_mobile = bool(options.get("mobileFirst")) or host.startswith("m.") or host.startswith("mbasic.")
    if prefer_mobile:
        # Minimal stable Android mobile UA and related client hints
        ua_mobile = {
            "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
            "secChUa": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "secChUaFullVersionList": '"Not/A)Brand";v="126.0.0.0", "Chromium";v="126.0.0.0", "Google Chrome";v="126.0.0.0"',
            "secChUaPlatform": '"Android"',
            "secChUaPlatformVersion": '"12.0.0"',
        }
        ua = ua_mobile
    headers: Dict[str, str] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Dpr": "1",
        "Host": host,
        "Origin": f"https://{host}",
        "Referer": referer,
        "Sec-Ch-Prefers-Color-Scheme": "light",
        "Sec-Ch-Ua": ua["secChUa"],
        "Sec-Ch-Ua-Full-Version-List": ua["secChUaFullVersionList"],
        "Sec-Ch-Ua-Mobile": "?1" if prefer_mobile else "?0",
        "Sec-Ch-Ua-Model": '""',
        "Sec-Ch-Ua-Platform": ua["secChUaPlatform"],
        "Sec-Ch-Ua-Platform-Version": ua["secChUaPlatformVersion"],
        "Sec-Fetch-Dest": "empty" if is_ajax else "document",
        "Sec-Fetch-Mode": "cors" if is_ajax else "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": None if is_ajax else "?1",
        "Upgrade-Insecure-Requests": None if is_ajax else "1",
        "User-Agent": options.get("userAgent") or ua["userAgent"],
        "Viewport-Width": "1920",
    }
    if is_ajax:
        headers["Accept"] = "*/*"
        headers["X-Requested-With"] = "XMLHttpRequest"
    if ctx:
        if ctx.get("region"):
            headers["X-MSGR-Region"] = str(ctx["region"])  # for some endpoints
        if ctx.get("lsd"):
            headers["X-Fb-Lsd"] = str(ctx["lsd"])
        if ctx.get("master"):
            master = ctx["master"]
            if master.get("__spin_r"):
                headers["X-Fb-Spin-R"] = str(master["__spin_r"]) 
            if master.get("__spin_b"):
                headers["X-Fb-Spin-B"] = str(master["__spin_b"]) 
            if master.get("__spin_t"):
                headers["X-Fb-Spin-T"] = str(master["__spin_t"]) 

    if custom_header:
        # Special flags (not real headers)
        if custom_header.get("noRef"):
            headers.pop("Referer", None)
        # Merge only real header key/values; coerce values to str; allow None to delete
        for k, v in custom_header.items():
            if k == "noRef":
                continue
            if v is None:
                headers.pop(k, None)
            else:
                headers[k] = str(v)
    return headers
