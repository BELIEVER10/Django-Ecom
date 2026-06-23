from .models import CountryZone, ShippingRate
import math

def get_shipping_cost(country_name, total_weight, shipping_type='economy'):
    """
    Returns the shipping cost (Decimal) or None if not found.
    total_weight: float in kg
    shipping_type: 'economy' or 'priority'
    """
    try:
        country_zone = CountryZone.objects.get(country_name__iexact=country_name)
    except CountryZone.DoesNotExist:
        return None   # country not in our list

    zone = country_zone.zone

    # Round up to nearest 0.5 kg (the rate table step)
    # e.g. 2.3 → 2.5, 2.0 → 2.0
    ceil_weight = math.ceil(total_weight * 2) / 2.0

    # Find the rate for this zone and type where weight >= ceil_weight, get the smallest such weight
    rate_obj = ShippingRate.objects.filter(
        zone=zone,
        type=shipping_type,
        weight__gte=ceil_weight
    ).order_by('weight').first()

    if rate_obj:
        return rate_obj.rate
    else:
        # If weight exceeds the maximum in table (300 kg), use the highest rate (weight=300)
        rate_obj = ShippingRate.objects.filter(
            zone=zone,
            type=shipping_type
        ).order_by('-weight').first()
        return rate_obj.rate if rate_obj else None