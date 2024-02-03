
def tickersDJ30():
    """Para obtener los tickers del DJ30.

    Returns:
        (list): lista con los tickers del DJ30.
    """
    # Tickers del DJ30
    dj30 = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','^DJI']

    return dj30



def tickersIBEX35():
    """Para obtener los tickers del IBEX35.

    Returns:
        (list): lista con los tickers del IBEX35.
    """
    # Tickers del IBEX35
    ibex35 = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
            'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
            'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
            'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
            'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
            'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
            'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
            'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
            'SLR.MC', 'TEF.MC', 'UNI.MC', '^IBEX']
    
    return ibex35



def tickersIndices():
    """Para obtener los tickers de los índices separados
    del resto de tickers.

    Returns:
        (list): lista con los tickers de los índices
    """
    indices = ['^DJI', '^IBEX']

    return indices



def tickersAdaptadosIBEX35():
    """Para obtener los tickers del IBEX35 con
    formato adaptado y evitar la notación de punto,
    así como la de '^' del índice, porque puede dar 
    problemas al acceder a las tablas de la BD.

    Returns:
        (list): lista con los tickers del IBEX35 adaptados.
    """
    ibex35 = tickersIBEX35()

    ibex35adaptado = []
    # Para evitar conflictos en BDs con la notación 
    # de '.' y con el '^' del índice
    for ticker in ibex35:
        ticker = ticker.replace("^","")
        ibex35adaptado.append(ticker.replace(".", "_"))

    return ibex35adaptado



def tickersAdaptadosDJ30():
    """Para obtener los tickers del DJ30 con
    formato adaptado y evitar la notación de '^' del 
    ínidice porque puede dar problemas al acceder a 
    las tablas de la BD.

    Returns:
        (list): lista con los tickers del DJ30 adaptados.
    """
    dj30 = tickersDJ30()

    dj30adaptado = []
    # Para evitar conflictos en BDs con la notación 
    # de '^' del índice
    for ticker in dj30:
        dj30adaptado.append(ticker.replace("^", ""))

    return dj30adaptado



def tickersAdaptadosIndices():
    """Para obtener los tickers de los índices con
    formato adaptado y evitar la notación de '^'.

    Returns:
        (list): lista con los tickers de los índices adaptados.
    """
    indices = tickersIndices()

    indicesAdaptado = []

    for ticker in indices:
        indicesAdaptado.append(ticker.replace("^", ""))

    return indicesAdaptado 



def ruta_bdDJ30():
    """Para obtener el path y nombre de la BD
    del DJ30.

    Returns:
        (str): path y nombre de la BD del DJ30.
    """
    # BD del DJ30
    bd = 'databases/dj30.sqlite3'

    return bd



def ruta_bdIBEX35():
    """Para obtener el path y nombre de la BD
    del IBEX35.

    Returns:
        (str): path y nombre de la BD del IBEX35.
    """
    # BD del IBEX35
    bd = 'databases/ibex35.sqlite3'

    return bd



def nombre_bdDJ30():
    """Para obtener sólo el nombre registrado 
    en el settings como base de datos

    Returns:
        (str): nombre de la BD en settings
    """
    nombre = 'dj30'
    return nombre



def nombre_bdIBEX35():
    """Para obtener sólo el nombre registrado 
    en el settings como base de datos

    Returns:
        (str): nombre de la BD en settings
    """
    nombre = 'ibex35'
    return nombre



def obtenerNombreBD(stock):
    """Para obtener el nombre de la BD a la que pertenece un 
    stock. No hay problema de identificación porque todos los 
    stocks tienen un sufijo (excepto los del DJ30).

    Args:
        stock (str): string con el nombre del stock.

    Returns:
        (str): nombre de la BD a la que pertenece el stock.
    """
    if stock in (tickersIBEX35() + tickersAdaptadosIBEX35()):
        return nombre_bdIBEX35()
    elif stock in (tickersDJ30() + tickersAdaptadosDJ30()):
        return nombre_bdDJ30()
    else:
        return None
    


def tickersDisponibles():
    """Para obtener todos los tickers disponibles, con
    índices y sin adaptar. 

    Returns:
        (list): lista con todos los tickers disponibles.
    """
    return tickersDJ30() + tickersIBEX35()