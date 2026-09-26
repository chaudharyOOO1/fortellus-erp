alter table public.attendance
  add column if not exists check_in_lat double precision,
  add column if not exists check_in_lng double precision,
  add column if not exists check_out_lat double precision,
  add column if not exists check_out_lng double precision,
  add column if not exists check_in_distance_m numeric(10,2),
  add column if not exists check_out_distance_m numeric(10,2),
  add column if not exists device_id_hash text,
  add column if not exists is_geofence_verified boolean not null default false,
  add column if not exists is_late_punch boolean not null default false,
  add column if not exists verification_status text not null default 'PENDING';

create index if not exists idx_attendance_geofence_verified on public.attendance(is_geofence_verified);
create index if not exists idx_attendance_device_hash on public.attendance(device_id_hash);
