# Builder — Claude Code Brief

## Your Role
You are the Builder. Your job is to build, maintain, and improve the packaging design reference library app. You work on a single `index.html` file with vanilla JavaScript — no backend, no build step, no frameworks. Do not over-engineer. Make it work, make it clean.

The CEO (Angela) is your primary stakeholder. Communicate clearly, avoid jargon, keep changes focused and practical.

## Project Location
The real working directory is `~/Desktop/packaging-library/` — NOT `~/packaging-library/`.
Always read, edit, and commit from `~/Desktop/packaging-library/`.

## Deployment
- Git remote: `https://github.com/angelamaesy/packaging-library.git`
- Deployed via Vercel: `https://vercel.com/25s/packaging-library/deployments`
- Images are in `TAGBOT/` and referenced with relative paths (e.g. `TAGBOT/2026-03-24/filename.jpg`)
- To deploy: `cd ~/Desktop/packaging-library && git add -A && git commit -m "message" && git push`

## Moodboard Templates

There are 3 templates (as of 2026-03-25):

1. **Territory Split** — works well, no changes needed
2. **Collage Overlay** — full-width chain of up to 5 images (portrait/landscape alternating, overlapping at edges), centered title at top, warm off-white background (`#f4f3ef`)
3. **Column Analysis** — works well, no changes needed

**Annotated Scatter was removed** on 2026-03-25 — layout was too uneven and messy.

### Export constraints
The PNG export (`exportMoodboard`) uses `getBoundingClientRect` to position images on a native canvas. Two important limitations:
- **CSS `transform: rotate()` is not captured** — images are drawn at their bounding box position without rotation. Do not use CSS rotation in templates.
- **Export background is hardcoded to `#0d0d10`** (dark) — template CSS background colours do not appear in the exported PNG.

## Known Bugs

No known bugs as of 2026-03-25. All previously logged Moodboard Builder issues (image load timing, thumbnail selection, generate button) are resolved.
