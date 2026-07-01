"""REST API — profils conversationnels persona (tuteur / formateur)."""
from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_core.tenant_context import tenant_organisation_id
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from apps.hugo.models import PersonaConversationProfile, TutorPrompt
from apps.hugo.serializers import PersonaConversationProfileSerializer
from apps.hugo.services.context_builder import HugoContext
from apps.hugo.services.persona_session import build_persona_context_block
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt


class PersonaConversationProfileListCreate(generics.ListCreateAPIView):
    serializer_class = PersonaConversationProfileSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        qs = PersonaConversationProfile.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
        ).select_related("tutor_prompt").order_by("persona", "name")
        persona = str(self.request.query_params.get("persona") or "").strip().lower()
        if persona in {PersonaConversationProfile.Persona.TUTOR, PersonaConversationProfile.Persona.TRAINER}:
            qs = qs.filter(persona=persona)
        return qs

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))


class PersonaConversationProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonaConversationProfileSerializer
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return PersonaConversationProfile.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
        ).select_related("tutor_prompt")


class PersonaConversationProfilePreviewView(APIView):
    """POST preview rendu template sans appel LLM."""

    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def post(self, request, id):
        profile = get_object_or_404(
            PersonaConversationProfile.objects.select_related("tutor_prompt"),
            id=id,
            organisation_id=tenant_organisation_id(request),
        )
        prompt = profile.tutor_prompt
        system_override = request.data.get("system_template")
        user_override = request.data.get("user_template")
        sample_content = str(request.data.get("sample_content") or "Message d'exemple pour prévisualisation.")

        preview_prompt = TutorPrompt(
            organisation_id=profile.organisation_id,
            code=prompt.code,
            name=prompt.name,
            system_template=str(system_override or prompt.system_template),
            user_template=str(user_override or prompt.user_template),
            persona_scope=prompt.persona_scope,
            is_active=True,
        )

        session_stub = type(
            "PreviewSession",
            (),
            {
                "id": profile.id,
                "organisation_id": profile.organisation_id,
                "learner": request.user,
                "group": None,
                "persona_conversation_profile": profile,
                "learner_conversation_profile": None,
                "messages": None,
            },
        )()

        ctx = HugoContext(
            referential_name="",
            referential_source_ref="",
            items_to_focus=[],
            items_already_covered=[],
            learner_summary="",
            recent_traces_info=[],
            class_documents=[],
        )

        rendered = render_with_tutor_prompt(
            preview_prompt,
            session_stub,
            ctx,
            sample_content,
        )
        persona_block = build_persona_context_block(session_stub, profile.persona)
        return Response(
            {
                "system_prompt": rendered.system_prompt,
                "user_prompt": rendered.user_prompt,
                "persona_context_block": persona_block,
                "available_variables": [
                    "situation_content",
                    "history_block",
                    "referential_block",
                    "persona_context_block",
                    "tutor_context_block",
                    "trainer_context_block",
                    "organisation_id",
                    "session_id",
                ],
            },
            status=status.HTTP_200_OK,
        )
