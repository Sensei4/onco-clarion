# Roadmap

This roadmap is intentionally high-level. Concrete tasks live in
GitHub Issues and project milestones.

## Phase 0 — Foundation ✅

- [x] Technology stack selected (see ADR 0001)
- [x] Domain model defined (see ADR 0002, docs/domain.md)
- [x] Repository structure and documentation
- [x] Backend skeleton (Django + Postgres in Docker)
- [x] Frontend skeleton (React + Vite)
- [x] Authentication end-to-end (session-based)
- [x] CI pipeline (lint + tests)

## Phase 1 — Core domain ✅

- [x] Organization and User models (custom user)
- [x] Patient model and CRUD (multi-tenant by organization)
- [x] CancerCase model with FSM lifecycle (9 statuses)
- [x] StatusTransition audit trail
- [x] Case transitions API with validation
- [x] Event base model and 6 subtypes (primary visit, follow-up,
      observation, consilium, hospitalization, treatment)
- [x] Event API (read all + write per subtype)
- [x] Patient model and CRUD (multi-tenant by organization)
- [x] Patient extended fields: insurance policy number, death date, first diagnosis date
- [x] Case detail UI with transition buttons, timeline, and events
- [x] Event create dialog with per-type fields
- [x] Referral model with 5 types and status lifecycle
- [x] Referral CRUD API with complete/cancel/reopen actions
- [x] Referral UI on case page with filter and detail dialog
- [x] DiagnosticDepartment and DiagnosticMethod reference models (org-scoped)
- [x] Diagnostic assignment on Referral: department, method, assigned_to, scheduled_at, room
- [x] Auto-fill Referral type and title from department/method
- [x] Filter Referrals by department, method, assigned_to, scheduled range
- [x] Document model with 5 types and file storage
- [x] Document upload/download API with multipart support
- [x] Documents section on case page with filter, upload, download, delete

## Phase 2 — Workflows ✅

- [x] Case timeline (status transitions)
- [x] Events section on case page
- [x] Schedule view (planned events for today and upcoming days)
- [x] Waiting list view (cases with `waiting_hospitalization` status)
- [x] Observation list view (cases with `observation` status)
- [ ] Tumor board recording workflow
- [ ] Hospitalization workflow

## Phase 3 — Reporting and interoperability (in progress)

- [x] Basic reports: cases by status, cases by stage, waiting time, events by type, top diagnoses
- [x] Reports page with bar charts and date filter
- [x] Full ICD-11 integration (release 2026-01):
  - [x] Local WHO ICD-API Docker container (offline, no runtime dependency)
  - [x] Full sync: 37,211 MMS + 31,837 foundation entities
  - [x] Search API over local database with synonyms support
  - [x] Autocomplete component in Case form (chapter 02: neoplasms)
  - [x] Case diagnosis linked to ICD-11 MMS entity URI
- [x] FHIR R4B export:
  - [x] Mappers: Patient → Patient, CancerCase → Condition, Event → Encounter, User → Practitioner
  - [x] Endpoints: GET /api/fhir/Patient/{id}/ and /api/fhir/Patient/{id}/$everything/
  - [x] Bundle.type=collection with all related resources
  - [x] Admin-only access
  - [x] Audit logging (AuditEvent.Action.EXPORT)
  - [x] Frontend Export FHIR button on patient page
- [ ] Comorbidities (search across all ICD-11 chapters)
- [ ] CSV export for reports
- [ ] Cross-organization data exchange (design phase)

## Phase 4 — Hardening (in progress)

- [x] AuditEvent model with automatic logging via AuditLogMixin
- [x] Audit log API (admin-only) with filters
- [x] Audit log UI (admin-only page with filters and search)
- [ ] Role-based access control (nurse, lab, consilium member)
- [ ] Localization framework (i18n scaffolding; English UI first)
- [ ] Deployment guide (VPS + Caddy + Docker Compose)
- [ ] Backup and restore procedures

## Out of scope (for now)

- DICOM viewer
- Mobile applications
- Automatic status transitions
- Third-party lab integrations
- Multi-tenant SaaS hosting
