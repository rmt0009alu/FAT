import yfinance as yf
import sqlite3
import logging

from logging.handlers import RotatingFileHandler


def crearLogger():
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



def crearBD(índice, bd, logger):

    logger.info("")
    logger.info("------------------------------------------")
    logger.info("Creando base de datos:")
    logger.info("------------------------------------------")

    # Conexión a la BD (si no existe, se crea)
    conn = sqlite3.connect(bd)

    try:
        # Uso una transacción para asegurar la atomicidad:
        with conn:
            for ticker in índice:

                stock = yf.Ticker(ticker)
                
                # Selecciono el máximo de datos posible de cada stock
                hist = stock.history(period="max", interval="1d")

                # Guardo un nombre de Ticker igual al nombre de la tabla
                # en la que se va a guardar. Los ticker que tienen sufijo
                # cambian el '.' por '_'. Los que no tienen sufijo, se 
                # mantienen igual
                ticker_cambiado = ticker.replace(".", "_")

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

                # Comprobar existencia de tabla
                if not conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ticker_cambiado}'").fetchone():
                    # Pasar del DataFrame a la BD. Si no existe
                    # la tabla, se crea
                    hist.to_sql(ticker_cambiado, conn, index=True, if_exists='replace')

                # Mostrar el nombre de la compañía agregada a la BD
                logger.info(" - [OK] %s", nombre)

        # Si todo ha ido bien:
        logger.info("")
        logger.info("[OK] Base de datos creada.")

    except sqlite3.Error as ex1:
        logger.error("[NO OK] Error SQLite: %s", ex1)

    except Exception as ex2: 
        logger.error("[NO OK] Fallo al crear base de datos. Error: %s", ex2)

    finally:
        # Cerrar conexión a la BD
        conn.close()
        logger.info("Proceso finalizado.")

    return
    

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
    crearBD(dj30, bd, logger)

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
    crearBD(ibex35, bd, logger)


