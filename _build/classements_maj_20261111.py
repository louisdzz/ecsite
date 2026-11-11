#!/usr/bin/env python3
"""Classements, arrêté au 11 novembre 2026, version A (corrections seules de la page Notion « Classements à publier »,
sans le rattrapage janvier-octobre). Ajoute maisons, personnes et opérations à assets/annuaire/profils.js, puis
régénère par le calcul les lignes concernées de assets/annuaire/classements.js (compteur = réalisations distinctes
dans la période ; annonces à part ; rang calculé à l'affichage). Contrôle : avant modification, le calcul doit
redonner les compteurs en ligne des 52 personnes. Idempotent.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://annuaire-exit-classement-maquette.louisdeb.chatgpt.site/assets/"
FIN = "2026-11-11"; CHK = "11 novembre 2026"
pp = os.path.join(ROOT, "assets/annuaire/profils.js"); pc = os.path.join(ROOT, "assets/annuaire/classements.js")
t = open(pp, encoding="utf-8").read(); lines = t.split("\n"); L = lines[2]
dec = json.JSONDecoder()
def load(name, s):
    i = s.index(name + "=") + len(name) + 1; v, j = dec.raw_decode(s[i:]); return v, i, i + j
houses, hi, hj = load("houses", L); people, pi, pj = load("people", L); deals, di, dj = load("deals", L)
def calc(p, fin):
    full = lambda d: d + "-01" if len(d) == 7 else d
    out = []
    for d in deals:
        if not ("2026-01-01" <= full(d["date"]) <= fin): continue
        debt = d.get("category") == "financing"
        if (p["profession"] == "debt") != debt: continue
        ps = d.get("participants") or [{"pid": d.get("pid")}]
        if any(x["pid"] == p["id"] and (p["profession"] != "tax" or x.get("practice") == "tax") and (p["profession"] != "debt" or x.get("practice") == "debt") for x in ps):
            out.append(d)
    return out
c = open(pc, encoding="utf-8").read(); ei = c.index("const entries=") + len("const entries="); entries, ej = dec.raw_decode(c[ei:]); ej += ei
byid = {p["id"]: p for p in people}
if not any(d["id"] == "n10c-dataouest-202611" for d in deals):
    for e in entries:  # contrôle de cohérence sur l'état en ligne
        ds = calc(byid[e["id"]], "2026-11-06")
        assert (sum(d["state"] == "closed" for d in ds), sum(d["state"] != "closed" for d in ds)) == (e["closed"], e["announced"]), e["id"]
    print("contrôle : le calcul redonne les 52 compteurs en ligne")
H = [{"id": "joffe", "name": "Joffe", "full": "Joffe & Associés", "logo": None, "color": "#2f4858"}, {"id": "gramond", "name": "Gramond", "full": "Gramond & Associés", "logo": None, "color": "#4a4e69"}]
P = [
 dict(id="chambeau", name="Yves Chambeau", house="inextenso", role="Senior Advisor", sector="IT & tech", type="M&A", profession="bankers", source="https://finance.inextenso.fr/equipe/yves-chambeau/"),
 dict(id="dombre", name="Antoine Dombre", house="inextenso", role="Associate", sector="Fusions-acquisitions", type="M&A", profession="bankers", source="https://finance.inextenso.fr/equipe/antoine-dombre/"),
 dict(id="patinier", name="Adèle Patinier", house="gide", role="Avocate", sector="Fusions-acquisitions", type="Avocat M&A", profession="lawyers", source="https://www.gide.com/avocats/adele-patinier/"),
 dict(id="degremont", name="Aymeric Dégremont", house="joffe", role="Avocat associé", sector="Corporate, fusions-acquisitions & private equity", type="Avocat M&A", profession="lawyers", source="https://www.joffeassocies.com/avocat/aymeric-degremont/"),
 dict(id="giuliani", name="Guillaume Giuliani", house="moncey", role="Avocat associé", sector="Fusions-acquisitions & private equity", type="Avocat M&A", profession="lawyers", source="https://www.monceyavocats.com/fr/equipe/guillaume-giuliani"),
 dict(id="saintjulien", name="Victoria Saint-Julien", house="moncey", role="Avocate", sector="Fusions-acquisitions & private equity", type="Avocat M&A", profession="lawyers", source="https://www.monceyavocats.com/fr/equipe/victoria-saint-julien"),
 dict(id="xgramond", name="Xavier Gramond", house="gramond", role="Avocat", sector="Corporate & M&A", type="Avocat M&A", profession="lawyers", source="https://gramond-avocats.com/portfolio-item/xavier-gramond/"),
 dict(id="lenaour", name="Christelle Le Naour", house="gramond", role="Avocate", sector="Corporate & M&A", type="Avocat M&A", profession="lawyers", source="https://gramond-avocats.com/portfolio-item/christelle-le-naour/"),
]
S_ABC = "https://finance.inextenso.fr/actualites/abc-informatique-rejoint-le-groupe-simpliciti/"
S_N10C = "https://www.gide.com/en/news-insights/gide-advises-n10c-on-the-recomposition-of-its-share-capital-and-two-external-growth-transactions-involving-dataouest-and-apixis/"
S_ARB = "https://www.moncey-avocats.com/fr/actualites/conseil-darcole-dans-le-cadre-de-sa-prise-de-participation-majoritaire-au-capital-d%27arbois-tourisme"
S_EMU = "https://www.joffeassocies.com/joffe-associes-conseille-les-associes-demulsion-dans-le-cadre-de-sa-cession-a-corail-partners/"
S_SAQ = "https://gramond-avocats.com/en/gramond-advised-the-founder-of-saqara-on-the-sale-of-the-company-to-the-once-for-all-group/"
def part(pid, house, side, src, practice=None):
    x = {"pid": pid, "house": house, "side": side, "sources": [src]}
    if practice: x["practice"] = practice
    return x
def deal(id, target, buyer, date, label, state, sector, kind, side, note, src, parts):
    return {"id": id, "target": target, "buyer": buyer, "date": date, "label": label, "state": state, "sector": sector, "kind": kind, "side": side, "note": note, "sources": [src], "checked": CHK, "participants": parts}
side_abc = "Conseil M&A du cédant, In Extenso Finance."
side_n10c = "Conseil juridique de n10c, acquéreur ; nommés par Gide."
D = [
 deal("abcinformatique-simpliciti-20261104", "ABC Informatique", "Simpliciti", "2026-11-10", "10 NOV. 2026", "announced", "Logiciels de transport", "Cession", side_abc,
      "In Extenso Finance annonce l’acquisition le 10 novembre et nomme Christophe Del Toso, Yves Chambeau et Antoine Dombre côté cédant. La photo du communiqué est légendée « lors de la signature de l’acquisition le 4 novembre ». Aucun closing écrit : annonce, hors compteur. Montant non documenté.", S_ABC,
      [part(x, "inextenso", side_abc, S_ABC) for x in ("deltoso", "chambeau", "dombre")]),
 deal("n10c-dataouest-202611", "Dataouest", "n10c", "2026-11-05", "5 NOV. 2026", "closed", "Services informatiques managés", "Acquisition", side_n10c,
      "Gide rapporte le 5 novembre la réalisation de deux opérations de croissance externe de n10c, dont l’acquisition de Dataouest (Normandie). Le 5 novembre est la date de publication, pas un jour de closing établi séparément. L’entrée d’ISAI au capital de n10c n’est pas comptée. Montant non documenté.", S_N10C,
      [part(x, "gide", side_n10c, S_N10C) for x in ("nacinovic", "patinier")]),
 deal("n10c-apixis-202611", "Apixis", "n10c", "2026-11-05", "5 NOV. 2026", "closed", "Services informatiques managés", "Acquisition", side_n10c,
      "Gide rapporte le 5 novembre la réalisation de deux opérations de croissance externe de n10c, dont l’acquisition d’Apixis (Toulouse). Le 5 novembre est la date de publication, pas un jour de closing établi séparément. Montant non documenté.", S_N10C,
      [part(x, "gide", side_n10c, S_N10C) for x in ("nacinovic", "patinier")]),
 deal("arboistourisme-arcole-20261103", "Arbois Tourisme", "Arcole", "2026-11-03", "3 NOV. 2026", "closed", "Transport de voyageurs", "MBI majoritaire", "Rôles détaillés par intervenant dans les preuves.",
      "Moncey rapporte le 3 novembre la prise de participation majoritaire d’Arcole, réalisée par le fonds Arcole II, avec un nouveau dirigeant. Le 3 novembre est la date de publication, pas un jour de closing établi séparément. Montant non documenté.", S_ARB,
      [part("giuliani", "moncey", "Conseil juridique d’Arcole, acquéreur ; Guillaume Giuliani est nommé en corporate par Moncey.", S_ARB),
       part("saintjulien", "moncey", "Conseil juridique d’Arcole, acquéreur ; Victoria Saint-Julien est nommée en corporate par Moncey.", S_ARB),
       part("bosc", "moncey", "Conseil fiscal d’Arcole, acquéreur ; Frédéric Bosc est nommé sur les aspects fiscaux par Moncey.", S_ARB, "tax")]),
 deal("emulsion-corailpartners-20261104", "Emulsion", "Corail Partners", "2026-11-04", "4 NOV. 2026", "closed", "Distribution pour cafés, hôtels et restaurants", "Cession", "Conseil juridique des cédants, Joffe & Associés.",
      "Joffe & Associés rapporte le 4 novembre être intervenu auprès des associés d’Emulsion à l’occasion du rachat par Corail Partners ; l’équipe est conduite par Aymeric Dégremont. Le 4 novembre est la date de publication, pas un jour de closing établi séparément. Montant non documenté.", S_EMU,
      [part("degremont", "joffe", "Conseil juridique des cédants ; équipe conduite par Aymeric Dégremont selon Joffe & Associés.", S_EMU)]),
 deal("saqara-onceforall-20261104", "Saqara", "Once For All", "2026-11-04", "4 NOV. 2026", "closed", "Logiciels pour le bâtiment", "Cession", "Conseil juridique du fondateur, Gramond & Associés.",
      "Gramond & Associés indique le 4 novembre avoir conseillé le fondateur de Saqara pour la vente de la société à Once For All et nomme Xavier Gramond et Christelle Le Naour. La source présente la vente comme faite, sans mot de closing ni date de réalisation. Le 4 novembre est la date de publication. Montant non documenté.", S_SAQ,
      [part(x, "gramond", "Conseil juridique du fondateur cédant ; nommés par Gramond & Associés.", S_SAQ) for x in ("xgramond", "lenaour")]),
]
for x in H:
    if not any(y["id"] == x["id"] for y in houses): houses.append(x)
for x in P:
    if x["id"] not in byid: x["checked"] = CHK; people.append(x); byid[x["id"]] = x
for x in D:
    if not any(y["id"] == x["id"] for y in deals): deals.append(x)
tdi = next(d for d in deals if d["id"] == "tdi-mytower-2026")
if not any(x["pid"] == "chambeau" for x in tdi["participants"]):
    tdi["participants"].append(part("chambeau", "inextenso", tdi["participants"][0]["side"], tdi["sources"][0]))
dump = lambda v: json.dumps(v, ensure_ascii=False, separators=(",", ":"))
L = L[:hi] + dump(houses) + L[hj:pi] + dump(people) + L[pj:di] + dump(deals) + L[dj:]
lines[2] = L
t2 = "\n".join(lines).replace("arrêté au 6 novembre 2026", "arrêté au 11 novembre 2026").replace("<='2026-11-06'", "<='%s'" % FIN)
assert "<='%s'" % FIN in t2
open(pp, "w", encoding="utf-8").write(t2)
hb = {h["id"]: h for h in houses}
def entry(p, old=None):
    ds = sorted(calc(p, FIN), key=lambda d: d["date"], reverse=True)
    h = hb[p["house"]]
    ph = p.get("photo") or ""
    e = {"id": p["id"], "name": p["name"], "profession": p["profession"], "house": h["full"], "logo": (BASE + "logos/" + h["logo"]) if h.get("logo") else "",
         "photo": (ph if ph.startswith("/") or ph.startswith("https://") else BASE + "portraits/" + ph) if ph else "",
         "closed": sum(d["state"] == "closed" for d in ds), "announced": sum(d["state"] != "closed" for d in ds),
         "refs": [{"id": d["id"], "target": d["target"], "date": d["date"], "state": d["state"], "sources": d["sources"]} for d in ds]}
    if old:  # on garde l'écriture en ligne des champs non concernés et des preuves déjà publiées
        for k in ("house", "logo", "photo"): e[k] = old[k]
        oldrefs = {r["id"]: r for r in old["refs"]}
        e["refs"] = [oldrefs.get(r["id"], r) for r in e["refs"]]
    return e
eb = {e["id"]: e for e in entries}; chg = []
for pid in ["deltoso", "nacinovic", "bosc"] + [x["id"] for x in P]:
    e = entry(byid[pid], eb.get(pid))
    if pid in eb:
        if e != eb[pid]: entries[entries.index(eb[pid])] = e; chg.append(pid)
    else: entries.append(e); chg.append(pid)
for e in entries:  # contrôle final : tout le fichier concorde avec le calcul
    ds = calc(byid[e["id"]], FIN); assert (sum(d["state"] == "closed" for d in ds), sum(d["state"] != "closed" for d in ds)) == (e["closed"], e["announced"]), e["id"]
c2 = c[:ei] + dump(entries) + c[ej:]
c2 = c2.replace("arrêté au 6 novembre 2026", "arrêté au 11 novembre 2026").replace("Du 1er janvier au 6 novembre 2026", "Du 1er janvier au 11 novembre 2026")
c2 = c2.replace("""<span class="rank-house"><img class="rank-logo" loading="lazy" src="'+esc(p.logo)+'" alt="">'+esc(p.house)""", """<span class="rank-house">'+(p.logo?'<img class="rank-logo" loading="lazy" src="'+esc(p.logo)+'" alt="">':'')+esc(p.house)""")
assert "(p.logo?'<img class=\"rank-logo\"" in c2 and "au 11 novembre 2026</p>" in c2
open(pc, "w", encoding="utf-8").write(c2)
pa = os.path.join(ROOT, "annuaire.html"); a = open(pa, encoding="utf-8").read()
a2 = a.replace("classements.js?v=20261106-batisante", "classements.js?v=20261111-arrete").replace("profils.js?v=20261106-batisante", "profils.js?v=20261111-arrete")
open(pa, "w", encoding="utf-8").write(a2)
print("modifiés ou ajoutés :", chg, "· personnes", len(people), "· opérations", len(deals), "· lignes du classement", len(entries))
for prof in ("bankers", "lawyers", "tax", "debt"):
    r = sorted([e for e in entries if e["profession"] == prof and e["closed"] > 0], key=lambda e: (-e["closed"], e["name"]))
    print(prof, [(1 + sum(q["closed"] > e["closed"] for q in r), e["name"], e["closed"], e["announced"]) for e in r])
