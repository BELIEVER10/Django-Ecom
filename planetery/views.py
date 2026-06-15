# store/views.py (or wherever your home view lives)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Min, Max
from store.models import Product, CarouselItem, WebsiteReview
from store.forms import WebsiteReviewForm
from category.models import LeftBanner, RightBanner, ContactMessage
from category.forms import ContactForm
from django.shortcuts import get_object_or_404

def home(request):
    # ---- existing product queries (unchanged) ----
    products = Product.objects.filter(is_available=True, is_new_arrival=True).order_by('-created_date').annotate(
        min_price=Min('variation__price'),
        max_price=Max('variation__price')
    )
    most_viewed = Product.objects.order_by('-views')[:10].annotate(
        min_price=Min('variation__price'),
        max_price=Max('variation__price')
    )
    left_banner = LeftBanner.objects.first()
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

    # ---- review form handling (new) ----
    if request.method == 'POST' and 'submit_review' in request.POST:
        # Only authenticated users can submit
        if request.user.is_authenticated:
            form = WebsiteReviewForm(request.POST, request.FILES)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                messages.success(request, 'Thank you for sharing your sound journey! Your review has been posted.')
                return redirect('home')  # redirect to home to avoid re‑submission
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('login')
    else:
        form = WebsiteReviewForm()

    # Fetch all reviews for display
    reviews = WebsiteReview.objects.select_related('user').all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    context = {
        'products': products,
        'most_viewed': most_viewed,
        'items': items,
        'left_banner': left_banner,
        'right_banner': right_banner,
        'left_banner_product': left_banner_product,
        'right_banner_product': right_banner_product,
        'review_form': form,          # <-- add form
        'reviews': reviews,           # <-- existing reviews
        'avg_rating': avg_rating,
        'total_reviews': reviews.count(),
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from store.models import WebsiteReview
from store.forms import WebsiteReviewForm

@login_required
def website_reviews(request):
    # Handle form submission
    if request.method == 'POST':
        form = WebsiteReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you for sharing your sound journey! Your review has been posted.')
            return redirect('reviews:website_reviews')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WebsiteReviewForm()

    # Get all reviews with user info
    reviews = WebsiteReview.objects.select_related('user').all()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'form': form,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': reviews.count(),
    }
    return render(request, 'reviews/review_list.html', context)