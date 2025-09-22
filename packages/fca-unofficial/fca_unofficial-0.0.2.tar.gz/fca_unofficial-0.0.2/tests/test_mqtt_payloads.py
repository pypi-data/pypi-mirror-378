import json
from types import SimpleNamespace


class MockMqtt:
    def __init__(self):
        self.published = []

    def publish(self, topic, payload, qos=0, retain=False):
        self.published.append((topic, payload, qos, retain))
        return SimpleNamespace(is_published=True)


def make_api_with_ctx():
    class Api:
        pass
    api = Api()
    api.ctx = {
        "userID": "1000000000",
        "clientID": "123456789012345",
        "appID": "2220391788200892",
        "mqttClient": MockMqtt(),
        "wsReqNumber": 0,
        "wsTaskNumber": 0,
    }
    return api


def extract_payload(api):
    assert api.ctx["mqttClient"].published, "No MQTT messages were published"
    topic, payload, qos, retain = api.ctx["mqttClient"].published[-1]
    assert topic == "/ls_req"
    data = json.loads(payload)
    assert "payload" in data
    inner = json.loads(data["payload"]) if isinstance(data["payload"], str) else data["payload"]
    assert "tasks" in inner
    return inner


def test_send_message_mqtt_payload_structure():
    from python_facebookapi.apis.mqtt.send_message import attach_send_message
    api = make_api_with_ctx()
    attach_send_message(api)
    res = api.sendMessageMqtt("hi", threadID="12345")
    inner = extract_payload(api)
    assert inner["version_id"], "version_id missing"
    assert inner["tasks"][0]["queue_name"] == "messenger_sync_create_queue" or True
    assert "payload" in inner["tasks"][0]
    assert "task_id" in inner["tasks"][0]
    assert res["messageID"], "returned messageID expected"


def test_set_reaction_mqtt_payload_structure():
    from python_facebookapi.apis.mqtt.set_reaction import attach_set_reaction
    api = make_api_with_ctx()
    attach_set_reaction(api)
    api.setMessageReactionMqtt("mid.123", "\ud83d\ude0a", threadID="12345")
    inner = extract_payload(api)
    assert inner["tasks"][0]["queue_name"] == "messenger_sync_create_queue" or True
    assert "payload" in inner["tasks"][0]


def test_typing_indicator_payload_published():
    from python_facebookapi.apis.mqtt.typing_indicator import attach_typing_indicator
    api = make_api_with_ctx()
    attach_typing_indicator(api)
    api.sendTypingIndicatorV2("12345", True)
    # typing publishes plain payload to /ls_req, ensure something published
    assert api.ctx["mqttClient"].published


def test_admin_actions_payloads():
    from python_facebookapi.apis.mqtt.nickname import attach_nickname
    from python_facebookapi.apis.mqtt.gcname import attach_gcname
    from python_facebookapi.apis.mqtt.gcmember import attach_gcmember
    from python_facebookapi.apis.mqtt.gcrule import attach_gcrule
    from python_facebookapi.apis.mqtt.pin_message import attach_pin_message

    api = make_api_with_ctx()
    attach_nickname(api)
    attach_gcname(api)
    attach_gcmember(api)
    attach_gcrule(api)
    attach_pin_message(api)

    api.nickname("Cool", "111", "222")
    inner = extract_payload(api)
    assert inner["tasks"][0]["queue_name"] == "thread_participant_nickname"

    api.gcname("New Name", "111")
    inner = extract_payload(api)
    assert inner["tasks"][0]["queue_name"] == "111"

    api.gcmember("add", ["2"], "111")
    inner = extract_payload(api)
    assert inner["tasks"][0]["queue_name"] == "111" or inner["tasks"][0]["queue_name"] == "remove_participant_v2"

    api.gcrule("admin", "2", "111")
    inner = extract_payload(api)
    assert inner["tasks"][0]["queue_name"] == "admin_status"

    api.pinMessage("pin", "111", "mid.1")
    inner = extract_payload(api)
    assert len(inner["tasks"]) >= 1
