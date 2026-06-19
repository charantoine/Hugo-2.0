from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import TutorPrompt
from .serializers import TutorPromptSerializer


class TutorPromptList(generics.ListAPIView):
    """
    List active TutorPrompts for the current organisation.
    Optional ?prompt_type=AFEST_HUGO filter.
    """

    serializer_class = TutorPromptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = TutorPrompt.objects.filter(
            organisation_id=self.request.user.organisation_id,
            is_active=True,
        )
        prompt_type = self.request.query_params.get("prompt_type")
        if prompt_type:
            qs = qs.filter(prompt_type=prompt_type)
        return qs

