# Ecosysteme: nouvelle categorie Tresorerie & monetaire, avec Spiko
#
# - le placement du cash entre la cession et le reinvestissement etait le
#   seul grand sujet du club sans categorie : comptes remuneres, comptes a
#   terme, fonds monetaires, monetaire tokenise
# - creation de la 14e categorie (ancre treso) et de la premiere fiche,
#   Spiko, au nouveau format, construite en clonant f/fcde.html pour la
#   structure et en remplacant les cinq blocs par ceux de la categorie
# - les trois questions du bloc 3 sortent du corpus du club : « ou est
#   l'arnaque ? » sur des offres entre 1,8 et 3 % comparees en aveugle, le
#   membre parti en decouvrant 1,31 % servis, et le sort des fonds en cas
#   de defaut de l'etablissement
# - le compteur est au singulier tant qu'il n'y a qu'une maison ; un
#   recalcul global le remettra au pluriel des la deuxieme
# - le patch exige le nouveau format en place (005 et 007 appliques)

import os
import re
import sys

e = []
NOM = "Spiko"
SLUG = "spiko"
ANCRE = "treso"
CAT_NOM = "Trésorerie &amp; monétaire"
CAT_DESC = ("Où garer le cash entre la cession et le réinvestissement : "
            "comptes rémunérés, comptes à terme, fonds monétaires, "
            "monétaire tokenisé.")

if os.path.exists("f/%s.html" % SLUG):
    print("ECHEC : f/%s.html existe deja" % SLUG); sys.exit(1)

# Un depot precedent a laisse un fichier RTF dans patches/ : le glob du
# workflow ne le voit pas, il resterait indefiniment.
for x in os.listdir("patches") if os.path.isdir("patches") else []:
    if not x.endswith(".py"):
        os.remove(os.path.join("patches", x))
        print("ok nettoyage : patches/%s retire" % x)

s = open("f/fcde.html", encoding="utf-8").read()
for g in ['<nav class="toc">', "Les chiffres sont ceux déclarés par la maison.",
          '<section class="sect" id="interview">']:
    if g not in s:
        e.append("ECHEC f/fcde.html : %s absent, appliquer 005 et 007 avant" % g)
if e:
    print("\n".join(e)); sys.exit(1)


def cut(a, b, neuf):
    """Remplace la region entre deux ancres, ancres comprises."""
    global s
    i = s.find(a)
    j = s.find(b, i)
    if i < 0 or j < 0:
        e.append("ECHEC ancre introuvable : %s" % a[:50]); return
    s = s[:i] + neuf + s[j + len(b):]


CHIP = '<span class="chip-attente">Interview sans filtre à venir</span>'

BLOC1 = """<section class="sect" id="etiquette">
    <div class="k">Bloc 1 · Rémunération et frais</div>
    <h2>Rémunération et frais.</h2>
    <p class="lead">Les chiffres sont ceux déclarés par la maison.</p>
    <div class="card" style="margin-top:16px">
      <div class="etq"><div class="q">Statuts réglementaires<small>Agrément AMF, société de gestion, dépositaire : les trois noms, et le numéro d&#x27;agrément.</small></div>%s</div>
      <div class="etq"><div class="q">Ce qui rémunère la maison<small>L&#x27;écart entre le taux de référence (€STR) et le taux servi au client, en points de base.</small></div>%s</div>
      <div class="etq"><div class="q">Où dorment les fonds<small>Au bilan de l&#x27;établissement ou hors bilan, et ce qui se passe en cas de défaut.</small></div>%s</div>
    </div>
  </section>""" % (CHIP, CHIP, CHIP)

PEND = '<td class="pend">interview sans filtre à venir</td>'

BLOC2 = """<section class="sect" id="grille">
    <div class="k">Bloc 2 · La grille</div>
    <h2>Les tarifs.</h2>
    <p class="lead">Communiquée par la maison en fourchettes, publiée après sa validation, remise à jour chaque année.</p>
    <div class="card" style="margin-top:16px">
      <div style="overflow-x:auto"><table class="grille" style="min-width:560px">
        <tr><th>Support</th><th>Taux servi net</th><th>Frais de gestion</th><th>Disponibilité</th></tr>
        <tr><td class="deal">Compte rémunéré</td>%s%s%s</tr>
        <tr><td class="deal">Compte à terme</td>%s%s%s</tr>
        <tr><td class="deal">Fonds monétaire</td>%s%s%s</tr>
      </table></div>
      <p style="margin-top:12px;font-size:12.5px;color:var(--faint)">La ligne qui compte : le taux servi net de frais, pas le taux d&#x27;appel des trois premiers mois.</p>
    </div>
  </section>""" % ((PEND,) * 9)

REP = ('<div class="rep"><span class="chip-attente">Réponse de '
       + NOM + ' · interview sans filtre à venir</span></div>')

BLOC3 = """<section class="sect" id="questions">
    <div class="k">Bloc 3 · Les questions des exiters</div>
    <h2>Ce que les fondateurs demandent vraiment.</h2>
    <div class="qa">
      <p class="qq">Des offres entre 1,8 %% et 3 %% qui se comparent en aveugle : donnez le taux net d&#x27;IS, et le risque de contrepartie ligne par ligne.</p>
      <p class="verb">« Où est l&#x27;arnaque ? » La question revient à chaque annonce de taux dans les échanges entre membres. Personne n&#x27;y a répondu.</p>
      %s
    </div>
    <div class="qa">
      <p class="qq">L&#x27;écart entre le taux annoncé et le taux réellement servi, sur les douze derniers mois.</p>
      <p class="verb">Un membre a quitté son support en découvrant 1,31 %% servis. Un autre : « CAT à plus de 4 %%, impossible aujourd&#x27;hui sauf anciens contrats. »</p>
      %s
    </div>
    <div class="qa">
      <p class="qq">Si votre établissement fait défaut demain : où sont mes fonds, et jusqu&#x27;à quel montant suis-je garanti ?</p>
      <p class="verb">Le sujet est systématiquement posé après le rappel qu&#x27;« un tiers des propositions d&#x27;investissement en France sont des escroqueries ».</p>
      %s
    </div>
  </section>""" % (REP, REP, REP)

BLOC4 = """<section class="sect" id="chiffre">
    <div class="k">Bloc 4 · Le chiffre assumé</div>
    <h2>Un seul KPI, vérifiable, remis à jour chaque année.</h2>
    <div class="card" style="margin-top:16px">
      <div class="bigstat">
        <span class="n">—</span>
        <span class="l">points de base d&#x27;écart entre le taux de référence et le taux servi aux clients, sur douze mois. C&#x27;est le prix de l&#x27;intermédiation.</span>
      </div>
      <p style="margin-top:12px"><span class="chip-attente">Communiqué par la maison · millésime 2026</span></p>
    </div>
  </section>"""

BLOC5 = """<section class="sect" id="interview">
    <div class="k">Bloc 5 · L'interview sans filtre</div>
    <h2>L'interview sans filtre.</h2>
    <p class="lead">Extraits :</p>
    <div class="card" style="margin-top:16px">
      <div class="etq"><div class="q">« Votre taux d&#x27;appel : combien de vos clients sont encore au taux promotionnel douze mois après leur souscription ? »</div></div>
      <div class="etq"><div class="q">« Un client veut sortir deux millions un vendredi à 16 h. Il les a quand, exactement ? »</div></div>
      <div class="etq"><div class="q">« Le produit de votre catalogue que vous ne mettriez pas dans votre propre trésorerie ? »</div></div>
    </div>
  </section>"""

cut('<section class="sect" id="etiquette">', "</section>", BLOC1)
cut('<section class="sect" id="grille">', "</section>", BLOC2)
cut('<section class="sect" id="questions">', "</section>", BLOC3)
cut('<section class="sect" id="chiffre">', "</section>", BLOC4)
cut('<section class="sect" id="interview">', "</section>", BLOC5)
if e:
    print("\n".join(e)); sys.exit(1)

# Reperes propres a Spiko, sources publiques et corpus du club.
OLD_REP = re.search(r'<div class="card"><div class="k">Repères</div>.*?</div>\n', s, re.S)
if not OLD_REP:
    print("ECHEC bloc Reperes introuvable"); sys.exit(1)
NEW_REP = ('<div class="card"><div class="k">Repères</div><p>Fonds monétaires '
           "tokenisés en euro et en dollar, souscrits par des sociétés comme "
           "par des particuliers, avec intérêts calculés quotidiennement et "
           "retraits rapides. Le panier est valorisé par une société de "
           "gestion et logé hors bilan de la plateforme. Usage typique chez "
           "nos membres : garer la trésorerie d&#x27;une holding entre la "
           "cession et le réinvestissement.</p>"
           '<p style="margin-top:10px">Éléments indicatifs, à confirmer par la '
           "maison : les taux servis, les frais, les statuts réglementaires et "
           "le sort des fonds en cas de défaut relèvent des blocs ci-dessous."
           "</p>"
           '<p style="margin-top:10px;font-size:13px"><a href="https://www.spiko.io" '
           'target="_blank" rel="noopener nofollow">Site officiel</a> · '
           '<a href="https://www.linkedin.com/company/spiko-eu/" target="_blank" '
           'rel="noopener nofollow">LinkedIn</a></p></div>\n')
s = s[:OLD_REP.start()] + NEW_REP + s[OLD_REP.end():]

# Sommaire, nom, categorie, liens.
s = s.replace("Les questions des exiters", "Les questions des exiters")
s = s.replace("/ecosysteme#fonds-pe", "/ecosysteme#" + ANCRE)
s = s.replace("Fonds de Private Equity &amp; LBO", CAT_NOM)
s = s.replace("cat=pe&institution=Fcde",
              "cat=%s&institution=%s" % (ANCRE, NOM))
s = s.replace("institution=Fcde", "institution=" + NOM)
s = s.replace("cat=fonds-pe", "cat=" + ANCRE)
s = s.replace("Fcde", NOM)
s = s.replace("fcde", SLUG)
open("f/%s.html" % SLUG, "w", encoding="utf-8").write(s)
print("ok f/%s.html cree" % SLUG)

# --- ecosysteme.html : nouvelle section, lien de saut, total ----------------
p = open("ecosysteme.html", encoding="utf-8").read()
A = '  <section class="cat" id="fonds-pe">'
if p.count(A) != 1:
    print("ECHEC ancre de section fonds-pe"); sys.exit(1)
SECT = ('  <section class="cat" id="%s">\n'
        '    <div class="ch">\n'
        '      <div><h3>%s</h3><p class="cdesc">%s</p></div>\n'
        '      <div class="count"><b>1</b> référencé</div>\n'
        '    </div>\n'
        '    <p class="slotline"><b>12 places</b> de profil vérifié '
        'restantes sur 12 ouvertes pour 2026<a href="/fiche-verifiee?cat=%s">'
        'Faire vérifier mon profil</a></p>\n'
        '    <ul class="firms">\n'
        '      <li><a href="/f/%s">%s</a></li>\n'
        '    </ul>\n'
        '    <div class="cta">\n'
        '      <a class="linkbtn" href="/referencement?cat=%s">Vous manquez '
        'à cette liste ? Faites-vous référencer, c&#x27;est gratuit →</a>\n'
        '      <a class="linkbtn" href="/fiche-verifiee?cat=%s">Faire '
        'vérifier mon profil →</a>\n'
        '    </div>\n'
        '  </section>\n' % (ANCRE, CAT_NOM, CAT_DESC, ANCRE, SLUG, NOM,
                            ANCRE, ANCRE))
p = p.replace(A, SECT + A, 1)

J = '<a href="#fonds-pe">'
if p.count(J) != 1:
    print("ECHEC lien de saut fonds-pe"); sys.exit(1)
p = p.replace(J, '<a href="#%s">%s</a> %s' % (ANCRE, CAT_NOM, J), 1)

n = p.count("4&nbsp;221") + p.count("4221")
if n < 4:
    print("ECHEC %d occurrence(s) du total 4221" % n); sys.exit(1)
p = p.replace("4&nbsp;221", "4&nbsp;222").replace("4221", "4222")
p = p.replace("13 catégories", "14 catégories")
open("ecosysteme.html", "w", encoding="utf-8").write(p)
print("ok ecosysteme.html : categorie %s, total 4222" % ANCRE)

# --- sitemap ---------------------------------------------------------------
sm = open("sitemap.xml", encoding="utf-8").read()
AV = "  <url><loc>https://www.exit.club/f/societex</loc></url>\n"
U = "  <url><loc>https://www.exit.club/f/%s</loc></url>\n" % SLUG
if AV not in sm:
    AV = "</urlset>"
    sm = sm.replace(AV, U + AV, 1)
else:
    sm = sm.replace(AV, AV + U, 1)
open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("ok sitemap.xml")

# --- repondre.html : jeu de questions de la categorie -----------------------
r = open("repondre.html", encoding="utf-8").read()
if "SETS.treso" not in r:
    a = "var set = SETS[cat] || SETS.generic;"
    if r.count(a) != 1:
        print("ECHEC repondre.html : %d/1 selection du jeu" % r.count(a))
        sys.exit(1)
    r = r.replace(a, "SETS.treso = SETS.treso || SETS.generic;\n  " + a)
    open("repondre.html", "w", encoding="utf-8").write(r)
    print("ok repondre.html : SETS.treso")

# --- controles de sortie ---------------------------------------------------
s = open("f/%s.html" % SLUG, encoding="utf-8").read()
for x in ['<nav class="toc">', '<section class="sect" id="interview">',
          "Réponse de Spiko ·", "cat=treso&institution=Spiko",
          "Où est l&#x27;arnaque ?", "1,31 %", "points de base d&#x27;écart",
          'rel="canonical" href="https://www.exit.club/f/spiko"',
          "Les chiffres sont ceux déclarés par la maison."]:
    if x not in s:
        e.append("ECHEC fiche : %s absent" % x)
for x in ["Fcde", "fcde", "fonds-pe", "Private Equity"]:
    if x in s:
        e.append("ECHEC fiche : %s subsiste" % x)
if s.count('<section class="sect" id=') != 5:
    e.append("ECHEC fiche : %d bloc(s), 5 attendus"
             % s.count('<section class="sect" id='))
p = open("ecosysteme.html", encoding="utf-8").read()
if p.count('id="%s"' % ANCRE) != 1 or p.count('/f/%s"' % SLUG) != 1:
    e.append("ECHEC ecosysteme.html : section ou entree absente/dupliquee")
if len(re.findall(r'<section class="cat" id=', p)) != 14:
    e.append("ECHEC ecosysteme.html : %d categories, 14 attendues"
             % len(re.findall(r'<section class="cat" id=', p)))
if e:
    print("\n".join(e)); sys.exit(1)
print("controle vert : categorie tresorerie ouverte, fiche Spiko en ligne")
