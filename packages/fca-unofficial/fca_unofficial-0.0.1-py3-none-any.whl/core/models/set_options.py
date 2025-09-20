from typing import Any, Dict
from ...utils.net import set_proxy
from ...utils.user_agents import random_user_agent


async def set_options(global_options: Dict[str, Any], options: Dict[str, Any]) -> None:
    handlers = {}

    def b(name):
        handlers[name] = lambda v, n=name: global_options.__setitem__(n, bool(v))

    b("online"); b("selfListen"); b("listenEvents"); b("updatePresence"); b("forceLogin");
    b("autoMarkDelivery"); b("autoMarkRead"); b("listenTyping"); b("autoReconnect"); b("emitReady")

    def set_user_agent(value):
        global_options["userAgent"] = value

    handlers["userAgent"] = set_user_agent

    def set_proxy_opt(value):
        if isinstance(value, str):
            global_options["proxy"] = value
            set_proxy(value)
        else:
            global_options.pop("proxy", None)
            set_proxy(None)

    handlers["proxy"] = set_proxy_opt

    def set_random_ua(value):
        global_options["randomUserAgent"] = bool(value)
        if value:
            ua = random_user_agent()["userAgent"]
            global_options["userAgent"] = ua

    handlers["randomUserAgent"] = set_random_ua

    def set_bypass_region(value):
        if value:
            value = str(value).upper()
        global_options["bypassRegion"] = value

    handlers["bypassRegion"] = set_bypass_region

    for k, v in (options or {}).items():
        if k in handlers:
            handlers[k](v)
