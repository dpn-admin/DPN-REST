"""
    There are two ways of constructing a software design.
    One way is to make it so simple that there are obviously no deficiencies.
    And the other way is to make it so complicated that there are no obvious deficiencies.
            - C. A. R. Hoare
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    # Grappelli URLs
   url(r'^grappelli/', include('grappelli.urls')),

   # Default Root
   # url(r'^$', 'dpn_registry.views.index', name="siteroot"),

   # Login URL
   url(r'^%s$' % settings.LOGIN_URL, 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
   url(r'^%s$' % settings.LOGOUT_URL, 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, name="logout"),

   # REST Login/Out
   url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

   # API calls
   url(r'^api-v1/', include('dpn.api.urls', namespace="api")),

   # API Documentation
   url(r'^docs/', include('rest_framework_swagger.urls', namespace="api-docs"))
)
