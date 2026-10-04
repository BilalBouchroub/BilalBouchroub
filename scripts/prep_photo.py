"""Prépare la photo pour la conversion ASCII.

1. Efface la bordure circulaire / le fond (tout ce qui est hors du cercle -> blanc)
2. Recadre sur la tête et les épaules
3. Applique CLAHE pour créer de vrais reflets et ombres sur le visage
4. Écrit assets/source-prepped.png (niveaux de gris, fond blanc pur)

Usage : python scripts/prep_photo.py assets/source-photo.jpg
"""
import sys
import cv2
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else "assets/source-photo.jpg"
img = cv2.imread(src)
if img is None:
    sys.exit(f"Impossible de lire {src}")

h, w = img.shape[:2]

# 1) masque circulaire : on retire l'anneau coloré de la photo de profil
mask = np.zeros((h, w), np.uint8)
cv2.circle(mask, (w // 2, h // 2), int(min(h, w) * 0.455), 255, -1)
mask = cv2.GaussianBlur(mask, (0, 0), 3)
white = np.full_like(img, 255)
alpha = (mask.astype(np.float32) / 255.0)[..., None]
img = (img * alpha + white * (1 - alpha)).astype(np.uint8)

# 2) recadrage tête + épaules
x0, x1 = int(w * 0.10), int(w * 0.90)
y0, y1 = int(h * 0.04), int(h * 0.96)
img = img[y0:y1, x0:x1]

# 3) niveaux de gris + CLAHE (contraste local)
gray0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
gray = clahe.apply(gray0)

# 4) fond remis en blanc pur
bg = gray0 > 245
bg = cv2.erode(bg.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
gray[bg] = 255

# 5) correction gamma : visage plus lisible
gray = (255 * (gray / 255.0) ** 1.25).astype(np.uint8)

cv2.imwrite("assets/source-prepped.png", gray)
print("OK -> assets/source-prepped.png", gray.shape)
