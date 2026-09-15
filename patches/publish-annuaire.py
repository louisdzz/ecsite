#!/usr/bin/env python3
# Renommer le repertoire public en L’Annuaire de l’Exit
import hashlib
import json
import re
import sys
from pathlib import Path

APOSTROPHE = r"(?:\\?['’]|&#x27;|&#39;|&apos;)"
BRAND = re.compile(r'([Ll])' + APOSTROPHE + r'Écosystème(?: de l' + APOSTROPHE + r'Exit)?')
CSS_PATH = 'assets/annuaire-navigation.css'
CSS = '''/* Navigation du nouvel Annuaire : le nom reste lisible sur mobile. */
@media(max-width:760px){
  .top{flex-wrap:wrap;gap:12px}
  .top>div{max-width:100%;flex-wrap:wrap;gap:12px!important}
  .top a,.crumb{overflow-wrap:anywhere}
  .header{gap:16px}
  .header .main-nav{min-width:0;flex:1;flex-wrap:wrap;justify-content:flex-end;gap:4px 12px}
  .header .main-nav a.current{line-height:1.35}
}
'''
CSS_LINK = '<link rel="stylesheet" href="/assets/annuaire-navigation.css?v=20260915">'

def paths(root):
    files = set(root.glob('*.html')) | set(root.glob('f/*.html')) | set(root.glob('regions/*.html'))
    files |= set(root.glob('_build/**/*.html')) | set(root.glob('_build/**/*.py'))
    files.add(root / CSS_PATH)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())

def transform(name, old):
    if name == CSS_PATH:
        return CSS.encode()
    text = old.decode('utf-8')
    # Le titre des Ligues répartit l'ancien nom entre deux éléments HTML.
    text = text.replace("L'Écosystème <span class=\"it\">de l'Exit.</span>", 'L’Annuaire <span class="it">de l’Exit.</span>')
    text = BRAND.sub(lambda m: m.group(1) + '’Annuaire de l’Exit', text)
    # Nom encodé dans l'objet du lien de retour utilisateur.
    text = text.replace('Écosystème%20de%20l%27Exit', 'Annuaire%20de%20l%27Exit')
    if name == 'ecosysteme.html':
        text = text.replace('L’annuaire de<br> <em>l’après-cession.</em>', 'L’Annuaire<br> <em>de l’Exit.</em>')
        text = text.replace('L’Annuaire de l’Exit — L’annuaire de l’après-cession', 'L’Annuaire de l’Exit — Banques, fonds et conseils')
        text = text.replace('L’annuaire public de la cession et de l’après-cession :', 'L’Annuaire de l’Exit :')
    if 'Annuaire de l’Exit' in text or ('L’Annuaire <span' in text):
        if '</head>' in text and CSS_LINK not in text:
            text = text.replace('</head>', CSS_LINK + '\n</head>', 1)
    return text.encode('utf-8')

def fingerprint(state):
    h = hashlib.sha256()
    for name, data in sorted(state.items()):
        h.update(name.encode() + b'\0')
        h.update(hashlib.sha256(data).digest() if data is not None else b'ABSENT')
    return h.hexdigest()

def state(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() if p.exists() else None for p in paths(root)}

def execute(root, expected_before, expected_after):
    before = state(root)
    current = fingerprint(before)
    if current == expected_after:
        print('Nom déjà mis à jour ; aucun changement.')
        return
    if current != expected_before:
        raise SystemExit('Le site a changé depuis la préparation : vérifier avant publication.')
    after = {name: transform(name, data) for name, data in before.items()}
    assert fingerprint(after) == expected_after
    changed = []
    for name, data in after.items():
        if data != before[name]:
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            changed.append(name)
    print(len(changed), 'fichiers renommés.')


execute(Path("."), 'b696ffbc7c3acad680d2b18d0a491fa6476a0cbd6d9cb7f8eb39bf2028f57711', '59d97d80c34b9491a240173c21ff6f4fa2bdb151eaa364100c2ba451d64e5eb5')
