from datetime import datetime

from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from drf_yasg.utils import swagger_auto_schema

from identity.permissions import AuthRBACPermission, RoleListOrManagePermission
from identity.rbac import get_role_permissions
from .models import Role, User, RefreshToken as RefreshTokenModel
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    RoleSerializer,
    VerifyTokenSerializer,
    UpdateUserRoleSerializer,
    UpdateUserEmailSerializer,
)
from identity.utils import get_role_permissions

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="Account_Register",
        tags=["Account"],
        request_body=RegisterSerializer,
        responses={201: "Registration successful"},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if User.objects.filter(username=data["userName"]).exists():
            return Response(
                {"message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"message": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(
            username=data["userName"],
            email=data["email"],
            password=make_password(data["password"]),
            role="User",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return Response(
            {"message": "Registration successful", "userId": user.id},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="Account_Login",
        tags=["Account"],
        request_body=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        userName = serializer.validated_data["userName"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(username=userName)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, user.password):
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        RefreshTokenModel.objects.create(
            user_id=user.id,
            token=str(refresh),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + refresh.lifetime,
        )

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "userName": user.username,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )



class VerifyTokenView(APIView):

    def post(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing")

        token = auth_header.split(" ")[1]

        try:
            access = AccessToken(token)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        role = access.get("role")

        permissions = get_role_permissions(role)

        return Response({
            "user_id": access.get("user_id"),
            "role": role,
            "permissions": permissions,
        })


class UpdateUserRoleView(APIView):
    permission_classes = [AuthRBACPermission]
    required_permission = "user.role.update"

    @swagger_auto_schema(
        operation_id="Account_updateUserRole",
        tags=["Account"],
        request_body=UpdateUserRoleSerializer,
        responses={
            200: "Role updated successfully",
            403: "Permission denied",
            404: "User not found",
        },
    )
    def post(self, request):
        serializer = UpdateUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=serializer.validated_data["userId"])
        user.role = serializer.validated_data["role"]
        user.save(update_fields=["role"])

        return Response(
            {
                "message": "Role updated successfully",
                "userId": user.id,
                "newRole": user.role,
            },
            status=status.HTTP_200_OK,
        )


class UpdateUserEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="Account_updateUserEmail",
        tags=["Account"],
        request_body=UpdateUserEmailSerializer,
        responses={200: "Email updated", 404: "User not found"},
    )
    def post(self, request):
        serializer = UpdateUserEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["userId"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.email = email
        user.save(update_fields=["email"])
        return Response(
            {"message": "Email updated successfully", "userId": user.id, "email": user.email},
            status=status.HTTP_200_OK,
        )


class RoleView(APIView):
    permission_classes = [RoleListOrManagePermission]

    @swagger_auto_schema(
        operation_id="roles_list",
        tags=["Roles"],
        responses={200: RoleSerializer(many=True)}
    )
    def get(self, request, role_id=None):
        if role_id is not None:
            try:
                role = Role.objects.get(id=role_id)
                serializer = RoleSerializer(role)
                return Response(serializer.data)
            except Role.DoesNotExist:
                return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.all().order_by('id')
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id="roles_create",
        tags=["Roles"],
        request_body=RoleSerializer,
        responses={201: "Role created successfully"}
    )
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Role created successfully"},
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_id="roles_update",
        tags=["Roles"],
        request_body=RoleSerializer,
        responses={200: "Role updated", 404: "Role not found"},
    )
    def patch(self, request, role_id: int):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="roles_delete",
        tags=["Roles"],
        responses={
            200: "Role deleted successfully",
            404: "Role not found"
        }
    )
    def delete(self, request, role_id: int):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {"message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        role.is_active = False
        role.save(update_fields=["is_active"])

        return Response(
            {"message": "Role deleted successfully"},
            status=status.HTTP_200_OK
        )
