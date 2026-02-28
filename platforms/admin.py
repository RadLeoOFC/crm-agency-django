from django.contrib import admin

# Register your models here.
from .models import Platform, Client, PriceList, Slot, Booking, PromoCode, PromoRedemption, PriceListRule, PriceOverride

admin.site.register(Platform)
admin.site.register(Client)
admin.site.register(PriceList)
admin.site.register(Slot)
admin.site.register(Booking)
admin.site.register(PromoCode)
admin.site.register(PromoRedemption)
admin.site.register(PriceListRule)
admin.site.register(PriceOverride)