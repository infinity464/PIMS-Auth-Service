# models.py
from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    username = models.CharField(max_length=150, db_column='Username')
    email = models.EmailField(max_length=255, db_column='Email')
    role = models.CharField(max_length=50, db_column='Role')
    is_superuser = models.BooleanField(db_column='IsSuperUser')
    last_login = models.DateTimeField(null=True, blank=True, db_column='LastLogin')

    class Meta:
        db_table = 'Users'
        managed = False
