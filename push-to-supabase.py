#!/usr/bin/env python3
"""
push-to-supabase.py
-------------------
Reads library.json and upserts all records into the Supabase library table.
Run this after the AutoTagger has filled in metadata for a batch.

Requirements:
    pip install requests python-dotenv

Run from the packaging-library folder:
    python3 push-to-supabase.py
"""

import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL      = os.environ['SUPABASE_URL']
SERVICE_ROLE_KEY  = os.environ['SUPABASE_SERVICE_ROLE_KEY']
LIBRARY_FILE      = 'library.json'

HEADERS = {
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'apikey':        SERVICE_ROLE_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'resolution=merge-duplicates',
}

def normalize_array(val):
    if isinstance(val, list): return val
    if not val: return []
    return [val]

def normalize_format(val):
    if isinstance(val, list): return val[0] if val else ''
    return val or ''

def main():
    with open(LIBRARY_FILE) as f:
        library = json.load(f)

    print(f'Upserting {len(library)} records from {LIBRARY_FILE} to Supabase…')

    records = []
    for entry in library:
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
        r = requests.post(
            f'{SUPABASE_URL}/rest/v1/library',
            headers=HEADERS,
            json=batch,
        )
        if r.status_code in (200, 201):
            upserted += len(batch)
            print(f'  {min(i+batch_size, total)}/{total} records upserted')
        else:
            print(f'  ✗ Batch failed at {i}: {r.status_code} — {r.text[:120]}')

    print(f'\n✓ Done: {upserted}/{total} records synced to Supabase')

if __name__ == '__main__':
    main()
