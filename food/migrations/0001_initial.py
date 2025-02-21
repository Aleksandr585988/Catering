# Generated by Django 5.1.5 on 2025-02-21 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Dish",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, null=True)),
                ("price", models.IntegerField()),
            ],
            options={
                "verbose_name_plural": "dishes",
                "db_table": "dishes",
            },
        ),
        migrations.CreateModel(
            name="DishesOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("external_order_id", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "dishes orders",
                "db_table": "dishes_orders",
            },
        ),
        migrations.CreateModel(
            name="DishOrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.SmallIntegerField()),
            ],
            options={
                "db_table": "dish_order_items",
            },
        ),
        migrations.CreateModel(
            name="Restaurant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("address", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "db_table": "restaurants",
            },
        ),
    ]
