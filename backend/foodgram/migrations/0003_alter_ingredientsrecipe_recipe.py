# Generated by Django 3.2.3 on 2024-03-01 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0002_alter_ingredientsrecipe_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
    ]
