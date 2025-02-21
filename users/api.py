from django.contrib.auth.hashers import make_password
from rest_framework import generics, serializers, status, permissions
from rest_framework.response import Response

from .models import User


class UserRegistratrionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
        ]

    def validate(self, attrs: dict) -> dict:
        """Change the password for its hash to make token validation available"""

        attrs["password"] = make_password(attrs["password"])

        return attrs


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "role"]


# /users: GET POST
class UserCreateRetrieveAPI(generics.ListCreateAPIView):
    http_method_names = ["get", "post"]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistratrionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            UserPublicSerializer(serializer.validated_data).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get(self, request):
        user = request.user
        serializer = UserPublicSerializer(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.data),
        )
