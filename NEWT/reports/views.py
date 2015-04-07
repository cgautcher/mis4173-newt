import sys

sys.path.append('..')

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import Group

from objects.models import (EnablementRequest, )

from .forms import DateRangeForm


# Collection of report names that will be used
REPORT_LIST = ('Assigned to Engineer',
               'Short Term Revenue per Date Range',
               )

# Create your views here.

class BaseReports(View):
    template_name = 'base-reports.html'

    def get(self, request, *args, **kwargs):
        context = {'navbar_options_template': 'enablement_navbar_options.html',
                   'report_list': REPORT_LIST,
                   }

        return render(request, self.template_name, context)


class SpecificReport(BaseReports):
    def post(self, request, *args, **kwargs):
        report_name = kwargs['report_name']
        report_template = report_name + '.html'
        context = {
            'navbar_options_template': 'enablement_navbar_options.html',
            'report_list': REPORT_LIST,
            'report_name': kwargs['report_name'],
            'report_template': report_template,
        }
        report_content = {}

        if report_name == 'short-term-revenue-per-date-range':
            date_range_form = DateRangeForm(request.POST)
            if date_range_form.is_valid():
                cleaned_data = date_range_form.cleaned_data
                report_content['start_date'] = cleaned_data['start_date']
                report_content['end_date'] = cleaned_data['end_date']
                objects_completed_in_range = EnablementRequest.objects.filter(
                    completion_timestamp__range=(cleaned_data['start_date'], cleaned_data['end_date'])).filter(
                    current_state='Completed')
                report_content['completed_object_count'] = len(objects_completed_in_range)
                total_short_term_revenue = 0
                for object in objects_completed_in_range:
                    total_short_term_revenue += object.short_term_revenue
                report_content['total_short_term_revenue'] = total_short_term_revenue
                context['form'] = date_range_form

        context['report_content'] = report_content
        return render(request, self.template_name, context)


    def get(self, request, *args, **kwargs):

        report_name = kwargs['report_name']
        report_template = report_name + '.html'
        context = {
            'navbar_options_template': 'enablement_navbar_options.html',
            'report_list': REPORT_LIST,
            'report_name': kwargs['report_name'],
            'report_template': report_template,
        }
        report_content = {}

        if report_name == 'assigned-to-engineer':

            states_to_exclude = ['Rejected', 'Completed']
            members_to_exclude = ['shiva', ]

            enablement_engineers_queryset = Group.objects.get(name='Enablement').user_set.exclude(
                username__in=members_to_exclude)
            active_objects_queryset = EnablementRequest.objects.exclude(current_state__in=states_to_exclude)

            for enablement_engineer in enablement_engineers_queryset:
                active_objects_per_engineer = active_objects_queryset.filter(assigned_engineer=enablement_engineer)
                report_content[enablement_engineer.username] = active_objects_per_engineer

        elif report_name == 'short-term-revenue-per-date-range':
            date_range_form = DateRangeForm()
            context['form'] = date_range_form
            report_content = True

        context['report_content'] = report_content
        return render(request, self.template_name, context)