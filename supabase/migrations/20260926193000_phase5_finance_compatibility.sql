alter table public.sites add column if not exists branch_region varchar(30);
alter table public.invoices
  add column if not exists cgst numeric(12,2) not null default 0,
  add column if not exists sgst numeric(12,2) not null default 0,
  add column if not exists igst numeric(12,2) not null default 0,
  add column if not exists clearance_status text not null default 'PENDING';
