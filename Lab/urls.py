"""
URLs para usar con Lab.
"""
from django.urls import path
from .views import lab, arima_auto, arima_rejilla, arima_manual

urlpatterns = [
    # El home pasa a depender de la app 'News'
    # path('', home, name="home"),

    path('lab/', lab, name="lab"),

    path('lab/arima_auto/', arima_auto, name="arima_auto"),

    path('lab/arima_rejilla/', arima_rejilla, name="arima_rejilla"),

    path('lab/arima_manual/', arima_manual, name="arima_manual"),

]