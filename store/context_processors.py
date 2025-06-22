from .utils.currency import get_currency_symbol, get_exchange_rates
from carts.models import Wishlist

def currency_context(request):
    currency = request.session.get('currency', 'USD')
    symbol = get_currency_symbol(currency)
    rates = get_exchange_rates()

    return {
        'current_currency': currency,
        'currency_symbol': symbol,
        'exchange_rates': rates,
    }

def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
        return {'wishlist_count': count}
    return {}

