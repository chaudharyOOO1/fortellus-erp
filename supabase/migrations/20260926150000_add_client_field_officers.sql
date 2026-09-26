create table if not exists public.client_field_officers (
  id uuid primary key default gen_random_uuid(),
  client_id integer not null references public.clients(id) on delete cascade,
  employee_id uuid not null references public.employees(id) on delete cascade,
  assigned_at timestamptz not null default now(),
  is_active boolean not null default true,
  unique(client_id, employee_id)
);
alter table public.client_field_officers enable row level security;
create index if not exists idx_client_field_officers_client on public.client_field_officers(client_id);
create index if not exists idx_client_field_officers_employee on public.client_field_officers(employee_id);
