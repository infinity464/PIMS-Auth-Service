from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .constant import Roles

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(db_column='Id', primary_key=True)
    username = models.CharField(db_column='Username', max_length=255, unique=True)
    email = models.CharField(db_column='Email', max_length=255)
    password = models.CharField(db_column='PasswordHash', max_length=500)

    role = models.CharField(
    db_column='Role',
    max_length=50
)


    is_superuser = models.BooleanField(db_column='IsSuperUser', default=False)
    last_login = models.DateTimeField(db_column='LastLogin', null=True)

    created_at = models.DateTimeField(db_column='CreatedAt')
    updated_at = models.DateTimeField(db_column='UpdatedAt')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'Users'
        managed = False




class RefreshToken(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    user_id = models.IntegerField(db_column='UserId')
    token = models.CharField(db_column='Token', max_length=500)
    expires_at = models.DateTimeField(db_column='ExpiresAt')
    created_at = models.DateTimeField(db_column='CreatedAt')

    class Meta:
        db_table = 'RefreshTokens'
        managed = False 
class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True) 
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "Permissions"
class RolePermission(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50) 
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = "RolePermissions"
        unique_together = ("role", "permission")
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Roles"

    def __str__(self):
        return self.name

class Module(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    module_key = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "Modules"
        managed = False


class RoleFeature(models.Model):
    id = models.AutoField(primary_key=True)

    role = models.CharField(max_length=50)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    feature_name = models.CharField(max_length=100)
    feature_key = models.CharField(max_length=100)

    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_report = models.BooleanField(default=False)

    class Meta:
        db_table = "RoleFeatures"
        unique_together = ("role", "feature_key")
        managed = False

