-- Reads are locked down, but INSERT has `with check (true)`, so any user can
-- create a row attributed to someone else (a classic write-side IDOR).
create table posts (
  id         uuid primary key,
  author_id  uuid not null,
  body       text
);
alter table posts enable row level security;
create policy read_own  on posts for select to authenticated using (author_id = auth.uid());
create policy write_any on posts for insert to authenticated with check (true);
