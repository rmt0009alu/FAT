from django.urls import path
from .views import *

urlpatterns = [
     
    path('', home, name="home"),

    path('mapa/', mapa_stocks, name="mapa_stocks"),

    path('signup/', signup, name="signup"),

    path('logout/', sigout, name="logout"),

    path('login/', signin, name="login"),

    # Path para acceder a info. de tickers en 
    # una BD (índice bursátil) concreta. 
    # Para sólo datos
    path('<str:nombre_bd>/<str:ticker>/', stock_data, name='stock_data'),
    # Para gráficos
    path('<str:nombre_bd>/<str:ticker>/chart', stock_chart, name='stock_chart'),
    
] 
