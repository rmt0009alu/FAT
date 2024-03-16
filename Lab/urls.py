"""
URLs para usar con Lab.
"""
from django.urls import path
from .views import lab, arima

urlpatterns = [
    # El home pasa a depender de la app 'News'
    # path('', home, name="home"),

    path('lab/', lab, name="lab"),

    path('lab/arima/', arima, name="arima"),

]