from django.db import models

from django.contrib.auth.models import User



class AccountRegistration(models.Model):

    user = models.OneToOneField(User)

    GROUP_STATUS_CHOICES = (
        ('GENERIC','Generic user (no special permissions needed)'),
        ('SALES','Sales user (Can create/comment on Enablement Requests)'),
        ('ENGSUP','Engineering/Support user (Can comment on Enablement Requests)'),
    )

    group_status = models.CharField(max_length=32, choices=GROUP_STATUS_CHOICES, default='GENERIC')

