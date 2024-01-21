import yfinance as yf
import sqlite3
import pandas as pd
import logging
import os

from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from tickers import Tickers_BDs



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
    # IMPORTANTE: PARA USO LOCAL ES DISTINTO AL USO EN SERVER:
    # El path por defecto es el de la máquina local
    LOG_PATH = './log'
    # Si no existe ese path es porque estoy en el server
    if not os.path.exists(LOG_PATH):
        LOG_PATH = './FAT/log'
    
    LOG_PATH = LOG_PATH + '/ActualizacionesDeBDs.log'

    handlerArchivo = RotatingFileHandler(LOG_PATH, 
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

    DB_PATH = bd

    # Comprobación de path y BD existente
    if not os.path.exists(DB_PATH):
        DB_PATH = './FAT/' + bd

    # Conexión a la BD
    conn = sqlite3.connect(DB_PATH)

    try:
        # Uso una transacción para asegurar la atomicidad
        with conn:
            for ticker in indice:
                
                stock = yf.Ticker(ticker)
                info = stock.info

                # Nombre de la compañía
                nombre = info['longName']

                # Coprobar horarios para actualizar de forma adecuada
                # según las actualizaciones de la API de yfinance
                if not permiteActualizar(logger):
                    logger.info(" - [Fuera de horario] No se puede actualizar. %s", nombre)
                else:
                    # NOTA: de nuevo se usan queries directas a las BDs 
                    # porque cuando se actualizan las BDs, igual que cuando
                    # se crean, los modelos no están cargados

                    # Obtener la última fecha registrada en la tabla
                    # Los ticker con sufijo pasan de '.' a '_'. Los 
                    # que no tienen sufijo se quedan igual
                    ticker_cambiado = ticker.replace(".", "_")
                    # Adaptar también los índices:
                    ticker_cambiado = ticker_cambiado.replace("^", "")
                    query = f"SELECT MAX(Date) FROM {ticker_cambiado}"
                    cursor = conn.cursor()
                    last_date_str = cursor.execute(query).fetchone()[0]
                    # Convertir la última fecha a un objeto datetime
                    last_date = pd.to_datetime(last_date_str)
                    cursor.close()

                    # Obtener el último 'id' registrado
                    query = f"SELECT MAX(id) FROM {ticker_cambiado}"
                    cursor = conn.cursor()
                    last_id = cursor.execute(query).fetchone()[0]
                    cursor.close()

                    # Si fuera necesario comprobar el nombre de las columnas:
                    # query = f"PRAGMA table_info({ticker_cambiado})"
                    # cursor.execute(query)
                    # column_names = [info[1] for info in cursor.fetchall()]
                    # print(column_names)

                    # Obtener los datos desde último día, incluido, para
                    # calcular el % de cambio con el Previous_Close
                    if pd.to_datetime('today').date() > last_date.date():
                        hist = stock.history(start=last_date, end=pd.to_datetime('today'))

                        # Dejo la columna 'date' como columna normal (no índice)
                        hist.reset_index(inplace=True)
                        # Aseguro que el formato de 'Date' será el adecuado 
                        # 'TIMESTAMP' en las BDs. Sumo horas para evitar
                        # problemas con los cambios horarios (si se cogen
                        # datos a las 00:00 +01 en UTC aparece como el día 
                        # anterior). Como solo me interesan los datos de cierre,
                        # con esto aseguro que las fechas serán adecuadas y, 
                        # además, lo almaceno con los horarios de cierre según
                        # hora española
                        if bd == Tickers_BDs.ruta_bdDJ30():
                            hist['Date'] = pd.to_datetime(hist['Date']) + timedelta(hours=17, minutes=30)
                        elif bd == Tickers_BDs.ruta_bdIBEX35():
                            hist['Date'] = pd.to_datetime(hist['Date']) + timedelta(hours=18, minutes=30)

                        # Uso una columna 'id' explícitamente. Es recomendable en
                        # Django, por eso lo tengo definido en los modelos dinámicos
                        # de manera autoincremental. Pero aunque sea autoincremental, 
                        # al acceder de forma directa a la BD, tengo que indicar cómo
                        # es ese 'id' porque, si no, cogerá los valores de 'id' del
                        # nuevo 'hist':
                        hist['id'] = range(last_id , last_id + len(hist))
                        hist.set_index('id', inplace=True)

                        # Comprobar que 'hist' no está vacío
                        if not hist.empty and (hist['Date'].max().date() != last_date.date()):
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
                            hist.to_sql(ticker_cambiado, conn, index=True, index_label='id', if_exists='append')
                            
                            # Commit
                            conn.commit()
                            logger.info("\t\t[OK] Datos")
                        
                            # Actualizo las medias móviles
                            calcularMediasMoviles(conn, ticker_cambiado, logger)
                        else:
                            # Hoy es mayor que la fecha del último registro
                            # pero no hay datos por festivo, fin de semana o mercado
                            # todavía no abierto
                            logger.info(" - [Sin datos nuevos] %s", nombre)
                    else:
                        # Hoy no es mayor que fecha de último registro
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

    # Para actualizar paso lista de tickers sin adaptar para hacer
    # las llamadas adecuadas a la API de yfinance. Se adaptan en
    # en el código
    
    # Actualizar la BD del DJ30 
    dj30 = Tickers_BDs.tickersDJ30()
    bd = Tickers_BDs.ruta_bdDJ30()
    actualizarBD(dj30, bd, logger)

    # Actualizar la BD del IBEX35
    ibex35 = Tickers_BDs.tickersIBEX35()
    bd = Tickers_BDs.ruta_bdIBEX35()
    actualizarBD(ibex35, bd, logger)
    