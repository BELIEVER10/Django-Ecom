from django import forms
from .models import CartItem
from store.models import Variation  # import from the correct app

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CartItemForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.product:
            self.fields['variation'].queryset = Variation.objects.filter(product=self.instance.product)
        else:
            self.fields['variation'].queryset = Variation.objects.none()
