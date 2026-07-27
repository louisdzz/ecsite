# -*- coding: utf-8 -*-
"""Ajoute sur chaque fiche de gestion privée sa ligne régionale.

Un CGP qui ouvre sa fiche doit voir, en une ligne, combien de confrères sont
recensés dans sa région et pouvoir y aller. C'est le lien qui transforme une
fiche isolée en comparaison.

Idempotent : délimiteurs RLINE:START / RLINE:END et /*RLINE_CSS_*/.
"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)

GEO = json.load(open('_build/cgp-geo.json'))
for v in GEO.values():
    d, cp = v.get('dep'), v.get('cp') or ''
    if d in ('97', '98') and len(cp) >= 3 and cp[:3].isdigit():
        v['dep'] = cp[:3]
IDX = json.load(open('_build/regions/index.json'))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa : réutilise REGIONS, slugify, ville, e

DEP2R = {}
for nom, prep, deps in gen.REGIONS:
    sl = gen.slugify(nom)
    if sl in IDX:
        for d in deps.split():
            DEP2R[d] = sl

CSS = """/*RLINE_CSS_START*/
.rline{margin:-6px 0 26px;padding:11px 15px;border:1px solid var(--line);border-radius:9px;
background:var(--card);font-size:13px;color:var(--muted)}
.rline b{color:var(--ink);font-weight:600}
.rline a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--line)}
.rline a:hover{border-color:var(--accent)}
/*RLINE_CSS_END*/"""

HERO = re.compile(r'<section class="hero[^"]*">.*?</section>', re.S)
n = 0
for slug, v in GEO.items():
    r = DEP2R.get(v.get('dep'))
    p = 'f/%s.html' % slug
    if not r or not os.path.exists(p):
        continue
    inf = IDX[r]
    vil = gen.ville(v.get('commune'))
    ou = ('Cabinet à <b>%s</b>' % gen.e(vil)) if vil else 'Cabinet %s' % gen.e(inf['prep'])
    line = ('<!--RLINE:START-->\n  <p class="rline">%s · <a href="/regions/%s">'
            'Voir les %d cabinets de gestion de patrimoine %s →</a></p><!--RLINE:END-->'
            % (ou, r, inf['n'], gen.e(inf['prep'])))
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'\s*<!--RLINE:START-->.*?<!--RLINE:END-->', '', s, flags=re.S)
    s = re.sub(r'/\*RLINE_CSS_START\*/.*?/\*RLINE_CSS_END\*/\n?', '', s, flags=re.S)
    m = HERO.search(s)
    if not m or '</style>' not in s:
        continue
    s = s[:m.end()] + '\n\n  ' + line + s[m.end():]
    s = s.replace('\n</style>', '\n' + CSS + '\n</style>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    n += 1

print('%d fiches enrichies de leur ligne régionale' % n)
