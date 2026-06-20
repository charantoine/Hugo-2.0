"""Serializers for accounts."""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from app_core.tenant_context import home_organisation_id, tenant_organisation_id
from apps.referentials.access_control import is_superadmin

from .models import Organisation, User, Role


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserMeSerializer(serializers.ModelSerializer):
    organisation_id = serializers.UUIDField(source="organisation.id", read_only=True)
    organisation_name = serializers.CharField(source="organisation.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "organisation_id",
            "organisation_name",
            "created_at",
        ]


class OrganisationSerializer(serializers.ModelSerializer):
    def validate_default_learner_display_profile(self, value):
        allowed = {"youth", "adult", "professional"}
        normalized = str(value or "professional").strip().lower()
        if normalized not in allowed:
            raise serializers.ValidationError("Must be one of: youth, adult, professional.")
        return normalized

    class Meta:
        model = Organisation
        fields = ["id", "name", "default_learner_display_profile", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "organisation", "role", "first_name", "last_name"]
        read_only_fields = ["id"]
        extra_kwargs = {"organisation": {"required": True}}

    def validate_role(self, value):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) == Role.ORGADMIN and value not in {Role.LEARNER, Role.TUTOR}:
            raise serializers.ValidationError("ORGADMIN can only create learner or tutor accounts.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        org = attrs.get("organisation")
        if not request or org is None:
            return attrs
        org_id = getattr(org, "id", org)
        effective_id = tenant_organisation_id(request)
        if is_superadmin(request.user):
            if effective_id and str(org_id) != str(effective_id):
                raise serializers.ValidationError(
                    {"organisation": "User must be created in the active tenant organisation."}
                )
        elif str(org_id) != str(home_organisation_id(request)):
            raise serializers.ValidationError(
                {"organisation": "Cannot assign user to another organisation."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "is_active", "created_at"]


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "is_active"]

    def validate_role(self, value):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) == Role.ORGADMIN and value not in {Role.LEARNER, Role.TUTOR}:
            raise serializers.ValidationError("ORGADMIN can only manage learner or tutor accounts here.")
        return value

    def validate(self, attrs):
        if "organisation" in attrs:
            raise serializers.ValidationError(
                {"organisation": "Transferring users between organisations is forbidden."}
            )
        return attrs
