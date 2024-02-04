from django.urls import path
from .views import mapa_stocks, signup, signout, signin,  chart_y_datos

urlpatterns = [
    # El home pasa a depender de la app 'News'
    # path('', home, name="home"),

    path('mapa/<str:nombre_bd>', mapa_stocks, name="mapa_stocks"),

    path('signup/', signup, name="signup"),

    path('logout/', signout, name="logout"),

    path('login/', signin, name="login"),

    # Para gráficos y datos
    path('<str:nombre_bd>/<str:ticker>/chart', chart_y_datos, name='chart_y_datos'),
]
