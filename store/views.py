from django.shortcuts import render, get_object_or_404
from .models import Product, Variation, ProductGallery
from category.models import Category
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .templatetags import currency_filters
from .utils.currency import get_currency_symbol, get_exchange_rates
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count
from carts.models import Wishlist
from django.db.models import Max, Min

# Create your views here.

from category.models import SubCategory



def store_by_subcategory(request, subcategory_slug):
    subcategory = SubCategory.objects.get(slug=subcategory_slug)
    products = Product.objects.filter(sub_category=subcategory).annotate(
    min_price=Min('variation__price'),
    max_price=Max('variation__price'))
    product_count = products.count()
    return render(request, 'store/store.html', {'products': products, 'product_count': product_count, 'category_slug': subcategory_slug})


def store(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date').annotate(
    min_price=Min('variation__price'),
    max_price=Max('variation__price'))
    
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product__id', flat=True)
    else:
        wishlist_products = []

    
    context = {
        'products': paged_products,
        'product_count': product_count,
        'wishlist_products': wishlist_products,

        
    }
    return render(request, 'store/store.html', context)



def product_detail(request, subcategory_slug=None, product_slug=None):
    product = Product.objects.filter(
    sub_category__slug=subcategory_slug,
    slug=product_slug).annotate(
    min_price=Min('variation__price'),
    max_price=Max('variation__price')).get()
    id = product.id
    product_without_variation = Product.objects.annotate(variation_count=Count('variation')).filter(id=id, variation_count=0).first()
  
    # product = Product.objects.get(slug=product_slug)

    
    # Increment views
    product.views += 1
    product.save()
    print("View count updated for:", product.product_name, "| Views:", product.views)

    size_variations= Variation.objects.filter(product__id=id, variation_value__isnull=False).exclude(variation_value='')
    selected_size = request.POST.get('size')
    model_number = None
    sub_desc = None
    price = None

    try:
        if selected_size:
            variation = product.variation_set.filter(variation_value__iexact=selected_size).first()
            if variation:
                model_number = variation.model_number
                sub_desc = variation.sub_description
                price = variation.price
        elif product_without_variation:
            model_number = ""
            sub_desc = ""
            price = ""
        else:
            variation = Variation.objects.get(product__id=id)
            model_number = variation.model_number
            sub_desc = variation.sub_description
            price = variation.price
    except MultipleObjectsReturned:
        model_number = ""
        sub_desc = ""
        price = ""

    #Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=product.id)


    context = {
        'product': product,
        'model_number': model_number,
        'price':price,
        'sub_description': sub_desc,
        'selected_size': selected_size,
        'size_variations': size_variations,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)
    

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'product_count' : product_count,
        'products': products,

    }

    return render(request, 'store/store.html', context)


from django.shortcuts import redirect

def set_currency(request, currency):
    request.session['currency'] = currency
    return redirect(request.META.get('HTTP_REFERER', '/'))  # go back to previous page


def price_search(request, category_slug=None):
    # Get min and max prices from the query parameters
    min_price = request.GET.get('min_price', 0)  # Default to 0 if not provided
    max_price = request.GET.get('max_price', None)  # Default to None if not provided

    #change the min_price and max_price rate according to currency


    # Get the current currency and exchange rates
    currency = request.session.get('currency', 'USD')  # Get currency from session or default to USD
    exchange_rates = get_exchange_rates()  # Get the exchange rates (cached or fetched)
    
    # Get the exchange rate for the selected currency
    rate = exchange_rates.get(currency, 1.0)
    # print("The rate is:", rate)

    # Convert the min_price and max_price to USD
    min_price_in_usd = float(min_price)/rate
    print("The min_price_in_usd", min_price_in_usd)
    max_price_in_usd = float(max_price)/rate


    if category_slug != None:
        products = Product.objects.filter(sub_category__slug=category_slug, price__gte=min_price_in_usd , price__lte=max_price_in_usd)
    else:
        products = Product.objects.filter(price__gte=min_price_in_usd , price__lte=max_price_in_usd)

    product_count = products.count()
    

    # Prepare the context for rendering
    context = {
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
        'product_count': product_count,
        'category_slug': category_slug,

        
    }
    return render(request, 'store/store.html', context)
