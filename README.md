# OncoClarion

An open-source web application for organizing the work of oncology
dispensaries and cancer clinics: patient flow, medical encounters,
tumor boards, hospitalizations, and long-term follow-up.

> **Status:** early development (pre-alpha). Not ready for clinical use.

## What problem does it solve

Oncology care is not a single visit — it is a long, cyclical journey
that moves a patient through several stages:

    visit → diagnostics → tumor board → waiting list →
    hospitalization → treatment → follow-up → (repeat) → remission

Most generic EMR systems model documents. OncoClarion models the
**patient flow** — the queues and transitions that oncologists
actually work with every day.

## Core concepts

- **Patient** — a person. Lives long, may have multiple cancer cases.
- **CancerCase** — one primary tumor with its metastases.
  Has a lifecycle (status) and moves through queues.
- **Event** — anything that happens in time: visit, tumor board,
  hospitalization, treatment, follow-up visit.
- **Queue** — not a table, but a _view_ over cases in a given status:
  schedule, waiting list, observation list.

See [`docs/domain.md`](docs/domain.md) for the full domain model.

## Tech stack

- Backend: Python 3.14, Django 5, Django REST Framework
- Database: PostgreSQL 16
- Frontend: React 18, TypeScript, Vite, shadcn/ui, TanStack Query
- Auth: Django session-based auth
- Infra: Docker Compose, Caddy (production)
- License: Apache 2.0

See [`docs/adr/`](docs/adr/) for architecture decision records.

## Getting started

> Requires Docker Desktop.

    git clone https://github.com/Sensei4/onco-clarion.git
    cd onco-clarion
    cp .env.example .env
    docker compose up

- Backend API: http://localhost:8000/api/
- Django admin: http://localhost:8000/admin/
- Frontend: http://localhost:5173/

Create a superuser:

    docker compose exec backend python manage.py createsuperuser

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

## Disclaimer

OncoClarion is a **research and educational project**. It is **not**
a certified medical device and is **not** intended for clinical use
without independent validation, regulatory review, and compliance
with local laws (e.g. GDPR, HIPAA) in the jurisdiction where it is
deployed. The authors take no responsibility for clinical decisions
made using this software.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions from
clinicians, medical informaticians, and developers are welcome.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
