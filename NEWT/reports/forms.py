from django import forms
from datetime import datetime, timedelta
from django.forms.extras.widgets import SelectDateWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Reset, Row, Field, Fieldset

class DateRangeForm(forms.Form):

    date_today = datetime.today() + timedelta(1)
    date_30_days_ago =  datetime.now() + timedelta(-30)
    start_date = forms.DateField(initial=date_30_days_ago, label='Start Date')
    end_date = forms.DateField(initial=date_today,)

    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-3'
    helper.layout = Layout(
        'start_date',
        'end_date',
        Reset('Reset The Form', 'Reset', css_class='btn btn-danger'),
        Submit('submit', 'Submit', css_class='btn btn-success'),
    )

