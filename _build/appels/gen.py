# -*- coding: utf-8 -*-
import json, html, re
S = json.load(open('_build/enrich/salve1.json'))
by = {c['nom'].split(' (')[0]: c for c in S}

# accroche = première phrase à dire, construite à partir de la preuve publique
ACC = {
 "Hexa Patrimoine":"Vous êtes le seul cabinet de la région à écrire noir sur blanc sur le 150-0 B ter et l'obligation de remploi. Nos membres, ce sont exactement les gens qui ont ces 36 mois devant eux.",
 "Treeefle Gestion Privée":"Votre page d'accueil dit « vous avez construit, vendu ou repris une entreprise ». C'est mot pour mot notre base de membres, sur votre segment 1 à 15 M€.",
 "Colbert Patrimoine Finance":"Vous avez monté Colbert Fusac en 2024 et vous visez le milliard. Le carburant, c'est du deal flow de cédants. On est assis dessus.",
 "Attitude Patrimoine":"Vous citez le report d'imposition et les 70 % à 36 mois sur votre page dirigeant. Nos membres sont dans ce compte à rebours.",
 "Tanguy Finances":"Votre article apport-cession de mars 2025. 400 M€, 4 000 clients, et vous êtes indépendants : la décision se prend chez vous, à Rennes.",
 "Version Patrimoine":"Vous êtes vice-président de la CNCGP et vous n'êtes rattaché à aucun réseau. Je veux votre lecture avant d'ouvrir la Nouvelle-Aquitaine.",
 "Office Experts Patrimoine":"Président CNCGP Languedoc-Roussillon, Trophée CF News Sud-Ouest en janvier. Je veux l'Occitanie représentée par vous, pas par un réseau.",
 "FINARENA Gestion Privée":"Vous avez une page « Transmettre son entreprise » et vous signez seul. Deux raisons pour lesquelles cet appel peut se conclure aujourd'hui.",
 "Bonjour Patrimoine":"Vous éditez gestiondepatrimoine.com, donc je n'ai pas à vous expliquer ce que vaut une audience qualifiée. La nôtre a vendu.",
 "Octopus Patrimoine":"Vous travaillez avec 123 Cession pour trouver des cédants. Nous, on a déjà les cédants, après la vente, avec le cash sur le compte.",
 "Verum Gestion Privée":"Vous rachetez des cabinets, vous ne vous faites pas racheter. Les gens qui vendent leur boîte, c'est notre matière première.",
 "Massalia Finance":"150 M€ pour 850 familles à Marseille, et une page sur la cession d'entreprise. Combien de dirigeants cédants vous êtes-vous vu passer sous le nez ?",
 "Fipad Conseil":"Groupe régional depuis 1993, 1 500 familles, patrimoine des dirigeants. Vous n'avez rien de public sur la cession : c'est justement le sujet.",
 "OP Finances":"30 ans, 850 clients, indépendant. Sur le Nord, la question c'est qui capte les dirigeants qui viennent de vendre.",
 "Boreal Patrimoine":"Vous avez un associé dédié aux personnes morales. Je veux lui parler des dirigeants qui ont déjà signé leur cession.",
 "ELITE Patrimoine":"Vous gérez le patrimoine de sportifs et de talents. Le parallèle est direct : un exit, c'est la même mécanique d'argent qui tombe d'un coup.",
 "Family and Office":"Vous écrivez « de l'analyse des motifs de transmission à la gestion de l'après-cession ». L'après-cession, c'est là qu'on vit.",
 "Master Conseil":"Vous êtes indépendants à Aix depuis longtemps. Ma question : qu'est-ce que vous faites aujourd'hui du dirigeant qui vient d'encaisser 8 M€ ?",
 "Novalfi Conseil":"11 bureaux, 6 juristes-fiscalistes en interne, une société de gestion agréée AMF. Vous avez la machine, il vous manque le flux.",
 "Office Patrimoine":"Vous avez repris Génération & Patrimoine et vous signez seuls. Sur la Somme, personne ne s'occupe des dirigeants qui ont vendu.",
 "Fidere Conseil":"75 M€, 1 000 clients, une clientèle de chefs d'entreprise, et rien de public sur la cession. C'est un angle mort qui se comble en un appel.",
}
C2 = {
 "Colbert Patrimoine Finance":"NE PAS demander Catherine Bize ni William David",
 "Tanguy Finances":"Laurence Tanguy, co-dirigeante (les deux signent)",
 "Version Patrimoine":"Pierre Bordas, Pierre Laurent (3 co-gérants, décision collégiale)",
 "Office Experts Patrimoine":"Jérémy Combettes, DG associé",
 "Bonjour Patrimoine":"Philippe Moussaud, Managing Partner",
 "Treeefle Gestion Privée":"Bastien Lequien",
 "Hexa Patrimoine":"NE PAS demander Excellis, c'est Hexa Patrimoine",
 "Verum Gestion Privée":"entité juridique D.D.A, demander VERUM",
 "Massalia Finance":"Gérard Degrutere, Directeur CGP",
 "OP Finances":"demander « Optimisation Patrimoine », Hélène Marin directrice de cabinet",
 "Boreal Patrimoine":"Alexis Masurel, personnes morales : c'est LUI",
 "ELITE Patrimoine":"Kevin Beesley, associé gérant",
 "Family and Office":"si le fixe ne répond pas : 06 77 76 20 96",
 "Master Conseil":"Stéphane Voss, associé gérant",
 "Novalfi Conseil":"Christophe Veran, pôle gestion de patrimoine",
 "Office Patrimoine":"Jean-Benoît Rigaux",
 "Fidere Conseil":None,
 "Octopus Patrimoine":None,
 "FINARENA Gestion Privée":"2e bureau Guérande 02 55 05 01 85",
 "Attitude Patrimoine":None,
 "Fipad Conseil":"site SSL cassé, email non confirmé : téléphone uniquement",
}
PRIX = {"Colbert Patrimoine Finance":3900,"Tanguy Finances":1900,"Massalia Finance":1900,"Inovea Finance":1900}
REG = {
 "Bretagne / Pays de la Loire":["Tanguy Finances","Attitude Patrimoine","Colbert Patrimoine Finance","FINARENA Gestion Privée","Octopus Patrimoine","Fidere Conseil"],
 "Auvergne-Rhône-Alpes":["Hexa Patrimoine","Verum Gestion Privée"],
 "Hauts-de-France":["Treeefle Gestion Privée","Boreal Patrimoine","OP Finances","Office Patrimoine"],
 "Nouvelle-Aquitaine / Occitanie":["Version Patrimoine","Bonjour Patrimoine","Office Experts Patrimoine","ELITE Patrimoine"],
 "PACA / Bourgogne-Franche-Comté":["Massalia Finance","Novalfi Conseil","Master Conseil","Family and Office","Fipad Conseil"],
}
def tr(a):
    if not a: return "à qualifier", 990
    return a
rows=[]
for reg, noms in REG.items():
    for n in noms:
        c = by.get(n) or by.get([k for k in by if k.startswith(n)][0])
        rows.append((reg,n,c))

def esc(s): return html.escape(s or '')
out=[]
out.append("""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>Feuille d'appel — CGP province — Salve 1</title>
<style>
@page{size:A4;margin:14mm 12mm}
*{box-sizing:border-box}
body{font:11pt/1.35 "Helvetica Neue",Helvetica,Arial,sans-serif;color:#111;margin:0;padding:24px;max-width:900px;margin:0 auto;-webkit-font-smoothing:antialiased}
h1{font-size:15pt;letter-spacing:.06em;text-transform:uppercase;margin:0 0 2px;font-weight:700}
.sub{font-size:9pt;color:#666;margin:0 0 22px;letter-spacing:.02em}
h2{font-size:9pt;letter-spacing:.14em;text-transform:uppercase;color:#000;border-bottom:1.5px solid #000;padding-bottom:4px;margin:26px 0 10px;font-weight:700;page-break-after:avoid}
.c{border:1px solid #d4d4d4;border-left:3px solid #111;padding:9px 11px;margin:0 0 8px;page-break-inside:avoid}
.c.b{border-left-color:#bbb}
.hd{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.nom{font-weight:700;font-size:11.5pt}
.tel{font-variant-numeric:tabular-nums;font-weight:700;font-size:12.5pt;letter-spacing:.01em;white-space:nowrap}
.who{font-size:9.5pt;margin:3px 0 0}
.who b{font-weight:600}
.meta{font-size:8.5pt;color:#666;margin:2px 0 0}
.acc{font-size:9.5pt;margin:6px 0 0;padding:6px 8px;background:#f5f5f3;border-left:2px solid #999}
.acc:before{content:"→ ";color:#999}
.warn{font-size:8.5pt;color:#8a4b00;margin:4px 0 0}
.notes{border-bottom:1px dotted #bbb;height:15px;margin:9px 0 0}
.notes2{border-bottom:1px dotted #bbb;height:15px}
.box{display:inline-block;width:11px;height:11px;border:1.5px solid #111;vertical-align:-1px;margin-right:6px}
.px{font-size:8.5pt;color:#111;border:1px solid #111;padding:0 4px;font-weight:700;white-space:nowrap}
.foot{margin-top:30px;font-size:8.5pt;color:#666;border-top:1px solid #ccc;padding-top:8px}
.reg-note{font-size:8.5pt;color:#666;margin:-6px 0 10px;page-break-after:avoid;break-after:avoid}
@media print{body{padding:0}.c{border-color:#999}}
</style></head><body>
<h1>Feuille d'appel — petits CGP de province</h1>
<p class="sub">Salve 1 · 21 cabinets qualifiés CIF · 11 priorité A puis 10 priorité B · groupés par région pour enchaîner · L'Écosystème de l'Exit 2026</p>
""")
cur=None
prio=[r for r in rows if r[2]['verdict']=='APPELER_PRIORITE_A']
sec=[r for r in rows if r[2]['verdict']=='APPELER']
def block(title, items, cls):
    out.append(f'<h2>{title}</h2>')
    cur=None
    for reg,n,c in items:
        if reg!=cur:
            out.append(f'<div class="reg-note"><b>{esc(reg)}</b></div>'); cur=reg
        aum=c.get('aum_publie'); prix=PRIX.get(n,990)
        ville=re.sub(r'^.*?(\d{5}\s+[^(,]+).*$',r'\1',c['adresse']).strip()
        out.append('<div class="c %s">'%cls)
        out.append(f'<div class="hd"><span class="nom"><span class="box"></span>{esc(n)}</span><span class="tel">{esc(c["tel"])}</span></div>')
        out.append(f'<div class="who">Demander <b>{esc(c["decideur"])}</b> — {esc(c["decideur_role"])}</div>')
        m=[ville]
        if aum: m.append(esc(aum))
        m.append(f'cible {prix} €')
        if c.get('email_publie'): m.append(esc(c['email_publie']))
        out.append('<div class="meta">%s</div>'%' · '.join(m))
        out.append(f'<div class="acc">{esc(ACC.get(n,""))}</div>')
        if C2.get(n): out.append(f'<div class="warn">⚑ {esc(C2[n])}</div>')
        out.append('<div class="notes"></div><div class="notes2"></div>')
        out.append('</div>')
block('Priorité A — appeler cette semaine', prio, '')
block('Priorité B — deuxième passe', sec, 'b')
out.append("""<div class="foot">
Tarif : 990 € sous 100 M€ · 1 900 € de 100 à 500 M€ · 3 900 € de 500 M€ à 2 Md€ · 6 900 € au-delà.<br>
Chaque cabinet ci-dessus a son statut CIF vérifié à l'ORIAS. 11 noms de la liste d'origine ont été écartés (courtiers en crédit, agences immobilières, holdings) et ne figurent pas ici.<br>
Levier de place : Henry Coudé est DG du Cercle France Patrimoine · Yves Mazin est vice-président de la CNCGP · Cyrille Brengues est président CNCGP Languedoc-Roussillon.
</div></body></html>""")
open('_build/appels/feuille-appel-salve1.html','w').write('\n'.join(out))
print('ok', len(prio), len(sec))
