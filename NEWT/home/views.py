from django.shortcuts import render

# Create your views here.

from objects.models import EnablementRequest

def index(request):
    context = {}
    object_dict = {}
    template_name = 'home/index.html'

    group_membership = request.user.groups.values_list('name',flat=True)
    for group in group_membership:
        if group == 'Sales':
            sales_initiator = int(request.user.id)    
            object_list_all = EnablementRequest.objects.filter(sales_initiator=sales_initiator)
            object_list_review =  object_list_all.filter(current_state__contains=group)
            object_dict = {'object_list_all': object_list_all,
                           'object_list_review': object_list_review,
                           'navbar_options_template': 'sales_navbar_options.html',
                          }
            template_name = 'home/sales.html'

        elif group == 'Enablement':
            object_list_review = EnablementRequest.objects.filter(current_state__contains=group)
            object_list_in_progress = EnablementRequest.objects.filter(current_state='Accepted - In Progress')
            object_dict = {'object_list_review': object_list_review,
                           'object_list_in_progress': object_list_in_progress,
                           'navbar_options_template': 'enablement_navbar_options.html',
                          }
            template_name = 'home/enablement.html'


    if object_dict:
        for k,v in object_dict.items():
            context[k] = v

    return render(request, template_name, context)
