-- The correct owner-only pattern. trespass proves no authenticated user can
-- reach another user's rows, and no one can forge a row for someone else.
create table secrets (
  id       uuid primary key,
  user_id  uuid not null,
  value    text
);
alter table secrets enable row level security;
create policy read_own   on secrets for select to authenticated using (user_id = auth.uid());
create policy insert_own on secrets for insert to authenticated with check (user_id = auth.uid());
create policy update_own on secrets for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy delete_own on secrets for delete to authenticated using (user_id = auth.uid());
