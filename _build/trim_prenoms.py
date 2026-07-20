#!/usr/bin/env python3
# Réduit les noms de dirigeants "Prénom1 Prénom2 Prénom3 NOM" -> "Prénom1 Nom"
# dans les blocs <div class="pers">...<b>NOM COMPLET</b>. Ne touche qu'aux fiches
# ayant une "Équipe dirigeante". Corrige aussi la casse des particules.
import re, glob

PARTICULES = {"de","du","des","le","la","van","von","di","da","dos","del","al","ben","el"}

def trim(nom):
    nom = nom.strip()
    toks = nom.split()
    if len(toks) <= 2:
        return nom
    # Cas particule dans le nom de famille : on garde prénom1 + tout à partir de la 1re particule
    for i in range(1, len(toks)):
        if toks[i].lower() in PARTICULES:
            return toks[0] + " " + " ".join(toks[i:])
    # Nom composé à trait d'union détecté sur le dernier token -> prénom1 + dernier
    # Heuristique standard : premier prénom + dernier mot (le patronyme)
    return toks[0] + " " + toks[-1]

PERS_B = re.compile(r'(<div class="pers"><div class="ava">)([^<]*)(</div><div><b>)([^<]+)(</b>)')

def av_init(nom):
    return "".join(w[0] for w in nom.split()[:2]).upper()

changed = 0
for fp in glob.glob('f/*.html'):
    h = open(fp).read()
    if "Équipe dirigeante" not in h:
        continue
    def repl(m):
        full = m.group(4)
        short = trim(full)
        if short == full:
            return m.group(0)
        return m.group(1) + av_init(short) + m.group(3) + short + m.group(5)
    h2 = PERS_B.sub(repl, h)
    if h2 != h:
        open(fp,'w').write(h2); changed += 1
print("fiches nettoyées:", changed)
