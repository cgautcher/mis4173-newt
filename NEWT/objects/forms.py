from django import forms
from django.contrib.auth.models import Group, User
from django.db.models.base import ObjectDoesNotExist

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

    # override save() in order to return existing instance if no changes during UpdateEnablementRequestForm,
    # + or if a new ER has the exact same configuration, use existing instance 
    def save(self, commit=True):
        if commit:
            cleaned_data = self.cleaned_data
            os_type_value = cleaned_data['os_type']
            os_version_value = cleaned_data['os_version']
            storage_adapter_vendor_value = cleaned_data['storage_adapter_vendor']
            storage_adapter_model_value = cleaned_data['storage_adapter_model']
            storage_adapter_driver_value = cleaned_data['storage_adapter_driver']
            storage_adapter_firmware_value = cleaned_data['storage_adapter_firmware']
            data_ontap_version_value = cleaned_data['data_ontap_version']

            # check database to see if this instance already exists,
            # + if not, it will raise an exception, which we will catch,
            # + and it will add the new instance instead of erroring out
            try:
                instance = ConfigurationDetails.objects.get(os_type=os_type_value,
                                                            os_version=os_version_value,
                                                            storage_adapter_vendor=storage_adapter_vendor_value,
                                                            storage_adapter_model=storage_adapter_model_value,
                                                            storage_adapter_driver=storage_adapter_driver_value,
                                                            storage_adapter_firmware=storage_adapter_firmware_value,
                                                            data_ontap_version=data_ontap_version_value)
            except ObjectDoesNotExist: 
                configuration_details = ConfigurationDetails(os_type=os_type_value,
                                                             os_version=os_version_value,
                                                             storage_adapter_vendor=storage_adapter_vendor_value,
                                                             storage_adapter_model=storage_adapter_model_value,
                                                             storage_adapter_driver=storage_adapter_driver_value,
                                                             storage_adapter_firmware=storage_adapter_firmware_value,
                                                             data_ontap_version=data_ontap_version_value)
                configuration_details.save()
                return configuration_details


            # if the exception above did not get raised, return instance
            return instance
                

class CommentForm(forms.ModelForm):
    text = forms.CharField(label="", widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ("text",)

    def save(self, commit=True, enablement_request=None, commenter=None,
             pre_comment_state=None, post_comment_state=None):

        if commit:
            comment = Comment(enablement_request=enablement_request,
                              commenter=commenter,
                              text=self.cleaned_data['text'])
            if pre_comment_state and post_comment_state:
                comment.pre_comment_state = pre_comment_state
                comment.post_comment_state = post_comment_state
            comment.save()


class RequestFeedbackForm(CommentForm):
    STATE_CHANGE_CHOICES = (
        ('', 'n/a'),
        ('Sales Review', 'Sales Review'),
        ('Engineering Review', 'Engineering Review'),
        ('Support Review', 'Support Review'),
    )
    commenters_choice = forms.ChoiceField(label='Change "Current State"?', choices=STATE_CHANGE_CHOICES, required=False, help_text='(Optional)')

    class Meta:
        model = Comment
        fields = ("commenters_choice", "text",)


class ProvideFeedbackForm(RequestFeedbackForm):
    STATE_CHANGE_CHOICES = (
        ('', 'n/a'), 
        ('Enablement Review', 'Enablement Review'),
    )
    commenters_choice = forms.ChoiceField(label='Change "Current State"?', choices=STATE_CHANGE_CHOICES, required=False, help_text='(Optional)')

