#!/usr/bin/env python3
"""Preview, then optionally update only the two shared profile asset URLs.

Run without --apply first. No profile generation and no content parsing/writing.
"""
from pathlib import Path
import argparse
import json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
root = args.root.resolve()
changes = (
    (b'/assets/maison/fiche-visuelle.css?v=20261019', b'/assets/maison/fiche-visuelle.css?v=20261020-comparison'),
    (b'/assets/maison/fiche-visuelle.js?v=20261019', b'/assets/maison/fiche-visuelle.js?v=20261020-comparison'),
)
slugs = {h['slug'] for h in json.loads((root/'assets/ecosysteme/maison/data.json').read_text())['houses']}
planned = []
already = []
for file in sorted((root/'f').glob('*.html')):
    before = file.read_bytes()
    old_counts = [before.count(old) for old, new in changes]
    new_counts = [before.count(new) for old, new in changes]
    if not any(old_counts):
        if new_counts == [1, 1]:
            already.append(file.stem)
        continue
    if old_counts != [1, 1] or any(new_counts):
        raise SystemExit(f'Unexpected mixed or duplicated asset references: {file}')
    after = before
    for old, new in changes:
        after = after.replace(old, new)
    check = after
    for old, new in changes:
        check = check.replace(new, old)
    if check != before:
        raise SystemExit(f'Unexpected content delta: {file}')
    planned.append((file, before, after))
if args.apply:
    for file, before, after in planned:
        if file.read_bytes() != before:
            raise SystemExit(f'File changed since scan: {file}')
        file.write_bytes(after)
        if file.read_bytes() != after:
            raise SystemExit(f'Write verification failed: {file}')
print(json.dumps({
    'mode': 'applied' if args.apply else 'dry-run',
    'profiles': len(planned),
    'catalog_profiles': sum(p.stem in slugs for p, _, _ in planned),
    'profiles_outside_catalog': [p.stem for p, _, _ in planned if p.stem not in slugs],
    'references': 2 * len(planned),
    'already_current': len(already),
    'other_changes': 0,
}, ensure_ascii=False, indent=2))
