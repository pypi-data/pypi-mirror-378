from typing import Any, Dict, List
import json
import base64
import random


def attach_friend(api: Any) -> None:
    """Attach friend API as api.friend with requests, accept, list, suggest.list, suggest.request."""

    def _post(form: Dict[str, Any]) -> Dict[str, Any]:
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"GraphQL failed with status {status}")
        try:
            data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        except Exception as e:
            raise RuntimeError("Failed parsing GraphQL response") from e
        if isinstance(data, dict) and data.get("errors"):
            # bubble the first error
            raise RuntimeError(json.dumps(data["errors"]))
        return data

    def _format_friends(data: Dict[str, Any], typ: str) -> List[Dict[str, Any]]:
        viewer = ((data.get("data") or {}).get("viewer")) or {}
        edges: List[Dict[str, Any]] = []
        if typ == "requests":
            edges = ((viewer.get("friend_requests") or {}).get("edges")) or []
        elif typ == "suggestions":
            edges = ((viewer.get("people_you_may_know") or {}).get("edges")) or []
        elif typ == "list":
            node = (data.get("data") or {}).get("node") or {}
            edges = (((((node.get("all_collections") or {}).get("nodes") or [{}])[0]).get("style_renderer") or {}).get("collection") or {}).get("pageItems", {}).get("edges", [])
        out: List[Dict[str, Any]] = []
        for e in edges:
            n = e.get("node") or {}
            user_id = n.get("id") or (n.get("node") or {}).get("id")
            out.append({
                "userID": user_id,
                "name": n.get("name") or ((n.get("title") or {}).get("text")),
                "profilePicture": ((n.get("profile_picture") or {}).get("uri") or (n.get("image") or {}).get("uri")),
                "socialContext": ((n.get("social_context") or {}).get("text") or (n.get("subtitle_text") or {}).get("text")),
                "url": n.get("url"),
            })
        return [x for x in out if x.get("userID")]

    class SuggestAPI:
        def list(self, limit: int = 30) -> List[Dict[str, Any]]:
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "FriendingCometPYMKPanelPaginationQuery",
                "variables": json.dumps({"count": limit, "cursor": None, "scale": 3}),
                "doc_id": "9917809191634193",
            }
            data = _post(form)
            return _format_friends(data, "suggestions")

        def request(self, userID: str) -> Dict[str, Any]:
            if not userID:
                raise ValueError("userID is required")
            variables = {
                "input": {
                    "friend_requestee_ids": [userID],
                    "friending_channel": "FRIENDS_HOME_MAIN",
                    "actor_id": api.ctx.get("userID"),
                    "client_mutation_id": str(random.randint(1, 10)),
                },
                "scale": 3,
            }
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "FriendingCometFriendRequestSendMutation",
                "variables": json.dumps(variables),
                "doc_id": "23982103144788355",
            }
            data = _post(form)
            return data.get("data") or {}

    class FriendAPI:
        def requests(self) -> List[Dict[str, Any]]:
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "FriendingCometRootContentQuery",
                "variables": json.dumps({"scale": 3}),
                "doc_id": "9103543533085580",
            }
            data = _post(form)
            return _format_friends(data, "requests")

        def accept(self, identifier: str) -> Dict[str, Any]:
            if not identifier:
                raise ValueError("A name or user ID is required.")
            target = identifier
            if not identifier.isdigit():
                reqs = self.requests()
                found = next((r for r in reqs if r.get("name", "").lower().find(identifier.lower()) != -1), None)
                if not found:
                    raise RuntimeError(f"Could not find any friend request matching '{identifier}'.")
                target = found["userID"]
            variables = {
                "input": {
                    "friend_requester_id": target,
                    "friending_channel": "FRIENDS_HOME_MAIN",
                    "actor_id": api.ctx.get("userID"),
                    "client_mutation_id": str(random.randint(1, 10)),
                },
                "scale": 3,
            }
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "FriendingCometFriendRequestConfirmMutation",
                "variables": json.dumps(variables),
                "doc_id": "24630768433181357",
            }
            try:
                data = _post(form)
                return data.get("data") or {}
            except Exception as err:
                msg = str(err)
                if "1431004" in msg:
                    raise RuntimeError("Cannot accept this friend request right now. Account may be restricted or need to wait.") from err
                raise

        def list(self, userID: str | None = None) -> List[Dict[str, Any]]:
            userID = userID or api.ctx.get("userID")
            section_token = base64.b64encode((f"app_section:{userID}:2356318349").encode()).decode()
            variables = {
                "collectionToken": None,
                "scale": 2,
                "sectionToken": section_token,
                "useDefaultActor": False,
                "userID": userID,
            }
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "ProfileCometTopAppSectionQuery",
                "variables": json.dumps(variables),
                "doc_id": "24492266383698794",
            }
            data = _post(form)
            return _format_friends(data, "list")

        @property
        def suggest(self) -> SuggestAPI:
            return SuggestAPI()

    api.friend = FriendAPI()
