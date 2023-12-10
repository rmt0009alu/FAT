"""
URL configuration for FAT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # RECORDAR QUE DJNAGO RECOMIENDA QUE CADA APP TENGA
    # SUS PROPIAS RUTAS URL. Por eso, se crea un "urls.py"
    # en cada una de las apps y se mete esta info
    
    # Al dejarlo en blanco es como indicar que se visita la
    # ruta principal y se lanza hello()
    # path('', hello)
    # path('', views.hello),
    # Para acceder, entrar a http://localhost:8000/about
    # path('about/', views.about)

    path('', include('Analysis.urls')),
    # Las rutas de Analysis van directas desde la página
    # principal, pero si quiero que empiecen desde otra ruta
    # puedo añadir aquí desde donde. P. ej:
    #
    # path('home/', include('miAppDePruebas.urls'))
    #
    # Así, para accederlas habría que poner http://localhost:8000/home
    # o http://localhost:8000/home/about
]
