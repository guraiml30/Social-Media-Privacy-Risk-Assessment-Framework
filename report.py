"""Privacy report generation: Markdown and a simple standalone HTML page."""
import html
import re
from datetime import datetime

from . import DISCLAIMER
from .awareness import LEVEL_GUIDANCE, TIPS, RED_FLAGS
from .questions import CATEGORY_BY_ID, CATEGORIES
from .recommendations import build_recommendations, build_checklist


def build_markdown(result, label="Demo profile"):
    recs = build_recommendations(result)
    checklist = build_checklist(result)
    L = [
        "# Social Media Privacy Risk Report",
        f"Profile: {label} | Generated: {datetime.now():%Y-%m-%d %H:%M}",
        "",
        DISCLAIMER,
        "",
        "## Summary",
        f"- **Privacy Risk Score:** {result.overall} / 100 (higher = more exposure)",
        f"- **Risk Level:** {result.level}",
        f"- Base score {result.base} + combination bonus {result.bonus}",
        f"- {LEVEL_GUIDANCE[result.level]}",
        "",
        "## Category scores",
        "| Category | Score |",
        "|---|---|",
    ]
    for c in CATEGORIES:
        L.append(f"| {c.name} | {result.category_scores[c.id]} |")

    L += ["", "## Detected weaknesses"]
    L += [f"- **{w['severity']}** - {w['category_name']}: {w['weakness']} (your answer: {w['answer']})"
          for w in result.weaknesses] or ["- None detected."]

    L += ["", "## Recommendations (most important first)"]
    L += [f"- **{r['priority']}** - {r['category']}: {r['action']}" for r in recs] \
        or ["- Keep up your current habits."]

    L += ["", "## Privacy checklist"]
    L += [f"- [{'x' if i['done'] else ' '}] {i['item']}" for i in checklist]

    L += ["", "## Security-awareness guidance"]
    L += [f"- **{t}:** {b}" for t, b in TIPS]
    L += ["", "### Scam red flags"] + [f"- {r}" for r in RED_FLAGS]
    return "\n".join(L) + "\n"


def _inline(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(text))


def build_html(result, label="Demo profile"):
    md = build_markdown(result, label)
    out, in_list, in_table = [], False, False
    for raw in md.splitlines():
        s = raw.rstrip()
        if s.startswith("|"):
            if set(s.replace("|", "").strip()) <= set("-: "):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if in_list:
                out.append("</ul>"); in_list = False
            tag = "td"
            if not in_table:
                out.append("<table>"); in_table = True; tag = "th"
            out.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>"); in_table = False
        if s.startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list = True
            item = s[2:].replace("[x] ", "&#9745; ").replace("[ ] ", "&#9744; ")
            out.append(f"<li>{_inline(item).replace('&amp;#', '&#')}</li>")
            continue
        if in_list:
            out.append("</ul>"); in_list = False
        if s.startswith("### "):
            out.append(f"<h3>{_inline(s[4:])}</h3>")
        elif s.startswith("## "):
            out.append(f"<h2>{_inline(s[3:])}</h2>")
        elif s.startswith("# "):
            out.append(f"<h1>{_inline(s[2:])}</h1>")
        elif s:
            out.append(f"<p>{_inline(s)}</p>")
    if in_list:
        out.append("</ul>")
    if in_table:
        out.append("</table>")
    style = ("body{font-family:system-ui,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;"
             "line-height:1.5}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 10px}"
             "th{background:#f0f0f0}")
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>Privacy Risk Report</title>"
            f"<style>{style}</style></head><body>{''.join(out)}</body></html>")
