# AutoTagger — Claude Code Brief

## Trigger Word

When the user says **"autotag assemble!"**, immediately run the full AutoTagger workflow below without waiting for further instruction. No confirmation needed — just go.

The user may also provide a **source directory** before the trigger word, e.g.:
> *"Images are in `/Users/angelasy/Desktop/new batch/` — autotag assemble!"*

If a source directory is provided, use that as the image source instead of the TAGBOT root. After tagging, still move files into the standard `TAGBOT/YYYY-MM-DD/` dated subfolder and write to `library.json` as normal. If no directory is given, default to scanning the `TAGBOT/` root.

## Your Role

You are the AutoTagger. Your job is to visually analyse unprocessed images in the TAGBOT folder, inject fully-tagged entries into `library.json` and `library-data.js`, then commit and push to GitHub so Vercel deploys automatically.

## CRITICAL: Always work from the correct repo

**The working repo is:** `/Users/angelasy/Desktop/CC/packaging-library/`

There are stale clones at `/Users/angelasy/packaging-library/` and `/Users/angelasy/Desktop/packaging-library/` — **never read or write to either.**

All file operations must use these paths:

| File | Path |
|---|---|
| TAGBOT drop zone | `/Users/angelasy/Desktop/CC/packaging-library/TAGBOT/` |
| Checkpoint | `/Users/angelasy/Desktop/CC/packaging-library/tagbot-progress.json` |
| Library JSON | `/Users/angelasy/Desktop/CC/packaging-library/library.json` |
| Library JS | `/Users/angelasy/Desktop/CC/packaging-library/library-data.js` |
| Dated subfolder | `/Users/angelasy/Desktop/CC/packaging-library/TAGBOT/YYYY-MM-DD/` |

## CRITICAL: Batch Processing

Process in batches of **10** per run. Commit after every batch so no work is lost if the session ends mid-run.

**Before doing anything else:**
1. Read `tagbot-progress.json` — this is your checkpoint
2. Query Supabase for untagged stubs (records with empty `tonality`) — this is the source of truth for what still needs tagging
3. Cross-reference with `tagbot-progress.json → processed` to skip anything already done
4. Take the **next 10** untagged stubs — that is your batch for this run
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
4. Push tagged records to Supabase:
   ```
   python3 push-to-supabase.py
   ```
5. **Update the running counter in `tagbot-progress.json`** — query Supabase after the push and record:
   - `db_total` — total records in DB
   - `db_tagged` — records with non-empty tonality
   - `db_remaining` — records still needing tags
   - `last_push` — today's date
6. Commit and push:
   ```
   git add library.json library-data.js tagbot-progress.json
   git commit -m "AutoTagger: tag N images (YYYY-MM-DD) — X tagged, Y remaining"
   git push
   ```
   Note: TAGBOT/ images are stored in Supabase Storage and should NOT be committed to git.

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
- `src`: **Supabase Storage public URL** — `https://exavuyhylfzbrxrapuor.supabase.co/storage/v1/object/public/tagbot-images/YYYY-MM-DD/filename.jpg`. This URL is set by `add-new-images.py` when the image is ingested — do not change it.
- `format` is now an array — a pack can have multiple formats (e.g. a range shot showing Box + Pouch)

## Tagging philosophy

The taxonomy below is a **baseline, not a ceiling**. It covers ~60–70% of cases. You are expected and encouraged to add new tag values on the fly when you see something that genuinely doesn't fit an existing option — do not force things into wrong buckets and do not ask permission. The goal is maximum accurate, searchable tags. More tags = more findable. Never invent tags randomly — every tag must be something a teammate would actually search for.

**Target richness per image:** aim for 3–5 values in every applicable field. After filling each field, ask yourself: *"What else fits here that a teammate might search for?"* One tag per field is almost always under-tagged.

## Per-field minimums and never-blank rules

### MANDATORY — never leave empty, always infer from the visual

| Field | Rule |
|---|---|
| `imageType` | Always assign exactly one value. |
| `format` | Always tag for Pack Design images. If a range is shown, tag all visible formats. |
| `productCategory` | Tag specific → broad (e.g. `["Chocolate", "Confectionery", "Snack", "Food"]`). Min 2 values. |
| `tonality` | Min 3 values — layer surface feel with underlying character. |
| `designCode` | Tag primary approach AND supporting codes. Min 2 values. |
| `targetAudience` | Tag primary and secondary audiences. Min 2 values. |
| `colourPalette` | Min 3 values — dominant hue group + intensity + temperature. |
| `style` | Min 1 value. Can combine cultural origin + movement + era. |
| `occasion` | Default to `["Everyday"]` if no seasonal or event signals. Never leave blank. |
| `mood` | Min 3 values — push past the first obvious reaction. |
| `ingredient` | Tag all visible front-of-pack flavours/ingredients. Leave `[]` **only** for non-packaging content (pure illustration, poster, mood board with no product). |

### OPTIONAL — tag if visible or inferable, otherwise leave `[]`

| Field | Rule |
|---|---|
| `typography` | Tag if type is visible. Leave `[]` only if there is genuinely no type on the image. |
| `finish` | Tag if the finish is visible or strongly inferable. Leave `[]` if the image is too stylised or flat to judge. |

### MINIMUM ONE — must have at least one value

| Field | Rule |
|---|---|
| `keywords` | Min 12 tags — use the category prompts below to scan systematically. |
| `notes` | Always write a sentence describing what makes this image useful as a reference. |

## Thinking prompts — use these for every image

Before finalising tags, run through these questions:

**Format** — What physical forms are shown? Is there a secondary pack (sachet inside a box, sleeve on a can)?

**productCategory** — What is the broadest category? What is the specific subcategory? Is there a functional crossover (e.g. a snack that is also Health & Wellness)?

**style** — Is there a cultural aesthetic at play? A design movement reference (Bauhaus, Art Deco, Memphis)? A decade? Multiple can apply — a pack can be both Korean and Minimal and Y2K.

**occasion** — Is this clearly for everyday use, or does the design signal a season, holiday, or event? Could it double as gifting even if that's not the primary occasion?

**finish** — Look at the image carefully: does it look like a shiny or flat surface? Are there any metallic, embossed, or textural elements visible? Tag if inferable; leave `[]` only if the image is too stylised to judge.

**colourPalette** — What is the primary colour temperature (Warm / Cool)? What is the intensity (Vivid / Muted / Pastel / Dark)? Are there metallic or gradient elements?

**typography** — What styles of type are used? Are there multiple type styles on the same pack (common in premium design)? Is type the hero or supporting?

**keywords** — After filling all structured fields, scan the image one more time: What specific visual elements, motifs, materials, or descriptors are still untagged? See the keyword prompt categories below.

## Taxonomy — 14 fields

### imageType
Pack Design, Label Design, Key Visual, Campaign, Illustration, Reference, Mood, Product Photography, Range Shot, Structural / Dieline

### format
Bag, Box, Gift Box, Pouch, Can, Bottle, Jar, Carton, Tube, Sachet, Wrapper, Label, Cup, Sleeve, Tray, Tin, Ampoule, Blister Pack, Capsule, Other

### productCategory
Tag from specific → broad. A chocolate snack bar should get `["Chocolate", "Confectionery", "Snack", "Food"]`.

Snack, Food, Confectionery, Chocolate, Bakery, Beverage, Tea, Coffee, Juice, Water, Dairy, Alcohol, Beer, Wine, Spirits, Health & Wellness, Supplement, Personal Care, Skincare, Haircare, Fragrance, Beauty, Makeup, Baby, Pet, Household, Gifting, Stationery, Apparel

### tonality
Layer feel and character — aim for 3–5. A pack can be simultaneously Luxury, Dark, and Ornate, or Minimal, Clean, and Sophisticated.

Bold, Minimal, Playful, Luxury, Dark, Bright, Retro, Heritage, Organic, Earthy, Maximalist, Clinical, Dreamy, Edgy, Elegant, Cool, Fun, Youthful, Vibrant, Feminine, Masculine, Brutalist, Kawaii, Nostalgic, Whimsical, Sophisticated, Approachable, Rebellious, Sensual, Comforting, Energising, Dopamine, Friendly, Gourmet, Ornate

### designCode
Tag the primary approach AND any supporting codes. A pack can be Illustration-led AND Pattern-led AND Colour-led.

Illustration-led, Typography-led, Colour-led, Photography-led, Pattern-led, Clean, Handcrafted, Abstract, Geometric, Line Art, Flat Design, Vector, Comic, Cartoon, Doodle, Pop Art, Text-driven, Gradient, Fluid, 3D, Collage, Mixed Media, Photomontage, Topshot, Visual Hammer

### targetAudience
Consider both the primary and secondary audience. A premium health snack might be `["Health Conscious", "Millennial", "Premium"]`.

Young Adults, Gen Z, Millennial, Gen X, Mass Market, Kids, Teens, Premium, Health Conscious, Eco Conscious, Women, Men, Unisex, Seniors, Parents, Athletes, Beauty Enthusiasts

### colourPalette
Min 3: dominant hue group + intensity + temperature. e.g. `["Dark", "Warm", "Metallic"]` or `["Pastel", "Cool", "Muted"]`.

Bright, Bold, Warm, Cool, Dark, Pastel, Neon, Neutral, Monochrome, Earthy, Metallic, Gradient, Muted, Vivid, Duotone, Black & White, Primary Colours

### style
Can combine cultural origin + design movement + era. e.g. `["Japanese", "Minimal", "Y2K"]` or `["French", "Art Nouveau", "Luxury Editorial"]`.

Japanese, Korean, Chinese, Southeast Asian, European, American, British, French, Scandinavian, Middle Eastern, Latin American, Bauhaus, Swiss / Modernist, Art Deco, Art Nouveau, Memphis, Y2K, 90s, 80s, 70s, Streetwear, Luxury Editorial, Neo-Brutalist, Retro-Futurist, Folk, Naive, Psychedelic, Grunge, Preppy, Cottagecore

### occasion
Default to `["Everyday"]` if no seasonal or event signals. Tag multiple if a design works for more than one context.

Everyday, Summer, Winter, Spring, Autumn, Chinese New Year, Mid-Autumn, Lunar New Year, Christmas, Valentine's Day, Mother's Day, Halloween, Ramadan, Easter, Limited Edition, Launch Campaign, Collab / IP, Anniversary, Gifting Season, Back to School

### mood
Min 3. Push past the first obvious reaction — what is the secondary emotional register?

Aspirational, Trustworthy, Adventurous, Indulgent, Wholesome, Calming, Energising, Nostalgic, Joyful, Mysterious, Confident, Playful, Romantic, Grounded, Empowering, Dreamy, Irreverent

### typography
Tag every distinct type style present. Mixed typography is common in premium and playful design — don't settle for one.

Serif, Sans-serif, Script, Hand-lettered, Display, Blackletter, Condensed, Mixed Fonts, Monospace, Italic, Uppercase Only, Kinetic / Expressive, Wordmark-led, No Type

### finish
Tag if visible or strongly inferable. Leave `[]` only if the image is too stylised or flat to judge. For photography of real packs: Gloss is the default unless the surface looks flat or textured.

Matte, Gloss, Soft Touch, Foil, Emboss, Deboss, Spot UV, Kraft, Textured, Metallic Ink, Transparent, Frosted, Die-cut, Screen Print, Letterpress, Risograph, Uncoated, Recyclable / Eco

### ingredient
What is physically featured or called out on the front of pack — actual product, flavour, or key ingredient. This is front-of-pack hero stuff only, not the full ingredients list. Tag all visible flavours, not just the primary one.
Examples: cookie, chocolate chip, chips, strawberry, matcha, jalapeño, rosemary, sea salt, oat, sesame, lemon, lavender, peanut butter, watermelon, caramel, chilli, mango, hazelnut, blueberry, vanilla, ginger, yuzu, etc.
Leave as `[]` only for non-packaging references (illustrations, posters, key visuals with no product).

### keywords
Free-form — aim for 12–20 tags. **Prefer single words.** Where a concept needs two words, keep it short (e.g. "kraft" not "kraft paper", "character" not "licensed character", "bilingual" not "bilingual text"). The search matches partial strings, so "kraft" will find any entry containing that word. Use the category prompts below to scan systematically — not every category applies to every image, but work through them all before finalising.

**Visual motifs & iconography:** floral, botanical, animal, character, mascot, face, eye, hand, ribbon, badge, crest, stamp, seal, arch, window, frame, pattern, swirl, wave, burst, starburst, sunburst, leaves, fruit, branch, vine, feather, wing, crown, halo, lantern, moon, star, cloud, mountain, landscape, horizon

**Structural & pack details:** range, flat, lifestyle, hero, product, close-up, dieline, pillow, pouch, ziplock, handle, tray, inlay, sleeve, band

**Materials & substrate:** kraft, tissue, glass, metal, ceramic, wood, fabric, washi, foil, film, frosted, eco, recycled

**Composition & layout:** bleed, centred, asymmetric, split, topdown, flatlay, editorial, grid, modular, wraparound, allover, vignette, layered, negative-space

**Typography & text:** wordmark, logotype, monogram, bilingual, multilingual, handwritten, chalk, neon, stencil, overprint, headline, callout, claims, certifications, QR

**Colour specifics:** red, pink, orange, yellow, green, blue, purple, brown, black, white, gold, silver, cream, beige, teal, coral, mint, navy, burgundy, terracotta, sage, lilac, peach, charcoal

**Cultural & thematic references:** tropical, apothecary, artisan, farmhouse, streetfood, finedining, spa, wellness, sport, streetwear, festival, folklore, mythology, celestial, nature, ocean, forest, desert, garden, K-beauty, kawaii

**Design techniques:** handdrawn, screenprint, risograph, grain, watercolour, gouache, linocut, engraving, etching, woodcut, collage, photomontage, duotone, halftone, spot-colour, deboss

**Functional & commercial signals:** new, reformulation, limited, seasonal, collab, character, celebrity, hero, multipack, travel-size, refill, subscription, premium, entry-level

## Duplicate prevention

- Before adding any entry, check `library.json` for an existing record with the same filename in `src`
- If found, skip it and add the filename to `tagbot-progress.json → processed` anyway so it is not re-attempted

## Progress reporting

After completing a batch, report:
- How many images processed this run
- DB totals: X tagged / Y total / Z remaining
- Estimated runs remaining at 10/batch
- Confirm push was successful
