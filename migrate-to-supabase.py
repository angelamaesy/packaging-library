#!/usr/bin/env python3
"""
migrate-to-supabase.py
----------------------
One-time migration. Uploads all images in TAGBOT/ to Supabase Storage,
then upserts all library.json records into the Supabase library table.
Also rewrites library.json and library-data.js to use Supabase public URLs.

Requirements:
    pip install requests python-dotenv

Run from the packaging-library folder:
    python3 migrate-to-supabase.py
"""

import json
import mimetypes
import os
from urllib.parse import quote, unquote
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL      = os.environ['SUPABASE_URL']
SERVICE_ROLE_KEY  = os.environ['SUPABASE_SERVICE_ROLE_KEY']
STORAGE_BUCKET    = 'tagbot-images'
LIBRARY_FILE      = 'library.json'
DATAJS_FILE       = 'library-data.js'
TAGBOT_DIR        = 'TAGBOT'

HEADERS = {
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'apikey':        SERVICE_ROLE_KEY,
}

def public_url(storage_path):
    return f'{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{quote(storage_path)}'

def upload_image(local_path, storage_path):
    """Upload a file to Supabase Storage. Returns True on success."""
    mime, _ = mimetypes.guess_type(local_path)
    mime = mime or 'image/jpeg'
    url = f'{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{quote(storage_path)}'
    with open(local_path, 'rb') as f:
        r = requests.post(
            url,
            headers={**HEADERS, 'Content-Type': mime, 'x-upsert': 'true'},
            data=f,
        )
    if r.status_code in (200, 201):
        return True
    print(f'  ✗ Upload failed ({r.status_code}): {r.text[:120]}')
    return False

def upsert_records(records):
    """Upsert a batch of records into the library table."""
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/library',
        headers={**HEADERS, 'Content-Type': 'application/json',
                 'Prefer': 'resolution=merge-duplicates'},
        json=records,
    )
    return r.status_code in (200, 201)

def normalize_array(val):
    if isinstance(val, list): return val
    if not val: return []
    return [val]

def normalize_format(val):
    """Normalize format to a string — take first element if it's an array."""
    if isinstance(val, list): return val[0] if val else ''
    return val or ''

def old_src_to_storage_path(src):
    """
    "TAGBOT/2026-03-24/Screenshot%202026-03-02%20at%2018.26.42.png"
    → "2026-03-24/Screenshot 2026-03-02 at 18.26.42.png"
    """
    decoded = unquote(src)         # "TAGBOT/2026-03-24/Screenshot 2026-03-02 at 18.26.42.png"
    parts = decoded.split('/', 1)
    if len(parts) == 2 and parts[0] == TAGBOT_DIR:
        return parts[1]
    return decoded

def old_src_to_local_path(src):
    return unquote(src)  # "TAGBOT/2026-03-24/Screenshot 2026-03-02 at 18.26.42.png"

def main():
    with open(LIBRARY_FILE) as f:
        library = json.load(f)

    print(f'Found {len(library)} entries in {LIBRARY_FILE}')

    # ── Step 1: Upload images ─────────────────────────────────────────────────
    print(f'\n── Uploading images to Supabase Storage ({STORAGE_BUCKET}) ─────────')
    src_map = {}  # old src → new public URL

    for i, entry in enumerate(library):
        old_src = entry.get('src', '')

        # Already migrated or a dataURL — skip upload
        if not old_src or old_src.startswith('data:') or old_src.startswith('http'):
            src_map[old_src] = old_src
            continue

        local_path   = old_src_to_local_path(old_src)
        storage_path = old_src_to_storage_path(old_src)

        if not os.path.exists(local_path):
            print(f'  [{i+1}/{len(library)}] ✗ File not found: {local_path}')
            src_map[old_src] = old_src  # keep old src if file is missing
            continue

        print(f'  [{i+1}/{len(library)}] {storage_path} … ', end='', flush=True)
        if upload_image(local_path, storage_path):
            print('✓')
            src_map[old_src] = public_url(storage_path)
        else:
            src_map[old_src] = old_src

    # ── Step 2: Build updated library with new src URLs ───────────────────────
    updated_library = []
    for entry in library:
        new_entry = dict(entry)
        new_entry['src'] = src_map.get(entry.get('src', ''), entry.get('src', ''))
        updated_library.append(new_entry)

    # ── Step 3: Upsert records into Supabase library table ────────────────────
    print(f'\n── Upserting {len(updated_library)} records into library table ───')
    records = []
    for entry in updated_library:
        records.append({
            'id':               entry['id'],
            'src':              entry.get('src', ''),
            'client':           entry.get('client', ''),
            'imageType':        entry.get('imageType', entry.get('type', '')),
            'format':           normalize_format(entry.get('format', '')),
            'productCategory':  normalize_array(entry.get('productCategory', [])),
            'tonality':         normalize_array(entry.get('tonality', [])),
            'designCode':       normalize_array(entry.get('designCode', [])),
            'targetAudience':   normalize_array(entry.get('targetAudience', [])),
            'colourPalette':    normalize_array(entry.get('colourPalette', [])),
            'ingredient':       normalize_array(entry.get('ingredient', [])),
            'style':            normalize_array(entry.get('style', [])),
            'occasion':         normalize_array(entry.get('occasion', [])),
            'mood':             normalize_array(entry.get('mood', [])),
            'typography':       normalize_array(entry.get('typography', [])),
            'finish':           normalize_array(entry.get('finish', [])),
            'keywords':         normalize_array(entry.get('keywords', [])),
            'notes':            entry.get('notes', ''),
            'added':            entry.get('added', entry['id']),
        })

    batch_size = 50
    total = len(records)
    upserted = 0
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        if upsert_records(batch):
            upserted += len(batch)
            print(f'  {min(i+batch_size, total)}/{total} records upserted')
        else:
            print(f'  ✗ Batch failed at index {i}')

    # ── Step 4: Rewrite library.json and library-data.js with new URLs ────────
    print(f'\n── Rewriting {LIBRARY_FILE} with Supabase Storage URLs ──────────')
    with open(LIBRARY_FILE, 'w') as f:
        json.dump(updated_library, f, indent=2)

    with open(DATAJS_FILE, 'w') as f:
        f.write('window.LIBRARY_DATA = \n')
        f.write(json.dumps(updated_library, indent=2))
        f.write('\n')

    print(f'✓ {LIBRARY_FILE} and {DATAJS_FILE} updated')

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f'\n── Summary ──────────────────────────────────────────────────────')
    print(f'✓ {upserted}/{total} records upserted to Supabase')
    print(f'✓ {LIBRARY_FILE} rewritten with Supabase Storage URLs')
    print(f'\nNext steps:')
    print(f'  1. Open the app and verify images load correctly')
    print(f'  2. Add TAGBOT/ to .gitignore (images are now in Supabase Storage):')
    print(f'     echo "TAGBOT/" >> .gitignore')
    print(f'  3. Remove TAGBOT/ from git tracking:')
    print(f'     git rm -r --cached TAGBOT/')
    print(f'  4. Commit: git add -A && git commit -m "Migrate images to Supabase Storage"')

if __name__ == '__main__':
    main()
