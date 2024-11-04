from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from user.views import EmailConfirm

urlpatterns = [
    path("api/v1/", include("djoser.urls")),
    path("api/v1/", include("djoser.urls.jwt")),
    path("admin/", admin.site.urls),
    path("api/v1/tickets/", include("ticket.urls")),
    path("api/v1/admin/", include("user.urls")),
    path("api/v1/chart/", include("chart.urls")),
    path("api/v1/payments/", include("payments.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
