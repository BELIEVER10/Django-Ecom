from django import forms
from .models import Order, OrderProduct

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note',]



from store.models import Variation  # import from the correct app

class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OrderProductForm, self).__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, 'product') and self.instance.product:
            self.fields['variation'].queryset = Variation.objects.filter(product=self.instance.product)
        else:
            self.fields['variation'].queryset = Variation.objects.none()


