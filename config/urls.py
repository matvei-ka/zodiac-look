from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('forecast/', include('forecasts.urls')),
    path('api/', include('api.urls')),
    path('wardrobe/', include('wardrobe.urls')),
    path('', include('core.urls')),
]