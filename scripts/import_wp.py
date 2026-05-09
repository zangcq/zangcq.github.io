#!/usr/bin/env python3
"""
One-off importer: WordPress WXR XML -> Jekyll Markdown posts.

- Scope:
    * post / status=publish  -> _posts_imported/YYYY-MM-DD-slug.md
    * post / status=draft    -> _drafts/slug.md
    * skips private / attachments / nav_menu_item / page / others
- Images: left as original URLs (no rewriting, no download).
- Front matter keeps original WP permalink for backwards compatibility.
"""
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import html2text

ROOT = Path(__file__).resolve().parent.parent
XML_PATH = ROOT / "chuanqizsblog.WordPress.2021-10-09.xml"
OUT_POSTS = ROOT / "_posts"
OUT_DRAFTS = ROOT / "_drafts"

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}


def clean_xml(raw: bytes) -> bytes:
    # Strip characters that are invalid in XML 1.0.
    return re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", raw)


def to_markdown(html_body: str) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    h.protect_links = True
    h.mark_code = True  # wraps <code>/<pre> with [code]...[/code]
    md = h.handle(html_body or "")
    # Convert html2text's [code] markers into fenced code blocks.
    def _fence(m: re.Match) -> str:
        body = m.group(1).strip("\n")
        return f"```\n{body}\n```"

    md = re.sub(r"\[code\](.*?)\[/code\]", _fence, md, flags=re.S)
    # Collapse 3+ blank lines.
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def yaml_escape(s: str) -> str:
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def slugify_fallback(post_id: str, title: str) -> str:
    # Strip chars that break file names / Jekyll URLs.
    base = re.sub(r"[^A-Za-z0-9\-_]+", "-", title or "").strip("-")
    return base.lower() if base else f"post-{post_id}"


def normalize_slug(raw_slug: str, post_id: str, title: str) -> str:
    """Prefer a clean ASCII slug: drop URL-encoded CJK, fall back if empty."""
    # WordPress may export slugs as percent-encoded UTF-8 for CJK titles.
    candidate = re.sub(r"%[0-9a-fA-F]{2}", "-", raw_slug or "")
    candidate = re.sub(r"[^A-Za-z0-9\-_]+", "-", candidate).strip("-").lower()
    candidate = re.sub(r"-+", "-", candidate)
    if candidate and candidate not in {"-", ""}:
        return candidate
    return slugify_fallback(post_id, title)


def main() -> None:
    OUT_POSTS.mkdir(exist_ok=True)
    OUT_DRAFTS.mkdir(exist_ok=True)

    raw = clean_xml(XML_PATH.read_bytes())
    root = ET.fromstring(raw)
    channel = root.find("channel")
    items = channel.findall("item")

    written_posts = 0
    written_drafts = 0
    skipped = 0

    for it in items:
        ptype = it.findtext("wp:post_type", "", NS)
        status = it.findtext("wp:status", "", NS)
        if ptype != "post" or status not in {"publish", "draft"}:
            skipped += 1
            continue

        title = (it.findtext("title") or "").strip()
        post_id = it.findtext("wp:post_id", "", NS)
        date = it.findtext("wp:post_date", "", NS) or ""
        raw_slug = (it.findtext("wp:post_name", "", NS) or "").strip()
        slug = normalize_slug(raw_slug, post_id, title)

        body_html = it.findtext("content:encoded", "", NS) or ""
        body_md = to_markdown(body_html)
        excerpt = (it.findtext("excerpt:encoded", "", NS) or "").strip()

        categories, tags = [], []
        for c in it.findall("category"):
            domain = c.get("domain")
            name = (c.text or "").strip()
            if not name:
                continue
            if domain == "category":
                categories.append(name)
            elif domain == "post_tag":
                tags.append(name)

        link = (it.findtext("link") or "").strip()
        permalink = ""
        m = re.search(r"https?://[^/]+(/.*)$", link)
        if m:
            permalink = m.group(1)

        def quote_list(values):
            if not values:
                return "[]"
            return "[" + ", ".join(f'"{yaml_escape(v)}"' for v in values) + "]"

        front = [
            "---",
            f'title: "{yaml_escape(title)}"',
        ]
        if date:
            front.append(f"date: {date}")
        if categories:
            front.append(f"categories: {quote_list(categories)}")
        if tags:
            front.append(f"tags: {quote_list(tags)}")
        if excerpt:
            front.append(f'excerpt: "{yaml_escape(excerpt)}"')
        if permalink:
            front.append(f'permalink: "{permalink}"')
        front.append("legacy: true")
        front.append("toc: true")
        front.append("classes: wide")
        front.append("---")

        content = "\n".join(front) + "\n\n" + body_md

        if status == "publish":
            date_prefix = (date[:10] if date[:4].isdigit() else "1970-01-01")
            filename = f"{date_prefix}-{slug}.md"
            out = OUT_POSTS / filename
            if out.exists():
                filename = f"{date_prefix}-{slug}-{post_id}.md"
                out = OUT_POSTS / filename
            written_posts += 1
        else:
            filename = f"{slug or post_id}.md"
            out = OUT_DRAFTS / filename
            written_drafts += 1
        out.write_text(content, encoding="utf-8")

    print(f"wrote {written_posts} posts to {OUT_POSTS}")
    print(f"wrote {written_drafts} drafts to {OUT_DRAFTS}")
    print(f"skipped {skipped} items (non-post or private)")


if __name__ == "__main__":
    main()
