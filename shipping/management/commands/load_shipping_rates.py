import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from shipping.models import Zone, CountryZone, ShippingRate

class Command(BaseCommand):
    help = 'Import shipping zones and rates from CSV files'

    def handle(self, *args, **options):
        # Get the shipping app directory
        shipping_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(shipping_dir, 'data')

        # File paths
        zone_file = os.path.join(data_dir, 'zone_definition.csv')
        economy_file = os.path.join(data_dir, 'economy_rates.csv')
        priority_file = os.path.join(data_dir, 'priority_rates.csv')

        # 1. Create zones A-K
        zones = 'ABCDEFGHIJK'
        for letter in zones:
            Zone.objects.get_or_create(letter=letter)

        # 2. Import Country → Zone mapping
        self.import_country_zones(zone_file)

        # 3. Import Economy rates
        self.import_rates(economy_file, 'economy')

        # 4. Import Priority rates
        self.import_rates(priority_file, 'priority')

        self.stdout.write(self.style.SUCCESS('Shipping data imported successfully'))

    def import_country_zones(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                country = row[0].strip()
                zone_letter = row[1].strip()
                if country == 'Country' or not country:  # skip header
                    continue
                zone = Zone.objects.get(letter=zone_letter)
                CountryZone.objects.get_or_create(
                    country_name=country,
                    defaults={'zone': zone}
                )

    def import_rates(self, filepath, rate_type):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)  # first row as headers: kg, A, B, C, ...
            for row in reader:
                if not row.get('kg'):
                    continue
                weight = float(row['kg'])
                for zone_letter in 'ABCDEFGHIJK':
                    rate_str = row.get(zone_letter)
                    if rate_str and rate_str.strip():
                        try:
                            rate = float(rate_str)
                            zone = Zone.objects.get(letter=zone_letter)
                            ShippingRate.objects.get_or_create(
                                weight=weight,
                                zone=zone,
                                type=rate_type,
                                defaults={'rate': rate}
                            )
                        except ValueError:
                            self.stdout.write(f"Skipping invalid rate: {rate_str}")