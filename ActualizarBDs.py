import yfinance as yf
import sqlite3
import pandas as pd
import logging

from logging.handlers import RotatingFileHandler
from datetime import datetime


def crearLogger():
    """Para configurar un log de las actualizaciones de las 
    BD de los stocks. 
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Formateador para el handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    # Configurar handler con nombre de archivo en el 
    # que almacenar el log
    handlerArchivo = RotatingFileHandler('log/ActualizacionesDeBDs.log', 
                                         maxBytes=10*1024*1024, backupCount=5, 
                                         encoding='utf-8')
    handlerArchivo.setLevel(logging.INFO)
    handlerArchivo.setFormatter(formatter)

    # Añadir el handler al logger
    logger.addHandler(handlerArchivo)

    # Handler para ver datos en consola
    handlerConsola = logging.StreamHandler()
    handlerConsola.setLevel(logging.INFO)
    handlerConsola.setFormatter(formatter)
    logger.addHandler(handlerConsola)

    return logger



def actualizarBD(indice, bd, logger):
    """Para actualizar la BD sin tener que crear una nueva completa
    o sobreescribir todo lo que había en la BD. 

    Args: 
        índice (list): lista con los tickers que se quieren 
            actualizar. 
    """
    logger.info("")
    logger.info("-------------------------------------------------")
    logger.info("Actualizando base de datos con los últimos datos:")
    logger.info("-------------------------------------------------")

    # Conexión a la BD
    conn = sqlite3.connect(bd)

    try:
        # Uso una transacción para asegurar la atomicidad
        with conn:
            for ticker in indice:
                
                stock = yf.Ticker(ticker)
                info = stock.info

                # Nombre de la compañía
                nombre = info['longName']

                # Flag para comprobar estado del mercado
                # abierto = bool
                
                # Estado de actividad (si está en mercado
                # abierto o cerrado). Cuando está cerrado
                # regularMarketOpen es 0
                # if info.get('regularMarketOpen') == 0.0:
                #     abierto = False
                # else:
                #     abierto = True
                
                # if abierto:
                if not permiteActualizar(logger):
                    logger.info(" - [Fuera de horario] No se puede actualizar. %s", nombre)
                else:
                    # Obtener la última fecha registrada en la tabla
                    # Los ticker con sufijo pasan de '.' a '_'. Los 
                    # que no tienen sufijo se quedan igual
                    ticker_cambiado = ticker.replace(".", "_")
                    query = f"SELECT MAX(Date) FROM {ticker_cambiado}"
                    last_date_str = conn.execute(query).fetchone()[0]

                    # Convertir la última fecha a un objeto datetime
                    last_date = pd.to_datetime(last_date_str)

                    # Obtener los datos desde último día, incluido, para
                    # calcular el % de cambio con el Previous_Close
                    hist = stock.history(start=last_date, end=pd.to_datetime('today'))

                    # Comprobar si la última fecha disponible ya está 
                    # en la BD (en tal caso, ya está actualizado). Tener
                    # en cuenta que aquí hist['Date'] no existe porque
                    # 'Date' es el index:
                    if not hist.empty and (hist.index.max() != last_date):
                        # Mostrar el nombre de la compañía actualizada en la BD
                        logger.info(" - [Actualizando... ] %s", nombre)

                        # Actualizar las columnas adicionales (porcentaje de 
                        # variación, medias móviles, etc.)
                        hist['Ticker'] = ticker_cambiado
                        hist['Previous_Close'] = hist['Close'].shift(1)

                        # Variación entre cierres
                        hist['Percent_Variance'] = ((hist['Close'] - hist['Previous_Close']) / hist['Previous_Close']) * 100

                        # Medias móviles nulas porque aquí no tengo
                        # la info. suficiente
                        hist['MM20'] = None
                        hist['MM50'] = None
                        hist['MM200'] = None

                        # Nombre de la compañía
                        hist['Name'] = nombre

                        # Elimino la primera fila porque es la del 
                        # último día registrado
                        hist = hist.iloc[1:]

                        # Insertar los nuevos datos en la tabla existente
                        # IMPORTANTE: en lugar de 'replace' uso 'append'
                        hist.to_sql(ticker_cambiado, conn, index=True, if_exists='append')
                        
                        # Commit
                        conn.commit()
                        logger.info("\t\t[OK] Datos")
                    
                        # Actualizo las medias móviles
                        calcularMediasMoviles(conn, ticker_cambiado, logger)

                    else:
                        logger.info(" - [Sin datos nuevos] %s", nombre)

        # Si todo ha ido bien
        logger.info("")
        logger.info("[OK] Base de datos actualizada.")

    except sqlite3.Error as ex1:
        logger.error("[NO OK] Error SQLite: %s", ex1)

    except Exception as ex2: 
        logger.error("[NO OK] Fallo al actualizar base de datos. Error: %s", ex2)

    finally:
        # Cerrar conexión a la BD
        conn.close()
        logger.info("Proceso finalizado.\n")

    return



def calcularMediasMoviles(conn, ticker, logger):
    """Una vez se obtienen los nuevos datos de un ticker, 
    hay que actualizar las medias móviles, porque son un
    dato calculado. 

    Args:
        conn (sqlite3.Connection): conexión a la BD.
        ticker (str): ticker del stock que se quiere actualizar.
    """
    try:
        # Consultar datos desde la BD
        query = f"SELECT * FROM {ticker}"
        data = pd.read_sql_query(query, conn, index_col='Date')

        # Calcular las medias móviles
        data['MM20'] = data['Close'].rolling(window=20).mean()
        data['MM50'] = data['Close'].rolling(window=50).mean()
        data['MM200'] = data['Close'].rolling(window=200).mean()

        # Actualizar los datos en la BD
        data.to_sql(ticker, conn, index=True, if_exists='replace')

        # Commit
        conn.commit()
        logger.info("\t\t[OK] Medias móviles")

    except Exception as ex:
        logger.error("[NO OK] Fallo al calcular medias móviles. Error %s", ex)

    return



def permiteActualizar(logger):
    try:
        # Horario UTC actual
        horarioUTC = datetime.utcnow()

        # Horario permitido fuera de los tiempos
        # de apertura y subastas
        inicio = horarioUTC.replace(hour=4, minute=0, second=0, microsecond=0)
        fin = horarioUTC.replace(hour=5, minute=30, second=0, microsecond=0)

        # Comprobar si la ejecución está en
        # el horario permitido
        return inicio <= horarioUTC <= fin

    except Exception as ex:
        logger.error("[NO OK] Fallo horario. Error %s", ex)
        return False
    

#######################################################
if __name__ == "__main__":

    logger = crearLogger()

    # -----------------------------------------------------
    # Actualizar la BD del DJ30 
    dj30 = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT']
    
    bd = 'databases/dj30.sqlite3'
    actualizarBD(dj30, bd, logger)

    # -----------------------------------------------------
    # Actualizar la BD del IBEX35
    ibex35 = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
         'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
         'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
         'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
         'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
         'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
         'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
         'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
         'SLR.MC', 'TEF.MC', 'UNI.MC']

    bd = 'databases/ibex35.sqlite3'
    actualizarBD(ibex35, bd, logger)
    