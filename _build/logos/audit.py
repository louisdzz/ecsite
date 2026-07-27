# -*- coding: utf-8 -*-
"""Détecte les logos qui appartiennent en fait à une AUTRE maison.
C'est la faille structurelle du pipeline : `related()` accepte un fichier dès
que son nom contient "logo", ce qui laisse passer les logos de participations,
de sociétés soeurs, de marques successeurs ou d'hébergeurs.

Méthode : on lit les jetons du nom de fichier. Un jeton est suspect s'il
désigne une autre maison de l'annuaire (jeton distinctif, porté par <= 3
maisons) ou une grande marque connue pour être scrapée par erreur.

Usage : python3 _build/logos/audit.py        # liste les suspects
        python3 _build/logos/purge.py <slug> # retire un logo confirmé faux
Le verdict final reste visuel : ce script trie, il ne décide pas.
"""
import glob, json, os, re, sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, '_build/domains')
from resolve import words, STOP  # noqa

# marques hors annuaire déjà prises la main dans le sac
BIG = set("""amazon google microsoft apple oracle salesforce shopify wordpress wix squarespace
hostinger ovhcloud 1und1 ionos godaddy synchrony learfield lseg pgim prudential phoenix
citwell glopal klintt fatec unomena destia tidal vision lacyme hellowatt mediaoptions
indosuez charterhouse blackrock vanguard fidelity schwab morningstar bloomberg refinitiv
sequoia accel benchmark bessemer insight tiger softbank naspers prosus""".split())


def load():
    dom = {}
    for p in sorted(glob.glob('_build/domains/*-*.json')):
        for s, v in json.load(open(p)).items():
            dom.setdefault(s, v)
    meta = json.load(open('_build/logos/dir-meta.json'))
    state = json.load(open('_build/logos/raw-state.json'))
    return dom, meta, state


def distinctifs(dom):
    cnt, owner = Counter(), {}
    for s, v in dom.items():
        for w in set(words(v['nom'])):
            if len(w) >= 5 and w not in STOP:
                cnt[w] += 1
                owner.setdefault(w, set()).add(s)
    return {w for w, c in cnt.items() if c <= 3}, owner


def suspects():
    dom, meta, state = load()
    DIST, OWNER = distinctifs(dom)
    out = []
    for s, v in meta.items():
        src = (state.get(s) or {}).get('src') or v.get('src')
        if not src:
            continue
        seg = re.sub(r'%[0-9a-f]{2}', ' ', src.split('?')[0].rsplit('/', 1)[-1], flags=re.I)
        own = set(words(v.get('nom', s)))
        base = (dom.get(s, {}).get('domain', '') or '').rsplit('.', 1)[0].replace('-', '')
        hits = []
        for t in [t for t in re.split(r'[^a-z0-9]+', seg.lower()) if len(t) >= 5]:
            if t in own or (base and (t in base or base[:6] in t)):
                continue
            if t in BIG:
                hits.append(t + '!')
            elif t in DIST and s not in OWNER[t]:
                hits.append(t)
        if hits:
            out.append((s, v.get('nom', s), seg, hits))
    return sorted(out)


if __name__ == '__main__':
    r = suspects()
    print('suspects marque-tierce : %d' % len(r))
    for s, nom, seg, h in r:
        print('%-44s %-30s %-24s %s' % (s, nom[:30], ','.join(h)[:24], seg[:52]))
