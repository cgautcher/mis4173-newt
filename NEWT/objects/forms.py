from django import forms

from django.contrib.auth.models import Group, User
from django.db.models.base import ObjectDoesNotExist

from models import EnablementRequest, ConfigDetails, Comment


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Reset, Row, Field, Fieldset


class InitiateForm(forms.Form):

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
        Fieldset('Customer Details',
            'customer_name',
            'short_term_revenue',
        ),
    )
    


    customer_name = forms.CharField(label='Customer Name')
    short_term_revenue = forms.IntegerField(label='Short Term Revenue')


class FilterForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
        Fieldset('Enablement Request Details',
            'customer_name',
            'short_term_revenue',
            'current_state',
        ),
        Fieldset('Configuration Details',
            'os_type',
            'os_version',
            'storage_adapter_vendor',
            'storage_adapter_model',
            'storage_adapter_driver',
            'storage_adapter_firmware',
            'data_ontap_version',
        ),
        Div(
               Reset('Reset The Form', 'Reset', css_class='btn btn-danger'),
               Submit('submit', 'Filter', css_class='btn btn-success'),
               css_class='col-lg-7 text-right',
           ),
    )


    customer_name = forms.CharField(label='Customer Name', required=False)
    short_term_revenue = forms.IntegerField(label='Short Term Revenue', initial=0)
    current_state_list = list(EnablementRequest.ALLOWED_STATES)
    current_state_list.insert(0, ('','----'))

    current_state = forms.ChoiceField(label='Current State', choices=current_state_list, required=False)

    os_type_list = list(ConfigDetails.OS_TYPES)
    os_type_list.insert(0, ('','----'))
    os_type = forms.ChoiceField(label='OS Type', choices=os_type_list, required=False)

    os_version = forms.CharField(label='OS Version', required=False)

    storage_adapter_vendor_list = list(ConfigDetails.STORAGE_ADAPTER_VENDORS)
    storage_adapter_vendor_list.insert(0, ('','----'))
    storage_adapter_vendor = forms.ChoiceField(label='Storage Adapter Vendor', choices=storage_adapter_vendor_list, required=False)

    storage_adapter_model = forms.CharField(label='Storage Adapter Model', required=False)
    storage_adapter_driver = forms.CharField(label='Storage Adapter Driver', required=False)
    storage_adapter_firmware = forms.CharField(label='Storage Adapter Firmware', required=False)
    data_ontap_version = forms.CharField(label='Data ONTAP Version', required=False)


class UpdateForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
        Fieldset('Enablement Request Details',
            'customer_name',
            'short_term_revenue',
            'current_state',
            'parent_request',
            'assigned_engineer',
        ),
    )
    

    customer_name = forms.CharField(label='Customer Name')
    short_term_revenue = forms.IntegerField(label='Short Term Revenue')
    current_state = forms.ChoiceField(label='Current State', choices=EnablementRequest.ALLOWED_STATES)
    parent_request = forms.CharField(label='Parent Request', required=False)

    ENABLEMENT_ENGINEERS = tuple(Group.objects.get(name='Enablement').user_set.values_list('id', 'username'))
    assigned_engineer = forms.ChoiceField(label='Assigned Engineer', choices=ENABLEMENT_ENGINEERS)

    class Meta:
        model = EnablementRequest
        fields = (
            "customer_name",
            "short_term_revenue",
            "current_state",
            "parent_request",
            "assigned_engineer",
        )

    def clean(self):
        #run the standard clean method first
        cleaned_data=super(UpdateForm, self).clean()

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


class ConfigDetailsForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
    )

    os_type = forms.ChoiceField(label='OS Type', choices=ConfigDetails.OS_TYPES)
    os_version = forms.CharField(label='OS Version')
    storage_adapter_vendor = forms.ChoiceField(label='Storage Adapter Vendor', choices=ConfigDetails.STORAGE_ADAPTER_VENDORS)
    storage_adapter_model = forms.CharField(label='Storage Adapter Model')
    storage_adapter_driver = forms.CharField(label='Storage Adapter Driver')
    storage_adapter_firmware = forms.CharField(label='Storage Adapter Firmware')
    data_ontap_version = forms.CharField(label='Data ONTAP Version')

    class Meta:
        model = ConfigDetails
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
                instance = ConfigDetails.objects.get(os_type=os_type_value,
                                                            os_version=os_version_value,
                                                            storage_adapter_vendor=storage_adapter_vendor_value,
                                                            storage_adapter_model=storage_adapter_model_value,
                                                            storage_adapter_driver=storage_adapter_driver_value,
                                                            storage_adapter_firmware=storage_adapter_firmware_value,
                                                            data_ontap_version=data_ontap_version_value)
            except ObjectDoesNotExist: 
                config_details = ConfigDetails(os_type=os_type_value,
                                                             os_version=os_version_value,
                                                             storage_adapter_vendor=storage_adapter_vendor_value,
                                                             storage_adapter_model=storage_adapter_model_value,
                                                             storage_adapter_driver=storage_adapter_driver_value,
                                                             storage_adapter_firmware=storage_adapter_firmware_value,
                                                             data_ontap_version=data_ontap_version_value)
                config_details.save()
                return config_details


            # if the exception above did not get raised, return instance
            return instance
                

class CommentForm(forms.ModelForm):
    text = forms.CharField(label="", widget=forms.Textarea)

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-7'
    helper.layout = Layout(
       Fieldset('Comments',
           'text',
           Div(
               Button('cancel', 'Cancel', onclick='history.go(-1);', css_class='btn btn-danger'),
               Submit('submit', 'Submit', css_class='btn btn-success'),
               css_class='col-lg-7 text-right',
           ),
       ),
    )


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
    text = forms.CharField(label="Comment", widget=forms.Textarea)

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-6'
    helper.layout = Layout(
       'commenters_choice',
       'text',
       Div(
           Reset('reset the form', 'Cancel', css_class='btn btn-danger'),
           Submit('submit', 'Submit', css_class='btn btn-success'),
           css_class='col-lg-8 text-right',
       ),
    )



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
    commenters_choice = forms.ChoiceField(label='Change "Current State"?', choices=STATE_CHANGE_CHOICES, required=False)

