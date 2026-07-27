# -*- coding: utf-8 -*-
"""Deuxième passe de vérification des domaines résolus.
Le résolveur accepte un domaine dès qu'un seul jeton du nom apparaît dans la page,
ce qui laisse passer des homonymes (alexa.com, smart.fr, jacquet.fr...). Ici on
exige beaucoup plus :
  - nom à plusieurs mots  -> au moins 2 mots distinctifs présents dans la page
  - nom à un seul mot     -> le mot + un signal de secteur (patrimoine, capital,
                             avocat, fonds, gestion, invest...)
Sortie : _build/domains/verdict.json {slug: {"ok":bool,"why":str,"domain":str}}
"""
import glob, json, os, re, socket, ssl, sys, threading, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, '_build/domains')
from resolve import strip_accents, words, STOP  # noqa

OUT = '_build/domains/verdict.json'
UA = 'Mozilla/5.0 (compatible; ExitClubBot/1.0; +https://www.exit.club)'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
socket.setdefaulttimeout(8)

SECTEUR = ('patrimoine', 'patrimonial', 'gestion privee', 'gestion de patrimoine',
           'investissement', 'capital', 'avocat', 'notaire', 'fonds', 'private equity',
           'family office', 'conseil', 'cession', 'acquisition', 'finance', 'financier',
           'wealth', 'banque', 'invest', 'legal', 'fiscal', 'assurance vie', 'immobilier',
           'venture', 'm&a', 'transmission', 'epargne', 'allocation', 'portefeuille',
           'credit', 'courtier', 'audit', 'expertise', 'asset management', 'fund')

verdict = json.load(open(OUT)) if os.path.exists(OUT) else {}
lock = threading.Lock()
n = [0]


def core(nom):
    return [w for w in words(nom) if w not in STOP and len(w) > 2]


def page(url):
    for u in (url, url.replace('https://www.', 'https://')):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
                return strip_accents(r.read(200000).decode('utf-8', 'ignore')).lower()
        except Exception:
            continue
    return None


def one(item):
    slug, v = item
    res = {'domain': v['domain'], 'ok': False, 'why': ''}
    body = page(v['url'])
    if body is None:
        res['why'] = 'injoignable'
    else:
        txt = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', body, flags=re.S)
        c = core(v['nom'])
        hits = [w for w in c if w in txt]
        if len(c) >= 2:
            res['ok'] = len(hits) >= 2
            res['why'] = '%d/%d mots' % (len(hits), len(c))
        elif len(c) == 1:
            sec = [s for s in SECTEUR if s in txt]
            res['ok'] = bool(hits and sec)
            res['why'] = 'mot unique + secteur:%s' % (sec[0] if sec else 'aucun')
        else:
            res['ok'] = True
            res['why'] = 'nom non testable'
    with lock:
        verdict[slug] = res
        n[0] += 1
        if n[0] % 100 == 0:
            json.dump(verdict, open(OUT, 'w'), ensure_ascii=False)
            print('%d vérifiés · %d ok' % (len(verdict), sum(1 for x in verdict.values() if x['ok'])), flush=True)


if __name__ == '__main__':
    dom = {}
    for p in sorted(glob.glob('_build/domains/*-*.json')):
        for s, v in json.load(open(p)).items():
            dom.setdefault(s, v)
    items = [(s, v) for s, v in dom.items() if s not in verdict]
    print('%d à vérifier' % len(items), flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        list(ex.map(one, items))
    json.dump(verdict, open(OUT, 'w'), ensure_ascii=False)
    ok = sum(1 for x in verdict.values() if x['ok'])
    print('FIN %d vérifiés · %d confirmés · %d écartés' % (len(verdict), ok, len(verdict) - ok), flush=True)
