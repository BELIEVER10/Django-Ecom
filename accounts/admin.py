from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.templatetags.static import static

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_name','last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-date_joined',)



class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture and hasattr(object.profile_picture, 'url'):
            img_url = object.profile_picture.url
        else:
            img_url = static('images/default_profile_pic.png')  # path inside your static folder
        return format_html('<img src="{}" width="30" style="border-radius:50%;">', img_url)

    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')



admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

