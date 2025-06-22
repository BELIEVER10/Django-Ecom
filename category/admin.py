from django.contrib import admin
from . models import Category, LeftBanner, RightBanner, ContactMessage, SubCategory, MainCategory
from .resources import CategoryResource
from import_export.admin import ImportExportModelAdmin


# Register your models here.
class CategoryAdmin(ImportExportModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')
    resource_class = CategoryResource

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'timestamp')

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline]
    list_display = ['name']

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'main_category']
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(LeftBanner)
admin.site.register(RightBanner)
