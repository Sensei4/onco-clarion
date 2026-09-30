"""Serializers for the admission queue endpoint.

The admission queue returns a flat list of cases ready for admission,
enriched with patient data, waiting context, and last consilium info.
"""

from rest_framework import serializers


class AdmissionQueueItemSerializer(serializers.Serializer):
    """Read-only serializer for a single admission queue item.

    Not a ModelSerializer — we compose data from multiple models.
    """

    # Case
    id = serializers.IntegerField()
    diagnosis_code = serializers.CharField()
    diagnosis_text = serializers.CharField()
    stage = serializers.CharField()
    tnm_t = serializers.CharField()
    tnm_n = serializers.CharField()
    tnm_m = serializers.CharField()

    # Patient
    patient = serializers.IntegerField()
    patient_name = serializers.CharField()
    patient_mrn = serializers.CharField()
    patient_birth_date = serializers.DateField()
    patient_age = serializers.IntegerField(allow_null=True)
    patient_sex = serializers.CharField()
    patient_insurance_policy_number = serializers.CharField()

    # Queue context
    waiting_since = serializers.DateTimeField(allow_null=True)
    waiting_days = serializers.IntegerField(allow_null=True)

    # Last consilium
    last_consilium_date = serializers.DateTimeField(allow_null=True)
    last_consilium_decision = serializers.CharField(allow_blank=True)
    last_consilium_recommended_plan = serializers.CharField(allow_blank=True)
