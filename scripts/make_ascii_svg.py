"""Convertit assets/source-prepped.png en portrait ASCII monochrome auto-imprimé (SVG/SMIL).

Un seul gris/noir, fond clair, haut contraste : le visage reste lisible.
Chaque ligne est révélée de gauche à droite (un petit curseur suit le balayage),
décalée de haut en bas. Le portrait s'imprime une fois puis reste figé.

Usage : python scripts/make_ascii_svg.py            -> ascii-portrait.svg (animé)
        STATIC=1 python scripts/make_ascii_svg.py   -> version figée (aperçu local)
"""
import os
from html import escape

import cv2
import numpy as np
from PIL import Image

STATIC = os.environ.get("STATIC") == "1"
SRC = "assets/source-prepped.png"
OUT = "ascii-portrait.svg"

COLS = 110                  # caractères par ligne
CHAR_ASPECT = 0.5           # largeur / hauteur d'une cellule monospace
RAMP = " .:-=+*#%@"         # clair -> dense (l'espace efface le fond)
FG = "#1f2328"              # un seul ton (monochrome)
BG = "#f6f8fa"
CURSOR = "#0969da"
FONT = os.environ.get("FONT", "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace")

gray_full = cv2.imread(SRC, cv2.IMREAD_GRAYSCALE)
h, w = gray_full.shape

# masque du sujet : le fond est du blanc pur relié au bord de l'image
bg = (gray_full >= 250).astype(np.uint8)
_, lab = cv2.connectedComponents(bg)
border = (set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])) - {0}
subject = (~np.isin(lab, list(border))).astype(np.uint8) * 255
subject = cv2.morphologyEx(subject, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))

rows = int(round(COLS * (h / w) * CHAR_ASPECT))
g = np.asarray(Image.fromarray(gray_full).resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
m = np.asarray(Image.fromarray(subject).resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0

g = np.clip((g - 0.08) / 0.85, 0, 1)         # contraste élevé
density = 0.05 + 0.95 * (1.0 - g)            # sombre = dense

NB = "\u00a0"  # espace insécable : conserve les marges dans tous les rendus
lines = []
for y in range(rows):
    row = ""
    for x in range(COLS):
        if m[y, x] < 0.5:
            row += NB
        else:
            row += RAMP[min(len(RAMP) - 1, int(density[y, x] * len(RAMP)))].replace(" ", NB)
    lines.append(row)

CW, CH = 6.4, 12.8
PAD = 16
W = int(COLS * CW + PAD * 2)
H = int(rows * CH + PAD * 2)
FS = 10.8
DUR = 0.5
STEP = 0.06

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ASCII portrait of Bilal Bouchroub">']
p.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
if not STATIC:
    p.append("<defs>")
    for i in range(rows):
        p.append(
            f'<clipPath id="c{i}"><rect x="{PAD}" y="{PAD + i*CH:.1f}" width="0" height="{CH:.1f}">'
            f'<animate attributeName="width" from="0" to="{COLS*CW:.1f}" dur="{DUR}s" begin="{i*STEP:.2f}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
    p.append("</defs>")
p.append(f'<g font-family="{FONT}" font-size="{FS}" fill="{FG}" xml:space="preserve">')
for i, line in enumerate(lines):
    if not line.replace(NB, "").strip():
        continue
    y = PAD + i * CH + CH * 0.8
    clip = "" if STATIC else f' clip-path="url(#c{i})"'
    p.append(f'<text x="{PAD}" y="{y:.1f}" textLength="{COLS*CW:.1f}" lengthAdjust="spacing"{clip}>{escape(line)}</text>')
p.append("</g>")

if not STATIC:  # curseur qui suit le bord du balayage
    for i in range(rows):
        b = f"{i*STEP:.2f}s"
        p.append(
            f'<rect x="{PAD}" y="{PAD + i*CH + 1.5:.1f}" width="4" height="{CH-3:.1f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + COLS*CW:.1f}" dur="{DUR}s" begin="{b}" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.05;0.9;1" dur="{DUR}s" begin="{b}" fill="freeze"/>'
            f"</rect>"
        )
p.append("</svg>")

open(OUT, "w", encoding="utf-8").write("\n".join(p))
print(f"OK -> {OUT}  ({COLS}x{rows} caractères, {os.path.getsize(OUT)//1024} KB, {W}x{H})")
