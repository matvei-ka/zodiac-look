from django.urls import path

from . import views

app_name = 'forecasts'

urlpatterns = [
    path('', views.forecast, name='forecast'),
    path('history/', views.history, name='history'),
]
