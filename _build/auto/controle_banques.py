# Relecture indépendante de la rubrique banques : la fiche HTML est comparée au registre des entreprises et au registre REGAFI de
# l'ACPR relus à l'instant, et chaque extrait d'activité est rechargé à sa source. Remplace pour cette rubrique le contrôle CIF de
# controle.py (critère validé par Louis le 13 novembre 2026 : activité de banque privée, de financement d'acquisition ou de banque
# d'affaires décrite par au moins une phrase visant l'entité du SIREN).
# Contrôles : SIREN au registre, société active et diffusible, dénomination, création, ville, dirigeants avec leur qualité ;
# inscription REGAFI (identifiant, SIREN publié par l'ACPR, dénomination, CIB, catégorie établissement de crédit) ; au moins une
# preuve d'activité, chacune avec catégorie, extrait, URL et date affichés, extrait retrouvé à la source ; aucune fiche personne,
# aucune coordonnée, aucun SIREN en double dans le manifeste.
# Usage : python3 _build/auto/controle_banques.py <sortie erreurs.json> [base, ex. https://www.exit.club], depuis la racine du dépôt.
import json, re, sys, html, time, urllib.request, urllib.parse, ssl, os, unicodedata, subprocess, collections
CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or None)
def fetch(u, n=4, ua="Mozilla/5.0 (compatible; AnnuaireControle/1.0)"):
    for k in range(n):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": ua, "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.5", "Accept": "text/html,application/xhtml+xml,application/json"}), timeout=30, context=CTX) as r:
                return r.read(8000000).decode(r.headers.get_content_charset() or "utf-8", "ignore")
        except Exception as e:
            time.sleep(10 * (k + 1) if "429" in str(e) else 3)
    return None
def plat(s): return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()).strip()
def txt(h): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", h, flags=re.S | re.I))))
def z(s): return re.sub(r"\s+([.,])", r"\1", re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("‘", "'").replace("\u00a0", " ").replace("\u202f", " "))).strip().lower()
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
def fr(iso):
    y, mo, d = iso.split("-"); return "%s %s %s" % ("1er" if int(d) == 1 else int(d), MOIS[int(mo) - 1], y)
LIB = {"banque privée": "Banque privée", "financement d'acquisition": "Financement d’acquisition", "banque d'affaires": "Banque d’affaires"}
m = json.load(open("_build/auto/manifeste.json", encoding="utf-8"))
lot = [x for x in m["maisons"] if x["categorie"] == "banques"]
BASE = sys.argv[2] if len(sys.argv) > 2 else None
def lit(ch): return fetch("%s/%s" % (BASE, ch[:-5])) if BASE else open(ch, encoding="utf-8").read()
pers = {p["siren"] for p in m["personnes"]}
dbl = [s for s, k in collections.Counter(x["siren"] for x in m["maisons"]).items() if k > 1]
err = []; src_ko = []; a_relire = []
if dbl: err.append(("manifeste", ["SIREN en double : %s" % dbl]))
for x in lot:
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
    h1 = html.unescape(re.search(r"<h1>(.*?)</h1>", h).group(1))
    ident = re.search(r'id="identite">(.*?)</section>', h, re.S).group(1)
    if "<dt>Dénomination</dt><dd>%s<" % html.escape(a["nom_raison_sociale"], quote=True) not in ident: e.append("dénomination du registre %r non affichée" % a["nom_raison_sociale"])
    if "%s %s %s" % (s[:3], s[3:6], s[6:]) not in txt(ident): e.append("siren affiché")
    if a.get("date_creation") and fr(a["date_creation"]) not in t: e.append("création " + a["date_creation"])
    v = a["siege"].get("libelle_commune") or ""
    if v and plat(v) not in plat(txt(ident)): e.append("ville " + v)
    if "Active au registre" not in t: e.append("statut")
    # dirigeants : chaque mandataire du registre figure avec sa qualité, et aucun autre (même lecture que controle_ec.py)
    bloc = re.search(r'id="dirigeants">(.*?)</section>', h, re.S).group(1)
    aff = [plat(html.unescape(re.sub(r"<[^>]+>", "", b))) for b in re.findall(r"<li><b>(.*?)</b>", bloc)]
    reg = [d_ for d_ in a.get("dirigeants") or [] if not re.search("commissaire aux comptes", d_.get("qualite") or "", re.I)]
    _v = []; _r = []
    for d_ in reg:
        k_ = (d_.get("type_dirigeant"), plat(re.sub(r"\(.*?\)", " ", d_.get("nom") or d_.get("denomination") or "")), d_.get("siren") or "", plat(d_.get("qualite") or ""), plat(d_.get("prenoms") or ""))
        if any(k_[:4] == q[:4] and ((k_[4] + " ").startswith(q[4] + " ") or (q[4] + " ").startswith(k_[4] + " ")) for q in _v): continue
        _v.append(k_); _r.append(d_)
    reg = _r
    if any(len(q.split()) > 1 and q.split()[0] == q.split()[1] for q in aff): e.append("prénom doublé")
    if len(aff) != len(reg): e.append("nb dirigeants %d/%d" % (len(aff), len(reg)))
    for d_ in reg:
        if d_.get("type_dirigeant") == "personne physique":
            pn = plat((d_.get("prenoms") or "").split()[0] if d_.get("prenoms") else ""); nm = plat(re.sub(r"\(.*?\)", "", d_.get("nom") or ""))
            par_ = plat(" ".join(re.findall(r"\((.*?)\)", d_.get("nom") or "")))
            if par_ and pn and nm == pn + " " + par_: nm = par_
            elif par_ and pn and nm == pn and par_ != pn: nm = par_
            if not any(pn.replace(" ", "") in q.replace(" ", "") and nm in q for q in aff): e.append("dirigeant absent " + nm)
            q = d_.get("qualite") or ""
            if q and q != "Autre" and html.escape(q) not in bloc and q not in html.unescape(bloc): e.append("qualité %r absente" % q)
    if re.search(r"\b(né|née) (le|en)\b|\d{2}/\d{2}/19\d\d", bloc): e.append("date de naissance")
    if 'href="/p/' in h or s in pers: e.append("fiche personne")
    # REGAFI : la fiche de l'ACPR relue par identifiant
    ac = r["acpr"]; st = re.search(r'id="statuts">(.*?)</section>', h, re.S).group(1); stt = txt(st)
    g = None
    for k in range(4):
        try:
            g = json.loads(fetch("https://regafi.fr/api/explore/v2.1/catalog/datasets/catalogue-banque/records?limit=20&where=" + urllib.parse.quote('id_referentiel="%s"' % ac["id_referentiel"])))["results"]; break
        except Exception: time.sleep(4)
    if g is None: e.append("REGAFI injoignable")
    elif len(g) != 1: e.append("REGAFI : %d enregistrements" % len(g))
    else:
        g = g[0]
        if g.get("siren") != s: e.append("REGAFI siren %r" % g.get("siren"))
        if g.get("denomination") != ac["denomination"] or html.escape(ac["denomination"], quote=True) not in st: e.append("REGAFI dénomination %r" % g.get("denomination"))
        if "Établissement de Crédit" not in (g.get("categorie") or ""): e.append("REGAFI catégorie %r" % g.get("categorie"))
        cibs = [c["code"] for c in json.loads(g.get("cib") or "[]")]
        if sorted(cibs) != sorted(ac.get("cib") or []) or any(c not in stt for c in cibs): e.append("REGAFI CIB %r" % cibs)
        if str(g.get("approval_withdrawal_process")) == "True": e.append("REGAFI retrait d'agrément en cours")
        if ac["url"] not in html.unescape(st): e.append("lien REGAFI")
    if "SIREN publié par l’ACPR %s %s %s" % (s[:3], s[3:6], s[6:]) not in stt: e.append("SIREN publié par l'ACPR non affiché")
    if "ORIAS" in stt: e.append("mention ORIAS dans les statuts")
    # activités : au moins une preuve, chacune avec catégorie, extrait, URL et date ; extrait retrouvé à la source
    sec = re.search(r'id="activites-banque">(.*?)</section>', h, re.S)
    ps = (r.get("activites") or {}).get("preuves") or []
    if not sec or not ps: e.append("aucune activité décrite")
    else:
        b = html.unescape(sec.group(1)); bt = txt(sec.group(1))
        if len(re.findall(r"<div><dt>", sec.group(1))) != len(ps): e.append("nb preuves affichées")
        for p in ps:
            dt = p.get("relu_le") or p.get("date_lecture")
            if p["categorie"] not in LIB or "<dt>%s</dt>" % LIB[p["categorie"]] not in sec.group(1): e.append("catégorie non affichée")
            if not p.get("url") or not dt or p["url"] not in b or ("consulté le " + fr(dt)) not in bt: e.append("preuve sans URL ou sans date affichée")
            if not p.get("extrait") or len(p["extrait"]) < 40 or z(p["extrait"]) not in z(bt): e.append("extrait non affiché")
            a_relire.append((s, p["url"], p["extrait"]))
        if set(r["activites"]["categories"]) != {p["categorie"] for p in ps}: e.append("catégories sans preuve")
    if re.search(r"[\w.-]+@[\w-]+\.[a-z]{2,}|\b0[1-9](?:[ .]?\d\d){4}\b|\+33", re.sub(r"mailto:louis@exit\.club[^\"]*|louis@exit\.club", "", t)): e.append("coordonnée affichée")
    if "—" in t: e.append("tiret cadratin")
    if "Revendiquer ce profil" not in h: e.append("bouton Revendiquer absent")
    for dd in re.findall(r"<div><dt>(.*?)</dt><dd>(.*?)</dd></div>", ident):
        if "fa-src" not in dd[1] and "Non renseigné" not in dd[1]: e.append("champ sans source : " + dd[0])
    print("OK " if not e else "ERR", s, h1, e or "", flush=True)
    if e: err.append((s, e))
    time.sleep(0.4)
# extraits rechargés à la source (pages à contenu variable : quatre essais)
def relit(q):
    s_, u_, ex = q
    frag = z(ex).rstrip(".…").rstrip(".")[:120]
    hh = None
    for k in range(4):
        hh = fetch(u_, 2, "Mozilla/5.0 (compatible; AnnuaireCollecte/1.0)")
        if not hh or frag not in z(txt(hh)):
            try: hh = subprocess.run(["curl", "-sL", "--compressed", "-m", "30", "-A", "Mozilla/5.0 (compatible; AnnuaireCollecte/1.0)", "-H", "Accept-Language: fr-FR,fr;q=0.9", u_], capture_output=True, timeout=40).stdout.decode("utf-8", "ignore") or hh
            except Exception: pass
        if hh and frag in z(txt(hh)): return None
        time.sleep(5)
    return (s_, u_, "source injoignable" if not hh else "extrait non retrouvé à la source : " + ex[:80])
for q in a_relire:
    k = relit(q)
    if k: src_ko.append(k)
    time.sleep(1.2)
print("banques relues", len(lot), "· fiches en erreur", len(err), "· extraits non retrouvés à la source", len(src_ko))
for q in src_ko: print("SOURCE", *q)
json.dump({"erreurs": err, "sources": src_ko}, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
