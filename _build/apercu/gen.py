# -*- coding: utf-8 -*-
"""Génère les fiches en APERÇU des cabinets appelables de la salve 1.
Une fiche en aperçu = la fiche vérifiée du cabinet, déjà remplie avec ses vraies
données publiques, marquée non publiée, avec le bouton pour la mettre en ligne.
Sortie : f/apercu/<slug>.html
"""
import json, os, re, html, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
OUTDIR = 'f/apercu'
os.makedirs(OUTDIR, exist_ok=True)

S = json.load(open('_build/enrich/salve1.json'))
BY = {c['nom'].split(' (')[0]: c for c in S}
LOGOS = json.load(open('_build/logos/meta.json'))

CAL = 'https://cal.com/louisdebouzy/25min'


def slugify(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()


def e(s):
    return html.escape(s or '', quote=True)


EDIT_MARKS = (' — ', ' – ', ' + ')


def quote(s):
    """Nettoie la citation : coupe le commentaire éditorial qui suit la citation,
    puis rééquilibre les guillemets pour éviter un » orphelin."""
    s = ' '.join(s.split())
    for m in EDIT_MARKS:
        i = s.find(m)
        if i > 0 and s.count('«', 0, i) == s.count('»', 0, i):
            s = s[:i]
    if s.count('«') > s.count('»'):
        s += ' »'
    return s.strip(' ,;:')


# ---------------------------------------------------------------- contenu
# pitch : le paragraphe « À propos », rédigé à partir des données publiques
# stats : trois chiffres publics vérifiables
# xps   : les domaines affichés
# prix  : la tranche AUM qui s'applique
D = {
"Tanguy Finances": dict(
 prix=1900, tranche="100 – 500 M€",
 stats=[("400 M€","d'encours conseillés"),("4 000","clients accompagnés"),("1995","associés indépendants depuis")],
 xps=["Apport-cession & 150-0 B ter","Ingénierie patrimoniale","Assurance-vie","Immobilier","Retraite du dirigeant"],
 pitch="Cabinet indépendant rennais dirigé par Vincent et Laurence Tanguy, associés depuis 1995, avec un second bureau à Nantes. Plus de 400 millions d'euros d'encours conseillés pour 4 000 clients, sans rattachement à un réseau de distribution : la décision se prend à Rennes. Le cabinet publie une doctrine technique sur l'apport-cession, le report d'imposition et les obligations qui l'accompagnent.",
 equipe=[("Vincent Tanguy","Co-dirigeant associé","https://fr.linkedin.com/in/vincent-tanguy-aa751a33"),("Laurence Tanguy","Co-dirigeante associée",None)]),

"Attitude Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("30+","collaborateurs"),("5","implantations en Bretagne et à Paris"),("Maison Attitude","Multi Family Office interne")],
 xps=["150-0 B ter & remploi","Holding patrimoniale","Multi Family Office","Transmission","Immobilier"],
 pitch="Cabinet fondé et présidé par Henry Coudé, docteur en droit, à Vannes, avec des bureaux à Saint-Brieuc, Nantes, Rennes et Paris. Plus de trente collaborateurs et une marque interne de Multi Family Office. Le cabinet documente publiquement l'apport de titres à une holding, le report d'imposition et l'obligation de réinvestir 70 % du produit de cession sous 36 mois.",
 equipe=[("Henry Coudé","Président fondateur, DG du Cercle France Patrimoine","https://fr.linkedin.com/in/henry-coude-84848444")]),

"Colbert Patrimoine Finance": dict(
 prix=3900, tranche="500 M€ – 2 Md€",
 stats=[("600 M€","d'encours conseillés"),("1923","groupe nantais fondé en"),("Colbert Fusac","banque d'affaires interne")],
 xps=["Préparation de cession","Family Office dirigeants","Banque d'affaires interne","Assurance","Immobilier"],
 pitch="Branche gestion de patrimoine du Colbert groupe, maison nantaise fondée en 1923, dont l'actionnaire majoritaire est Charles Clérice de Meynard. Près de 600 millions d'euros d'encours conseillés et une ambition affichée du milliard sous trois à cinq ans. Le groupe s'est doté en 2024 de sa propre banque d'affaires, Colbert Fusac, et d'un Family Office dédié aux dirigeants de PME et d'ETI.",
 equipe=[("Charles Clérice de Meynard","Associé fondateur, actionnaire majoritaire","https://fr.linkedin.com/in/charles-clerice-de-meynard-2327b9166")]),

"FINARENA Gestion Privée": dict(
 prix=990, tranche="< 100 M€",
 stats=[("2011","cabinet indépendant depuis"),("2","bureaux : Nantes et Guérande"),("20 ans","auprès des dirigeants")],
 xps=["Transmission d'entreprise","Valorisation","Conseil patrimonial du dirigeant","Retraite","Prévoyance"],
 pitch="Cabinet indépendant fondé par Yvan Boutier à Nantes, avec un second bureau à Guérande, positionné sur la double compétence entreprise et patrimoine après vingt ans passés auprès des dirigeants. Aucun groupement, aucune tutelle : la décision se prend au cabinet. Une page entière du site est consacrée à la transmission d'entreprise et à l'évaluation préalable à la cession.",
 equipe=[("Yvan Boutier","Dirigeant fondateur","https://fr.linkedin.com/in/yvanboutier")]),

"Octopus Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("6","collaborateurs dont 2 CGP diplômés"),("2018","cabinet angevin depuis"),("2","bureaux : Angers et La Baule")],
 xps=["Transmission d'entreprise","Recherche d'acquéreurs","Audit patrimonial du dirigeant","Immobilier","Assurance-vie"],
 pitch="Cabinet angevin fondé par Christophe Roche, entrepreneur depuis 1993, six collaborateurs dont deux conseillers diplômés, et un second bureau en ouverture à La Baule. Le cabinet travaille la transmission d'entreprise de bout en bout, de l'audit de la société et de la situation patrimoniale du dirigeant jusqu'à la négociation, en s'appuyant sur une collaboration avec un cabinet de cession.",
 equipe=[("Christophe Roche","Fondateur dirigeant","https://fr.linkedin.com/in/christophe-r-52454929")]),

"Fidere Conseil": dict(
 prix=990, tranche="< 100 M€",
 stats=[("75 M€","d'encours sous gestion"),("1 000","clients accompagnés"),("2003","cabinet angevin depuis")],
 xps=["Chefs d'entreprise","Professions libérales","Assurance-vie","Immobilier","Retraite"],
 pitch="Cabinet angevin né en 2003, rebaptisé Fidere en 2018, dirigé par Samuel Sautjeau. Plus de 75 millions d'euros d'encours sous gestion pour environ mille clients, avec une équipe de cinq personnes et une clientèle dominée par les chefs d'entreprise et les professions libérales.",
 equipe=[("Samuel Sautjeau","Associé dirigeant","https://www.linkedin.com/in/samuel-sautjeau-40293a59")]),

"Hexa Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("700","familles accompagnées"),("6","implantations en France"),("12","salariés au siège")],
 xps=["Cession d'entreprise","150-0 B ter & remploi","Accompagnement post-cession","Valorisation","Immobilier"],
 pitch="Cabinet lyonnais fondé par Sébastien Martinez, ex-Excellis Ingénierie et Patrimoine, tête d'un réseau de six implantations d'Oullins au Pays de Gex. Sept cents familles accompagnées et douze salariés au siège. C'est le cabinet de la salve qui écrit le plus explicitement sur le mécanisme du 150-0 B ter et sur l'obligation de remploi, avec plusieurs articles techniques signés.",
 equipe=[("Sébastien Martinez","Fondateur associé","https://fr.linkedin.com/in/s%C3%A9bastien-martinez-05944831")]),

"Verum Gestion Privée": dict(
 prix=990, tranche="< 100 M€",
 stats=[("2007","maison lyonnaise depuis"),("2","bureaux : Lyon et Paris 8e"),("Repreneur","de cabinets, pas cible")],
 xps=["Gestion privée","Ingénierie patrimoniale","Immobilier","Assurance-vie","Croissance externe"],
 pitch="Maison lyonnaise fondée par Dominique Dimier, avec un second bureau à Paris 8e. Verum est un consolidateur, pas une cible : le cabinet a racheté Hera Consultants et affiche une stratégie d'intraprenariat face au mouvement de concentration du métier. Indépendance capitalistique totale.",
 equipe=[("Dominique Dimier","Président fondateur","https://fr.linkedin.com/in/dominique-dimier-2a31aa16")]),

"Treeefle Gestion Privée": dict(
 prix=990, tranche="< 100 M€",
 stats=[("1997","indépendant depuis"),("3","bureaux : Lille, Rouen, Paris"),("1 à 15 M€","segment de valorisation ciblé")],
 xps=["Cession à un tiers","Transmission intra-familiale","Conseil aux entrepreneurs","Assurance-vie","Immobilier"],
 pitch="Cabinet lillois indépendant depuis 1997, ex-Patrimum Nord de France, cofondé par Antoine Cauchy, avec des bureaux à Rouen et Paris. Le cabinet s'adresse frontalement aux entrepreneurs dont la société est valorisée entre 1 et 15 millions d'euros, avec une offre construite autour de la cession à un tiers et de la transmission intra-familiale.",
 equipe=[("Antoine Cauchy","Cofondateur dirigeant","https://fr.linkedin.com/in/antoine-cauchy-%F0%9F%8D%80-627960b1"),("Bastien Lequien","Associé",None)]),

"Boreal Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("2020","cabinet lillois depuis"),("3","associés"),("Personnes morales","un associé dédié")],
 xps=["Conseil aux personnes morales","Trésorerie d'entreprise","Assurance-vie","Immobilier","Retraite"],
 pitch="Cabinet de Marcq-en-Barœul créé en 2020 par trois associés, dont Marc-Antoine Gromez. Particularité utile côté dirigeant : un associé est spécifiquement dédié au conseil aux personnes morales et aux entreprises.",
 equipe=[("Marc-Antoine Gromez","Associé gérant cofondateur","https://fr.linkedin.com/in/marc-antoine-gromez-a3236bb5"),("Alexis Masurel","Associé, conseil aux personnes morales",None)]),

"OP Finances": dict(
 prix=990, tranche="< 100 M€",
 stats=[("850","clients accompagnés"),("30 ans","d'expérience du fondateur"),("6","collaborateurs")],
 xps=["Placements financiers","Prévoyance TNS","Retraite","Assurance-vie","Immobilier"],
 pitch="Cabinet indépendant d'Hazebrouck connu sous l'enseigne Optimisation Patrimoine, fondé par Olivier Pruvost, trente ans de métier. Une équipe de six personnes pour 850 clients, sur un positionnement placements financiers et prévoyance du travailleur non salarié.",
 equipe=[("Olivier Pruvost","Gérant fondateur","https://fr.linkedin.com/in/olivierpruvostsp%C3%A9cialisteenplacementsfinanciers"),("Hélène Marin","Directrice de cabinet",None)]),

"Office Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("2005","cabinet amiénois fondé en"),("2020","repris par les associés actuels"),("CNCGP","membre")],
 xps=["Conseil patrimonial","Assurance-vie","Immobilier","Personnes vulnérables","Retraite"],
 pitch="Cabinet amiénois né de la reprise en 2020 de Génération & Patrimoine, cabinet fondé en 2005. Deux associés gérants, un conseiller junior et une assistante. Les associés signent seuls : leurs plateformes sont des fournisseurs, pas des actionnaires.",
 equipe=[("Bertrand Bracq","Associé gérant","https://fr.linkedin.com/in/bertrand-bracq-63782ab0"),("Jean-Benoît Rigaux","Associé gérant",None)]),

"Version Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("Aucun réseau","de distribution"),("2","bureaux : Bordeaux et Tulle"),("CNCGP","vice-présidence")],
 xps=["Conseil patrimonial indépendant","Assurance-vie","Immobilier","Retraite","Transmission"],
 pitch="Cabinet bordelais dirigé collégialement par trois co-gérants, avec un second bureau à Tulle. Le cabinet revendique de n'être rattaché à aucun réseau de distribution. Yves Marie Mazin, co-gérant, est vice-président de la CNCGP.",
 equipe=[("Yves Marie Mazin","Co-gérant associé, vice-président de la CNCGP","https://fr.linkedin.com/in/yves-mazin-09091621"),("Pierre Bordas","Co-gérant associé",None)]),

"Bonjour Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("15","conseillers en gestion de patrimoine"),("3","ingénieurs patrimoniaux"),("5","implantations en France")],
 xps=["Apport-cession","Trésorerie d'entreprise","Assurance-vie","Private equity","Immobilier"],
 pitch="Cabinet toulousain dirigé par François Lebeau et Philippe Moussaud, avec des bureaux à Paris, Bordeaux, Soorts-Hossegor et Nantes. Quinze conseillers et trois ingénieurs patrimoniaux. Le groupe édite également un média de référence sur la gestion de patrimoine, dont une page complète traite de l'apport-cession de titres et des conditions de réinvestissement.",
 equipe=[("François Lebeau","Managing Partner","https://fr.linkedin.com/in/gestionnairedepatrimoine"),("Philippe Moussaud","Managing Partner",None)]),

"Office Experts Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("7","implantations en Occitanie"),("CNCGP","présidence Languedoc-Roussillon"),("2026","Trophée CF News Sud-Ouest")],
 xps=["Accompagnement du dirigeant","Transmission","Expertise comptable associée","Assurance-vie","Immobilier"],
 pitch="Cabinet millavois fondé et présidé par Cyrille Brengues, président de la CNCGP Languedoc-Roussillon et intervenant au Master de gestion de patrimoine de Montpellier. Sept implantations, Trophée CF News Sud-Ouest en janvier 2026 et meilleur cabinet d'Occitanie au Grand Forum 2025. Le cabinet accompagne le dirigeant depuis la création de son entreprise jusqu'à sa transmission.",
 equipe=[("Cyrille Brengues","Président fondateur","https://fr.linkedin.com/in/cyrille-brengues-01843755"),("Jérémy Combettes","DG associé, directeur de la gestion privée",None)]),

"ELITE Patrimoine": dict(
 prix=990, tranche="< 100 M€",
 stats=[("4","bureaux dont Tampa"),("2009","cabinet toulousain depuis"),("Sportifs & talents","spécialité")],
 xps=["Sportifs professionnels","Talents de l'entertainment","International","Assurance-vie","Immobilier"],
 pitch="Cabinet toulousain fondé par Frédéric Schatzlé, spécialisé dans le patrimoine des sportifs professionnels et des talents de l'entertainment, avec quatre bureaux dont un à Tampa. Une expertise rare : gérer un capital qui arrive d'un coup, sur une carrière courte, avec une fiscalité et une exposition publique particulières.",
 equipe=[("Frédéric Schatzlé","Fondateur associé gérant",None),("Kevin Beesley","Associé gérant","https://fr.linkedin.com/in/kevin-beesley-3459b21b0")]),

"Massalia Finance": dict(
 prix=1900, tranche="100 – 500 M€",
 stats=[("150 M€","conseillés"),("850","familles accompagnées"),("2000","cabinet marseillais depuis")],
 xps=["Cession d'entreprise","Pacte Dutreil","Donation avant cession","Family buy out","Assurance-vie"],
 pitch="Cabinet marseillais indépendant fondé en 2000 par Lionel Lafon, membre de la CNCGP, 150 millions d'euros conseillés pour 850 familles. Le cabinet publie une page dédiée à l'optimisation de la cession d'entreprise : pacte Dutreil, donation avant cession, family buy out.",
 equipe=[("Lionel Lafon","Gérant fondateur","https://fr.linkedin.com/in/lionel-lafon-gestion-de-patrimoine"),("Gérard Degrutere","Directeur CGP",None)]),

"Novalfi Conseil": dict(
 prix=1900, tranche="100 – 500 M€",
 stats=[("11","implantations"),("30","collaborateurs"),("6","juristes-fiscalistes en interne")],
 xps=["Ingénierie juridique et fiscale","Gestion sous mandat","Société de gestion agréée AMF","Assurance-vie","Immobilier"],
 pitch="Maison aixoise adossée à Financière de l'Arc, société de gestion agréée par l'AMF, présidée par Grégory Teyssier. Onze implantations d'Aix à Paris en passant par Toulon, Mougins, Montpellier, Manosque et Tassin, trente collaborateurs et un pôle juridique interne de six juristes-fiscalistes.",
 equipe=[("Grégory Teyssier","Président, DG de Financière de l'Arc","https://fr.linkedin.com/in/gr%C3%A9gory-teyssier-9534925"),("Christophe Veran","Associé, pôle gestion de patrimoine",None)]),

"Master Conseil": dict(
 prix=990, tranche="< 100 M€",
 stats=[("2011","cabinet aixois depuis"),("2","associés gérants"),("ANACOFI","membre")],
 xps=["Ingénierie fiscale","Produits structurés","PER & retraite","Immobilier","Assurance-vie"],
 pitch="Cabinet indépendant d'Aix-en-Provence dirigé par deux associés gérants, Olivier Janin et Stéphane Voss, membre de l'ANACOFI. Positionnement technique sur l'ingénierie fiscale et les solutions de placement, avec une clientèle de dirigeants et de professions libérales du bassin aixois.",
 equipe=[("Olivier Janin","Associé gérant","https://fr.linkedin.com/in/olivier-janin-a7a15b182"),("Stéphane Voss","Associé gérant",None)]),

"Family and Office": dict(
 prix=990, tranche="< 100 M€",
 stats=[("2021","né de la fusion de deux cabinets"),("Aix","Provence"),("2026","« les 100 qui font le patrimoine »")],
 xps=["Après-cession","Reprise d'entreprise","Club deals","Levée de fonds","Prise de participation"],
 pitch="Cabinet aixois né en 2021 de la fusion de deux structures, codirigé par Lambert Debus, distingué parmi « les 100 qui font le patrimoine » au Grand Forum du Patrimoine 2026. Profil hybride entre gestion privée et investissement direct : club deals immobiliers et financiers, levée de fonds, prise de participation. Le cabinet revendique le processus complet, du motif de transmission jusqu'à la gestion de l'après-cession.",
 equipe=[("Lambert Debus","Codirigeant","https://www.linkedin.com/in/lambert-d-54429216/")]),

"Fipad Conseil": dict(
 prix=990, tranche="< 100 M€",
 stats=[("1 500","familles depuis 1993"),("4","bureaux : Besançon, Dijon, Reims, Beaune"),("1993","groupe régional depuis")],
 xps=["Patrimoine des dirigeants","Interprofessionnel","Transmission","Assurance-vie","Immobilier"],
 pitch="Groupe régional bisontin fondé en 1993 par Jean-Claude Jehanno, avec des bureaux à Dijon, Reims et Beaune. Mille cinq cents familles accompagnées et un positionnement affiché d'expertise patrimoniale interprofessionnelle sur le patrimoine des familles et des dirigeants d'entreprise. Décideur unique : il signe seul.",
 equipe=[("Jean-Claude Jehanno","Gérant fondateur","https://fr.linkedin.com/in/jcjehanno")]),
}

# accroches : la raison personnelle, signée, pour laquelle la fiche a été préparée
ACC = {
 "Hexa Patrimoine":"Vous êtes le seul cabinet de votre région à écrire noir sur blanc sur le 150-0 B ter et l'obligation de remploi. Nos membres, ce sont exactement les gens qui ont ces 36 mois devant eux.",
 "Treeefle Gestion Privée":"Votre page d'accueil dit « vous avez construit, vendu ou repris une entreprise ». C'est mot pour mot notre base de membres, sur votre segment 1 à 15 M€.",
 "Colbert Patrimoine Finance":"Vous avez monté Colbert Fusac en 2024 et vous visez le milliard. Le carburant, c'est du deal flow de cédants. C'est précisément ce que l'Exit Club rassemble.",
 "Attitude Patrimoine":"Vous citez le report d'imposition et les 70 % à 36 mois sur votre page dirigeant. Nos membres sont dans ce compte à rebours, en ce moment.",
 "Tanguy Finances":"Votre article apport-cession de mars 2025. 400 M€, 4 000 clients, et vous êtes indépendants : la décision se prend chez vous, à Rennes.",
 "Version Patrimoine":"Vous êtes vice-président de la CNCGP et vous n'êtes rattaché à aucun réseau. Je voulais votre lecture avant d'ouvrir la Nouvelle-Aquitaine.",
 "Office Experts Patrimoine":"Président CNCGP Languedoc-Roussillon, Trophée CF News Sud-Ouest en janvier. Je veux l'Occitanie représentée par vous, pas par un réseau national.",
 "FINARENA Gestion Privée":"Vous avez une page « Transmettre son entreprise » et vous signez seul. Deux raisons pour lesquelles cette fiche peut être en ligne aujourd'hui.",
 "Bonjour Patrimoine":"Vous éditez un média sur la gestion de patrimoine, donc je n'ai pas à vous expliquer ce que vaut une audience qualifiée. La nôtre a déjà vendu.",
 "Octopus Patrimoine":"Vous travaillez avec un cabinet de cession pour trouver des cédants. Nous, on a déjà les cédants, après la vente, avec le cash sur le compte.",
 "Verum Gestion Privée":"Vous rachetez des cabinets, vous ne vous faites pas racheter. Les gens qui vendent leur entreprise, c'est votre matière première.",
 "Massalia Finance":"150 M€ pour 850 familles à Marseille, et une page entière sur la cession d'entreprise. Combien de dirigeants cédants sont passés à côté de vous cette année ?",
 "Fipad Conseil":"Groupe régional depuis 1993, 1 500 familles, patrimoine des dirigeants. Vous n'avez rien de public sur la cession : c'est justement le sujet de cette fiche.",
 "OP Finances":"30 ans, 850 clients, indépendant. Sur les Hauts-de-France, la question c'est qui capte les dirigeants qui viennent de vendre.",
 "Boreal Patrimoine":"Vous avez un associé dédié aux personnes morales. Cette fiche est faite pour lui : les dirigeants qui ont déjà signé leur cession.",
 "ELITE Patrimoine":"Vous gérez le patrimoine de sportifs et de talents. Le parallèle est direct : un exit, c'est la même mécanique d'argent qui tombe d'un coup.",
 "Family and Office":"Vous écrivez « de l'analyse des motifs de transmission à la gestion de l'après-cession ». L'après-cession, c'est exactement là que vivent nos membres.",
 "Master Conseil":"Vous êtes indépendants à Aix depuis longtemps. Ma question tient en une ligne : que faites-vous aujourd'hui du dirigeant qui vient d'encaisser 8 M€ ?",
 "Novalfi Conseil":"11 implantations, 6 juristes-fiscalistes en interne, une société de gestion agréée AMF. Vous avez la machine. Il vous manque le flux.",
 "Office Patrimoine":"Vous avez repris Génération & Patrimoine et vous signez seuls. Sur la Somme, personne ne s'occupe des dirigeants qui viennent de vendre.",
 "Fidere Conseil":"75 M€, 1 000 clients, une clientèle de chefs d'entreprise, et rien de public sur la cession. C'est un angle mort qui se comble en une fiche.",
}

REG = {
 "Tanguy Finances":"Bretagne","Attitude Patrimoine":"Bretagne","Colbert Patrimoine Finance":"Pays de la Loire",
 "FINARENA Gestion Privée":"Pays de la Loire","Octopus Patrimoine":"Pays de la Loire","Fidere Conseil":"Pays de la Loire",
 "Hexa Patrimoine":"Auvergne-Rhône-Alpes","Verum Gestion Privée":"Auvergne-Rhône-Alpes",
 "Treeefle Gestion Privée":"Hauts-de-France","Boreal Patrimoine":"Hauts-de-France","OP Finances":"Hauts-de-France",
 "Office Patrimoine":"Hauts-de-France","Version Patrimoine":"Nouvelle-Aquitaine","Bonjour Patrimoine":"Occitanie",
 "Office Experts Patrimoine":"Occitanie","ELITE Patrimoine":"Occitanie","Massalia Finance":"Provence-Alpes-Côte d'Azur",
 "Novalfi Conseil":"Provence-Alpes-Côte d'Azur","Master Conseil":"Provence-Alpes-Côte d'Azur",
 "Family and Office":"Provence-Alpes-Côte d'Azur","Fipad Conseil":"Bourgogne-Franche-Comté",
}

# forme prépositionnelle : « En Bretagne » mais « Dans les Pays de la Loire »
REGP = {
 "Bretagne":"En Bretagne", "Pays de la Loire":"Dans les Pays de la Loire",
 "Auvergne-Rhône-Alpes":"En Auvergne-Rhône-Alpes", "Hauts-de-France":"Dans les Hauts-de-France",
 "Nouvelle-Aquitaine":"En Nouvelle-Aquitaine", "Occitanie":"En Occitanie",
 "Provence-Alpes-Côte d'Azur":"En Provence-Alpes-Côte d'Azur",
 "Bourgogne-Franche-Comté":"En Bourgogne-Franche-Comté",
}

MODULES = [
 ("Votre logo et vos associés en tête de fiche", "Photos, fonctions, LinkedIn. Le lecteur voit des visages, pas une raison sociale."),
 ("Votre présentation et vos expertises post-cession", "Le texte que vous validez, pas celui qu'un algorithme a deviné."),
 ("Actualités &amp; opérations", "Deals, levées, nominations, prix. Chaque publication vous fait remonter dans le fil de l'Écosystème."),
 ("Opportunité du moment", "Un encart daté, que vous changez quand vous voulez : un fonds qui ouvre, un club deal, une place au comité."),
 ("Le one-pager de votre dernier fonds ou de votre offre", "Téléchargeable directement depuis la fiche."),
 ("La prise de rendez-vous directe", "Votre agenda intégré. Le membre réserve sans passer par personne."),
]

TR = ["< 100 M€", "100 – 500 M€", "500 M€ – 2 Md€", "> 2 Md€"]
TRP = {"< 100 M€":"990 €", "100 – 500 M€":"1 900 €", "500 M€ – 2 Md€":"3 900 €", "> 2 Md€":"6 900 €"}

PHOTOS = json.load(open('_build/apercu/photos.json')) if os.path.exists('_build/apercu/photos.json') else {}

CSS = open('_build/apercu/style.css').read()
TPL = open('_build/apercu/tpl.html').read()


def initials(n):
    parts = [p for p in re.split(r'[\s\-]+', n) if p and p[0].isalpha()]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()


def build(nom):
    c = BY[nom]
    d = D[nom]
    slug = slugify(nom)
    lg = LOGOS.get(slug)

    if lg:
        logo = '<div class="logo logo-img%s"><img src="%s" alt="%s"></div>' % (
            ' logo-dark' if lg['dark'] else '', lg['src'], e(nom))
    else:
        logo = '<div class="logo">%s</div>' % initials(nom)

    stats = ''.join('<div class="stat"><b>%s</b><span>%s</span></div>' % (e(a), e(b)) for a, b in d['stats'])
    xps = ''.join('<span class="xp">%s</span>' % e(x) for x in d['xps'])

    eq = ''
    for n, r, li in d['equipe']:
        lia = '<a href="%s" target="_blank" rel="noopener">LinkedIn</a>' % e(li) if li else ''
        ph = PHOTOS.get('%s|%s' % (slug, n))
        if ph:
            ava = '<div class="ava ph"><img src="%s" alt="%s" loading="lazy"></div>' % (e(ph['f']), e(n))
            chip = ''
        else:
            ava = '<div class="ava">%s</div>' % initials(n)
            chip = '<span class="slot">photo a ajouter</span>'.replace('a ajouter', '\u00e0 ajouter')
        eq += ('<div class="pers">%s<div><b>%s</b><span>%s</span>%s</div>%s</div>') % (
            ava, e(n), e(r), lia, chip)

    preuve = ''
    if c.get('angle_exit'):
        src = c.get('angle_source') or c.get('site')
        preuve = ('<div class="proof"><div class="k">Ce que vous dites déjà, publiquement</div>'
                  '<p class="q">%s</p><a class="psrc" href="%s" target="_blank" rel="noopener">Relevé sur votre site &rarr;</a></div>') % (
            e(quote(c['angle_exit'])), e(src))
    else:
        preuve = ('<div class="proof proof-none"><div class="k">Ce qui manque, et qui se règle en une fiche</div>'
                  '<p class="q">Rien, sur votre site, ne dit au dirigeant qui vient de vendre que vous savez le prendre en charge. '
                  'Vos confrères de la région, eux, l\'écrivent. Cette fiche est l\'endroit le plus rapide pour le dire.</p></div>')

    mods = ''.join('<div class="mod"><div class="mh"><span class="mt">%s</span><span class="chip">à remplir</span></div>'
                   '<p>%s</p></div>' % (t, p) for t, p in MODULES)

    grid = ''
    for t in TR:
        cur = ' cur' if t == d['tranche'] else ''
        grid += '<div class="pr%s"><b>%s</b><span>%s</span></div>' % (cur, TRP[t], t)

    equipe_noms = ' et '.join(x[0] for x in d['equipe'][:2])

    return TPL.format(
        css=CSS, nom=e(nom), slug=slug, logo=logo, stats=stats, xps=xps, pitch=e(d['pitch']),
        equipe=eq, preuve=preuve, mods=mods, grid=grid, acc=e(ACC[nom]), region=e(REG[nom]),
        regionp=e(REGP[REG[nom]]),
        site=e(c.get('site') or ''), cal=CAL, prix=TRP[d['tranche']], tranche=e(d['tranche']),
        decideur=e(c['decideur'].split()[0]), equipe_noms=e(equipe_noms),
        sitebtn=('<a class="btn2" href="%s" target="_blank" rel="noopener">Site officiel</a>' % e(c['site'])) if c.get('site') else '',
    )


if __name__ == '__main__':
    idx = {}
    for nom in D:
        h = build(nom)
        slug = slugify(nom)
        open(os.path.join(OUTDIR, slug + '.html'), 'w').write(h)
        idx[nom] = {'slug': slug, 'url': 'https://www.exit.club/f/apercu/' + slug,
                    'email': BY[nom].get('email_publie'), 'tel': BY[nom].get('tel'),
                    'decideur': BY[nom]['decideur'], 'prix': D[nom]['prix'], 'region': REG[nom]}
    json.dump(idx, open('_build/apercu/index.json', 'w'), ensure_ascii=False, indent=1)
    print(len(idx), 'fiches en aperçu générées')
