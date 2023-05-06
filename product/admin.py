from django.contrib import admin
from product.models import Address
from product.models import Order
from product.models import Coupon
from product.models import Banner
from store.models import Account
# Register your models here.
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(Account)
admin.site.register(Banner)