#!/usr/bin/env python3
# Génère une fiche VÉRIFIÉE (débloquée) depuis _build/verified/<slug>.json
# Usage : python3 _build/build_fiche_verifiee.py <slug> [--apercu]
#   mode normal : écrit f/<slug>.html (remplace la fiche verrouillée)
#   mode --apercu : écrit f/apercu-<slug>.html (noindex, bandeau "aperçu", non lié)
# Schéma JSON : {nom, categorie_label, categorie_id, annee, description (2-3 phrases),
#   expertises [..], equipe [{nom, role, linkedin?}], site?, calendly?, onepager?,
#   actus [{date "AAAA-MM", texte}], initiales?}
import json, sys, html, re, unicodedata

slug = sys.argv[1]
apercu = "--apercu" in sys.argv
d = json.load(open(f"_build/verified/{slug}.json"))
def esc(s): return html.escape(str(s), quote=False)

def nk(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())

# Stats Ligues éventuelles
try:
    deals = json.load(open('_build/ligues-deals.json'))["deals"]
except FileNotFoundError:
    deals = []
ops = [x for x in deals if nk(d["nom"]) in [nk(f) for f in (x.get("conseils") or []) + (x.get("avocats") or [])]]

init = d.get("initiales") or "".join(w[0] for w in d["nom"].split()[:2]).upper()
annee = d.get("annee", 2026)

equipe = "".join(
    f'<div class="pers"><div class="ava">{esc("".join(w[0] for w in p["nom"].split()[:2]).upper())}</div>'
    f'<div><b>{esc(p["nom"])}</b><span>{esc(p["role"])}</span>'
    + (f'<a href="{esc(p["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>' if p.get("linkedin") else "")
    + '</div></div>'
    for p in d.get("equipe", []))

expertises = "".join(f'<span class="xp">{esc(x)}</span>' for x in d.get("expertises", []))

def fmtm(am):
    a, m = am.split("-")[:2]
    mois = ["","janv.","févr.","mars","avr.","mai","juin","juil.","août","sept.","oct.","nov.","déc."]
    return f"{mois[int(m)]} {a}"

actus = "".join(f'<div class="arow"><span class="adate">{fmtm(a["date"])}</span><span>{esc(a["texte"])}</span></div>'
                for a in d.get("actus", []))
if ops:
    tot = sum(x["valeur"] for x in ops if x.get("valeur"))
    actus = f'<div class="arow"><span class="adate">Ligues</span><span><b>{len(ops)} opération{"s" if len(ops)>1 else ""}</b> conseillée{"s" if len(ops)>1 else ""} côté cédant{f" · {int(tot)}+ M€" if tot else ""} · <a href="/ecosysteme#ligues">voir le classement →</a></span></div>' + actus

banner = ''
robots = ''
if apercu:
    robots = '<meta name="robots" content="noindex, nofollow">'
    banner = ('<div style="background:#8A6D1D;color:#FFF;padding:10px 16px;text-align:center;font-size:13px;font-weight:600">'
              f'Aperçu préparé pour {esc(d["nom"])} · cette fiche n\'est pas publiée · elle attend votre validation</div>')
demo_note = ''
if d.get("demo"):
    demo_note = ('<div style="background:var(--ink);color:var(--paper);padding:10px 16px;text-align:center;font-size:13px">'
                 'Fiche de démonstration · firme fictive · <a href="/referencement?demande=verifier" style="color:#D9C68A">obtenir la vôtre →</a></div>')

liens = []
if d.get("site"): liens.append(f'<a class="btn2" href="{esc(d["site"])}" target="_blank" rel="noopener">Site officiel</a>')
if d.get("onepager"): liens.append(f'<a class="btn2" href="{esc(d["onepager"])}" target="_blank" rel="noopener">One-pager (PDF)</a>')
rdv = f'<a class="btnp" href="{esc(d["calendly"])}" target="_blank" rel="noopener">Prendre rendez-vous</a>' if d.get("calendly") else ''

page = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(d["nom"])} · Fiche vérifiée {annee} | L'Écosystème de l'Exit</title>
<meta name="description" content="{esc(d["description"][:150])}">
{robots}
<link rel="canonical" href="https://www.exit.club/f/{slug}">
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300;1,9..144,400&family=Inter:wght@400;500;600&display=swap');
:root{{--paper:#F7F3E4;--ink:#2A351A;--accent:#47621E;--muted:#6F7854;--faint:#98A07E;--line:#DDD6BC;--card:#FCFAF0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font-family:'Inter',Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}}
.disp{{font-family:'Fraunces',Georgia,serif;font-variation-settings:"opsz" 144;font-weight:300;letter-spacing:-.01em}}
.wrap{{max-width:860px;margin:0 auto;padding:0 40px}}
.top{{display:flex;align-items:center;justify-content:space-between;padding:26px 0}}
.mark{{font-family:'Fraunces',Georgia,serif;font-size:21px}}.mark i{{font-style:italic}}.mark b{{font-weight:600}}
.crumb{{font-size:13px;color:var(--muted);margin:14px 0 0}}
.crumb a{{color:var(--muted);text-decoration:none;border-bottom:1px dotted var(--line)}}
.hero{{padding:26px 0 8px;display:flex;gap:22px;align-items:center}}
.logo{{flex:none;width:84px;height:84px;border-radius:20px;background:var(--ink);color:var(--paper);display:flex;align-items:center;justify-content:center;font-family:'Fraunces',Georgia,serif;font-size:32px}}
.vbadge{{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#FFF;background:var(--accent);border-radius:999px;padding:5px 12px;margin-bottom:8px}}
h1.disp{{font-size:42px;line-height:1.02}}
.tagl{{margin-top:6px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:600}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 24px;margin:20px 0 0}}
.card .k{{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--faint);font-weight:600;margin-bottom:10px}}
.card p{{font-size:14.5px;color:var(--muted);line-height:1.65}}
.xp{{display:inline-block;font-size:12.5px;font-weight:600;color:var(--accent);border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:5px 12px;margin:4px 6px 0 0}}
.pers{{display:flex;gap:12px;align-items:center;padding:10px 0;border-bottom:1px solid #EFEBDB}}
.pers:last-child{{border-bottom:0}}
.ava{{flex:none;width:42px;height:42px;border-radius:50%;background:#E7E2D0;color:var(--ink);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600}}
.pers b{{display:block;font-size:14px}}
.pers span{{display:block;font-size:12.5px;color:var(--muted)}}
.pers a{{font-size:12px;color:var(--accent);text-decoration:none}}
.arow{{display:flex;gap:14px;align-items:baseline;padding:9px 0;border-bottom:1px solid #EFEBDB;font-size:14px;color:var(--muted)}}
.arow:last-child{{border-bottom:0}}
.adate{{flex:none;width:78px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}}
.arow a{{color:var(--accent)}}
.cta{{margin-top:24px;display:flex;gap:12px;flex-wrap:wrap}}
.btnp{{font-size:14.5px;font-weight:600;padding:14px 24px;border-radius:999px;background:var(--ink);color:var(--paper);text-decoration:none}}
.btn2{{font-size:14px;font-weight:600;padding:13px 20px;border-radius:999px;border:1px solid var(--line);color:var(--ink);text-decoration:none}}
.foot{{border-top:1px solid var(--line);margin-top:48px;padding:22px 0 40px;font-size:12px;color:var(--faint);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}}
.foot a{{color:var(--muted);text-decoration:none}}
@media(max-width:760px){{.wrap{{padding:0 22px}}h1.disp{{font-size:32px}}.hero{{flex-direction:column;align-items:flex-start}}}}
</style>
</head>
<body>
{banner}{demo_note}
<div class="wrap">
  <div class="top">
    <a class="mark" href="/" style="text-decoration:none;color:var(--ink)"><i>exit</i><b>.club</b></a>
    <div style="display:flex;align-items:center;gap:22px">
      <a href="/ecosysteme" style="font-size:13.5px;color:var(--muted);text-decoration:none">L'Écosystème</a>
      <a href="https://tally.so/r/wADNZN" target="_blank" rel="noopener" style="font-size:13px;font-weight:600;color:var(--paper);background:var(--accent);padding:9px 16px;border-radius:999px;text-decoration:none">Rejoindre</a>
    </div>
  </div>
  <div class="crumb"><a href="/ecosysteme">L'Écosystème de l'Exit</a> · <a href="/ecosysteme#{d["categorie_id"]}">{esc(d["categorie_label"])}</a></div>
  <section class="hero">
    <div class="logo">{esc(init)}</div>
    <div>
      <span class="vbadge">✓ Fiche vérifiée {annee}</span>
      <h1 class="disp">{esc(d["nom"])}</h1>
      <div class="tagl">{esc(d["categorie_label"])}</div>
    </div>
  </section>
  <div class="card"><div class="k">À propos</div><p>{esc(d["description"])}</p>
  <p style="margin-top:12px">{expertises}</p></div>
  <div class="card"><div class="k">L'équipe</div>{equipe}</div>
  <div class="card"><div class="k">Actualités & opérations</div>{actus or '<p>Aucune actualité publiée pour le moment.</p>'}</div>
  <div class="cta">{rdv}{"".join(liens)}</div>
  <p style="margin-top:30px;font-size:12px;color:var(--faint);line-height:1.5">Fiche vérifiée : contenu fourni et validé par la firme, qualifiée par l'équipe de l'Exit Club. La vérification est un engagement commercial : elle n'influence ni la présence dans l'annuaire, ni l'ordre d'affichage, ni les Ligues.</p>
  <div class="foot">
    <div>Exit Club · L'Écosystème de l'Exit</div>
    <div><a href="/referencement">Se référencer</a> · <a href="mailto:louis@exit.club?subject=Fiche%20{slug}">Contact</a></div>
  </div>
</div>
</body>
</html>
'''
out = f"f/apercu-{slug}.html" if apercu else f"f/{slug}.html"
open(out, "w").write(page)
print("écrit:", out)
