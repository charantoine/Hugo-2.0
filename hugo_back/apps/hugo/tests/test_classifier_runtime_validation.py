from django.test import SimpleTestCase
from rest_framework import serializers

from apps.hugo.serializers import SessionClassifierConfigSerializer
from apps.referentials.serializers import GroupSerializer


class ClassifierRuntimeValidationTests(SimpleTestCase):
    def test_session_classifier_config_serializer_rejects_out_of_bounds_confidence(self):
        serializer = SessionClassifierConfigSerializer(
            data={"phase_classifier_min_confidence": 1.2},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("phase_classifier_min_confidence", serializer.errors)

    def test_session_classifier_config_serializer_rejects_non_positive_tokens(self):
        serializer = SessionClassifierConfigSerializer(
            data={"phase_classifier_max_tokens": 0},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("phase_classifier_max_tokens", serializer.errors)

    def test_session_classifier_config_serializer_accepts_nulls_for_fallback(self):
        serializer = SessionClassifierConfigSerializer(
            data={
                "phase_classifier_enabled": None,
                "phase_classifier_max_tokens": None,
                "phase_classifier_min_confidence": None,
                "phase_classifier_max_input_chars": None,
            },
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_group_serializer_validates_positive_max_input_chars(self):
        serializer = GroupSerializer()
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_phase_classifier_max_input_chars(0)
