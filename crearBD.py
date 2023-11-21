import yfinance as yf
import sqlite3
import pandas as pd
# from datetime import datetime, timedelta
# from alpha_vantage.timeseries import TimeSeries
# from iexfinance.stocks import Stock, get_historical_data



# Lista de tickers para el DJ30
# dj30 = [
#     "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG",
#     "TSLA", "BRK-B", "JPM", "JNJ", "NVDA",
#     "HD", "MA", "DIS", "V", "PYPL",
#     "INTC", "ADBE", "CRM", "NFLX", "CMCSA",
#     "KO", "T", "PEP", "CSCO", "XOM",
#     "VZ", "PFE", "ABBV", "WMT", "MRK"
# ]

ibex35 = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
         'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
         'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
         'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
         'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
         'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
         'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
         'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
         'SLR.MC', 'TEF.MC', 'UNI.MC']

for ticker in ibex35:

    stock = yf.Ticker(ticker)
    # Para ver las claves de un diccionario que contiene info. 
    # actualizada en el mismo día. Útil para mostrar datos 
    # con llamada directa a API (sin usar BD)
    # 
    # data = stock.fast_info
    # print("Moneda: ", data['currency'], "Máx. 52s: ", data['yearHigh'])
    #
    # Para ver todas las claves del diccionario
    # print(data)

    # Para obtener info. histórica hay dos métodos:
    # history() y download(). Me gusta más history
    # 
    # tickers = ["AAPL", "MSFT"]
    # historical_data = yf.download(tickers, start="2023-10-19", end="2023-11-19")
    #
    # hist = stock.history(period="1d")
    # hist = stock.history(period="max", interval="1wk")
    hist = stock.history(period="max", interval="1d")
    # Añadir columnas. MUY IMPORTANTE: INTERESA TENER NOMBRES 
    # EN INGLÉS PARA TRABAJAR CON OTRAS LIBRERÍAS COMO 'mplfinance'
    hist['Ticker'] = ticker
    hist['Previous_Close'] = hist['Close'].shift(1)

    # Añadir columna para el porcentaje de variación entre días
    hist['Percent_Variance'] = ((hist['Close'] - hist['Previous_Close']) / hist['Previous_Close']) * 100

    # Añado las columnas de las medias móviles. Esto se podría
    # calcular 'sobre la marcha' pero es másrápido tenerlo almacenado
    hist['MM20'] = hist['Close'].rolling(window=20).mean()
    hist['MM50'] = hist['Close'].rolling(window=50).mean()
    hist['MM200'] = hist['Close'].rolling(window=200).mean()


    # Conexión a la BD (si no existe, se crea)
    # conn = sqlite3.connect('IBEX35.db')
    # conn = sqlite3.connect('IBEX35.sqlite3')
    conn = sqlite3.connect('./databases/db.sqlite3')

    # Pasar del DataFrame a la BD
    hist.to_sql(ticker, conn, index=True, if_exists='replace')

    # Cerrar conexión a la BD
    conn.close()
    # Eliminar los NaN de las primeras filas implica
    # eliminar todas esas filas pero puede merecer
    # la pena perder info de 200 días para poder
    # trabajar sin NaN
    #
    # hist = hist.dropna()

# print(hist)

# for index, row in hist.iterrows():
#     if row['Dividends'] != 0:
#         print(row)



