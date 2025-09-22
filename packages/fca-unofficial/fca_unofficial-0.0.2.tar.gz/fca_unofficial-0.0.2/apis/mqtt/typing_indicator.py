from typing import Any
import json
import time


def attach_typing_indicator(api: Any) -> None:
    def sendTypingIndicatorV2(threadID: str, isTyping: bool = True):
        client = api.ctx.get("mqttClient")
        if not client:
            raise RuntimeError("MQTT is not connected. Call api.listenMqtt() first.")
        payload = {
            "type": "typ",
            "thread": threadID,
            "state": 1 if isTyping else 0,
            "to": threadID,
        }
        client.publish("/ls_req", json.dumps(payload), qos=0, retain=False)
        return {"threadID": threadID, "isTyping": isTyping}

    api.sendTypingIndicatorV2 = sendTypingIndicatorV2
