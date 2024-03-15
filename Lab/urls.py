"""
URLs para usar con Lab.
"""
from django.urls import path
from .views import lab

urlpatterns = [
    # El home pasa a depender de la app 'News'
    # path('', home, name="home"),

    path('lab/', lab, name="lab"),

]