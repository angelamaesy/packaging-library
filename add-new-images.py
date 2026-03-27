#!/usr/bin/env python3
"""
add-new-images.py
-----------------
Finds new images sitting loose in TAGBOT/ (not in any dated subfolder),
moves them into TAGBOT/YYYY-MM-DD/, uploads them to Supabase Storage,
adds stub entries to the Supabase library table and to library.json,
and regenerates library-data.js.

Requirements:
    pip install requests

Run from the packaging-library folder:
    python3 add-new-images.py
"""

import json
import mimetypes
import os
import shutil
import time
from datetime import date
from urllib.parse import quote, unquote
import requests

TAGBOT_DIR        = 'TAGBOT'
LIBRARY_FILE      = 'library.json'
DATAJS_FILE       = 'library-data.js'
IMAGE_EXTS        = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}

SUPABASE_URL      = 'https://exavuyhylfzbrxrapuor.supabase.co'
SERVICE_ROLE_KEY  = 'sb_secret_JUaay_TDSz-A7MbXEQEzMQ_KFxGoofL'
STORAGE_BUCKET    = 'tagbot-images'

HEADERS = {
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'apikey':        SERVICE_ROLE_KEY,
}

def find_new_images():
    """Images sitting directly in TAGBOT/ — not inside any subfolder."""
    new = []
    for name in os.listdir(TAGBOT_DIR):
        full = os.path.join(TAGBOT_DIR, name)
        if os.path.isfile(full) and os.path.splitext(name)[1].lower() in IMAGE_EXTS:
            new.append(name)
    return sorted(new)

def upload_image(local_path, storage_path):
    """Upload a file to Supabase Storage. Returns public URL or None."""
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
        return f'{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{quote(storage_path)}'
    print(f'  ✗ Upload failed ({r.status_code}): {r.text[:120]}')
    return None

def insert_stub(entry):
    """Insert a stub record into the Supabase library table."""
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/library',
        headers={**HEADERS, 'Content-Type': 'application/json',
                 'Prefer': 'resolution=ignore-duplicates'},
        json=[entry],
    )
    return r.status_code in (200, 201)

def load_library():
    with open(LIBRARY_FILE) as f:
        return json.load(f)

def save_library(data):
    with open(LIBRARY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_datajs(data):
    with open(DATAJS_FILE, 'w') as f:
        f.write('window.LIBRARY_DATA = \n')
        f.write(json.dumps(data, indent=2))
        f.write('\n')

def make_stub(public_url, timestamp):
    return {
        'id':              timestamp,
        'src':             public_url,
        'client':          '',
        'imageType':       '',
        'format':          '',
        'productCategory': [],
        'tonality':        [],
        'designCode':      [],
        'targetAudience':  [],
        'colourPalette':   [],
        'ingredient':      [],
        'style':           [],
        'occasion':        [],
        'mood':            [],
        'typography':      [],
        'finish':          [],
        'keywords':        [],
        'notes':           '',
        'added':           timestamp,
    }

def main():
    new_images = find_new_images()

    if not new_images:
        print('No new images found in TAGBOT/. Nothing to do.')
        return

    print(f'Found {len(new_images)} new image(s):')
    for name in new_images:
        print(f'  {name}')

    dated_folder = str(date.today())  # e.g. "2026-03-27"
    dest_dir = os.path.join(TAGBOT_DIR, dated_folder)
    os.makedirs(dest_dir, exist_ok=True)

    library = load_library()
    existing_srcs = {e['src'] for e in library}

    new_entries = []
    skipped = []

    for i, name in enumerate(new_images):
        storage_path = f'{dated_folder}/{name}'
        pub_url = f'{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{quote(storage_path)}'

        if pub_url in existing_srcs:
            skipped.append(name)
            continue

        src_path  = os.path.join(TAGBOT_DIR, name)
        dest_path = os.path.join(dest_dir, name)

        # Move file to dated folder
        shutil.move(src_path, dest_path)

        # Upload to Supabase Storage
        print(f'  Uploading {name} … ', end='', flush=True)
        result_url = upload_image(dest_path, storage_path)
        if not result_url:
            print(f'  ✗ Skipping {name} due to upload failure')
            # Move file back
            shutil.move(dest_path, src_path)
            continue
        print('✓')

        timestamp = int(time.time() * 1000) + i
        stub = make_stub(result_url, timestamp)

        # Insert stub into Supabase
        if not insert_stub(stub):
            print(f'  ✗ DB insert failed for {name}')

        new_entries.append(stub)

    if skipped:
        print(f'\nSkipped (already in library): {skipped}')

    if new_entries:
        library = new_entries + library
        save_library(library)
        save_datajs(library)

        print(f'\n✓ Uploaded {len(new_entries)} image(s) → Supabase Storage / {dated_folder}/')
        print(f'✓ Inserted {len(new_entries)} stub entry(s) into Supabase library table')
        print(f'✓ Updated {LIBRARY_FILE} and {DATAJS_FILE}')
        print(f'\nNext steps:')
        print(f'  1. Run the autotagger to fill in metadata')
        print(f'  2. After autotagger: python3 push-to-supabase.py')
        print(f'  3. git add library.json library-data.js tagbot-progress.json && git commit -m "Add {len(new_entries)} new images" && git push')
    else:
        print('No new entries added.')

if __name__ == '__main__':
    main()
