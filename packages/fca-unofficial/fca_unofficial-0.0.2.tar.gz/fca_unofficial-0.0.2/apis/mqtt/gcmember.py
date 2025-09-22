from typing import Any, Dict, List
import json
from ...utils.helpers import generate_offline_threading_id


def attach_gcmember(api: Any) -> None:
    def gcmember(action: str, userIDs: List[str] | str, threadID: str):
        client = api.ctx.get("mqttClient")
        if not client:
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        action = (action or "").lower()
        if action not in ("add", "remove"):
            raise ValueError("action must be 'add' or 'remove'")

        # best-effort membership precheck if getThreadInfo exists
        try:
            thread_info = api.getThreadInfo(threadID)
        except Exception:
            thread_info = None
        if isinstance(userIDs, str):
            ids = [userIDs]
        else:
            ids = list(userIDs)

        api.ctx["wsReqNumber"] = (api.ctx.get("wsReqNumber") or 0) + 1
        api.ctx["wsTaskNumber"] = (api.ctx.get("wsTaskNumber") or 0) + 1

        if action == "add":
            # only add users not already in group if we have info
            if thread_info and getattr(thread_info, "participantIDs", None):
                ids = [i for i in ids if i not in thread_info.participantIDs]
                if not ids:
                    return {"type": "error_gc", "error": "All specified users are already in the group."}
            query_payload: Dict[str, Any] = {
                "thread_key": int(threadID),
                "contact_ids": [int(i) for i in ids],
                "sync_group": 1,
            }
            query = {
                "label": "23",
                "payload": json.dumps(query_payload),
                "queue_name": str(threadID),
                "task_id": api.ctx["wsTaskNumber"],
                "failure_count": None,
            }
        else:  # remove
            uid = ids[0]
            query_payload = {
                "thread_id": str(threadID),
                "contact_id": str(uid),
                "sync_group": 1,
            }
            query = {
                "label": "140",
                "payload": json.dumps(query_payload),
                "queue_name": "remove_participant_v2",
                "task_id": api.ctx["wsTaskNumber"],
                "failure_count": None,
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
            "type": "gc_member_update",
            "threadID": threadID,
            "userIDs": ids,
            "action": action,
            "senderID": api.ctx.get("userID"),
            "BotID": api.ctx.get("userID"),
        }

    api.gcmember = gcmember
