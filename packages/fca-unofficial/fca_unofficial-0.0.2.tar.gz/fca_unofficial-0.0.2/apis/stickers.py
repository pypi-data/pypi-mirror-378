from typing import Any, Dict, List
import json


def attach_stickers(api: Any) -> None:
    def _post(form: Dict[str, Any]):
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Stickers GraphQL failed with status {status}")
        try:
            data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        except Exception:
            data = {}
        if isinstance(data, dict) and data.get("errors"):
            raise RuntimeError(data["errors"][0].get("message", "GraphQL error"))
        return data

    def search(query: str) -> List[Dict[str, Any]]:
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CometStickerPickerSearchResultsRootQuery",
            "variables": json.dumps({
                "scale": 3,
                "search_query": query,
                "sticker_height": 128,
                "sticker_width": 128,
                "stickerInterface": "MESSAGES",
            }),
            "doc_id": "24004987559125954",
        }
        data = _post(form)
        edges = (((data.get("data") or {}).get("sticker_search") or {}).get("sticker_results") or {}).get("edges") or []
        out = []
        for e in edges:
            n = e.get("node") or {}
            out.append({
                "type": "sticker",
                "ID": n.get("id"),
                "url": (n.get("image") or {}).get("uri"),
                "animatedUrl": (n.get("animated_image") or {}).get("uri"),
                "packID": (n.get("pack") or {}).get("id"),
                "label": n.get("label") or n.get("accessibility_label"),
                "stickerID": n.get("id"),
            })
        return out

    def listPacks() -> List[Dict[str, Any]]:
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CometStickerPickerCardQuery",
            "variables": json.dumps({"scale": 3, "stickerInterface": "MESSAGES"}),
            "doc_id": "10095807770482952",
        }
        data = _post(form)
        edges = (((((data.get("data") or {}).get("picker_plugins") or {}).get("sticker_picker") or {}).get("sticker_store") or {}).get("tray_packs") or {}).get("edges") or []
        out = []
        for e in edges:
            n = e.get("node") or {}
            out.append({
                "id": n.get("id"),
                "name": n.get("name"),
                "thumbnail": ((n.get("thumbnail_image") or {}).get("uri")),
            })
        return out

    def getStorePacks() -> List[Dict[str, Any]]:
        all_packs: List[Dict[str, Any]] = []
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CometStickersStoreDialogQuery",
            "variables": json.dumps({}),
            "doc_id": "29237828849196584",
        }
        data = _post(form)
        pack_data = (((data.get("data") or {}).get("viewer") or {}).get("sticker_store") or {}).get("available_packs") or {}
        edges = pack_data.get("edges") or []
        page_info = pack_data.get("page_info") or {}
        store_id = (((data.get("data") or {}).get("viewer") or {}).get("sticker_store") or {}).get("id")
        all_packs.extend([{ "id": (n:=e.get("node") or {}).get("id"), "name": n.get("name"), "thumbnail": ((n.get("thumbnail_image") or {}).get("uri")) } for e in edges])
        while page_info.get("has_next_page"):
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "CometStickersStorePackListPaginationQuery",
                "variables": json.dumps({
                    "count": 20,
                    "cursor": page_info.get("end_cursor"),
                    "id": store_id,
                }),
                "doc_id": "9898634630218439",
            }
            data = _post(form)
            pack_data = (((data.get("data") or {}).get("viewer") or {}).get("sticker_store") or {}).get("available_packs") or {}
            edges = pack_data.get("edges") or []
            page_info = pack_data.get("page_info") or {}
            all_packs.extend([{ "id": (n:=e.get("node") or {}).get("id"), "name": n.get("name"), "thumbnail": ((n.get("thumbnail_image") or {}).get("uri")) } for e in edges])
        return all_packs

    def listAllPacks() -> List[Dict[str, Any]]:
        seen = {}
        for p in listPacks() + getStorePacks():
            seen[p["id"]] = p
        return list(seen.values())

    def getStickersInPack(packID: str) -> List[Dict[str, Any]]:
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CometStickerPickerPackContentRootQuery",
            "variables": json.dumps({"packID": packID, "stickerWidth": 128, "stickerHeight": 128, "scale": 3}),
            "doc_id": "23982341384707469",
        }
        data = _post(form)
        edges = ((((data.get("data") or {}).get("sticker_pack") or {}).get("stickers") or {}).get("edges")) or []
        out = []
        for e in edges:
            n = e.get("node") or {}
            out.append({
                "type": "sticker",
                "ID": n.get("id"),
                "url": (n.get("image") or {}).get("uri"),
                "animatedUrl": (n.get("animated_image") or {}).get("uri"),
                "packID": (n.get("pack") or {}).get("id"),
                "label": n.get("label") or n.get("accessibility_label"),
                "stickerID": n.get("id"),
            })
        return out

    def getAiStickers(limit: int = 10) -> List[Dict[str, Any]]:
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CometStickerPickerStickerGeneratedCardQuery",
            "variables": json.dumps({"limit": limit}),
            "doc_id": "24151467751156443",
        }
        data = _post(form)
        nodes = (((data.get("data") or {}).get("xfb_trending_generated_ai_stickers") or {}).get("nodes")) or []
        out = []
        for n in nodes:
            out.append({"type": "sticker", "ID": n.get("id"), "url": n.get("url"), "label": n.get("label"), "stickerID": n.get("id")})
        return out

    class StickersAPI:
        def search(self, query: str):
            return search(query)

        def listPacks(self):
            return listPacks()

        def getStorePacks(self):
            return getStorePacks()

        def listAllPacks(self):
            return listAllPacks()

        def addPack(self, packID: str):
            form = {
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "CometStickersStorePackMutationAddMutation",
                "variables": json.dumps({"input": {"pack_id": packID, "actor_id": api.ctx.get("userID"), "client_mutation_id": "1"}}),
                "doc_id": "9877489362345320",
            }
            data = _post(form)
            return (((data.get("data") or {}).get("sticker_pack_add") or {}).get("sticker_pack"))

        def getStickersInPack(self, packID: str):
            return getStickersInPack(packID)

        def getAiStickers(self, limit: int = 10):
            return getAiStickers(limit)

    api.stickers = StickersAPI()
