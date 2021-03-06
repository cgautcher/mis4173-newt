from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.core.mail import send_mail

from django.core.exceptions import PermissionDenied

from django.views.generic import View, ListView, DetailView, FormView

# My Stuff
from forms import (InitiateForm,
                   UpdateForm,
                   ConfigDetailsForm,
                   CommentForm,
                   RequestFeedbackForm,
                   ProvideFeedbackForm,
                   FilterForm,)

from models import (EnablementRequest,
                    ConfigDetails,
                    Comment,)


# Create your views here.

class Initiate(View):
    template_name = 'initiate.html'

    def post(self, request, *args, **kwargs):
        initiate_form = InitiateForm(request.POST)
        config_details_form = ConfigDetailsForm(request.POST)
        comment_form = CommentForm(request.POST)

        group_membership = request.user.groups.values_list('name',flat=True)

        if initiate_form.is_valid() and config_details_form.is_valid() and comment_form.is_valid():
            customer_name = initiate_form.cleaned_data['customer_name']
            short_term_revenue = initiate_form.cleaned_data['short_term_revenue']
            config_details = config_details_form.save()

            config_details_id = int(config_details.id)
            first_parent_request = EnablementRequest.objects.filter(config_details_id=config_details_id).first()
            if first_parent_request:
                parent_request = first_parent_request.identifier
            else:
                parent_request = ""
            
            # set current_state to 'Enablement Review'
            current_state = 'Enablement Review'

            enablement_request = EnablementRequest(customer_name=customer_name,
                                                   short_term_revenue=short_term_revenue,
                                                   parent_request=parent_request,
                                                   sales_initiator=request.user,
                                                   config_details=config_details,
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

            # send emails to Enablement group members and
            email_subject = 'Enablement Request %s - New Request initiated by %s' % (identifier, request.user.username)
            url = 'http://newt.netapp.com:4173/view/%s' % identifier

            sales_initiator_email = request.user.email
            sales_initiator_message = 'Thank you for your request (%s).  We will review it and respond within 1-2 days. ' % identifier
            sales_initiator_message += 'You can view the Enablement Request at <a href="%s">%s</a>' % (url, url)

            send_mail(email_subject, sales_initiator_message, 'NEWT Admin', [sales_initiator_email], html_message=sales_initiator_message)

            enablement_group_emails = Group.objects.get(name='Enablement').user_set.values_list('email', flat=True)
            enablement_group_message = 'A new request has been submitted.  Someone please go look at it:  <a href="%s">%s</a>' % (url, url)

            send_mail(email_subject, enablement_group_message, 'NEWT Admin', enablement_group_emails, html_message=enablement_group_message)




            return HttpResponseRedirect(reverse('view', kwargs={'slug': slug}))

        context = {'initiate_form': initiate_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form,
                   'group_membership': group_membership,}

        return render(request, self.template_name, context)

            
    def get(self, request, *args, **kwargs):
        initiate_form = InitiateForm()
        config_details_form = ConfigDetailsForm()
        comment_form = CommentForm()

        group_membership = request.user.groups.values_list('name',flat=True)

        context = {'initiate_form': initiate_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form,
                   'group_membership': group_membership,}

        return render(request, self.template_name, context)


class Update(View):
    template_name = 'update.html'

    def post(self, request, *args, **kwargs):
        group_membership = request.user.groups.values_list('name',flat=True)
        # if this user is not in the Enablement group, throw a permission denied error
        if 'Enablement' not in group_membership:
            raise PermissionDenied

        self.slug = self.kwargs['slug']
        enablement_request = EnablementRequest.objects.get(slug=self.slug)
        pre_update_state = enablement_request.current_state
        old_config_details_id = int(enablement_request.config_details_id)

        update_form = UpdateForm(request.POST, instance=enablement_request)
        config_details_form = ConfigDetailsForm(request.POST)
        comment_form = CommentForm(request.POST)

        if update_form.is_valid() and config_details_form.is_valid() and comment_form.is_valid():
            # don't commit to database until we check for other conditions
            updated_enablement_request = update_form.save(commit=False)

            # see if the config_details_id changed upon update, and if so,
            # + does it match an existing request, and if so,
            # + associate the two via the "parent_request" attribute
            config_details = config_details_form.save()
            config_details_id = int(config_details.id)
            if old_config_details_id != config_details_id:
                first_parent_request = EnablementRequest.objects.filter(
                                           config_details_id=config_details_id,
                                           ).exclude(id=enablement_request.id).first()
                if first_parent_request:
                    parent_request = first_parent_request.identifier
                    updated_enablement_request.parent_request = parent_request

            post_update_state = updated_enablement_request.current_state
            if pre_update_state != post_update_state:
                comment_form.save(enablement_request=enablement_request,
                                  commenter=request.user,
                                  pre_comment_state=pre_update_state,
                                  post_comment_state=post_update_state)

                identifier = enablement_request.identifier
                url = 'http://newt.netapp.com:4173/view/%s' % identifier
                email_subject = 'Enablement Request %s - current state has changed to %s' % (identifier, post_update_state)
                email_message = 'The Enablement Request (%s) state has been changed to "%s".' % (identifier, post_update_state)
                email_message += 'You can view the Enablement Request at <a href="%s">%s</a>' % (url, url)
                enablement_group_emails = Group.objects.get(name='Enablement').user_set.values_list('email', flat=True)
                sales_initiator_email = enablement_request.sales_initiator.email
                email_addresses = []

                if post_update_state == 'Completed':
                    updated_enablement_request.completion_timestamp = datetime.now()
                    email_addresses = [sales_initiator_email]
                    email_addresses.extend(enablement_group_emails)
                elif post_update_state == 'Enablement Review':
                    email_addresses.extend(enablement_group_emails)
                elif post_update_state == 'Sales Review':
                    email_addresses = [sales_initiator_email]
                elif post_update_state == 'Engineering Review':
                    engineering_group_emails = Group.objects.get(name='Engineering').user_set.values_list('email', flat=True) 
                    email_addresses.extend(engineering_group_emails)
                elif post_update_state == 'Support Review':
                    support_group_emails = Group.objects.get(name='Support').user_set.values_list('email', flat=True) 
                    email_addresses.extend(support_group_emails)
                else:
                    email_addresses = [sales_initiator_email]

                send_mail(email_subject, email_message, 'NEWT Admin', email_addresses, html_message=email_message)

            else:
                comment_form.save(enablement_request=enablement_request, commenter=request.user)

            updated_enablement_request.save()

            return HttpResponseRedirect(reverse('view', kwargs={'slug': self.slug}))

        context = {'enablement_request': enablement_request,
                   'update_form': update_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form,
                   'group_membership': group_membership,
                   'navbar_options_template': 'enablement_navbar_options.html',}

        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        group_membership = request.user.groups.values_list('name',flat=True)
        # if this user is not in the Enablement group, throw a permission denied error
        if 'Enablement' not in group_membership:
            raise PermissionDenied

        self.slug = self.kwargs['slug']
        enablement_request = EnablementRequest.objects.get(slug=self.slug)
        config_details = enablement_request.config_details
        
        update_form = UpdateForm(instance=enablement_request)
        config_details_form = ConfigDetailsForm(instance=config_details)
        comment_form = CommentForm()

        context = {'enablement_request': enablement_request,
                   'update_form': update_form,
                   'config_details_form': config_details_form,
                   'comment_form': comment_form,
                   'group_membership': group_membership,
                   'navbar_options_template': 'enablement_navbar_options.html',}

        return render(request, self.template_name, context)


class Locate(View):
    """View to handle the search box form POST in base.html"""

    template_name = 'locate.html'
 
    def post(self, request, *args, **kwargs):
        locate_identifier = request.POST['locate_identifier']
        objects = EnablementRequest.objects.filter(identifier__contains=locate_identifier).order_by('-identifier')
        group_membership = request.user.groups.values_list('name',flat=True)
        if 'Enablement' in group_membership:
            navbar_options_template = 'enablement_navbar_options.html'
        elif 'Sales' in group_membership:
            navbar_options_template = 'sales_navbar_options.html'        
        else:
            navbar_options_template = ''

        context = {'objects': objects,
                   'locate_identifier': locate_identifier,
                   'group_membership': group_membership,
                   'navbar_options_template': navbar_options_template,}
                   

        return render(request, self.template_name, context)  


class Filter(View):
    """View to filter the objects based on specific fields"""

    template_name = 'filter.html'

    def post(self, request, *args, **kwargs):
        group_membership = request.user.groups.values_list('name',flat=True)
        # if this user is not in the Enablement group, throw a permission denied error
        if 'Enablement' not in group_membership:
            raise PermissionDenied
        filter_form = FilterForm(request.POST)

        # save values from form fields into a dictionary
        filter_form.full_clean() 
        cd = filter_form.cleaned_data

        if cd['assigned_engineer'] == '':
            cd['assigned_engineer'] = None

        # show pre-filled forms with criteria from the form that triggered the POST
        filter_form = FilterForm(initial=cd)        

        # 
        objects = EnablementRequest.objects.filter(customer_name__contains=cd['customer_name'],
                                                   short_term_revenue__gte=cd['short_term_revenue'],
                                                   current_state__contains=cd['current_state'],
                                                   assigned_engineer=cd['assigned_engineer'],
                                                   config_details__os_type__contains=cd['os_type'],
                                                   config_details__os_version__contains=cd['os_version'],
                                                   config_details__storage_adapter_vendor__contains=cd['storage_adapter_vendor'],
                                                   config_details__storage_adapter_model__contains=cd['storage_adapter_model'],
                                                   config_details__storage_adapter_driver__contains=cd['storage_adapter_driver'],
                                                   config_details__storage_adapter_firmware__contains=cd['storage_adapter_firmware'],
                                                   config_details__data_ontap_version__contains=cd['data_ontap_version'],
                                               ).order_by('-identifier')

        context = {'objects': objects,
                   'filter_form': filter_form,
                   'request': request,
                   'group_membership': group_membership,
                   'navbar_options_template': 'enablement_navbar_options.html',}

        return render(request, self.template_name, context)


    def get(self, request, *args, **kwargs):
        group_membership = request.user.groups.values_list('name',flat=True)
        # if this user is not in the Enablement group, throw a permission denied error
        if 'Enablement' not in group_membership:
            raise PermissionDenied
        filter_form = FilterForm()
        context = {'filter_form': filter_form,
                   'request': request,
                   'group_membership': group_membership,
                   'navbar_options_template': 'enablement_navbar_options.html',}

        return render(request, self.template_name, context)
        


class ViewDetails(DetailView):
    """View to show all details and comments of the items"""

    template_name = 'view.html'
    model = EnablementRequest

    context_object_name = 'enablement_request'

    def get_context_data(self, **kwargs):
        context = super(ViewDetails, self).get_context_data()
        context['config_details'] = context['enablement_request'].config_details
        group_membership = self.request.user.groups.values_list('name',flat=True)
        context['group_membership'] = group_membership
        if 'Enablement' in group_membership:
            context['comment_form'] = RequestFeedbackForm()
            context['navbar_options_template'] = 'enablement_navbar_options_update_button.html'
        elif 'Sales' or 'Engineering' or 'Support' in group_membership:
            context['comment_form'] = ProvideFeedbackForm()
        else:
            context['comment_form'] = False
        if 'Sales' in group_membership:
            context['navbar_options_template'] = 'sales_navbar_options.html'
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

        enablement_request_slug = request.POST['er_slug']
        if comment_form.is_valid():
            enablement_request = EnablementRequest.objects.get(slug=enablement_request_slug)
            comment = request.POST['text']
            identifier = enablement_request.identifier
            url = 'http://newt.netapp.com:4173/view/%s' % identifier
            email_addresses = []

            if request.POST['commenters_choice'] and (request.POST['commenters_choice'] != enablement_request.current_state):
                pre_comment_state = enablement_request.current_state
                post_comment_state = request.POST['commenters_choice']
                comment_form.save(enablement_request=enablement_request,
                                  commenter=request.user,
                                  pre_comment_state=pre_comment_state,
                                  post_comment_state=post_comment_state)
                enablement_request.current_state = post_comment_state
                enablement_request.save()

                email_subject = 'Enablement Request %s - current state has changed to %s' % (identifier, post_comment_state)
                email_message = 'The Enablement Request (%s) state has been changed to "%s".<BR><BR>' % (identifier, post_comment_state)
                email_message += '%s commented: %s <BR><BR>' % (request.user.username, comment)
                email_message += 'You can view the Enablement Request at <a href="%s">%s</a>' % (url, url)

                if post_comment_state == 'Enablement Review':
                    enablement_group_emails = Group.objects.get(name='Enablement').user_set.values_list('email', flat=True)
                    email_addresses.extend(enablement_group_emails)
                elif post_comment_state == 'Sales Review':
                    sales_initiator_email = enablement_request.sales_initiator.email
                    email_addresses = [sales_initiator_email]
                elif post_comment_state == 'Engineering Review':
                    engineering_group_emails = Group.objects.get(name='Engineering').user_set.values_list('email', flat=True)
                    email_addresses.extend(engineering_group_emails)
                elif post_comment_state == 'Support Review':
                    support_group_emails = Group.objects.get(name='Support').user_set.values_list('email', flat=True)
                    email_addresses.extend(support_group_emails)

            else:
                comment_form.save(enablement_request=enablement_request, commenter=request.user)

                sales_initiator_email = enablement_request.sales_initiator.email
                commenter_email = request.user.email
                enablement_group_emails = Group.objects.get(name='Enablement').user_set.values_list('email', flat=True)
                email_addresses = [sales_initiator_email, commenter_email]
                email_addresses.extend(enablement_group_emails)

                email_subject = 'Enablement Request %s - %s commented' % (identifier, request.user.username)
                email_message = '%s commented: %s <BR><BR>' % (request.user.username, comment)
                email_message += 'You can view the Enablement Request at <a href="%s">%s</a>' % (url, url)
            
            # send email after figuring out what to send and who to send it to    
            send_mail(email_subject, email_message, 'NEWT Admin', email_addresses, html_message=email_message)

        return HttpResponseRedirect(reverse('view', kwargs={'slug': enablement_request_slug}))


class ViewDetailsAndComments(View):
    """View to direct traffic to appropriate views that handle POST vs. GET"""

    def get(self, request, *args, **kwargs):
        view = ViewDetails.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentInViewDetails.as_view()
        return view(request, *args, **kwargs)

