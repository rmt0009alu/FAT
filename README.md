# FAT: Financial Analysis Tool

![Financial Analysis](static/Portada.jpg)

## Bienvenidos a FAT

Tome decisiones financieras más inteligentes, basadas en información poco convencional y fácil de entender. Los índices bursátiles disponibles son: DJ30, IBEX35, FTSE100 y DAX40. Si es usted desarrollador y quiere añadir nuevos ínidices se recomienda leer la documentación.

Entre las principales funcionalidades que podrá encontrar, destacan las siguientes:

 - Disponer de un área de usuario (DashBoard) para realizar seguimiento de valores y almacenar información relevante sobre su cartera. 
 - Comparación de distribuciones de cartera con gráficas de Markowitz y Sharpe ratio. 
 - Gráficas interactivas de valores. 
 - Comparación con sectores de referencia de valores cotizados. 
 - Disponibilidad de grafos de correlaciones con NetworkX.
 - Experimentación con modelos ARIMA para forecasting de series temporales.  
 - Experimentación con algoritmo de cruce de medias.
 - Experimentación con modelos de regresión y clasificación para realizar forecasting de series temporales. 
 - En caso de que utilice este repositorio podrá utlizar redes LSTM para realizar forecasting de series temporales (funcionalidad no disponible en la web). 


### Get Started

 - ¿Quieres mejorar el control de tus inversiones? [Visita FAT](http://takeiteasy.pythonanywhere.com/).

### Documentación

 - ¿Quieres saber más sobre el código fuente? [Read The Docs](https://fat.readthedocs.io/es/latest/).

## Instalación en local

Aquí se detallan los paso más importantes que hay que dar para utilizar esta herramienta de forma local:

### Paso 1. Descargar repositorio:

Descargar el repositorio [FAT](https://github.com/rmt0009alu/FAT)


### Paso 2. Intalar Python:

Instalar [Python](https://www.python.org/downloads/). 

** Nota: ** Para el desarrollo de esta herramienta se ha trabajado con Python 3.11.5

### Paso 3. Instalar entorno:

Instalar un entorno de desarrollo del gusto del usuario. Se recomienda el uso de [VS Code](https://code.visualstudio.com/download).

### Paso 4. Abrir directorio del respositorio:

Abrir la ruta donde están los archivos del repositorio desde VS Code (o el editor/entorno deseado).

### Paso 5. Entorno virtual:

Crear un entorno virtual en el mismo directorio en el que tengamos los archivos del repositorio:

> python -m venv venv

### Paso 6. Instalar las dependencias en el entorno virtual:

En este proyecto se puede encontrar un archivo requirements.txt con todas las dependencias. Pero para facilitar la instalación se recomienda seguir los siguientes pasos, ya que se instalarán las librerías en el orden adecuado y todas las dependencias de terceros estarán disponibles igualmente:

 - Abrir entorno virtual:

   > .\venv\Scripts\activate

 - Instalar framework, librerías y APIs:

  (venv) > python -m pip install Django
  (venv) > python -m pip install pandas
  (venv) > python -m pip install plotly==5.18.0
  (venv) > python -m pip install newsapi-python
  (venv) > python -m pip install -U matplotlib
  (venv) > python -m pip install mpld3
  (venv) > python -m pip install django-pandas
  (venv) > python -m pip install feedparser
  (venv) > python -m pip install yfinance
  (venv) > python -m pip install python-dotenv
  (venv) > python -m pip install networkx
  (venv) > python -m pip install statsmodels
  (venv) > python -m pip install scikit-learn
  (venv) > python -m pip install pmdarima
  (venv) > python -m pip install tensorflow


### Paso 7. Configurar claves secretas:

Esta herramienta requiere dos claves secretas que no están disponibles pero que son fácilmente conseguibles:
 - Clave SECRET_KEY de Django
 - Clave para conexión a la API de noticias NewsAPI

Aquí se explica cómo conseguirlas y añadirlas al entorno del usuario:

#### Paso 7.1. SECRET_KEY de Django:

Generar una SECRET_KEY de Django de manera aleatoria desde una terminal en el entorno virtual:

> (venv) > python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

Guardar la clave en /FAT/.env.example, sin usar comillas, nos deberá quedar un archivo con el siguiente texto:

 > export SECRET_KEY=clave_larga_6v2_ldx_clave_larga

#### Paso 7.2. Clave de API NewsAPI:

Acceder a [NewsAPI](https://newsapi.org/) y solicitar una clave de acceso con un registro (puede usarse un '10 minute mail' o similar):

Guardar la clave en /FAT/.env.example, sin usar comillas, nos deberá quedar un archivo con el siguiente texto:

 > export SECRET_KEY=clave_larga_6v2_ldx_clave_larga
 > export NEWS_API_KEY=clave_api_123456_clave_api

#### Paso 7.3. Cambiar el nombre de .env.example:

Cambiar el nombre de /FAT/.env.example por /FAT/.env

### Paso 8. Lanzar el servidor:

Como ya tenemos configruado el entorno, sólo queda empezar a utilizarlo:

> (venv) > python .\manage.py runserver

Hacer click en la ruta local que aparece, normalmente: [127.0.0.1:8000](http://127.0.0.1:8000/)

### Paso 9. Dependencias adicionales interesantes:

 - Para limpiar las rutas de _pycache_:

  > (venv) > python -m pip install pyclean        
   
   Modo de uso:
  
  > (venv) > pyclean .
 
 - Para testear el código:

  > (venv) > python -m pip install coverage

  Modos de uso:

  > (venv) > coverage run manage.py test tests
  > (venv) > coverage html

- Para comprobar la calidad del código:

  > (venv) > python -m pip install pylint           # Para medir calidad de código (venv) > pylint .\DashBoard\views.py
  
  Modos de uso:

  > (venv) > pylint .\DashBoard\views.py
  > (venv) > pylint .\DashBoard
  > (venv) > pylint .

- Para crear documentación del estilo de ReadTheDocs:

  > (venv) > python -m pip install sphinx
  > (venv) > python -m pip install sphinxcontrib-django
  > (venv) > python -m pip install sphinx_rtd_theme

  Modo de uso:

  > (venv) > .\make.bat html