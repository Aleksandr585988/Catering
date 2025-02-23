from rest_framework import status, permissions, viewsets, routers
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserRegistratrionSerializer, UserPublicSerializer


class UserAPIViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserRegistratrionSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.AllowAny()]
        elif self.action == None:
            return [permissions.AllowAny()]
        else:
            raise NotImplementedError(f"Action {self.action} is not ready yet")

    def create(self, request):
        serializer = UserRegistratrionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            UserPublicSerializer(serializer.validated_data).data,
            status=status.HTTP_201_CREATED,
        )

    def list(self, request):
        return Response(
            UserPublicSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


router = routers.DefaultRouter()
router.register(r"users", UserAPIViewSet, basename="user")
