# Accueil: menu mobile, la navigation etait invisible sous 760px
#
# Une seule ligne de CSS masquait toute la navigation sur mobile :
#   @media(max-width:760px){ .nav-links a:not(.btn){display:none} }
# Seul le bouton « Rejoindre » restait. Six liens disparaissaient, dont
# « L'Ecosysteme », qui pointe vers les 4 236 fiches d'acteurs, l'actif le plus
# travaille du site. Un visiteur mobile ne pouvait ni le decouvrir, ni lire le
# manifeste, ni voir les evenements : il n'avait que le bouton d'adhesion,
# demande a quelqu'un qui ne sait pas encore ce qu'est le club.
#
# - bouton d'ouverture visible uniquement sous 760px
# - panneau deroulant reprenant les six liens, dans la charte de la page
# - fermeture au clic sur un lien (la page navigue par ancres), sur le fond,
#   ou avec la touche Echap
# - aucun changement au-dessus de 760px : la barre reste identique
#
# Accessibilite : le bouton porte aria-expanded et aria-controls, le panneau
# est masque a la lecture quand il est ferme.

import re
import sys

echecs = []

p = "index.html"
try:
    s = open(p, encoding="utf-8").read()
except FileNotFoundError:
    print("ECHEC: index.html introuvable")
    sys.exit(1)


def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        echecs.append(
            "ECHEC: « %s » attendu %d fois, trouve %d" % (a[:70].replace("\n", "\\n"), n, c)
        )
        return
    s = s.replace(a, b)
    print("  ok  %dx  %s" % (c, a[:70].replace("\n", "\\n")))


# ------------------------------------------------------------------ CSS
sub(
    "  @media(max-width:760px){ .nav-links a:not(.btn){display:none} }\n",
    "  /* Sous 760px, les liens passent dans le panneau deroulant ouvert par le\n"
    "     bouton ci-dessous. Sans lui, la navigation etait simplement absente. */\n"
    "  .burger{display:none;background:none;border:1px solid var(--line);border-radius:8px;\n"
    "    padding:7px 9px;cursor:pointer;line-height:0}\n"
    "  .burger span{display:block;width:18px;height:1.5px;background:var(--ink);margin:3.5px 0;\n"
    "    transition:transform .25s ease,opacity .2s ease}\n"
    "  .burger[aria-expanded=\"true\"] span:nth-child(1){transform:translateY(5px) rotate(45deg)}\n"
    "  .burger[aria-expanded=\"true\"] span:nth-child(2){opacity:0}\n"
    "  .burger[aria-expanded=\"true\"] span:nth-child(3){transform:translateY(-5px) rotate(-45deg)}\n"
    "  @media(max-width:760px){\n"
    "    .burger{display:block}\n"
    "    .nav-links{position:absolute;top:100%;left:0;right:0;display:none;\n"
    "      flex-direction:column;align-items:stretch;gap:0;\n"
    "      background:var(--paper);border-bottom:1px solid var(--line);\n"
    "      padding:6px 22px 18px;font-size:15px}\n"
    "    .nav-links.open{display:flex}\n"
    "    .nav-links a{padding:13px 0;border-bottom:1px solid var(--line)}\n"
    "    .nav-links a:last-child{border-bottom:none;margin-top:12px;text-align:center}\n"
    "  }\n",
    1,
)

# ------------------------------------------------------------------ HTML
sub(
    '      <a class="logo" href="#top"><i>exit</i><b>.club</b></a>\n'
    '      <div class="nav-links">',
    '      <a class="logo" href="#top"><i>exit</i><b>.club</b></a>\n'
    '      <button class="burger" id="burger" aria-expanded="false" aria-controls="nav-links"\n'
    '        aria-label="Ouvrir le menu"><span></span><span></span><span></span></button>\n'
    '      <div class="nav-links" id="nav-links">',
    1,
)

# ------------------------------------------------------------------- JS
# On insere le script juste avant la fermeture du body.
if "</body>" not in s:
    echecs.append("ECHEC: pas de </body> dans index.html")
else:
    if s.count("</body>") != 1:
        echecs.append("ECHEC: %d occurrences de </body>, attendu 1" % s.count("</body>"))
    else:
        script = (
            "<script>\n"
            "// Menu mobile. La barre est en position sticky : le panneau se place en\n"
            "// dessous et se referme des qu'on navigue, la page fonctionnant par ancres.\n"
            "(function(){\n"
            "  var b = document.getElementById('burger');\n"
            "  var m = document.getElementById('nav-links');\n"
            "  if(!b || !m) return;\n"
            "  function ferme(){ m.classList.remove('open'); b.setAttribute('aria-expanded','false');\n"
            "    b.setAttribute('aria-label','Ouvrir le menu'); }\n"
            "  b.addEventListener('click', function(){\n"
            "    var ouvert = m.classList.toggle('open');\n"
            "    b.setAttribute('aria-expanded', ouvert ? 'true' : 'false');\n"
            "    b.setAttribute('aria-label', ouvert ? 'Fermer le menu' : 'Ouvrir le menu');\n"
            "  });\n"
            "  m.addEventListener('click', function(e){ if(e.target.tagName === 'A') ferme(); });\n"
            "  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') ferme(); });\n"
            "  document.addEventListener('click', function(e){\n"
            "    if(!m.contains(e.target) && !b.contains(e.target)) ferme();\n"
            "  });\n"
            "})();\n"
            "</script>\n"
            "</body>"
        )
        s = s.replace("</body>", script)
        print("  ok  1x  script du menu mobile insere avant </body>")

# ------------------------------------------------------------ controles
if not echecs:
    if "nav-links a:not(.btn){display:none}" in s:
        echecs.append("ECHEC: l'ancienne regle qui masquait la navigation subsiste")
    for attendu in ('id="burger"', 'id="nav-links"', ".nav-links.open{display:flex}"):
        if attendu not in s:
            echecs.append("ECHEC: « %s » absent du resultat" % attendu)
    # la nav ne doit pas se dupliquer
    if s.count('class="nav-links"') != 1:
        echecs.append("ECHEC: la barre de navigation apparait plusieurs fois")

if echecs:
    print()
    for e in echecs:
        print(e)
    sys.exit(1)

open(p, "w", encoding="utf-8").write(s)
print("\nTermine : la navigation est accessible sur mobile.")
