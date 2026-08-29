-- The single most common vibe-coded bug: a table exposed through the API with
-- row-level security never turned on. In a 2026 scan of 1,072 Supabase-backed
-- apps, 172 allowed *unauthenticated deletion* of rows this exact way.
create table orders (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id),
  total_cents integer not null,
  card_last4  text
);
-- PostgREST exposes this to anon + authenticated. No RLS => everyone sees everything.
grant select, insert, update, delete on orders to anon, authenticated;
