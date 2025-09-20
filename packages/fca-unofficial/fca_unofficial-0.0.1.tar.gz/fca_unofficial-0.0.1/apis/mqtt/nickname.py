from typing import Any, Dict
import json
from ...utils.helpers import generate_offline_threading_id


def attach_nickname(api: Any) -> None:
    def nickname(nickname: str, threadID: str, participantID: str | None = None, initiatorID: str | None = None):
        client = api.ctx.get("mqttClient")
        if not client:
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        participantID = participantID or api.ctx.get("userID")
        api.ctx["wsReqNumber"] = (api.ctx.get("wsReqNumber") or 0) + 1
        api.ctx["wsTaskNumber"] = (api.ctx.get("wsTaskNumber") or 0) + 1
        query_payload: Dict[str, Any] = {
            "thread_key": str(threadID),
            "contact_id": str(participantID),
            "nickname": nickname,
            "sync_group": 1,
        }
        query = {
            "failure_count": None,
            "label": "44",
            "payload": json.dumps(query_payload),
            "queue_name": "thread_participant_nickname",
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
            "type": "thread_nickname_update",
            "threadID": threadID,
            "participantID": participantID,
            "newNickname": nickname,
            "senderID": initiatorID or api.ctx.get("userID"),
            "BotID": api.ctx.get("userID"),
        }

    api.nickname = nickname
