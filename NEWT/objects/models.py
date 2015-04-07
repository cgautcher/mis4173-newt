from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

# Create your models here.


class EnablementRequest(models.Model):
    # things that will be entered as input from the users
    customer_name = models.CharField(max_length=100)
    short_term_revenue = models.IntegerField(default='0')
    parent_request = models.CharField(max_length=9, null=True, blank=True)    
    
    assigned_engineer = models.ForeignKey(User, null=True, blank=True, unique=False,
        limit_choices_to= Q( groups__name = 'Enablement'), related_name='enablement_engineer')

    ALLOWED_STATES = (
        ('Enablement Review', 'Enablement Review'),
        ('Sales Review', 'Sales Review'),
        ('Engineering Review', 'Engineering Review'),
        ('Support Review', 'Support Review'),
        ('Accepted - In Progress', 'Accepted - In Progress'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    )

    current_state = models.CharField(max_length=32, choices=ALLOWED_STATES)


    # this should be updated if the current_state changes to "Completed"
    completion_timestamp = models.DateTimeField(blank=True, null=True)

    # Things that get set automatically
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    config_details = models.ForeignKey('ConfigDetails', null=True)

    sales_initiator = models.ForeignKey(User, null=True,
        limit_choices_to= Q( groups__name = 'Sales'), related_name='sales_representative')

    identifier = models.CharField(max_length=9, unique=True, blank=True)
    slug = models.SlugField(max_length=9, unique=True, blank=True)


    # return the view path to the object.
    # + example: "/view/er-000123"
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('view', kwargs={'slug': self.slug})

    # return the update path to the object.
    # + example: "/update/er-000123"
    def get_update_url(self):
        from django.core.urlresolvers import reverse
        return reverse('update', kwargs={'slug': self.slug})

    

class ConfigDetails(models.Model):

    OS_TYPES = (
        ('Windows Server', 'Windows Server'),
        ('Hyper-V Server', 'Hyper-V Server'),
        ('Linux - Redhat', 'Linux - Redhat'),
        ('Linux - SuSE', 'Linux - SuSE'),
        ('Linux - Oracle', 'Linux - Oracle'),
        ('Oracle VM', 'Oracle VM'),
        ('VMware vSphere', 'VMware vSphere'),
        ('Solaris', 'Solaris'),
        ('AIX', 'AIX'),
        ('HP-UX', 'HP-UX'),
    )

    os_type = models.CharField(max_length=32, choices=OS_TYPES)    
    os_version = models.CharField(max_length=32)

    STORAGE_ADAPTER_VENDORS = (
        ('Cisco', 'Cisco'),
        ('Brocade', 'Brocade'),
        ('QLogic', 'QLogic'),
        ('Emulex', 'Emulex'),
        ('Broadcom', 'Broadcom'),
        ('Intel', 'Intel'),
    )

    storage_adapter_vendor = models.CharField(max_length=32, choices=STORAGE_ADAPTER_VENDORS)
    storage_adapter_model = models.CharField(max_length=32)
    storage_adapter_driver = models.CharField(max_length=32)
    storage_adapter_firmware = models.CharField(max_length=32)
    data_ontap_version = models.CharField(max_length=32)


class Comment(models.Model):
    enablement_request = models.ForeignKey('EnablementRequest')
    commenter = models.ForeignKey(User)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    ALLOWED_STATES = (
        ('Enablement Review', 'Enablement Review'),
        ('Sales Review', 'Sales Review'),
        ('Engineering Review', 'Engineering Review'),
        ('Support Review', 'Support Review'),
        ('Accepted In-progress', 'Accepted In-progress'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    )

    pre_comment_state = models.CharField(max_length=32, choices=ALLOWED_STATES, null=True, blank=True)
    post_comment_state = models.CharField(max_length=32, choices=ALLOWED_STATES, null=True, blank=True)
