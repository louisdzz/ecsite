#!/usr/bin/env python3
# Nettoie le bloc "Équipe dirigeante" des fiches gratuites f/*.html :
# ne garde que les dirigeants OPÉRATIONNELS pertinents (gérants, présidents de SAS,
# directeurs généraux, directoire) ; retire administrateurs, commissaires aux comptes,
# conseil de surveillance, "Autre", liquidateurs, représentants étrangers, etc.
# Si aucun dirigeant pertinent ne reste, la carte entière est supprimée.
# Usage : python3 _build/filtre_dirigeants.py   (depuis la racine du repo ecsite)
import re, glob

def keep(role):
    r = role.strip().lower()
    if not r:
        return False
    exec_tokens = ("gérant", "gerant", "directeur général", "directeur general",
                   "directoire", "et directeur général", "et directeur general")
    if any(t in r for t in exec_tokens):
        return True
    if r.startswith("président de sas") or r.startswith("presidente de sas"):
        return True
    if r in ("président", "presidente", "présidente", "pdg"):
        return True
    return False

CARD_RE = re.compile(
    r'<div class="card"><div class="k">Équipe dirigeante</div>.*?Une correction \? Écrivez-moi</a></p></div>')
PERS_RE = re.compile(
    r'<div class="pers"><div class="ava">([^<]*)</div><div><b>([^<]*)</b><span>([^<]*)</span></div></div>')
TAIL = ('<p style="margin-top:10px;font-size:11.5px;color:var(--faint)">'
        'Identifiée via le registre national des entreprises. '
        '<a href="mailto:louis@exit.club?subject=Fiche%20·%20correction" '
        'style="color:var(--muted)">Une correction ? Écrivez-moi</a></p></div>')

files = glob.glob('f/*.html')
touched = removed_card = kept_people = dropped_people = 0

for fp in files:
    html = open(fp).read()
    m = CARD_RE.search(html)
    if not m:
        continue
    card = m.group(0)
    pers = PERS_RE.findall(card)          # [(initiales, nom, role), ...]
    kept = [(i, n, r) for (i, n, r) in pers if keep(r)]
    dropped_people += len(pers) - len(kept)
    kept_people += len(kept)
    if not kept:
        # supprime la carte entière (avec l'espace/newline qui suit si présent)
        html = html.replace(card + "\n\n  ", "").replace(card, "")
        removed_card += 1
    else:
        blocks = "".join(
            f'<div class="pers"><div class="ava">{i}</div><div><b>{n}</b><span>{r}</span></div></div>'
            for (i, n, r) in kept)
        newcard = f'<div class="card"><div class="k">Équipe dirigeante</div>{blocks}{TAIL}'
        html = html.replace(card, newcard)
    open(fp, "w").write(html)
    touched += 1

print(f"fiches traitées: {touched} | cartes retirées (0 pertinent): {removed_card} | "
      f"dirigeants conservés: {kept_people} | supprimés: {dropped_people}")
