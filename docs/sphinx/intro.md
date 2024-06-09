# ![Financial Analysis](/logo.png) FAT: Financial Analysis Tool 



## <u>Bienvenidos a FAT</u>

Tome decisiones financieras más inteligentes, basadas en información poco convencional y fácil de entender. Los índices bursátiles disponibles son: DJ30, IBEX35, FTSE100 y DAX40. Si es usted desarrollador y quiere añadir nuevos índices se recomienda leer la documentación.

Entre las principales funcionalidades que podrá encontrar, destacan las siguientes:

 - Disponer de un área de usuario para realizar _seguimiento de valores_ y _almacenar información relevante sobre su cartera_.
 - Comparación de distribuciones de cartera con gráficas de _Markowitz_ y _Sharpe ratio_.
 - Gráficas interactivas de valores. 
 - Comparación con _sectores de referencia_ de valores cotizados. 
 - Disponibilidad de _grafos de correlaciones con NetworkX_.
 - Experimentación con _modelos ARIMA_ para forecasting de series temporales.  
 - Experimentación con algoritmo de _cruce de medias_.
 - Experimentación con _modelos de regresión y clasificación_ para realizar forecasting de series temporales. 
 - En caso de que utilice este repositorio podrá utlizar _redes LSTM_ para realizar forecasting de series temporales (funcionalidad no disponible en la web). 


## <u>Empieza a controlar tus inversiones</u>

- ¿Quieres mejorar el control de tus inversiones? [Visita FAT](http://takeiteasy.pythonanywhere.com/).

## <u>Documentación</u>

- ¿Quieres saber más sobre el código fuente? [Read The Docs](https://fat.readthedocs.io/es/latest/).

## <u>Instalación en local</u>

Aquí se detallan los paso más importantes que hay que dar para utilizar esta herramienta de forma local:

### Paso 1. Descargar repositorio:

 - Descargar el repositorio [FAT](https://github.com/rmt0009alu/FAT)

 
### Paso 2. Intalar Python:

 - Instalar [Python](https://www.python.org/downloads/). 

   Para el desarrollo de esta herramienta se ha trabajado con `Python 3.11.5`.


### Paso 3. Instalar entorno:

 - Instalar un entorno de desarrollo del gusto del usuario. Se recomienda el uso de [VS Code](https://code.visualstudio.com/download).


### Paso 4. Abrir directorio del respositorio:

 - Abrir la ruta donde están los archivos del repositorio desde VS Code (o el editor/entorno deseado).


### Paso 5. Entorno virtual:

 - Crear un entorno virtual en el mismo directorio en el que tengamos los archivos del repositorio:

   `> python -m venv venv`

### Paso 6. Instalar las dependencias en el entorno virtual:

En este proyecto se puede encontrar un archivo requirements.txt con todas las dependencias. Pero para facilitar la instalación se recomienda seguir los siguientes pasos, ya que se instalarán las librerías en el orden adecuado y todas las dependencias de terceros estarán disponibles igualmente:

- Abrir entorno virtual:

  `> .\venv\Scripts\activate`

- Instalar framework, librerías y APIs:

  `(venv) > python -m pip install Django`<br>
  `(venv) > python -m pip install pandas`<br>
  `(venv) > python -m pip install plotly==5.18.0`<br>
  `(venv) > python -m pip install newsapi-python`<br>
  `(venv) > python -m pip install -U matplotlib`<br>
  `(venv) > python -m pip install mpld3`<br>
  `(venv) > python -m pip install django-pandas`<br>
  `(venv) > python -m pip install feedparser`<br>
  `(venv) > python -m pip install yfinance`<br>
  `(venv) > python -m pip install python-dotenv`<br>
  `(venv) > python -m pip install networkx`<br>
  `(venv) > python -m pip install statsmodels`<br>
  `(venv) > python -m pip install scikit-learn`<br>
  `(venv) > python -m pip install pmdarima`<br>
  `(venv) > python -m pip install tensorflow`

### Paso 7. Configurar claves secretas:

Esta herramienta requiere dos claves secretas que no están disponibles pero que son fácilmente conseguibles.

Aquí se explica cómo conseguirlas y añadirlas al entorno del usuario:

 - **Paso 7.1. SECRET_KEY de Django:**

   Generar una `SECRET_KEY` de Django de manera aleatoria desde una terminal en el entorno virtual:

   `(venv) > python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

   Guardar la clave en `/FAT/.env.example`, sin usar comillas, nos deberá quedar un archivo con el siguiente texto:

   `export SECRET_KEY=clave_larga_6v2_ldx_clave_larga`

 - **Paso 7.2. Clave de API NewsAPI:**

   Acceder a [NewsAPI](https://newsapi.org/) y solicitar una clave de acceso con un registro (puede usarse un '10 minute mail' o similar):

   Guardar la clave en /FAT/.env.example, sin usar comillas, nos deberá quedar un archivo con el siguiente texto:

   `export SECRET_KEY=clave_larga_6v2_ldx_clave_larga`<br>
   `export NEWS_API_KEY=clave_api_123456_clave_api`

 - **Paso 7.3. Cambiar el nombre de .env.example:**

   Cambiar el nombre de `/FAT/.env.example` por `/FAT/.env`


### Paso 8. Lanzar el servidor:

- Como ya tenemos configruado el entorno, sólo queda empezar a utilizarlo:

  `(venv) > python .\manage.py runserver`

  Hacer click en la ruta local que aparece, normalmente: [127.0.0.1:8000](http://127.0.0.1:8000/)


### Paso 9. ¿Quieres actualizar las bases de datos?

 - Es posible actualizar las bases de datos de los índices bursátiles y sus valores cotizados, 
   para tener información con precios de cierre de la última sesión disponible. 

   Es **IMPORTANTE** que antes de actualizar compruebes que el servidor no está activo. 

   Una vez realizada la comprobación previa, puedes lanzar el script `ActualizarBDs.py`
   desde la ruta principal del proyecto:

   `(venv) > python .\util\ActualizarBDs.py`
   
   Este script permite actualizar las bases de datos _dj30_, _ibex35_, _ftse100_ y _dax40_ con precios 
   de cierre. **PARA QUE SE OBTENGAN PRECIOS DE CIERRE ES NECESARIO ACTUALIZAR FUERA DE HORARIOS DE COTIZACIÓN**. 
   Es decir, necesitamos que los mercados estén cerrados y, por ello, en el script
  `ActualizarBDs.py` se ha configurado un rango de horas permitidas. Esto está pensado para 
   trabajar en un servidor remoto que lanza el script de forma automática (con cron, por ejemplo), pero
   si se quieren modificar las horas es cuestión de cambiar los horarios en el 
   método `_permite_actualizar(logger)`.

   Se recomienda hacer actualizaciones en fines de semana o en horarios en los que tanto mercados estadounidenses como europeos estén cerrados. 


### Paso 10. ¿Quieres crear las bases de datos desde cero?

  - Es posible eliminar las bases de datos actuales y crearlas desde cero si se desea, por ejemplo, limpiar toda la 
  información de la base de datos por defecto o si se quiere ampliar la cantidad de datos históricos de los índices
  bursátiles. 
  
    Para realizar esta operación hay que eliminar las migraciones previas:

    `(venv) > python .\manage.py migrate Analysis zero`<br>
    `(venv) > python .\manage.py migrate DashBoard zero`
  
    Además de los comandos anteriores es altamente recomendable eliminar los archivos /Analysis/migrations/0001_initial.py
    y /DashBoard/migrations/0001_initial.py

    Con las migraciones eliminadas, el siguiente paso es eliminar las bases de datos del directorio /databases.

    Posteriormente ya podremos crear las nuevas migraciones con:

    `(venv) > python manage.py makemigrations`<br>
    `(venv) > python manage.py migrate`<br>
    `(venv) > python manage.py migrate --database=dj30`<br>
    `(venv) > python manage.py migrate --database=ibex35`<br>
    `(venv) > python manage.py migrate --database=ftse100`<br>
    `(venv) > python manage.py migrate --database=dax40`

    Por último, hay que lanzar el script `CrearBDs.py`, asegurnándonos, como se indica en el paso 9, de no tener el 
    servidor activo y de que los mercados bursátiles están cerrados:

    `(venv) > python .\util\CrearBDs.py`


### Paso 11. ¿Quieres crear un usuario administrador?

  - Los usuarios administradores en Django tienen la capacidad de gestionar información de la plataforma en un entorno
  visual agradable, pudiendo crear, eliminar y modificar objetos. 
  
    Lo que el administrador podrá modificar depende de la configuración establecida en los archivos `admin.py` de las diferentes aplicaciones.

    Para crear un _admin_ sólo hay que lanzar el siguiente comando:

    `(venv) > python manage.py createsuperuser`


### Opcional. Dependencias adicionales interesantes:

  - Para limpiar las rutas de `_pycache_`:

    `(venv) > python -m pip install pyclean`
  
    Modo de uso:
  
    `(venv) > pyclean .`


  - Para testear el código:

    `(venv) > python -m pip install coverage`

    Modo de uso:

    `(venv) > coverage run manage.py test tests`<br>
    `(venv) > coverage html`
    
    Consular el informe generado en /htmlcov/index.html


  - Para realizar tests de interfaz:

    `(venv) > python -m pip install selenium`

    Modo de uso:

    `(venv) > python .\manage.py test .\tests\tests_ui`


  - Para comprobar la calidad del código:

    `(venv) > python -m pip install pylint`
  
    Modos de uso:
  
    `(venv) > pylint .\DashBoard\views.py`<br>
    `(venv) > pylint .\DashBoard`<br>
    `(venv) > pylint .`<br>


  - Para crear documentación del estilo de ReadTheDocs:

    `(venv) > python -m pip install sphinx`<br>
    `(venv) > python -m pip install sphinxcontrib-django`<br>
    `(venv) > python -m pip install sphinx_rtd_theme`<br>
    `(venv) > python -m pip install recommonmark`

    Modo de uso:
    
    `cd .\docs\sphinx\`<br>
    `(venv) \docs\sphinx\ > .\make.bat html`

    Consular la documentación del código generada en `/docs/sphinx/_build/html/index.html`.