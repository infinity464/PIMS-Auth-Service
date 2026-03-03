from identity.constant import Roles
from identity.models import Role
from rest_framework import serializers
   

class UpdateUserRoleSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    role = serializers.CharField(max_length=50)

    def validate_role(self, value):
        if not Role.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid role")
        return value



class RegisterSerializer(serializers.Serializer):
    userName = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)


class LoginSerializer(serializers.Serializer):
    userName = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "is_active"]


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UpdateUserEmailSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    email = serializers.EmailField()
