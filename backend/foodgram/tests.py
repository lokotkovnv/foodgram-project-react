from http import HTTPStatus

from django.test import Client, TestCase
from foodgram.models import Ingredient, Recipe, Tag, User


class FoodgramAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='test', password='12345', first_name='test',
            last_name='test', email='test@test.com')
        self.ingredient = Ingredient.objects.create(
            name='test', measurement_unit='test'
        )
        self.tag = Tag.objects.create(
            name='test', color='#000000', slug='slug'
        )
        self.recipe = Recipe.objects.create(
            author=self.user, name='test', text='test', cooking_time=2
        )
        self.recipe.ingredients.add(self.ingredient)
        self.recipe.tags.add(self.tag)

    def test_recipe_list(self):
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipe_detail(self):
        response = self.client.get(f'/api/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
