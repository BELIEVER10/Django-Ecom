from django.core.cache import cache
import requests

def get_currency_symbol(code):
    return {
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }.get(code.upper(), '$')

def get_exchange_rates():
    # Try to get from cache
    cached_rates = cache.get('exchange_rates')
    if cached_rates:
        return cached_rates

    # If not cached, fetch from API
    try:
        response = requests.get('https://api.frankfurter.app/latest?from=USD&to=EUR,GBP')
        rates = response.json().get('rates', {})
        exchange_rates = {
            'USD': 1.0,
            'EUR': rates.get('EUR', 1.0),
            'GBP': rates.get('GBP', 1.0),
        }

        # Cache the result for 1 hour (3600 seconds)
        cache.set('exchange_rates', exchange_rates, timeout=3600)
        return exchange_rates
    except Exception:
        # Fallback static values if API fails
        return {'USD': 1.0, 'EUR': 0.9, 'GBP': 0.8}
