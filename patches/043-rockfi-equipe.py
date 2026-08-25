# Ecosysteme: fiche RockFi, le bloc equipe suit le retour de la maison
#
# Les trois cofondateurs entrent (Pierre Marin CEO, Marie Bedu COO,
# Maxime Durand CTO), les trois partners associes sont mis en avant
# (Stephane Carles, Bertrand Breavoine, Yann Garnier), Rene Vignau
# Loustau et Delphine Colin sortent. Une ligne d'intro dit la
# complementarite tech / banque privee, reprise de leurs propres mots.
# Le bloc 4 ne bouge pas : reformulation en attente de leur validation.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "Marie Bedu" in s:
    print("existe deja : equipe a jour, rien a faire")
    sys.exit(0)

for balise, att in (
    ("Pierre Marin", 1),
    ("René Vignau Loustau", 1),
    ("Delphine Colin", 1),
    ('<section class="sect" id="etiquette">', 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:40], att))
        sys.exit(1)

deb = s.rindex('<div class="card">', 0, s.index("Pierre Marin"))
fin = s.index('<section class="sect" id="etiquette">')
if not (0 < fin - deb < 1600):
    print("ECHEC bloc equipe de taille inattendue (%d)" % (fin - deb))
    sys.exit(1)


def pers(ini, nom, role, lien=""):
    a = ('<a href="' + lien + '" target="_blank" rel="noopener">LinkedIn'
         '</a>') if lien else ""
    return ('<div class="pers"><div class="ava">' + ini + '</div><div><b>'
            + nom + '</b><span>' + role + '</span>' + a + '</div></div>')


bloc = (
    '<div class="card"><div class="k">L’équipe</div>'
    '<p style="font-size:13.5px;color:var(--muted);margin:2px 0 10px">'
    'Une maison à deux moteurs : des fondateurs issus de la tech, qui '
    'construisent l’outil, et des partners issus de la banque '
    'privée, qui accompagnent les familles.</p>'
    + pers("PM", "Pierre Marin", "Co-fondateur &amp; CEO",
           "https://fr.linkedin.com/in/pierre-marin-rockfi")
    + pers("MB", "Marie Bedu", "Co-fondatrice &amp; COO")
    + pers("MD", "Maxime Durand", "Co-fondateur &amp; CTO")
    + pers("SC", "Stéphane Carles", "Partner associé")
    + pers("BB", "Bertrand Bréavoine", "Partner associé")
    + pers("YG", "Yann Garnier", "Partner associé")
    + '</div>\n\n  ')

s = s[:deb] + bloc + s[fin:]

for balise, att in (
    ("Marie Bedu", 1),
    ("Maxime Durand", 1),
    ("Bertrand Bréavoine", 1),
    ("Yann Garnier", 1),
    ("Stéphane Carles", 1),
    ("Partner associé", 3),
    ("René Vignau Loustau", 0),
    ("Delphine Colin", 0),
    ("deux moteurs", 1),
    ("pierre-marin-rockfi", 1),
    ('class="pers"', 6),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:40], att))
        sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : six profils, deux moteurs, deux sorties")
