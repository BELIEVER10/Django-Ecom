from django.contrib import admin
from .models import Product, Variation, ProductGallery, WebsiteReview, Gallery, GalleryImage
from .resources import ProductResource, VariationResource
from import_export.admin import ImportExportModelAdmin
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(ImportExportModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'modified_date', 'is_available', 'is_new_arrival', 'views')
    resource_class = ProductResource
    inlines = [ProductGalleryInline]
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(ImportExportModelAdmin):
    list_display = ('product', 'price', 'stock', 'variation_category', 'variation_value', 'weight', 'packaging_weight','model_number', 'is_active')
    list_editable = ('is_active', )
    list_filter = ('product', 'variation_category', 'variation_value')
    resource_class = VariationResource



@admin.register(WebsiteReview)
class WebsiteReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'rating', 'professional_title', 'institution', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'professional_title']
    readonly_fields = ['created_at', 'updated_at']


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3
    fields = ('image', 'title', 'description')   # show description in admin

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]




admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductGallery)