from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

# Create your models here.


class EnablementRequest(models.Model):
    identifier = models.CharField(max_length=9, unique=True, blank=True)
    parent_request = models.ForeignKey('self', to_field='identifier', null=True, blank=True)    
    slug = models.SlugField(max_length=9, unique=True, blank=True)
    customer_name = models.CharField(max_length=100)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    configuration_details = models.ForeignKey('ConfigurationDetails', null=True)

    sales_initiator = models.ForeignKey(User, null=True,
        limit_choices_to= Q( groups__name = 'Sales'), related_name='sales_representative')

    assigned_engineer = models.ForeignKey(User, null=True, blank=True, unique=False,
        limit_choices_to= Q( groups__name = 'Enablement'), related_name='enablement_engineer')

    ALLOWED_STATES = (
        ('Enablement Review', 'Enablement Review'),
        ('Sales Review', 'Sales Review'),
        ('Engineering Review', 'Engineering Review'),
        ('Support Review', 'Support Review'),
        ('Accepted In-progress', 'Accepted In-progress'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    )

    current_state = models.CharField(max_length=32, choices=ALLOWED_STATES)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('view', kwargs={'slug': self.slug})


class ConfigurationDetails(models.Model):

    # need to figure out how to how to NOT save new instance of this class
    #  when the details are identical to an existing record
    #  and instead have EnablementRequest reference the existing ConfigurationDetails record 

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

    pre_comment_state = models.CharField(max_length=3, choices=ALLOWED_STATES, null=True, blank=True)
    post_comment_state = models.CharField(max_length=3, choices=ALLOWED_STATES, null=True, blank=True)
