#!/usr/bin/env python3
# Nettoie la ligne "Repères" des fiches gratuites f/*.html :
#   - retire le lien Pappers (registre) : on s'en passe.
#   - renomme "Site officiel (recherche)" -> "Site officiel".
# Idempotent. Usage : python3 _build/nettoie_liens.py
import glob, re

PAPPERS_RE = re.compile(
    r'\s*·\s*<a href="https://www\.pappers\.fr/recherche\?q=[^"]*"[^>]*>Registre & comptes \(Pappers\)</a>')

n = 0
for fp in glob.glob('f/*.html'):
    html = open(fp).read()
    if 'pappers.fr/recherche' not in html and 'Site officiel (recherche)' not in html:
        continue
    new = PAPPERS_RE.sub('', html)
    new = new.replace('>Site officiel (recherche)</a>', '>Site officiel</a>')
    if new != html:
        open(fp, 'w').write(new)
        n += 1
print(f"fiches nettoyées: {n}")
