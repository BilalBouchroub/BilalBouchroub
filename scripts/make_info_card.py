"""Fiche d'info façon neofetch (SVG) : les lignes apparaissent l'une après l'autre.
Usage : python scripts/make_info_card.py        (STATIC=1 pour une image figée)
"""
import os
from html import escape

STATIC = os.environ.get("STATIC") == "1"

USER = "BilalBouchroub"
ROWS = [  # (clé, valeur, couleur de valeur ou None)
    ("OS", "Engineering Student @ ENSA El Jadida (ENSAJ)", None),
    ("Role", "Full-Stack · Data Engineering · AI / MLOps", None),
    ("Status", "Open to PFE (final-year project) ●", "#3fb950"),
    ("Now", "MLOps platform: water stress in Morocco", None),
    ("Prev", ".NET AI Developer @ BPS Maroc (2026)", None),
    ("", "Data Engineer @ TAQA Morocco (2025)", None),
    ("Stack", "C# · ASP.NET Core · Spring Boot · React · FastAPI", None),
    ("Data/AI", "SSIS · Power BI · Spark · Kafka · ClearML", None),
    ("Cloud", "AWS · Docker · Kubernetes · GitHub Actions", None),
    ("Mobile", "Kotlin · MVVM · Room · Firebase", None),
    ("Certs", "AWS Cloud Foundations · Java SE 17 · C# .NET", None),
    ("Langs", "العربية (native) · Français · English", None),
    ("Shell", "bash, with a bit of AI in the loop", None),
]

W, H = 640, 470
LX, VX = 34, 130
Y0, LH = 108, 25
KEY, TXT, MUTED, BG = "#58a6ff", "#c9d1d9", "#8b949e", "#0d1117"

def fade(i):
    if STATIC:
        return ""
    return (f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{0.5 + i*0.22:.2f}s" fill="freeze"/>')

def wrap(inner, i):
    op = "" if STATIC else ' opacity="0"'
    return f"<g{op}>{inner}{fade(i)}</g>"

s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Info card for Bilal Bouchroub">']
s.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="#30363d"/>')
s.append('<circle cx="26" cy="24" r="6" fill="#ff5f56"/><circle cx="46" cy="24" r="6" fill="#ffbd2e"/><circle cx="66" cy="24" r="6" fill="#27c93f"/>')
s.append(f'<text x="{W/2}" y="29" text-anchor="middle" font-size="12" fill="{MUTED}" font-family="ui-monospace,Menlo,Consolas,monospace">bilal@github: ~</text>')
s.append('<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace" font-size="14">')

s.append(wrap(f'<text x="{LX}" y="64" fill="{TXT}">$ neofetch</text>', 0))
s.append(wrap(f'<text x="{LX}" y="92" font-size="17" font-weight="700"><tspan fill="{KEY}">bilal</tspan><tspan fill="{TXT}">@</tspan><tspan fill="{KEY}">{USER}</tspan></text>', 1))
i = 2
for k, v, col in ROWS:
    y = Y0 + (i - 2) * LH + 14
    key = f'<tspan fill="{KEY}" font-weight="700">{escape(k)}</tspan>' if k else ""
    s.append(wrap(
        f'<text x="{LX}" y="{y}" xml:space="preserve">{key}</text>'
        f'<text x="{VX}" y="{y}" fill="{col or TXT}">{escape(v)}</text>', i))
    i += 1

# palette de couleurs façon neofetch
py = H - 28
pal = "".join(f'<rect x="{LX + n*26}" y="{py}" width="22" height="12" rx="3" fill="{c}"/>'
              for n, c in enumerate(["#ff7b72", "#ffa657", "#e3b341", "#3fb950", "#58a6ff", "#bc8cff", "#f778ba", "#c9d1d9"]))
s.append(wrap(pal, i))
s.append("</g></svg>")

open("info-card.svg", "w", encoding="utf-8").write("\n".join(s))
print(f"OK -> info-card.svg ({os.path.getsize('info-card.svg')//1024} KB)")
