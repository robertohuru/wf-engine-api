from django.urls import path, include


urlpatterns = [
    path("services/", include("services.urls")),
    path("auth/", include("account.urls")),
]
