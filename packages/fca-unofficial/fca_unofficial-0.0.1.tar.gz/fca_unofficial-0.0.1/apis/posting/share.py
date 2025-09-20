from typing import Any, Dict
import json


def attach_share(api: Any) -> None:
    """Attach getPostPreview as api.getPostPreview(postID)."""

    def getPostPreview(postID: str) -> Dict[str, Any]:
        if not postID:
            raise ValueError("A postID is required to generate a preview.")
        variables = {
            "shareable_id": str(postID),
            "scale": 3,
        }
        form = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CometXMAProxyShareablePreviewQuery",
            "variables": json.dumps(variables),
            "doc_id": "28939050904374351",
        }
        status, res = api.defaultFuncs.post("https://www.facebook.com/api/graphql/", api.ctx.get("jar"), form, api.ctx)
        if status < 200 or status >= 300:
            raise RuntimeError(f"getPostPreview failed with status {status}")
        data = json.loads((res.get("body") or "").replace("for (;;);", ""))
        if isinstance(data, dict) and data.get("errors"):
            # raise the first error
            err = data["errors"][0]
            raise RuntimeError(err.get("message") or str(err))
        preview = (((data.get("data") or {}).get("xma_preview_data")))
        if not preview:
            raise RuntimeError("Could not generate a preview for this post.")
        return {
            "postID": preview.get("post_id"),
            "header": preview.get("header_title"),
            "subtitle": preview.get("subtitle_text"),
            "title": preview.get("title_text"),
            "previewImage": preview.get("preview_url"),
            "favicon": preview.get("favicon_url"),
            "headerImage": preview.get("header_image_url"),
        }

    api.getPostPreview = getPostPreview
