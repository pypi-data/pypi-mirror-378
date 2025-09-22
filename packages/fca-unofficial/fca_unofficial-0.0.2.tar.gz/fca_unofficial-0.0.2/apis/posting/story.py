from typing import Any, Dict
import json
import random
from urllib.parse import urlparse


def attach_story(api: Any) -> None:
    """Attach story APIs: api.story.create, api.story.react, api.story.msg"""

    def _post(form: Dict[str, Any]) -> Dict[str, Any]:
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Story GraphQL failed with status {status}")
        try:
            data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        except Exception as e:
            raise RuntimeError("Failed parsing GraphQL response") from e
        if isinstance(data, dict) and data.get("errors"):
            raise RuntimeError(json.dumps(data["errors"]))
        return data

    def _get_story_id_from_url(url: str) -> str | None:
        try:
            p = urlparse(url)
            parts = p.path.split('/')
            if 'stories' in parts:
                idx = parts.index('stories')
                if len(parts) > idx + 2:
                    return parts[idx + 2]
            return None
        except Exception:
            return None

    def _send_story_reply(storyIdOrUrl: str, message: str, isReaction: bool) -> Dict[str, Any]:
        allowed = ["\u2764\ufe0f", "\ud83d\udc4d", "\ud83e\udd17", "\ud83d\ude06", "\ud83d\ude21", "\ud83d\ude22", "\ud83d\ude2e"]
        if not storyIdOrUrl:
            raise ValueError("Story ID or URL is required.")
        if not message:
            raise ValueError("A message or reaction is required.")
        storyID = _get_story_id_from_url(storyIdOrUrl) or storyIdOrUrl
        variables: Dict[str, Any] = {
            "input": {
                "attribution_id_v2": "StoriesCometSuspenseRoot.react,comet.stories.viewer,via_cold_start",
                "message": message,
                "story_id": storyID,
                "story_reply_type": "LIGHT_WEIGHT" if isReaction else "TEXT",
                "actor_id": api.ctx.get("userID"),
                "client_mutation_id": str(random.randint(1, 10)),
            }
        }
        if isReaction:
            if message not in allowed:
                raise ValueError("Invalid reaction. Use one of: " + " ".join(allowed))
            variables["input"]["lightweight_reaction_actions"] = {"offsets": [0], "reaction": message}
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "useStoriesSendReplyMutation",
            "variables": json.dumps(variables),
            "doc_id": "9697491553691692",
        }
        data = _post(form)
        dm = (((data.get("data") or {}).get("direct_message_reply")))
        if not dm:
            raise RuntimeError("Could not find 'direct_message_reply' in response.")
        return {"success": True, "result": dm}

    def _create(message: str, fontName: str = "classic", backgroundName: str = "blue") -> Dict[str, Any]:
        fontMap = {
            "headline": "1919119914775364",
            "classic": "516266749248495",
            "casual": "516266749248495",
            "fancy": "1790435664339626",
        }
        bgMap = {
            "orange": "2163607613910521",
            "blue": "401372137331149",
            "green": "367314917184744",
            "modern": "554617635055752",
        }
        fontId = fontMap.get((fontName or "").lower(), fontMap["classic"])  # default classic
        bgId = bgMap.get((backgroundName or "").lower(), bgMap["blue"])   # default blue
        variables = {
            "input": {
                "audiences": [{"stories": {"self": {"target_id": api.ctx.get("userID")}}}],
                "audiences_is_complete": True,
                "logging": {"composer_session_id": "createStoriesText-" + str(__import__('time').time())},
                "navigation_data": {"attribution_id_v2": "StoriesCreateRoot.react,comet.stories.create"},
                "source": "WWW",
                "message": {"ranges": [], "text": message},
                "text_format_metadata": {"inspirations_custom_font_id": fontId},
                "text_format_preset_id": bgId,
                "tracking": [None],
                "actor_id": api.ctx.get("userID"),
                "client_mutation_id": "2",
            }
        }
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "StoriesCreateMutation",
            "variables": json.dumps(variables),
            "doc_id": "24226878183562473",
        }
        data = _post(form)
        storyNode = ((((data.get("data") or {}).get("story_create") or {}).get("viewer") or {}).get("actor") or {}).get("story_bucket", {}).get("nodes", [{}])[0].get("first_story_to_show")
        if not storyNode or not storyNode.get("id"):
            raise RuntimeError("Could not find the storyCardID in the response.")
        return {"success": True, "storyID": storyNode.get("id")}

    class StoryAPI:
        def create(self, message: str, fontName: str = "classic", backgroundName: str = "blue") -> Dict[str, Any]:
            return _create(message, fontName, backgroundName)

        def react(self, storyIdOrUrl: str, reaction: str) -> Dict[str, Any]:
            return _send_story_reply(storyIdOrUrl, reaction, True)

        def msg(self, storyIdOrUrl: str, message: str) -> Dict[str, Any]:
            return _send_story_reply(storyIdOrUrl, message, False)

    api.story = StoryAPI()
