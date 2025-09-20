from typing import Any, Dict
import json
from ...utils.helpers import generate_offline_threading_id


def attach_gcrule(api: Any) -> None:
    def gcrule(action: str, userID: str, threadID: str):
        client = api.ctx.get("mqttClient")
        if not client:
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        action = (action or "").lower()
        if action not in ("admin", "unadmin"):
            raise ValueError("action must be 'admin' or 'unadmin'")

        # best effort thread info
        try:
            thread_info = api.getThreadInfo(threadID)
        except Exception:
            thread_info = None
        if thread_info and getattr(thread_info, "adminIDs", None):
            is_admin = any((getattr(x, "id", None) or x) == userID for x in thread_info.adminIDs)
            if action == "admin" and is_admin:
                return {"type": "error_gc_rule", "error": "User is already an admin."}
            if action == "unadmin" and not is_admin:
                return {"type": "error_gc_rule", "error": "User is not an admin."}

        api.ctx["wsReqNumber"] = (api.ctx.get("wsReqNumber") or 0) + 1
        api.ctx["wsTaskNumber"] = (api.ctx.get("wsTaskNumber") or 0) + 1

        query_payload: Dict[str, Any] = {
            "thread_key": int(threadID),
            "contact_id": int(userID),
            "is_admin": 1 if action == "admin" else 0,
        }
        query = {
            "failure_count": None,
            "label": "25",
            "payload": json.dumps(query_payload),
            "queue_name": "admin_status",
            "task_id": api.ctx["wsTaskNumber"],
        }
        context = {
            "app_id": api.ctx.get("appID") or "2220391788200892",
            "payload": {
                "epoch_id": int(generate_offline_threading_id()),
                "tasks": [query],
                "version_id": "24631415369801570",
            },
            "request_id": api.ctx["wsReqNumber"],
            "type": 3,
        }
        context["payload"] = json.dumps(context["payload"])  # serialize
        client.publish("/ls_req", json.dumps(context), qos=1, retain=False)
        return {
            "type": "gc_rule_update",
            "threadID": threadID,
            "userID": userID,
            "action": action,
            "senderID": api.ctx.get("userID"),
            "BotID": api.ctx.get("userID"),
        }

    api.gcrule = gcrule
