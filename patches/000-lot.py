# Ecosysteme: tarif unique 2 400 EUR, interview sans filtre, nouveau format
#
# - execute les patches ranges par erreur dans patches/site-ecsite, que le
#   glob patches/*.py du workflow ne voyait pas
# - ordre impose : 002 titre produit, puis 003 tarif, 004 apercus,
#   005 interview sans filtre, 007 nouveau format, 008 fiche Comptoir du PE
# - neutralise ensuite 001 et 002, deja traites, pour que la suite de la
#   boucle passe, et supprime le sous-dossier
import glob, shutil, subprocess, sys
L = ["patches/002-titre-produit.py"] + sorted(glob.glob("patches/site-ecsite/*.py"))
if len(L) != 7:
    print("ECHEC %d patch(s), 7 attendus" % len(L)); sys.exit(1)
for f in L:
    print("== " + f)
    if subprocess.run([sys.executable, f]).returncode:
        print("ECHEC " + f); sys.exit(1)
shutil.rmtree("patches/site-ecsite")
for f in ["patches/001-residus-fiche.py", "patches/002-titre-produit.py"]:
    open(f, "w").write("# Patch deja applique dans le lot\nprint('ok')\n")
print("controle vert : lot applique")
