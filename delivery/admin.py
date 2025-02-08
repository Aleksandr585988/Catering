from django.contrib import admin

from .models import DeliveryDishesOrder


@admin.register(DeliveryDishesOrder)
class DeliveryDishesOrderAdmin(admin.ModelAdmin):
    pass
