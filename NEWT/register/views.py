from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.views.generic import View


from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login

# Create your views here.

from forms import UserCreationWithEmailFieldForm, AccountRegistrationForm

class Register(View):

    template_name = 'register.html'

    def post(self, request):
        user_create_form = UserCreationWithEmailFieldForm(request.POST)
        account_registration_form = AccountRegistrationForm(request.POST)

        if user_create_form.is_valid() and account_registration_form.is_valid():
            new_user = user_create_form.save()
            group_status = request.POST['group_status']

            if group_status == 'SALES':
                g = Group.objects.get(name='Sales') 
                g.user_set.add(new_user)
            elif group_status == 'ENGSUP':
                # send email to ET-admin DL and Cc: new user
                pass

            account_registration_form.save(user=new_user)

            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            
            return HttpResponseRedirect('/')

        context = {'user_create_form': user_create_form, 'account_registration_form': account_registration_form}
        return render(request, self.template_name, context)

            
    def get(self, request):
        user_create_form = UserCreationWithEmailFieldForm()
        account_registration_form = AccountRegistrationForm()

        context = {'user_create_form': user_create_form, 'account_registration_form': account_registration_form}
        return render(request, self.template_name, context)

