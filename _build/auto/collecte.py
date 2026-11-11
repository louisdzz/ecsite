#!/usr/bin/env python3
"""Collecte des faits publics pour les fiches automatiques de l'Annuaire.
Sources : API Recherche d'entreprises (État, SIRENE/RNE), registre ORIAS, site officiel de la maison.
Aucune donnée privée. Les dates de naissance renvoyées par le registre ne sont jamais conservées.
Usage : python3 collecte.py pilote_entrees.json donnees/
"""
import json, re, sys, os, time, html, urllib.request, urllib.parse, ssl, unicodedata, datetime
UA = "Mozilla/5.0 (compatible; AnnuaireCollecte/1.0)"
TODAY = datetime.date.today().isoformat()
CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or None)

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.geturl(), r.read(1500000).decode("utf-8", "ignore")
    except Exception as e:
        return None, "ERR %s" % e

def text(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)))

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def api(siren):
    for _ in range(3):
        u, t = get("https://recherche-entreprises.api.gouv.fr/search?q=%s&per_page=1" % siren)
        if u:
            r = json.loads(t).get("results") or []
            return r[0] if r and r[0]["siren"] == siren else None
        time.sleep(2)
    return None

def luhn(s):
    t = 0
    for i, c in enumerate(reversed(s)):
        d = int(c) * (2 if i % 2 else 1)
        t += d - 9 if d > 9 else d
    return t % 10 == 0

def sirens_in(t):
    out = []
    for m in re.finditer(r"(?:SIREN|SIRET|RCS|R\.C\.S\.?|immatricul[ée]e?)[^0-9]{0,80}((?:\d[  .]?){9,14})", t, flags=re.I):
        d = re.sub(r"\D", "", m.group(1))[:9]
        if len(d) == 9 and luhn(d) and d not in out:
            out.append(d)
    return out

def site_scan(site):
    """Renvoie pages lues, SIREN publiés, numéros ORIAS publiés et page LinkedIn de la maison liée depuis le site."""
    res = {"pages": [], "sirens": {}, "orias": {}, "linkedin": None}
    u, h = get(site)
    if not u:
        return res
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(u))
    cand = [u]
    for m in re.finditer(r'href="([^"]+)"', h):
        l = m.group(1)
        if re.search(r"mention|legal|l%C3%A9gal|légal|conformit|reglement|cgu", l, re.I):
            l = urllib.parse.urljoin(u, l)
            if l.startswith(base) and l not in cand:
                cand.append(l)
    for p in ("/mentions-legales", "/mentions-legales/"):
        if base + p not in cand:
            cand.append(base + p)
    for l in cand[:6]:
        uu, hh = (u, h) if l == u else get(l)
        if not uu:
            continue
        res["pages"].append(uu)
        t = text(hh)
        for s in sirens_in(t):
            res["sirens"].setdefault(s, uu)
        for m in re.finditer(r"ORIAS[^0-9]{0,60}(\d{2}[  ]?\d{3}[  ]?\d{3})\b", t, flags=re.I):
            res["orias"].setdefault(re.sub(r"\D", "", m.group(1)), uu)
        if not res["linkedin"]:
            m = re.search(r'href="(https?://(?:[a-z]+\.)?linkedin\.com/company/[^"?#]+)', hh)
            if m:
                res["linkedin"] = {"url": m.group(1).rstrip("/"), "source": uu}
    return res

CATS = "COA|CIF|COBSP|MOBSPL|MOBSP|MIOBSP|AGA|MIA|MA|ALPSI|CIP|IFP|IAE"
def orias(siren):
    url = "https://www.orias.fr/home/showIntermediaire/%s" % siren
    u, h = get(url)
    if not u:
        return None
    t = text(h)
    m = re.search(r"N° Orias (\d{8})", t)
    if not m:
        return {"url": url, "inscrit": False}
    o = {"url": url, "numero": m.group(1), "inscrit": True, "categories": []}
    e = re.search(r"Etat & Inscriptions (\w+)", t)
    o["etat"] = e.group(1) if e else None
    for c in re.finditer(r"\b(%s) ([A-ZÉa-zéèêàçôûî' \-]{8,90}?) (Inscrit le|Radié le|Supprimé le) (\d{2}/\d{2}/\d{4})" % CATS, t):
        o["categories"].append({"code": c.group(1), "libelle": c.group(2).strip(), "etat": c.group(3).split()[0], "date": c.group(4)})
    return o

NJ = {"5710": "SAS, société par actions simplifiée", "5720": "SASU, société par actions simplifiée à associé unique", "5499": "SARL, société à responsabilité limitée", "5498": "EURL, SARL à associé unique", "5599": "SA à conseil d'administration", "5699": "SA à directoire", "6599": "Société civile", "6540": "Société civile immobilière", "1000": "Entrepreneur individuel", "5202": "Société en nom collectif", "5308": "Société en commandite par actions", "5800": "Société européenne", "9220": "Association déclarée", "6589": "Société civile de moyens", "5485": "Société d'exercice libéral à responsabilité limitée", "5785": "Société d'exercice libéral par actions simplifiée"}

def main(src, out):
    os.makedirs(out, exist_ok=True)
    rej = []
    for e in json.load(open(src)):
        rec = {"nom_usuel": e["nom"], "categorie": e["cat"], "crm": e.get("crm"), "slug_existant": e.get("slug_existant"), "consulte_le": TODAY, "sources": {}}
        sc = site_scan(e["site"]) if e.get("site") else {"pages": [], "sirens": {}, "orias": {}, "linkedin": None}
        siren = e.get("siren")
        if siren:
            rec["siren_source"] = {"type": "site officiel, mentions légales (relevé au CRM)" if siren not in sc["sirens"] else "site officiel", "url": sc["sirens"].get(siren)}
        else:
            ok = []
            for s, pu in sc["sirens"].items():
                a = api(s)
                if not a:
                    continue
                names = " ".join(filter(None, [a.get("nom_complet"), a.get("nom_raison_sociale"), a.get("sigle"), (a.get("siege") or {}).get("nom_commercial"), " ".join((a.get("siege") or {}).get("liste_enseignes") or [])]))
                toks = [w for w in norm(e["nom"]).split() if w not in ("family", "office", "gestion", "privee", "patrimoine", "conseil", "finance", "capital", "partners", "groupe", "group", "et", "cie", "invest", "wealth", "management", "private", "fo", "am")]
                if toks and all(w in norm(names) for w in toks):
                    ok.append((s, pu))
            if len(ok) != 1:
                rej.append({"nom": e["nom"], "motif": "identité non établie (SIREN publiés sur le site : %s ; concordants : %d)" % (list(sc["sirens"]) or "aucun", len(ok)), "pages": sc["pages"]})
                continue
            siren = ok[0][0]
            rec["siren_source"] = {"type": "site officiel", "url": ok[0][1]}
        a = api(siren)
        if not a:
            rej.append({"nom": e["nom"], "motif": "SIREN %s introuvable à l'API Recherche d'entreprises" % siren}); continue
        if a.get("statut_diffusion") != "O":
            rej.append({"nom": e["nom"], "motif": "entité non diffusible au registre : pas de fiche"}); continue
        sg = a.get("siege") or {}
        reg = "https://annuaire-entreprises.data.gouv.fr/entreprise/%s" % siren
        rec.update({"siren": siren, "denomination": a.get("nom_raison_sociale") or a.get("nom_complet"), "nom_complet": a.get("nom_complet"), "sigle": a.get("sigle"),
            "enseigne": sg.get("nom_commercial") or ((sg.get("liste_enseignes") or [None])[0]),
            "forme": NJ.get(a.get("nature_juridique")), "forme_code": a.get("nature_juridique"), "creation": a.get("date_creation"),
            "ville": sg.get("libelle_commune"), "actif": a.get("etat_administratif") == "A", "naf": a.get("activite_principale"),
            "opposition_prospection": bool(a.get("opposition_diffusion_commerciale")), "registre_url": reg, "maj_rne": a.get("date_mise_a_jour_rne")})
        dirs = []
        for d in a.get("dirigeants") or []:
            q = d.get("qualite") or ""
            if re.search(r"commissaire aux comptes", q, re.I):
                continue
            if d.get("type_dirigeant") == "personne physique":
                dirs.append({"type": "pp", "prenoms": d.get("prenoms"), "nom": d.get("nom"), "qualite": q})
            else:
                dirs.append({"type": "pm", "denomination": d.get("denomination"), "siren": d.get("siren"), "qualite": q})
        rec["dirigeants"] = dirs
        rec["orias"] = orias(siren)
        rec["orias_site"] = sc["orias"]
        rec["site"] = e.get("site"); rec["site_pages"] = sc["pages"]; rec["linkedin"] = sc["linkedin"]
        json.dump(rec, open(os.path.join(out, siren + ".json"), "w"), ensure_ascii=False, indent=1)
        print("OK", e["nom"], siren, rec["denomination"], rec["ville"], len(dirs), (rec["orias"] or {}).get("numero"))
        time.sleep(0.4)
    json.dump(rej, open(os.path.join(out, "_rejets.json"), "w"), ensure_ascii=False, indent=1)
    for r in rej: print("REJET", r["nom"], "-", r["motif"])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
