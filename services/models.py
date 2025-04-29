from django.db import models
from django.utils import timezone

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
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'db_server'

        ordering = ['name']


class UserServers(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'db_user_servers'


class Workflow(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    content = models.JSONField(null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'db_workflow'
        ordering = ['-created']

    @property
    def executions(self):
        # This is a property that returns the number of executions related to this workflow.
        return Execution.objects.filter(workflow=self).count()


class Execution(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=100, blank=False, null=False)
    result = models.JSONField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'db_execution'
        ordering = ['-created']


class Task(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    uuid = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    outputs = models.JSONField(null=True)
    execution = models.ForeignKey(
        Execution, on_delete=models.CASCADE, null=True)
    workflow = models.ForeignKey(
        Workflow, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    started = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, blank=False, null=True)

    class Meta:
        db_table = 'db_task'
        ordering = ['-started']
