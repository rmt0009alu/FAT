from logging.handlers import RotatingFileHandler
from datetime import timedelta
from tickers import Tickers_BDs
from datetime import datetime

import yfinance as yf
import sqlite3
import logging
import pandas as pd


def crear_logger():
    """Para configurar un log de la creación de las 
    BD de los stocks. 
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Formateador para el handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    # Configurar handler con nombre de archivo en el 
    # que almacenar el log
    handlerArchivo = RotatingFileHandler('log/CreaciónDeBDs.log', 
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



def crear_bds(índice, bd, logger):

    logger.info("")
    logger.info("------------------------------------------")
    logger.info("Creando bases de datos:")
    logger.info("------------------------------------------")

    # Conexión a la BD (si no existe, se crea)
    conn = sqlite3.connect(bd)

    try:
        # Uso una transacción para asegurar la atomicidad:
        with conn:
            for ticker in índice:

                stock = yf.Ticker(ticker)
                
                # Selecciono el máximo de datos posible de cada stock
                # excepto para el FTSE100 porque son muchos stocks y 
                # la BD crece demasiado (130MB) y podría ser un problema 
                # en GitHub y en el servidor de la web:
                if bd == 'databases/ibex35.sqlite3':
                    hist = stock.history(period="max", interval="1d")
                else:
                    hist = stock.history(period="5y", interval="1d")

                # Dejo la columna 'date' como columna normal
                hist.reset_index(inplace=True)
                # Aseguro que el formato de 'Date' será el adecuado 
                # 'TIMESTAMP' en las BDs. Sumo horas para evitar
                # problemas con los cambios horarios (si se cogen
                # datos a las 00:00 +01 en UTC aparece como el día 
                # anterior). Como solo me interesan los datos de cierre,
                # con esto aseguro que las fechas serán adecuadas y, 
                # además, lo almaceno con los horarios de cierre según
                # hora española
                if bd == 'databases/dj30.sqlite3':
                    hist['Date'] = pd.to_datetime(hist['Date']) + timedelta(hours=17, minutes=30)
                elif bd == 'databases/ibex35.sqlite3':
                    hist['Date'] = pd.to_datetime(hist['Date']) + timedelta(hours=18, minutes=30)
                elif bd == 'databases/ftse100.sqlite3':
                    hist['Date'] = pd.to_datetime(hist['Date']) + timedelta(hours=17, minutes=30)
                elif bd == 'databases/dax40.sqlite3':
                    hist['Date'] = pd.to_datetime(hist['Date']) + timedelta(hours=18, minutes=30)

                # No uso una columna 'id' explícitamente. Es recomendable en
                # Django, por eso lo tengo definido en los modelos dinámicos
                # de manera autoincremental. En cualquier caso, podría ser así:
                # hist['id'] = range(1, len(hist) + 1)
                # hist.set_index('id', inplace=True)

                # Guardo un nombre de Ticker igual al nombre de la tabla
                # en la que se va a guardar. Los ticker que tienen sufijo
                # cambian el '.' por '_'. Los que no tienen sufijo, se 
                # mantienen igual
                ticker_cambiado = ticker.replace(".", "_")
                # Los índices, con prefijo ^, también se cambian
                ticker_cambiado = ticker_cambiado.replace("^", "")

                # Añadir columnas. MUY IMPORTANTE: INTERESA TENER NOMBRES 
                # EN INGLÉS PARA TRABAJAR CON OTRAS LIBRERÍAS COMO 'mplfinance'
                hist['Ticker'] = ticker_cambiado
                # hist['Ticker'] = ticker
                
                # Guardo el cierre previo para calcular el % de cambio
                hist['Previous_Close'] = hist['Close'].shift(1)

                # Añadir columna para el porcentaje de variación entre días
                hist['Percent_Variance'] = ((hist['Close'] - hist['Previous_Close']) / hist['Previous_Close']) * 100

                # Añado las columnas de las medias móviles. Esto se podría
                # calcular 'sobre la marcha' pero es másrápido tenerlo almacenado
                hist['MM20'] = hist['Close'].rolling(window=20).mean()
                hist['MM50'] = hist['Close'].rolling(window=50).mean()
                hist['MM200'] = hist['Close'].rolling(window=200).mean()

                # Para guardar el nombre de la compañía
                info = stock.info
                nombre = info['longName']
                hist['Name'] = nombre

                # Para guardar el sector al que pertenece la compañía
                sector = info.get('sector', 'Sector information not available')
                hist['Sector'] = sector

                # Para guardar la moneda en la que cotiza
                currency = info.get('currency', 'Currency information not available')
                hist['Currency'] = currency

                # Comprobar existencia de tabla
                if conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ticker_cambiado}'").fetchone():
                    # Pasar del DataFrame a la BD. NOTA: AQUÍ SÍ
                    # INDICO QUÉ COLUMNA SERÁ EL INDEX:
                    hist.to_sql(ticker_cambiado, conn, index=True, index_label='id', if_exists='replace')
                    # Mostrar el nombre de la compañía agregada a la BD
                    logger.info(" - [OK] %s", nombre)

                else:
                    logger.error(" - [NO OK] Error en base de datos. Tabla %s no existe", nombre)

        # Si todo ha ido bien:
        logger.info("")
        logger.info("[OK] Bases de datos creadas.")

    except sqlite3.Error as ex1:
        logger.error("[NO OK] Error SQLite: %s", ex1)

    except Exception as ex2: 
        logger.error("[NO OK] Fallo al crear bases de datos. Error: %s", ex2)

    finally:
        # Cerrar conexión a la BD
        conn.close()
        logger.info("Proceso finalizado.")

    return
    

def crear_tabla_sectores(índices, logger):

    logger.info("")
    logger.info("------------------------------------------")
    logger.info("Creando tabla de sectores en 'db.sqlite3':")
    logger.info("------------------------------------------")

    datos = []
    for ticker in índices:
        stock = yf.Ticker(ticker)

        ticker_cambiado = ticker.replace(".", "_")
        # Los índices, con prefijo ^, también se cambian
        ticker_cambiado = ticker_cambiado.replace("^", "")

        bd = Tickers_BDs.obtener_nombre_bd(ticker_cambiado)

        # Para bd, nombre largo y sector
        info = stock.info
        datos.append({'Ticker_bd': ticker_cambiado, 
                      'BaseDatos': bd,
                      'Ticker': ticker,
                      'Nombre': info['longName'], 
                      'Sector': info.get('sector', 'Sector information not available')})
        
    try:
        conn = sqlite3.connect('databases/db.sqlite3')
        cursor = conn.cursor()
        # No puedo usar algo parecido a esto porque la tabla la relleno
        # al ejecutar este script, i.e., lo modelos no están cargados. 
        # Sectores.objects.bulk_create(datos)
        #
        # Así que accedo directamente a la BD:
        for dato in datos:
            # No hace falta el 'id' porque es autoincremental
            query = """
                INSERT INTO Analysis_sectores (Ticker_bd, BaseDatos, Ticker, Nombre, Sector)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (dato['Ticker_bd'], dato['BaseDatos'], dato['Ticker'], dato['Nombre'], dato['Sector']))

            # Mostrar el nombre de la compañía agregada a la BD
            logger.info(" - [OK] %s", dato['Nombre'])

        conn.commit()

        # Si todo ha ido bien:
        logger.info("")
        logger.info("[OK] Tabla creada con éxito.")

    except sqlite3.Error as ex1:
        logger.error("[NO OK] Error SQLite: %s", ex1)

    except Exception as ex2: 
        logger.error("[NO OK] Fallo al crear la tabla. Error: %s", ex2)

    finally:
        # Cerrar conexión a la BD
        conn.close()
        logger.info("Proceso finalizado.")

    return


def crear_tabla_cambio_moneda(pares_monedas, logger):

    logger.info("")
    logger.info("--------------------------------------------------")
    logger.info("Creando tabla de cambio de moneda en 'db.sqlite3':")
    logger.info("--------------------------------------------------")

    datos = []
    for par in pares_monedas:
        ticker = yf.Ticker(par)
        info = ticker.info

        # Sólo me interesa el último cierre, así que con 1 día vale
        hist = ticker.history(period='1d')

        # Hago que 'Date' sea una columna normal
        hist.reset_index(inplace=True)

        # El 'hist' en este caso son Pandas.series, entonces,
        # para obtener el valor que necesito, puedo usar acceso por 
        # el índice: iloc[0]
        datos.append({'Ticker_forex': info['symbol'].split('=')[0], 
                      'Date': datetime.date(hist['Date'].iloc[0]),
                      'Ultimo_cierre': hist['Close'].iloc[0],
                      })
        
    try:
        conn = sqlite3.connect('databases/db.sqlite3')
        cursor = conn.cursor()
        
        # Accedo directamente a la BD:
        for dato in datos:
            # No hace falta el 'id' porque es autoincremental
            query = """
                INSERT INTO Analysis_cambiomoneda (Ticker_forex, Date, Ultimo_cierre)
                VALUES (?, ?, ?)
            """
            cursor.execute(query, (dato['Ticker_forex'], dato['Date'], dato['Ultimo_cierre']))

            # Mostrar el nombre de la compañía agregada a la BD
            logger.info(" - [OK] %s", dato['Ticker_forex'])

        conn.commit()

        # Si todo ha ido bien:
        logger.info("")
        logger.info("[OK] Tabla creada con éxito.")

    except sqlite3.Error as ex1:
        logger.error("[NO OK] Error SQLite: %s", ex1)

    except Exception as ex2: 
        logger.error("[NO OK] Fallo al crear la tabla. Error: %s", ex2)

    finally:
        # Cerrar conexión a la BD
        conn.close()
        logger.info("Proceso finalizado.")

    return


#######################################################
if __name__ == "__main__":

    logger = crear_logger()

    # Para insertar paso lista de tickers sin adaptar para hacer
    # las llamadas adecuadas a la API de yfinance. Se adaptan en
    # en el código
    
    # Insertar datos en la BD del DJ30 
    dj30 = Tickers_BDs.tickers_dj30()
    bd = Tickers_BDs.ruta_bd_dj30()
    crear_bds(dj30, bd, logger)

    # Insertar datos en la BD del IBEX35
    ibex35 = Tickers_BDs.tickers_ibex35()
    bd = Tickers_BDs.ruta_bd_ibex35()
    crear_bds(ibex35, bd, logger)
    
    # Insertar datos en la BD del FTSE100
    ftse100 = Tickers_BDs.tickers_ftse100()
    bd = Tickers_BDs.ruta_bd_ftse100()
    crear_bds(ftse100, bd, logger)

    # Insertar datos en la BD del DAX40
    dax40 = Tickers_BDs.tickers_dax40()
    bd = Tickers_BDs.ruta_bd_dax40()
    crear_bds(dax40, bd, logger)

    # Insertar datos en la tabla de sectores
    índices = Tickers_BDs.tickers_dj30() + Tickers_BDs.tickers_ibex35() + Tickers_BDs.tickers_ftse100() + Tickers_BDs.tickers_dax40()
    crear_tabla_sectores(índices, logger)

    # Insertar datos en la tabla de cambio de monedas
    pares_monedas = ["EURUSD=X", "EURGBP=X"]
    crear_tabla_cambio_moneda(pares_monedas, logger)
    