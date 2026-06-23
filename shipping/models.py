from django.db import models

class Zone(models.Model):
    letter = models.CharField(max_length=1, unique=True)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.letter

class CountryZone(models.Model):
    country_name = models.CharField(max_length=100, unique=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.country_name} → Zone {self.zone.letter}"

class ShippingRate(models.Model):
    TYPE_CHOICES = (
        ('economy', 'Economy'),
        ('priority', 'Priority'),
    )
    weight = models.FloatField(help_text="Weight in kg (exact value from the rate table)")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ('weight', 'zone', 'type')
        ordering = ['type', 'zone', 'weight']

    def __str__(self):
        return f"{self.type} | Zone {self.zone.letter} | {self.weight}kg → ${self.rate}"