#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create the exoticalloycn.com A records through the DNSPod API.

Why this exists: the Lighthouse MCP connector's create_DNS_record tool is
broken -- it returns "The parameter `domainIds` is not recognized." for every
valid call, on every domain. This script is the working alternative and needs
nothing but a DNSPod login token.

Token (one of):
  env DNSPOD_TOKEN        "<login_token_id>,<login_token_key>"
  env DNSPOD_TOKEN_FILE   path to a file whose first line is the same string

Modes:
  probe   TLS reachability check, no token required
  check   read-only: list every record the API returns for the domain
  apply   create the missing @ / www A records (idempotent: skips existing)

Example:
  DNSPOD_TOKEN=123456,abcdef python dnspod-set-a-records.py apply
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DOMAIN = "exoticalloycn.com"
TARGET_IP = "122.51.221.165"
RECORDS = (("@", "122.51.221.165"), ("www", "122.51.221.165"))
TTL = "600"
UA = "exoticalloycn-deploy/1.0 (ops@exoticalloycn.com)"
API = "https://dnsapi.cn/"


def die(msg, code=1):
    sys.stderr.write(msg + "\n")
    raise SystemExit(code)


def load_token():
    raw = os.environ.get("DNSPOD_TOKEN", "").strip()
    if not raw:
        path = os.environ.get("DNSPOD_TOKEN_FILE", "").strip()
        if path and os.path.exists(path):
            raw = open(path, encoding="utf-8").readline().strip()
    if not raw:
        die("TOKEN_MISSING: set DNSPOD_TOKEN='<id>,<key>' "
            "(or DNSPOD_TOKEN_FILE=<path>).", 3)
    if "," not in raw:
        die("TOKEN_MALFORMED: expected '<id>,<key>'.", 3)
    return raw


def call(path, data, token):
    payload = dict(data)
    payload["login_token"] = token
    payload["format"] = "json"
    body = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        API + path,
        data=body,
        headers={"User-Agent": UA,
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        die("HTTP_FAIL %s: status=%s" % (path, exc.code), 4)
    except Exception as exc:  # noqa: BLE001
        die("HTTP_FAIL %s: %s" % (path, exc), 4)


def status_of(payload):
    st = payload.get("status") or {}
    return str(st.get("code", "")), st.get("message", "")


def list_records(token):
    out = call("Record.List", {"domain": DOMAIN}, token)
    code, msg = status_of(out)
    if code != "1":
        die("RECORD_LIST_FAIL code=%s msg=%s" % (code, msg), 5)
    return out.get("records") or []


def ensure(name, value, token):
    hit = [r for r in list_records(token)
           if r.get("name") == name and r.get("type") == "A"]
    if hit:
        for r in hit:
            print("EXISTS  %-4s A %-18s id=%s line=%s" %
                  (name, r.get("value"), r.get("id"), r.get("line")))
        return False
    out = call("Record.Create", {
        "domain": DOMAIN,
        "sub_domain": name,
        "record_type": "A",
        "record_line_id": "0",  # 0 == default line, keeps the payload ASCII
        "value": value,
        "ttl": TTL,
    }, token)
    code, msg = status_of(out)
    if code != "1":
        die("CREATE_FAIL sub=%s code=%s msg=%s" % (name, code, msg), 6)
    print("CREATED %-4s A %-18s id=%s" %
          (name, value, (out.get("record") or {}).get("id")))
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"

    if mode == "probe":
        req = urllib.request.Request(API, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                print("NET_OK status=%s" % resp.status)
        except urllib.error.HTTPError as exc:
            print("NET_OK status=%s" % exc.code)
        except Exception as exc:  # noqa: BLE001
            die("NET_FAIL %s" % exc, 7)
        return

    if mode == "check":
        token = load_token()
        recs = list_records(token)
        print("domain=%s records=%d" % (DOMAIN, len(recs)))
        for r in recs:
            print("  %-8s %-6s %-18s line=%-8s ttl=%-5s status=%s" %
                  (r.get("name"), r.get("type"), r.get("value"),
                   r.get("line"), r.get("ttl"), r.get("status")))
        return

    if mode == "apply":
        token = load_token()
        changed = 0
        for name, value in RECORDS:
            if ensure(name, value, token):
                changed += 1
            time.sleep(1)
        print("APPLY_DONE created=%d skipped=%d" %
              (changed, len(RECORDS) - changed))
        print("then on the server: bash /opt/tongjun-overseas/finish-le.sh")
        return

    die("usage: dnspod-set-a-records.py [probe|check|apply]", 2)


if __name__ == "__main__":
    main()
