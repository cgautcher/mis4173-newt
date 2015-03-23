from django import forms
from django.contrib.auth.models import Group, User

from models import EnablementRequest, ConfigurationDetails, Comment


class InitiateEnablementRequestForm(forms.Form):
    customer_name = forms.CharField(label='Customer Name')

class UpdateEnablementRequestForm(forms.ModelForm):
    customer_name = forms.CharField(label='Customer Name')
    current_state = forms.ChoiceField(label='Current State', choices=EnablementRequest.ALLOWED_STATES)
    parent_request = forms.CharField(label='Parent Request', required=False)

    ENABLEMENT_ENGINEERS = tuple(Group.objects.get(name='Enablement').user_set.values_list('id', 'username'))
    assigned_engineer = forms.ChoiceField(label='Assigned Engineer', choices=ENABLEMENT_ENGINEERS)

    class Meta:
        model = EnablementRequest
        fields = (
            "customer_name",
            "current_state",
            "parent_request",
            "assigned_engineer",
        )

    def clean(self):
        #run the standard clean method first
        cleaned_data=super(UpdateEnablementRequestForm, self).clean()

        assigned_engineer_id = cleaned_data['assigned_engineer']
        assigned_engineer_instance = User.objects.get(id=assigned_engineer_id)
        cleaned_data['assigned_engineer'] = assigned_engineer_instance

        parent_request = cleaned_data['parent_request']
        if parent_request:
            parent_request_instance = EnablementRequest.objects.get(identifier=parent_request)
            cleaned_data['parent_request'] = parent_request_instance
        else:
            del cleaned_data['parent_request']

        #always return the cleaned data
        return cleaned_data


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


