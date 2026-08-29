-- Correct organization-scoped multi-tenancy: every row carries an org_id, and
-- the policy ties it to the caller's org claim. Proved isolated.
create table invoices (
  id      uuid primary key,
  org_id  uuid not null,
  amount  integer
);
alter table invoices enable row level security;
alter table invoices force row level security;
create policy tenant_all on invoices
  for all to authenticated
  using (org_id = (auth.jwt() ->> 'org_id')::uuid)
  with check (org_id = (auth.jwt() ->> 'org_id')::uuid);
