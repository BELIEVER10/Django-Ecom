from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, CarouselItem
from category.models import LeftBanner, RightBanner
from category.models import ContactMessage
from category.forms import ContactForm
from django.contrib import messages

def home(request):
    products = Product.objects.filter(is_available=True, is_new_arrival=True).order_by('created_date')
    most_viewed = Product.objects.order_by('-views')[:10]

    left_banner = LeftBanner.objects.first()  # Safe fallback if no banners
    right_banner = RightBanner.objects.first()

    try:
        left_banner_product = Product.objects.get(is_available=True, is_left_banner_offer=True)
    except Product.DoesNotExist:
        left_banner_product = None

    try:
        right_banner_product = Product.objects.get(is_available=True, is_right_banner_offer=True)
    except Product.DoesNotExist:
        right_banner_product = None

    items = CarouselItem.objects.all()

    context = {
        'products': products,
        'most_viewed': most_viewed,
        'items': items,
        'left_banner': left_banner,
        'right_banner': right_banner,
        'left_banner_product': left_banner_product,
        'right_banner_product': right_banner_product,
    }
    return render(request, 'home.html', context)



def event_detail(request, slug):
    event = get_object_or_404(CarouselItem, slug=slug)
    return render(request, 'event_detail.html', {'event': event})


def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

def about_us(request):
    return render(request, 'about_us.html')
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to database
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            # ... (rest of the email sending logic if you still want it)
            messages.success(request, 'Thank you! Your message has been received.')
            return redirect('contact_us')
        # ... (else part for invalid form)
    else:
        form = ContactForm()
    return render(request, 'contact_us.html', {'form': form})

