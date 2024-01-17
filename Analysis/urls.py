from django.urls import path
# Ojo, en server no se puede usar *, hay que indicar los métodos
from .views import signup, signout, signin, chart_y_datos, mapa_stocks

urlpatterns = [

    # path('', home, name="home"),

    path('mapa/<str:nombre_bd>', mapa_stocks, name="mapa_stocks"),

    path('signup/', signup, name="signup"),

    path('logout/', signout, name="logout"),

    path('login/', signin, name="login"),

    # Para gráficos y datos
    path('<str:nombre_bd>/<str:ticker>/chart', chart_y_datos, name='chart_y_datos'),
    
] 
