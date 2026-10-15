#!/usr/bin/env python3
"""Revisa cada repo de payloads.json i actualitza l'entrada si hi ha una release nova (no prerelease)."""
import json
import os
import re
import sys
import urllib.request

PAYLOADS_FILE = os.path.join(os.path.dirname(__file__), "..", "payloads.json")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


def gh_get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def latest_release(repo):
    releases = gh_get(f"https://api.github.com/repos/{repo}/releases")
    for r in releases:
        if not r.get("prerelease") and not r.get("draft"):
            return r
    return None


def pick_asset(release, entry):
    assets = release.get("assets", [])
    pattern = entry.get("asset_pattern")
    if pattern:
        regex = re.compile(pattern)
        for a in assets:
            if regex.search(a["name"]):
                return a
        return None
    for a in assets:
        if a["name"] == entry["filename"]:
            return a
    return None


def main():
    with open(PAYLOADS_FILE, "r", encoding="utf-8") as f:
        payloads = json.load(f)

    changed = False

    for entry in payloads:
        repo = entry.get("repo")
        if not repo:
            continue
        try:
            release = latest_release(repo)
        except Exception as e:
            print(f"[WARN] {entry['name']}: no s'ha pogut consultar {repo}: {e}", file=sys.stderr)
            continue
        if not release:
            print(f"[WARN] {entry['name']}: cap release estable trobada a {repo}", file=sys.stderr)
            continue

        asset = pick_asset(release, entry)
        if not asset:
            print(f"[WARN] {entry['name']}: no s'ha trobat l'asset esperat a {release['tag_name']}", file=sys.stderr)
            continue

        digest = asset.get("digest", "")
        checksum = digest.split(":", 1)[1] if digest.startswith("sha256:") else digest

        if checksum and checksum != entry.get("checksum"):
            print(f"[UPDATE] {entry['name']}: {entry['version']} -> {release['tag_name']}")
            entry["filename"] = asset["name"]
            entry["url"] = asset["browser_download_url"]
            entry["source_direct"] = asset["browser_download_url"]
            entry["version"] = release["tag_name"] if release["tag_name"].startswith("v") else f"v{release['tag_name']}"
            entry["last_update"] = release["published_at"][:10]
            entry["checksum"] = checksum
            changed = True
        else:
            print(f"[OK] {entry['name']}: ja al dia ({entry['version']})")

    if changed:
        with open(PAYLOADS_FILE, "w", encoding="utf-8") as f:
            json.dump(payloads, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("payloads.json actualitzat.")
    else:
        print("Cap canvi.")

    # Per GitHub Actions: exposa si hi ha hagut canvis
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")


if __name__ == "__main__":
    main()
