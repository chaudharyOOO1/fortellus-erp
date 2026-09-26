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

Current checkpoint status: **READY TO HAND OVER TO PHASE 2**

Next phase:
1. Recruitment candidate pipeline: APPLIED → VERIFIED → ONBOARDED.
2. Unified multi-vertical Staff Profile.
3. KYC/statutory/arms/uniform fields.
4. Compliance expiry evaluation and BENCH locking.
5. Personnel UI with recruitment and compliance tabs.

## Repository audit notes
- Existing production stack: React/Vite frontend + FastAPI backend + Supabase PostgreSQL.
- Existing Supabase schema already contains employees, attendance, salary, invoices, GST/ITC, compliance and risk tables.
- Existing `client_field_officers` table is present and RLS-enabled from the preceding ERP upgrade work.
