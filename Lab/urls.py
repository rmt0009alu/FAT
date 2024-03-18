"""
URLs para usar con Lab.
"""
from django.urls import path
from .views import lab, arima_parametros_auto, arima_parametros_rejilla

urlpatterns = [
    # El home pasa a depender de la app 'News'
    # path('', home, name="home"),

    path('lab/', lab, name="lab"),

    path('lab/arima_parametros_auto/', arima_parametros_auto, name="arima_parametros_auto"),

    path('lab/arima_parametros_rejilla/', arima_parametros_rejilla, name="arima_parametros_rejilla"),

]