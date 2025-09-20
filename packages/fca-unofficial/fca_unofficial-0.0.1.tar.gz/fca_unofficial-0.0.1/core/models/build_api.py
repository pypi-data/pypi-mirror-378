from typing import Any, Dict, List, Tuple
from http.cookiejar import CookieJar
from ...utils.defaults import make_defaults


async def build_api(html: str, jar: CookieJar, net_data: List[Dict[str, Any]], global_options: Dict[str, Any]):
    # extract userID from cookies (c_user or i_user)
    cookies = getattr(jar, "_cookies", None)
    def _get_cookie(name: str) -> str:
        try:
            for c in jar:  # type: ignore
                if c.name in (name,):
                    return c.value
        except Exception:
            pass
        # Fallback for requests cookiejar
        for c in jar:  # type: ignore
            if getattr(c, "name", None) == name:
                return getattr(c, "value", "")
        return ""

    user_id = _get_cookie("i_user") or _get_cookie("c_user")
    if not user_id:
        raise RuntimeError("Error retrieving userID from cookies.")

    # Extract dtsg token from html
    import re
    m = re.search(r'"token":"([^"]+)"', html)
    dtsg = m.group(1) if m else ""
    jazoest = "2" + "".join(str(ord(ch)) for ch in dtsg)

    # Try to extract LSD token and spin params from HTML
    lsd = None
    master: Dict[str, Any] = {}
    try:
        mlsd = re.search(r'\{"token":"([^"]+)"\}\]\],"LSD"', html)
        if mlsd:
            lsd = mlsd.group(1)
    except Exception:
        pass
    try:
        import re as _re
        sr = _re.search(r'"__spin_r":(\d+)', html)
        sb = _re.search(r'"__spin_b":"([^"]+)"', html)
        st = _re.search(r'"__spin_t":(\d+)', html)
        if sr: master["__spin_r"] = sr.group(1)
        if sb: master["__spin_b"] = sb.group(1)
        if st: master["__spin_t"] = st.group(1)
    except Exception:
        pass

    ctx: Dict[str, Any] = {
        "userID": user_id,
        "jar": jar,
        "clientID": None,
        "globalOptions": global_options,
        "loggedIn": True,
        "access_token": "NONE",
        "clientMutationId": 0,
        "mqttClient": None,
        "lastSeqId": None,
        "syncToken": None,
        "mqttEndpoint": None,
        "wsReqNumber": 0,
        "wsTaskNumber": 0,
        "reqCallbacks": {},
        "callback_Task": {},
        "region": None,
        "firstListen": True,
        "fb_dtsg": dtsg,
        "jazoest": jazoest,
        "lsd": lsd,
        "master": master,
        "netData": net_data,
        "html": html,
    }
    default_funcs = make_defaults(html, user_id, ctx)
    return ctx, default_funcs
