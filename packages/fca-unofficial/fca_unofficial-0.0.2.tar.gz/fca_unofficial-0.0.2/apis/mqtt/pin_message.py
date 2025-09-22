from typing import Any, Dict
import json
from ...utils.helpers import generate_offline_threading_id

VERSION_ID = "9523201934447612"
APP_ID = "2220391788200892"


essential_labels = {
    "pin": {"label": "430", "queue": "pin_msg_v2_{threadID}"},
    "search": {"label": "751", "queue": "set_pinned_message_search"},
    "unpin": {"label": "431", "queue": "unpin_msg_v2_{threadID}"},
}


def attach_pin_message(api: Any) -> None:
    def pinMessage(action: str, threadID: str, messageID: str | None = None):
        client = api.ctx.get("mqttClient")
        if not client:
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        action = (action or "").lower()
        if action not in ("pin", "unpin", "list"):
            raise ValueError('Invalid action. Use "pin", "unpin", or "list".')

        if action == "list":
            # We don't have the JSON scraper util here; return a stub response instructing to call thread page.
            # A future enhancement can port a JSON page scraper analogous to utils.json in JS.
            return {"note": "Listing pinned messages requires scraping thread page JSON; not yet implemented."}

        if not threadID or not messageID:
            raise ValueError('"pin"/"unpin" require threadID and messageID.')

        def next_ids():
            api.ctx["wsReqNumber"] = (api.ctx.get("wsReqNumber") or 0) + 1
            api.ctx["wsTaskNumber"] = (api.ctx.get("wsTaskNumber") or 0) + 1
            return api.ctx["wsReqNumber"], api.ctx["wsTaskNumber"]

        def make_task(label: str, queue_name: str, payload: Dict[str, Any]):
            return {
                "label": label,
                "payload": json.dumps(payload),
                "queue_name": queue_name,
                "task_id": api.ctx["wsTaskNumber"],
                "failure_count": None,
            }

        # Build tasks
        tasks = []
        if action == "pin":
            _, _ = next_ids()
            tasks.append(make_task(
                essential_labels["pin"]["label"],
                essential_labels["pin"]["queue"].format(threadID=threadID),
                {"thread_key": threadID, "message_id": messageID, "timestamp_ms": __import__("time").time() * 1000},
            ))
            _, _ = next_ids()
            tasks.append(make_task(
                essential_labels["search"]["label"],
                essential_labels["search"]["queue"],
                {"thread_key": threadID, "message_id": messageID, "pinned_message_state": 1},
            ))
        else:  # unpin
            _, _ = next_ids()
            tasks.append(make_task(
                essential_labels["search"]["label"],
                essential_labels["search"]["queue"],
                {"thread_key": threadID, "message_id": messageID, "pinned_message_state": 0},
            ))
            _, _ = next_ids()
            tasks.append(make_task(
                essential_labels["unpin"]["label"],
                essential_labels["unpin"]["queue"].format(threadID=threadID),
                {"thread_key": threadID, "message_id": messageID, "timestamp_ms": __import__("time").time() * 1000},
            ))
            _, _ = next_ids()
            tasks.append(make_task(
                essential_labels["search"]["label"],
                essential_labels["search"]["queue"],
                {"thread_key": threadID, "message_id": messageID, "pinned_message_state": 0},
            ))

        context = {
            "app_id": api.ctx.get("appID") or APP_ID,
            "payload": {
                "epoch_id": int(generate_offline_threading_id()),
                "tasks": tasks,
                "version_id": VERSION_ID,
            },
            "request_id": (api.ctx.get("wsReqNumber") or 0) + 1,
            "type": 3,
        }
        context["payload"] = json.dumps(context["payload"])  # serialize
        api.ctx["wsReqNumber"] = context["request_id"]

        client.publish("/ls_req", json.dumps(context), qos=1, retain=False)
        return {"success": True, "action": action, "threadID": threadID, "messageID": messageID}

    api.pinMessage = pinMessage
