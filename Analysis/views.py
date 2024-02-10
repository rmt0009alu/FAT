from django.shortcuts import render, redirect

# Para enviar un error (en fallo de conexión a BD, p. ej.)
from django.http import HttpResponseServerError

from django.db import connections
import pandas as pd

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
from django.contrib.auth import login, logout

# Exception de violación de clave única. Da un IntegrityError
# en caso de intentar registrar un usuario que ya existe,
# por ejemplo
from django.db import IntegrityError

# Para proteger rutas. Las funciones que tienen este decorador
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required

# Para obtener los tickers y los paths de las BDs
from util.tickers.Tickers_BDs import tickersAdaptadosDJ30, tickersAdaptadosIBEX35, tickersAdaptadosIndices

# Para usar los modelos creados de forma dinámica
from django.apps import apps

# Para generar figuras sin repetir código
from News.views import _generar_figura
import matplotlib.pyplot as plt
import mpld3

# Para los RSS
from util.rss.RSS import RSSIbex35, RSSDj30
import feedparser


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
        # Envío el 'form'
        context = {
            "form": UserCreationForm,
        }
        return render(request, "signup.html", context)

    else:
        # Comprobar que las contraseñas son iguales
        if request.POST["password1"] == request.POST["password2"]:
            try:
                # Para crear el usuario y su contraseña (con lo que llega
                # desde el request.POST del formulario de signup.html)
                user = User.objects.create_user(
                    username=request.POST["username"],
                    # No hace falta securizar explícitamente las
                    # contraseñas, Django lo hace por mí creando
                    # un hash de la pass de los usuarios
                    password=request.POST['password1'],
                )
                # Guardar usuario y dejarle ya logueado
                user.save()
                login(request, user)

                # Redireccionar para informar al usuario
                context = {
                    "msg": "Usuario creado correctamente."
                }
                return render(request, 'signup_ok.html', context)
            except IntegrityError:
                context = {
                    "form": UserCreationForm,
                    "error": "Error: Usuario ya existe",
                }
                return render(request, "signup.html", context)
            except Exception as ex:
                context = {
                    "form": UserCreationForm,
                    "error": f"Error: error inesperado: {ex}",
                }
                return render(request, "signup.html", context)
        else:
            context = {
                "form": UserCreationForm,
                "error": "Error: Password no coinciden",
            }
            return render(request, "signup.html", context)


def signout(request):
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
        username = request.POST["username"]
        password = request.POST["password"]

        # Obtengo el objeto usuario:
        user = User.objects.filter(username=username).first()

        # Compruebo que el usuario exista y
        # checkeo su password cifrada. Si todo está
        # bien, entonces hago login y redirijo a home
        if user is not None and user.check_password(password):
            # Hago el login
            login(request, user)
            return redirect("dashboard")

        else:
            context = {
                "form": AuthenticationForm,
                "error": "Usuario o contraseña incorrectos",
            }
            return render(request, "login.html", context)


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
def mapa_stocks(request, nombre_bd):
    """Para mapear los stocks de una base de datos.
    Función protegida. Requiere login para ser accedida.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if nombre_bd == 'dj30':
        tickers = tickersAdaptadosDJ30()
    elif nombre_bd == 'ibex35':
        tickers = tickersAdaptadosIBEX35()

    miApp = 'Analysis'

    # Lista para los diccionarios de las últimas entradas
    datosFinStocks = []

    # Figura del índice
    figura = None

    # Nombre del índice
    nombreIndice = None

    for t in tickers:
        # No quiero que se muestren los índices con los
        # componentes del índice
        if t not in tickersAdaptadosIndices():
            dictMutable = {}
            # Para obtener los modelos de forma dinámica
            model = apps.get_model(miApp, t)
            try:
                # Cojo las última entrada de cada stock:
                entrada = model.objects.using(nombre_bd).order_by('-date')[:1].values('ticker', 'close',
                                                                                      'high', 'low', 'previous_close',
                                                                                      'percent_variance', 'volume',
                                                                                      'date', 'name')
                # 'entrada' es un QuerySet INMUTABLE y 'entrada[0]' es un Dict
                dictMutable = entrada[0]
                # Cambio la notación de _ de la BD a . para mostrar
                dictMutable['ticker'] = dictMutable['ticker'].replace('_', '.')
                dictMutable['variance'] = dictMutable['close'] - dictMutable['previous_close']
                dictMutable['volume'] = formatearVolumen(dictMutable['volume'])
                dictMutable['ticker_bd'] = t
                datosFinStocks.append(dictMutable)
            except Exception as ex:
                print("[NO OK] Error mapa stocks: ", ex)
        else:
            nombreIndice = t
            # Supuesto de ser el índice
            model = apps.get_model(miApp, t)
            try:
                entradas = model.objects.using(nombre_bd).order_by('-date')[:250].values('date', 'close',
                                                                                         'ticker', 'name')
                figura = _generar_figura(entradas)
                figura = mpld3.fig_to_html(figura)

                # Conviene ir cerrando los plots para que no
                # haya problemas de memoria
                plt.close()
            except Exception as ex:
                print("[NO OK] Error mapa stocks: ", ex)

    listaRSS = getListaRSS(nombre_bd)

    context = {
        "nombre_bd": nombre_bd,
        "nombreIndice": nombreIndice,
        "datosFinStocks": datosFinStocks,
        "figura": figura,
        "listaRSS": listaRSS,
    }
    return render(request, "mapa_stocks.html", context)


def getListaRSS(nombre_bd):
    """Para obtener una lista con noticias relacionadas
    con los índices y otros mercados.

    Args:
        nombre_bd (str): nombre de la base de datos, i.e.,
            índice del que se recuperan los RSS.

    Returns:
        (list): lista con los RSS del índice.
    """
    RSS = []
    listaRSS = []
    if nombre_bd == 'dj30':
        RSS = RSSDj30()
    elif nombre_bd == 'ibex35':
        RSS = RSSIbex35()

    numNoticiasPorFeed = 2

    for n in range(numNoticiasPorFeed):
        for fuente in RSS:
            feed = feedparser.parse(fuente)
            # Cojo sólo la última entrada de cada RSS (que es
            # la última noticia en todos los casos)
            entrada = feed["entries"][n]
            diccionario = {'title': entrada.title, 'href': entrada.links[0]['href']}
            listaRSS.append(diccionario)

    return listaRSS


@login_required
def chart_y_datos(request, ticker, nombre_bd):
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
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]

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
                          # height=800,
                          # width=1000,
                          autosize=True)

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

    # Para obtener el nombre completo
    model = apps.get_model('Analysis', ticker)
    entradas = model.objects.using(nombre_bd)[:1].values('name')

    # Contexto para el render
    context = {
        "nombre_ticker": nombre_ticker,
        "nombre_completo": entradas[0]['name'],
        "image_json": image_json,
        "tabla_datos": get_datos(ticker, nombre_bd),
    }

    return render(request, "chart_y_datos.html", context)


def get_datos(ticker, nombre_bd):
    """Método que devuelve los datos del último mes (aprox.)
    del stock seleccionado.

    Args:
        ticker (str): nombre del ticker del que quiero obtener
            la info.
        nombre_bd (str): nombre (no ruta) de la BD a la que me
            quiero conectar.

    Returns:
        (QuerySet): tabla con los datos del stock
    """
    # Los modelos se crean de forma dinámica desde 'Analysis'
    # pero están disponibles para todas las apps
    miApp = 'Analysis'
    model = apps.get_model(miApp, ticker)

    # Devuelvo los últimos 22 registros (aprox. 1 mes)
    query_set = model.objects.using(nombre_bd).order_by('-date')[:22].all()

    # 'query_set' es un QuerySet INMUTABLE donde se puede acceder a
    # las entradas con query_set[1], query_set[21], ... y 'tabla_datos'
    # es un Dict
    for _ in range(len(query_set)):
        # Dar formato adecuado al volumen
        query_set[_].volume = formatearVolumen(query_set[_].volume)

    return query_set
