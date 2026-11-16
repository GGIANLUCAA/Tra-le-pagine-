#!/usr/bin/env python3
"""Small fail-closed Browserless bridge: public pages only, no account login.

Requests originate from JSON files written through the connected GitHub app.
The Browserless API token is read ONLY from the Actions secret BROWSERLESS_TOKEN.
No browser visit is made without a valid request and the secret.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = frozenset(("example.com", "docs.browserless.io"))
REQUEST_ID = re.compile(r"^[a-z][a-z0-9-]{7,59}$")
FILE_PATH = re.compile(r"^requests/browserless/[a-z0-9][a-z0-9-]{7,59}\.json$")
API_URL = "https://production-lon.browserless.io/function"
MAX_ACTIONS = 4

FUNCTION_CODE = r"""
export default async ({page, context}) => {
  const allowed = new Set(["example.com", "docs.browserless.io"]);
  function ensureAllowed() {
    const u = new URL(page.url());
    if (u.protocol !== "https:" || !allowed.has(u.hostname)) {
      throw new Error("REDIRECT_OUTSIDE_PUBLIC_ALLOWLIST");
    }
  }
  await page.goto(context.url, {waitUntil: "domcontentloaded", timeout: 15000});
  ensureAllowed();
  for (const action of context.actions) {
    try {
      ensureAllowed();
      if (action.type === "click") {
        const el = await page.waitForSelector(action.selector, {timeout: 6500});
        if (!el) throw new Error("SELECTOR_NOT_FOUND");
        const isLink = await el.evaluate(n => n.tagName.toLowerCase() === "a");
        if (!isLink) throw new Error("ONLY_PUBLIC_LINK_CLICKS_ALLOWED");
        const href = await el.evaluate(n => n.href);
        const u = new URL(href);
        if (u.protocol !== "https:" || !allowed.has(u.hostname))
          throw new Error("LINK_OUTSIDE_PUBLIC_ALLOWLIST");
        await Promise.all([
          page.waitForNavigation({waitUntil: "domcontentloaded", timeout: 10000}).catch(() => null),
          el.click({timeout: 8500})
        ]);
      } else if (action.type === "type_public") {
        await page.type(action.selector, action.text, {delay: 8});
      } else {
        throw new Error("INVALID_ACTION");
      }
      ensureAllowed();
    } catch (err) {
      // Return only a fixed diagnostic code. Never disclose page content,
      // stack traces, URLs containing tokens, or raw error messages.
      const msg = String(err && err.message || "");
      const browserError = msg.includes("SELECTOR_NOT_FOUND") || msg.includes("waiting for selector")
        ? "SELECTOR_NOT_FOUND"
        : msg.includes("LINK_OUTSIDE_PUBLIC_ALLOWLIST") ? "LINK_OUTSIDE_PUBLIC_ALLOWLIST"
        : msg.includes("REDIRECT_OUTSIDE_PUBLIC_ALLOWLIST") ? "REDIRECT_OUTSIDE_PUBLIC_ALLOWLIST"
        : msg.includes("ONLY_PUBLIC_LINK_CLICKS_ALLOWED") ? "UNSAFE_ELEMENT_REFUSED"
        : /timeout|timed out/i.test(msg) ? "INTERACTION_TIMEOUT"
        : "OTHER_INTERACTION_ERROR";
      return {data: {browser_error: browserError}, type: "application/json"};
    }
  }
  const title = (await page.title()).slice(0, 240);
  const heading = await page.$eval("h1", n => (n.innerText || "").slice(0, 400)).catch(() => "");
  return {data: {title, heading, url: page.url(), action_count: context.actions.length}, type: "application/json"};
};"""


def validate_request(value):
    if not isinstance(value, dict) or set(value) != {"version", "request_id", "url", "actions"}:
        raise ValueError("Request must contain exactly version, request_id, url, actions")
    if value["version"] != 1 or not isinstance(value["request_id"], str) or not REQUEST_ID.fullmatch(value["request_id"]):
        raise ValueError("Invalid version or request ID")
    url = value["url"]
    if not isinstance(url, str) or len(url) > 320:
        raise ValueError("Invalid URL")
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.port not in (None, 443)
            or parts.username is not None or parts.password is not None or parts.query or parts.fragment):
        raise ValueError("Only approved public HTTPS URLs without query strings or credentials")
    actions = value["actions"]
    if not isinstance(actions, list) or len(actions) > MAX_ACTIONS:
        raise ValueError("Too many actions")
    for action in actions:
        if not isinstance(action, dict) or action.get("type") not in ("click", "type_public"):
            raise ValueError("Invalid action")
        if set(action) != ({"type", "selector"} if action["type"] == "click"
                           else {"type", "selector", "text"}):
            raise ValueError("Invalid action fields")
        selector = action["selector"]
        if not isinstance(selector, str) or not selector.strip() or len(selector) > 100:
            raise ValueError("Invalid CSS selector")
        if action["type"] == "type_public":
            content = action["text"]
            if not isinstance(content, str) or not 0 < len(content) <= 90:
                raise ValueError("Invalid text length")
            # Public GitHub requests must NEVER include emails, passwords, tokens or codes.
            if "@" in content or re.search(r"(secret|token|password|passw|api.?key|otp|codice|chiave)", content, re.I):
                raise ValueError("Potential private input refused")
    return value


def load_request(path):
    relative = str(path).replace("\\", "/")
    if not FILE_PATH.fullmatch(relative):
        raise ValueError("Request path outside dedicated queue")
    return validate_request(json.loads(Path(path).read_text(encoding="utf-8")))


def run_request(value, token):
    query = urllib.parse.urlencode({"token": token})
    payload = json.dumps({"code": FUNCTION_CODE, "context": {
        "url": value["url"], "actions": value["actions"]
    }}).encode("utf-8")
    req = urllib.request.Request(API_URL + "?" + query, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=55) as response:
            result = json.loads(response.read(100000).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Inspect only fixed error categories. Never log token-bearing URLs,
        # response body, or headers (they may contain API credentials).
        body = exc.read(8192).decode("utf-8", "replace").lower()
        categories = (
            ("selector_not_found", "selector_not_found"),
            ("link_outside_public_allowlist", "link_outside_allowlist"),
            ("redirect_outside_public_allowlist", "redirect_outside_allowlist"),
            ("only_public_link_clicks_allowed", "unsafe_click_refused"),
            ("navigation timeout", "navigation_timeout"),
            ("timeout exceeded", "timeout"),
            ("net::err_", "browser_network_error"),
        )
        error_code = next((label for marker, label in categories if marker in body), "other_provider_error")
        raise RuntimeError("Browserless HTTP status " + str(exc.code) + " (" + error_code + ")") from None
    except urllib.error.URLError:
        raise RuntimeError("Browserless connection unavailable") from None
    data = result.get("data") if isinstance(result, dict) else None
    if isinstance(data, dict) and "browser_error" in data:
        code = data["browser_error"]
        safe = ("SELECTOR_NOT_FOUND", "LINK_OUTSIDE_PUBLIC_ALLOWLIST",
                "REDIRECT_OUTSIDE_PUBLIC_ALLOWLIST", "UNSAFE_ELEMENT_REFUSED",
                "INTERACTION_TIMEOUT", "OTHER_INTERACTION_ERROR")
        raise RuntimeError("Browserless interaction: " + (code if code in safe else "UNKNOWN_ERROR"))
    if not isinstance(data, dict) or not isinstance(data.get("title"), str):
        raise RuntimeError("Unexpected Browserless response")
    final_url = urllib.parse.urlsplit(data.get("url", ""))
    if final_url.scheme != "https" or final_url.hostname not in ALLOWED_HOSTS:
        raise RuntimeError("Final browser URL outside allowlist")
    return {"request_id": value["request_id"], "status": "verified_public_page",
            "title": data["title"][:240], "heading": str(data.get("heading", ""))[:400],
            "final_host": final_url.hostname, "actions_executed": data.get("action_count")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    try:
        value = load_request(args.request)
        if args.dry_run:
            print(json.dumps({"status": "validated_no_browser_call", "request_id": value["request_id"]}))
            return 0
        token = os.environ.get("BROWSERLESS_TOKEN", "").strip()
        if not token:
            print(json.dumps({"status": "blocked_missing_github_secret", "secret": "BROWSERLESS_TOKEN"}))
            return 2
        print(json.dumps(run_request(value, token), ensure_ascii=False))
        return 0
    except (ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(json.dumps({"status": "failed_closed", "reason": str(exc)[:150]}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
