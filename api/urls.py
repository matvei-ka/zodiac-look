from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('forecast/', views.forecast, name='forecast'),
]