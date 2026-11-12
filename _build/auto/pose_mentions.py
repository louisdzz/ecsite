#!/usr/bin/env python3
"""Pose le bloc « Mentions externes » sur les fiches maisons existantes listées dans _build/auto/mentions_externes.json.

Méthode 02 : une reconnaissance de tiers est datée, liée, distincte du classement de l'Annuaire, sans rang ni texte recopié.
Les fiches automatiques reçoivent le bloc par le générateur (build_fiches_auto.py lit le même fichier). Ce script traite les
autres fiches : le bloc est inséré une seule fois, juste avant <div class="pv-bottom">, et rien d'autre ne change.
Jamais posé sur : fiche protégée, profil vérifié, étalon, redirection, fiche qui cite déjà la source.
Idempotent : relancer après toute régénération des fiches (python3 _build/auto/pose_mentions.py).
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "_build"))
from build_fiches_auto import bloc_mentions
PROTEGES = {"norman-k", "myway-family-office", "rockfi", "parallel", "ibc-aviation"}
BLOC = re.compile(r'<section aria-labelledby="fa-mentions" id="mentions-externes">.*?</section>', re.S)
ANCRE = '<div class="pv-bottom">'


def exclue(slug, h):
    if slug in PROTEGES: return "fiche protégée"
    if slug.startswith("etalon-") or slug == "demo-fiche-verifiee" or re.search(r"profil étalon|chip-etalon", h, re.I): return "étalon"
    if 'http-equiv="refresh"' in h: return "redirection"
    if "ec-verifie-status" in h or "ec-premium" in h: return "profil vérifié"
    if "leadersleague" in BLOC.sub("", h): return "source déjà citée sur la fiche"
    if 'data-fiche-auto="maison"' in h: return "fiche automatique : bloc posé par le générateur"
    if BLOC.sub("", h).count(ANCRE) != 1: return "gabarit sans emplacement de bas de fiche"
    return None


def main():
    ms = json.load(open(os.path.join(ROOT, "_build/auto/mentions_externes.json"), encoding="utf-8"))["fiches"]
    stats = {"posées": 0, "inchangées": 0}; sautees = []
    for slug, mentions in sorted(ms.items()):
        p = os.path.join(ROOT, "f", slug + ".html")
        if not os.path.exists(p): sautees.append((slug, "fiche absente")); continue
        h0 = open(p, encoding="utf-8").read()
        motif = exclue(slug, h0)
        if motif:
            if not motif.startswith("fiche automatique"): sautees.append((slug, motif))
            continue
        h = BLOC.sub("", h0)
        h = h.replace(ANCRE, bloc_mentions(mentions) + ANCRE, 1)
        if h != h0:
            open(p, "w", encoding="utf-8").write(h); stats["posées"] += 1
        else: stats["inchangées"] += 1
    print(stats, "· non traitées", len(sautees), sautees[:20])


if __name__ == "__main__":
    main()
