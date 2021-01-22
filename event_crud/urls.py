from . import views
from django.urls import path

urlpatterns = [
    path('all/', views.AllEvents.as_view()),
    path('', views.EventView.as_view()),
    path("<uuid:public_id>/", views.EventView.as_view()),
    path('<uuid:public_id>/categories/', views.EventCategory.as_view()),
    path('<uuid:public_id>/address/', views.EventAddress.as_view()),
    path('<uuid:public_id>/cohost/', views.CoHostEventView.as_view()),
    path('<uuid:public_id>/ticket/', views.EventTicketsView.as_view())
]

