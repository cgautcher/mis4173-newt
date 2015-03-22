from django import forms
from django.contrib.auth.models import Group

from models import EnablementRequest, ConfigurationDetails, Comment


class InitiateEnablementRequestForm(forms.Form):
    customer_name = forms.CharField(label='Customer Name')

class UpdateEnablementRequestForm(forms.ModelForm):
    customer_name = forms.CharField(label='Customer Name')
    current_state = forms.ChoiceField(label='Current State', choices=EnablementRequest.ALLOWED_STATES)
    parent_request = forms.CharField(label='Parent Request')

    ENABLEMENT_USERS = tuple(Group.objects.get(name='Enablement').user_set.values_list('id','username'))
    assigned_engineer = forms.ChoiceField(label='Assigned Engineer', choices=ENABLEMENT_USERS)

    class Meta:
        model = EnablementRequest
        fields = (
            "customer_name",
            "current_state",
            "parent_request",
            "assigned_engineer",
        )
    

class ConfigurationDetailsForm(forms.ModelForm):
    os_type = forms.ChoiceField(label='OS Type', choices=ConfigurationDetails.OS_TYPES)
    os_version = forms.CharField(label='OS Version')
    storage_adapter_vendor = forms.ChoiceField(label='Storage Adapter Vendor', choices=ConfigurationDetails.STORAGE_ADAPTER_VENDORS)
    storage_adapter_model = forms.CharField(label='Storage Adapter Model')
    storage_adapter_driver = forms.CharField(label='Storage Adapter Driver')
    storage_adapter_firmware = forms.CharField(label='Storage Adapter Firmware')
    data_ontap_version = forms.CharField(label='Data ONTAP Version')

    class Meta:
        model = ConfigurationDetails
        fields = (
            "os_type",
            "os_version",
            "storage_adapter_vendor",
            "storage_adapter_model",
            "storage_adapter_driver",
            "storage_adapter_firmware",
            "data_ontap_version",
        )


class CommentForm(forms.ModelForm):
    text = forms.CharField(label="", widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ("text",)

    def save(self, commit=True, enablement_request=None, commenter=None):
        if commit:
            comment = Comment(
                enablement_request=enablement_request,
                commenter=commenter,
                text=self.cleaned_data['text']
            )
            comment.save()


