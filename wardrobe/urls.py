from django.urls import path

from . import views

app_name = 'wardrobe'

urlpatterns = [
    path('', views.wardrobe_list, name='wardrobe_list'),
    path('add/', views.item_add, name='item_add'),
    path('<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('stylist/', views.stylist, name='stylist'),
    path('looks/', views.look_list, name='look_list'),
    path('looks/<int:pk>/save/', views.look_save, name='look_save'),
    path('looks/<int:pk>/delete/', views.look_delete, name='look_delete'),
]
