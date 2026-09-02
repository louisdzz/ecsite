# Ecosysteme: fiche RockFi, le bloc 4 adopte le wording valide par la
# maison (mail d'Alice Megret)
#
# Le label du KPI devient factuel ("audites par RockFi") et la phrase de
# positionnement proposee par la maison est publiee entre guillemets,
# mot pour mot, juste au-dessus de l'attribution.
# Prerequis : patch 044 deja applique.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "gestion lisible, transparente" in s:
    print("existe deja : wording bloc 4 en place, rien a faire")
    sys.exit(0)
if 'class="lk"' not in s:
    print("ECHEC : deposer d'abord le patch 044")
    sys.exit(1)

A = ("constaté sur les portefeuilles entrants audités par la maison. "
     "Le chiffre qui mesure ce que coûte le marché, avant elle.</span>\n"
     "      </div>\n"
     '      <p style="margin-top:12px">')
if s.count(A) != 1:
    print("ECHEC %d occurrence(s) de l'ancre bloc 4" % s.count(A))
    sys.exit(1)

s = s.replace(A,
    "constaté sur les portefeuilles entrants audités par "
    "RockFi.</span>\n"
    "      </div>\n"
    '      <p style="margin-top:12px;font-size:14.5px;'
    'color:var(--ink);line-height:1.6">« Au-delà des frais, nous '
    "défendons une gestion lisible, transparente et plus exigeante dans "
    "son accompagnement. »</p>\n"
    '      <p style="margin-top:10px">', 1)

for balise, att in (
    ("audités par RockFi", 1),
    ("gestion lisible, transparente", 1),
    ("Le chiffre qui mesure ce que coûte le marché", 0),
    ("Communiqué par la maison · millésime 2026", 1),
    ("20 pb", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : bloc 4 aux mots de la maison, attribution conservee")
