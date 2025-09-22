from typing import Any, Dict, List, Optional
from ..utils.logging import log, warn


def attach_messaging(api: Any) -> None:
    # sendMessage (HTTP)
    def sendMessage(msg: Dict[str, Any], threadID: Any, replyToMessage: Optional[str] = None, isSingleUser: bool = False):
        if isinstance(msg, str):
            msg = {"body": msg}

        if not isinstance(msg, dict):
            raise ValueError("Message must be string or dict")

        # minimal validation and build form similar to JS
        utils = api  # reuse helpers on api where available
        messageAndOTID = api.defaultFuncs  # just to signal context
        import time
        from ..utils.helpers import generate_offline_threading_id, generate_threading_id, get_signature_id, generate_timestamp_relative
        messageAndOTID = generate_offline_threading_id()

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
            "offline_threading_id": messageAndOTID,
            "message_id": messageAndOTID,
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

        # address thread target
        if isinstance(threadID, list):
            for i, t in enumerate(threadID):
                form[f"specific_to_list[{i}]"] = f"fbid:{t}"
            form[f"specific_to_list[{len(threadID)}]"] = f"fbid:{api.ctx.get('userID')}"
            form["client_thread_id"] = f"root:{messageAndOTID}"
        else:
            if isSingleUser:
                form["specific_to_list[0]"] = f"fbid:{threadID}"
                form["specific_to_list[1]"] = f"fbid:{api.ctx.get('userID')}"
                form["other_user_fbid"] = threadID
            else:
                form["thread_fbid"] = threadID

        # Debug: basic target summary
        if api.ctx.get("globalOptions", {}).get("logging"):
            tgt = {
                "isSingleUser": bool(isSingleUser),
                "threadID": threadID,
                "hasBody": bool(msg.get("body")),
                "hasAttachment": bool(msg.get("attachment") or msg.get("url") or msg.get("sticker")),
            }
            log("sendMessage HTTP ->", tgt)

        status, res = api.defaultFuncs.post("https://www.facebook.com/messaging/send/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"sendMessage failed with status {status}")
        # best-effort payload parse
        import json
        try:
            payload = json.loads((res.get("body") or "").replace("for (;;);", ""))
        except Exception:
            payload = {}
        # Detect common error shapes
        if isinstance(payload, dict):
            err = payload.get("error") or payload.get("errorDescription") or payload.get("errorSummary")
            if err:
                raise RuntimeError(f"sendMessage error: {err}")
            if payload.get("payload") is None and not payload.get("actions"):
                # Sometimes errors hide under 't' or other keys; log for debugging
                if api.ctx.get("globalOptions", {}).get("logging"):
                    warn("sendMessage: unexpected response structure", payload)
        actions = ((payload or {}).get("payload") or {}).get("actions") or []
        info = None
        for a in actions:
            info = {
                "threadID": a.get("thread_fbid"),
                "messageID": a.get("message_id"),
                "timestamp": a.get("timestamp"),
            }
            break
        result = info or {"messageID": messageAndOTID}
        if api.ctx.get("globalOptions", {}).get("logging"):
            log("sendMessage HTTP <-", {k: result.get(k) for k in ("messageID", "threadID", "timestamp")})
        return result

    def unsendMessage(messageID: str):
        form = {"message_id": messageID}
        status, res = api.defaultFuncs.post("https://www.facebook.com/messaging/unsend_message/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"unsendMessage failed with status {status}")
        return True

    def setMessageReaction(reaction: str, messageID: str):
        variables = {
            "data": {
                "client_mutation_id": api.ctx.get("clientMutationId", 0) + 1,
                "actor_id": api.ctx.get("userID"),
                "action": "REMOVE_REACTION" if reaction == "" else "ADD_REACTION",
                "message_id": messageID,
                "reaction": reaction,
            }
        }
        api.ctx["clientMutationId"] = variables["data"]["client_mutation_id"]
        status, res = api.defaultFuncs.postFormData(
            "https://www.facebook.com/webgraphql/mutation/",
            api.ctx.get("jar"),
            {},
            {"doc_id": "1491398900900362", "variables": __import__("json").dumps(variables), "dpr": 1},
            api.ctx,
        )
        if status < 200 or status >= 300:
            raise RuntimeError(f"setMessageReaction failed with status {status}")
        return True

    def markAsSeen(seen_timestamp: Optional[int] = None):
        if seen_timestamp is None:
            import time
            seen_timestamp = int(time.time() * 1000)
        form = {"seen_timestamp": seen_timestamp}
        status, _ = api.defaultFuncs.post("https://www.facebook.com/ajax/mercury/mark_seen.php", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"markAsSeen failed with status {status}")
        return True

    def markAsRead(threadID: str, read: bool = True):
        form: Dict[str, Any] = {}
        # Pages flow uses HTTP endpoint
        if api.ctx.get("globalOptions", {}).get("pageID") is not None:
            form["source"] = "PagesManagerMessagesInterface"
            form["request_user_id"] = api.ctx.get("globalOptions", {}).get("pageID")
            form[f"ids[{threadID}]"] = read
            form["watermarkTimestamp"] = __import__("time").time() * 1000
            form["shouldSendReadReceipt"] = True
            form["commerce_last_message_type"] = ""
            status, _ = api.defaultFuncs.post("https://www.facebook.com/ajax/mercury/change_read_status.php", api.ctx.get("jar"), form, api.ctx)
            if status < 200 or status >= 300:
                raise RuntimeError(f"markAsRead failed with status {status}")
            return True
        # MQTT path if connected
        client = api.ctx.get("mqttClient")
        if client:
            payload = {
                "threadID": str(threadID),
                "mark": "read",
                "state": bool(read),
            }
            # qos=1 and no retain, consistent with JS
            client.publish("/mark_thread", __import__("json").dumps(payload), qos=1, retain=False)
            return True
        raise RuntimeError("markAsRead requires MQTT connection (call api.listenMqtt()).")

    def markAsDelivered(threadID: str, messageID: str):
        form: Dict[str, Any] = {}
        form["message_ids[0]"] = messageID
        form[f"thread_ids[{threadID}][0]"] = messageID
        status, _ = api.defaultFuncs.post("https://www.facebook.com/ajax/mercury/delivery_receipts.php", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"markAsDelivered failed with status {status}")
        return True

    def markAsReadAll():
        status, _ = api.defaultFuncs.post("https://www.facebook.com/ajax/mercury/mark_folder_as_read.php", api.ctx.get("jar"), {"folder": "inbox"}, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"markAsReadAll failed with status {status}")
        return True

    def sendTypingIndicatorV2(sendTyping: bool, threadID: str):
        # Requires MQTT client; implement when listenMqtt is added
        raise NotImplementedError("sendTypingIndicatorV2 requires MQTT listen to be active.")

    def resolvePhotoUrl(photoID: str):
        status, res = api.defaultFuncs.get("https://www.facebook.com/mercury/attachments/photo", api.ctx.get("jar"), {"photo_id": photoID}, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"resolvePhotoUrl failed with status {status}")
        # The JS implementation reads jsmods; here we return the raw HTML for now.
        return res.get("body")

    def listThemes() -> List[Dict[str, Any]]:
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "MWPThreadThemeQuery_AllThemesQuery",
            "variables": __import__("json").dumps({"version": "default"}),
            "server_timestamps": True,
            "doc_id": "24474714052117636",
        }
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, {
            "x-fb-friendly-name": "MWPThreadThemeQuery_AllThemesQuery",
            "x-fb-lsd": api.ctx.get("lsd"),
        })
        if status < 200 or status >= 300:
            raise RuntimeError(f"listThemes failed with status {status}")
        import json as _json
        data = _json.loads((res.get("body") or "").replace("for (;;);", ""))
        arr = (((data.get("data") or {}).get("messenger_thread_themes")) or [])
        out: List[Dict[str, Any]] = []
        for themeData in arr:
            if not themeData or not themeData.get("id"):
                continue
            out.append({
                "id": themeData.get("id"),
                "name": themeData.get("accessibility_label"),
                "description": themeData.get("description"),
                "appColorMode": themeData.get("app_color_mode"),
                "composerBackgroundColor": themeData.get("composer_background_color"),
                "backgroundGradientColors": themeData.get("background_gradient_colors"),
                "titleBarButtonTintColor": themeData.get("title_bar_button_tint_color"),
                "inboundMessageGradientColors": themeData.get("inbound_message_gradient_colors"),
                "titleBarTextColor": themeData.get("title_bar_text_color"),
                "composerTintColor": themeData.get("composer_tint_color"),
                "titleBarAttributionColor": themeData.get("title_bar_attribution_color"),
                "composerInputBackgroundColor": themeData.get("composer_input_background_color"),
                "hotLikeColor": themeData.get("hot_like_color"),
                "backgroundImage": (((themeData.get("background_asset") or {}).get("image") or {}).get("uri")),
                "messageTextColor": themeData.get("message_text_color"),
                "inboundMessageTextColor": themeData.get("inbound_message_text_color"),
                "primaryButtonBackgroundColor": themeData.get("primary_button_background_color"),
                "titleBarBackgroundColor": themeData.get("title_bar_background_color"),
                "tertiaryTextColor": themeData.get("tertiary_text_color"),
                "reactionPillBackgroundColor": themeData.get("reaction_pill_background_color"),
                "secondaryTextColor": themeData.get("secondary_text_color"),
                "fallbackColor": themeData.get("fallback_color"),
                "gradientColors": themeData.get("gradient_colors"),
                "normalThemeId": themeData.get("normal_theme_id"),
                "iconAsset": (((themeData.get("icon_asset") or {}).get("image") or {}).get("uri")),
            })
        return out

    def shareContact(text: str, senderID: str, threadID: str):
        # Requires MQTT; expose signature and raise with hint
        raise NotImplementedError("shareContact requires MQTT client (listenMqtt) which is not yet implemented in Python port.")

    # Attach to api
    api.sendMessage = sendMessage
    api.unsendMessage = unsendMessage
    api.setMessageReaction = setMessageReaction
    api.markAsSeen = markAsSeen
    api.markAsRead = markAsRead
    api.markAsDelivered = markAsDelivered
    api.markAsReadAll = markAsReadAll
    api.sendTypingIndicatorV2 = sendTypingIndicatorV2
    api.resolvePhotoUrl = resolvePhotoUrl
    api.listThemes = listThemes
    api.shareContact = shareContact
