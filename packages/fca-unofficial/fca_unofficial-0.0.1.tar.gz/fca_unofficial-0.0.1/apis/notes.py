from typing import Any, Dict, Optional
import json


def attach_notes(api: Any) -> None:
    def _post(form: Dict[str, Any]):
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Notes GraphQL failed with status {status}")
        try:
            data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        except Exception:
            data = {}
        if isinstance(data, dict) and data.get("errors"):
            raise RuntimeError(data["errors"][0].get("message", "GraphQL error"))
        return data

    def check() -> Optional[Dict[str, Any]]:
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "MWInboxTrayNoteCreationDialogQuery",
            "variables": json.dumps({"scale": 2}),
            "doc_id": "30899655739648624",
        }
        data = _post(form)
        return (((data.get("data") or {}).get("viewer") or {}).get("actor") or {}).get("msgr_user_rich_status")

    def create(text: str, privacy: str = "EVERYONE") -> Any:
        variables = {
            "input": {
                "client_mutation_id": str(int(__import__("random").random() * 10)),
                "actor_id": api.ctx.get("userID"),
                "description": text,
                "duration": 86400,
                "note_type": "TEXT_NOTE",
                "privacy": privacy,
                "session_id": __import__("uuid").uuid4().hex,
            }
        }
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "MWInboxTrayNoteCreationDialogCreationStepContentMutation",
            "variables": json.dumps(variables),
            "doc_id": "24060573783603122",
        }
        data = _post(form)
        return (((data.get("data") or {}).get("xfb_rich_status_create") or {}).get("status"))

    def delete(noteID: str) -> Any:
        variables = {
            "input": {
                "client_mutation_id": str(int(__import__("random").random() * 10)),
                "actor_id": api.ctx.get("userID"),
                "rich_status_id": noteID,
            }
        }
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "useMWInboxTrayDeleteNoteMutation",
            "variables": json.dumps(variables),
            "doc_id": "9532619970198958",
        }
        data = _post(form)
        return ((data.get("data") or {}).get("xfb_rich_status_delete"))

    class NotesAPI:
        def check(self):
            return check()

        def create(self, text: str, privacy: str = "EVERYONE"):
            return create(text, privacy)

        def delete(self, noteID: str):
            return delete(noteID)

        def recreate(self, oldNoteID: str, newText: str):
            _ = delete(oldNoteID)
            return create(newText)

    api.notes = NotesAPI()
