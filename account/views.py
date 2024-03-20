# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .forms import SignupForm
from .models import User


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            refresh = response.data['refresh']
            access = response.data['access']
            response.data['refresh_expires_in'] = RefreshToken(
                refresh).access_token.lifetime.total_seconds()

            token = AccessToken(access)
            user_id = token.payload['user_id']
            user = self.get_user_by_id(user_id)
            response.data['access_expires_in'] = token.lifetime.total_seconds()
            response.data['user'] = {
                'user_id': user.id, 'username': user.username, 'fullname': user.fullname}
        return response

    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


class SignUpView(APIView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.data)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            return Response({'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Invalid data', 'msgs': form.errors.as_json()}, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'user_id': user.id, 'username': user.username, 'fullname': user.fullname})
