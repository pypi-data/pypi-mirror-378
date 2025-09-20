from typing import Any, Dict
import json
import time

from ...utils.helpers import generate_offline_threading_id  # type: ignore


def attach_set_reaction(api: Any) -> None:
    def setMessageReactionMqtt(messageID: str, reaction: str | None, threadID: str):
        if not api.ctx.get("mqttClient"):
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        form: Dict[str, Any] = {
            "reaction": reaction or "",
            "action": "ADD_REACTION" if reaction else "REMOVE_REACTION",
            "client": "mercury",
            "message_id": messageID,
            "actor_id": api.ctx.get("userID"),
            "thread_id": threadID,
        }
        context = {
            "app_id": api.ctx.get("appID") or "2220391788200892",
            "payload": {
                "epoch_id": int(generate_offline_threading_id()),
                "tasks": [{
                    "failure_count": None,
                    "label": "46",
                    "payload": json.dumps(form),
                    "queue_name": "messenger_sync_create_queue",
                    "task_id": (api.ctx.get("wsTaskNumber") or 0) + 1,
                }],
                "version_id": "7214102258676893",
            },
            "request_id": (api.ctx.get("wsReqNumber") or 0) + 1,
            "type": 3,
        }
        context["payload"] = json.dumps(context["payload"])  # serialize payload
        api.ctx["wsReqNumber"] = context["request_id"]
        api.ctx["wsTaskNumber"] = (api.ctx.get("wsTaskNumber") or 0) + 1

        client = api.ctx.get("mqttClient")
        client.publish("/ls_req", json.dumps(context), qos=1, retain=False)
        return {"messageID": messageID, "reaction": reaction}

    api.setMessageReactionMqtt = setMessageReactionMqtt
