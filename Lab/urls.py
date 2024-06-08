"""
URLs para usar con Lab.
"""
from django.urls import path
from .views import lab, buscar_paramateros_arima, arima_auto, arima_rejilla, arima_manual, lstm
from .views import cruce_medias, estrategia_machine_learning

urlpatterns = [
    # El home pasa a depender de la app 'News'
    # path('', home, name="home"),

    path('lab/', lab, name="lab"),

    path('lab/buscar_paramateros_arima/', buscar_paramateros_arima, name="buscar_paramateros_arima"),

    path('lab/arima_auto/', arima_auto, name="arima_auto"),

    path('lab/arima_rejilla/', arima_rejilla, name="arima_rejilla"),

    path('lab/arima_manual/', arima_manual, name="arima_manual"),

    path('lab/lstm/', lstm, name="lstm"),

    path('lab/cruce_medias/', cruce_medias, name="cruce_medias"),

    path('lab/estrategia_ML/', estrategia_machine_learning, name="estrategia_ML"),
]
