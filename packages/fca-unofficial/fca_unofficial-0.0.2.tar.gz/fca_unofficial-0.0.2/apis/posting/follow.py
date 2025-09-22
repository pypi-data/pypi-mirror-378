from typing import Any, Dict
import json


def attach_follow(api: Any) -> None:
    """Attach postFollow api.postFollow(senderID: str, follow: bool)."""

    def postFollow(senderID: str, follow: bool = True):
        if not senderID:
            raise ValueError("senderID is required")
        if follow:
            friendly = "CometUserFollowMutation"
            doc_id = "25472099855769847"
            variables: Dict[str, Any] = {
                "input": {
                    "attribution_id_v2": "ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,via_cold_start,1717249218695,723451,250100865708545,,",
                    "is_tracking_encrypted": True,
                    "subscribe_location": "PROFILE",
                    "subscribee_id": senderID,
                    "tracking": None,
                    "actor_id": api.ctx.get("userID"),
                    "client_mutation_id": "1",
                },
                "scale": 1,
            }
        else:
            friendly = "CometUserUnfollowMutation"
            doc_id = "25472099855769847"
            variables = {
                "action_render_location": "WWW_COMET_FRIEND_MENU",
                "input": {
                    "attribution_id_v2": "ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,tap_search_bar,1717294006136,602597,250100865708545,,",
                    "is_tracking_encrypted": True,
                    "subscribe_location": "PROFILE",
                    "tracking": None,
                    "unsubscribee_id": senderID,
                    "actor_id": api.ctx.get("userID"),
                    "client_mutation_id": "10",
                },
                "scale": 1,
            }

        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": friendly,
            "variables": json.dumps(variables),
            "doc_id": doc_id,
        }
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"postFollow failed with status {status}")
        try:
            return json.loads((res.get("body") or "").replace("for (;;);", ""))
        except Exception:
            return {"ok": True}

    api.postFollow = postFollow
