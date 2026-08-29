-- RLS is on, and the policy is `using (true)` -- which protects nothing. A very
-- common "I turned on RLS, why is it still leaking?" mistake.
create table messages (
  id       uuid primary key,
  user_id  uuid not null,
  body     text
);
alter table messages enable row level security;
create policy "read messages" on messages
  for select to authenticated
  using (true);
