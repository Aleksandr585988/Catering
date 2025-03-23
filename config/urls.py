
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from food.api import bueno_webhook
from users.api import router as users_router
from food.api import router as food_router


# def user_create_api(request):
#     raise NotImplementedError


urlpatterns = ([
    # USERS MANAGEMENT
    # ==================
    path("admin/", admin.site.urls),
    path('auth/token/', TokenObtainPairView.as_view()),
    path("webhooks/bueno/", bueno_webhook),

] + users_router.urls 
  + food_router.urls)
