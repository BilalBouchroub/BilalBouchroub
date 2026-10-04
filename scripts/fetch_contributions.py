"""Récupère le calendrier de contributions public (sans token, sans API GraphQL).

Source : https://github.com/users/<user>/contributions  (fragment HTML public)
Écrit data/contributions.json : jours bruts + statistiques dérivées.

Usage : python scripts/fetch_contributions.py [pseudo]
"""
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "BilalBouchroub")
URL = f"https://github.com/users/{USER}/contributions"

resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# texte des infobulles : "3 contributions on May 4th." / "No contributions on May 5th."
tips = {}
for tt in soup.find_all("tool-tip"):
    m = re.match(r"\s*(No|\d[\d,]*)\s+contribution", tt.get_text())
    if m and tt.get("for"):
        tips[tt["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))

days = []
for td in soup.find_all("td", attrs={"data-date": True}):
    d = td["data-date"]
    level = int(td.get("data-level", 0))
    count = tips.get(td.get("id"))
    if count is None:  # vieux format : le nombre est dans data-count
        count = int(td.get("data-count", 0))
    days.append({"date": d, "count": count, "level": level})

if not days:
    sys.exit("Aucune cellule trouvée : le HTML de GitHub a peut-être changé.")

days.sort(key=lambda x: x["date"])
total = sum(x["count"] for x in days)

# séries (streaks)
by_date = OrderedDict((x["date"], x["count"]) for x in days)
today = date.today().isoformat()
longest = cur = 0
for dt, c in by_date.items():
    cur = cur + 1 if c > 0 else 0
    longest = max(longest, cur)
current = 0
for dt in reversed(list(by_date)):
    if dt > today:
        continue
    if by_date[dt] > 0:
        current += 1
    elif dt == today:  # aujourd'hui pas encore commité : ne casse pas la série
        continue
    else:
        break

best = max(days, key=lambda x: x["count"])
months = OrderedDict()
for x in days:
    months[x["date"][:7]] = months.get(x["date"][:7], 0) + x["count"]

out = {
    "user": USER,
    "generated": today,
    "total": total,
    "current_streak": current,
    "longest_streak": longest,
    "best_day": best,
    "months": months,
    "days": days,
}
os.makedirs("data", exist_ok=True)
with open("data/contributions.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"OK -> data/contributions.json : {len(days)} jours, {total} contributions, série en cours {current}, record {longest}")
