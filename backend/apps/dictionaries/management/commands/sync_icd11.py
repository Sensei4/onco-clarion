"""Sync ICD-11 from the local ICD-API container into the database.

Usage:
    python manage.py sync_icd11 --release 2026-01
    python manage.py sync_icd11 --release 2026-01 --chapters 02
    python manage.py sync_icd11 --release 2026-01 --dry-run

This command:
  1. Fetches the MMS root (list of chapters).
  2. For each chapter, walks the subtree breadth-first.
  3. Saves MmsEntity records in batches.
  4. Collects foundation URIs and syncs FoundationEntity records.
  5. Logs progress to Icd11SyncLog.

Idempotent: re-running updates existing records (update_or_create by URI).
Interruptible: progress is saved after each chapter.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.dictionaries.exceptions import (
    IcdApiError,
    IcdApiNotFoundError,
)
from apps.dictionaries.icd_client import IcdApiClient
from apps.dictionaries.models import (
    FoundationEntity,
    Icd11SyncLog,
    MmsEntity,
)

logger = logging.getLogger(__name__)

MMS_BATCH_SIZE = 100
FOUNDATION_BATCH_SIZE = 100
PROGRESS_EVERY = 200


class Command(BaseCommand):
    help = "Sync ICD-11 entities from the local ICD-API container."

    def add_arguments(self, parser):
        parser.add_argument(
            "--release",
            type=str,
            default="2026-01",
            help="ICD-11 release id, e.g. 2026-01",
        )
        parser.add_argument(
            "--chapters",
            type=str,
            default=None,
            help="Comma-separated chapter codes to sync (e.g. '02,03'). " "Default: all chapters.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Walk the tree but do not write to the database.",
        )
        parser.add_argument(
            "--max-entities",
            type=int,
            default=None,
            help="Stop after this many MMS entities (for testing).",
        )

    def handle(self, *args, **options):
        release_id: str = options["release"]
        chapters_filter: set[str] | None = None
        if options["chapters"]:
            chapters_filter = {c.strip() for c in options["chapters"].split(",") if c.strip()}
        dry_run: bool = options["dry_run"]
        max_entities: int | None = options["max_entities"]

        client = IcdApiClient()

        # Verify connection
        try:
            root = client.get_mms_root(release_id=release_id)
        except IcdApiError as exc:
            raise CommandError(f"Cannot reach ICD-API at {client.base_url}: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(f"Connected to ICD-API ({client.base_url}), release {release_id}.")
        )
        self.stdout.write(f"MMS root title: {client.extract_title(root)}")

        # Create sync log
        sync_log: Icd11SyncLog | None = None
        if not dry_run:
            sync_log = Icd11SyncLog.objects.create(
                release_id=release_id,
                status=Icd11SyncLog.Status.RUNNING,
            )
            self.stdout.write(f"Created sync log #{sync_log.pk}.")

        try:
            mms_count, foundation_count = self._run_sync(
                client=client,
                release_id=release_id,
                root=root,
                chapters_filter=chapters_filter,
                dry_run=dry_run,
                max_entities=max_entities,
                sync_log=sync_log,
            )
        except Exception as exc:
            if sync_log is not None:
                sync_log.status = Icd11SyncLog.Status.FAILED
                sync_log.finished_at = timezone.now()
                sync_log.error_message = str(exc)[:5000]
                sync_log.save()
            raise

        if sync_log is not None:
            sync_log.status = Icd11SyncLog.Status.SUCCESS
            sync_log.finished_at = timezone.now()
            sync_log.mms_count = mms_count
            sync_log.foundation_count = foundation_count
            sync_log.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync complete: {mms_count} MMS entities, "
                f"{foundation_count} foundation entities."
            )
        )

    # ------------------------------------------------------------------
    # Core sync logic
    # ------------------------------------------------------------------
    def _run_sync(
        self,
        *,
        client: IcdApiClient,
        release_id: str,
        root: dict[str, Any],
        chapters_filter: set[str] | None,
        dry_run: bool,
        max_entities: int | None,
        sync_log: Icd11SyncLog | None,
    ) -> tuple[int, int]:
        """Walk the MMS tree chapter by chapter.

        Returns (mms_count, foundation_count).
        """
        # Step 1: identify chapters from the root
        chapter_uris: list[str] = list(root.get("child", []))

        # Step 2: fetch each chapter to get its code, filter if needed
        selected_chapters: list[tuple[str, str]] = []  # (uri, code)
        for chapter_uri in chapter_uris:
            try:
                chapter_entity = client.get_mms_entity(chapter_uri)
            except IcdApiError as exc:
                logger.warning("Cannot fetch chapter %s: %s", chapter_uri, exc)
                continue

            code = client.extract_code(chapter_entity)
            if chapters_filter is not None and code not in chapters_filter:
                continue
            selected_chapters.append((chapter_uri, code))

        self.stdout.write(f"Selected {len(selected_chapters)} chapter(s) to sync.")

        # Step 3: sync each chapter's subtree
        total_mms = 0
        foundation_uris: set[str] = set()

        for chapter_uri, chapter_code in selected_chapters:
            self.stdout.write(self.style.MIGRATE_HEADING(f"--- Chapter {chapter_code} ---"))
            mms_count, chapter_foundation_uris = self._sync_chapter(
                client=client,
                chapter_uri=chapter_uri,
                chapter_code=chapter_code,
                dry_run=dry_run,
                max_entities=max_entities,
                sync_log=sync_log,
                already_processed=total_mms,
            )
            total_mms += mms_count
            foundation_uris.update(chapter_foundation_uris)

            if max_entities is not None and total_mms >= max_entities:
                self.stdout.write(
                    self.style.WARNING(f"Reached --max-entities={max_entities}, stopping early.")
                )
                break

        # Step 4: sync foundation entities
        self.stdout.write(self.style.MIGRATE_HEADING("--- Foundation ---"))
        foundation_count = self._sync_foundation(
            client=client,
            foundation_uris=foundation_uris,
            dry_run=dry_run,
        )

        return total_mms, foundation_count

    def _sync_chapter(
        self,
        *,
        client: IcdApiClient,
        chapter_uri: str,
        chapter_code: str,
        dry_run: bool,
        max_entities: int | None,
        sync_log: Icd11SyncLog | None,
        already_processed: int,
    ) -> tuple[int, set[str]]:
        """Walk one chapter's subtree via BFS."""
        queue: deque[str] = deque([chapter_uri])
        visited: set[str] = set()
        foundation_uris: set[str] = set()

        mms_buffer: list[dict[str, Any]] = []
        mms_count = 0

        while queue:
            uri = queue.popleft()
            if uri in visited:
                continue
            visited.add(uri)

            try:
                entity = client.get_mms_entity(uri)
            except IcdApiNotFoundError:
                logger.warning("MMS entity not found: %s", uri)
                continue
            except IcdApiError as exc:
                logger.error("Error fetching %s: %s", uri, exc)
                continue

            # Extract data
            code = client.extract_code(entity)
            title = client.extract_title(entity)
            is_leaf = not entity.get("child")
            is_unspecified = uri.endswith("/unspecified")
            is_other = uri.endswith("/other")
            foundation_uri = entity.get("source", "") or ""

            mms_buffer.append(
                {
                    "uri": uri,
                    "the_code": code,
                    "title": title,
                    "chapter": chapter_code,
                    "is_leaf": is_leaf,
                    "is_residual_unspecified": is_unspecified,
                    "is_residual_other": is_other,
                    "parent_uris": entity.get("parent", []) or [],
                    "child_uris": entity.get("child", []) or [],
                    "synonyms": client.extract_synonyms(entity),
                    "foundation_uri": foundation_uri,
                    "last_synced_at": timezone.now(),
                }
            )

            if foundation_uri:
                foundation_uris.add(foundation_uri)

            # Enqueue children
            for child_uri in entity.get("child", []) or []:
                if child_uri not in visited:
                    queue.append(child_uri)

            mms_count += 1

            # Flush buffer
            if len(mms_buffer) >= MMS_BATCH_SIZE:
                self._flush_mms(mms_buffer, dry_run=dry_run)
                mms_buffer = []

            if (already_processed + mms_count) % PROGRESS_EVERY == 0:
                self.stdout.write(
                    f"  Progress: {mms_count} in this chapter, " f"{len(queue)} in queue."
                )
                if sync_log is not None:
                    sync_log.mms_count = already_processed + mms_count
                    sync_log.save(update_fields=["mms_count"])

            if max_entities is not None and already_processed + mms_count >= max_entities:
                break

        # Final flush
        if mms_buffer:
            self._flush_mms(mms_buffer, dry_run=dry_run)

        self.stdout.write(
            self.style.SUCCESS(f"  Chapter {chapter_code}: {mms_count} MMS entities.")
        )

        return mms_count, foundation_uris

    def _flush_mms(self, buffer: list[dict[str, Any]], *, dry_run: bool) -> None:
        """Write a batch of MMS entities to the database."""
        if dry_run or not buffer:
            return
        with transaction.atomic():
            for data in buffer:
                MmsEntity.objects.update_or_create(
                    uri=data["uri"],
                    defaults=data,
                )

    def _sync_foundation(
        self,
        *,
        client: IcdApiClient,
        foundation_uris: set[str],
        dry_run: bool,
    ) -> int:
        """Fetch and save foundation entities by their URIs."""
        if not foundation_uris:
            return 0

        self.stdout.write(f"Syncing {len(foundation_uris)} foundation entities...")

        count = 0
        for foundation_uri in foundation_uris:
            entity_id = foundation_uri.rsplit("/", 1)[-1]
            try:
                entity = client.get_foundation_entity(entity_id)
            except IcdApiNotFoundError:
                logger.warning("Foundation entity not found: %s", foundation_uri)
                continue
            except IcdApiError as exc:
                logger.error("Error fetching %s: %s", foundation_uri, exc)
                continue

            data = {
                "uri": foundation_uri,
                "title": client.extract_title(entity),
                "definition": self._extract_lang_value(entity.get("definition")),
                "long_definition": self._extract_lang_value(entity.get("longDefinition")),
                "synonyms": client.extract_synonyms(entity),
                "parent_uris": entity.get("parent", []) or [],
                "child_uris": entity.get("child", []) or [],
                "exclusions": self._normalize_exclusions(entity.get("exclusion", [])),
                "browser_url": entity.get("browserUrl", "") or "",
                "chapter": "",
                "last_synced_at": timezone.now(),
            }

            if not dry_run:
                FoundationEntity.objects.update_or_create(
                    uri=foundation_uri,
                    defaults=data,
                )

            count += 1

            if count % PROGRESS_EVERY == 0:
                self.stdout.write(f"  Foundation progress: {count}/{len(foundation_uris)}.")

        return count

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_lang_value(value: Any) -> str:
        """Extract @value from {'@value': '...', '@language': 'en'}."""
        if isinstance(value, dict):
            return value.get("@value", "") or ""
        if isinstance(value, str):
            return value
        return ""

    @staticmethod
    def _normalize_exclusions(value: Any) -> list[dict[str, str]]:
        """Normalize the exclusion list from foundation entities."""
        if not isinstance(value, list):
            return []
        result: list[dict[str, str]] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            label = item.get("label", {})
            if isinstance(label, dict):
                label_text = label.get("@value", "") or ""
            elif isinstance(label, str):
                label_text = label
            else:
                label_text = ""
            result.append(
                {
                    "label": label_text,
                    "foundation_reference": item.get("foundationReference", ""),
                    "linearization_reference": item.get("linearizationReference", ""),
                }
            )
        return result
