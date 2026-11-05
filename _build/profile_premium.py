"""Badge commercial, indépendant de la vérification et des classements.

Liste explicite maintenue depuis les accords commerciaux et décisions de Louis.
Ne jamais déduire ce statut de la présence d'une fiche ou d'un label tiers.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / '_build/premium-profils.json').read_text())
CSS = '/assets/maison/premium.css?v=20261105-prisme'
JS = '/assets/maison/premium.js?v=20261105-prisme'


def apply_premium(soup, slug):
    if slug not in CONFIG['slugs']:
        return False
    identity = soup.select_one('.pv-identity')
    if not identity:
        raise ValueError(f'En-tête de fiche absent : {slug}')
    if identity.select_one('.ec-premium-status'):
        return False
    status = identity.select_one('.pv-status')
    wrapper = soup.new_tag('div', attrs={'class': 'ec-premium-status'})
    button = soup.new_tag('button', attrs={
        'class': 'ec-premium-badge', 'type': 'button',
        'aria-describedby': f'premium-info-{slug}', 'aria-expanded': 'false',
    })
    button.string = CONFIG['label']
    icon = soup.new_tag('span', attrs={'class': 'ec-premium-info', 'aria-hidden': 'true'})
    icon.string = 'i'
    button.append(icon)
    tooltip = soup.new_tag('span', attrs={
        'class': 'ec-premium-tooltip', 'role': 'tooltip', 'id': f'premium-info-{slug}',
    })
    tooltip.string = CONFIG['explanation']
    wrapper.append(button)
    wrapper.append(tooltip)
    if status:
        status.replace_with(wrapper)
    else:
        identity.append(wrapper)
    # Ancien badge commercial à coche : le statut unique est désormais en tête.
    for badge in soup.select('.vbadge'):
        badge.decompose()
    for text in list(soup.find_all(string=True)):
        if text.parent.name in ('script', 'style'):
            continue
        value = str(text)
        updated = value.replace(
            'Profil vérifié : contenu fourni et validé par la firme.',
            'Profil Premium : présentation enrichie dans le cadre d’un abonnement payant.'
        ).replace(
            "La vérification est un engagement commercial qui n'influence ni la présence dans l'annuaire, ni l'ordre d'affichage, ni les Ligues.",
            "Cet abonnement n’influence ni la présence dans l’annuaire, ni l’ordre d’affichage, ni les classements."
        )
        if updated != value:
            text.replace_with(updated)
    soup.head.append(soup.new_tag('link', rel='stylesheet', href=CSS))
    script = soup.new_tag('script', src=JS)
    script['defer'] = ''
    soup.head.append(script)
    return True


if __name__ == '__main__':
    from bs4 import BeautifulSoup
    for slug in CONFIG['slugs']:
        path = ROOT / 'f' / f'{slug}.html'
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        if apply_premium(soup, slug):
            path.write_text(str(soup))
            print(slug)
