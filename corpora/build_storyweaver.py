"""Build <lang>-storyweaver from StoryWeaver's levelled children's books (https://storyweaver.org.in).

StoryWeaver publishes stories under CC BY 4.0 and grades each one in four
levels: 1 (beginning to read, easy words and repetition), 2 (learning to read,
simple concepts), 3 (reading independently, longer sentences), 4 (reading
proficiently, longer and more nuanced stories). The level is assigned by the
publisher; it is ordinal and carries no ages.

A story enters only if its own attribution page says "This story ... Released
under CC BY 4.0 license"; its attribution is kept with the text. Many Spanish
stories are translations, marked in `translated`. Reading a story needs a free
account; the credentials file holds `email=` and `password=` lines.

Run: python corpora/build_storyweaver.py es CREDENTIALS [cache dir]
"""
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
SITE = "https://storyweaver.org.in"
LANGUAGES = {"es": "Spanish", "en": "English"}
UA = {"User-Agent": "anagnosis-research (https://github.com/gia-uh/anagnosis)"}
LICENSE = re.compile(r"This story: .*?Released under (CC BY 4\.0) license\.", re.S)


class Client:
    def __init__(self, credentials: Path):
        creds = dict(line.split("=", 1) for line in credentials.read_text().split())
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        body = urllib.parse.urlencode({"user[email]": creds["email"], "user[password]": creds["password"]}).encode()
        self.opener.open(urllib.request.Request(f"{SITE}/node/api/v1/users/sign_in", body, UA), timeout=60)

    def get(self, path: str) -> dict:
        """The site rate-limits with 429 and no Retry-After: pace requests and back off when refused."""
        wait = 60
        while True:
            time.sleep(5)
            try:
                with self.opener.open(urllib.request.Request(SITE + path, headers=UA), timeout=60) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code != 429 or wait > 1800:
                    raise
                print(f"429 on {path}; waiting {wait}s", file=sys.stderr, flush=True)
                time.sleep(wait)
                wait *= 2


def plain(fragment: str) -> str:
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", "", fragment, flags=re.S)
    fragment = re.sub(r"</(p|div|h\d|li)>|<br\s*/?>", "\n", fragment)
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment)).replace("﻿", "").replace("\xad", "")


def story(read: dict) -> tuple[str, str | None]:
    """The story text, paragraph per line block, and its attribution sentence if CC BY 4.0."""
    paras, attribution = [], None
    for page in read["pages"]:
        text = plain(page["html"])
        if page.get("pageType") == "StoryPage":
            text = re.sub(r"^\s*\d+/\d+\s*", "", text)  # page counter
            paras += [" ".join(p.split()) for p in text.split("\n") if p.strip() and not re.fullmatch(r"\s*\d+/\d+\s*", p)]
        elif page.get("pageType") == "BackInnerCoverPage" and attribution is None:
            m = LICENSE.search(" ".join(text.split()))
            attribution = m.group(0) if m else None
    return "\n\n".join(paras), attribution


def main(lang: str, credentials: Path, cache: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    client = Client(credentials)
    books, page = [], 1
    while True:
        res = client.get(f"/api/v1/books-search?languages[]={LANGUAGES[lang]}&per_page=100&page={page}")
        books += res["data"]
        if page >= res["metadata"]["totalPages"]:
            break
        page += 1
    records, skipped = [], {"license": 0, "empty": 0, "server error": 0}
    for b in books:
        path = cache / f"{b['slug']}.json"
        if not path.exists():
            try:
                path.write_text(json.dumps(client.get(f"/api/v1/stories/{b['slug']}/read")["data"]))
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    raise
                skipped["server error"] += 1
                continue
        read = json.loads(path.read_text())
        text, attribution = story(read)
        if attribution is None:
            skipped["license"] += 1
        elif len(text.split()) < 20:
            skipped["empty"] += 1
        else:
            records.append({"id": b["slug"], "text": text, "label": f"level{read['level']}", "group": b["slug"],
                            "translated": bool(read.get("isTranslation")), "attribution": attribution})
    out = HERE / f"{lang}-storyweaver"
    with open(out / "texts.jsonl", "w") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    print(f"{out.name}: {len(records)} of {len(books)} stories; skipped {skipped}")


if __name__ == "__main__":
    lang, creds = sys.argv[1], Path(sys.argv[2])
    main(lang, creds, Path(sys.argv[3]) if len(sys.argv) > 3 else Path.home() / ".cache" / "anagnosis" / f"storyweaver-{lang}")
