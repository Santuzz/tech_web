
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from casino import settings
from initcmds import init_db, erase_db

urlpatterns = [
                  path('user/', include('users.urls')),
                  path('room/', include('rooms.urls')),
                  path('', include('core.urls')),
                  path('admin/', admin.site.urls),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

erase_db()
init_db()
