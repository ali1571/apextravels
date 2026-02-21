from django.urls import path
from . import views


app_name = 'travelApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('fleet/', views.fleet, name='fleet'),
    path('about/', views.about, name= 'about'),
    path('fleet/<int:vehicle_id>/', views.fleet_vehicle, name='fleet_vehicle'),
    path('gallery/<int:vehicle_id>/', views.vehicle_gallery, name='vehicle_gallery'),



]


