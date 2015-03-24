from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.views.generic import View, ListView, DetailView, FormView

# My Stuff
from forms import (InitiateEnablementRequestForm,
                   UpdateEnablementRequestForm,
                   ConfigurationDetailsForm,
                   CommentForm,
                   RequestFeedbackForm,
                   ProvideFeedbackForm,
                   FilterForm,)

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

        if initiate_form.is_valid() and config_details_form.is_valid() and comment_form.is_valid():
            customer_name = initiate_form.cleaned_data['customer_name']
            configuration_details = config_details_form.save()

            configuration_details_id = int(configuration_details.id)
            first_parent_request = EnablementRequest.objects.filter(configuration_details_id=configuration_details_id).first()
            if first_parent_request:
                parent_request = first_parent_request.identifier
            else:
                parent_request = ""
            
            # set current_state to 'Enablement Review'
            current_state = 'Enablement Review'

            enablement_request = EnablementRequest(customer_name=customer_name,
                                                   parent_request=parent_request,
                                                   sales_initiator=request.user,
                                                   configuration_details=configuration_details,
                                                   current_state=current_state)

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

        context = {'initiate_form': initiate_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form,}

        return render(request, self.template_name, context)

            
    def get(self, request, *args, **kwargs):
        initiate_form = InitiateEnablementRequestForm()
        config_details_form = ConfigurationDetailsForm()
        comment_form = CommentForm()

        context = {'initiate_form': initiate_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form,}

        return render(request, self.template_name, context)


class Update(View):
    template_name = 'update.html'

    def post(self, request, *args, **kwargs):
        self.slug = self.kwargs['slug']
        enablement_request = EnablementRequest.objects.get(slug=self.slug)
        pre_update_state = enablement_request.current_state
        old_configuration_details_id = enablement_request.configuration_details_id

        update_form = UpdateEnablementRequestForm(request.POST, instance=enablement_request)
        config_details_form = ConfigurationDetailsForm(request.POST)
        comment_form = CommentForm(request.POST)

        if update_form.is_valid() and config_details_form.is_valid() and comment_form.is_valid():
            configuration_details = config_details_form.save()
            configuration_details_id = int(configuration_details.id)
            first_parent_request = EnablementRequest.objects.filter(configuration_details_id=configuration_details_id).first()
            if first_parent_request:
                parent_request = first_parent_request.identifier
                updated_enablement_request = update_form.save(commit=False)
                updated_enablement_request.parent_request = parent_request
                updated_enablement_request.save()
            else:
                updated_enablement_request = update_form.save()

            post_update_state = updated_enablement_request.current_state

            if pre_update_state != post_update_state:
                comment_form.save(enablement_request=enablement_request,
                                  commenter=request.user,
                                  pre_comment_state=pre_update_state,
                                  post_comment_state=post_update_state)
            else:
                comment_form.save(enablement_request=enablement_request, commenter=request.user)

            return HttpResponseRedirect(reverse('view', kwargs={'slug': self.slug}))

        context = {'enablement_request': enablement_request,
                   'update_form': update_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form}

        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        self.slug = self.kwargs['slug']
        enablement_request = EnablementRequest.objects.get(slug=self.slug)
        configuration_details = enablement_request.configuration_details
        
        update_form = UpdateEnablementRequestForm(instance=enablement_request)
        config_details_form = ConfigurationDetailsForm(instance=configuration_details)
        comment_form = CommentForm()

        context = {'enablement_request': enablement_request,
                   'update_form': update_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form}

        return render(request, self.template_name, context)


class Locate(View):
    """View to handle the search box form POST in base.html"""

    template_name = 'locate.html'
 
    def post(self, request, *args, **kwargs): 
        locate_identifier = request.POST['locate_identifier']
        results = EnablementRequest.objects.filter(identifier__contains=locate_identifier)
  
        context = {'results': results}
                   

        return render(request, self.template_name, context)  


class Filter(View):
    """View to filter the objects based on specific fields"""

    template_name = 'filter.html'

    def post(self, request, *args, **kwargs):
        filter_form = FilterForm(request.POST)

        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            customer_name = cd['customer_name']
            os_type = cd['os_type']
            os_version = cd['os_version']
            storage_adapter_vendor = cd['storage_adapter_vendor']
            storage_adapter_model = cd['storage_adapter_model']
            storage_adapter_driver = cd['storage_adapter_driver']
            storage_adapter_firmware = cd['storage_adapter_firmware']
            data_ontap_version = cd['data_ontap_version']


        # show pre-filled forms with criteria from the form that triggered the POST
        filter_form = FilterForm(initial=cd)        

        # need to do the JOIN queries to check config details
        results = EnablementRequest.objects.filter(customer_name__contains=customer_name,
                                                   configuration_details__os_type__contains=os_type,
                                                   configuration_details__os_version__contains=os_version,
                                                   configuration_details__storage_adapter_vendor__contains=storage_adapter_vendor,
                                                   configuration_details__storage_adapter_model__contains=storage_adapter_model,
                                                   configuration_details__storage_adapter_driver__contains=storage_adapter_driver,
                                                   configuration_details__storage_adapter_firmware__contains=storage_adapter_firmware,
                                                   configuration_details__data_ontap_version__contains=data_ontap_version,)

        context = {'results': results,
                   'filter_form': filter_form,
                   'request': request}

        return render(request, self.template_name, context)


    def get(self, request, *args, **kwargs):
        filter_form = FilterForm()
        context = {'filter_form': filter_form,
                   'request': request,}

        return render(request, self.template_name, context)
        


class ViewDetails(DetailView):
    """View to show all details and comments of the items"""

    template_name = 'view.html'
    model = EnablementRequest

    context_object_name = 'enablement_request'

    def get_context_data(self, **kwargs):
        context = super(ViewDetails, self).get_context_data()
        context['configuration_details'] = context['enablement_request'].configuration_details
        context['comments'] = context['enablement_request'].comment_set.all()
        enablement_user_list = User.objects.filter(groups__name='Enablement')
        if self.request.user in enablement_user_list:
            context['comment_form'] = RequestFeedbackForm()
        else:
            context['comment_form'] = ProvideFeedbackForm()
        return context


class CommentInViewDetails(View):
    """View to specifically handle POST method when hitting submit button,
       after form processing, redirects back to the ViewDetails view.
    """

    template_name = 'view.html'
    
    def post(self, request, *args, **kwargs):
        enablement_user_list = User.objects.filter(groups__name='Enablement')
        if request.user in enablement_user_list:
            comment_form = RequestFeedbackForm(request.POST)
        else:
            comment_form = ProvideFeedbackForm(request.POST)
        if comment_form.is_valid():
            enablement_request_slug = request.POST['er_slug']
            enablement_request = EnablementRequest.objects.get(slug=enablement_request_slug)
            if request.POST['commenters_choice'] and (request.POST['commenters_choice'] != enablement_request.current_state):
                pre_comment_state = enablement_request.current_state
                post_comment_state = request.POST['commenters_choice']
                comment_form.save(enablement_request=enablement_request,
                                  commenter=request.user,
                                  pre_comment_state=pre_comment_state,
                                  post_comment_state=post_comment_state)
                enablement_request.current_state = post_comment_state
                enablement_request.save()
            else:
                comment_form.save(enablement_request=enablement_request, commenter=request.user)
            return HttpResponseRedirect(reverse('view', kwargs={'slug': enablement_request_slug}))


class ViewDetailsAndComments(View):
    """View to direct traffic to appropriate views that handle POST vs. GET"""

    def get(self, request, *args, **kwargs):
        view = ViewDetails.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentInViewDetails.as_view()
        return view(request, *args, **kwargs)

