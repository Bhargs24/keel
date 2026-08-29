-- Multi-tenant table "secured" by inspecting the JWT -- but the claim compared
-- is `role`, which is identical for every authenticated user, not the tenant.
-- The filter looks like tenancy and enforces nothing: every org sees every org.
create table invoices (
  id      uuid primary key,
  org_id  uuid not null,
  amount  integer
);
alter table invoices enable row level security;
create policy tenant_read on invoices
  for select to authenticated
  using ((auth.jwt() ->> 'role') = 'authenticated');
