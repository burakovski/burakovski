#!/usr/bin/env python3
import json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone

user = os.environ.get("GITHUB_USER", "burakovski")
out = Path(os.environ.get("OUT_FILE", ".github/assets/streak-cards.svg"))
# Half of original 195 — keep full width layout, scale type/icons to height
H = 98
W = 495
S = 0.5  # 0.5

raw = subprocess.check_output(
    ["curl", "-sL", "-A", "Mozilla/5.0", f"https://streak-stats.demolab.com/?user={user}&type=json"],
    text=True,
)
data = json.loads(raw)

def fmt(iso):
    if not iso:
        return ""
    d = datetime.strptime(iso, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    year = d.year != datetime.now(timezone.utc).year
    return d.strftime("%b %-d, %Y" if year else "%b %-d")

total = data.get("totalContributions", 0)
first = fmt(data.get("firstContribution"))
curr = (data.get("currentStreak") or {}).get("length", 0)
cs = fmt((data.get("currentStreak") or {}).get("start"))
ce = fmt((data.get("currentStreak") or {}).get("end"))
curr_range = f"{cs} - {ce}" if cs and ce and cs != ce else (cs or ce or "")
longest = (data.get("longestStreak") or {}).get("length", 0)
ls = fmt((data.get("longestStreak") or {}).get("start"))
le = fmt((data.get("longestStreak") or {}).get("end"))
long_range = " - ".join(x for x in (ls, le) if x)

panels = [
    (0, "#2563EB", total, "Total Contributions", f"{first} - Present" if first else "", "chart"),
    (165, "#F97316", curr, "Current Streak", curr_range, "fire"),
    (330, "#7C3AED", longest, "Longest Streak", long_range, "trophy"),
]

def icon(t, color):
    if t == "fire":
        return f'<path fill="{color}" d="M12 23c-4.2 0-7-2.9-7-7 0-2.6 1.4-4.6 2.9-6.2.3-.3.8-.2.9.2.3 1.4.9 2.4 1.7 3-.2-2.4.5-4.8 2.1-6.8.4-.5 1.2-.2 1.2.4 0 2.2.9 3.9 2.1 5.2.7-1.1 1.2-2.5 1.2-4.1 0-.5.6-.8 1-.5C19.6 8.8 21 11.4 21 14.5 21 19.2 17.4 23 12 23z"/>'
    if t == "trophy":
        return f'<path fill="{color}" d="M6 4h12v2a5 5 0 0 1-4 4.9V13h2.5a1 1 0 0 1 0 2H7.5a1 1 0 0 1 0-2H10v-2.1A5 5 0 0 1 6 6V4zm-2 1H2.5A1.5 1.5 0 0 0 1 6.5C1 9.5 3 11 6 11V9C4.6 9 3 8.2 3 6.5V5zm16 0h-1.5v1.5C17.5 8.2 15.9 9 14.5 9v2c3 0 5-1.5 5-4.5A1.5 1.5 0 0 0 18 5zM9 17h6v2H9v-2zm-1 3h8v2H8v-2z"/>'
    return f'<rect x="4" y="14" width="4" height="6" rx="1" fill="{color}"/><rect x="10" y="9" width="4" height="11" rx="1" fill="{color}"/><rect x="16" y="5" width="4" height="15" rx="1" fill="{color}"/>'

# Original y layout (195h) scaled by S; x unchanged for full width
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
for i, (x, color, num, label, sub, ic) in enumerate(panels):
    cx = x + 82.5
    line = f'<line x1="{x}" y1="{line_y1}" x2="{x}" y2="{line_y2}" stroke="#E4E2E2"/>' if i else ""
    parts.append(f'''{line}
  <g transform="translate({cx - 12 * S}, {icon_ty})">
    <circle cx="{12 * S}" cy="{22 * S}" r="{r}" fill="none" stroke="{color}" stroke-width="{3 * S}"/>
    <g transform="translate(0, {icon_inner}) scale({S})">{icon(ic, color)}</g>
  </g>
  <text x="{cx}" y="{y_num}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{font_num}" font-weight="700" fill="{color}">{num}</text>
  <text x="{cx}" y="{y_label}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{font_label}" font-weight="600" fill="{color}">{label}</text>
  <text x="{cx}" y="{y_sub}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{font_sub}" fill="#9CA3AF">{sub}</text>''')

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub streak stats">
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="4.5" fill="#FFFEFE" stroke="#E4E2E2"/>
  {''.join(parts)}
</svg>
'''
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(svg)
print("wrote", out, {"total": total, "curr": curr, "longest": longest, "H": H})
