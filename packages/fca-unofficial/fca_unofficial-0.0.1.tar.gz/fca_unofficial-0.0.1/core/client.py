import asyncio
from typing import Any, Callable, Dict, Optional

from .models.set_options import set_options
from .models.build_api import build_api
from .models.login_helper import login_helper
from ..utils.logging import log_options


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


async def _login_async(credentials: Dict[str, Any], options: Optional[Dict[str, Any]], callback: Optional[Callable]):
    if options and "logging" in options:
        log_options(bool(options.get("logging")))

    global_options: Dict[str, Any] = {
        "selfListen": False,
        "listenEvents": True,
        "listenTyping": False,
        "updatePresence": False,
        "forceLogin": False,
        "autoMarkDelivery": False,
        "autoMarkRead": True,
        "autoReconnect": True,
        "online": True,
        "emitReady": False,
        "userAgent": DEFAULT_USER_AGENT,
    }
    if options:
        global_options.update(options)

    await set_options(global_options, options or {})

    def _final_cb(err: Optional[Exception], api: Optional[Any]):
        # Auto-save appstate if requested in options, before returning
        if not err and api and global_options.get("autoSaveAppState"):
            try:
                path = str(global_options.get("appStatePath") or "appstate.json")
                api.save_app_state(path)
            except Exception:
                pass
        if callback:
            return callback(err, api)
        if err:
            raise err
        return api

    return await login_helper(
        credentials,
        global_options,
        _final_cb,
        set_options,
        build_api,
        None,
    )


def login(credentials: Dict[str, Any], options: Optional[Dict[str, Any]] = None, callback: Optional[Callable] = None):
    """Entrypoint similar to module/index.js -> client.login in JS.

    credentials: { appState: list[ {key/name, value}], or email/password }
    options: overrides for behavior
    callback: optional (err, api)
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_login_async(credentials, options, callback))
