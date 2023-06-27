from django.urls import include, path

from . import views
from core import views as views_cr

app_name = 'rooms'

urlpatterns = [
    path('', views_cr.HomePageView.as_view(), name='homepage'),
    path('search', views.search_room, name='room-search'),
    path('<int:pk>/detail', views.room_overview, name='room-overview'),
    path('<int:pk>/detail', views.room_signup, name='room-signup'),

    path('create/<int:user_id>', views.CreateRoom.as_view(), name='create-room'),
    path('update/<int:room_pk>/<int:croupier_pk>', views.room_update, name='update-room'),
    path('delete/<int:room_pk>/<int:croupier_pk>', views.room_delete, name='delete-room'),
]
