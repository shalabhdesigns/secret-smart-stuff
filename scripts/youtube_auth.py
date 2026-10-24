#!/usr/bin/env python3
"""One-time YouTube login on YOUR computer. Prints a refresh token to store as
the GitHub secret YT_REFRESH_TOKEN.

    python3 scripts/youtube_auth.py --client-id XXX --client-secret YYY

What it does:
1. Opens Google's consent page in your browser (sign in with the CHANNEL's account).
2. Google redirects back to http://127.0.0.1:8765 on your own machine.
3. The script swaps the code for tokens and prints the refresh token.

Nothing is sent anywhere except Google. Keep the token secret.
IMPORTANT: set your OAuth consent screen to "In production" first, otherwise
Google expires the refresh token after 7 days and the automation stops.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import secrets
import urllib.parse
import webbrowser

import requests

SCOPES = " ".join([
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
])
PORT = 8765
REDIRECT = f"http://127.0.0.1:{PORT}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    a = ap.parse_args()
    state = secrets.token_urlsafe(16)
    verifier = secrets.token_urlsafe(64)                       # PKCE, as Google recommends
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": a.client_id, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    got: dict = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Done. You can close this tab and return to the terminal.")

        def log_message(self, *args):
            pass

    print("Opening your browser. Sign in with the Google account that owns the channel...")
    webbrowser.open(url)
    print(f"If it did not open, paste this link into your browser:\n{url}\n")
    with http.server.HTTPServer(("127.0.0.1", PORT), H) as srv:
        while "code" not in got and "error" not in got:
            srv.handle_request()
    if got.get("state") != state or "code" not in got:
        raise SystemExit(f"Login failed: {got.get('error', 'state mismatch')}")
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "code": got["code"], "client_id": a.client_id, "client_secret": a.client_secret,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code", "code_verifier": verifier}, timeout=30)
    r.raise_for_status()
    tok = r.json()
    if "refresh_token" not in tok:
        raise SystemExit("Google did not return a refresh token. Remove the app's access at "
                         "myaccount.google.com/permissions and run this again.")
    print("\nSUCCESS. Add this as the GitHub secret YT_REFRESH_TOKEN:\n")
    print(tok["refresh_token"])


if __name__ == "__main__":
    main()
