
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from users.api import UserCreateRetrieveAPI


def user_create_api(request):
    raise NotImplementedError


urlpatterns = [
    # USERS MANAGEMENT
    # ==================
    path("admin/", admin.site.urls),

    path('auth/token/', TokenObtainPairView.as_view()),
    path("users/", UserCreateRetrieveAPI.as_view()),
    # ============================================
    # path("import-dishes/", import_dishes),
    # path("users/", user_create_retrieve),  # GET to retrieve user, POST to create user
    # path(
    #     "users/<id:int>", user_update_delete
    # ),  # PUT to updaste user, DELETE to remove user
    # path("users/password/forgot", password_forgot),  # POST to generate temp UUID key
    # path(
    #     "users/passwordt/change", password_change
    # ),  # POST, receive key and new password
    # AUTH
    # ==================
    # path("auth/token", access_token),  # POST
    # BASKET & ORDERS
    # ==================
    # path("basket/", basket_create),  # POST  -> return ID
    # path("basket/<id:int>", basket_retrieve),  # GET to see all details
    # path(
    #     "basket/<id:int>/dishes/<id:int>", basket_dish_add_update_delete
    # ),  # PUT (change quantity), DELETE, POST (add dish)
    # path("basket/<id:int>/order", order_from_basket),  # POST -> [Order] with ID
    # path(
    #     "orders/<id:int>", order_details
    # ),  # GET (owner, support), PUT (only by SUPPORT)
]
