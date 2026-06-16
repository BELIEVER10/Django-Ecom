from django.contrib import admin
from django import forms  # <-- added
from .models import Product, CarouselItem, Variation, ProductGallery, WebsiteReview, Gallery, GalleryImage
from .resources import ProductResource, VariationResource, CarouselItemResource
from import_export.admin import ImportExportModelAdmin
import admin_thumbnails

# ----- Custom form for ProductGallery inline -----
class ProductGalleryInlineForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = ('image', 'variation')

    def save(self, commit=True):
        instance = super().save(commit=False)
        # If a variation is selected and product is not set, set it from variation
        if instance.variation and not instance.product_id:
            instance.product = instance.variation.product
        if commit:
            instance.save()
        return instance

# ----- Inline with custom form -----
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    form = ProductGalleryInlineForm   # use custom form
    extra = 1
    fields = ('image', 'variation')

# ----- ProductAdmin -----
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'modified_date', 'is_available', 'is_new_arrival', 'views')
    resource_class = ProductResource
    inlines = [ProductGalleryInline]
    prepopulated_fields = {'slug': ('product_name',)}

# ----- VariationAdmin -----
class VariationAdmin(ImportExportModelAdmin):
    list_display = ('product', 'price', 'stock', 'variation_category', 'variation_value', 'model_number', 'is_active')
    list_editable = ('is_active', )
    list_filter = ('product', 'variation_category', 'variation_value')
    resource_class = VariationResource
    inlines = [ProductGalleryInline]   # reuses the same inline

# ----- CarouselAdmin -----
class CarouselAdmin(ImportExportModelAdmin):
    resource_class = CarouselItemResource

# ----- WebsiteReviewAdmin -----
@admin.register(WebsiteReview)
class WebsiteReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'rating', 'professional_title', 'institution', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'professional_title']
    readonly_fields = ['created_at', 'updated_at']

# ----- GalleryImageInline and GalleryAdmin -----
class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3
    fields = ('image', 'title', 'description')

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]

# ----- Register models -----
admin.site.register(Product, ProductAdmin)
admin.site.register(CarouselItem, CarouselAdmin)
admin.site.register(Variation, VariationAdmin)
# admin.site.register(ProductGallery)   # already included via inlines