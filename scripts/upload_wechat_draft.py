from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vx_daily.rendering import write_json  # noqa: E402
from vx_daily.wechat_api import (  # noqa: E402
    WeChatApiError,
    add_draft,
    build_article_payload,
    get_access_token,
    upload_permanent_image,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a generated article to WeChat draft box.")
    parser.add_argument("--article-dir", required=True, help="Path to a generated drafts/YYYY-MM-DD/... folder.")
    parser.add_argument("--access-token", default=os.environ.get("WECHAT_ACCESS_TOKEN"))
    parser.add_argument("--author", default="科技互联网博士")
    parser.add_argument("--cover", default="cover.png")
    parser.add_argument("--dry-run", action="store_true", help="Write payload JSON without calling WeChat APIs.")
    return parser.parse_args()


def _read_metadata(article_dir: Path) -> dict:
    metadata_path = article_dir / "metadata.json"
    if not metadata_path.exists():
        raise WeChatApiError(f"metadata.json not found: {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8-sig"))


def _write_metadata(article_dir: Path, metadata: dict) -> None:
    write_json(article_dir / "metadata.json", metadata)


def main() -> int:
    args = parse_args()
    article_dir = Path(args.article_dir).resolve()
    html_path = article_dir / "article.html"
    cover_path = article_dir / args.cover

    if not html_path.exists():
        raise WeChatApiError(f"article.html not found: {html_path}")

    metadata = _read_metadata(article_dir)
    draft = metadata["draft"]
    score = metadata["attempts"][-1]["score"]
    if not score.get("passed"):
        raise WeChatApiError("Refusing to upload a draft that did not pass scoring.")

    html_content = html_path.read_text(encoding="utf-8")
    digest = str(draft.get("summary", ""))[:128]

    if args.dry_run:
        payload = build_article_payload(
            title=draft["title"],
            html_content=html_content,
            thumb_media_id="DRY_RUN_THUMB_MEDIA_ID",
            author=args.author,
            digest=digest,
        )
        write_json(article_dir / "wechat_draft_payload.dry_run.json", {"articles": [payload]})
        metadata["wechat_draft"] = {
            "status": "dry_run_ready",
            "payload_file": "wechat_draft_payload.dry_run.json",
        }
        _write_metadata(article_dir, metadata)
        print(f"Dry-run payload written: {article_dir / 'wechat_draft_payload.dry_run.json'}")
        return 0

    access_token = args.access_token or get_access_token()
    cover_response = upload_permanent_image(access_token, cover_path)
    thumb_media_id = cover_response["media_id"]
    payload = build_article_payload(
        title=draft["title"],
        html_content=html_content,
        thumb_media_id=thumb_media_id,
        author=args.author,
        digest=digest,
    )
    draft_response = add_draft(access_token, payload)

    private_dir = article_dir / "wechat_private"
    private_dir.mkdir(exist_ok=True)
    write_json(private_dir / "wechat_cover_response.json", cover_response)
    write_json(private_dir / "wechat_draft_response.json", draft_response)
    metadata["wechat_draft"] = {
        "status": "uploaded",
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "private_response_dir": "wechat_private",
    }
    _write_metadata(article_dir, metadata)
    print(f"WeChat draft uploaded: {draft_response.get('media_id')}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WeChatApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
