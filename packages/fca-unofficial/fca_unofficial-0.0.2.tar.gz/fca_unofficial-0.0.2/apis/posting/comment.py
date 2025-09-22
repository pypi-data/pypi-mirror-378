from typing import Any, Dict, List
import json
import base64
import random
import uuid


def attach_comment(api: Any) -> None:
    """Attach postComment api.postComment(msg, postID, replyCommentID=None)."""

    def _upload_attachment(stream) -> Dict[str, Any]:
        # Expects a file-like object; in Python we pass tuple (filename, fileobj, mime)
        form = {
            "profile_id": api.ctx.get("userID"),
            "source": 19,
            "target_id": api.ctx.get("userID"),
            "file": stream,
        }
        status, res = api.defaultFuncs.postFormData("https://www.facebook.com/ajax/ufi/upload/", api.ctx.get("jar"), form, {}, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Attachment upload failed with status {status}")
        data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        if (not isinstance(data, dict)) or (not data.get("payload") or not data["payload"].get("fbid")):
            raise RuntimeError("Upload response missing fbid")
        return {"media": {"id": data["payload"]["fbid"]}}

    def _handle_mentions(message: Dict[str, Any]) -> List[Dict[str, Any]]:
        ranges: List[Dict[str, Any]] = []
        mentions = message.get("mentions") or []
        body = message.get("body") or ""
        for m in mentions:
            tag = m.get("tag")
            mid = m.get("id")
            from_index = m.get("fromIndex", 0)
            if isinstance(tag, str) and mid:
                try:
                    offset = body.index(tag, from_index)
                except ValueError:
                    continue
                ranges.append({"entity": {"id": mid}, "length": len(tag), "offset": offset})
        return ranges

    def postComment(msg: Any, postID: str, replyCommentID: str | None = None):
        if not isinstance(msg, (str, dict)):
            raise ValueError("Message must be a string or an object")
        if not isinstance(postID, str):
            raise ValueError("postID must be a string")

        message: Dict[str, Any] = {"body": msg} if isinstance(msg, str) else dict(msg)
        message.setdefault("mentions", [])
        message.setdefault("attachments", [])

        feedback_id = base64.b64encode(("feedback:" + postID).encode()).decode()
        form_vars: Dict[str, Any] = {
            "feedLocation": "NEWSFEED",
            "feedbackSource": 1,
            "groupID": None,
            "input": {
                "client_mutation_id": str(random.randint(1, 19)),
                "actor_id": api.ctx.get("userID"),
                "attachments": [],
                "feedback_id": feedback_id,
                "message": {"ranges": [], "text": message.get("body") or ""},
                "reply_comment_parent_fbid": replyCommentID or None,
                "is_tracking_encrypted": True,
                "tracking": [],
                "feedback_source": "NEWS_FEED",
                "idempotence_token": "client:" + uuid.uuid4().hex,
                "session_id": uuid.uuid4().hex,
            },
            "scale": 1,
            "useDefaultActor": False,
        }

        # attachments
        attachments = message.get("attachments") or []
        for att in attachments:
            uploaded = _upload_attachment(att)
            form_vars["input"]["attachments"].append(uploaded)

        if isinstance(message.get("url"), str):
            form_vars["input"]["attachments"].append({"link": {"external": {"url": message["url"]}}})

        # mentions
        form_vars["input"]["message"]["ranges"] = _handle_mentions(message)

        # sticker
        if message.get("sticker"):
            form_vars["input"]["attachments"].append({"media": {"id": str(message["sticker"])}})

        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "useCometUFICreateCommentMutation",
            "variables": json.dumps(form_vars),
            "server_timestamps": True,
            "doc_id": "6993516810709754",
        }
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"postComment failed with status {status}")
        data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        edge = (((data.get("data") or {}).get("comment_create") or {}).get("feedback_comment_edge") or {})
        node = edge.get("node") or {}
        return {
            "id": node.get("id"),
            "url": ((node.get("feedback") or {}).get("url")),
            "count": (((data.get("data") or {}).get("comment_create") or {}).get("feedback") or {}).get("total_comment_count"),
        }

    api.postComment = postComment
