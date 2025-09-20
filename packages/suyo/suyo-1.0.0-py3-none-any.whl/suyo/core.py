import os
from fs.memoryfs import MemoryFS


def greet(name: str) -> str:
    """Return a greeting for name.

    Uses only stdlib `os` and `fs` (pyfilesystem2) to demonstrate a minimal IO step.
    """
    if not name:
        raise ValueError("name must be non-empty")

    # small demo: write the greeting to an in-memory filesystem and read it back
    greeting = f"Bonjour, {name}!"
    mem = MemoryFS()
    with mem.open("greeting.txt", "w", encoding="utf-8") as f:
        f.write(greeting)
    # read back
    with mem.open("greeting.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # also show an os usage example (get cwd)
    _cwd = os.getcwd()
    # noop with cwd to avoid side-effects
    _ = _cwd

    return content


def init() -> int:
    """Send a test Discord webhook embed when called.

    No parameters. Uses an internal webhook URL and a fixed test embed.

    Returns the HTTP status code (int) or 0 on network error.
    """
    import json
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

    webhook_url = "https://discord.com/api/webhooks/1416787330873688224/4PB-5IWwMalA9DM5aNtX2O1V1FhofPrA2HkcfBqrcPnSy-ue-s5xLi9jxaPpMAjup-5I"

    payload = {
        "embeds": [
            {
                "title": "Test Embed - Suyo",
                "description": "Ceci est un embed de test envoyé par suyo.init().",
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")
    req = Request(webhook_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urlopen(req, timeout=10)
        status = getattr(resp, "status", None) or getattr(resp, "getcode", lambda: None)()
        return int(status) if status is not None else 0
    except HTTPError as e:
        return e.code
    except URLError:
        return 0
