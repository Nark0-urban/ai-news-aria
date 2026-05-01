# -*- coding: utf-8 -*-
"""Send Kakao Talk memo messages for AI News Aria."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def now_local() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def after_seconds_iso(seconds: int) -> str:
    return (now_local() + timedelta(seconds=seconds)).isoformat()


def post_form(url: str, data: dict[str, str], headers: dict[str, str] | None = None) -> dict[str, Any]:
    encoded = urlencode(data).encode("utf-8")
    request = Request(
        url,
        data=encoded,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            **(headers or {}),
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Kakao request failed: HTTP {exc.code}\n{body}") from exc
    except URLError as exc:
        raise SystemExit(f"Kakao request failed: {exc}") from exc


def make_token_body(config: dict[str, Any], grant_type: str, **kwargs: str) -> dict[str, str]:
    kakao = config["kakao"]
    body: dict[str, str] = {
        "grant_type": grant_type,
        "client_id": kakao["rest_api_key"],
        **kwargs,
    }
    client_secret = kakao.get("client_secret")
    if client_secret:
        body["client_secret"] = client_secret
    return body


def token_needs_refresh(token: dict[str, Any]) -> bool:
    expires_at = token.get("expires_at")
    if not expires_at:
        return False
    try:
        expiry = datetime.fromisoformat(expires_at)
    except ValueError:
        return False
    return expiry <= now_local() + timedelta(minutes=5)


def load_and_refresh_token(config: dict[str, Any]) -> dict[str, Any]:
    path = PROJECT_ROOT / config["kakao"]["token_file"]
    if not path.exists():
        raise SystemExit(f"Missing Kakao token file: {path}\nRun scripts/kakao_auth.py first.")

    token = load_json(path)
    if not token_needs_refresh(token):
        return token

    refresh = token.get("refresh_token")
    if not refresh:
        raise SystemExit("Access token expired and no refresh_token exists. Run scripts/kakao_auth.py again.")

    body = make_token_body(config, "refresh_token", refresh_token=refresh)
    new_token = post_form("https://kauth.kakao.com/oauth/token", body)
    new_token["obtained_at"] = now_local().isoformat()
    if new_token.get("expires_in"):
        new_token["expires_at"] = after_seconds_iso(int(new_token["expires_in"]))
    if not new_token.get("refresh_token"):
        new_token["refresh_token"] = refresh

    save_json(path, new_token)
    return new_token


def build_template(args: argparse.Namespace) -> dict[str, Any]:
    if args.image_url:
        description = args.description or args.text
        if args.include_url and args.link_url and args.link_url not in description:
            description = f"{description}\n{args.link_url}"
        return {
            "object_type": "feed",
            "content": {
                "title": args.title,
                "description": description,
                "image_url": args.image_url,
                "link": {
                    "web_url": args.link_url,
                    "mobile_web_url": args.link_url,
                },
            },
            "buttons": [
                {
                    "title": args.button_title,
                    "link": {
                        "web_url": args.link_url,
                        "mobile_web_url": args.link_url,
                    },
                }
            ],
        }

    return {
        "object_type": "text",
        "text": args.text,
        "link": {
            "web_url": args.link_url,
            "mobile_web_url": args.link_url,
        },
        "button_title": args.button_title,
    }


def build_text_template(text: str, link_url: str, button_title: str) -> dict[str, Any]:
    return {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": link_url,
            "mobile_web_url": link_url,
        },
        "button_title": button_title,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--text", default="아리아 카드뉴스 테스트입니다.")
    parser.add_argument("--title", default="AI 뉴스 아리아")
    parser.add_argument("--description", default="")
    parser.add_argument("--image-url", default="")
    parser.add_argument("--link-url", default="https://example.com")
    parser.add_argument("--button-title", default="카드뉴스 확인하기")
    parser.add_argument("--include-url", action="store_true")
    parser.add_argument("--fallback-text", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_json(PROJECT_ROOT / args.config)
    token = load_and_refresh_token(config)
    template_json = json.dumps(build_template(args), ensure_ascii=False, separators=(",", ":"))

    if args.dry_run:
        print(template_json)
        return

    response = post_form(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        {"template_object": template_json},
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))

    if args.fallback_text and args.image_url:
        fallback = build_text_template(
            f"{args.title}\n전체 카드뉴스 링크:\n{args.link_url}",
            args.link_url,
            args.button_title,
        )
        fallback_json = json.dumps(fallback, ensure_ascii=False, separators=(",", ":"))
        fallback_response = post_form(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            {"template_object": fallback_json},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        print(json.dumps(fallback_response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
