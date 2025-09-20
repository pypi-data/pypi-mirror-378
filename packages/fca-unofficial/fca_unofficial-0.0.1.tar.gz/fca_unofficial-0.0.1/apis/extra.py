from typing import Any, Dict, Optional


def attach_extra(api: Any) -> None:
    def addExternalModule(module_name: str, functions: Dict[str, Any]):
        if not isinstance(functions, dict):
            raise ValueError("functions must be a dict of callables")
        for k, v in functions.items():
            setattr(api, k, v)
        return True

    def getAccess() -> Optional[Dict[str, Any]]:
        # JS uses business access discovery; return basic context for now
        return {
            "userID": api.ctx.get("userID"),
            "region": api.ctx.get("region"),
            "lsd": api.ctx.get("lsd"),
        }

    api.addExternalModule = addExternalModule
    api.getAccess = getAccess
