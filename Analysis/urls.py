from django.urls import path
from .views import hello, stock_data

urlpatterns = [
     
    path('', hello, name="hello"),

    # Path para acceder a info. de tickers en 
    # una BD (índice bursátil) concreta
    path('<str:nombre_bd>/<str:ticker>/', stock_data, name='stock_data'),
    
]
