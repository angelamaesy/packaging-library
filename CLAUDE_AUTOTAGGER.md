# AutoTagger — Claude Code Brief

## Trigger Word

When the user says **"autotag assemble!"**, immediately run the full AutoTagger workflow below without waiting for further instruction. No confirmation needed — just go.

## Your Role

You are the AutoTagger. Your job is to visually analyse unprocessed images in the TAGBOT folder, inject fully-tagged entries into `library.json` and `library-data.js`, then commit and push to GitHub so Vercel deploys automatically.

## CRITICAL: Always work from the correct repo

**The working repo is:** `/Users/angelasy/Desktop/packaging-library/`

There is a stale clone at `/Users/angelasy/packaging-library/` — **never read or write to it.**

All file operations must use these paths:

| File | Path |
|---|---|
| TAGBOT drop zone | `/Users/angelasy/Desktop/packaging-library/TAGBOT/` |
| Checkpoint | `/Users/angelasy/Desktop/packaging-library/tagbot-progress.json` |
| Library JSON | `/Users/angelasy/Desktop/packaging-library/library.json` |
| Library JS | `/Users/angelasy/Desktop/packaging-library/library-data.js` |
| Dated subfolder | `/Users/angelasy/Desktop/packaging-library/TAGBOT/YYYY-MM-DD/` |

## CRITICAL: Batch Processing (do not skip this)

Previous runs got cut off because 300+ images exhausted the context window. You MUST process in batches of 25.

**Before doing anything else:**
1. Read `tagbot-progress.json` — this is your checkpoint
2. Get the full list of unprocessed files from `TAGBOT/` root (jpg/jpeg/png/gif only, not subfolders)
3. Filter out any filenames already in `tagbot-progress.json → processed`
4. Take the **next 25** from that filtered list — that is your batch for this run
5. If there are 0 unprocessed files, report that and stop

## Per-image workflow

For each image in your batch of 25:
1. Read the image file visually
2. Assign full taxonomy tags (see schema below)
3. Write the entry to `library.json` with a **relative src path** pointing to the dated subfolder destination
4. Move the file into `/Users/angelasy/Desktop/packaging-library/TAGBOT/YYYY-MM-DD/` (today's date)

## After the batch

1. Write the updated `library.json` (all existing + new records)
2. Regenerate `library-data.js` from the full `library.json`:
   ```js
   const LIBRARY_DATA = [ ... ];
   ```
3. Update `tagbot-progress.json`:
   - Add all processed filenames to `processed`
   - Set `last_batch_date` to today
4. Commit and push from `/Users/angelasy/Desktop/packaging-library/`:
   ```
   git add TAGBOT/YYYY-MM-DD/ library.json library-data.js tagbot-progress.json
   git commit -m "AutoTagger: tag and commit N images (YYYY-MM-DD)"
   git push
   ```

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
- `src`: **relative path only** — `TAGBOT/YYYY-MM-DD/filename.jpg`. No `file://` prefix. Images are committed to git and served by Vercel as static files so all users can see them.

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
- How many remain (total unprocessed − this batch)
- Estimated runs remaining at 25/batch
- Confirm push was successful
