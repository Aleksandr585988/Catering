
from rest_framework import status, permissions, viewsets, routers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (UserRegistrationSerializer, UserPublicSerializer,
                          UserActivationSerializer, CustomTokenObtainPairSerializer)
from users.service import Activator


class UserAPIViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    # def get_serializer_class(self):
    #     return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.AllowAny()]
        elif self.action == None:
            return [permissions.AllowAny()]
        elif self.action == "activate":
            return [permissions.AllowAny()]
        else:
            raise NotImplementedError(f"Action {self.action} is not ready yet")

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # # functional approach
        # actional_key: uuid.UUID = service.create_activation_key(email=serializer.validated_data["email"])
        # service.set_user_activation_email(email=serializer.validated_data["email"]), activation_key=activation_key

        service = Activator(email=getattr(serializer.instance, "email"))
        activation_key = service.create_activation_key()
        service.save_activation_information(
            user_id=getattr(serializer.instance, "id"), activation_key=activation_key
        )
        service.send_user_activation_email(activation_key=activation_key)

        return Response(
            UserPublicSerializer(serializer.validated_data).data,
            status=status.HTTP_201_CREATED,
        )

    def list(self, request):
        return Response(
            UserPublicSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    @action(methods=["POST"], detail=False)
    def activate(self, request):
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = Activator()
        service.activate_user(activation_key=serializer.validated_data.get("key"))

        # serializer.validated_data
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


router = routers.DefaultRouter()
router.register(r"users", UserAPIViewSet, basename="user")
