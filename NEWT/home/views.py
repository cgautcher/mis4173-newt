from django.shortcuts import render

# Create your views here.

from objects.models import EnablementRequest

def index(request):

    object_dict = {}

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

        elif group == 'Enablement':
            object_list_review = EnablementRequest.objects.filter(current_state__contains=group)
            object_dict = {'object_list_review': object_list_review,
                           'navbar_options_template': 'enablement_navbar_options.html',
                          }

    context = {'group_membership': group_membership,}

    if object_dict:
        for k,v in object_dict.items():
            context[k] = v

    return render(request, 'home/index.html', context)
