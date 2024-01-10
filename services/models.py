from django.db import models
from account.models import User
# Create your models here.


class Server(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    provider = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=100, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    is_process = models.BooleanField(null=True, default=True)
    url = models.CharField(max_length=255, blank=False, null=False)

    enabled = models.BooleanField(default=True, null=True)

    class Meta:
        db_table = 'db_server'
