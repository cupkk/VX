from __future__ import annotations

import json
import mimetypes
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

WECHAT_API_BASE = "https://api.weixin.qq.com"


class WeChatApiError(RuntimeError):
    pass


def _json_request(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("errcode") not in (None, 0):
        raise WeChatApiError(f"WeChat API error {result.get('errcode')}: {result.get('errmsg')}")
    return result


def _multipart_request(url: str, field_name: str, file_path: Path) -> dict[str, Any]:
    boundary = f"----vx-daily-{int(time.time() * 1000)}"
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    request = urllib.request.Request(
        url,
        data=header + file_bytes + footer,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("errcode") not in (None, 0):
        raise WeChatApiError(f"WeChat API error {result.get('errcode')}: {result.get('errmsg')}")
    return result


def get_access_token(app_id: str | None = None, app_secret: str | None = None) -> str:
    app_id = app_id or os.environ.get("WECHAT_APP_ID")
    app_secret = app_secret or os.environ.get("WECHAT_APP_SECRET")
    if not app_id or not app_secret:
        raise WeChatApiError("Missing WECHAT_APP_ID or WECHAT_APP_SECRET environment variable.")

    url = f"{WECHAT_API_BASE}/cgi-bin/stable_token"
    result = _json_request(
        url,
        {
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret,
            "force_refresh": False,
        },
    )
    access_token = result.get("access_token")
    if not access_token:
        raise WeChatApiError("WeChat did not return access_token.")
    return str(access_token)


def upload_permanent_image(access_token: str, image_path: Path) -> dict[str, Any]:
    if not image_path.exists():
        raise WeChatApiError(f"Cover image not found: {image_path}")
    query = urllib.parse.urlencode({"access_token": access_token, "type": "image"})
    return _multipart_request(f"{WECHAT_API_BASE}/cgi-bin/material/add_material?{query}", "media", image_path)


def upload_article_image(access_token: str, image_path: Path) -> dict[str, Any]:
    if not image_path.exists():
        raise WeChatApiError(f"Article image not found: {image_path}")
    query = urllib.parse.urlencode({"access_token": access_token})
    return _multipart_request(f"{WECHAT_API_BASE}/cgi-bin/media/uploadimg?{query}", "media", image_path)


def add_draft(access_token: str, article: dict[str, Any]) -> dict[str, Any]:
    query = urllib.parse.urlencode({"access_token": access_token})
    return _json_request(f"{WECHAT_API_BASE}/cgi-bin/draft/add?{query}", {"articles": [article]})


def build_article_payload(
    title: str,
    html_content: str,
    thumb_media_id: str,
    author: str,
    digest: str,
) -> dict[str, Any]:
    if len(title) > 32:
        raise WeChatApiError("WeChat draft title must not exceed 32 characters.")
    if len(author) > 16:
        raise WeChatApiError("WeChat author must not exceed 16 characters.")
    if len(digest) > 128:
        digest = digest[:128]
    if len(html_content) >= 20000 or len(html_content.encode("utf-8")) >= 1024 * 1024:
        raise WeChatApiError("WeChat draft HTML is too large.")

    return {
        "article_type": "news",
        "title": title,
        "author": author,
        "digest": digest,
        "content": html_content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
