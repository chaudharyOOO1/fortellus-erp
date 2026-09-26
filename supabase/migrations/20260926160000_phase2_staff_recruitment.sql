-- Phase 2: unified multi-vertical staff and recruitment/compliance
create table if not exists public.recruitment_candidates (
  id uuid primary key default gen_random_uuid(),
  candidate_id text not null unique,
  full_name text not null,
  phone text not null,
  vertical text not null check (vertical in ('SECURITY','HOUSEKEEPING','NURSING')),
  category text,
  status text not null default 'APPLIED' check (status in ('APPLIED','VERIFIED','ONBOARDED')),
  documents jsonb not null default '{}'::jsonb,
  verified_at timestamptz,
  onboarded_at timestamptz,
  employee_id uuid references public.employees(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.staff_profiles (
  id uuid primary key default gen_random_uuid(),
  employee_id uuid not null unique references public.employees(id) on delete cascade,
  intimation_id text not null unique,
  badge_number text unique,
  vertical text not null check (vertical in ('SECURITY','HOUSEKEEPING','NURSING')),
  category text not null,
  status text not null default 'ACTIVE' check (status in ('ACTIVE','BENCH','INACTIVE','TERMINATED')),
  aadhaar_number text,
  pan_number text,
  bank_account_no text,
  bank_name text,
  bank_ifsc text,
  nominee_name text,
  nominee_relation text,
  nominee_aadhaar text,
  arms_license_no text,
  arms_expiry_date date,
  arms_caliber text,
  ammunition_count integer,
  uniform_total_cost numeric(12,2) not null default 0,
  uniform_monthly_emi numeric(12,2) not null default 0,
  uniform_balance_due numeric(12,2) not null default 0,
  police_verification_expiry date,
  medical_fitness_expiry date,
  psara_cert_no text,
  psara_training_expiry date,
  gun_license_expiry date,
  is_bench_locked boolean not null default false,
  bench_lock_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_recruitment_status on public.recruitment_candidates(status);
create index if not exists idx_staff_vertical_status on public.staff_profiles(vertical,status);
create index if not exists idx_staff_compliance on public.staff_profiles(police_verification_expiry,medical_fitness_expiry);

alter table public.recruitment_candidates enable row level security;
alter table public.staff_profiles enable row level security;

drop policy if exists deny_recruitment_candidates_api on public.recruitment_candidates;
create policy deny_recruitment_candidates_api on public.recruitment_candidates for all to anon, authenticated using (false) with check (false);

drop policy if exists deny_staff_profiles_api on public.staff_profiles;
create policy deny_staff_profiles_api on public.staff_profiles for all to anon, authenticated using (false) with check (false);
