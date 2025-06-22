from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Product, Variation, CarouselItem

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product

class VariationResource(resources.ModelResource):
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget(Product, 'product_name')
    )
    class Meta:
        model = Variation

class CarouselItemResource(resources.ModelResource):
    class Meta:
        model = CarouselItem