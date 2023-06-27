from django.contrib.auth import views as auth_views
from django.urls import include, path

from users import views
from core import views as views_cr

app_name = 'users'

urlpatterns = [
    path('', views_cr.HomePageView.as_view(), name='homepage'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/signup/player/', views.PlayerSignUpView.as_view(), name='player-signup'),
    path('auth/signup/croupier/', views.CroupierSignUpView.as_view(), name='croupier-signup'),
    path('auth/login', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout', auth_views.LogoutView.as_view(), name='logout'),

    path('<int:pk>/profile', views.Profile, name="profile"),
    path('<int:pk>/aggiorna-saldo', views.SaldoUpdate, name='update_saldo'),
    path('<int:pk>/update-profile-pic', views.UpdateProfilePic.as_view(), name='update-profile-pic'),
]
