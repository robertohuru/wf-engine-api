# urls.py
from django.urls import path
from .views import LoginView, SignUpView, UserInfoView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('user-info/', UserInfoView.as_view(), name='user_info'),

]
