from typing import Any, Dict, List
from http.cookiejar import CookieJar
from ...utils.defaults import make_defaults


async def build_api(html: str, jar: CookieJar, net_data: List[Dict[str, Any]], global_options: Dict[str, Any]):
    # extract userID from cookies (c_user or i_user)
    def _get_cookie(name: str) -> str:
        try:
            for c in jar:  # type: ignore
                if getattr(c, "name", None) == name:
                    return getattr(c, "value", "")
        except Exception:
            pass
        return ""

    user_id = _get_cookie("i_user") or _get_cookie("c_user")
    if not user_id:
        raise RuntimeError("Error retrieving userID. Try logging in via browser to verify the cookies are valid.")

    import re

    def _find_config(key: str):
        for script in (net_data or []):
            req = script.get("require") if isinstance(script, dict) else None
            if isinstance(req, list):
                for item in req:
                    if isinstance(item, list) and len(item) >= 3:
                        if item[0] == key and item[2]:
                            return item[2]
                        if len(item) >= 4 and isinstance(item[3], list) and item[3]:
                            bbox = item[3][0]
                            if isinstance(bbox, dict) and bbox.get("__bbox", {}).get("define"):
                                for d in bbox["__bbox"]["define"]:
                                    if isinstance(d, list) and len(d) >= 3 and str(d[0]).endswith(key) and d[2]:
                                        return d[2]
        return None

    dtsg_data = _find_config("DTSGInitialData")
    dtsg = (dtsg_data.get("token") if isinstance(dtsg_data, dict) else None) or (
        re.search(r'"token":"([^"]+)"', html).group(1) if re.search(r'"token":"([^"]+)"', html) else ""
    )
    jazoest = "2" + "".join(str(ord(ch)) for ch in dtsg)

    client_id_data = _find_config("MqttWebDeviceID")
    client_id = client_id_data.get("clientID") if isinstance(client_id_data, dict) else None

    mqtt_config = _find_config("MqttWebConfig")
    mqtt_app_id = mqtt_config.get("appID") if isinstance(mqtt_config, dict) else None
    mqtt_endpoint = mqtt_config.get("endpoint") if isinstance(mqtt_config, dict) else None

    current_user = _find_config("CurrentUserInitialData")
    user_app_id = current_user.get("APP_ID") if isinstance(current_user, dict) else None

    primary_app_id = user_app_id or mqtt_app_id

    # Region and iris sequence id
    region = None
    if mqtt_endpoint:
        try:
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(mqtt_endpoint).query)
            reg = (q.get("region") or [None])[0]
            region = reg.upper() if reg else None
        except Exception:
            region = None
    m_seq = re.search(r'irisSeqID:"(.+?)"', html)
    iris_seq_id = m_seq.group(1) if m_seq else None

    # Bypass region if requested
    if global_options.get("bypassRegion") and mqtt_endpoint:
        try:
            from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
            p = urlparse(mqtt_endpoint)
            qs = parse_qs(p.query)
            qs["region"] = [str(global_options["bypassRegion"]).lower()]
            mqtt_endpoint = urlunparse((p.scheme, p.netloc, p.path, p.params, urlencode(qs, doseq=True), p.fragment))
            region = str(global_options["bypassRegion"]).upper()
        except Exception:
            pass

    # Extract LSD and spin params
    lsd = None
    try:
        mlsd = re.search(r'\{"token":"([^"]+)"\}\]\],"LSD"', html)
        if mlsd:
            lsd = mlsd.group(1)
    except Exception:
        pass
    master: Dict[str, Any] = {}
    try:
        sr = re.search(r'"__spin_r":(\d+)', html)
        sb = re.search(r'"__spin_b":"([^"]+)"', html)
        st = re.search(r'"__spin_t":(\d+)', html)
        if sr: master["__spin_r"] = sr.group(1)
        if sb: master["__spin_b"] = sb.group(1)
        if st: master["__spin_t"] = st.group(1)
    except Exception:
        pass

    ctx: Dict[str, Any] = {
        "userID": user_id,
        "jar": jar,
        "clientID": client_id,
        "appID": primary_app_id,
        "mqttAppID": mqtt_app_id,
        "userAppID": user_app_id,
        "globalOptions": global_options,
        "loggedIn": True,
        "access_token": "NONE",
        "clientMutationId": 0,
        "mqttClient": None,
        "lastSeqId": iris_seq_id,
        "syncToken": None,
        "mqttEndpoint": mqtt_endpoint,
        "wsReqNumber": 0,
        "wsTaskNumber": 0,
        "reqCallbacks": {},
        "callback_Task": {},
        "region": region,
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
