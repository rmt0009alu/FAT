from django.urls import path
# Ojo, en server no se puede usar *, hay que indicar los métodos
from .views import home

urlpatterns = [

    path('', home, name="home"),

] 
