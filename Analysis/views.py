from django.shortcuts import render, redirect

# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from .forms import CreateNewTaskForm, CreateNewProjectForm

from django.db import connections
import pandas as pd
# Para mostrar datos de forma más atractiva
import mplfinance as mpf
import matplotlib.pyplot as plt

# Para meter una imagen en un buffer
from io import BytesIO
import base64

# Para creación de formularios de signup y login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Para registrar usuarios en la bd por defecto de Django
from django.contrib.auth.models import User

# Para crear la cookie de login
from django.contrib.auth import login, logout, authenticate

# Exception de violación de clave única. Da un IntegrityError
# en caso de intentar registrar un usuario que ya existe,
# por ejemplo
from django.db import IntegrityError

# Para proteger rutas. Las funciones que tienen este decorador 
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "home.html")



def signup(request):
    """Función que retorna un mensaje al cliente/navegador
    y devuelve una respuesta HTTP al cleinte (para ello, se
    importa HTTPresponse)

    Args:
        request (request): Variable pasada por Django en la
                          que se recibe info. que el cliente
                          esté enviando cuando visite esta función.

    Returns:
        HttpResponse:
    """
    if request.method == "GET":
        # print("Enviando form")
        context = {
            "form": UserCreationForm,
        }
        return render(request, "signup.html", context)

    else:
        # Comprobar que las contraseñas son iguales
        if request.POST["password1"] == request.POST["password2"]:
            try:
                # Registrar usuario
                print(request.POST)
                print("Registrar usuario")
                # Para crear el usuario y su contraseña (con lo que llega
                # desde el request.POST del formulario de signup.html)
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )
                user.save()
                # return HttpResponse("usuario creado")
                # context = {
                #     "form": UserCreationForm,
                # }
                # return render(request, "signup.html", context)
                login(request, user)
                return redirect("mapa_stocks")
            except IntegrityError:
                # return  HttpResponse("usuario ya existe")
                context = {
                    "form": UserCreationForm,
                    "error": "Error: Usuario ya existe",
                }
                return render(request, "signup.html", context)
            except:
                context = {
                    "form": UserCreationForm,
                    "error": "Error: error inesperado",
                }
                return render(request, "signup.html", context)

        else:
            # return HttpResponse("Password no coinciden")
            context = {
                "form": UserCreationForm,
                "error": "Error: Password no coinciden",
            }
            return render(request, "signup.html", context)



def sigout(request):
    """Para realizar el logout. No lo llamo 'logout' para 
    que no haya conflicto de nombres con el método de Django

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Para cerrar una sesión aprovecho el método predefinido
    # de Django que me permite borrar la cookie con el id del
    # usuario
    logout(request)
    return redirect("home")



def signin(request):
    """Para realizar el login. No lo llamo 'login' para 
    que no haya conflicto de nombres con el método de 
    Django.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "GET":
        context = {
            "form": AuthenticationForm,
        }
        return render(request, "login.html", context)
    else:
        # Comprobar si el usuario existe en la BD. Si el usuario
        # no es válido authenticate devuelve 'None'
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is None:
            context = {
                "form": AuthenticationForm,
                "error": "Usuario o contraseña incorrectos",
            }
            return render(request, "login.html", context)
        else:
            login(request, user)
            return redirect("mapa_stocks")



def formatearVolumen(volumen):
    """Método auxiliar para dar formato al volumen. 

    Args:
        value (int): _description_

    Returns:
        _type_: _description_
    """
    if volumen >= 1000000:
        return "{:.1f}M".format(volumen / 1000000)
    elif volumen >= 1000:
        return "{:.1f}K".format(volumen / 1000)
    else:
        return str(volumen)
    

@login_required
def mapa_stocks(request):
    """Para mapear los stocks de una base de datos.
    Función protegida. Requiere login para ser accedida.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    nombre_bd = "ibex35"

    datosFinStocks = {}

    # Para obtener el nombre de todas las tablas en la BD (usando
    # SQLite3, ojo)
    with connections[nombre_bd].cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        nombresStocks = cursor.fetchall()

        for stock in nombresStocks:
            table_name = stock[0]
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY Date DESC LIMIT 1;")
            últimaEntrada = cursor.fetchone()

            # Para poder ver el volumen con separador de miles
            # hago un 'apaño' aquí porque no me funciona el filtro
            # intcomma en html:
            últimaEntrada = list(últimaEntrada)
            # last_entry[5] = "{:,}".format(last_entry[5])
            últimaEntrada[5] = formatearVolumen(últimaEntrada[5])

            datosFinStocks[table_name] = últimaEntrada
    
    # Los nombres de los tickers son los mismos que los de
    # las tablas
    tickers = [table[0] for table in nombresStocks]

    context = {
        "tickers": tickers,
        "datosFinStocks": datosFinStocks,
    }
    return render(request, "mapa_stocks.html", context)



@login_required
def stock_data(request, ticker, nombre_bd):
    """Método que no usa los modelos/clases sino que accede
    directamente a la BD, busca el nombre de la tabla con
    el ticker pasado a través de la barra de direcciones
    y recoge toda su info.
    Función protegida. Requiere login para ser accedida.

    Args:
        request (request): Variable pasada por Django en la
                          que se recibe info. que el cliente
                          esté enviando cuando visite esta función.
        ticker (str): nombre del ticker del que quiero obtener la info.
        nombre_bd (str): nombre de la BD a la que me quiero conectar.

    Returns:
        render:
    """
    # Para llamar a la tabla que se pase como ticker
    table_name = f"{ticker.lower()}"

    # Sentencia SQL para acceder a la tabla deseada
    query = f"SELECT * FROM {table_name};"

    # Necesito indicar la BD a la que conectarme porque no estoy
    # usando la que viene por defecto (además de que las BD las he
    # puesto en una ruta distinta a la de por defecto, porque
    # están es "./databases")
    with connections[nombre_bd].cursor() as cursor:
        cursor.execute(query)
        # Fetch
        results = cursor.fetchall()

    # Convertir los resultados a una lista de diccionarios
    columns = [col[0] for col in cursor.description]
    ticker_data = [dict(zip(columns, row)) for row in results]
    
    # Contexto para el render
    context = {
        "ticker_data": ticker_data,
        "nombre_ticker": ticker,
    }

    return render(request, "stock_data.html", context)




@login_required
def stock_chart(request, ticker, nombre_bd):
    """Para mostrar los últimos 200 días de un stock en una gráfica.
    Función protegida. Requiere login para ser accedida.

    Args:
        request (_type_): _description_
        ticker (_type_): _description_
        nombre_bd (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Crear la conexión a la BD
    conn = connections.create_connection(nombre_bd)

    # Para llamar a la tabla que se pase como ticker
    table_name = f"{ticker.upper()}"

    # Sentencia SQL para acceder a la tabla deseada
    # y coger las últimas 200 filas/días
    query = f"SELECT * FROM '{table_name}' ORDER BY ROWID DESC LIMIT 200;"

    # Ejecutar la sentencia y pasar a DataFrame
    ticker_data = pd.read_sql_query(query, conn)

    # Cerrar conexión
    conn.close()

    # Paso la colunma 'Date' a datetime y ordeno por fecha
    ticker_data["Date"] = pd.to_datetime(ticker_data["Date"], utc=True)
    ticker_data = ticker_data.sort_values(by="Date", ascending=True)

    # Pongo la columna como index
    ticker_data.set_index("Date", inplace=True)

    # Crear la figura
    fig, ax = mpf.plot(
        ticker_data,
        type="candle",
        style="yahoo",
        title=str(ticker),
        returnfig=True,
        ylabel="Precio",
        ylabel_lower="Volumen",
        volume=True,
        mav=(20, 50),
        figsize=(14, 10),
    )

    # Guardar la figura como una cadena codificada a base64.
    # Todo esto me permite meter la imagen en un buffer y no
    # guardarla directamente en una ruta del servidor
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    plt.close(fig)

    # Contexto para el render
    context = {
        "ticker_data": ticker_data,
        "nombre_ticker": ticker,
        "image_base64": image_base64,
    }

    return render(request, "stock_chart.html", context)
