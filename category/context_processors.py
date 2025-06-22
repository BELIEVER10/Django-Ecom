from .models import Category, MainCategory

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def categories_dropdown(request):
    categories = MainCategory.objects.prefetch_related('subcategories')
    return {'main_categories': categories}