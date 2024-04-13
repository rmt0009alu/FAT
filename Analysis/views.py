"""
Métodos de vistas para usar con Analysis.
"""
import re
import pandas as pd
import feedparser
import mpld3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .models import Sectores
# Para charts dinámicos en lugar de imágenes estáticas
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from django.shortcuts import render, redirect
# Para proteger rutas. Las funciones que tienen este decorador
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required
# Para creación de formularios de signup y login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Para registrar usuarios en la bd por defecto de Django
from django.contrib.auth.models import User
# Para crear la cookie de login
from django.contrib.auth import login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
# Exception de violación de clave única. Da un IntegrityError
# en caso de intentar registrar un usuario que ya existe, por ejemplo
from django.db import IntegrityError
# Para usar los modelos creados de forma dinámica
from django.apps import apps
# Para usar django-pandas y frames
from django_pandas.io import read_frame
# Para los grafos
import networkx as nx
# Para el buffer y la imagen del grafo
from io import BytesIO
import base64
# Para generar figuras sin repetir código
from News.views import _generar_figura
# Para los RSS
from util.rss.RSS import rss_dj30, rss_ibex35, rss_ftse100, rss_dax40
# Para obtener los tickers y los paths de las BDs
# (para no sobrepasar las 120 columnas y mejorar
# la calidad del código según pylint hago varios import)
from util.tickers.Tickers_BDs import tickers_adaptados_dj30, tickers_adaptados_ibex35, tickers_adaptados_ftse100
from util.tickers.Tickers_BDs import tickers_adaptados_dax40, tickers_adaptados_indices, bases_datos_disponibles
from util.tickers.Tickers_BDs import tickers_adaptados_disponibles, obtener_nombre_bd, tickers_disponibles


def signup(request):
    """Para registrar a un usuario.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        render
            Renderiza las plantillas 'signup.html' o 'signup_ok.html' con datos de contexto.
    """
    if request.method == "GET":
        # Envío el 'form'
        context = {
            "form": UserCreationForm,
        }
        return render(request, "signup.html", context)

    # POST
    # ----
    usuario = request.POST.get("username")
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")

    # Reglas de validación de usuarios
    # --------------------------------
    if not usuario:
        context = {
            "form": UserCreationForm,
            "error": "Error: se requiere un nombre de usuario",
        }
        return render(request, "signup.html", context)
    if not re.match("^[a-zA-Z0-9]+$", usuario):
        context = {
            "form": UserCreationForm,
            "error": "Error: el nombre sólo puede tener letras y números",
        }
        return render(request, "signup.html", context)
    if len(usuario) < 5:
        context = {
            "form": UserCreationForm,
            "error": "Error: nombre demasiado corto",
        }
        return render(request, "signup.html", context)

    # Reglas de validación de password
    # --------------------------------
    # Django tiene un validador de contraseñas integrado para
    # longitud (8), máyus./minus., números, que no sean similares
    # al nombre, etc.
    try:
        validate_password(password1)
    except ValidationError as error:
        context = {
            "form": UserCreationForm,
            "error": f"Error: {', '.join(error.messages)}",
        }
        return render(request, "signup.html", context)

    if password1 != password2:
        context = {
            "form": UserCreationForm,
            "error": "Error: contraseñas no coinciden",
        }
        return render(request, "signup.html", context)

    # Suponiendo que se pasa la validación de usuario y pass
    # compruebo que el usuario no exista en la BD
    try:
        user = User.objects.create_user(
            username=usuario,
            password=password1,
        )
        # A la vez que se registra le hago login
        user.save()
        login(request, user)
        context = {
            "msg": "Usuario creado correctamente."
        }
        return render(request, 'signup_ok.html', context)
    except IntegrityError:
        context = {
            "form": UserCreationForm,
            "error": "Error: usuario ya existe",
        }
        return render(request, "signup.html", context)


def signout(request):
    """Para realizar el logout. No lo llamo 'logout' para que no haya conflicto de nombres con el método de Django

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        redirect
            Plantilla de home.
    """
    # Para cerrar una sesión aprovecho el método predefinido
    # de Django que me permite borrar la cookie con el id del
    # usuario
    logout(request)
    return redirect("home")


def signin(request):
    """Para realizar el login. No lo llamo 'login' para que no haya conflicto de nombres con el método de Django.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Union[render, redirect]
            * render: Renderiza la plantilla 'login.html' con datos de contexto (para GET).
            * redirect: Plantilla de dashboard (para POST).
    """
    if request.method == "GET":
        context = {
            "form": AuthenticationForm,
        }
        return render(request, "login.html", context)

    # POST
    # ----
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

    # Si no he redirigido algo está mal
    context = {
        "form": AuthenticationForm,
        "error": "Usuario o contraseña incorrectos",
    }
    return render(request, "login.html", context)


def mapa_stocks(request, nombre_bd):
    """Para mapear los stocks de una base de datos.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        render
            Renderiza la plantilla 'mapa_stocks.html' con datos de contexto.
    """
    if nombre_bd not in bases_datos_disponibles():
        return render(request, '404.html')
    if nombre_bd == 'dj30':
        tickers = tickers_adaptados_dj30()
    if nombre_bd == 'ibex35':
        tickers = tickers_adaptados_ibex35()
    if nombre_bd == 'ftse100':
        tickers = tickers_adaptados_ftse100()
    if nombre_bd == 'dax40':
        tickers = tickers_adaptados_dax40()

    # Lista para los diccionarios de las últimas entradas
    datos_fin_stocks = []

    # Figura del índice
    figura = None

    # Nombre del índice
    nombre_indice = None

    for t in tickers:
        # No quiero que se muestren los índices con los
        # componentes del índice
        if t not in tickers_adaptados_indices():
            dict_mutable = {}
            # Para obtener los modelos de forma dinámica
            model = apps.get_model('Analysis', t)
            # Cojo las última entrada de cada stock:
            entrada = model.objects.using(nombre_bd).order_by('-date')[:1].values('ticker', 'close',
                                                                                  'high', 'low', 'previous_close',
                                                                                  'percent_variance', 'volume',
                                                                                  'date', 'name')
            # 'entrada' es un QuerySet INMUTABLE y 'entrada[0]' es un Dict
            dict_mutable = entrada[0]
            # Cambio la notación de _ de la BD a . para mostrar
            dict_mutable['ticker'] = dict_mutable['ticker'].replace('_', '.')
            dict_mutable['variance'] = dict_mutable['close'] - dict_mutable['previous_close']
            dict_mutable['volume'] = _formatear_volumen(dict_mutable['volume'])
            dict_mutable['ticker_bd'] = t
            datos_fin_stocks.append(dict_mutable)

        else:
            nombre_indice = t
            # Supuesto de ser el índice
            model = apps.get_model('Analysis', t)
            entradas = model.objects.using(nombre_bd).order_by('-date')[:250].values('date', 'close',
                                                                                     'ticker', 'name')
            figura = _generar_figura(entradas)
            figura = mpld3.fig_to_html(figura)

            # Conviene ir cerrando los plots para que no
            # haya problemas de memoria
            plt.close()

    lista_rss = _get_lista_rss(nombre_bd)

    context = {
        "nombre_bd": nombre_bd,
        "nombreIndice": nombre_indice,
        "datosFinStocks": datos_fin_stocks,
        "figura": figura,
        "listaRSS": lista_rss,
    }
    return render(request, "mapa_stocks.html", context)


@login_required
def chart_y_datos(request, ticker, nombre_bd):
    """Para mostrar los últimos 200 días de un stock en una gráfica.

    Función protegida. Requiere login para ser accedida.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest)
            Solicitud HTTP encapsulada por Django.

        ticker : str
            Nombre adaptado del ticker recogido de la URL.

        nombre_bd : str
            Nombre de la BD recogido de la URL.
        
    Returns
    -------
        render
            Renderiza la plantilla 'chart_y_datos.html' con datos de contexto.
    """
    if (nombre_bd not in bases_datos_disponibles()) or (ticker not in tickers_adaptados_disponibles()):
        return render(request, '404.html')

    # Obtengo los datos del modelo y lo paso a DataFrame
    model = apps.get_model('Analysis', ticker)
    entradas = model.objects.using(nombre_bd).order_by('-date')[:500].all()
    ticker_data = pd.DataFrame(list(entradas.values()))

    # Contexto para el render. Contenido común a los diferentes casos
    context = {
        "nombre_ticker": ticker.replace('_', '.'),
        "nombre_completo": ticker_data['name'].iloc[0],
        "image_json": _get_image_json(ticker_data),
        "tabla_datos": _get_datos(ticker, nombre_bd),
        "grafo": _generar_correlaciones(ticker),
        "lista_tickers": tickers_disponibles(),
        "grafica_sectores": _grafica_evolucion_sector(ticker),
    }

    # Cuando es una solicitud GET retorno sin más
    if request.method == "GET":
        return render(request, "chart_y_datos.html", context)

    # ----
    # POST
    # ----
    ticker_a_comparar = request.POST.get("ticker_a_comparar")

    if ticker_a_comparar not in tickers_disponibles():
        context["msg_error"] = 'El ticker no existe'
        return render(request, "chart_y_datos.html", context)

    # Paso el ticker a la notación de '_' que es la de las BDs
    ticker_a_comparar = ticker_a_comparar.replace('.', '_')
    # Se puede comparar con un índice también
    ticker_a_comparar = ticker_a_comparar.replace('^', '')

    context["graficas_comparacion"] = _generar_graficas_comparacion(ticker, ticker_a_comparar)

    return render(request, "chart_y_datos.html", context)


def _formatear_volumen(volumen):
    """Método auxiliar para dar formato al volumen.

    Parameters
    ----------
        volumen : int
            Valor a formatear.

    Returns
    -------
        str
            Volumen formateado.
    """
    if volumen >= 1000000:
        return "{:.1f}M".format(volumen / 1000000)
    if volumen >= 1000:
        return "{:.1f}K".format(volumen / 1000)

    return str(volumen)


def _get_lista_rss(nombre_bd):
    """Para obtener una lista con noticias relacionadas con los índices y otros mercados.

    Parameters
    ----------
        nombre_bd : str
            Nombre de la base de datos, i.e., índice del que se recuperan los RSS.

    Returns
    -------
        lista_rss : list
            lista con los RSS del índice.
    """
    rss = []
    lista_rss = []
    if nombre_bd == 'dj30':
        rss = rss_dj30()
    elif nombre_bd == 'ibex35':
        rss = rss_ibex35()
    elif nombre_bd == 'ftse100':
        rss = rss_ftse100()
    elif nombre_bd == 'dax40':
        rss = rss_dax40()

    num_noticias_por_feed = 2

    for n in range(num_noticias_por_feed):
        for fuente in rss:
            feed = feedparser.parse(fuente)
            # Cojo sólo la última entrada de cada RSS (que es
            # la última noticia en todos los casos)
            entrada = feed["entries"][n]
            diccionario = {'title': entrada.title, 'href': entrada.links[0]['href']}
            lista_rss.append(diccionario)

    return lista_rss


def _get_datos(ticker, nombre_bd):
    """Método que devuelve los datos del último mes (aprox.) del stock seleccionado.

    Parameters
    ----------
        ticker : str
            Nombre del ticker del que quiero obtener la info.

        nombre_bd : str
            Nombre (no ruta) de la BD a la que me quiero conectar.

    Returns
    -------
        query_set : QuerySet
            Tabla con los datos del stock.
    """
    # Los modelos se crean de forma dinámica desde 'Analysis'
    # pero están disponibles para todas las apps
    model = apps.get_model('Analysis', ticker)

    # Devuelvo los últimos 22 registros (aprox. 1 mes)
    query_set = model.objects.using(nombre_bd).order_by('-date')[:22].all()

    # 'query_set' es un QuerySet INMUTABLE donde se puede acceder a
    # las entradas con query_set[1], query_set[21], ... y 'tabla_datos'
    # es un Dict
    for _ in range(len(query_set)):
        # Dar formato adecuado al volumen
        query_set[_].volume = _formatear_volumen(query_set[_].volume)

    return query_set


def _get_image_json(ticker_data):
    """Para obtener una figura en JSON que permitirá mostrar un gráfico dinámico.

    Parameters
    ----------
        ticker_data : pandas.core.frame.DataFrame
            DataFrame con los datos del ticker seleccionado.

    Returns
    -------
        image_json : str
            Cadena JSON con los datos de la figura.
    """
    # Paso la colunma 'Date' a datetime y ordeno por fecha
    ticker_data["date"] = pd.to_datetime(ticker_data["date"], utc=True)
    ticker_data = ticker_data.sort_values(by="date", ascending=True)

    # Para eliminar los días que no hay mercado hay que hacer más
    # que un dropna() porque plotly hace su propia lista entre
    # fechas a la hora de mostrar y aunque no haya huecos los crea
    # Idea sacada de: https://stackoverflow.com/questions/61895282/plotly-how-to-remove-empty-dates-from-x-axis
    trading_days_data = ticker_data.dropna()

    dt_all = pd.date_range(start=ticker_data['date'].iloc[0],
                           end=ticker_data['date'].iloc[-1])
    dt_obs = [d.strftime("%Y-%m-%d") for d in ticker_data['date']]
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]

    # Pongo la columna como index
    trading_days_data.set_index("date", inplace=True)

    # Creo la figura para el gráfico de velas de plotly
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=['', 'Volumen'])

    # Añado el gráfico de velas
    candlestick = go.Candlestick(x=trading_days_data.index,
                                 open=trading_days_data['open'],
                                 high=trading_days_data['high'],
                                 low=trading_days_data['low'],
                                 close=trading_days_data['close'],
                                 name='Velas')
    fig.add_trace(candlestick, row=1, col=1)

    # Añado las medias móviles
    mm20_trace = go.Scatter(x=trading_days_data.index,
                            y=trading_days_data['mm20'],
                            mode='lines',
                            # line=dict(width=1),
                            line={"width": 1},
                            marker_color='rgba(234, 113, 37, 0.8)',
                            name='MM20')
    fig.add_trace(mm20_trace, row=1, col=1)

    mm50_trace = go.Scatter(x=trading_days_data.index,
                            y=trading_days_data['mm50'],
                            mode='lines',
                            # line=dict(width=1),
                            line={"width": 1},
                            marker_color='rgba(21, 50, 231, 0.8)',
                            name='MM50')
    fig.add_trace(mm50_trace, row=1, col=1)

    # Volumen. Lo pongo en gris
    volume_trace = go.Bar(x=trading_days_data.index,
                          y=trading_days_data['volume'],
                          marker_color='rgba(51, 45, 48, 0.8)',
                          name='Volumen')
    fig.add_trace(volume_trace, row=2, col=1)

    # Actualizo los ejes y su disposición
    fig.update_xaxes(
        # Para que no coja las fechas auto creadas, sino las
        # de datos reales, i.e., que no coja los días de
        # no trading
        # rangebreaks=[dict(values=dt_breaks)]
        rangebreaks=[{"values": dt_breaks}]
    )
    # Para mostrar un selector de días, meses, años..
    fig.update_xaxes(
        # rangeslider_visible=True,
        rangeselector={
            "buttons": list([
                {"count": 7, "label": '1W', "step": 'day', "stepmode": 'todate'},
                {"count": 90, "label": '3M', "step": 'day', "stepmode": 'todate'},
                {"count": 180, "label": '6M', "step": 'day', "stepmode": 'todate'},
                {"count": 365, "label": '1Y', "step": 'day', "stepmode": 'todate'},
                {"step": 'all'}
                ])
            }
    )
    fig.update_xaxes(title_text='Fecha', row=2, col=1, categoryorder='category ascending')
    fig.update_yaxes(title_text='Precio', row=1, col=1)
    fig.update_yaxes(title_text='Volumen', row=2, col=1)
    fig.update_layout(showlegend=True,
                      # height=800,
                      # width=1000,
                      autosize=True)

    # Guardar la figura como una cadena de JSON
    image_json = fig.to_json()

    return image_json


def _generar_correlaciones(ticker_objetivo):
    """Para generar la matriz de correlación de todos los valores disponibles en las bases de datos. 

    Parameters
    ----------
        ticker_objetivo : str
            Nombre del ticker con el que se quieren calcular las correlaciones (nodo raíz de la red).

    Returns
    -------
        grafos : str
            Cadena de datos que guarda los grafos generados con las correlaciones positiva y negativa, 
            según la evolución del último mes (22 sesiones).
    """
    dic_datos = {}
    tickers = tickers_adaptados_disponibles()

    for ticker in tickers:
        bd = obtener_nombre_bd(ticker)
        model = apps.get_model('Analysis', ticker)
        # Útimas 22 sesiones en precios de cierre, aprox. 1 mes
        entradas = model.objects.using(bd).order_by('-date')[:22].values('date', 'close')
        # Convierto a lista de tuplas para separar después
        fechas_cierres = [(ent['date'], ent['close']) for ent in entradas]
        # Separo la info de las tuplas
        fechas = [ent[0] for ent in fechas_cierres]
        cierres = [ent[1] for ent in fechas_cierres]
        # Guardo los datos de cada ticker en un dict
        dic_datos[ticker] = {'Date': fechas, 'Close': cierres}

    # Convierto a DataFrame
    df = pd.DataFrame({ticker: pd.Series(datos['Close'], index=datos['Date']) for ticker, datos in dic_datos.items()})

    # Creo la matriz de correlación (esta matriz sigue
    # siendo un DataFrame)
    matriz_correl = df.corr()

    # Creo el grafo con NetwrokX
    grafos = _crear_grafos(matriz_correl, tickers, ticker_objetivo)

    return grafos


def _crear_grafos(matriz_correl, tickers, ticker_objetivo):
    """Para crear los grafos de correlaciones a partir de la matriz de correlación. 

    Parameters
    ----------
        matriz_correl : pandas.core.frame.DataFrame
            Matriz de correlación entre valores cotizados según precios de cierre de últimas 22 
            sesiones (aprox. un mes).
            
        tickers : list
            Lista de tickers disponibles.

        ticker_objetivo : str
            Ticker del que se quieren obtener las correlaciones.

    Returns
    -------
        grafos : str
            Cadena de datos que guarda los grafos generados con las correlaciones positiva y negativa, 
            según la evolución del último mes (22 sesiones).
    """
    # Creo un grafo vacío y añado los nodos (que son los tickers
    # NO adaptados para mostrar con formato de '.')
    grafo_correl_positiva = nx.Graph()
    grafo_correl_positiva.add_nodes_from(tickers_disponibles())
    grafo_correl_negativa = nx.Graph()
    grafo_correl_negativa.add_nodes_from(tickers_disponibles())

    # Añado los enlaces con su peso (el valor de correlación)
    for ticker in tickers:
        # Para no generar enlaces recursivos
        if ticker != ticker_objetivo:
            peso_correl = matriz_correl.loc[ticker_objetivo, ticker]
            # Solo correlación positiva:
            if peso_correl > 0.75:
                # Redondeo los pesos para que se vea mejor en el grafo
                # si lo llego a mostrar
                grafo_correl_positiva.add_edge(ticker_objetivo.replace("_", "."),
                                               ticker.replace("_", "."),
                                               weight=round(peso_correl, 3))
            if peso_correl < -0.75:
                # Redondeo los pesos para que se vea mejor en el grafo
                # si lo llego a mostrar
                grafo_correl_negativa.add_edge(ticker_objetivo.replace("_", "."),
                                               ticker.replace("_", "."),
                                               weight=round(peso_correl, 3))

    # Elimino todos aquellos nodos que no tengan un enlace
    for ticker in tickers_disponibles():
        if ticker != ticker_objetivo.replace("_", ".") and not nx.has_path(grafo_correl_positiva,
                                                                           ticker,
                                                                           ticker_objetivo.replace("_", ".")):
            grafo_correl_positiva.remove_node(ticker)
        if ticker != ticker_objetivo.replace("_", ".") and not nx.has_path(grafo_correl_negativa,
                                                                           ticker,
                                                                           ticker_objetivo.replace("_", ".")):
            grafo_correl_negativa.remove_node(ticker)

    # Guardo los grafos en una figura (2 filas y 1 columna)
    fig, axes = plt.subplots(2, 1, figsize=(6, 8))

    pos = nx.circular_layout(grafo_correl_positiva)
    nx.draw_networkx(grafo_correl_positiva, pos, with_labels=True, node_size=1000,
                     font_size=8, node_color='skyblue', font_color='black', ax=axes[0])
    axes[0].set_title("Alta correlación positiva en \núltimas 30 sesiones (precios de cierre)", fontsize=10)
    axes[0].axis('off')

    pos = nx.circular_layout(grafo_correl_negativa)
    nx.draw_networkx(grafo_correl_negativa, pos, with_labels=True, node_size=1000,
                     font_size=8, node_color='red', font_color='black', ax=axes[1])
    axes[1].set_title("Alta correlación negativa en \núltimas 30 sesiones (precios de cierre)", fontsize=10)
    axes[1].axis('off')

    # Aumento la separación vertical entre subplots
    plt.subplots_adjust(hspace=0.5)

    # edge_labels = nx.get_edge_attributes(G_correl_positiva, 'weight')
    # Los enlaces son 'todos con todos' pero, aunque no lo muestro
    # dichos enlaces tienen sus pesos, que es lo que interesa
    # nx.draw_networkx_edge_labels(G, pos)

    # Lo guardo en un byte buffer y así lo puedo mostrar directamente
    # integrado en la plantilla html
    buffer = BytesIO()
    plt.savefig(buffer, format="PNG")
    plt.close()

    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    grafos = base64.b64encode(buffer.read()).decode()

    return grafos


def _generar_graficas_comparacion(ticker, ticker_a_comparar):
    """Para crear las figuras que muestran las evoluciones de precios de cierre y de porcentajes de 
    dos tickers de forma relativa (comparación entre ambos valores).

    Parameters
    ----------
        ticker : str
            Ticker original (objetivo).

        ticker_a_comparar : str
            Ticker con el que comparar. 

    Returns
    -------
        graficas_comparacion : str
            Cadena de datos con la comparación entre valores (gráficas del buffer decodificadas).
    """
    bd = obtener_nombre_bd(ticker)
    model = apps.get_model('Analysis', ticker)
    # Último año aprox.
    entradas_ticker = model.objects.using(bd).order_by('-date')[:220].values('date', 'close', 'percent_variance')

    bd = obtener_nombre_bd(ticker_a_comparar)
    model = apps.get_model('Analysis', ticker_a_comparar)
    # Último año aprox.
    entradas_ticker_a_comparar = model.objects.using(bd).order_by('-date')[:220].values('date',
                                                                                        'close',
                                                                                        'percent_variance')

    # Obtener los 'values' del queryset 'entradas'
    # y pasar a df
    df_ticker = read_frame(entradas_ticker.values('date', 'close', 'percent_variance'))
    df_ticker_comparar = read_frame(entradas_ticker_a_comparar.values('date', 'close', 'percent_variance'))

    # Normalizar para ver relación 'directa' sin precios
    df_ticker, df_ticker_comparar = _normalizar_dataframes(df_ticker, df_ticker_comparar)

    # FIGURAS
    # -------
    fig, axes = plt.subplots(2, 1, figsize=(7, 10))
    buffer = BytesIO()

    # FIG 1
    # -----
    # Plot de la evolución de las variaciones diarias
    axes[0].plot(df_ticker['date'], df_ticker['normalizado'], label=ticker.replace("_","."))
    axes[0].plot(df_ticker_comparar['date'],
                 df_ticker_comparar['normalizado'],
                 label=ticker_a_comparar.replace("_","."))
    # Título y estilos
    axes[0].set(xlabel='Fecha',
                ylabel=f'{ticker.replace("_",".")} vs {ticker_a_comparar.replace("_",".")}',
                title='Comparación relativa (evolución de cierres diarios)')
    axes[0].grid(True, linestyle='--', alpha=0.5)
    axes[0].legend()

    # Elimino las etiquetas del eje y porque se muestran
    # valores normalizados
    axes[0].set_yticklabels([])

    # FIG 2
    # -----
    # Plot de la evolución de las variaciones diarias
    axes[1].plot(df_ticker['date'], df_ticker['percent_variance'], label=ticker.replace("_","."))
    axes[1].plot(df_ticker_comparar['date'],
                 df_ticker_comparar['percent_variance'],
                 label=ticker_a_comparar.replace("_","."))
    # Título y estilos
    axes[1].set(xlabel='Fecha',
                ylabel=f'{ticker.replace("_",".")} vs {ticker_a_comparar.replace("_",".")}',
                title='Comparación relativa (evolución de variaciones diarias)')
    axes[1].grid(True, linestyle='--', alpha=0.5)
    axes[1].legend()

    # Aumentar distancia vertical entre figuras
    plt.subplots_adjust(hspace=0.4)

    # Ajusto los bins y etiquetas
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.savefig(buffer, format="PNG")
    plt.close()

    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    graficas_comparacion = base64.b64encode(buffer.read()).decode()

    return graficas_comparacion


def _normalizar_dataframes(df_ticker, df_ticker_comparar):
    """Para normalizar los precios de cierre del valor con el que se quiere comparar. 
    
    Esta acción permite ver la evolución en términos relativos.

    Parameters
    ----------
        df_ticker : pandas.core.frame.DataFrame
            DataFrame con los datos del ticker original. 

        df_ticker_comparar : pandas.core.frame.DataFrame
            DataFrame con los datos del ticker con el que se quiere comparar.

    Returns
    -------
        Tuple: Tupla con los DataFrames de los tickers a comparar.
            * df_ticker: pandas.core.frame.DataFrame
                DataFrame con los datos normalizados del ticker original. 
            * df_ticker_comparar: pandas.core.frame.DataFrame
                DataFrame con los datos normalizados del ticker con el que se quiere comparar.
    """
    # Cojo las fechas más antiguas con iloc[-1]. Pueden no
    # empezar a la vez porque haya valores cotizados en un
    # día festivo de diferentes índices
    if df_ticker['close'].iloc[-1] > df_ticker_comparar['close'].iloc[-1]:
        ratio = df_ticker['close'].iloc[-1] / df_ticker_comparar['close'].iloc[-1]
        df_ticker['normalizado'] = df_ticker['close']
        df_ticker_comparar['normalizado'] = df_ticker_comparar['close'] * ratio

    elif df_ticker_comparar['close'].iloc[-1] > df_ticker['close'].iloc[-1]:
        ratio = df_ticker_comparar['close'].iloc[-1] / df_ticker['close'].iloc[-1]
        df_ticker['normalizado'] = df_ticker['close'] * ratio
        df_ticker_comparar['normalizado'] = df_ticker_comparar['close']

    else:
        df_ticker['normalizado'] = df_ticker['close']
        df_ticker_comparar['normalizado'] = df_ticker_comparar['close']

    return df_ticker, df_ticker_comparar


def _grafica_evolucion_sector(ticker):
    """Para generar la gráfica comparativa con el sector de referencia del valor pasado a 
    través del nombre del ticker.

    Parameters
    ----------
        ticker : str
            Nombre del ticker de un valor. 

    Returns
    -------
        grafica_sector : str
            Cadena de datos con la comparación con el sector (gráfica del buffer decodificada). 
    """

    lista_dataframes = []
    bd = obtener_nombre_bd(ticker)
    model = apps.get_model('Analysis', ticker)
    # Último año aprox.
    entrada = model.objects.using(bd).order_by('-date')[:220].values('date', 'close', 'sector', 'name')
    df_ticker = read_frame(entrada.values('date', 'close'))

    # No excluyo el ticker 'objetivo' porque así lo meto
    # en la lista de los dataframes para nosrmalizar
    sector = list(entrada)[0]['sector']
    lista_mismo_sector = Sectores.objects.filter(sector=sector)

    for t in lista_mismo_sector:
        bd = obtener_nombre_bd(t.ticker_bd)
        model = apps.get_model('Analysis', t.ticker_bd)
        # Último año aprox.
        entrada = model.objects.using(bd).order_by('-date')[:220]
        df = pd.DataFrame(list(entrada.values()))
        # Adapto la fecha para hacer luego un merge por fecha
        df['date'] = df['date'].apply(lambda x: x.date())
        lista_dataframes.append(df[['date', 'close']])

    dfs_merged = _calcular_media_sector(lista_dataframes)

    # Normalizar para ver relación 'directa' sin precios
    df_ticker, dfs_merged = _normalizar_dataframes(df_ticker, dfs_merged)

    # FIGURA
    # ------
    fig = plt.figure(figsize=(7, 5))
    buffer = BytesIO()
    # Plot de la evolución de las variaciones diarias
    plt.plot(df_ticker['date'], df_ticker['normalizado'], label=ticker.replace("_", "."))
    plt.plot(dfs_merged['date'], dfs_merged['normalizado'], label=f'Media sector "{sector}"')
    # Título y estilos
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    # Elimino las etiquetas del eje 'y' porque se muestran
    # valores normalizados
    plt.gca().set_yticklabels([])
    # Ajusto los bins
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    # Y les doy formato a los meses
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.savefig(buffer, format="PNG")
    plt.close()

    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    grafica_sector = base64.b64encode(buffer.read()).decode()

    return grafica_sector


def _calcular_media_sector(lista_dataframes):
    """Para calcular la media de un sector. 

    Parameters
    ----------
        lista_dataframes : list
            Lista con los dataframes que contienen los precios de cierre y las fechas de los valores 
            que están en el mismo sector que el ticker 'objetivo'.

    Returns
    -------
        dfs_merged : pandas.core.frame.DataFrame
            Dataframe que ha pasado por un proceso de merging para equilibrar fechas y que tiene la 
            media de los cierres del sector.
    """
    # Empiezo con el primer dataframe de la lista
    dfs_merged = lista_dataframes[0]

    # Hago un merge sobre las fechas para eliminar
    # aquellos días en los que unos valores tengan datos
    # y otros no. Se pierde algo de info. pero los datos
    # serán coherentes
    for df in lista_dataframes[1:]:
        dfs_merged = pd.merge(dfs_merged, df, on='date', suffixes=('', '_'))

    # Calculo la columna con las medias del sector
    dfs_merged['media'] = dfs_merged.filter(like='close').mean(axis=1)

    # Elimino todas las columnas de cierres, porque ya no son
    # necesarias y cambio la media a 'close' para poder aprovechar
    # el método de normalizar dataframes
    dfs_merged = dfs_merged[['date', 'media']]
    dfs_merged = dfs_merged.rename(columns={'media': 'close'})

    return dfs_merged
