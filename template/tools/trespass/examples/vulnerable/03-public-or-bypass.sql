-- Owner-only *except* for an is_public escape hatch that was meant for something
-- else. With an owner-only intent declared, trespass proves this leaks.
create table documents (
  id         uuid primary key,
  user_id    uuid not null,
  is_public  boolean default false,
  title      text,
  body       text
);
alter table documents enable row level security;
create policy read_docs on documents
  for select to authenticated
  using (user_id = auth.uid() or is_public);
