# Webhook: prevenir Louis a chaque nouvelle adhesion
#
# Constate le 30 aout : Clement Escande a paye son adhesion le 1er juillet,
# sa fiche est bien passee en Actif et il a recu son lien d'acces, mais Louis
# n'a jamais ete prevenu. Resultat, deux mois sans onboarding pour un membre
# qui a paye 719,86 EUR.
#
# La cause est structurelle : activerAdhesion active la fiche et envoie le lien
# de bienvenue au membre, puis s'arrete. Tous les autres parcours notifient
# Louis (fiche verifiee, Sparring, sponsoring, echec de paiement) ; l'adhesion,
# le produit le plus important, est le seul qui ne le fait pas.
#
# - email a Louis a chaque adhesion : nom, email, montant, lien vers la fiche
# - le mail indique si la fiche existait deja (candidature Tally, vetting fait)
#   ou si elle a ete creee en secours, ce qui signale une adhesion arrivee
#   directement par le lien de paiement, sans passer par la candidature.
#
# L'envoi est non bloquant : un echec d'email ne doit jamais empecher une
# adhesion payee de s'activer.

import sys

echecs = []


def patch(chemin, remplacements):
    try:
        s = open(chemin, encoding="utf-8").read()
    except FileNotFoundError:
        echecs.append("ECHEC: fichier absent %s" % chemin)
        return
    avant = s
    for a, b, n in remplacements:
        c = s.count(a)
        if c != n:
            echecs.append(
                "ECHEC [%s]: « %s » attendu %d fois, trouve %d"
                % (chemin, a[:60].replace("\n", "\\n"), n, c)
            )
            continue
        s = s.replace(a, b)
        print("  ok  %dx  %s" % (c, a[:64].replace("\n", "\\n")))
    if s != avant and not echecs:
        open(chemin, "w", encoding="utf-8").write(s)


patch(
    "src/app/api/stripe/webhook/route.ts",
    [
        # 1. retenir si la fiche existait deja (vetting) ou non
        (
            "  // Active la fiche existante (créée par Tally) ou la crée en secours.\n"
            "  let notionPageId: string | null = null;\n"
            "  try {\n"
            "    const membre = await setMembreStatutByEmail(email, \"Actif\", true);\n"
            "    notionPageId = membre?.id ?? null;\n"
            "    if (!membre) {\n"
            "      notionPageId = await createMembreComplet({",
            "  // Active la fiche existante (créée par Tally) ou la crée en secours.\n"
            "  let notionPageId: string | null = null;\n"
            "  // Une fiche absente signale une adhésion arrivée directement par le lien\n"
            "  // de paiement, sans candidature Tally : Louis doit le savoir, c'est le cas\n"
            "  // où l'onboarding manuel compte le plus.\n"
            "  let ficheExistante = true;\n"
            "  try {\n"
            "    const membre = await setMembreStatutByEmail(email, \"Actif\", true);\n"
            "    notionPageId = membre?.id ?? null;\n"
            "    if (!membre) {\n"
            "      ficheExistante = false;\n"
            "      notionPageId = await createMembreComplet({",
            1,
        ),
        # 2. notification a Louis, apres le lien magique
        (
            "  } catch (e) {\n"
            "    console.error(\"[Stripe webhook] envoi lien magique adhésion :\", e);\n"
            "  }\n"
            "}",
            "  } catch (e) {\n"
            "    console.error(\"[Stripe webhook] envoi lien magique adhésion :\", e);\n"
            "  }\n"
            "\n"
            "  // Alerte à Louis. Sans elle, un membre paie, reçoit son accès, et\n"
            "  // personne ne l'accueille : c'est exactement ce qui s'est produit\n"
            "  // pendant deux mois avant l'ajout de ce bloc.\n"
            "  try {\n"
            "    const montant =\n"
            "      typeof session.amount_total === \"number\"\n"
            "        ? (session.amount_total / 100).toLocaleString(\"fr-FR\", {\n"
            "            style: \"currency\",\n"
            "            currency: (session.currency ?? \"eur\").toUpperCase(),\n"
            "          })\n"
            "        : \"montant inconnu\";\n"
            "    const ficheUrl = notionPageId\n"
            "      ? `https://www.notion.so/${notionPageId.replace(/-/g, \"\")}`\n"
            "      : \"\";\n"
            "    await sendEmail({\n"
            "      to: NOTIFY,\n"
            "      subject: `[Exit Club] Nouvelle adhésion — ${fullName}`,\n"
            "      html: `\n"
            "        <div style=\"font-family:Helvetica,Arial,sans-serif;color:#1a1a1a;max-width:560px;margin:0 auto;\">\n"
            "          <p style=\"font-size:13px;letter-spacing:2px;color:#8a7d6a;\">EXIT&nbsp;CLUB&nbsp;·&nbsp;ADHÉSION</p>\n"
            "          <h1 style=\"font-size:20px;font-weight:600;margin:8px 0 4px;\">${fullName} vient d'adhérer</h1>\n"
            "          <div style=\"border:1px solid #e6e1d8;border-radius:10px;padding:16px;margin:14px 0;\">\n"
            "            <p style=\"font-size:14px;color:#6b6257;margin:2px 0;\">Email : <a href=\"mailto:${email}\">${email}</a></p>\n"
            "            <p style=\"font-size:14px;color:#6b6257;margin:2px 0;\">Montant : <b>${montant}</b></p>\n"
            "            <p style=\"font-size:14px;color:#6b6257;margin:2px 0;\">Candidature Tally : <b>${ficheExistante ? \"oui, fiche déjà vettée\" : \"NON — arrivé par le lien de paiement, à qualifier\"}</b></p>\n"
            "            ${ficheUrl ? `<p style=\"font-size:14px;color:#6b6257;margin:8px 0 2px;\">Fiche : <a href=\"${ficheUrl}\">${ficheUrl}</a></p>` : \"\"}\n"
            "          </div>\n"
            "          <p style=\"font-size:14px;line-height:1.6;\">Il a reçu son lien d'accès automatiquement. Il reste à l'accueillir : mot de bienvenue, ajout aux groupes, prochain dîner.</p>\n"
            "        </div>`,\n"
            "    });\n"
            "  } catch (e) {\n"
            "    console.error(\"[Stripe webhook] alerte adhésion à Louis :\", e);\n"
            "  }\n"
            "}",
            1,
        ),
    ],
)

# ------------------------------------------------------------ controles
if not echecs:
    s = open("src/app/api/stripe/webhook/route.ts", encoding="utf-8").read()
    if "Nouvelle adhésion" not in s:
        echecs.append("ECHEC: l'alerte d'adhésion n'a pas été posée")
    if "ficheExistante" not in s:
        echecs.append("ECHEC: le drapeau ficheExistante est absent")
    if s.count("let ficheExistante = true;") != 1:
        echecs.append("ECHEC: ficheExistante déclaré un nombre de fois inattendu")

if echecs:
    print()
    for e in echecs:
        print(e)
    sys.exit(1)

print("\nTermine : chaque adhesion previent Louis.")
