# Fortellus Enterprise ERP — Implementation Progress

Last updated: 2026-09-26
Active roadmap: Master Implementation Plan v2.0

## Phase 1 — Brand Unification & Granular RBAC

### Backend
- [x] Fortellus project identity updated in FastAPI settings.
- [x] Version baseline updated to 2.0.0.
- [x] Enterprise roles present in `UserRole`: OWNER, SUPER_ADMIN, ADMIN (legacy), HR, OPERATIONS, ACCOUNTS, SUPERVISOR, CLIENT, STAFF.
- [x] JWT access tokens now carry the authenticated user's role claim.
- [x] `RoleChecker` accepts multiple roles.
- [x] Added `require_roles(...)` helper.
- [x] Added strict `get_current_owner` helper.
- [x] Existing admin dependencies remain compatible with the legacy ADMIN role.
- [x] Production Supabase users provisioned for the enterprise persona set; credentials inherit the existing administrator password hash and must be reset to the client's chosen initial password if different.

### Frontend
- [x] Browser title and metadata updated to Fortellus Security & Facility Management ERP.
- [x] Main application branding updated to FORTELLUS ENTERPRISE ERP.
- [x] Owner Executive navigation shell added and hidden from non-OWNER roles.
- [x] Login page rebranded to Fortellus enterprise portal.
- [x] Quick persona login chips added for Owner, HR, Operations, Accounts, Client and Employee.
- [x] Persona switching now uses live API authentication instead of client-only demo tokens.
- [x] `ProtectedRoute` now supports role-based access restrictions and a 403 state.
- [x] Application routes assigned to enterprise role groups.

### Production / Verification
- [x] Latest production deployment reached READY.
- [x] Production login HTML returns HTTP 200.
- [x] Production bundle contains Fortellus branding, owner-executive route, and 403 guard.
- [x] Supabase `users` table contains the enterprise role accounts.
- [ ] Verify live persona credentials end-to-end through the production login form.
- [ ] Replace the temporary Phase 1 Owner Executive shell with the full Phase 6 implementation.

## STOP & HANDOVER CHECKPOINT 1

Current checkpoint status: **COMPLETED — PHASE 2 IMPLEMENTED / LIVE SCHEMA DEPLOYED**

Phase 2 verification:
1. [x] Recruitment candidate pipeline: APPLIED → VERIFIED → ONBOARDED.
2. [x] Unified multi-vertical Staff Profile with SECURITY / HOUSEKEEPING / NURSING.
3. [x] Mandatory Aadhaar/PAN/Bank Account/IFSC validation; Aadhaar uses Verhoeff checksum.
4. [x] Gunman arms fields enforced during onboarding.
5. [x] Missing/expired Police Verification or Medical Fitness creates BENCH LOCK at onboarding.
6. [x] Compliance runner re-evaluates existing staff and synchronizes employee status/reason.
7. [x] Personnel UI provides staff, recruitment and compliance views with vertical filtering.
8. [x] Phase 2 frontend/backend CI passed on commits 986a74f, 4ee4c0b and 7972ceb.
9. [x] Live Phase 2 Supabase migration applied to production project `zvogktuqdcpjsfargewg`; protected API routes and health/docs endpoints verified.

## STOP & HANDOVER CHECKPOINT 2

Current checkpoint status: **PHASE 3 COMPLETE IN REPOSITORY; LIVE DEPLOYMENT CHECKPOINT DEFERRED**

Phase 3 implementation completed in repository:
1. [x] 15-character GSTIN validation and branch-region enforcement.
2. [x] Client contract records with 30/60-day renewal classification.
3. [x] Site-specific multi-tier rate-card schema and APIs.
4. [x] Site latitude/longitude/geofence-radius fields for Phase 4 readiness.
5. [x] Roster BENCH-lock prevention.
6. [x] Same-date guard collision prevention across sites.
7. [x] Shortfall Index calculation and replacement suggestions.
8. [x] Client, site and roster UI updated for the Phase 3 controls.
9. [x] Phase 3 migration applied to production Supabase.
10. [ ] Final CI/Vercel production rollout and authenticated end-to-end checkpoint verification.

STOP & HANDOVER CHECKPOINT 3 remains pending until the production build is READY and the four PDF verification scenarios are executed.

## Phase 3 modified files
- `backend/app/api/v1/api.py` — registered contract/rate APIs.
- `backend/app/api/v1/endpoints/client_master.py` — GSTIN enforcement and contract renewal metadata.
- `backend/app/api/v1/endpoints/contract_master.py` — dynamic contract and site rate-card APIs.
- `backend/app/api/v1/endpoints/site_master.py` — GPS/geofence-ready site master.
- `backend/app/api/v1/endpoints/roster_master.py` — BENCH-lock prevention, collision prevention and shortfall analysis.
- `frontend/src/pages/Clients.jsx` — GSTIN and contract renewal UI.
- `frontend/src/pages/Sites.jsx` — GPS/geofence UI.
- `frontend/src/pages/Rosters.jsx` — shortfall alerts and deployment safeguards.
- `supabase/migrations/20260926173000_phase3_contract_rates_roster.sql` — contracts, rate cards and site geofence schema.

## Phase 2 modified files
- `backend/app/api/v1/endpoints/recruitment.py` — recruitment pipeline, onboarding, KYC, Aadhaar and compliance lock enforcement (127 lines).
- `backend/app/api/v1/endpoints/staff.py` — compliance evaluation and BENCH synchronization (49 lines).
- `frontend/src/pages/Personnel.jsx` — Staff Master, recruitment and compliance UI (76 lines).
- `supabase/migrations/20260926160000_phase2_staff_recruitment.sql` — recruitment/staff schema and RLS (64 lines).

## Repository audit notes
- Existing production stack: React/Vite frontend + FastAPI backend + Supabase PostgreSQL.
- Existing Supabase schema already contains employees, attendance, salary, invoices, GST/ITC, compliance and risk tables.
- Existing `client_field_officers` table is present and RLS-enabled from the preceding ERP upgrade work.


## Deployment trigger
- [x] Phase 3 source consolidated on main; this commit triggers the consolidated Vercel production build.
- [x] Manual redeploy trigger requested after verifying the previous production deployment remained on commit d62c84ce.


## Phase 4 — GPS Geofenced Attendance & Field Verification
Current status: **IMPLEMENTED IN GITHUB**
- [x] Haversine geofence helper with configurable site radius, default 100m.
- [x] Server-side GPS validation for staff check-in/check-out.
- [x] Device fingerprint hashing and roster device-binding enforcement.
- [x] Verified check-in/check-out coordinates and distance persisted.
- [x] Regular hours and overtime calculated at checkout.
- [x] Staff assigned-roster endpoint added for the field terminal.
- [x] Dashboard field punch wired to browser geolocation.
- [x] Attendance UI displays GPS verification and distance.
- [ ] Live authenticated GPS checkpoint test.

## Phase 5 — Automated Statutory Payroll & Tax Invoicing
Current status: **IMPLEMENTED IN GITHUB**
- [x] Payroll run lifecycle DRAFT/CALCULATED/APPROVED/DISBURSED schema.
- [x] Attendance-driven salary calculation.
- [x] Basic/HRA/allowances/OT/night allowance.
- [x] PF 12%, ESIC 0.75%, LWF and Uniform EMI deductions.
- [x] Salary Hold Engine with mandatory audit note.
- [x] PDF payslip endpoint and frontend payroll workspace.
- [x] Verified-attendance billing endpoint with CGST/SGST vs IGST calculation.
- [x] Payroll migration and reportlab runtime dependency added.
- [ ] Live authenticated payroll/invoice checkpoint test.

## Phase 6 — Owner Executive Command Center
Current status: **IMPLEMENTED IN GITHUB**
- [x] OWNER-only executive summary API.
- [x] Revenue, expenses, payroll, statutory liabilities, net profit and net margin.
- [x] Client-level dynamic P&L view.
- [x] Financial, compliance and operational risk-radar foundation.
- [x] Owner Executive UI activated.
- [ ] Live authenticated OWNER checkpoint test.

## GitHub-first build policy
All remaining production verification and deployment actions are intentionally deferred until the complete implementation is built and CI-verified on GitHub.


## GitHub Validation Pass — 2026-09-26
- [x] Added repository CI workflow at `.github/workflows/erp-ci.yml` for backend dependency install, Python compilation, regression tests, FastAPI import validation, frontend lint and production build.
- [x] Added geofence regression tests under `backend/tests/test_geofence.py`.
- [x] Added Phase 5 compatibility migration for invoice GST split fields, site branch region and finance expense ledger.
- [x] Corrected attendance billing to use the existing invoice schema and site/client region fields.
- [x] Corrected Owner P&L to use the new finance expense ledger.
- [x] Confirmed `main` is the repository branch.
- [ ] GitHub-hosted CI result still needs to be observed; the connected GitHub workflow-run endpoint only exposes pull-request-triggered runs.
- [ ] Live Supabase Phase 5 migration application and authenticated Phase 4-6 checkpoint testing remain after repository CI.
- [ ] Vercel deployment remains intentionally deferred.


## Supabase Phase 4-6 Database Checkpoint — 2026-09-26
- [x] Applied `phase5_payroll_finance` to production Supabase project `zvogktuqdcpjsfargewg`.
- [x] Applied `phase5_finance_compatibility` to production Supabase project.
- [x] Verified GPS attendance columns required by the Phase 4 API exist.
- [x] Verified payroll_runs, salary_slips and salary_slip_holds exist with RLS.
- [x] Verified invoice GST split fields and site branch region exist.
- [x] Verified live baseline contains 2 employees, 0 verified GPS attendance rows, 0 payroll runs, 0 salary slips, 0 posted invoices and 0 expenses; no synthetic test records were inserted.
- [x] Supabase security advisor reviewed; new payroll tables have deny policies. Existing INFO findings remain on pre-existing `attendances` and `users` RLS policy coverage.
- [ ] Authenticated end-to-end Phase 4-6 test still requires a valid authorized ERP account/session.
- [ ] Vercel deployment remains deferred until GitHub validation is complete.


## CI / Schema Audit — 2026-09-26
- [x] GitHub Actions ERP CI passed on main commit `130edf957530eb7d7956c96eb76fd3e6cd64042c`: backend and frontend jobs both SUCCESS.
- [x] Live schema audit completed for attendance, rosters, staff, payroll, invoices and finance tables.
- [x] Corrected payroll manual salary-hold persistence to use `salary_slip_holds`, matching the new payroll slip schema.
- [ ] CI re-run for the latest salary-hold correction pending/expected from the new push.
