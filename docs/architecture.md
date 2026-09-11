# Architecture

> This document is a work in progress and will be expanded as the
> system takes shape.

## High-level view

    ┌──────────────┐      HTTPS      ┌──────────────┐
    │   React SPA  │ ──────────────▶ │  Django API  │
    │  (Vite, TS)  │ ◀────────────── │  (DRF)       │
    └──────────────┘                 └──────┬───────┘
                                            │
                                            ▼
                                     ┌──────────────┐
                                     │  PostgreSQL  │
                                     └──────────────┘

## Components

- **Frontend** — React SPA served as static files.
- **Backend** — Django REST Framework, session-based auth.
- **Database** — PostgreSQL.
- **File storage** — filesystem in development; S3-compatible
  object storage in production (planned).
- **Reverse proxy** — Caddy in production.

## Decisions

See `docs/adr/` for Architecture Decision Records.
