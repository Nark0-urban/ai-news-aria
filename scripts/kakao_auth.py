# -*- coding: utf-8 -*-
"""Kakao OAuth token setup for AI News Aria.

Run this once on a local PC:
    python scripts/kakao_auth.py

It opens a temporary localhost callback server, receives the authorization code,
and saves config/kakao_token.json.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def after_seconds_iso(seconds: int) -> str:
    return (datetime.now(timezone.utc).astimezone() + timedelta(seconds=seconds)).isoformat()


def load_config(config_path: str) -> dict[str, Any]:
    path = PROJECT_ROOT / config_path
    if not path.exists():
        raise SystemExit(
            f"Missing config file: {path}\n"
            "Create it from config/config.example.json and set kakao.rest_api_key."
        )
    return json.loads(path.read_text(encoding="utf-8-sig"))


def token_path(config: dict[str, Any]) -> Path:
    return PROJECT_ROOT / config["kakao"]["token_file"]


def post_form(url: str, data: dict[str, str]) -> dict[str, Any]:
    encoded = urlencode(data).encode("utf-8")
    request = Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Kakao token request failed: HTTP {exc.code}\n{body}") from exc
    except URLError as exc:
        raise SystemExit(f"Kakao token request failed: {exc}") from exc


def save_token(path: Path, token: dict[str, Any]) -> None:
    token["obtained_at"] = now_iso()
    if token.get("expires_in"):
        token["expires_at"] = after_seconds_iso(int(token["expires_in"]))
    if token.get("refresh_token_expires_in"):
        token["refresh_token_expires_at"] = after_seconds_iso(int(token["refresh_token_expires_in"]))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(token, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved Kakao token: {path}")


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


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    error: str | None = None

    def do_GET(self) -> None:  # noqa: N802 - stdlib hook name
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        OAuthCallbackHandler.code = params.get("code", [None])[0]
        OAuthCallbackHandler.error = params.get("error_description", params.get("error", [None]))[0]

        if OAuthCallbackHandler.code:
            message = "Kakao OAuth complete. You can close this browser tab."
            status = 200
        else:
            message = f"Kakao OAuth failed: {OAuthCallbackHandler.error or 'missing code'}"
            status = 400

        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_authorization_code_flow(config: dict[str, Any]) -> None:
    kakao = config["kakao"]
    redirect_uri = kakao["redirect_uri"]
    parsed = urlparse(redirect_uri)
    if parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise SystemExit("This local OAuth helper only supports localhost redirect_uri.")

    port = parsed.port or 80
    path = parsed.path or "/"
    server = HTTPServer((parsed.hostname or "localhost", port), OAuthCallbackHandler)

    query = urlencode(
        {
            "response_type": "code",
            "client_id": kakao["rest_api_key"],
            "redirect_uri": redirect_uri,
            "scope": "talk_message",
        }
    )
    auth_url = f"https://kauth.kakao.com/oauth/authorize?{query}"

    print("")
    print("Open this URL in your browser, approve Kakao login, then keep this terminal open:")
    print(auth_url)
    print("")
    print(f"Waiting for callback on http://{parsed.hostname}:{port}{path}")

    server.handle_request()
    server.server_close()

    if not OAuthCallbackHandler.code:
        raise SystemExit(f"No authorization code received: {OAuthCallbackHandler.error}")

    body = make_token_body(
        config,
        "authorization_code",
        redirect_uri=redirect_uri,
        code=OAuthCallbackHandler.code,
    )
    token = post_form("https://kauth.kakao.com/oauth/token", body)
    save_token(token_path(config), token)


def refresh_token(config: dict[str, Any]) -> None:
    path = token_path(config)
    if not path.exists():
        raise SystemExit(f"No token file found: {path}")

    saved = json.loads(path.read_text(encoding="utf-8"))
    refresh = saved.get("refresh_token")
    if not refresh:
        raise SystemExit("Token file has no refresh_token. Run without --refresh.")

    body = make_token_body(config, "refresh_token", refresh_token=refresh)
    token = post_form("https://kauth.kakao.com/oauth/token", body)
    if not token.get("refresh_token"):
        token["refresh_token"] = refresh
    save_token(path, token)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    if config["kakao"]["rest_api_key"] == "YOUR_KAKAO_REST_API_KEY":
        raise SystemExit("Set kakao.rest_api_key in config/config.json first.")

    if args.refresh:
        refresh_token(config)
    else:
        run_authorization_code_flow(config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCanceled.")
        sys.exit(130)
