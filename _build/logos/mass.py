# -*- coding: utf-8 -*-
"""Récupère le logo de TOUTES les institutions dont le domaine a été résolu.
Entrée  : _build/domains/*.json  {slug: {nom, domain, url, titre}}
Sortie  : /root/logoraw/<slug>.<ext>  (brut, hors repo)
          _build/logos/raw-state.json  {slug: {"nom","domain","file","src"} | null}
Reprenable : un slug déjà présent dans raw-state.json n'est pas retenté.
"""
import json, os, glob, sys, threading
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, '_build/logos')
from fetch import candidates, get, EXT  # noqa

RAW = '/root/logoraw'
os.makedirs(RAW, exist_ok=True)
STATE = '_build/logos/raw-state.json'

state = json.load(open(STATE)) if os.path.exists(STATE) else {}
lock = threading.Lock()
done = [0]


def targets():
    seen = {}
    for p in sorted(glob.glob('_build/domains/*.json')):
        for slug, v in json.load(open(p)).items():
            seen.setdefault(slug, v)
    return [(s, v) for s, v in seen.items() if s not in state]


def one(item):
    slug, v = item
    out = None
    try:
        html, ct, final = get(v['url'], timeout=12)
        html = html.decode('utf-8', 'ignore')
        for u in candidates(html, final)[:6]:
            try:
                data, ct2, _ = get(u, timeout=12)
            except Exception:
                continue
            ext = EXT.get(ct2.split(';')[0].strip().lower())
            if not ext:
                continue
            if len(data) < 400 and ext != '.svg':
                continue
            if len(data) > 1_200_000:
                continue
            f = os.path.join(RAW, slug + ext)
            open(f, 'wb').write(data)
            out = {'nom': v['nom'], 'domain': v['domain'], 'file': f, 'src': u}
            break
    except Exception:
        out = None
    with lock:
        state[slug] = out
        done[0] += 1
        if done[0] % 50 == 0:
            json.dump(state, open(STATE, 'w'), ensure_ascii=False)
            got = sum(1 for x in state.values() if x)
            print('%d traités · %d logos' % (len(state), got), flush=True)


if __name__ == '__main__':
    items = targets()
    print('%d à traiter (%d déjà en état)' % (len(items), len(state)), flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        list(ex.map(one, items))
    json.dump(state, open(STATE, 'w'), ensure_ascii=False)
    got = sum(1 for x in state.values() if x)
    print('FIN %d traités · %d logos récupérés' % (len(state), got), flush=True)
