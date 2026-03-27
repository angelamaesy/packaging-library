-- supabase-setup.sql
-- Run this in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/exavuyhylfzbrxrapuor/sql/new

-- ── 1. Library table ──────────────────────────────────────────────────────────
create table if not exists public.library (
  id                float8    primary key,
  src               text      not null default '',
  client            text      not null default '',
  "imageType"       text      not null default '',
  format            text      not null default '',
  "productCategory" text[]    not null default '{}',
  tonality          text[]    not null default '{}',
  "designCode"      text[]    not null default '{}',
  "targetAudience"  text[]    not null default '{}',
  "colourPalette"   text[]    not null default '{}',
  ingredient        text[]    not null default '{}',
  style             text[]    not null default '{}',
  occasion          text[]    not null default '{}',
  mood              text[]    not null default '{}',
  typography        text[]    not null default '{}',
  finish            text[]    not null default '{}',
  keywords          text[]    not null default '{}',
  notes             text      not null default '',
  added             float8    not null
);

-- ── 2. Row Level Security ─────────────────────────────────────────────────────
-- The app is already protected by a password gate — allow full anon access.
alter table public.library enable row level security;

drop policy if exists "allow_all" on public.library;
create policy "allow_all" on public.library
  for all to anon using (true) with check (true);

-- ── 3. Storage bucket ─────────────────────────────────────────────────────────
-- If you prefer the UI: Storage → New bucket → name "tagbot-images" → Public ✓
insert into storage.buckets (id, name, public)
  values ('tagbot-images', 'tagbot-images', true)
  on conflict (id) do nothing;

-- ── 4. Storage RLS policies ───────────────────────────────────────────────────
drop policy if exists "tagbot_public_read"  on storage.objects;
drop policy if exists "tagbot_anon_upload"  on storage.objects;
drop policy if exists "tagbot_anon_update"  on storage.objects;
drop policy if exists "tagbot_anon_delete"  on storage.objects;

create policy "tagbot_public_read" on storage.objects
  for select to anon using (bucket_id = 'tagbot-images');

create policy "tagbot_anon_upload" on storage.objects
  for insert to anon with check (bucket_id = 'tagbot-images');

create policy "tagbot_anon_update" on storage.objects
  for update to anon using (bucket_id = 'tagbot-images');

create policy "tagbot_anon_delete" on storage.objects
  for delete to anon using (bucket_id = 'tagbot-images');
