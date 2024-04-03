import os

import django
import pandas as pd
from foodgram.models import Ingredient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()


class LoadData:

    def load_ingredients_from_csv(self):
        csv_file = os.path.join('data', 'ingredients.csv')
        if not os.path.exists(csv_file):
            print('CSV file does not exist')
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
                print(f'Successfully created {ingredient}')
            else:
                print(f'{ingredient} already exists')


if __name__ == "__main__":
    loader = LoadData()
    loader.load_ingredients_from_csv()
