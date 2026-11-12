# Relecture indépendante du lot experts-comptables : la fiche HTML est comparée au registre relu à l'instant, et chaque preuve du
# lien avec la cession est rechargée à sa source. Remplace pour cette rubrique le contrôle CIF de controle.py (aucun cabinet du lot
# n'est inscrit à l'ORIAS : le critère est le lien documenté avec la cession, décision de Louis du 12 novembre 2026).
# Contrôles : SIREN au registre, NAF 69.20Z, société active et diffusible, pas d'entrepreneur individuel, dénomination, création,
# ville, dirigeants ; au moins une preuve, chacune avec son URL et sa date de consultation ; preuve « b » sur le site de la fiche et
# terme retrouvé à la source ; aucune fiche personne, aucun titre « expert-comptable » accolé à un dirigeant, aucune coordonnée.
# Usage : python3 _build/auto/controle_ec.py <taille échantillon ou 0 pour tout> <sortie erreurs.json> [base, ex. https://www.exit.club], depuis la racine du dépôt.
import json, re, sys, html, time, random, urllib.request, ssl, os, unicodedata, subprocess
from urllib.parse import urlparse
CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or None)
def fetch(u, n=4, ua="Mozilla/5.0 (compatible; AnnuaireControle/1.0)"):
    for k in range(n):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": ua, "Accept-Language": "fr"}), timeout=25, context=CTX) as r:
                return r.read(6000000).decode("utf-8", "ignore")
        except Exception as e:
            time.sleep(10 * (k + 1) if "429" in str(e) else 2)
    return None
def plat(s): return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()).strip()
def txt(h): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", h, flags=re.S | re.I))))
def hote(u): return re.sub(r"^www\.", "", (urlparse(u).hostname or "").lower())
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
def fr(iso):
    y, mo, d = iso.split("-"); return "%s %s %s" % ("1er" if int(d) == 1 else int(d), MOIS[int(mo) - 1], y)
m = json.load(open("_build/auto/manifeste.json", encoding="utf-8"))
lot = [x for x in m["maisons"] if x["categorie"] == "experts-comptables"]
n = int(sys.argv[1]); BASE = sys.argv[3] if len(sys.argv) > 3 else None
random.seed(2026111223)
ech = lot if not n else random.sample(lot, min(n, len(lot)))
def lit(ch): return fetch("%s/%s" % (BASE, ch[:-5])) if BASE else open(ch, encoding="utf-8").read()
pers = {p["siren"] for p in m["personnes"]}
err = []; src_ko = []; a_relire = []
for x in ech:
    s = x["siren"]; e = []
    r = json.load(open("_build/auto/donnees/%s.json" % s, encoding="utf-8"))
    h = lit(x["chemin"])
    if not h: err.append((s, ["fiche illisible"])); print("ERR", s, x["slug"], "fiche illisible", flush=True); continue
    t = txt(h)
    a = None
    for k in range(4):
        try:
            a = json.loads(fetch("https://recherche-entreprises.api.gouv.fr/search?q=%s&per_page=1" % s))["results"][0]; break
        except Exception: time.sleep(3)
    if not a: err.append((s, ["registre injoignable"])); print("ERR", s, x["slug"], "registre injoignable", flush=True); continue
    if a["siren"] != s: e.append("siren")
    if a["etat_administratif"] != "A": e.append("cessée")
    if a.get("statut_diffusion") != "O": e.append("non diffusible")
    if a.get("nature_juridique") == "1000": e.append("entrepreneur individuel")
    if a.get("activite_principale") != "69.20Z": e.append("NAF %s" % a.get("activite_principale"))
    if "69.20Z" not in t: e.append("NAF non affiché")
    h1 = html.unescape(re.search(r"<h1>(.*?)</h1>", h).group(1))
    if h1 != a["nom_raison_sociale"]: e.append("nom %r/%r" % (h1, a["nom_raison_sociale"]))
    if "%s %s %s" % (s[:3], s[3:6], s[6:]) not in t: e.append("siren affiché")
    if fr(a["date_creation"]) not in t: e.append("création " + a["date_creation"])
    v = a["siege"].get("libelle_commune") or ""
    if plat(v) not in plat(t): e.append("ville " + v)
    if "Active au registre" not in t: e.append("statut")
    # dirigeants : chaque mandataire du registre figure, et aucun autre (même lecture que controle.py)
    bloc = re.search(r'id="dirigeants">(.*?)</section>', h, re.S).group(1)
    aff = [plat(html.unescape(re.sub(r"<[^>]+>", "", b))) for b in re.findall(r"<li><b>(.*?)</b>", bloc)]
    reg = [d_ for d_ in a.get("dirigeants") or [] if not re.search("commissaire aux comptes", d_.get("qualite") or "", re.I)]
    _v = []; _r = []
    for d_ in reg:
        k_ = (d_.get("type_dirigeant"), plat(re.sub(r"\(.*?\)", " ", d_.get("nom") or d_.get("denomination") or "")), d_.get("siren") or "", plat(d_.get("qualite") or ""), plat(d_.get("prenoms") or ""))
        if any(k_[:4] == z[:4] and ((k_[4] + " ").startswith(z[4] + " ") or (z[4] + " ").startswith(k_[4] + " ")) for z in _v): continue
        _v.append(k_); _r.append(d_)
    reg = _r
    if any(len(z.split()) > 1 and z.split()[0] == z.split()[1] for z in aff): e.append("prénom doublé")
    if len(aff) != len(reg): e.append("nb dirigeants %d/%d" % (len(aff), len(reg)))
    for d_ in reg:
        if d_.get("type_dirigeant") == "personne physique":
            pn = plat((d_.get("prenoms") or "").split()[0] if d_.get("prenoms") else ""); nm = plat(re.sub(r"\(.*?\)", "", d_.get("nom") or ""))
            par_ = plat(" ".join(re.findall(r"\((.*?)\)", d_.get("nom") or "")))
            if par_ and pn and nm == pn + " " + par_: nm = par_
            elif par_ and pn and nm == pn and par_ != pn: nm = par_
            if not any(pn.replace(" ", "") in z.replace(" ", "") and nm in z for z in aff): e.append("dirigeant absent " + nm)
            q = d_.get("qualite") or ""
            if q and q != "Autre" and html.escape(q) not in bloc and q not in html.unescape(bloc): e.append("qualité %r absente" % q)
    if re.search(r"\b(né|née) (le|en)\b|\d{2}/\d{2}/19\d\d", bloc): e.append("date de naissance")
    # fiches cabinets seulement ; aucun titre professionnel accolé à un dirigeant
    if 'href="/p/' in h or s in pers: e.append("fiche personne")
    if re.search(r"expert[- ]comptable", html.unescape(re.sub(r"<[^>]+>", " ", bloc)), re.I): e.append("titre expert-comptable dans le bloc dirigeants")
    st = re.search(r'id="statuts">(.*?)</section>', h, re.S).group(1)
    if "N° " in st or "non vérifiée par cette fiche" not in st: e.append("statuts réglementaires")
    # lien avec la cession : au moins une preuve, chacune avec URL et date ; preuve b sur le site de la fiche et retrouvée à la source
    lc = re.search(r'id="lien-cession">(.*?)</section>', h, re.S)
    ps = (r.get("lien_cession") or {}).get("preuves") or []
    if not lc or not ps or not any(p["critere"] in "abcd" for p in ps): e.append("aucune preuve du lien avec la cession")
    else:
        blc = html.unescape(lc.group(1))
        if len(re.findall(r"<div><dt>", lc.group(1))) != len(ps): e.append("nb preuves affichées")
        site = re.search(r"<dt>Site officiel</dt><dd><a href=\"([^\"]+)\"", h)
        for p in ps:
            if not p.get("url") or not p.get("date") or p["url"] not in blc or ("consulté le " + fr(p["date"])) not in txt(lc.group(1)): e.append("preuve sans URL ou sans date affichée"); continue
            if p["critere"] == "b":
                terme = re.search(r"«\s*(.*?)\s*»", p["texte"]).group(1)
                if not site or hote(html.unescape(site.group(1))) != hote(p["url"]) or hote(r.get("site") or "") != hote(p["url"]): e.append("preuve b hors du site officiel de la fiche")
                if terme not in blc: e.append("terme non affiché")
                a_relire.append((s, p["url"], terme))
            elif p["critere"] in ("d", "complement") and "Cité dans le classement" not in p["texte"]: e.append("libellé de classement")
    if re.search(r"[\w.-]+@[\w-]+\.[a-z]{2,}|\b0[1-9](?:[ .]?\d\d){4}\b|\+33", re.sub(r"mailto:louis@exit\.club[^\"]*|louis@exit\.club", "", t)): e.append("coordonnée affichée")
    if "—" in re.sub(r'<aside.*?</aside>', "", h, flags=re.S) .replace("content:\"—\"", "") and "—" in t: e.append("tiret cadratin")
    if "Revendiquer ce profil" not in h: e.append("bouton Revendiquer absent")
    for dd in re.findall(r"<div><dt>(.*?)</dt><dd>(.*?)</dd></div>", re.search(r'id="identite">(.*?)</section>', h, re.S).group(1)):
        if "fa-src" not in dd[1] and "Non renseigné" not in dd[1]: e.append("champ sans source : " + dd[0])
    print("OK " if not e else "ERR", s, h1, e or "", flush=True)
    if e: err.append((s, e))
    time.sleep(0.35)
# preuves rechargées à la source (en parallèle, les sites des cabinets étant lents)
def relit(q):
    s_, u_, terme = q
    hh = fetch(u_, 2, "Mozilla/5.0 (compatible; AnnuaireCollecte/1.0)") or fetch(u_.replace("://", "://www.") if "//www." not in u_ else u_.replace("://www.", "://"), 1, "Mozilla/5.0 (compatible; AnnuaireCollecte/1.0)")
    z = lambda q_: re.sub(r"\s+", " ", q_.lower().replace("’", "'"))
    if not hh or z(terme) not in z(txt(hh)):
        # certains sites répondent compressés (brotli) quel que soit l'en-tête : seconde lecture par curl
        try: hh = subprocess.run(["curl", "-sL", "--compressed", "-m", "30", "-A", "Mozilla/5.0 (compatible; AnnuaireCollecte/1.0)", u_], capture_output=True, timeout=40).stdout.decode("utf-8", "ignore") or hh
        except Exception: pass
    if not hh: return (s_, u_, "source injoignable")
    if z(terme) not in z(txt(hh)): return (s_, u_, "terme non retrouvé à la source : " + terme)
from concurrent.futures import ThreadPoolExecutor
src_ko = [k for k in ThreadPoolExecutor(16).map(relit, a_relire) if k]
print("cabinets relus", len(ech), "sur", len(lot), "· fiches en erreur", len(err), "· preuves non retrouvées à la source", len(src_ko))
for z in src_ko: print("SOURCE", *z)
json.dump({"erreurs": err, "sources": src_ko}, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
