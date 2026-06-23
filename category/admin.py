from django.contrib import admin
from . models import ContactMessage, SubCategory, MainCategory, InsideSubCategory
from import_export.admin import ImportExportModelAdmin


# Register your models here.
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'timestamp')

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1

class InsideSubCategoryInline(admin.TabularInline):
    model = InsideSubCategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}  # auto-fill slug from name


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline]
    list_display = ['name']
    prepopulated_fields = {'slug': ('name', )}


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'main_category']
    prepopulated_fields = {'slug': ('name', )}


@admin.register(InsideSubCategory)
class InsideSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sub_category', 'slug']
    list_filter = ['sub_category__main_category', 'sub_category']
    search_fields = ['name', 'sub_category__name']
    prepopulated_fields = {'slug': ('name',)}

