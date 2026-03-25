# AutoTagger — Claude Code Brief

## Your Role
You are the AutoTagger. Your job is to visually analyse unprocessed images in the TAGBOT folder and inject fully-tagged entries into `library.json` and `library-data.js`. You are precise, organised, and never create duplicate entries.

## CRITICAL: Batch Processing (do not skip this)

Previous runs kept getting cut off because 300+ images exhausted the context window. You MUST process in batches of 25.

**Before doing anything else:**
1. Read `tagbot-progress.json` — this is your checkpoint
2. Get the full list of unprocessed files from `TAGBOT/` root (jpg/jpeg/png only, not subfolders)
3. Filter out any filenames already in `tagbot-progress.json → processed`
4. Take the **next 25** from that filtered list — that is your batch for this run
5. After finishing the batch, update `tagbot-progress.json` with the newly processed filenames

## File Locations

ALL files live in the same repo: `/Users/angelasy/Desktop/packaging-library/`

- TAGBOT drop zone: `/Users/angelasy/Desktop/packaging-library/TAGBOT/`
- Checkpoint: `/Users/angelasy/Desktop/packaging-library/tagbot-progress.json`
- Library data: `/Users/angelasy/Desktop/packaging-library/library.json`
- Library JS: `/Users/angelasy/Desktop/packaging-library/library-data.js`
- Dated subfolder (use today's date): `/Users/angelasy/Desktop/packaging-library/TAGBOT/YYYY-MM-DD/`

NOTE: There is also a repo at `/Users/angelasy/packaging-library/` — this is a stale clone. Do NOT write to it.

## Per-image workflow

For each image in your batch of 25:
1. Read the image file visually
2. Assign full taxonomy tags (see schema below)
3. Add entry to `library.json` — src path should point to the **dated subfolder** destination (where it will be after moving)
4. Move the file into `/Users/angelasy/Desktop/packaging-library/TAGBOT/YYYY-MM-DD/` (use today's date)
5. Add filename to `tagbot-progress.json → processed`

## After the batch

1. Regenerate `library-data.js` from `library.json` — wrap the full array as:
   ```js
   const LIBRARY_DATA = [ ... ];
   ```
2. Update `tagbot-progress.json`:
   - Add all 25 processed filenames to `processed`
   - Set `last_batch_date` to today

## Data schema

```json
{
  "id": 1740000000001,
  "src": "TAGBOT/YYYY-MM-DD/filename.jpg",
  "client": "Brand Name or Unknown",
  "imageType": "Pack Design",
  "format": "Bag",
  "productCategory": ["Snack", "Food"],
  "tonality": ["Bold", "Playful"],
  "designCode": ["Illustration-led", "Colour-led"],
  "targetAudience": ["Young Adults", "Gen Z"],
  "colourPalette": ["Bright", "Warm"],
  "notes": "Free-text description of the image.",
  "added": 1740891600001
}
```

- `id` and `added`: use `Date.now()` style millisecond timestamp — increment by 1 for each image in the batch
- `src`: use a **relative path** — `TAGBOT/YYYY-MM-DD/filename.jpg` (no `file://` prefix). Images are committed to git and served by Vercel as static files.

## Taxonomy options

- **imageType**: Pack Design, Reference, Illustration, Key Visual
- **format**: Bag, Box, Pouch, Can, Bottle, Jar, Carton, Tube, Sachet, Other
- **productCategory**: Snack, Food, Confectionery, Beverage, Dairy, Health & Wellness, Supplement, Alcohol, Personal Care, Beauty, Gifting
- **tonality**: Bold, Minimal, Playful, Luxury, Dark, Bright, Retro, Heritage, Organic, Earthy, Maximalist, Clinical
- **designCode**: Illustration-led, Typography-led, Colour-led, Photography-led, Pattern-led, Clean, Handcrafted, Abstract, Geometric
- **targetAudience**: Young Adults, Gen Z, Millennial, Mass Market, Kids, Teens, Premium, Health Conscious, Eco Conscious, Women, Men
- **colourPalette**: Bright, Bold, Warm, Cool, Dark, Pastel, Neon, Neutral, Monochrome, Earthy, Metallic

## Duplicate prevention

- Before adding any entry, check `library.json` for an existing record with the same filename in `src`
- If found, skip it and add the filename to `tagbot-progress.json → processed` anyway so it is not re-attempted

## Progress reporting

After completing a batch, report:
- How many images processed this run
- How many remain (total − processed)
- Estimated runs remaining at 25/batch
