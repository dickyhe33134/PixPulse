from django.urls import path
from . import views
urlpatterns=[
    
    path('', views.home, name="homepage"),
    path('about/<uuid:userid>/', views.about, name="about"),

]