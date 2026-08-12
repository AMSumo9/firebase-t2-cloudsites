#!/usr/bin/env python3
"""Keep three Firebase Hosting rollback versions before each shared deploy."""

import json
import os
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://firebasehosting.googleapis.com/v1beta1"
SITES = ("sites-e470-1", "sites-e470-2")
KEEP = 3


def request(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(
        f"{API}/{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"Firebase API {method} {path} failed: HTTP {error.code}: {detail}") from error


def list_all(path, field, token):
    rows = []
    page_token = None
    while True:
        query = {"pageSize": 1000}
        if page_token:
            query["pageToken"] = page_token
        page = request("GET", f"{path}?{urlencode(query)}", token)
        rows.extend(page.get(field, []))
        page_token = page.get("nextPageToken")
        if not page_token:
            return rows


def versions_to_delete(releases, versions):
    keep = {
        release["version"]["name"]
        for release in sorted(releases, key=lambda row: row.get("releaseTime", ""), reverse=True)[:KEEP]
        if release.get("version", {}).get("name")
    }
    return [
        version
        for version in versions
        if version.get("status") != "DELETED" and version.get("name") not in keep
    ]


def prune_site(site, token):
    channels = list_all(f"sites/{site}/channels", "channels", token)
    channel_ids = {channel["name"].rsplit("/", 1)[-1] for channel in channels}
    if channel_ids != {"live"}:
        raise RuntimeError(f"{site}: expected only live channel, found {sorted(channel_ids)}")

    request(
        "PATCH",
        f"sites/{site}/channels/live?updateMask=retainedReleaseCount",
        token,
        {"name": f"sites/{site}/channels/live", "retainedReleaseCount": KEEP},
    )
    releases = list_all(f"sites/{site}/channels/live/releases", "releases", token)
    versions = list_all(f"sites/{site}/versions", "versions", token)
    doomed = versions_to_delete(releases, versions)
    for version in doomed:
        request("DELETE", version["name"], token)
    removed_bytes = sum(int(version.get("versionBytes", 0)) for version in doomed)
    print(
        f"{site}: retention={KEEP}, releases={len(releases)}, versions={len(versions)}, "
        f"deleted={len(doomed)}, reported_bytes={removed_bytes}"
    )


def self_test():
    releases = [
        {"releaseTime": f"2026-01-0{day}T00:00:00Z", "version": {"name": f"sites/x/versions/{day}"}}
        for day in range(1, 6)
    ]
    versions = [{"name": f"sites/x/versions/{day}", "status": "FINALIZED"} for day in range(1, 6)]
    assert [row["name"] for row in versions_to_delete(releases, versions)] == [
        "sites/x/versions/1",
        "sites/x/versions/2",
    ]
    print("self-test passed")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        access_token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN")
        if not access_token:
            raise SystemExit("GOOGLE_OAUTH_ACCESS_TOKEN is required")
        for site_id in SITES:
            prune_site(site_id, access_token)
