# Présentation commune des maisons

Modèle approuvé par Louis le 6 octobre 2026, à partir de la fiche IBC Aviation.

Après création ou régénération de fiches, exécuter `python3 _build/normalise_profils.py --all` (Python avec BeautifulSoup). Pour une vérification limitée, passer les slugs en arguments. Le script est idempotent et ne modifie pas les données du CRM ni celles du moteur de recherche.

Le style commun est dans `assets/maison/profil-commun.css`. Les sections sont affichées selon le contenu existant. Aucun entretien, prix, contact ni statut commercial ne doit être inventé. Les questions non répondues restent signalées comme telles. Les logos officiels existants sont repris ; à défaut, le nom sert de cartouche typographique.

Le script contrôle la conservation des textes, liens et anciennes ancres avant chaque écriture. Avant publication, vérifier aussi les métadonnées et scripts, puis un exemple de banque, fonds, conseil M&A et lifestyle sur ordinateur et mobile.
