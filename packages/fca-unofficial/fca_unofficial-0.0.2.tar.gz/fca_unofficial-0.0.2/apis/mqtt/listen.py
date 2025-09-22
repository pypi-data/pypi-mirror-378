from typing import Any, Callable
import json
import time
import threading
import random
import os

import paho.mqtt.client as mqtt
from websocket import WebSocketApp  # reserved for realtime subscriptions (future)

TOPICS = [
    "/legacy_web", "/webrtc", "/rtc_multi", "/onevc", "/br_sr", "/sr_res",
    "/t_ms", "/thread_typing", "/orca_typing_notifications", "/notify_disconnect",
    "/orca_presence", "/inbox", "/mercury", "/messaging_events",
    "/orca_message_notifications", "/pp", "/webrtc_response"
]


def _build_username(ctx: dict) -> dict:
    session_id = random.randint(1, 2**31 - 1)
    return {
        "u": ctx.get("userID"),
        "s": session_id,
        "chat_on": ctx.get("globalOptions", {}).get("online", True),
        "fg": False,
        "d": ctx.get("clientID"),
        "ct": "websocket",
        "aid": ctx.get("mqttAppID") or "2220391788200892",
        "mqtt_sid": "",
        "cp": 3,
        "ecp": 10,
        "st": [],
        "pm": [],
        "dc": "",
        "no_auto_fg": True,
        "gas": None,
        "pack": [],
        "a": ctx.get("globalOptions", {}).get("userAgent"),
    }


def attach_listen(api: Any) -> None:
    def listenMqtt(callback: Callable[[dict | None, dict | None], None] | None = None):
        """Connect to Facebook MQTT and emit messages via callback.
        Returns an object with .stop() to end listening.
        """
        ctx = api.ctx
        # Enable internal logging based on ctx global options
        verbose_log = bool(ctx.get("globalOptions", {}).get("logging"))

        username = json.dumps(_build_username(ctx))
        # Build ws host like JS: wss://edge-chat.messenger.com/chat?sid=...&cid=...
        sid = random.randint(1, 2**31 - 1)
        cid = ctx.get("clientID") or str(random.randint(10**15, 10**16 - 1))
        if not ctx.get("clientID"):
            ctx["clientID"] = cid
        region = ctx.get("region")
        base = "wss://edge-chat.messenger.com/chat"
        qs = f"?sid={sid}&cid={cid}"
        if region:
            qs += f"&region={str(region).lower()}"
        host = base + qs

        # Grab cookie header
        try:
            cookies = "; ".join([c.name + "=" + c.value for c in ctx.get("jar")])
        except Exception:
            cookies = ""

        # Configure MQTT client using WebSocket transport (use v3.1 as in the stable version)
        client = mqtt.Client(client_id="mqttwsclient", transport="websockets", protocol=mqtt.MQTTv31)
        client.username_pw_set(username=username)
        client.tls_set()  # wss
        # paho uses host/path separately. Extract path from URL
        from urllib.parse import urlparse
        p = urlparse(host)
        ws_path = p.path + ("?" + p.query if p.query else "")

        # Add headers (Cookie, Origin, Referer, UA) as a dict for paho-mqtt
        headers = {
            # Revert to messenger.com, which matched the previously working handshake
            "Origin": "https://www.messenger.com",
            "Referer": "https://www.messenger.com/",
        }
        if cookies:
            headers["Cookie"] = cookies
        ua = ctx.get("globalOptions", {}).get("userAgent")
        if ua:
            headers["User-Agent"] = ua

        # Bind events
        stop_event = threading.Event()
        reconnect_attempt = {"count": 0}

        def _log(*args):
            if verbose_log:
                try:
                    print("[python-facebookapi][LOG] listenMqtt():", *args)
                except Exception:
                    pass

        def on_connect(_client, _userdata, _flags, rc):
            reconnect_attempt["count"] = 0  # reset on successful connect
            _log("on_connect rc=", rc)
            # Subscribe topics and publish sync queue
            for t in TOPICS:
                _client.subscribe(t)
                _log("subscribed", t)
            queue = {"sync_api_version": 10, "max_deltas_able_to_process": 1000, "delta_batch_size": 500, "encoding": "JSON", "entity_fbid": ctx.get("userID")}
            topic = "/messenger_sync_get_diffs" if ctx.get("syncToken") else "/messenger_sync_create_queue"
            if ctx.get("syncToken"):
                queue["last_seq_id"] = ctx.get("lastSeqId")
                queue["sync_token"] = ctx.get("syncToken")
            else:
                queue["initial_titan_sequence_id"] = ctx.get("lastSeqId")
                queue["device_params"] = None
            _client.publish(topic, json.dumps(queue), qos=1, retain=False)
            _log("published initial sync to", topic)

        def _emit(event: dict):
            if callback:
                try:
                    callback(None, event)
                except Exception:
                    pass

        def _thread_id_from_key(thread_key: dict | None) -> str | None:
            if not thread_key:
                return None
            # Prefer group thread id if present, else other user id
            if thread_key.get("threadFbId"):
                return str(thread_key["threadFbId"])
            if thread_key.get("otherUserFbId"):
                return str(thread_key["otherUserFbId"])
            return None

        def _parse_delta(delta: dict):
            # New message
            if delta.get("class") == "NewMessage" or (
                delta.get("messageMetadata") and ("body" in delta or "attachments" in delta)
            ):
                md = delta.get("messageMetadata", {})
                thread_id = _thread_id_from_key(md.get("threadKey"))
                event = {
                    "type": "message",
                    "messageID": md.get("messageId"),
                    "threadID": thread_id,
                    "author": str(md.get("actorFbId")) if md.get("actorFbId") else None,
                    "timestamp": int(md.get("timestamp")) if md.get("timestamp") else None,
                    "body": delta.get("body"),
                    "attachments": delta.get("attachments") or [],
                    "isGroup": True if md.get("threadKey", {}).get("threadFbId") else False,
                }
                _emit(event)
                return

            # Read receipts
            if delta.get("class") == "ReadReceipt" or delta.get("type") == "ReadReceipt" or delta.get("readReceipt"):
                rr = delta.get("readReceipt", delta)
                thread_id = _thread_id_from_key((rr.get("threadKey") or delta.get("threadKey")))
                event = {
                    "type": "read",
                    "threadID": thread_id,
                    "reader": str(rr.get("actorFbId") or rr.get("readerFbId") or ""),
                    "watermark": int(rr.get("watermarkTimestampMs") or rr.get("watermark") or 0),
                }
                _emit(event)
                return

            # Delivery receipts
            if delta.get("class") == "DeliveryReceipt" or delta.get("deliveryReceipt"):
                dr = delta.get("deliveryReceipt", delta)
                thread_id = _thread_id_from_key(dr.get("threadKey"))
                event = {
                    "type": "delivery",
                    "threadID": thread_id,
                    "actor": str(dr.get("actorFbId") or ""),
                    "watermark": int(dr.get("deliveredWatermarkTimestampMs") or 0),
                }
                _emit(event)
                return

            # Thread name change
            if delta.get("class") == "ThreadName" or delta.get("name"):
                md = delta.get("messageMetadata", {})
                thread_id = _thread_id_from_key(md.get("threadKey"))
                event = {
                    "type": "thread-name",
                    "threadID": thread_id,
                    "name": delta.get("name"),
                    "author": str(md.get("actorFbId") or ""),
                    "messageID": md.get("messageId"),
                    "timestamp": int(md.get("timestamp") or 0),
                }
                _emit(event)
                return

            # Participants added/removed
            if delta.get("class") in ("ParticipantsAddedToGroupThread", "ParticipantLeftGroupThread"):
                md = delta.get("messageMetadata", {})
                thread_id = _thread_id_from_key(md.get("threadKey"))
                event = {
                    "type": "participants",
                    "threadID": thread_id,
                    "added": [str(x) for x in (delta.get("addedParticipantsFbIds") or [])],
                    "removed": [str(x) for x in (delta.get("leftParticipantFbId") or [])]
                    if isinstance(delta.get("leftParticipantFbId"), list)
                    else ([str(delta.get("leftParticipantFbId"))] if delta.get("leftParticipantFbId") else []),
                    "author": str(md.get("actorFbId") or ""),
                    "messageID": md.get("messageId"),
                    "timestamp": int(md.get("timestamp") or 0),
                }
                _emit(event)
                return

            # Message unsend
            if delta.get("class") == "DeleteMessages" or delta.get("deletedMessageIds") or delta.get("retractedMessageIds"):
                md = delta.get("messageMetadata", {})
                thread_id = _thread_id_from_key(md.get("threadKey")) if md else None
                ids = delta.get("deletedMessageIds") or delta.get("retractedMessageIds") or []
                if isinstance(ids, str):
                    ids = [ids]
                event = {
                    "type": "message-unsend",
                    "threadID": thread_id,
                    "messageIDs": ids,
                }
                _emit(event)
                return

            # Reactions (best effort)
            if delta.get("class") in ("MessageReaction", "Reaction") or delta.get("messageReaction"):
                mr = delta.get("messageReaction", delta)
                md = mr.get("messageMetadata") or delta.get("messageMetadata") or {}
                thread_id = _thread_id_from_key(md.get("threadKey"))
                event = {
                    "type": "reaction",
                    "threadID": thread_id,
                    "messageID": md.get("messageId"),
                    "actor": str(mr.get("userId") or md.get("actorFbId") or ""),
                    "reaction": mr.get("reaction") or mr.get("reactionEmoji") or None,
                }
                _emit(event)
                return

            # Fallback: emit raw delta
            _emit({"type": "delta_raw", "delta": delta})

        def on_message(_client, _userdata, msg):
            # Lightweight log of incoming topics
            if verbose_log:
                try:
                    print("[python-facebookapi][LOG] listenMqtt(): msg topic=", msg.topic)
                except Exception:
                    pass
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
            except Exception:
                return
            if msg.topic == "/t_ms":
                if isinstance(payload, dict) and payload.get("lastIssuedSeqId"):
                    try:
                        ctx["lastSeqId"] = int(payload.get("lastIssuedSeqId"))
                    except Exception:
                        pass
                if isinstance(payload, dict) and payload.get("syncToken"):
                    ctx["syncToken"] = payload.get("syncToken")
                # Parse deltas
                for delta in (payload.get("deltas") or []):
                    try:
                        _parse_delta(delta)
                    except Exception:
                        _emit({"type": "delta_raw", "delta": delta})
            elif msg.topic in ("/thread_typing", "/orca_typing_notifications"):
                data = {
                    "type": "typ",
                    "isTyping": bool(payload.get("state")),
                    "from": str(payload.get("sender_fbid")),
                    "threadID": str((payload.get("thread") or payload.get("sender_fbid"))),
                }
                _emit(data)
            elif msg.topic == "/notify_disconnect":
                # Broker asks client to disconnect; we'll let on_disconnect handle reconnection
                _log("received /notify_disconnect")

        def on_error(_client, _userdata, rc):
            if callback:
                callback({"type": "error", "code": rc}, None)

        def on_disconnect(_client, _userdata, rc):
            if stop_event.is_set():
                return
            _log("on_disconnect rc=", rc)
            # Backoff with jitter
            reconnect_attempt["count"] += 1
            delay = min(30, (2 ** min(5, reconnect_attempt["count"])) + random.random())
            _log(f"reconnecting in {delay:.1f}s")
            def _reconnect():
                if stop_event.is_set():
                    return
                try:
                    _client.reconnect()
                except Exception as e:
                    _log("reconnect failed:", e)
            timer = threading.Timer(delay, _reconnect)
            timer.daemon = True
            timer.start()

        client.on_connect = on_connect
        client.on_message = on_message

        # Filter noisy paho logs (e.g., PINGREQ/PINGRESP). Set MQTT_TRACE=1 to see everything.
        def _on_log(_client, _userdata, level, buf):
            if not verbose_log:
                return
            trace = os.getenv("MQTT_TRACE", "").strip().lower() in ("1", "true", "yes", "on")
            if not trace:
                noisy = (
                    "PINGREQ" in buf or "PINGRESP" in buf or
                    "Sending SUBSCRIBE" in buf or "Received SUBACK" in buf or
                    "Sending CONNECT" in buf or "Received CONNACK" in buf
                )
                if noisy:
                    return
            try:
                print("[python-facebookapi][LOG] listenMqtt(): paho_log", _client, _userdata, level, buf)
            except Exception:
                pass

        client.on_log = _on_log if verbose_log else None
        client.on_disconnect = on_disconnect

        # Connect
        api.ctx["mqttClient"] = client
        client.ws_set_options(path=ws_path, headers=headers)
        # Configure reconnect delays and start async loop
        try:
            client.reconnect_delay_set(min_delay=1, max_delay=30)
        except Exception:
            pass
        # Longer keepalive is more tolerant to network jitter
        client.connect_async(p.hostname, port=443, keepalive=60)
        client.loop_start()

        class Listener:
            def stop(self):
                stop_event.set()
                try:
                    client.disconnect()
                finally:
                    api.ctx["mqttClient"] = None

        return Listener()

    api.listenMqtt = listenMqtt
