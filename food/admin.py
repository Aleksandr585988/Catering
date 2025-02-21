from django.contrib import admin
from django.http.response import HttpResponseRedirect
from .models import Dish, Restaurant, DishesOrder, DishOrderItem


def import_csv(self, request, queryset):
    print("testing import CSV custom action")
    return HttpResponseRedirect("/import-dishes")


admin.site.add_action(import_csv)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name",)


# admin.site.register(Dish)
@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "restaurant")
    search_fields = ("name",)
    list_filter = ("name", "restaurant")
    actionss = ("import_csv",)


# admin.site.register(DishOrderItem)
class DishOrderItemInline(admin.TabularInline):
    model = DishOrderItem


@admin.register(DishesOrder)
class DishesOrderAdmin(admin.ModelAdmin):
    list_display = ("external_order_id", "user")
    list_filter = ("user",)
    search_fields = ("external_order_id",)
    inlines = [DishOrderItemInline]


@admin.register(DishOrderItem)
class DishOrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "dish", "quantity")
    list_filter = ("order", "dish")
    search_fields = ("order__external_order_id", "dish__name")
