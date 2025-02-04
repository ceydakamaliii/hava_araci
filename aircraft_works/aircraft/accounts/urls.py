from django.urls import path

from aircraft.accounts import views

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("v1/users/token/", views.AircraftTokenObtainPairView.as_view(), name="login"),
    path("v1/users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), # Refresh tokenı kullanarak yeni access token almamızı sağlar.
    path("v1/users/token/verify/", TokenVerifyView.as_view(), name="token_verify"), # Access tokenın geçerliliğini kontrol eder.
    path("v1/users/sign-up/", views.SignUpView.as_view(), name="sign_up"),
    path("v1/users/logout/", views.UserLogoutView.as_view(), name="user_logout"),
    path("v1/users/me/", views.MyUserDetailView.as_view(), name="my_user_details"),
]
