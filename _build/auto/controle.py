# Relecture indépendante : la fiche HTML publiée est comparée au registre et à l'ORIAS relus à l'instant ; pour une société de gestion, au registre et à la base GECO de l'AMF.
# Usage : python3 _build/auto/controle.py <json des SIREN déjà publiés> <taille échantillon> <sortie erreurs.json>, depuis la racine du dépôt.
import json,re,sys,html,time,random,urllib.request,ssl,os,unicodedata
CTX=ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or None)
def fetch(u):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (compatible; AnnuaireControle/1.0)"}),timeout=25,context=CTX) as r: return r.read().decode("utf-8","ignore")
        except Exception as e:
            time.sleep(10*(k+1) if "429" in str(e) else 3)
    return None
def plat(s): return re.sub(r"[^a-z0-9]+"," ",unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()).strip()
def txt(h): return html.unescape(re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",re.sub(r"<script.*?</script>|<style.*?</style>"," ",h,flags=re.S))))
MOIS="janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
m=json.load(open("_build/auto/manifeste.json"))
anciens=set(json.load(open(sys.argv[1])))
nouv=[x for x in m["maisons"] if x["siren"] not in anciens]
random.seed(2026111123)
BASE=sys.argv[4] if len(sys.argv)>4 else None  # 4e argument facultatif : relire les fiches en ligne (https://www.exit.club) au lieu des fichiers locaux
def lit(ch): return fetch("%s/%s"%(BASE,ch[:-5])) if BASE else open(ch,encoding="utf-8").read()
ech=random.sample(nouv,int(sys.argv[2]))
pers={}
for p in m["personnes"]: pers.setdefault(p["siren"],[]).append(p)
err=[];np=0;GECO=None
for x in ech:
    s=x["siren"]; h=lit(x["chemin"]); t=txt(h)
    a=json.loads(fetch("https://recherche-entreprises.api.gouv.fr/search?q=%s&per_page=1"%s))["results"][0]
    e=[]
    if a["siren"]!=s: e.append("siren")
    if a["etat_administratif"]!="A": e.append("cessée")
    if a.get("statut_diffusion")!="O": e.append("non diffusible")
    if a.get("nature_juridique")=="1000": e.append("entrepreneur individuel")
    h1=html.unescape(re.search(r"<h1>(.*?)</h1>",h).group(1))
    # Nom affiché : dénomination exacte du registre ; avec un site officiel vérifié sur la fiche, le nom du site est admis s'il ne diffère que par la casse et la ponctuation.
    if h1!=a["nom_raison_sociale"] and not ("Non renseigné" not in re.search(r'id="liens">(.*?)</section>',h,re.S).group(1).split("LinkedIn")[0] and plat(h1)==plat(a["nom_raison_sociale"])): e.append("nom %r/%r"%(h1,a["nom_raison_sociale"]))
    if "%s %s %s"%(s[:3],s[3:6],s[6:]) not in t: e.append("siren affiché")
    y,mo,d=a["date_creation"].split("-"); dc="%s %s %s"%("1er" if int(d)==1 else int(d),MOIS[int(mo)-1],y)
    if dc not in t: e.append("création "+dc)
    v=a["siege"].get("libelle_commune") or ""
    if plat(v) not in plat(t): e.append("ville "+v)
    # dirigeants : chaque personne physique du registre doit figurer, et aucune autre
    bloc=re.search(r'id="dirigeants">(.*?)</section>',h,re.S).group(1)
    aff=[plat(html.unescape(re.sub(r"<[^>]+>","",b))) for b in re.findall(r"<li><b>(.*?)</b>",bloc)]
    reg=[d_ for d_ in a.get("dirigeants") or [] if not re.search("commissaire aux comptes",d_.get("qualite") or "",re.I)]
    # un même mandat saisi deux fois au registre (même personne, même nom hors parenthèses, même qualité, prénoms identiques ou inclus) n'est affiché qu'une fois
    _v=[]; _r=[]
    for d_ in reg:
        k_=(d_.get("type_dirigeant"),plat(re.sub(r"\(.*?\)"," ",d_.get("nom") or d_.get("denomination") or "")),d_.get("siren") or "",plat(d_.get("qualite") or ""),plat(d_.get("prenoms") or ""))
        if any(k_[:4]==z[:4] and ((k_[4]+" ").startswith(z[4]+" ") or (z[4]+" ").startswith(k_[4]+" ")) for z in _v): continue
        _v.append(k_); _r.append(d_)
    reg=_r
    if any(len(z.split())>1 and z.split()[0]==z.split()[1] for z in aff): e.append("prénom doublé")
    if len(aff)!=len(reg): e.append("nb dirigeants %d/%d"%(len(aff),len(reg)))
    for d_ in reg:
        if d_.get("type_dirigeant")=="personne physique":
            pn=plat((d_.get("prenoms") or "").split()[0] if d_.get("prenoms") else ""); nm=plat(re.sub(r"\(.*?\)","",d_.get("nom") or ""))
            # le registre range parfois le prénom dans le champ nom : « BENOIT PAILLET (PAILLET) » se lit Paillet, « CHRISTOPHE (LAUVERGEON) » se lit Lauvergeon
            par_=plat(" ".join(re.findall(r"\((.*?)\)",d_.get("nom") or "")))
            if par_ and pn and nm==pn+" "+par_: nm=par_
            elif par_ and pn and nm==pn and par_!=pn: nm=par_
            if not any(pn in z and nm in z for z in aff): e.append("dirigeant absent "+nm)
            if "(" in (d_.get("nom") or "") and plat(re.search(r"\((.*?)\)",d_["nom"]).group(1)) in plat(bloc) and plat(re.search(r"\((.*?)\)",d_["nom"]).group(1)) not in nm: e.append("nom entre parenthèses affiché")
    if re.search(r"\b(né|née) (le|en)\b|\d{2}/\d{2}/19\d\d",bloc): e.append("date de naissance")
    time.sleep(0.6)
    if x.get("amf"):
        # Société de gestion : l'agrément affiché est comparé à la base GECO de l'AMF relue à l'instant (liste et page détail).
        am=json.load(open("_build/auto/donnees/%s.json"%s,encoding="utf-8"))["amf"]; idt=int(am["url"].rsplit("/",1)[1])
        if GECO is None: GECO={z["idThirdParty"]:z for z in json.loads(fetch("https://geco.amf-france.org/back-office/thirdParties?isSdgFr=true"))}
        g=GECO.get(idt); gd=json.loads(fetch("https://geco.amf-france.org/back-office/thirdParties/%s"%idt) or "{}")
        if not g: e.append("absente de la liste AMF")
        else:
            if g["agreementNum"]!=x["amf"] or ("N° "+x["amf"]) not in t: e.append("agrément AMF %s/%s"%(g["agreementNum"],x["amf"]))
            if not re.match(r"GP-?\d{4,8}$",x["amf"]): e.append("numéro hors format GP")
            y2,m2,d2=g["agreementDate"][:10].split("-")
            if "%s %s %s"%("1er" if int(d2)==1 else int(d2),MOIS[int(m2)-1],y2) not in t: e.append("date d'agrément "+g["agreementDate"])
            if (g["roleStatusDTO"] or [{}])[0].get("status")!="VIV": e.append("statut AMF "+str((g["roleStatusDTO"] or [{}])[0].get("status")))
            if plat(g["name"])!=plat(am["denomination"]): e.append("dénomination AMF %r"%g["name"])
        sa=re.sub(r"\D","",gd.get("siren") or "")[:9]
        if sa and sa!=s: e.append("SIREN AMF %s"%sa)
        if am["url"] not in html.unescape(h): e.append("lien GECO absent")
        if "ORIAS" in re.search(r'id="statuts">(.*?)</section>',h,re.S).group(1): e.append("mention ORIAS sur une fiche SGP")
        if "—" in t: e.append("tiret cadratin")
    else:
        o=txt(fetch("https://www.orias.fr/home/showIntermediaire/%s"%s) or "")
        mo_=re.search(r"N° Orias (\d{8})",o)
        if not mo_ or mo_.group(1)!=x["orias"] or ("N° "+x["orias"]) not in t: e.append("orias %s/%s"%(mo_ and mo_.group(1),x["orias"]))
        if not re.search(r"\bCIF [^.]{8,90}? Inscrit le \d{2}/\d{2}/\d{4}",o): e.append("CIF non inscrit à l'ORIAS")
    # fiches personnes de la maison
    for p in pers.get(s,[]):
        np+=1; hp=lit(p["chemin"]); tp=txt(hp)
        cand=[d_ for d_ in reg if d_.get("type_dirigeant")=="personne physique" and plat(p["nom"])==plat(((d_.get("prenoms") or "").split() or [""])[0]+" "+re.sub(r"\(.*?\)","",d_.get("nom") or ""))]
        if len(cand)!=1: e.append("personne %s introuvable au registre"%p["slug"]); continue
        q=cand[0].get("qualite") or ""
        if q!=p["fonction"] or html.escape(q) not in hp and q not in tp: e.append("fonction %s : %r/%r"%(p["slug"],p["fonction"],q))
        if not re.match(r"(?i)(pr[ée]sident|g[ée]rant|co-?g[ée]rant|directeur g[ée]n[ée]ral)",q): e.append("fonction hors périmètre "+p["slug"])
        if h1 not in html.unescape(hp): e.append("maison absente fiche "+p["slug"])
        if re.search(r"\b(né|née) (le|en)\b|@|\b0[1-9](?:[ .]?\d\d){4}\b",re.sub(r"mailto:louis@exit\.club[^\"]*|louis@exit\.club","",tp)): e.append("donnée personnelle "+p["slug"])
    print("OK " if not e else "ERR",s,h1,"|",len(pers.get(s,[])),"pers.",e or "",flush=True)
    if e: err.append((s,e))
    time.sleep(0.6)
print("maisons relues",len(ech),"sur",len(nouv),"· personnes relues",np,"· fiches en erreur",len(err))
json.dump(err,open(sys.argv[3],"w"),ensure_ascii=False)
