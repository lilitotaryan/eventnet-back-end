from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('verify_email/', views.EmailVerification.as_view()),
    path('categories/', views.get_all_categories),
    path('forgot_password/<int:ot_token>/<str:email>/', views.ForgotPasswordView.as_view()),
    path('forgot_password/<str:email>/', views.ForgotPasswordView.as_view()),
    path('stripe/', views.StripeAuthView.as_view())
]

