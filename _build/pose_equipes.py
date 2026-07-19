#!/usr/bin/env python3
# Pose un bloc "Équipe dirigeante" sur les fiches f/*.html à partir d'un dict
# {nom_firme: [{"nom":..,"role":..,"linkedin"?:..}]} (JSON passé en argument).
# - N'écrase PAS une fiche qui a déjà un bloc équipe (idempotent, priorité au 1er passage).
# - Filtre les rôles non pertinents (réutilise la logique de filtre_dirigeants).
# - Insère la carte juste avant <section class="sect"> (zone "Réservé aux fiches vérifiées").
# Usage : python3 _build/pose_equipes.py _build/equipes.json [--source "recherche Exit Club"]
import json, re, sys, html as H, unicodedata, glob, os

src_json = sys.argv[1]
source_note = "recherche Exit Club"
if "--source" in sys.argv:
    source_note = sys.argv[sys.argv.index("--source") + 1]

def nk(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())

def esc(s): return H.escape(str(s), quote=False)

def keep(role):
    r = (role or "").strip().lower()
    if not r:
        return True  # rôles curés (CEO, Partner, Associé...) : on garde par défaut
    drop = ("commissaire aux comptes", "conseil de surveillance", "administrateur",
            "liquidateur", "contrôleur", "controleur", "commanditaire",
            "à l'étranger", "personne morale étrangère", "non spécifié")
    return not any(d in r for d in drop)

teams = json.load(open(src_json))

# map nom firme -> slug depuis ecosysteme.html
page = open('ecosysteme.html').read()
name2slug = {}
for m in re.finditer(r'<li><a href="/f/([^"]+)">([^<]+)</a></li>', page):
    name2slug[nk(H.unescape(m.group(2)))] = m.group(1)

def card_html(people):
    rows = []
    for p in people:
        nom = p.get("nom", "").strip()
        if not nom:
            continue
        role = p.get("role", "").strip()
        if not keep(role):
            continue
        init = "".join(w[0] for w in nom.split()[:2]).upper()
        li = f'<a href="{esc(p["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>' if p.get("linkedin") else ""
        rows.append(f'<div class="pers"><div class="ava">{esc(init)}</div><div><b>{esc(nom)}</b>'
                    f'<span>{esc(role)}</span>{li}</div></div>')
    if not rows:
        return None
    note = (f'<p style="margin-top:10px;font-size:11.5px;color:var(--faint)">Équipe identifiée par {esc(source_note)}. '
            f'<a href="mailto:louis@exit.club?subject=Fiche%20·%20correction" style="color:var(--muted)">Une correction ? Écrivez-moi</a></p>')
    return f'<div class="card"><div class="k">Équipe dirigeante</div>{"".join(rows)}{note}</div>'

posed = skipped_exists = skipped_nofiche = 0
for name, people in teams.items():
    slug = name2slug.get(nk(name))
    if not slug:
        skipped_nofiche += 1
        continue
    fp = f"f/{slug}.html"
    if not os.path.exists(fp):
        skipped_nofiche += 1
        continue
    html = open(fp).read()
    if "Équipe dirigeante" in html:
        skipped_exists += 1
        continue
    card = card_html(people)
    if not card:
        continue
    anchor = '<section class="sect">'
    if anchor not in html:
        continue
    html = html.replace(anchor, card + "\n\n  " + anchor, 1)
    open(fp, "w").write(html)
    posed += 1

print(f"équipes posées: {posed} | déjà un bloc: {skipped_exists} | fiche introuvable: {skipped_nofiche}")
