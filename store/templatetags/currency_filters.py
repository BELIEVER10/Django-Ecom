from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def convert_price(context, price_usd):
    rates = context.get('exchange_rates', {})
    currency = context.get('current_currency', 'USD')
    rate = rates.get(currency, 1.0)
    converted = round(price_usd * rate, 2)
    return converted
