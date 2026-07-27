# -*- coding: utf-8 -*-
"""Pose le logo réel dans le hero des fiches et remplace le lien
"Site officiel" (recherche Google) par la vraie URL du site.
Idempotent : une fiche déjà traitée porte la classe `hero wl` ou un href réel.
Entrée : _build/logos/dir-meta.json  +  _build/domains/*.json
"""
import glob, json, os, re, urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(ROOT)

META = json.load(open('_build/logos/dir-meta.json'))
VERDICT = json.load(open('_build/domains/verdict.json'))
DOM = {}
for p in sorted(glob.glob('_build/domains/*-*.json')):
    for slug, v in json.load(open(p)).items():
        if VERDICT.get(slug, {}).get('ok'):
            DOM.setdefault(slug, v)

CSS_MARK = '.hero.wl{'
CSS = """.hero.wl{display:flex;gap:24px;align-items:flex-start}
.hero.wl>.hb{min-width:0}
.flogo{flex:none;width:88px;height:88px;border-radius:20px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#fff;border:1px solid var(--line)}
.flogo.dk{background:var(--ink);border-color:var(--ink)}
.flogo.wd{width:148px}
.flogo.xw{width:230px}
.flogo img{width:100%;height:100%;object-fit:contain;padding:10px}
.sitel{font-weight:600}
@media(max-width:760px){.hero.wl{gap:14px}.flogo{width:60px;height:60px;border-radius:14px;padding:0}.flogo.wd{width:108px}.flogo.xw{width:100%;max-width:230px}.flogo img{padding:7px}}
"""

HERO = re.compile(r'<section class="hero">(.*?)</section>', re.S)
GLINK = re.compile(
    r'<a href="https://www\.google\.com/search\?q=[^"]*"([^>]*)>Site officiel</a>')

nlogo = nsite = 0
for fp in sorted(glob.glob('f/*.html')):
    slug = os.path.basename(fp)[:-5]
    d, m = DOM.get(slug), META.get(slug)
    if not d and not m:
        continue
    h = open(fp, encoding='utf-8').read()
    orig = h

    # 1. vrai lien site, affiché comme domaine
    if d:
        lab = d['domain']
        h = GLINK.sub(lambda mo: '<a class="sitel" href="%s"%s>%s</a>'
                      % (d['url'].rstrip('/'), mo.group(1), lab), h, count=1)

    # 2. logo dans le hero
    if m and 'class="hero wl"' not in h:
        img = ('<div class="flogo%s"><img src="%s" alt="%s" loading="lazy" '
               'width="%d" height="%d"></div>'
               % ((' dk' if m['dark'] else '') + (' wd' if m['wide'] else '')
                  + (' xw' if m.get('xwide') else ''), m['f'],
                  re.sub(r'["<>]', '', m['nom'])[:80], m['w'], m['h']))
        def rep(mo):
            return '<section class="hero wl">%s<div class="hb">%s</div></section>' % (img, mo.group(1))
        h2 = HERO.sub(rep, h, count=1)
        if h2 != h:
            h = h2
            if CSS_MARK not in h:
                h = h.replace('@media(max-width:760px){.wrap{padding:0 22px}',
                              CSS + '@media(max-width:760px){.wrap{padding:0 22px}', 1)
            nlogo += 1

    # 3. schema.org : logo + site réel
    if '"sameAs"' not in h:
        extra = []
        if d:
            extra.append('"sameAs": ["%s"]' % d['url'].rstrip('/'))
        if m:
            extra.append('"logo": "https://www.exit.club%s"' % m['f'])
        if extra:
            h = re.sub(r'("@type": "Organization")', r'\1, ' + ', '.join(extra), h, count=1)

    if h != orig:
        open(fp, 'w', encoding='utf-8').write(h)
        if d and 'class="sitel"' in h:
            nsite += 1

print('logos posés : %d · liens site réels : %d' % (nlogo, nsite))
