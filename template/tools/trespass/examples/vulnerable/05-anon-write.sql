-- A policy handed the anonymous role write access. Unauthenticated visitors can
-- delete anyone's data.
create table waitlist (
  id     uuid primary key,
  email  text,
  user_id uuid
);
alter table waitlist enable row level security;
create policy anyone_delete on waitlist for delete to anon using (true);
