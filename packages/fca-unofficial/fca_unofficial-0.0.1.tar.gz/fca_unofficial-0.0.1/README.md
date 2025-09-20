# python-facebookapi

python-facebookapi: Unofficial Facebook Messenger API (Python) developed by Adnan Sami Bhuiyan.

Status: Experimental WIP. Supports cookie-based login (appState) and basic HTTP wrappers. MQTT realtime and full endpoint parity are in progress.

## Install (editable)

- Local development: use pip in editable mode from this folder.

## Quickstart

```python
from python_facebookapi import login

api = login({"appState": [
    {"key": "c_user", "value": "123456789"},
    {"key": "xs", "value": "..."},
    # other cookies
]})

print("Logged in as:", api.get_current_user_id())
status, res = api.httpGet("https://www.facebook.com/")
print(status)
```

## MQTT realtime (preview)

```python
from python_facebookapi import login

api = login({"appState": [
    {"key": "c_user", "value": "123456789"},
    {"key": "xs", "value": "..."},
]})

def on_event(err, event):
    if err:
        print("MQTT error:", err)
        return
    print("event:", event)

listener = api.listenMqtt(on_event)

# Send a message via MQTT
api.sendMessageMqtt("Hello MQTT", threadID="<THREAD_ID>")

# React to a message
api.setMessageReactionMqtt("<MESSAGE_ID>", "🙂", threadID="<THREAD_ID>")

# Typing indicator
api.sendTypingIndicatorV2("<THREAD_ID>", True)

# Admin actions
api.nickname("Cool Guy", "<THREAD_ID>", participantID="<USER_ID>")
api.gcname("New Group Name", "<THREAD_ID>")
api.gcmember("add", ["<USER_ID>"], "<THREAD_ID>")
api.gcrule("admin", "<USER_ID>", "<THREAD_ID>")
api.pinMessage("pin", "<THREAD_ID>", "<MESSAGE_ID>")

# Stop listener when done
listener.stop()
```

Dependencies for realtime: paho-mqtt, websocket-client (declared in pyproject).

## Run tests (optional)

If you have pytest installed in your environment:

```bash
pytest -q
```

## Notes
- Use valid cookies (appState). Email/password login is intentionally not implemented.
- For proxies, pass options={"proxy": "http://host:port"}.
- Headers are randomized with realistic UA strings.
