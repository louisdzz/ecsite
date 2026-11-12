# Relecture indépendante du lot « maisons repérées par les classements publics » (12 novembre 2026) : chaque fiche HTML est comparée
# au registre relu à l'instant, à l'ORIAS (hors avocats) et à son enregistrement source. Les classements servent au repérage : aucune
# donnée de fiche n'en vient, seule la mention externe datée et liée est affichée, sans rang.
# Contrôles : SIREN au registre, société active et diffusible, pas d'entrepreneur individuel, dénomination, création, ville, dirigeants ;
# rubrique cohérente avec le registre (avocats : NAF 69.10Z ; experts-comptables : 69.20Z) ; barreau affiché seulement avec sa source ;
# chaque champ d'identité avec sa source, sinon « Non renseigné » ; mentions externes à la forme convenue, liées, sans rang ni niveau ;
# aucune mention dans le titre, la description ou le JSON-LD ; aucune fiche personne ; aucune coordonnée ; aucun doublon par SIREN,
# identifiant, nom ou site dans tout le répertoire.
# Usage : python3 _build/auto/controle_ll.py <taille échantillon ou 0 pour tout> <sortie erreurs.json> [base, ex. https://www.exit.club]
import json, re, sys, html, time, random, urllib.request, ssl, os, unicodedata, glob, collections
from urllib.parse import urlparse
LOT = "reperage-classements-publics-20261112"
CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or None)
def fetch(u, n=4):
    for k in range(n):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; AnnuaireControle/1.0)", "Accept-Language": "fr"}), timeout=25, context=CTX) as r:
                return r.read(6000000).decode("utf-8", "ignore")
        except Exception as e:
            time.sleep(10 * (k + 1) if "429" in str(e) else 2)
    return None
def plat(s): return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()).strip()
def txt(h): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", h, flags=re.S | re.I))))
def hote(u): return re.sub(r"^www\.", "", (urlparse(u or "").hostname or "").lower())
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
def fr(iso):
    y, mo, d = iso.split("-"); return "%s %s %s" % ("1er" if int(d) == 1 else int(d), MOIS[int(mo) - 1], y)
LABELS = {"avocats": "Avocats d'affaires & fiscalistes", "banques-affaires": "Banques d'affaires (M&A)", "boutiques-ma": "Boutiques M&A", "fonds-pe": "Fonds de Private Equity & LBO", "fonds-vc": "Fonds de Venture Capital", "fonds-dette": "Fonds de dette", "experts-comptables": "Experts-comptables & auditeurs", "cgp": "Conseillers en gestion de patrimoine (CGP)"}
RANG = re.compile(r"\b(rang|rangs|class[ée]e? (?:n°|\d)|n°\s*\d|\d+(?:er|e|ème)\b|incontournable|excellent|forte notoriété|pratique réputée|pratique de qualité|band \d|tier \d|top \d)", re.I)
MENTION = re.compile(r"^Cité dans les classements publics Leaders League \((.+), édition (20\d\d)\), consulté le (\d\d)/(\d\d)/(\d{4})$")
m = json.load(open("_build/auto/manifeste.json", encoding="utf-8"))
recs = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in glob.glob("_build/auto/donnees/[0-9]*.json")}
lot = [x for x in m["maisons"] if recs[x["siren"]].get("lot") == LOT]
n = int(sys.argv[1]); BASE = sys.argv[3] if len(sys.argv) > 3 else None
random.seed(2026111301)
ech = lot if not n else random.sample(lot, min(n, len(lot)))
def lit(ch): return fetch("%s/%s" % (BASE, ch[:-5])) if BASE else open(ch, encoding="utf-8").read()
pers = {p["siren"] for p in m["personnes"]}
err = []
# doublons dans tout le répertoire : SIREN, identifiant, nom, site
cs = collections.Counter(x["siren"] for x in m["maisons"]); cl = collections.Counter(x["slug"] for x in m["maisons"])
houses = json.load(open("assets/ecosysteme/maison/data.json", encoding="utf-8"))["houses"]
cn = collections.Counter(plat(h["name"]) for h in houses)
sites = collections.defaultdict(set)
if not BASE:
    for f in glob.glob("f/*.html"):
        hh = open(f, encoding="utf-8").read()
        for pat in (r'class="sitel" href="(https?://[^"]+)"', r'<dt>Site officiel</dt><dd><a href="(https?://[^"]+)"', r'class="pv-primary" href="(https?://[^"]+)"[^>]*>Découvrir la maison', r'<a href="(https?://[^"]+)"[^>]*>Site (?:de la maison|officiel)'):
            mm = re.search(pat, hh)
            if mm: sites[html.unescape(mm.group(1)).rstrip("/").lower().replace("://www.", "://")].add(os.path.basename(f)[:-5]); break
dom_lot = collections.defaultdict(set)
for x in lot:
    if recs[x["siren"]].get("site"): dom_lot[hote(recs[x["siren"]]["site"])].add(x["slug"])
dom_tous = collections.defaultdict(set)
for u, sl in sites.items(): dom_tous[hote(u)] |= sl
for x in ech:
    s = x["siren"]; e = []; r = recs[s]
    h = lit(x["chemin"])
    if not h: err.append((s, ["fiche illisible"])); print("ERR", s, x["slug"], "fiche illisible", flush=True); continue
    t = txt(h)
    a = None
    for k in range(4):
        try: a = json.loads(fetch("https://recherche-entreprises.api.gouv.fr/search?q=%s&per_page=1" % s))["results"][0]; break
        except Exception: time.sleep(3)
    if not a: err.append((s, ["registre injoignable"])); print("ERR", s, x["slug"], "registre injoignable", flush=True); continue
    if a["siren"] != s: e.append("siren")
    if a["etat_administratif"] != "A": e.append("cessée")
    if a.get("statut_diffusion") != "O": e.append("non diffusible")
    if a.get("nature_juridique") == "1000": e.append("entrepreneur individuel")
    cat = x["categorie"]; naf = a.get("activite_principale")
    if cat not in LABELS: e.append("rubrique inconnue " + cat)
    if cat == "avocats" and naf != "69.10Z": e.append("avocats hors NAF 69.10Z : %s" % naf)
    if cat == "experts-comptables" and naf != "69.20Z": e.append("experts-comptables hors NAF 69.20Z : %s" % naf)
    if cat != "avocats" and naf == "69.10Z": e.append("NAF 69.10Z hors rubrique avocats")
    if 'data-category="%s"' % cat not in h or "<dt>Rubrique</dt><dd>%s</dd>" % html.escape(LABELS.get(cat, "?"), quote=True) not in h: e.append("rubrique affichée")
    rai = re.search(r"<dt>Raison</dt><dd>(.*?)</dd>", h, re.S).group(1)
    if cat not in ("avocats", "experts-comptables") and "Rubrique retenue d’après la catégorie des classements publics où la maison est citée (voir Mentions externes)." not in rai: e.append("raison : origine de la rubrique non dite")
    if "fa-src" not in rai or naf not in rai: e.append("raison de rubrique sans source ou sans le NAF du registre")
    h1 = html.unescape(re.search(r"<h1>(.*?)</h1>", h).group(1)); den = a["nom_raison_sociale"]
    site = re.search(r"<dt>Site officiel</dt><dd><a href=\"([^\"]+)\"", h)
    if "<dt>Dénomination</dt><dd>%s<small" % html.escape(den, quote=True) not in h: e.append("dénomination %r" % den)
    # Nom affiché : dénomination exacte du registre ; nom du site officiel (site qui publie le SIREN) ; nom de la structure à l'annuaire du barreau.
    if h1 != den and not site and not (cat == "avocats" and r.get("barreau") and plat(h1) != plat(den)): e.append("nom %r/%r" % (h1, den))
    if h1 != r["nom_usuel"]: e.append("nom différent de l'enregistrement")
    if "%s %s %s" % (s[:3], s[3:6], s[6:]) not in t: e.append("siren affiché")
    if fr(a["date_creation"]) not in t: e.append("création " + a["date_creation"])
    v = a["siege"].get("libelle_commune") or ""
    if v and plat(v) not in plat(re.search(r'id="identite">(.*?)</section>', h, re.S).group(1)): e.append("ville " + v)
    if not v and "<dt>Ville du siège</dt><dd>Non renseignée</dd>" not in h: e.append("ville inventée")
    if "Active au registre" not in t: e.append("statut")
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
    if not reg and "Non renseigné au registre consulté." not in bloc: e.append("dirigeants : mention d'absence manquante")
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
    if 'href="/p/' in h or s in pers: e.append("fiche personne")
    if re.search(r"\bavocate?s?\b|expert[- ]comptable", html.unescape(re.sub(r"<[^>]+>", " ", bloc)).replace(html.unescape(re.sub(r"<[^>]+>", " ", "")), ""), re.I) and not any(re.search(r"avocat|expert", (d_.get("denomination") or "") + (d_.get("qualite") or ""), re.I) for d_ in reg): e.append("titre professionnel dans le bloc dirigeants")
    # statuts réglementaires
    st = re.search(r'id="statuts">(.*?)</section>', h, re.S).group(1); stt = txt(st)
    if cat == "avocats":
        ba = r.get("barreau")
        if "ORIAS" in st: e.append("ORIAS sur une fiche avocats")
        if ba:
            if "<dt>Barreau</dt><dd>%s<small" % html.escape(ba["texte"]) not in st or not re.match(r"Inscrit (au barreau|aux barreaux) ", ba["texte"]): e.append("texte barreau")
            if not ba.get("sources") or len(ba["sources"]) != len(re.findall(r"\b(?:de|d’|des) ", ba["texte"])) - 0 and len(ba["sources"]) < 1: e.append("barreau sans source")
            for y in ba.get("sources") or []:
                if not y.get("url") or html.escape(y["url"], quote=True) not in st or ("consulté le " + fr(y["date"])) not in stt: e.append("source barreau non affichée")
                if not re.search(r"annuaire du barreau de %s|mentions légales du site officiel" % re.escape(y["barreau"]), y["label"]): e.append("libellé de source barreau")
                if y["barreau"] not in ba["texte"]: e.append("barreau hors texte")
            if len(st.split("fa-src")) - 1 != len(ba["sources"]): e.append("nb sources barreau")
        elif "Inscription au barreau : non renseignée." not in stt or "Inscrit" in stt: e.append("barreau non sourcé affiché")
    else:
        o = txt(fetch("https://www.orias.fr/home/showIntermediaire/%s" % s) or "")
        if not o: e.append("ORIAS injoignable")
        mo_ = re.search(r"N° Orias (\d{8})", o)
        if mo_ and (x.get("orias") != mo_.group(1) or ("N° " + mo_.group(1)) not in stt): e.append("orias %s/%s" % (mo_.group(1), x.get("orias")))
        if not mo_ and (x.get("orias") or "N° " in stt or "Aucune inscription retrouvée sous ce SIREN" not in stt): e.append("orias affiché sans inscription")
        if "Inscrit au barreau" in stt: e.append("barreau hors rubrique avocats")
    # identité et liens : chaque champ avec sa source, sinon « Non renseigné »
    for sec in ("identite", "liens"):
        for dd in re.findall(r"<div><dt>(.*?)</dt><dd>(.*?)</dd></div>", re.search(r'id="%s">(.*?)</section>' % sec, h, re.S).group(1)):
            if "fa-src" not in dd[1] and "Non renseigné" not in dd[1]: e.append("champ sans source : " + dd[0])
    if site and (hote(html.unescape(site.group(1))) != hote(r.get("site")) or s not in re.sub(r"\D", "", (r.get("siren_source") or {}).get("type", "") + r.get("site_source", "") + json.dumps(r.get("site_concordance", ""))) and not r.get("site_source")): e.append("site officiel")
    if bool(site) != bool(r.get("site")): e.append("site affiché sans enregistrement")
    # mentions externes
    me = re.search(r'<section aria-labelledby="fa-mentions" id="mentions-externes">(.*?)</section>', h, re.S)
    ms = r.get("mentions_externes") or []
    if cat == "experts-comptables":
        # Même gabarit que le lot experts-comptables : la citation est la preuve « classement public » du bloc « Lien avec la cession ».
        lc = re.search(r'id="lien-cession">(.*?)</section>', h, re.S); ps = (r.get("lien_cession") or {}).get("preuves") or []
        if me or ms or not lc or not ps: e.append("experts-comptables : lien avec la cession absent, ou bloc de mentions en double")
        else:
            if len(re.findall(r"<div><dt>", lc.group(1))) != len(ps): e.append("nb preuves affichées")
            for p_ in ps:
                if p_["critere"] != "d" or not p_["url"].startswith("https://www.leadersleague.com/fr/classements/") or p_["url"] not in html.unescape(lc.group(1)) or ("consulté le " + fr(p_["date"])) not in txt(lc.group(1)) or not re.match(r"^Cité dans le classement « .+ » de Leaders League, édition 20\d\d\.$", p_["texte"]): e.append("preuve de classement")
            if RANG.search(re.sub(r"Leaders League", "", txt(lc.group(1)))): e.append("rang ou niveau dans les preuves")
    elif not me or not ms: e.append("mentions externes absentes")
    else:
        lis = re.findall(r'<li><span style="text-align:left">(.*?)</span> <a href="([^"]+)" rel="noopener nofollow" style="white-space:nowrap" target="_blank">Voir le classement</a></li>', me.group(1))
        if len(lis) != len(ms) or len(re.findall(r"<li>", me.group(1))) != len(ms): e.append("nb mentions %d/%d" % (len(lis), len(ms)))
        for (tx, u), z in zip(lis, ms):
            g = MENTION.match(html.unescape(tx)); u = html.unescape(u)
            if not g: e.append("forme de la mention"); continue
            if u != z["url"] or not u.startswith("https://www.leadersleague.com/fr/classements/"): e.append("lien de la mention")
            if g.group(2) != z["edition"] or "%s-%s-%s" % (g.group(5), g.group(4), g.group(3)) != z["consulte_le"]: e.append("édition ou date de la mention")
            if plat(g.group(1)) not in plat(z["classement"]) and plat(re.sub(r"20\d\d|Classement", "", z["classement"])) != plat(g.group(1)): e.append("catégorie de la mention")
        if RANG.search(re.sub(r"Leaders League", "", txt(me.group(1)))): e.append("rang ou niveau dans les mentions")
        if "Elles n’entrent pas dans le classement de l’Annuaire" not in me.group(1): e.append("note des mentions absente")
        if h.index('id="mentions-externes"') < h.index('id="activite"'): e.append("mentions avant l'activité documentée")
    tete = h.split("</head>")[0] + re.search(r"<header class=\"pv-identity\">.*?</header>", h, re.S).group(0)
    if "Leaders League" in tete or "leadersleague" in tete: e.append("mention externe dans le titre, la description ou le JSON-LD")
    if cat != "experts-comptables" and h.count("Leaders League") != len(ms) + (1 if len(ms) > 3 else 0): e.append("Leaders League cité hors du bloc des mentions")
    if re.search(r"[\w.-]+@[\w-]+\.[a-z]{2,}|\b0[1-9](?:[ .]?\d\d){4}\b|\+33", re.sub(r"mailto:louis@exit\.club[^\"]*|louis@exit\.club", "", t)): e.append("coordonnée affichée")
    if "—" in t: e.append("tiret cadratin")
    if "Revendiquer ce profil" not in h or "sans effet sur le classement" not in h: e.append("bouton Revendiquer absent")
    if "Fiche générée à partir de sources publiques · non relue par la maison" not in t: e.append("bandeau")
    # doublons
    if cs[s] != 1 or cl[x["slug"]] != 1: e.append("doublon SIREN ou identifiant")
    if cn[plat(h1)] > 1: e.append("doublon de nom dans le répertoire")
    if not BASE and r.get("site"):
        autres = (dom_tous[hote(r["site"])] | dom_lot[hote(r["site"])]) - {x["slug"]}
        memes = sites.get(r["site"].rstrip("/").lower().replace("://www.", "://"), set()) - {x["slug"]}
        if memes or (autres - dom_lot[hote(r["site"])]): e.append("doublon de site : %s" % sorted(memes | autres))
    print("OK " if not e else "ERR", s, h1, "|", cat, e or "", flush=True)
    if e: err.append((s, e))
    time.sleep(0.35)
print("maisons relues", len(ech), "sur", len(lot), "· fiches en erreur", len(err))
json.dump(err, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
