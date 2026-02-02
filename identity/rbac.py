from identity.models import RolePermission

def get_role_permissions(role_name: str) -> list[str]:
    return list(
        RolePermission.objects
        .filter(role=role_name)
        .select_related("permission")
        .values_list("permission__code", flat=True)
    )
