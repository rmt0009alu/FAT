from django.shortcuts import render, redirect

# Para enviar un error (en fallo de conexión a BD, p. ej.)
from django.http import HttpResponseServerError

# from django.shortcuts import get_object_or_404, redirect
# from .forms import CreateNewTaskForm, CreateNewProjectForm

from django.db import connections
import pandas as pd
# Para mostrar datos de forma más atractiva
# import mplfinance as mpf
# import matplotlib.pyplot as plt

# Para meter una imagen en un buffer
# from io import BytesIO
# import base64
# Para usar un canvas en vez de imágenes
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# Para charts dinámicos en lugar de imágenes estáticas
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Para controlar errores de conexión a la BD
import sqlite3

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
    """Para la página principal. 

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
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
    try:
        # Crear la conexión a la BD
        conn = connections.create_connection(nombre_bd)
        
        # Para llamar a la tabla que se pase como ticker
        table_name = f"{ticker.upper()}"

        # Sentencia SQL para acceder a la tabla deseada
        # y coger las últimas 200 filas/días
        query = f"SELECT * FROM '{table_name}' ORDER BY ROWID DESC LIMIT 200;"

        # Ejecutar la sentencia y pasar a DataFrame
        ticker_data = pd.read_sql_query(query, conn)
        
        # Paso la colunma 'Date' a datetime y ordeno por fecha
        ticker_data["Date"] = pd.to_datetime(ticker_data["Date"], utc=True)
        ticker_data = ticker_data.sort_values(by="Date", ascending=True)

        # Para eliminar los días que no hay mercado hay que hacer más
        # que un dropna() porque plotly hace su propia lista entre 
        # fechas a la hora de mostrar y aunque no haya huecos los crea
        # Idea sacada de: https://stackoverflow.com/questions/61895282/plotly-how-to-remove-empty-dates-from-x-axis
        trading_days_data = ticker_data.dropna()

        dt_all = pd.date_range(start=ticker_data['Date'].iloc[0],
                               end=ticker_data['Date'].iloc[-1])
        dt_obs = [d.strftime("%Y-%m-%d") for d in ticker_data['Date']]
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

        # Pongo la columna como index
        trading_days_data.set_index("Date", inplace=True)
        
        # Creo la figura para el gráfico de velas de plotly
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=['', 'Volumen'])
        
        # Añado el gráfico de velas
        candlestick = go.Candlestick(x=trading_days_data.index,
                                     open=trading_days_data['Open'],
                                     high=trading_days_data['High'],
                                     low=trading_days_data['Low'],
                                     close=trading_days_data['Close'],
                                     name='Velas')
        fig.add_trace(candlestick, row=1, col=1)

        # Añado las medias móviles
        mm20_trace = go.Scatter(x=trading_days_data.index,
                               y=trading_days_data['MM20'],
                               mode='lines',
                               line=dict(width=1),
                               marker_color='rgba(234, 113, 37, 0.8)', 
                               name='MM20')
        fig.add_trace(mm20_trace, row=1, col=1)

        mm50_trace = go.Scatter(x=trading_days_data.index,
                               y=trading_days_data['MM50'],
                               mode='lines',
                               line=dict(width=1),
                               marker_color='rgba(21, 50, 231, 0.8)', 
                               name='MM50')
        fig.add_trace(mm50_trace, row=1, col=1)

        # Volumen. Lo pongo en gris
        volume_trace = go.Bar(x=trading_days_data.index,
                              y=trading_days_data['Volume'],
                              marker_color='rgba(51, 45, 48, 0.8)',  
                              name='Volumen')
        fig.add_trace(volume_trace, row=2, col=1)

        # Actualizo los ejes y su disposición
        fig.update_xaxes(
            # Para que no coja las fechas auto creadas, sino las
            # de datos reales, i.e., que no coja los días de 
            # no trading
            rangebreaks=[dict(values=dt_breaks)] 
        )
        # Para mostrar un selector de días, meses, años..
        fig.update_xaxes(
            # rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="todate"),
                    dict(count=24, label="1M", step="day", stepmode="todate"),
                    dict(count=365, label="1Y", step="day", stepmode="todate"),
                    dict(step="all")
                ])
            )
        )
        fig.update_xaxes(title_text='Fecha', row=2, col=1,
                         categoryorder='category ascending')
        fig.update_yaxes(title_text='Precio', row=1, col=1)
        fig.update_yaxes(title_text='Volumen', row=2, col=1)
        fig.update_layout(showlegend=True, 
                        #   height=800, 
                        #   width=1000,
                          autosize=True)

        # Guardar la figura decodificada como base64 (prefiero en JSON)
        # image_base64 = fig.to_html(full_html=False)

        # Guardar la figura como una cadena de JSON
        image_json = fig.to_json()

    except sqlite3.Error as e:
        return HttpResponseServerError(f"Error de conexión a la BD: {e}")
    finally:
        if conn:
            # Cerrar conexión en cualquier caso
            conn.close()

    # Solo para mostrar el nombre más "bonito"
    nombre_ticker = ticker.split('_')[0]

    # Contexto para el render
    context = {
        # "ticker_data": ticker_data,
        "nombre_ticker": nombre_ticker,
        # "image_base64": image_base64,
        "image_json": image_json,
    }

    return render(request, "stock_chart.html", context)
