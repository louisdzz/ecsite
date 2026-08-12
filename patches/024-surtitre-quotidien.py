# Ecosysteme: surtitre du second bloc, "La suite" devient "Le quotidien"
#
# "Le capital" nomme un domaine, "La suite" nommait une chronologie : le
# couple etait desequilibre. Le quotidien dit ce que le bloc contient
# vraiment, le trajet, l'ecole, la maison, le corps, le personnel.
import io, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s

A = '<p class="over">La suite</p>'
B = '<p class="over">Le quotidien</p>'

if s.count(A) != 1:
    print("ECHEC %d occurrence(s) de l'ancien surtitre au lieu de 1" % s.count(A))
    sys.exit(1)
if s.count(B):
    print("ECHEC le nouveau surtitre est deja present")
    sys.exit(1)

s = s.replace(A, B)

# controles de sortie
for balise, att in (
    (B, 1),
    (A, 0),
    ('<p class="over">Le capital</p>', 1),
    ("Je fais quoi de mon argent.", 1),
    ("Je fais quoi de ma vie.", 1),
    ('id="argent"', 1),
    ('id="vie"', 1),
    ('<div class="cats">', 2),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)

# le surtitre doit rester dans l'entete du bloc de la vie
i_vie = s.find('id="vie"')
i_sur = s.find(B)
i_h2 = s.find("Je fais quoi de ma vie.")
if not (i_vie < i_sur < i_h2):
    print("ECHEC surtitre hors de l'entete : %d %d %d" % (i_vie, i_sur, i_h2))
    sys.exit(1)

if len(s) != len(o) + len("Le quotidien") - len("La suite"):
    print("ECHEC variation de taille inattendue : %d -> %d" % (len(o), len(s)))
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : Le capital / Le quotidien")
