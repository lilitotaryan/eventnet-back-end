from . import views
from django.urls import path

urlpatterns = [
    path('', views.User.as_view()),
    path('categories/', views.UserCategory.as_view()),
    path('address/', views.UserAddress.as_view()),
    path('reset_password/', views.ResetPassword.as_view())
]

