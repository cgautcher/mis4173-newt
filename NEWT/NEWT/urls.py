from django.conf.urls import patterns, include, url
from django.contrib import admin

from home import views
from register.views import Register
from objects.views import Initiate, List, ViewDetailsAndComments, Update


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'NEWT.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'home.views.index', name='home'),
    
    url(r'^register/', Register.as_view(), name='register'),
    
    url(r'^initiate/', Initiate.as_view(), name='initiate'),

    url(r'^list/', List.as_view(), name='list'),

    url(r'^view/(?P<slug>[-_\w]+)/$', ViewDetailsAndComments.as_view(), name='view'),

    url(r'^update/(?P<slug>[-_\w]+)/$', Update.as_view(), name='update'),

    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    url(r'^admin/', include(admin.site.urls)),
)
