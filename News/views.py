from django.shortcuts import render
from newsapi import NewsApiClient
# Para obtener los tickers y los paths de las BDs
from util.tickers.Tickers_BDs import tickersAdaptadosDJ30, tickersAdaptadosIBEX35, nombre_bdDJ30, nombre_bdIBEX35, tickersAdaptadosIndices
# Para usar django-pandas y frames
from django_pandas.io import read_frame
# Para usar los modelos creados de forma dinámica
from django.apps import apps

import pandas as pd
import matplotlib.pyplot as plt
import mpld3

# Para evitar el "UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail"
# https://stackoverflow.com/questions/69924881/userwarning-starting-a-matplotlib-gui-outside-of-the-main-thread-will-likely-fa
import matplotlib
matplotlib.use('agg')


def home(request):
    """Para llamar a home.html y mostrar el contenido
    de noticias junto con información de los mejores
    y peores stocks.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): request

    Returns:
        (function): render
    """
    # NOTICIAS
    # ----------------------------------
    newsapi = NewsApiClient(api_key='a3c6c53f961941279b2daee097261b5d')

    # Creo un diccionario para las noticias
    top_headlines = newsapi.get_top_headlines(q='stock',
                                              category='business',
                                              language='en')

    # Con la clave 'articles' cojo los artículos de
    # la categoría indicada anteriormente
    misArticulos = top_headlines['articles']
    noticias = []
    descripcion = []
    img = []
    listaArticulos = []
    urls = []

    for i in range(len(misArticulos)):
        articulo = misArticulos[i]
        # Comprobar que los artículos tengan imagen
        if articulo['urlToImage'] is not None:
            noticias.append(articulo['title'])
            descripcion.append(articulo['description'])
            img.append(articulo['urlToImage'])
            urls.append(articulo['url'])

            listaArticulos = zip(noticias, descripcion, img, urls)

    # MEJORES Y PEORES
    # ----------------------------------
    df_ultimos_dj30 = getMejoresPeores(tickersAdaptadosDJ30(), nombre_bdDJ30())
    mejores_dj30 = df_ultimos_dj30.head(3)
    perores_dj30 = df_ultimos_dj30.tail(3)

    df_ultimos_ibex35 = getMejoresPeores(tickersAdaptadosIBEX35(), nombre_bdIBEX35())
    mejores_ibex35 = df_ultimos_ibex35.head(3)
    peores_ibex35 = df_ultimos_ibex35.tail(3)

    # GRÁFICOS DE STOCKS
    # ----------------------------------
    figuras_dj30 = getListaGraficos(mejores_dj30, perores_dj30, nombre_bdDJ30())
    figuras_ibex35 = getListaGraficos(mejores_ibex35, peores_ibex35, nombre_bdIBEX35())

    # CONTEXTO
    # ----------------------------------
    # Adaptación para mostrar los tickers del IBEX35 (u otros si los hubiera)
    # con notación de '.'
    df_ultimos_ibex35['ticker'] = df_ultimos_ibex35['ticker'].str.replace('_', '.')
    mejores_ibex35 = df_ultimos_ibex35.head(3)
    peores_ibex35 = df_ultimos_ibex35.tail(3)

    context = {
        "listaArticulos": listaArticulos,
        "tresMejores_dj30": mejores_dj30,
        "tresPeores_dj30": perores_dj30,
        "tresMejores_ibex35": mejores_ibex35,
        "tresPeores_ibex35": peores_ibex35,
        "figuras_dj30": figuras_dj30,
        "figuras_ibex35": figuras_ibex35,
    }

    return render(request, "home.html", context)


def getMejoresPeores(listaTickers, bd):
    # DataFrame que voy a devolver
    df_ultimos = pd.DataFrame(columns=['ticker', 'variacion'])

    # Nombre de la app para acceder a los modelos
    miApp = 'Analysis'

    for t in listaTickers:
        if t not in tickersAdaptadosIndices():
            # Para obtener los modelos de forma dinámica
            model = apps.get_model(miApp, t)
            try:
                # Query de acceso a la BD
                ultimaEntrada = model.objects.using(bd).values('percent_variance', 'ticker').order_by('-date').first()
                if ultimaEntrada:
                    datos = {'ticker': ultimaEntrada['ticker'], 'variacion': ultimaEntrada['percent_variance']}
                    # Pandas append() deprecated:
                    # https://stackoverflow.com/questions/75956209/error-dataframe-object-has-no-attribute-append
                    # df_ultimosRegistros = df_ultimosRegistros.append(datos, ignore_index=True)
                    # https://stackoverflow.com/questions/77254777/alternative-to-concat-of-empty-dataframe-now-that-it-is-being-deprecated
                    df_ultimos = pd.concat([df_ultimos if not df_ultimos.empty else None,
                                            pd.DataFrame([datos])], ignore_index=True)
                else:
                    print("Sin datos en", t)
            except Exception as ex:
                print("[NO OK] Error: ", ex)

    df_ultimos.sort_values(by='variacion', ascending=False, inplace=True, ignore_index=True)

    return df_ultimos


def getListaGraficos(mejores, peores, bd):
    """Devuelve una lista con los gráficos de los stocks
    que están en 'mejores' y 'peores' para mostrarlos
    al usuario en la página principal.

    Args:
        mejores (_type_): _description_
        peores (_type_): _description_
        bd (_type_): _description_

    Returns:
        _type_: _description_
    """
    tickersMejoresPeores = mejores['ticker'].tolist()
    for _, fila in peores.iterrows():
        tickersMejoresPeores.append(fila['ticker'])

    figuras = []

    # Nombre de la app para acceder a los modelos
    miApp = 'Analysis'

    for t in tickersMejoresPeores:
        # Para obtener los modelos de forma dinámica
        model = apps.get_model(miApp, t)
        try:
            # Cojo las últimas 200 entradas de cada stock:
            entradas = model.objects.using(bd).order_by('-date')[:200].values('date', 'close', 'ticker', 'name')
            figura = generarFigura(entradas)
            # Añado la figura a la lista de figuras
            figuras.append(mpld3.fig_to_html(figura))

            # Conviene ir cerrando los plots abiertos para que no
            # haya problemas de memoria (de hecho, si no hago
            # un plt.close() salta un warning)
            plt.close()

        except Exception as ex:
            print("[NO OK] Error: ", ex)

    return figuras


def generarFigura(entradas):
    """Para generar las figuras de los stocks que están
    entre los mejores/peores del último día.

    Args:
        entradas (queryset): los últimos 200 registros del
            ticker asociado
        ticker (str): nombre del ticker

    Returns:
        (matplotlib.figure.Figure): la figura que se crea
    """
    # Obtener los 'values' del queryset 'entradas'
    # y pasar a df
    df = read_frame(entradas.values('date', 'close', 'name'))

    # Creo la figura de Matplotlib.pyplot
    fig, ax = plt.subplots()
    ax.plot(df['date'], df['close'])
    nombre = df['name'].iat[0]
    ax.set(xlabel='Fecha', ylabel='Cierre', title=f'{nombre}')

    ax.grid(True, linestyle='--', alpha=0.5)
    # ax.set_xticklabels(ax.get_xticklabels(), rotate=45)

    return fig
