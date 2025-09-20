from typing import Any, Dict, List, Optional
import json
import re


def attach_login(api: Any) -> None:
    def getBotInitialData() -> Optional[Dict[str, Any]]:
        # Fetch profile page and extract CurrentUserInitialData from HTML body
        url = f"https://www.facebook.com/profile.php?id={api.ctx.get('userID')}"
        status, res = api.httpGet(url)
        if status < 200 or status >= 300:
            raise RuntimeError(f"getBotInitialData failed with status {status}")
        body = res.get("body", "")
        m = re.search(r'"CurrentUserInitialData",\[\],\{(.*?)\},', body, re.S)
        if not m:
            return None
        try:
            obj = json.loads("{" + m.group(1) + "}")
        except Exception:
            return None
        # Normalize fields similar to JS
        out = dict(obj)
        if "NAME" in out:
            out["name"] = out.pop("NAME")
        if "USER_ID" in out:
            out["uid"] = out.pop("USER_ID")
        return out

    def GetBotInfo(netData: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        data = netData if netData is not None else api.ctx.get("netData")
        if not data or not isinstance(data, list):
            return None

        def find_config(key: str):
            for script in data:
                req = script.get("require")
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

        current = find_config("CurrentUserInitialData")
        dtsg_initial = find_config("DTSGInitialData")
        dtsg_init = find_config("DTSGInitData")
        lsd = find_config("LSD")
        if not current or not dtsg_initial:
            return None
        return {
            "name": current.get("NAME"),
            "firstName": current.get("SHORT_NAME"),
            "uid": current.get("USER_ID"),
            "appID": current.get("APP_ID"),
            "dtsgToken": dtsg_initial.get("token") if isinstance(dtsg_initial, dict) else None,
            "lsdToken": lsd.get("token") if isinstance(lsd, dict) else None,
            "dtsgInit": {"token": (dtsg_init or {}).get("token"), "async_get_token": (dtsg_init or {}).get("async_get_token")} if dtsg_init else None,
            "getCtx": lambda k: api.ctx.get(k),
            "getOptions": lambda k: api.globalOptions.get(k),
            "getRegion": lambda: api.ctx.get("region"),
        }

    api.getBotInitialData = getBotInitialData
    api.GetBotInfo = GetBotInfo
