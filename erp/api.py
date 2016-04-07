# myapp/api.py
from tastypie.authorization import Authorization,DjangoAuthorization
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication
from tastypie.resources import Resource, ModelResource
from tastypie import fields
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache
from erp.models import *

from django.http import HttpResponse
from tastypie import resources

def build_content_type(format, encoding='utf-8'):
    """
    Appends character encoding to the provided format if not already present.
    """
    if 'charset' in format:
        return format

    return "%s; charset=%s" % (format, encoding)

class BaseCorsResource(Resource):
    """
    Class implementing CORS
    """
    def create_response(self, *args, **kwargs):
        response = super(BaseCorsResource, self).create_response(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    def method_check(self, request, allowed=None):
        if allowed is None:
            allowed = []

        request_method = request.method.lower()
        allows = ','.join([a.upper() for a in allowed])

        if request_method == 'options':
            response = HttpResponse(allows)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        if not request_method in allowed:
            response = http.HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        return request_method

class MyModelResource(BaseCorsResource, ModelResource):
    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        response = super(MyModelResource, self).create_response(request, data, response_class=HttpResponse, **response_kwargs)
        return response

        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        # desired_format = self.determine_format(request)
        # serialized = self.serialize(request, data, desired_format)
        # return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)

class AttachmentResource(MyModelResource):
    class Meta:
        queryset = Attachment.objects.all()
        resource_name = 'attachment'
        # allowed_methods = ['get','post','delete']

class UserResource(MyModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']

        filtering = {
            'username': 'exact',
            'id': ALL_WITH_RELATIONS,
        }
        authentication = ApiKeyAuthentication

class VendorResource(MyModelResource):
    class Meta:
        queryset = MyCRM.objects.vendors().order_by('name')
        filtering = {
            'name': ALL,
        }
        # authorization = DjangoAuthorization()

class CustomerResource(MyModelResource):
    class Meta:
        queryset = MyCRM.objects.customers().order_by('name')
        # authorization = DjangoAuthorization()

class ProductResource(MyModelResource):
    brand = fields.ForeignKey(VendorResource, 'brand', full=True)
    attachments = fields.ToManyField(AttachmentResource, 'attachments', full=False)
    class Meta:
        queryset = MyItem.objects.all()
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'brand': ALL_WITH_RELATIONS,
            'name': ['icontains'],
        }
        cache = SimpleCache(timeout=100)
    
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(name__icontains = 'LEO')