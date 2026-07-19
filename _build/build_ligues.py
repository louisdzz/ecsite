#!/usr/bin/env python3
# Régénère la section #ligues de ecosysteme.html depuis _build/ligues-deals.json
# SOURCE DE VÉRITÉ : base Notion "Opérations — Ligues de l'Exit"
#   (data source collection://936c1991-f1b6-44f0-971d-15a84dd83581, sous la page Webapp Exit Club)
# Flux de mise à jour : la session Claude exporte la base Notion (Statut = Comptée)
#   vers _build/ligues-deals.json, puis exécute ce script, puis commit + push.
# Classement par montants cumulés conseillés (M€), puis nb d'opérations, puis récence.
# Usage : python3 _build/build_ligues.py  (depuis la racine du repo ecsite)
import json, re, html, unicodedata
from collections import defaultdict

def esc(s): return html.escape(s, quote=False)
def nk(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())

deals = json.load(open('_build/ligues-deals.json'))["deals"]
page = open('ecosysteme.html').read()

slugs = {}
for m in re.finditer(r'<li><a href="/f/([^"]+)">([^<]+)</a></li>', page):
    slugs[nk(html.unescape(m.group(2)))] = m.group(1)

SAISON_DEBUT = "2025-08-01"

def standings(kind):
    agg = defaultdict(lambda: {"meur": 0.0, "nd": 0, "saison": 0, "total": 0, "last": None, "lastcible": ""})
    for d in deals:
        for f in (d.get(kind) or []):
            a = agg[f]
            a["total"] += 1
            if d.get("valeur") is not None: a["meur"] += d["valeur"]
            else: a["nd"] += 1
            if d["date"] >= SAISON_DEBUT: a["saison"] += 1
            if a["last"] is None or d["date"] > a["last"]:
                a["last"] = d["date"]; a["lastcible"] = d["cible"]
    rows = [{"firme": f, **v} for f, v in agg.items()]
    rows.sort(key=lambda r: (-r["meur"], -r["total"], r["last"] or "", nk(r["firme"])))
    return rows

def fmt_date(d):
    y, m, _ = d.split("-")
    mois = ["", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
    return f"{mois[int(m)]} {y}"

def fmt_meur(r):
    if r["meur"] <= 0: return '<span style="color:var(--faint)">n.c.</span>'
    v = int(round(r["meur"]))
    plus = "+" if r["nd"] else ""
    return f"{v}{plus}"

def table(rows, title, sub):
    trs = []
    for i, r in enumerate(rows, 1):
        cls = ' class="pod"' if i <= 3 and r["meur"] > 0 else ""
        s = slugs.get(nk(r["firme"]))
        cell = f'<a href="/f/{s}">{esc(r["firme"])}</a>' if s else esc(r["firme"])
        trs.append(f'      <tr{cls}><td class="pos">{i}</td><td class="team">{cell}</td><td class="num big">{fmt_meur(r)}</td><td class="num">{r["total"]}</td><td class="num">{r["saison"]}</td><td class="lastop">{esc(r["lastcible"])} <span>· {fmt_date(r["last"])}</span></td></tr>')
    return f'''
  <section class="league-t">
    <div class="lh"><h2 class="disp">{esc(title)}</h2><p class="lsub">{esc(sub)}</p></div>
    <table>
      <thead><tr><th>#</th><th>Firme</th><th title="Montants cumulés des opérations à valeur publiée">M€ conseillés</th><th title="Opérations depuis 2020">Opé.</th><th title="Opérations saison 2025-26">25-26</th><th>Dernière opération</th></tr></thead>
      <tbody>
{chr(10).join(trs)}
      </tbody>
    </table>
  </section>'''

conseils = standings("conseils")
avocats = standings("avocats")
nb = len(deals)

fragment = f'''<section class="league" id="ligues">
    <div class="ah"><div><p class="eyebrow2">Saison 2025-2026 · le championnat des conseils</p><h2 class="disp2">Les Ligues de l'Exit.</h2></div></div>
    <div class="metho">
      <p><b>Méthodologie.</b> Une opération = une cession d'entreprise française annoncée publiquement et documentée par l'Exit Club ({nb} opérations suivies). Le classement se fait au montant cumulé des opérations conseillées côté cédant (valorisation ou montant publiés ; quand seule une fourchette est publiée, on retient son point médian), puis au nombre d'opérations. Le signe + indique des opérations supplémentaires à montant non communiqué ; n.c. = aucun montant publié. Le périmètre s'élargit en continu. <b>Une opération manque ?</b> <a href="mailto:louis@exit.club?subject=Ligues%20·%20opération%20à%20ajouter" style="color:var(--accent)">Signalez-la</a>, elle sera vérifiée puis comptée.</p>
    </div>
{table(conseils, "La Ligue des Conseils M&A", "Banques d'affaires et boutiques M&A citées aux côtés des cédants")}
{table(avocats, "La Ligue des Avocats", "Cabinets cités sur la structuration juridique des cessions")}
  </section>'''

start = page.index('<section class="league" id="ligues">')
end = page.index('<div class="mid">', start)
page = page[:start] + fragment + "\n\n  " + page[end:]
# La classe interne .league devient .league-t pour ne pas hériter du scroll-margin, même CSS
page = page.replace(".league-t", ".league-t")
open('ecosysteme.html','w').write(page)
print(f"ligues OK — {nb} deals, {len(conseils)} conseils (leader: {conseils[0]['firme']}), {len(avocats)} avocats")
