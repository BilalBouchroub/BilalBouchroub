"""Dessine data/contributions.json en carte thermique SVG (53 semaines x 7 jours).

Révélation diagonale unique (CSS keyframes, pas de boucle), légende Moins->Plus et pied de stats.
Usage : python scripts/render_heatmap_svg.py        (STATIC=1 pour une image figée)
"""
import json
import os
from datetime import date, datetime

STATIC = os.environ.get("STATIC") == "1"
data = json.load(open("data/contributions.json", encoding="utf-8"))
days = data["days"]

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, TXT, MUTED = "#0d1117", "#c9d1d9", "#8b949e"
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 40, 46
W = 860

first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
offset = (first.weekday() + 1) % 7            # dimanche = 0 (comme GitHub)
weeks = (offset + len(days) + 6) // 7
H = TOP + 7 * STEP + 62

# niveau 5 = jours très actifs (au-dessus de 80 % du record)
mx = max((d["count"] for d in days), default=0)
def level(d):
    l = d["level"]
    if l == 4 and mx > 0 and d["count"] >= 0.8 * mx and mx >= 5:
        return 5
    return l

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub contributions of the last year">']
svg.append("<style>")
svg.append(f"text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{MUTED};font-size:10px}}")
svg.append(f".t{{fill:{TXT};font-size:12px}} .g{{fill:#3fb950}}")
if not STATIC:
    svg.append(".d{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out forwards}")
    svg.append("@keyframes pop{0%{opacity:0;transform:scale(.2)}100%{opacity:1;transform:scale(1)}}")
svg.append("</style>")
svg.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
svg.append(f'<text class="t" x="{LEFT}" y="22">$ ./contributions.sh <tspan class="g">--user {data["user"]}</tspan></text>')

# libellés de jours
for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    svg.append(f'<text x="8" y="{TOP + i*STEP + 10}">{lab}</text>')

# cellules + libellés de mois
last_month = None
for idx, d in enumerate(days):
    pos = idx + offset
    wk, dow = divmod(pos, 7)
    x, y = LEFT + wk * STEP, TOP + dow * STEP
    dt = datetime.strptime(d["date"], "%Y-%m-%d").date()
    if dow == 0 and dt.month != last_month and (last_month is not None or dt.day <= 7 or True):
        if wk < weeks - 2:
            svg.append(f'<text x="{x}" y="{TOP-8}">{dt.strftime("%b")}</text>')
        last_month = dt.month
    delay = (wk * 0.035 + dow * 0.035)
    style = "" if STATIC else f' class="d" style="animation-delay:{delay:.2f}s"'
    tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} — {d["date"]}'
    svg.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level(d)]}"{style}><title>{tip}</title></rect>')

# légende
ly = TOP + 7 * STEP + 18
lx = W - 40 - 6 * STEP - 70
svg.append(f'<text x="{lx}" y="{ly+10}">Moins</text>')
for i, c in enumerate(PALETTE):
    svg.append(f'<rect x="{lx + 40 + i*STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
svg.append(f'<text x="{lx + 40 + 6*STEP + 4}" y="{ly+10}">Plus</text>')

# pied de page : stats
fy = H - 16
best = data["best_day"]
svg.append(
    f'<text class="t" x="{LEFT}" y="{ly+10}"><tspan class="g">{data["total"]:,}</tspan> contributions in the last year</text>'.replace(",", " ")
)
svg.append(
    f'<text x="{LEFT}" y="{fy}">streak actuelle : {data["current_streak"]} j  ·  record : {data["longest_streak"]} j  ·  meilleur jour : {best["count"]} ({best["date"]})  ·  mis à jour : {data["generated"]}</text>'
)
svg.append("</svg>")

open("contrib-heatmap.svg", "w", encoding="utf-8").write("\n".join(svg))
print(f"OK -> contrib-heatmap.svg ({weeks} semaines, {os.path.getsize('contrib-heatmap.svg')//1024} KB)")
