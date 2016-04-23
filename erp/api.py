# myapp/api.py
from tastypie.authorization import Authorization,DjangoAuthorization
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication
from tastypie.resources import Resource, ModelResource
from tastypie import fields
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.cache import SimpleCache
from tastypie.paginator import Paginator
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
  
class CurrencyResource(MyModelResource):
    class Meta:
        queryset = MyCurrency.objects.all()
        resource_name = 'currency'
        fields = ['name', 'symbol']

class UserResource(MyModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            'username': 'exact',
            'id': ALL_WITH_RELATIONS,
        }
        # authentication = ApiKeyAuthentication()
        # authorization = DjangoAuthorization()

class VendorResource(MyModelResource):
    avartar = fields.FileField(attribute = 'avartar', blank=True, null=True)
    class Meta:
        queryset = MyCRM.objects.vendors().order_by('name')
        fields = ['name', 'url']
        filtering = {
            'name': ALL,
        }
        # authentication = ApiKeyAuthentication()
        # authorization = DjangoAuthorization()

class CustomerResource(MyModelResource):
    class Meta:
        queryset = MyCRM.objects.customers().order_by('name')
        # authentication = ApiKeyAuthentication()
        # authorization = DjangoAuthorization()

class SeasonResource(MyModelResource):
    item_count = fields.IntegerField('item_count')
    vendor_count = fields.IntegerField('vendor_count')
    vendors = fields.ListField(attribute='vendors', null = True)
    items = fields.ListField(attribute='items', null = True)

    class Meta:
        queryset = MySeason.objects.all()
        filtering = {
            'name': ['icontains', 'exact']
        }

    def dehydrate_vendors(self, bundle):
        if not 'vendorId' in bundle.request.GET:
            vendors = bundle.data['vendors']
        else:
            vendors = filter(lambda x: x.id==int(bundle.request.GET['vendorId']), bundle.data['vendors'])            
        tmp = []
        for v in vendors:
            if v.avartar:
                tmp.append({'id': v.id,'name': v.name, 'avartar': v.avartar.file.url })
            else:
                tmp.append({'id': v.id,'name': v.name, 'avartar': None })
        return tmp

    def dehydrate_items(self,bundle):
        if 'vendorId' in bundle.request.GET:
            items = filter(lambda x: x.brand.id == int(bundle.request.GET['vendorId']), bundle.data['items'])
            return [{'id': i.id, 'name': i.name, 'color': i.color, 'product_id':i.product_id, 'avartar': i.avartar.thumbnail_base64 if i.avartar else None} for i in items]
        else:
            return []

class ProductResource(MyModelResource):
    brand = fields.ForeignKey(VendorResource, 'brand', full = True)

    # Set full=False. Otherwise, it will return season details, which will involve computing
    # a whole set of derivative values under the MySeason object.
    season = fields.ForeignKey(SeasonResource, 'season', full = False)
    
    currency = fields.ForeignKey(CurrencyResource, 'currency', full = True)
    attachments = fields.ToManyField('erp.api.AttachmentResource', 'attachments', full=True)

    # derivative fields
    product_id = fields.CharField(attribute='product_id', null = False)    
    sizes = fields.ListField(attribute='sizes', blank = True, null = True)
    avartar = fields.FileField(attribute = 'avartar', blank=True, null=True)
    season_name = fields.CharField(attribute='season_name')

    class Meta:
        queryset = MyItem.objects.all()
        # authentication = ApiKeyAuthentication()
        # authorization = DjangoAuthorization()
        allowed_methods = ['get','post']
        filtering = {
            'brand': ALL_WITH_RELATIONS,
            'name': ['icontains'],
            'price': ['lt', 'gt'],
            'season': ALL_WITH_RELATIONS
        }
        fields = ['id','brand','name', 'color','price','season','currency']
        paginator_class = Paginator
        # max_limit = None
        cache = SimpleCache(timeout=100)

    def dehydrate_avartar(self, bundle):
        # Using base64 version avoids the hassle of maintaining media_root server
        return bundle.data['avartar'].thumbnail_base64 if bundle.data['avartar'] else None

    # def apply_authorization_limits(self, request, object_list):
    #     return object_list.filter(name__icontains = 'LEO')

class AttachmentResource(MyModelResource):
    content_object = GenericForeignKeyField({
        MyItem: ProductResource,
    }, 'content_object')    
    class Meta:
        queryset = Attachment.objects.all()
        resource_name = 'attachment'
        fields = ['name', 'description', 'file', 'thumbnail_base64']
        # authentication = ApiKeyAuthentication()
        # authorization = DjangoAuthorization()      