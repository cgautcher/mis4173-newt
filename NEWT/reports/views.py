import sys
sys.path.append('..')

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import Group

from objects.models import (EnablementRequest,)


# Collection of report names that will be used
REPORT_LIST = ('Assigned to Engineer',
               'Some other report',
               )

# Create your views here.

class BaseReports(View):
    template_name = 'base_reports.html'

    def get(self, request, *args, **kwargs):

        context = { 'navbar_options_template': 'enablement_navbar_options.html',
                    'report_list': REPORT_LIST,
                    }

        return render(request, self.template_name, context)




class SpecificReport(BaseReports):


    def get(self, request, *args, **kwargs):

        report_name = kwargs['report_name']
        report_content = {}

        if report_name == 'assigned-to-engineer':
            assignment_dict = {}
            states_to_exclude = ['Rejected', 'Completed']
            members_to_exclude = ['shiva',]

            enablement_engineers_queryset = Group.objects.get(name='Enablement').user_set.exclude(username__in=members_to_exclude)
            current_objects_queryset = EnablementRequest.objects.exclude(current_state__in=states_to_exclude)

            for enablement_engineer in enablement_engineers_queryset:
                how_many_objects = current_objects_queryset.filter(assigned_engineer=enablement_engineer)
                assignment_dict[enablement_engineer.username] = len(how_many_objects)

            report_content = assignment_dict
            report_template = 'assigned-to-engineer.html'

        if report_name == 'some-other-report':
            report_content = True
            report_template = 'some-other-report.html'

        context = { 'navbar_options_template': 'enablement_navbar_options.html',
                    'report_list': REPORT_LIST,
                    'report_name': kwargs['report_name'],
                    'report_content': report_content,
                    'report_template': report_template,
                    }

        return render(request, self.template_name, context)