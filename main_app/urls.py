"""EventNet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    # path('jet/', include('jet.urls', 'jet')),
    path('auth/', include('authentication.urls')),
    path('user/', include('user_crud.urls')),
    path('event/', include('event_crud.urls')),
    path('payment/', include('buy_ticket.urls')),
    path('subscribe/', include('subscribe.urls'))
    ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "EventNet Admin"
admin.site.site_title = "EventNet Admin Portal"
admin.site.index_title = "Welcome to EventNet Admin Portal"