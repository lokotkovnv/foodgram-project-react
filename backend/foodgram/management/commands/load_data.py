import os

import pandas as pd
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from CSV file'

    def handle(self, *args, **options):
        csv_file = os.path.join('data', 'ingredients.csv')
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR('CSV file does not exist'))
            return

        df = pd.read_csv(
            csv_file, names=['name', 'measurement_unit'], header=None
        )

        for index, row in df.iterrows():
            ingredient, created = Ingredient.objects.get_or_create(
                name=row['name'].strip(),
                measurement_unit=row['measurement_unit'].strip(),
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {ingredient}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'{ingredient} already exists')
                )
