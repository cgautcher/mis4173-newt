from django.conf.urls import patterns, url

from reports.views import (BaseReports,
                           SpecificReport,)


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'NEWT.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', BaseReports.as_view(), name='reports'),
    url(r'(?P<report_name>[-_\w]+)/$', SpecificReport.as_view(), name='specific-report'),
)
