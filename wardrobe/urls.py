from django.urls import path
from . import views

app_name = 'wardrobe'

urlpatterns = [
    path('', views.wardrobe_list, name='wardrobe_list'),
    path('stylist/', views.stylist, name='stylist'),
]