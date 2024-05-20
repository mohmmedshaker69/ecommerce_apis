from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Payment)
admin.site.register(NNotification)
admin.site.register(PaymentMethod)
# Register your models here.
