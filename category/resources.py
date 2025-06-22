from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Category

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category

