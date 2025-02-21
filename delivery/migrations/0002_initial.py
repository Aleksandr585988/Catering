# Generated by Django 5.1.5 on 2025-02-21 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("delivery", "0001_initial"),
        ("food", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverydishesorder",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="food.dishesorder"
            ),
        ),
    ]
