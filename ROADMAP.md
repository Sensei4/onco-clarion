# Roadmap

This roadmap is intentionally high-level. Concrete tasks live in
GitHub Issues and project milestones.

## Phase 0 — Foundation (current)

- [x] Technology stack selected (see ADR 0001)
- [x] Domain model defined (see ADR 0002, docs/domain.md)
- [ ] Repository structure and documentation
- [ ] Backend skeleton (Django + Postgres in Docker)
- [ ] Frontend skeleton (React + Vite)
- [ ] Authentication end-to-end
- [ ] CI pipeline (lint + tests)

## Phase 1 — Core domain

- [ ] Organization and User models (custom user)
- [ ] Patient model and CRUD
- [ ] CancerCase model with lifecycle (status machine)
- [ ] StatusTransition audit trail
- [ ] Event base model + subtypes (visit, consilium,
      hospitalization, treatment, observation visit)
- [ ] Referral model
- [ ] Document model with file storage

## Phase 2 — Workflows

- [ ] Schedule view (today's and upcoming visits)
- [ ] Waiting list view
- [ ] Observation list view
- [ ] Case timeline (events + status transitions)
- [ ] Tumor board recording workflow
- [ ] Hospitalization workflow

## Phase 3 — Reporting and interoperability

- [ ] Basic reports (patients per stage, per status)
- [ ] ICD-O-3 and ICD-10 reference data
- [ ] FHIR export (Patient, Condition, Encounter)
- [ ] Cross-organization data exchange (design phase)

## Phase 4 — Hardening

- [ ] Audit log UI
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
