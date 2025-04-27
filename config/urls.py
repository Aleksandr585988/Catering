from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from food.api import bueno_webhook
from food.api import router as food_router
from users.api import router as users_router
from django.conf.urls.static import static
from django.conf import settings

# def user_create_api(request):
#     raise NotImplementedError

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("auth/token/", TokenObtainPairView.as_view()),
        path("webhooks/bueno/", bueno_webhook, name="bueno_webhook"),
    ]
    + users_router.urls
    + food_router.urls
)

if settings.DEBUG is True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
