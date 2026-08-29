-- A blog: anyone may read posts, only the author may change them. Declaring the
-- public read intent is what makes this "safe" rather than "leaky".
create table articles (
  id         uuid primary key,
  author_id  uuid not null,
  title      text,
  body       text
);
alter table articles enable row level security;
create policy read_all   on articles for select using (true);
create policy write_own  on articles for insert to authenticated with check (author_id = auth.uid());
create policy update_own on articles for update to authenticated using (author_id = auth.uid()) with check (author_id = auth.uid());
create policy delete_own on articles for delete to authenticated using (author_id = auth.uid());
