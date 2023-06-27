from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
]
