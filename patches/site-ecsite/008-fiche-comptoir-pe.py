# Ecosysteme: fiche Le Comptoir du Private Equity (fonds de fonds PE)
#
# - nouvelle fiche f/comptoir-du-private-equity.html, categorie Fonds PE / LBO,
#   au nouveau format (sommaire, cinq blocs, appel a repondre)
# - construite en clonant la fiche fcde, de la meme categorie : le patch doit
#   donc etre applique APRES 005 et 007, sa garde le verifie
# - Reperes et Equipe dirigeante renseignes d'apres la documentation de
#   presentation du fonds (indicatif, non contractuel) : fonds de fonds small
#   cap Europe, FPS gere par Tygrow (AMF GP-20226), comite d'investissement
#   Lapouge / Meunier / Michal
# - les frais ne sont pas repris de la documentation : ils relevent des blocs
#   « interview sans filtre », declares et valides par la maison
# - ecosysteme.html passe a 318 fonds PE references et 4247 institutions,
#   sitemap.xml recoit l'URL

import os
import sys

e = []
NOM = "Le Comptoir du Private Equity"
SLUG = "comptoir-du-private-equity"
CIBLE = "f/%s.html" % SLUG

if os.path.exists(CIBLE):
    print("ECHEC : %s existe deja" % CIBLE)
    sys.exit(1)

s = open("f/fcde.html", encoding="utf-8").read()
for garde in ['<nav class="toc">',
              "Les chiffres sont ceux déclarés par la maison.",
              "cat=pe&institution=Fcde"]:
    if garde not in s:
        e.append("ECHEC f/fcde.html : %s absent, appliquer 005 et 007 avant 008"
                 % garde)
if e:
    print("\n".join(e))
    sys.exit(1)


def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        e.append("ECHEC %d/%d pour %s" % (c, n, a[:52]))
        return
    s = s.replace(a, b)


# 1. Reperes : le contenu reel remplace la carte generique.
REPERES_OLD = ('<div class="card"><div class="k">Repères</div><p>Fonds de '
               "Private Equity &amp; LBO : réinvestissement au capital de "
               'sociétés non cotées.</p><p style="margin-top:10px;font-size:'
               '13px"><a href="https://www.google.com/search?q=Fcde" '
               'target="_blank" rel="noopener nofollow">Site officiel</a> · '
               '<a href="https://www.linkedin.com/search/results/companies/'
               '?keywords=Fcde" target="_blank" rel="noopener nofollow">'
               "LinkedIn</a></p></div>")

REPERES_NEW = ('<div class="card"><div class="k">Repères</div><p>Fonds de '
               "fonds de private equity dédié au small cap européen : un "
               "portefeuille concentré de 8 à 10 gérants (buyout, croissance "
               "rentable, secondaire) sélectionnés au Royaume-Uni, dans les "
               "pays nordiques, au Benelux et en zone DACH, soit une "
               "exposition à 80-100 sociétés. Véhicule cible de 50 M€ sous "
               "forme de FPS (fonds professionnel spécialisé) géré par "
               "Tygrow, société de gestion agréée AMF (n° GP-20226), le "
               "Comptoir du Private Equity intervenant comme conseiller en "
               "investissements financiers (CIF).</p>"
               '<p style="margin-top:10px">Ticket d\'entrée à partir de '
               "500 000 €, premier closing visé au second semestre 2026. "
               "Réservé aux investisseurs professionnels ou avertis. "
               "Éléments indicatifs, non contractuels, d'après la "
               "documentation de présentation du fonds.</p>"
               '<p style="margin-top:10px;font-size:13px"><a href="https://'
               "www.google.com/search?q=%22Le%20Comptoir%20du%20Private%20"
               'Equity%22" target="_blank" rel="noopener nofollow">Site '
               'officiel</a> · <a href="https://www.linkedin.com/search/'
               "results/companies/?keywords=Comptoir%20du%20Private%20"
               'Equity" target="_blank" rel="noopener nofollow">LinkedIn</a>'
               "</p></div>")

EQUIPE = ('\n\n  <div class="card"><div class="k">Équipe dirigeante</div>'
          '<div class="pers"><div class="ava">JL</div><div><b>Jérémy '
          "Lapouge</b><span>Comité d'investissement · parcours Amundi, "
          "Société Générale Private Banking, Heritage</span></div></div>"
          '<div class="pers"><div class="ava">NM</div><div><b>Nicolas '
          "Meunier</b><span>Comité d'investissement · parcours Crédit "
          "Mutuel Equity, Dentressangle, Siparex, Reflexion Capital</span>"
          '</div></div><div class="pers"><div class="ava">IM</div><div>'
          "<b>Ivan Michal</b><span>Comité d'investissement · parcours "
          "Newfund, Rothschild &amp; Co, DC Advisory</span></div></div>"
          '<p style="margin-top:10px;font-size:11.5px;color:var(--faint)">'
          "Équipe identifiée d'après la documentation de présentation du "
          'fonds. <a href="mailto:louis@exit.club?subject=Profil%20'
          + SLUG + '%20·%20correction" style="color:var(--muted)">Une '
          "correction ? Écrivez-moi</a></p></div>")

sub(REPERES_OLD, REPERES_NEW + EQUIPE, 1)

# 2. Le nom, du plus specifique au plus general.
sub("institution=Fcde", "institution=Le%20Comptoir%20du%20Private%20Equity", 3)
sub("Réponse de Fcde ·", "Réponse du Comptoir du Private Equity ·", 3)
sub("Vous représentez Fcde ?", "Vous représentez le Comptoir du Private Equity ?", 1)
sub("Fcde", NOM, 5)   # title, meta description, og:title, JSON-LD, h1
sub("fcde", SLUG, 7)  # og:url, canonical, JSON-LD, fiche= x3, mailto

# 3. Les styles de la carte equipe, absents du gabarit fcde.
CSS_PERS = ("\n.pers{display:flex;gap:12px;align-items:center;padding:8px 0;"
            "border-bottom:1px solid #EFEBDB}\n"
            ".pers:last-child{border-bottom:0}\n"
            ".pers b{display:block;font-size:14px;color:var(--ink)}\n"
            ".pers span{display:block;font-size:12.5px;color:var(--muted)}\n"
            ".pers .ava{flex:none;width:38px;height:38px;border-radius:50%;"
            "background:#E7E2D0;color:var(--ink);display:flex;align-items:"
            "center;justify-content:center;font-size:13px;font-weight:600}\n")
sub("\n</style>", CSS_PERS + "</style>", 1)

if e:
    print("\n".join(e))
    sys.exit(1)
open(CIBLE, "w", encoding="utf-8").write(s)
print("ok %s cree" % CIBLE)

# 4. ecosysteme.html : entree dans la liste, compteur de categorie, totaux.
s = open("ecosysteme.html", encoding="utf-8").read()
ANCRE = '<li><a href="/f/l-catterton-europe-sas">L Catterton Europe SAS</a></li>'
LI = '<li><a href="/f/%s">%s</a></li>' % (SLUG, NOM)
sub(ANCRE, ANCRE + "\n      " + LI, 1)
sub('<div class="count"><b>317</b> référencés</div>',
    '<div class="count"><b>318</b> référencés</div>', 1)
c = s.count("4246")
if c < 1:
    e.append("ECHEC ecosysteme.html : total 4246 introuvable")
else:
    s = s.replace("4246", "4247")
    print("ok ecosysteme.html : %d total(aux) 4246 -> 4247" % c)
if e:
    print("\n".join(e))
    sys.exit(1)
open("ecosysteme.html", "w", encoding="utf-8").write(s)
print("ok ecosysteme.html : 318 fonds PE references")

# 5. sitemap.xml, trie par slug.
s = open("sitemap.xml", encoding="utf-8").read()
AV = "  <url><loc>https://www.exit.club/f/connect-pro</loc></url>"
U = "  <url><loc>https://www.exit.club/f/%s</loc></url>" % SLUG
sub(AV, U + "\n" + AV, 1)
if e:
    print("\n".join(e))
    sys.exit(1)
open("sitemap.xml", "w", encoding="utf-8").write(s)
print("ok sitemap.xml")

# --- controles de sortie ----------------------------------------------------
s = open(CIBLE, encoding="utf-8").read()
for x in ['<nav class="toc">', '<section class="sect" id="interview">',
          "Réponse du Comptoir du Private Equity ·",
          "cat=pe&institution=Le%20Comptoir",
          'rel="canonical" href="https://www.exit.club/f/%s"' % SLUG,
          ".pers{", "Jérémy Lapouge", "Nicolas Meunier", "Ivan Michal",
          "GP-20226", "Les chiffres sont ceux déclarés par la maison."]:
    if x not in s:
        e.append("ECHEC fiche : %s absent" % x)
for x in ["Fcde", "fcde"]:
    if x in s:
        e.append("ECHEC fiche : %s subsiste" % x)
if s.count('<section class="sect" id=') != 5:
    e.append("ECHEC fiche : %d bloc(s), 5 attendus"
             % s.count('<section class="sect" id='))
if s.count("0,8") or s.count("7,5 %"):
    e.append("ECHEC fiche : frais repris de la documentation, interdits ici")
s = open("ecosysteme.html", encoding="utf-8").read()
if s.count(LI) != 1:
    e.append("ECHEC ecosysteme.html : entree absente ou dupliquee")
s = open("sitemap.xml", encoding="utf-8").read()
if s.count("/f/%s<" % SLUG) != 1:
    e.append("ECHEC sitemap.xml : URL absente ou dupliquee")
if e:
    print("\n".join(e))
    sys.exit(1)
print("controle vert : fiche %s en ligne dans la categorie fonds PE" % SLUG)
