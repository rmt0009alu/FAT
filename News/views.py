"""
Métodos de vistas para usar con News.
"""
import os
import base64
# Para etiquetas de gráficos en castellano
import locale
from io import BytesIO
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Para usar django-pandas y frames
from django_pandas.io import read_frame
from django.shortcuts import render
# Para usar los modelos creados de forma dinámica
from django.apps import apps
from newsapi import NewsApiClient
# Para cargar variables de entorno
from dotenv import load_dotenv
# Para obtener los tickers y los paths de las BDs
from util.tickers.Tickers_BDs import tickers_adaptados_dj30, tickers_adaptados_ibex35, tickers_adaptados_ftse100
from util.tickers.Tickers_BDs import tickers_adaptados_dax40, tickers_adaptados_indices, obtener_nombre_bd

# Para evitar el "UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail"
# https://stackoverflow.com/questions/69924881/userwarning-starting-a-matplotlib-gui-outside-of-the-main-thread-will-likely-fa
matplotlib.use('agg')


def home(request):
    """Para llamar a home.html y mostrar el contenido
    de noticias junto con información de los mejores
    y peores stocks.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'home.html' con datos de contexto.
    """
    # NOTICIAS
    # ----------------------------------
    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    newsapi = NewsApiClient(api_key=news_api_key)

    # Creo un diccionario para las noticias
    top_headlines = newsapi.get_top_headlines(q='stock',
                                              category='business',
                                              country='us',
                                              language='en')

    # Con la clave 'articles' cojo los artículos de
    # la categoría indicada anteriormente
    mis_articulos = top_headlines['articles']
    noticias = []
    descripcion = []
    img = []
    lista_articulos = []
    urls = []

    for _, articulo in enumerate(mis_articulos):
        # Comprobar que los artículos tengan imagen
        if articulo['urlToImage'] is not None:
            noticias.append(articulo['title'])
            descripcion.append(articulo['description'])
            img.append(articulo['urlToImage'])
            urls.append(articulo['url'])

    # Crear la lista de artículos
    lista_articulos = list(zip(noticias, descripcion, img, urls))

    # MEJORES Y PEORES
    # ----------------------------------
    df_ultimos_dj30 = _mejores_peores(tickers_adaptados_dj30())
    mejores_dj30 = df_ultimos_dj30.head(3)
    perores_dj30 = df_ultimos_dj30.tail(3)

    df_ultimos_ibex35 = _mejores_peores(tickers_adaptados_ibex35())
    mejores_ibex35 = df_ultimos_ibex35.head(3)
    peores_ibex35 = df_ultimos_ibex35.tail(3)

    df_ultimos_ftse100 = _mejores_peores(tickers_adaptados_ftse100())
    mejores_ftse100 = df_ultimos_ftse100.head(3)
    peores_ftse100 = df_ultimos_ftse100.tail(3)

    df_ultimos_dax40 = _mejores_peores(tickers_adaptados_dax40())
    mejores_dax40 = df_ultimos_dax40.head(3)
    peores_dax40 = df_ultimos_dax40.tail(3)

    # GRÁFICOS DE STOCKS
    # ----------------------------------
    figuras_dj30 = _lista_de_graficos(mejores_dj30, perores_dj30)
    figuras_ibex35 = _lista_de_graficos(mejores_ibex35, peores_ibex35)
    figuras_ftse100 = _lista_de_graficos(mejores_ftse100, peores_ftse100)
    figuras_dax40 = _lista_de_graficos(mejores_dax40, peores_dax40)

    # CONTEXTO
    # ----------------------------------
    # Adaptación para mostrar los tickers del IBEX35 (u otros si los hubiera)
    # con notación de '.'
    df_ultimos_ibex35['ticker_bd'] = df_ultimos_ibex35['ticker']
    df_ultimos_ibex35['ticker'] = df_ultimos_ibex35['ticker'].str.replace('_', '.')
    mejores_ibex35 = df_ultimos_ibex35.head(3)
    peores_ibex35 = df_ultimos_ibex35.tail(3)

    df_ultimos_ftse100['ticker_bd'] = df_ultimos_ftse100['ticker']
    df_ultimos_ftse100['ticker'] = df_ultimos_ftse100['ticker'].str.replace('_', '.')
    mejores_ftse100 = df_ultimos_ftse100.head(3)
    peores_ftse100 = df_ultimos_ftse100.tail(3)

    df_ultimos_dax40['ticker_bd'] = df_ultimos_dax40['ticker']
    df_ultimos_dax40['ticker'] = df_ultimos_dax40['ticker'].str.replace('_', '.')
    mejores_dax40 = df_ultimos_dax40.head(3)
    peores_dax40 = df_ultimos_dax40.tail(3)

    context = {
        "listaArticulos": lista_articulos,
        "tresMejores_dj30": mejores_dj30,
        "tresPeores_dj30": perores_dj30,
        "tresMejores_ibex35": mejores_ibex35,
        "tresPeores_ibex35": peores_ibex35,
        "tresMejores_ftse100": mejores_ftse100,
        "tresPeores_ftse100": peores_ftse100,
        "tresMejores_dax40": mejores_dax40,
        "tresPeores_dax40": peores_dax40,
        "figuras_dj30": figuras_dj30,
        "figuras_ibex35": figuras_ibex35,
        "figuras_ftse100": figuras_ftse100,
        "figuras_dax40": figuras_dax40,
    }
    return render(request, "home.html", context)


def _mejores_peores(lista_tickers):
    """Para calcular los mejores y peores valores de la
    última sesión de cada base de datos.

    Parameters
    ----------
        lista_tickers : list
            Lista de tickers adaptados de cada bd.

    Returns
    -------
        df_ultimos : pandas.core.frame.DataFrame
            DataFrame con los datos ordenados de los stocks 
            según la variación en la última sesión.
    """
    # Inicializar lista vacía para mejorar rendimiento
    data = []

    for t in lista_tickers:
        if t not in tickers_adaptados_indices():
            # Para obtener los modelos de forma dinámica
            model = apps.get_model('Analysis', t)
            bd = obtener_nombre_bd(t)
            # Query de acceso a la BD
            ultima_entrada = model.objects.using(bd).values('percent_variance', 'ticker').order_by('-date').first()
            if ultima_entrada:
                data.append({
                    'ticker': ultima_entrada['ticker'],
                    'bd': bd,
                    'variacion': ultima_entrada['percent_variance']
                })

    # Crear DataFrame con la lista de diccionarios
    df_ultimos = pd.DataFrame(data)
    df_ultimos.sort_values(by='variacion', ascending=False, inplace=True, ignore_index=True)

    return df_ultimos


def _lista_de_graficos(mejores, peores):
    """Devuelve una lista con los gráficos de los stocks
    que están en 'mejores' y 'peores' para mostrarlos
    al usuario en la página principal.

    Parameters
    ----------
        mejores : pandas.core.frame.DataFrame
            DataFrame con los 3 mejores de la bd.

        peores : pandas.core.frame.DataFrame
            DataFrame con los 3 peores de la bd.

        bd : str
            Nombre e la bd.

    Returns
    -------
        figuras: list
            Lista con los gráficos de los mejores y peores.
    """
    tickers_mejores_peores = mejores['ticker'].tolist()
    for _, fila in peores.iterrows():
        tickers_mejores_peores.append(fila['ticker'])

    figuras = []

    for t in tickers_mejores_peores:
        # Para obtener los modelos de forma dinámica
        model = apps.get_model('Analysis', t)
        bd = obtener_nombre_bd(t)
        # Cojo las últimas 252 sesiones de cada stock (aprox. 1 año)
        entradas = model.objects.using(bd).order_by('-date')[:252].values('date', 'close', 'ticker', 'name')
        figura = _generar_figura(entradas)
        # Añado la figura a la lista de figuras (con mpld3 se pierde
        # configuración y se gana interactividad):
        # figuras.append(mpld3.fig_to_html(figura))
        figuras.append(figura)

    return figuras


def _generar_figura(entradas):
    """Para generar las figuras de los stocks que están
    entre los mejores/peores del último día.

    Parameters
    ----------
        entradas : django.db.models.query.QuerySet
            Los últimos 200 registros del ticker asociado.

    Returns
    -------
        figura : str
            La figura que se crea, codificada en base64.
    """
    # Obtener los 'values' del queryset 'entradas'
    # y pasar a df
    df = read_frame(entradas.values('date', 'close', 'name'))

    # Creo la figura de Matplotlib.pyplot
    plt.figure(facecolor='white')

    plt.plot(df['date'], df['close'], color='#212428', linewidth=2, label='Cierre')
    plt.fill_between(df['date'], df['close'], color='#212428', alpha=0.2)
    plt.ylabel('Cierre', fontsize=10)
    # +/- 1% en los límites
    plt.ylim(df['close'].min()/1.01, df['close'].max()*1.01)
    plt.xlim(df['date'].min(), df['date'].max())
    nombre = df['name'].iat[0]
    plt.title(f'{nombre}', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5, linewidth=0.5, color='gray')
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(6))

    # Mostrar nombres de meses en lugar de fechas ()
    # locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    # Modificación para evitar error de GitHub actions de Coverage: 'locale.Error: unsupported locale setting'
    # Idea sacada de: https://github.com/israel-dryer/ttkbootstrap/issues/505
    locale.setlocale(locale.LC_ALL, locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8'))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='PNG')
    plt.close()
    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    figura = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    figura = f'<img src="data:image/png;base64,{figura}">'

    return figura
