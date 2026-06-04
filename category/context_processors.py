from .models import Category, MainCategory

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def categories_dropdown(request):
    main_categories = MainCategory.objects.prefetch_related(
        'subcategories__insidesubcategories'
    ).all()
    return {'main_categories': main_categories}