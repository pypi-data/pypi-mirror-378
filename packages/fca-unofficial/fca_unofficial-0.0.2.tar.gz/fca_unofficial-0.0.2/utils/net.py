from typing import Any, Dict, Optional, Tuple
import requests
from requests import Session
from .headers import build_headers

_session: Optional[Session] = None
_proxy: Optional[str] = None


def get_session() -> Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def set_proxy(proxy_url: Optional[str]):
    global _proxy
    _proxy = proxy_url


def _apply_proxy(kwargs: Dict[str, Any]):
    if _proxy:
        kwargs["proxies"] = {
            "http": _proxy,
            "https": _proxy,
        }


def get(url: str, jar: requests.cookies.RequestsCookieJar, qs: Optional[Dict[str, Any]], options: Dict[str, Any], ctx: Optional[Dict[str, Any]] = None, custom_header: Optional[Dict[str, str]] = None) -> Tuple[int, Dict[str, Any]]:
    sess = get_session()
    sess.cookies = jar
    headers = build_headers(url, options, ctx, custom_header)
    params = qs or {}
    timeout = int(options.get("requestTimeout", 60)) if isinstance(options, dict) else 60
    kwargs: Dict[str, Any] = {"headers": headers, "params": params, "timeout": timeout}
    _apply_proxy(kwargs)
    resp = sess.get(url, **kwargs)
    return resp.status_code, {"body": resp.text, "headers": dict(resp.headers), "url": str(resp.url)}


def post(url: str, jar: requests.cookies.RequestsCookieJar, form: Dict[str, Any], options: Dict[str, Any], ctx: Optional[Dict[str, Any]] = None, custom_header: Optional[Dict[str, str]] = None) -> Tuple[int, Dict[str, Any]]:
    sess = get_session()
    sess.cookies = jar
    headers = build_headers(url, options, ctx, custom_header)
    data: Any
    if headers.get("Content-Type", "").find("json") >= 0:
        data = form
        timeout = int(options.get("requestTimeout", 60)) if isinstance(options, dict) else 60
        kwargs = {"json": data, "headers": headers, "timeout": timeout}
    else:
        data = {}
        for k, v in (form or {}).items():
            data[k] = v if not isinstance(v, (dict, list)) else __import__("json").dumps(v)
        timeout = int(options.get("requestTimeout", 60)) if isinstance(options, dict) else 60
        kwargs = {"data": data, "headers": headers, "timeout": timeout}
    _apply_proxy(kwargs)
    resp = sess.post(url, **kwargs)
    return resp.status_code, {"body": resp.text, "headers": dict(resp.headers), "url": str(resp.url)}


def post_formdata(url: str, jar: requests.cookies.RequestsCookieJar, form: Dict[str, Any], qs: Optional[Dict[str, Any]], options: Dict[str, Any], ctx: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
    sess = get_session()
    sess.cookies = jar
    headers = build_headers(url, options, ctx, {"Content-Type": None})
    params = qs or {}
    files = {}
    data = {}
    for k, v in (form or {}).items():
        if hasattr(v, "read"):
            files[k] = v
        else:
            data[k] = v
    timeout = int(options.get("requestTimeout", 60)) if isinstance(options, dict) else 60
    kwargs: Dict[str, Any] = {"headers": headers, "files": files or None, "data": data, "params": params, "timeout": timeout}
    _apply_proxy(kwargs)
    resp = sess.post(url, **kwargs)
    return resp.status_code, {"body": resp.text, "headers": dict(resp.headers), "url": str(resp.url)}
