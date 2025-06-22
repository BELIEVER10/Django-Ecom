from django.contrib import admin
from .models import Product, CarouselItem, Variation, ProductGallery
from .resources import ProductResource, VariationResource, CarouselItemResource
from import_export.admin import ImportExportModelAdmin
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(ImportExportModelAdmin):
    prepopulated_fields = {'slug': ('product_name', )}
    list_display = ('product_name', 'price', 'stock', 'modified_date', 'is_available', 'is_new_arrival', 'views')
    resource_class = ProductResource
    inlines = [ProductGalleryInline]

class VariationAdmin(ImportExportModelAdmin):
    list_display = ('product', 'price', 'variation_category', 'variation_value', 'model_number', 'is_active')
    list_editable = ('is_active', )
    list_filter = ('product', 'variation_category', 'variation_value')
    resource_class = VariationResource

class CarouselAdmin(ImportExportModelAdmin):
    resource_class = CarouselItemResource


admin.site.register(Product, ProductAdmin)
admin.site.register(CarouselItem, CarouselAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductGallery)
