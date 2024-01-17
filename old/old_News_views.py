from django.shortcuts import render
from newsapi import NewsApiClient
import sqlite3
import pandas as pd

# Para obtener los tickers y los paths de las BDs
from tickers.tickersYBDs import tickersDJ30, bdDJ30, tickersIBEX35, tickersAdaptadosIBEX35, bdIBEX35

# Para usar los modelos creados de forma dinámica
from django.apps import apps



def getDatosStock(symbol):
    # Conectar a la BD
    conn = sqlite3.connect('databases/dj30.sqlite3')

    # Sentencia SQL
    query = f"SELECT * FROM '{symbol}' ORDER BY ROWID DESC LIMIT 200;"
    
    # Ejecutar la sentencia y pasar a DataFrame
    ticker_data = pd.read_sql_query(query, conn)


    # Paso la colunma 'Date' a datetime y ordeno por fecha
    ticker_data["Date"] = pd.to_datetime(ticker_data["Date"], utc=True)
    ticker_data = ticker_data.sort_values(by="Date", ascending=True)

    # Cerrar conexión con BD
    conn.close()

    return ticker_data



def home(request):

    # NOTICIAS
    # ----------------------------------
    newsapi = NewsApiClient(api_key='')

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
        noticias.append(articulo['title'])
        descripcion.append(articulo['description'])
        img.append(articulo['urlToImage'])
        urls.append(articulo['url'])
    
        listaArticulos = zip(noticias, descripcion, img, urls)

    # DATOS DE STOCKS
    # ----------------------------------
    # stock_data = getDatosStock('AAPL')
    # stock_dates_AAPL = stock_data['Date'].tolist()
    # stock_dates_AAPL = [d.strftime('%Y-%m-%d') for d in stock_dates_AAPL]
    # stock_prices_AAPL = stock_data['Close'].tolist()

    # stock_data = getDatosStock('MSFT')
    # stock_dates_MSFT = stock_data['Date'].tolist()
    # stock_dates_MSFT = [d.strftime('%Y-%m-%d') for d in stock_dates_MSFT]
    # stock_prices_MSFT = stock_data['Close'].tolist()

    # stock_data = getDatosStock('IBM')
    # stock_dates_IBM = stock_data['Date'].tolist()
    # stock_dates_IBM = [d.strftime('%Y-%m-%d') for d in stock_dates_IBM]
    # stock_prices_IBM = stock_data['Close'].tolist()
    tickers_dj30 = tickersDJ30()

    miApp = 'News'

    for t in tickers_dj30:
        # Para obtener los modelos de forma dinámica
        model = apps.get_model(miApp, t)
        try:
            entries = model.objects.using('dj30').order_by('-date')[:200].values('percent_variance', 'ticker', 'date')
        except Exception as ex:
            print("[NO OK] Error: ", ex)


    # MEJORES Y PEORES
    # ----------------------------------
    # tickers_dj30 = tickersDJ30()

    # miApp = 'News'
    
    df_ultimos = pd.DataFrame(columns=['ticker', 'variacion'])

    for t in tickers_dj30:
        # Para obtener los modelos de forma dinámica
        model = apps.get_model(miApp, t)
        try:
            # Query de acceso a la BD dj30
            ultimaEntrada = model.objects.using('dj30').values('percent_variance', 'ticker').order_by('-date').first()
            if ultimaEntrada:
                datos = {'ticker': ultimaEntrada['ticker'], 'variacion': ultimaEntrada['percent_variance']}
                # Pandas append() deprecated: https://stackoverflow.com/questions/75956209/error-dataframe-object-has-no-attribute-append
                # df_ultimosRegistros = df_ultimosRegistros.append(datos, ignore_index=True)
                df_ultimos = pd.concat([df_ultimos, pd.DataFrame([datos])], ignore_index=True)
            else:
                print("Sin datos en", t)
        except Exception as ex:
            print("[NO OK] Error: ", ex)
    
    df_ultimos.sort_values(by='variacion', ascending=False, inplace=True, ignore_index=True)

    tresMejores = df_ultimos.head(3)
    tresPeores = df_ultimos.tail(3)

    context = {
        "listaArticulos": listaArticulos,
        "stockDataList": [
            {"symbol": "Apple Inc.", "dates": stock_dates_AAPL, "prices": stock_prices_AAPL},
            {"symbol": "Microsoft Corporation", "dates": stock_dates_MSFT, "prices": stock_prices_MSFT},
            {"symbol": "International Business Machines Corporation", "dates": stock_dates_IBM, "prices": stock_prices_IBM},
        ],
        "tresMejores": tresMejores,
        "tresPeores": tresPeores,
    }
    return render(request, "home.html", context)