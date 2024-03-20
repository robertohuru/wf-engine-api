# urls.py
from django.urls import path
from .views import LoginView, SignUpView, UserInfoView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('user-info/', UserInfoView.as_view(), name='user_info'),

]
