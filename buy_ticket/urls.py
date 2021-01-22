from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.StripePayementsView.as_view()),
    path('ticket/', views.TicketView.as_view()),
    path('ticket/<int:public_id>/', views.TicketView.as_view())
]
