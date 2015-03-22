from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from models import AccountRegistration

class UserCreationWithEmailFieldForm(UserCreationForm):
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

    group_status = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=AccountRegistration.GROUP_STATUS_CHOICES)

    class Meta:
        model = AccountRegistration
        fields = ("group_status",)

    def save(self, commit=True, user=None):
        if commit:
            account_registration = AccountRegistration(user=user, group_status=self.cleaned_data["group_status"])
            account_registration.save()
