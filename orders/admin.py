from django.contrib import admin
from .models import Payment, Order, OrderProduct
from .forms import OrderProductForm


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    form = OrderProductForm
    readonly_fields = ['payment', 'user', 'product', 'quantity', 'product_price', 'ordered',]
    extra = 0

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'quantity', 'model_number', 'payment']
    form = OrderProductForm


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'ip', 'is_ordered', 'created_at')
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone', ]
    list_per_page = 20
    inlines = [OrderProductInline]
    # form = OrderProductForm

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)

