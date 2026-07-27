# -*- coding: utf-8 -*-
"""Réordonne les catégories de l'Écosystème + déplace la Ligue des CGP juste
au-dessus de la catégorie CGP (elle ne doit plus être le premier classement lu).
Idempotent : relancer ne change rien si l'ordre est déjà bon.
"""
import re, sys, io

F = 'ecosysteme.html'
ORDER = ['banques-affaires', 'boutiques-ma', 'mfo', 'banques-privees',
         'avocats', 'experts-comptables', 'notaires', 'cgp',
         'assurance-vie-lux', 'fonds-pe', 'fonds-dette', 'fonds-vc',
         'secondaire']

H = open(F, encoding='utf-8').read()

# ---------- 1. extraction des blocs catégorie ----------
starts = [(m.group(1), m.start()) for m in
          re.finditer(r'<section class="cat" id="([^"]+)"', H)]
assert starts, 'aucune section cat'
cats_open = H.find('<div class="cats">')
assert cats_open != -1 and cats_open < starts[0][1]
head = H[:starts[0][1]]

# fin du dernier bloc = dernier </section> avant le </div> qui ferme .cats
tail_start = H.index('</section>', starts[-1][1]) + len('</section>')
tail = H[tail_start:]

blocks = {}
for i, (slug, off) in enumerate(starts):
    end = starts[i + 1][1] if i + 1 < len(starts) else tail_start
    b = H[off:end]
    assert b.count('<section') == 1 and b.count('</section>') == 1, slug
    blocks[slug] = b

missing = [s for s in blocks if s not in ORDER]
assert not missing, 'catégories non prévues dans ORDER: %s' % missing
seq = [s for s in ORDER if s in blocks]
assert len(seq) == len(blocks)

new_cats = ''.join(blocks[s] for s in seq)

# ---------- 2. déplacement du bloc Ligue des CGP ----------
LS, LE = '<!-- LIGUE-CGP:START -->', '<!-- LIGUE-CGP:END -->'
a, b = head.find(LS), head.find(LE)
ligue = ''
if a != -1 and b != -1:
    ligue = head[a:b + len(LE)]
    head = head[:a].rstrip() + '\n\n' + head[b + len(LE):].lstrip('\n')
    head = re.sub(r'\n{3,}', '\n\n', head)
else:  # déjà déplacé
    a2 = new_cats.find(LS)
    assert a2 != -1, 'bloc Ligue introuvable'
    b2 = new_cats.find(LE)
    ligue = new_cats[a2:b2 + len(LE)]
    new_cats = new_cats[:a2] + new_cats[b2 + len(LE):]

if 'cgp' in blocks:
    anchor = blocks['cgp']
    i = new_cats.find(anchor)
    assert i != -1
    new_cats = new_cats[:i] + ligue + '\n\n  ' + new_cats[i:]

# ---------- 3. nav d'ancres dans le même ordre ----------
jm = re.search(r'<div class="jump">(.*?)</div>', head, re.S)
assert jm, 'nav .jump introuvable'
links = {m.group(1): m.group(0) for m in
         re.finditer(r'<a href="#([a-z\-]+)">.*?</a>', jm.group(1), re.S)}
assert links, 'aucun lien dans .jump'
newjump = '<div class="jump">' + ' '.join(
    links[s] for s in ORDER if s in links) + '</div>'
head = head[:jm.start()] + newjump + head[jm.end():]

out = head + new_cats + tail
assert out.count('<section class="cat"') == len(blocks)
assert out.count(LS) == 1 and out.count(LE) == 1
open(F, 'w', encoding='utf-8').write(out)
print('ordre appliqué :', ' > '.join(seq))
print('Ligue des CGP repositionnée juste avant la catégorie CGP')
print('nav .jump :', len([s for s in ORDER if s in links]), 'liens')
