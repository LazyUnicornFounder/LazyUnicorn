#!/usr/bin/env python3
"""
Reads all prompt files in prompts/ and extracts the version from the first
line that contains a version string. Updates versions.json with the result.

Run after pushing any prompt update:
    python sync_versions.py
"""

import os
import re
import json

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')
VERSIONS_FILE = os.path.join(os.path.dirname(__file__), 'versions.json')

versions = {}

for filename in sorted(os.listdir(PROMPTS_DIR)):
    if not filename.endswith('.md'):
        continue

    engine = filename.replace('.md', '')  # e.g. lazy-blogger

    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, 'r') as f:
        content = f.read()

    match = re.search(r'v(\d+\.\d+\.\d+)', content)
    if match:
        versions[engine] = match.group(1)
        print(f'{engine}: {match.group(1)}')
    else:
        print(f'SKIP (no version found): {filename}')

with open(VERSIONS_FILE, 'w') as f:
    json.dump(versions, f, indent=2, sort_keys=True)
    f.write('\n')

print(f'\nUpdated versions.json with {len(versions)} entries.')
