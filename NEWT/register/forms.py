from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from models import AccountRegistration

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Reset, Row, Field, Fieldset


class UserCreationWithEmailFieldForm(UserCreationForm):

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
        'username',
        'email',
        'password1',
        'password2',
    )


    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationWithEmailFieldForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user # return user so we can authenticate and login

class AccountRegistrationForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
        'group_status',
        Div(
           Button('cancel', 'Cancel', onclick='location.href="/";', css_class='btn btn-danger'),
           Submit('submit', 'Submit', css_class='btn btn-success'),
           css_class='col-lg-7 text-right',
        ),
    )

    group_status = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=AccountRegistration.GROUP_STATUS_CHOICES)

    class Meta:
        model = AccountRegistration
        fields = ("group_status",)

    def save(self, commit=True, user=None):
        if commit:
            account_registration = AccountRegistration(user=user, group_status=self.cleaned_data["group_status"])
            account_registration.save()
