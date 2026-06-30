"""Auth views: login (JWT), me."""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import LoginSerializer, UserMeSerializer


class LoginView(generics.GenericAPIView):
    """POST /auth/login — returns access + refresh tokens."""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": str(user.id),
            "organisation_id": str(user.organisation_id),
            "role": user.role,
        })


class MeView(generics.GenericAPIView):
    """GET /auth/me — current user profile (org + roles)."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserMeSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
