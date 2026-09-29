"""Seed diagnostic departments and methods for an organization.

Usage:
    python manage.py seed_diagnostic_departments --organization-id=1
    python manage.py seed_diagnostic_departments --organization-id=1 --truncate

This command is idempotent: it uses update_or_create by (organization, name)
for departments and (department, name) for methods.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Organization
from apps.referrals.models import DiagnosticDepartment, DiagnosticMethod

# ---------------------------------------------------------------------------
# Seed data: departments → methods
# ---------------------------------------------------------------------------

SEED_DATA: list[dict] = [
    {
        "name": "Day hospital #1",
        "category": DiagnosticDepartment.Category.SURGERY,
        "methods": [
            {"code": "", "name": "Excision of breast neoplasm"},
            {
                "code": "",
                "name": "Wound dressing for skin integrity violation",
            },
            {"code": "", "name": "Removal of benign skin neoplasms"},
            {
                "code": "",
                "name": "Removal of benign skin neoplasms by electrocoagulation",
            },
        ],
    },
    {
        "name": "Cytology laboratory",
        "category": DiagnosticDepartment.Category.PATHOLOGY,
        "methods": [
            {"code": "", "name": "Cytological specimen examination"},
        ],
    },
    {
        "name": "Clinical laboratory",
        "category": DiagnosticDepartment.Category.LABORATORY,
        "methods": [
            {"code": "CBC-cito", "name": "Complete blood count (cito)"},
            {"code": "CBC-ven", "name": "Complete blood count (venous)"},
            {"code": "CBC-ret", "name": "Complete blood count (reticulocytes)"},
            {"code": "UA", "name": "Urinalysis"},
            {
                "code": "BIO",
                "name": "Blood test (general therapeutic biochemistry)",
            },
            {
                "code": "HORM",
                "name": "Blood test (hormones and tumor markers)",
            },
            {"code": "NECH", "name": "Urinalysis (Nechiporenko method)"},
            {"code": "GLU", "name": "Blood test (glucose)"},
            {"code": "HBA1C", "name": "Blood test (glycated hemoglobin)"},
            {"code": "PLT", "name": "Blood test (platelets in chamber)"},
            {"code": "COAG", "name": "Coagulogram"},
            {"code": "SYPH", "name": "Virus detection (syphilis)"},
            {"code": "HIV", "name": "Virus detection (HIV)"},
            {"code": "HEP", "name": "Virus detection (hepatitis B, C)"},
        ],
    },
    {
        "name": "Molecular diagnostics laboratory",
        "category": DiagnosticDepartment.Category.MOLECULAR,
        "methods": [
            {
                "code": "C-KIT",
                "name": "C-KIT gene mutations in biopsy material",
            },
            {"code": "BRAF", "name": "BRAF gene mutations in biopsy material"},
            {"code": "EGFR", "name": "EGFR gene mutations in biopsy material"},
            {"code": "KRAS", "name": "KRAS gene mutations in biopsy material"},
            {"code": "NRAS", "name": "NRAS gene mutations in biopsy material"},
            {
                "code": "PIK3CA",
                "name": "PIK3CA gene mutations in biopsy material",
            },
            {
                "code": "BRCA",
                "name": "BRCA1 and BRCA2 gene mutations in blood",
            },
            {"code": "GENE", "name": "Gene mutations in biopsy material"},
            {
                "code": "JAK2",
                "name": "V617F mutations in JAK2 gene in blood, quantitative",
            },
            {"code": "HPV", "name": "HPV DNA and type determination (HRC)"},
            {"code": "COV", "name": "Virus detection (coronavirus RNA)"},
            {"code": "HIV", "name": "Virus detection (HIV)"},
            {"code": "HEP", "name": "Virus detection (hepatitis B, C)"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed diagnostic departments and methods for an organization."

    def add_arguments(self, parser):
        parser.add_argument(
            "--organization-id",
            type=int,
            required=True,
            help="ID of the organization to seed data for",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete existing departments and methods first",
        )

    def handle(self, *args, **options):
        org_id: int = options["organization_id"]

        try:
            organization = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            raise CommandError(f"Organization with id={org_id} does not exist.") from None

        if options["truncate"]:
            dept_count = DiagnosticDepartment.objects.filter(organization=organization).count()
            DiagnosticDepartment.objects.filter(organization=organization).delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {dept_count} existing departments "
                    f"(and their methods) for {organization.name}."
                )
            )

        created_depts = 0
        updated_depts = 0
        created_methods = 0
        updated_methods = 0

        for dept_data in SEED_DATA:
            dept, dept_created = DiagnosticDepartment.objects.update_or_create(
                organization=organization,
                name=dept_data["name"],
                defaults={
                    "category": dept_data["category"],
                    "is_active": True,
                },
            )
            if dept_created:
                created_depts += 1
            else:
                updated_depts += 1

            for method_data in dept_data["methods"]:
                _, method_created = DiagnosticMethod.objects.update_or_create(
                    department=dept,
                    name=method_data["name"],
                    defaults={
                        "code": method_data.get("code", ""),
                        "is_active": True,
                    },
                )
                if method_created:
                    created_methods += 1
                else:
                    updated_methods += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete for {organization.name}: "
                f"{created_depts} created / {updated_depts} updated departments, "
                f"{created_methods} created / {updated_methods} updated methods."
            )
        )
