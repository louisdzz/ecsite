# Présentation visuelle des fiches

Version validée par Louis le 19 octobre 2026 sur Spiko, puis publication et déclinaison sur toutes les fiches explicitement demandées.

Le générateur conserve le dossier d’origine, ses textes, liens, ancres et métadonnées. Le nouveau haut de page utilise une présentation existante propre à la maison quand elle est disponible. Sinon, il décrit explicitement le métier et signale les particularités restant à documenter. Les schémas de catégorie sont des repères de métier, pas des promesses propres à chaque maison.

## Utilisation

Après la création ou la régénération d’une fiche, exécuter `python3 _build/normalise_profils.py nom-de-la-fiche`. La normalisation appelle désormais le générateur visuel. Pour traiter un lot : `python3 _build/build_visual_profiles.py --all`.

Une fiche portant déjà `data-profile-design="visual-20261019"` est préservée. Les changements éditoriaux ne doivent pas être écrasés par une ancienne copie. L’option `--source-directory` est réservée à la reconstruction d’une version en cours de revue, à partir de sa version de départ identifiée.

Les données de catégorie sont dans `categories.json`. L’extraction conservative du contenu existant est dans `content.py`. Les redirections et les démonstrations fictives ne sont pas transformées. Le fichier `spiko-approved.html` est la version du prototype approuvée, utilisée uniquement lors de sa première intégration ; une fiche Spiko déjà transformée n’est pas remplacée.

Les styles et interactions partagés sont dans `assets/maison/fiche-visuelle.css` et `.js`. La publication ne modifie ni l’accueil, ni l’annuaire, ni ses données. Les scripts et sources de `_build/` restent protégés par la configuration existante de publication.
