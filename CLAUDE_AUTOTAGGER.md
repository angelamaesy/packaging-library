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

## CRITICAL: Batch Processing

Process in batches of **50** per run to avoid context window limits.

**Before doing anything else:**
1. Read `tagbot-progress.json` — this is your checkpoint
2. Get the full list of unprocessed files from `TAGBOT/` root (jpg/jpeg/png/gif only, not subfolders)
3. Filter out any filenames already in `tagbot-progress.json → processed`
4. Take the **next 50** from that filtered list — that is your batch for this run
5. If there are 0 unprocessed files, report that and stop

## Per-image workflow

For each image in your batch:
1. Read the image file visually
2. Assign full taxonomy tags across ALL 13 fields (see schema below) — be thorough, accurate, and comprehensive. More tags = more findable. Never tag randomly but always think: what would someone type to find this?
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
  "format": ["Box"],
  "productCategory": ["Snack", "Food"],
  "tonality": ["Bold", "Playful"],
  "designCode": ["Illustration-led", "Colour-led"],
  "targetAudience": ["Young Adults", "Gen Z"],
  "colourPalette": ["Bright", "Warm"],
  "ingredient": ["chocolate chip", "cookie", "oat"],
  "style": ["Japanese", "Minimal"],
  "occasion": ["Everyday", "Gifting Season"],
  "mood": ["Joyful", "Aspirational"],
  "typography": ["Sans-serif", "Display"],
  "finish": ["Matte", "Spot UV"],
  "keywords": ["lemon", "fruit", "summer", "line art", "product shot"],
  "notes": "Free-text description of the image.",
  "added": 1740891600001
}
```

- `id` and `added`: use `Date.now()` style millisecond timestamp — increment by 1 for each image in the batch
- `src`: **relative path only** — `TAGBOT/YYYY-MM-DD/filename.jpg`. No `file://` prefix.
- `format` is now an array — a pack can have multiple formats (e.g. a range shot showing Box + Pouch)

## Tagging philosophy

The taxonomy below is a **baseline, not a ceiling**. It covers ~60–70% of cases. You are expected and encouraged to add new tag values on the fly when you see something that genuinely doesn't fit an existing option — do not force things into wrong buckets and do not ask permission. The goal is maximum accurate, searchable tags. More tags = more findable. Never invent tags randomly — every tag must be something a teammate would actually search for.

## Taxonomy — 14 fields

### imageType
Pack Design, Label Design, Key Visual, Campaign, Illustration, Reference, Mood, Product Photography, Range Shot, Structural / Dieline

### format
Bag, Box, Gift Box, Pouch, Can, Bottle, Jar, Carton, Tube, Sachet, Wrapper, Label, Cup, Sleeve, Tray, Tin, Ampoule, Blister Pack, Capsule, Other

### productCategory
Snack, Food, Confectionery, Chocolate, Bakery, Beverage, Tea, Coffee, Juice, Water, Dairy, Alcohol, Beer, Wine, Spirits, Health & Wellness, Supplement, Personal Care, Skincare, Haircare, Fragrance, Beauty, Makeup, Baby, Pet, Household, Gifting, Stationery, Apparel

### tonality
Bold, Minimal, Playful, Luxury, Dark, Bright, Retro, Heritage, Organic, Earthy, Maximalist, Clinical, Dreamy, Edgy, Elegant, Cool, Fun, Youthful, Vibrant, Feminine, Masculine, Brutalist, Kawaii, Nostalgic, Whimsical, Sophisticated, Approachable, Rebellious, Sensual, Comforting, Energising, Dopamine, Friendly, Gourmet, Ornate

### designCode
Illustration-led, Typography-led, Colour-led, Photography-led, Pattern-led, Clean, Handcrafted, Abstract, Geometric, Line Art, Flat Design, Vector, Comic, Cartoon, Doodle, Pop Art, Text-driven, Gradient, Fluid, 3D, Collage, Mixed Media, Photomontage, Topshot, Visual Hammer

### targetAudience
Young Adults, Gen Z, Millennial, Gen X, Mass Market, Kids, Teens, Premium, Health Conscious, Eco Conscious, Women, Men, Unisex, Seniors, Parents, Athletes, Beauty Enthusiasts

### colourPalette
Bright, Bold, Warm, Cool, Dark, Pastel, Neon, Neutral, Monochrome, Earthy, Metallic, Gradient, Muted, Vivid, Duotone, Black & White, Primary Colours

### style
Japanese, Korean, Chinese, Southeast Asian, European, American, British, French, Scandinavian, Middle Eastern, Latin American, Bauhaus, Swiss / Modernist, Art Deco, Art Nouveau, Memphis, Y2K, 90s, 80s, 70s, Streetwear, Luxury Editorial, Neo-Brutalist, Retro-Futurist, Folk, Naive, Psychedelic, Grunge, Preppy, Cottagecore

### occasion
Everyday, Summer, Winter, Spring, Autumn, Chinese New Year, Mid-Autumn, Lunar New Year, Christmas, Valentine's Day, Mother's Day, Halloween, Ramadan, Easter, Limited Edition, Launch Campaign, Collab / IP, Anniversary, Gifting Season, Back to School

### mood
Aspirational, Trustworthy, Adventurous, Indulgent, Wholesome, Calming, Energising, Nostalgic, Joyful, Mysterious, Confident, Playful, Romantic, Grounded, Empowering, Dreamy, Irreverent

### typography
Serif, Sans-serif, Script, Hand-lettered, Display, Blackletter, Condensed, Mixed Fonts, Monospace, Italic, Uppercase Only, Kinetic / Expressive, Wordmark-led, No Type

### finish
Matte, Gloss, Soft Touch, Foil, Emboss, Deboss, Spot UV, Kraft, Textured, Metallic Ink, Transparent, Frosted, Die-cut, Screen Print, Letterpress, Risograph, Uncoated, Recyclable / Eco

### ingredient
What is physically featured or called out on the front of pack — actual product, flavour, or key ingredient. This is front-of-pack hero stuff only, not the full ingredients list.
Examples: cookie, chocolate chip, chips, strawberry, matcha, jalapeño, rosemary, sea salt, oat, sesame, lemon, lavender, peanut butter, watermelon, caramel, chilli, mango, hazelnut, blueberry, vanilla, ginger, yuzu, etc.
Leave as `[]` for non-packaging references (illustrations, posters, key visuals with no product).

### keywords
Free-form array — add anything specific and searchable that doesn't fit the fields above. Think: materials, motifs, themes, cultural references, techniques, visual elements, descriptors your team would actually type. Examples: floral, animals, characters, swirl, IP collab, lifestyle, botanicals, faces, food photography, abstract shapes, storytelling, noodles, ribbon, badge, crest, hand, eye, stamp, window, kraft paper, green tea, bubble tea, ramen, art deco, filigree, visual hammer, emboss, etc.

## Duplicate prevention

- Before adding any entry, check `library.json` for an existing record with the same filename in `src`
- If found, skip it and add the filename to `tagbot-progress.json → processed` anyway so it is not re-attempted

## Progress reporting

After completing a batch, report:
- How many images processed this run
- How many remain
- Estimated runs remaining at 50/batch
- Confirm push was successful
