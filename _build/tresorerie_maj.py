#!/usr/bin/env python3
# Comparateur trésorerie (www.exit.club/tresorerie) : mise à jour des taux.
#
# Deux usages, lancés par l'Action GitHub « tresorerie-taux.yml » :
#
#   python3 _build/tresorerie_maj.py
#       Met à jour, dans tresorerie.json et dans la copie embarquée de
#       tresorerie.html, tout ce qui se lit sur une source officielle sans
#       intervention humaine : le taux de la facilité de dépôt de la BCE,
#       l'€STR de la veille, et le rendement des produits qui exposent une API
#       publique (Spiko). Chaque valeur garde sa date. Ne touche à rien d'autre.
#
#   python3 _build/tresorerie_maj.py --issue
#       Imprime, en Markdown, la liste des produits sans API (relevés à la
#       main) avec leur taux courant, leur date et leur source : c'est le corps
#       de l'issue mensuelle « vérifier les taux publiés ».
#
# Règles : uniquement la bibliothèque standard ; toute source injoignable laisse
# la valeur précédente en place et l'écrit sur la sortie standard ; le script
# ne renvoie jamais une erreur pour une source en panne, seulement pour un
# fichier absent ou illisible. Aucune clé, aucun secret.

import json
import re
import sys
import urllib.request
from datetime import date, datetime

FICHIER_JSON = "tresorerie.json"
FICHIER_HTML = "tresorerie.html"
DEBUT_EMBARQUE = '<script id="donnees" type="application/json">'
FIN_EMBARQUE = "</script>"

ESTR_CSV = "https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT?lastNObservations=1&format=csvdata"
BCE_TAUX = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html"
HOTES_API = ("https://public-api.spiko.io/",)

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]
MOIS_EN = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def lire(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "exit.club comparateur tresorerie (contact@exit.club)",
                                               "Accept": "application/json, text/csv, text/html;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def pourcent_fr(x):
    return ("%.2f" % x).replace(".", ",") + " %"


def date_fr(iso):
    a, m, j = iso.split("-")
    return "%d %s %s" % (int(j), MOIS_FR[int(m) - 1], a)


def maj_estr(d, journal):
    try:
        lignes = [l for l in lire(ESTR_CSV).splitlines() if l.startswith("EST.")]
        if not lignes:
            raise ValueError("aucune observation")
        champs = lignes[-1].split(",")
        jour, valeur = champs[4], float(champs[5])
        for r in d.get("reperes", []):
            if r.get("libelle", "").upper().startswith("€STR") or r.get("libelle", "").upper().startswith("EUR STR"):
                r["valeur"] = pourcent_fr(valeur)
                r["detail"] = "taux au jour le jour, " + date_fr(jour)
                journal.append("€STR %s au %s" % (r["valeur"], jour))
                return
        journal.append("€STR : aucun repère à mettre à jour")
    except Exception as e:  # noqa: BLE001
        journal.append("€STR injoignable, valeur conservée (%s)" % e)


def maj_bce(d, journal):
    try:
        page = lire(BCE_TAUX)
        lignes = re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S)
        for l in lignes:
            cellules = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", l, re.S)]
            if len(cellules) >= 3 and re.match(r"^\d{4}$", cellules[0]):
                annee = int(cellules[0])
                m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3})", cellules[1])
                if not m:
                    continue
                jour, mois = int(m.group(1)), MOIS_EN.get(m.group(2).lower()[:3])
                if not mois:
                    continue
                depot = float(cellules[2])
                iso = "%04d-%02d-%02d" % (annee, mois, jour)
                for r in d.get("reperes", []):
                    if "BCE" in r.get("libelle", "").upper() or "dépôt" in r.get("libelle", "").lower():
                        r["valeur"] = pourcent_fr(depot)
                        r["detail"] = "depuis le " + date_fr(iso)
                        journal.append("BCE facilité de dépôt %s depuis le %s" % (r["valeur"], iso))
                        return
                break
        journal.append("BCE : tableau des taux non reconnu, valeur conservée")
    except Exception as e:  # noqa: BLE001
        journal.append("BCE injoignable, valeur conservée (%s)" % e)


def maj_api(p, journal):
    api = p.get("api", "")
    if not api or not any(api.startswith(h) for h in HOTES_API):
        return
    try:
        y = json.loads(lire(api))
        m = float(y.get("monthlyYield"))
        if not (0 < m < 0.5):
            raise ValueError("rendement hors bornes : %r" % m)
        pct = round(m * 10000) / 100.0
        jour = str(y.get("updatedAt", ""))[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", jour):
            jour = date.today().isoformat()
        p["taux"] = pourcent_fr(pct)
        p["taux_num"] = pct
        p["taux_date"] = jour
        p["verifie"] = jour
        journal.append("%s, %s : %s au %s" % (p.get("maison"), p.get("produit"), p["taux"], jour))
    except Exception as e:  # noqa: BLE001
        journal.append("%s, %s : API injoignable, valeur conservée (%s)" % (p.get("maison"), p.get("produit"), e))


def reecrire_embarque(json_txt):
    try:
        s = open(FICHIER_HTML, encoding="utf-8").read()
    except FileNotFoundError:
        return False
    a = s.find(DEBUT_EMBARQUE)
    if a < 0:
        return False
    a += len(DEBUT_EMBARQUE)
    b = s.find(FIN_EMBARQUE, a)
    if b < 0:
        return False
    nouveau = s[:a] + "\n" + json_txt.replace("</", "<\\/") + "  " + s[b:]
    if nouveau != s:
        open(FICHIER_HTML, "w", encoding="utf-8").write(nouveau)
        return True
    return False


def corps_issue(d):
    manuels = [p for p in d["produits"] if not p.get("api")]
    lignes = [
        "Relevé mensuel des taux publiés par les maisons du comparateur https://www.exit.club/tresorerie",
        "",
        "Pour chaque ligne : ouvrir la source, comparer, et si le chiffre a bougé, corriger `taux`, `taux_num`, `taux_type` si besoin, `taux_date` et `verifie` dans `tresorerie.json` (édition directe : https://github.com/louisdzz/ecsite/edit/main/tresorerie.json). Mettre `mis_a_jour` à la date du relevé une fois toutes les lignes vues. La page se met à jour au déploiement suivant.",
        "",
        "Règles : le taux tel que la maison le publie, jamais recalculé ; la date de la page source ; aucune recommandation ; pas de tiret cadratin.",
        "",
    ]
    for p in manuels:
        lignes.append("- [ ] **%s, %s** : %s (%s), publié au %s, vérifié le %s. Source : %s" % (
            p.get("maison"), p.get("produit"), p.get("taux"), p.get("taux_type"),
            p.get("taux_date", "?"), p.get("verifie", "?"), p.get("source")))
    lignes += [
        "",
        "Automatique, rien à faire : les deux fonds Spiko (API publique) et les repères BCE / €STR.",
        "",
        "Dernier relevé complet : %s." % d.get("mis_a_jour", "?"),
    ]
    return "\n".join(lignes)


def main():
    try:
        d = json.load(open(FICHIER_JSON, encoding="utf-8"))
    except (FileNotFoundError, ValueError) as e:
        print("ECHEC : %s illisible (%s)" % (FICHIER_JSON, e))
        return 1

    if "--issue" in sys.argv:
        print(corps_issue(d))
        return 0

    d.pop("auto_le", None)
    avant = json.dumps(d, ensure_ascii=False, sort_keys=True)
    journal = []
    maj_bce(d, journal)
    maj_estr(d, journal)
    for p in d.get("produits", []):
        maj_api(p, journal)

    for l in journal:
        print("  " + l)

    if json.dumps(d, ensure_ascii=False, sort_keys=True) == avant:
        print("Aucun changement de taux.")
        return 0

    d["auto_le"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    json_txt = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
    open(FICHIER_JSON, "w", encoding="utf-8").write(json_txt)
    embarque = reecrire_embarque(json_txt)
    print("tresorerie.json mis à jour" + (", copie embarquée dans tresorerie.html aussi" if embarque else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
