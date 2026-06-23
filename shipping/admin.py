from django.contrib import admin
from .models import Zone, CountryZone, ShippingRate

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('letter', 'name')

@admin.register(CountryZone)
class CountryZoneAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'zone')
    search_fields = ('country_name',)

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('type', 'zone', 'weight', 'rate')
    list_filter = ('type', 'zone')
    search_fields = ('zone__letter',)