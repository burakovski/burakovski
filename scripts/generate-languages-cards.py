#!/usr/bin/env python3
"""Build top-3 languages card in streak-cards visual style (half height)."""
import json, os, subprocess, collections
from pathlib import Path

user = os.environ.get("GITHUB_USER", "burakovski")
token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or ""
out = Path(os.environ.get("OUT_FILE", ".github/assets/languages-cards.svg"))

H = 98
W = 495
S = 0.5

FALLBACK = [
    ("TypeScript", 83.83, "#3178C6", "ts"),
    ("JavaScript", 12.83, "#CA8A04", "js"),
    ("CSS", 2.84, "#7C3AED", "css"),
]

COLORS = {
    "TypeScript": "#3178C6",
    "JavaScript": "#CA8A04",
    "CSS": "#7C3AED",
    "PLpgSQL": "#336791",
    "HTML": "#E34F26",
    "Python": "#3776AB",
    "Shell": "#4EAA25",
}

def curl_json(url):
    cmd = [
        "curl", "-4", "-sL", "--max-time", "20", "-A", "Mozilla/5.0",
        "-H", "Accept: application/vnd.github+json", url,
    ]
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    try:
        raw = subprocess.check_output(cmd, text=True)
        return json.loads(raw) if raw.strip() else None
    except Exception:
        return None

def fetch_top3():
    repos = curl_json(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner")
    if not isinstance(repos, list):
        return None
    totals = collections.Counter()
    for r in repos:
        if r.get("fork"):
            continue
        langs = curl_json(f"https://api.github.com/repos/{r['full_name']}/languages")
        if isinstance(langs, dict):
            totals.update(langs)
    total = sum(totals.values())
    if total <= 0:
        return None
    icons = {"TypeScript": "ts", "JavaScript": "js", "CSS": "css"}
    result = []
    for name, bytes_ in totals.most_common(3):
        pct = bytes_ / total * 100
        result.append((name, pct, COLORS.get(name, "#2563EB"), icons.get(name, "ts")))
    return result

def icon(t, color):
    if t == "js":
        return f'<rect x="3" y="5" width="18" height="14" rx="2" fill="{color}"/><text x="12" y="15.5" text-anchor="middle" font-size="7" font-weight="700" fill="#111" font-family="ui-sans-serif,system-ui,sans-serif">JS</text>'
    if t == "css":
        return f'<rect x="3" y="5" width="18" height="14" rx="2" fill="{color}"/><text x="12" y="15.5" text-anchor="middle" font-size="6.5" font-weight="700" fill="#fff" font-family="ui-sans-serif,system-ui,sans-serif">CSS</text>'
    label = "TS" if t == "ts" else t[:3].upper()
    return f'<rect x="3" y="5" width="18" height="14" rx="2" fill="{color}"/><text x="12" y="15.5" text-anchor="middle" font-size="7" font-weight="700" fill="#fff" font-family="ui-sans-serif,system-ui,sans-serif">{label}</text>'

langs = fetch_top3() or FALLBACK

font_num = 28 * S
font_label = 14 * S
font_sub = 12 * S
r = 20 * S
icon_ty = 18 * S
icon_inner = 10 * S
y_num = 95 * S
y_label = 125 * S
y_sub = 148 * S
line_y1 = 28 * S
line_y2 = 170 * S

parts = []
for i, (name, pct, color, ic) in enumerate(langs):
    x = i * 165
    cx = x + 82.5
    num = f"{pct:.1f}%"
    line = f'<line x1="{x}" y1="{line_y1}" x2="{x}" y2="{line_y2}" stroke="#E4E2E2"/>' if i else ""
    parts.append(f'''{line}
  <g transform="translate({cx - 12 * S}, {icon_ty})">
    <circle cx="{12 * S}" cy="{22 * S}" r="{r}" fill="none" stroke="{color}" stroke-width="{3 * S}"/>
    <g transform="translate(0, {icon_inner}) scale({S})">{icon(ic, color)}</g>
  </g>
  <text x="{cx}" y="{y_num}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{font_num}" font-weight="700" fill="{color}">{num}</text>
  <text x="{cx}" y="{y_label}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{font_label}" font-weight="600" fill="{color}">{name}</text>
  <text x="{cx}" y="{y_sub}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{font_sub}" fill="#9CA3AF">by code volume</text>''')

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Top languages">
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="4.5" fill="#FFFEFE" stroke="#E4E2E2"/>
  {''.join(parts)}
</svg>
'''
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(svg)
print("wrote", out, langs, {"H": H})
