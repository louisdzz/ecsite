# -*- coding: utf-8 -*-
"""Résout le vrai domaine de chaque institution de l'Écosystème.
Méthode : on fabrique des candidats de domaine à partir du nom, on vérifie que
le DNS répond, que le site répond en HTTP, et que la page cite bien un jeton
distinctif du nom. Aucun moteur de recherche n'est interrogé.
Sortie : _build/domains/<cat>.json  {slug: {"nom","domain","url","titre"}}
"""
import json, os, re, socket, ssl, sys, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
OUT = '_build/domains'
os.makedirs(OUT, exist_ok=True)

UA = 'Mozilla/5.0 (compatible; ExitClubBot/1.0; +https://www.exit.club)'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
socket.setdefaulttimeout(6)

STOP = {'sa', 'sas', 'sarl', 'scp', 'selarl', 'aarpi', 'associes', 'et', 'de', 'du', 'des',
        'la', 'le', 'les', 'and', 'the', 'llp', 'avocats', 'france'}


def strip_accents(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()


def words(nom):
    s = strip_accents(nom).lower()
    s = re.sub(r"[^a-z0-9]+", ' ', s)
    return [w for w in s.split() if w]


def candidates(nom):
    w = words(nom)
    core = [x for x in w if x not in STOP] or w
    joins = []
    joins.append(''.join(core))
    joins.append('-'.join(core))
    if len(core) > 1:
        joins.append(''.join(core[:2]))
        joins.append('-'.join(core[:2]))
        joins.append(core[0])
    out, seen = [], set()
    for base in joins:
        if len(base) < 3 or len(base) > 40:
            continue
        for tld in ('.com', '.fr'):
            d = base + tld
            if d not in seen:
                seen.add(d)
                out.append(d)
    return out[:10]


def token(nom):
    """Jeton distinctif à retrouver dans la page pour valider le domaine."""
    core = [x for x in words(nom) if x not in STOP and len(x) > 3]
    return max(core, key=len) if core else (words(nom)[0] if words(nom) else '')


def alive(domain):
    try:
        socket.getaddrinfo(domain, 443)
    except Exception:
        return None
    for host in ('https://www.' + domain, 'https://' + domain):
        try:
            req = urllib.request.Request(host, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=8, context=CTX) as r:
                body = r.read(120000).decode('utf-8', 'ignore')
                return r.geturl(), body
        except Exception:
            continue
    return None


PARK = ('domain is for sale', 'ce domaine est a vendre', 'sedo', 'godaddy',
        'parked', 'buy this domain', 'domaine reserve', 'under construction')


def resolve(item):
    slug, nom = item
    tk = token(nom)
    for d in candidates(nom):
        got = alive(d)
        if not got:
            continue
        url, body = got
        low = strip_accents(body).lower()
        if any(p in low for p in PARK):
            continue
        if tk and tk not in low:
            continue
        m = re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I)
        titre = ' '.join(m.group(1).split())[:120] if m else ''
        return slug, {'nom': nom, 'domain': d, 'url': url, 'titre': titre}
    return slug, None


def liste(cat):
    h = open('ecosysteme.html', encoding='utf-8').read()
    m = re.search(r'id="%s".*?<ul class="firms">(.*?)</ul>' % cat, h, re.S)
    items = re.findall(r'href="/f/([a-z0-9\-]+)"[^>]*>(.*?)</a>', m.group(1), re.S)
    return [(s, re.sub(r'<[^>]+>', '', n).strip()) for s, n in items]


if __name__ == '__main__':
    cat = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    items = liste(cat)[lo:hi]
    res = {}
    with ThreadPoolExecutor(max_workers=14) as ex:
        for slug, val in ex.map(resolve, items):
            if val:
                res[slug] = val
    p = os.path.join(OUT, '%s-%s.json' % (cat, lo))
    json.dump(res, open(p, 'w'), ensure_ascii=False, indent=1)
    print('%s [%d:%d] %d/%d résolus -> %s' % (cat, lo, hi, len(res), len(items), p))
