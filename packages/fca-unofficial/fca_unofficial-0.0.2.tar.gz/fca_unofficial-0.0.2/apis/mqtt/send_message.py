from typing import Any, Dict
from ...utils.logging import log
import json
import time
import random

from ...utils.helpers import (
    generate_offline_threading_id,
    generate_threading_id,
    get_signature_id,
    generate_timestamp_relative,
)


def attach_send_message(api: Any) -> None:
    def sendMessageMqtt(msg: Dict[str, Any], threadID: str, replyToMessage: str | None = None, isSingleUser: bool = False):
        if not api.ctx.get("mqttClient"):
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        if isinstance(msg, str):
            msg = {"body": msg}
        otid = generate_offline_threading_id()
        form: Dict[str, Any] = {
            "client": "mercury",
            "action_type": "ma-type:user-generated-message",
            "author": f"fbid:{api.ctx.get('userID')}",
            "timestamp": int(time.time() * 1000),
            "timestamp_absolute": "Today",
            "timestamp_relative": generate_timestamp_relative(),
            "timestamp_time_passed": "0",
            "is_unread": False,
            "is_cleared": False,
            "is_forward": False,
            "is_filtered_content": False,
            "is_filtered_content_bh": False,
            "is_filtered_content_account": False,
            "is_filtered_content_quasar": False,
            "is_spoof_warning": False,
            "source": "source:chat:web",
            "source_tags[0]": "source:chat",
            "html_body": False,
            "ui_push_phase": "V3",
            "status": "0",
            "offline_threading_id": otid,
            "message_id": otid,
            "threading_id": generate_threading_id(api.ctx.get("clientID")),
            "ephemeral_ttl_mode:": "0",
            "manual_retry_cnt": "0",
            "has_attachment": bool(msg.get("attachment") or msg.get("url") or msg.get("sticker")),
            "signatureID": get_signature_id(),
        }
        if msg.get("body"):
            form["body"] = msg["body"]
        if replyToMessage:
            form["replied_to_message_id"] = replyToMessage
        if isinstance(threadID, list):
            for i, t in enumerate(threadID):
                form[f"specific_to_list[{i}]"] = f"fbid:{t}"
            form[f"specific_to_list[{len(threadID)}]"] = f"fbid:{api.ctx.get('userID')}"
            form["client_thread_id"] = f"root:{otid}"
        else:
            if isSingleUser:
                form["specific_to_list[0]"] = f"fbid:{threadID}"
                form["specific_to_list[1]"] = f"fbid:{api.ctx.get('userID')}"
                form["other_user_fbid"] = threadID
            else:
                form["thread_fbid"] = threadID

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
        if api.ctx.get("globalOptions", {}).get("logging"):
            log("sendMessage MQTT ->", {
                "topic": "/ls_req",
                "hasBody": bool(msg.get("body")),
                "isSingleUser": bool(isSingleUser),
                "threadID": threadID,
            })
        client.publish("/ls_req", json.dumps(context), qos=1, retain=False)
        res = {"messageID": otid}
        if api.ctx.get("globalOptions", {}).get("logging"):
            log("sendMessage MQTT <-", res)
        return res

    api.sendMessageMqtt = sendMessageMqtt
