from django.contrib import admin
from .models import NewsletterSubscriber

# Register your models here.
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']

admin.site.register(NewsletterSubscriber, NewsLetterAdmin)