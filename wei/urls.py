from django.conf.urls import patterns,include,url
from django.contrib import admin
import settings

# tastypie API urls
from tastypie.api import Api
from erp.api import *
v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(VendorResource())
v1_api.register(CustomerResource())
v1_api.register(ProductResource())
v1_api.register(AttachmentResource())
v1_api.register(SeasonResource())
v1_api.register(CurrencyResource())


urlpatterns = patterns('',
    # REST endpoints
    url(r'^api/', include(v1_api.urls)),

    # Admin interface
    url(r'^admin/', include(admin.site.urls)),

    # Social media login
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),

    # MyApplication urls
    url(r'^wei/', include ('erp.urls')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
