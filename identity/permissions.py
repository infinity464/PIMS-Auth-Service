from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from identity.models import User
from identity.rbac import get_role_permissions


class AuthRBACPermission(BasePermission):

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise PermissionDenied("Authorization header missing or invalid")

        token = auth_header.split(" ", 1)[1]

        try:
            access = AccessToken(token)
            user = User.objects.get(id=access["user_id"])
        except Exception:
            raise PermissionDenied("Invalid or expired token")

        permissions = get_role_permissions(user.role)

        required_permission = getattr(view, "required_permission", None)
        if required_permission and required_permission not in permissions:
            raise PermissionDenied("You do not have permission")

        request.user_data = {
            "id": user.id,
            "role": user.role,
            "permissions": permissions,
        }

        return True
