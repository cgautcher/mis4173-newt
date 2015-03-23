from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.views.generic import View, ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin

# My Stuff
from forms import (InitiateEnablementRequestForm,
                   UpdateEnablementRequestForm,
                   ConfigurationDetailsForm,
                   CommentForm,)

from models import (EnablementRequest,
                    ConfigurationDetails,
                    Comment,)


# Create your views here.

class Initiate(View):
    template_name = 'initiate.html'

    def post(self, request, *args, **kwargs):
        initiate_form = InitiateEnablementRequestForm(request.POST)
        config_details_form = ConfigurationDetailsForm(request.POST)
        comment_form = CommentForm(request.POST)

        groups_of_request_user = request.user.groups.values_list('name', flat=True)

        if initiate_form.is_valid() and config_details_form.is_valid() and comment_form.is_valid():
            customer_name = initiate_form.cleaned_data['customer_name']
            configuration_details = config_details_form.save()
            
            # set current_state to 'Enablement Review'
            current_state = 'Enablement Review'

            enablement_request = EnablementRequest(
                customer_name=customer_name,
                sales_initiator=request.user,
                configuration_details=configuration_details,
                current_state=current_state
            )

            enablement_request.full_clean()
            enablement_request.save()
            id = enablement_request.id
            identifier = 'ER-' + str(id).zfill(6)
            slug = identifier.lower()
            enablement_request_add_things = EnablementRequest.objects.get(id=id)
            enablement_request_add_things.identifier = identifier
            enablement_request_add_things.slug = slug
            enablement_request_add_things.save()

            comment_form.save(enablement_request=enablement_request, commenter=request.user)

            return HttpResponseRedirect(reverse('view', kwargs={'slug': slug}))

        context = {
            'initiate_form': initiate_form,
            'config_details_form': config_details_form,
            'comment_form': comment_form,
            'groups_of_request_user': groups_of_request_user 
        }
        return render(request, self.template_name, context)
            
    def get(self, request, *args, **kwargs):
        initiate_form = InitiateEnablementRequestForm()
        config_details_form = ConfigurationDetailsForm()
        comment_form = CommentForm()

        groups_of_request_user = request.user.groups.values_list('name', flat=True)

        context = {
            'initiate_form': initiate_form,
            'config_details_form': config_details_form,
            'comment_form': comment_form,
            'groups_of_request_user': groups_of_request_user 
        }
        return render(request, self.template_name, context)


class Update(View):
    template_name = 'update.html'

    def post(self, request, *args, **kwargs):
        self.slug = self.kwargs['slug']
        enablement_request = EnablementRequest.objects.get(slug=self.slug)
        old_configuration_details_id = enablement_request.configuration_details_id

        update_form = UpdateEnablementRequestForm(request.POST, instance=enablement_request)
        config_details_form = ConfigurationDetailsForm(request.POST)
        comment_form = CommentForm(request.POST)

        if update_form.is_valid() and config_details_form.is_valid() and comment_form.is_valid():
            new_configuration_details_id = config_details_form.save()
            if old_configuration_details_id == new_configuration_details_id:
                update_form.save()
            else:
                updated_enablement_request = update_form.save(commit=False)
                updated_enablement_request.configuration_details_id = new_configuration_details_id
                updated_enablement_request.save()
            comment_form.save(enablement_request=enablement_request, commenter=request.user)

            return HttpResponseRedirect(reverse('view', kwargs={'slug': self.slug}))

        context = {
            'enablement_request': enablement_request,
            'update_form': update_form,
            'config_details_form': config_details_form,
            'comment_form': comment_form,
        }
        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        self.slug = self.kwargs['slug']
        enablement_request = EnablementRequest.objects.get(slug=self.slug)
        configuration_details = enablement_request.configuration_details
        
        update_form = UpdateEnablementRequestForm(instance=enablement_request)
        config_details_form = ConfigurationDetailsForm(instance=configuration_details)
        comment_form = CommentForm()

        context = {
            'enablement_request': enablement_request,
            'update_form': update_form,
            'config_details_form': config_details_form,
            'comment_form': comment_form,
        }
        return render(request, self.template_name, context)


class List(ListView):
    template_name = 'list.html'
    model = EnablementRequest

    context_object_name = 'enablement_request_list'


class ViewDetails(DetailView):
    template_name = 'view.html'
    model = EnablementRequest

    context_object_name = 'enablement_request'

    def get_context_data(self, **kwargs):
        context = super(ViewDetails, self).get_context_data()
        context['configuration_details'] = context['enablement_request'].configuration_details
        context['comments'] = context['enablement_request'].comment_set.all()
        context['groups_of_request_user'] = self.request.user.groups.values_list('name', flat=True)
        context['comment_form'] = CommentForm()
        return context


class CommentInViewDetails(View):
    template_name = 'view.html'
    
    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            enablement_request_slug = request.POST['er_slug']
            enablement_request = EnablementRequest.objects.get(slug=enablement_request_slug)
            comment_form.save(enablement_request=enablement_request, commenter=request.user)
            return HttpResponseRedirect(reverse('view', kwargs={'slug': enablement_request_slug}))


class ViewDetailsAndComments(View):

    def get(self, request, *args, **kwargs):
        view = ViewDetails.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentInViewDetails.as_view()
        return view(request, *args, **kwargs)

