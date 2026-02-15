from django.urls import path
from . import views


app_name = 'travelApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('fleet/', views.fleet, name='fleet'),
    path('about/', views.about, name= 'about'),

]