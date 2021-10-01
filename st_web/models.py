from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.db import models


class ShareLink(models.Model):
    expiration_date = models.DateTimeField(default=None, blank=True, null=True)
    resource_path = models.CharField(max_length=1028, blank=False, null=False)
    short_code = models.CharField(max_length=36, blank=True, null=True, unique=True)
    visit_limit = models.IntegerField(default=None, blank=True, null=True)


class User(AbstractUser):
    pass
