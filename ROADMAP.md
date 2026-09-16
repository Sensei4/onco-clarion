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

## Phase 1 — Core domain (in progress)

- [x] Organization and User models (custom user)
- [x] Patient model and CRUD (multi-tenant by organization)
- [x] CancerCase model with FSM lifecycle (9 statuses)
- [x] StatusTransition audit trail
- [x] Case transitions API with validation
- [x] Patient list, detail, and create UI
- [x] Case detail UI with transition buttons and timeline
- [ ] Event base model + subtypes (visit, consilium,
      hospitalization, treatment, observation visit)
- [ ] Referral model
- [ ] Document model with file storage

## Phase 2 — Workflows (partially started)

- [x] Case timeline (status transitions)
- [ ] Schedule view (today's and upcoming visits)
- [ ] Waiting list view (cases with `waiting_hospitalization` status)
- [ ] Observation list view (cases with `observation` status)
- [ ] Tumor board recording workflow
- [ ] Hospitalization workflow

## Phase 3 — Reporting and interoperability

- [ ] Basic reports (patients per stage, per status)
- [ ] ICD-O-3 and ICD-10 reference data
- [ ] FHIR export (Patient, Condition, Encounter)
- [ ] Cross-organization data exchange (design phase)

## Phase 4 — Hardening

- [ ] Audit log UI (user access log)
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
