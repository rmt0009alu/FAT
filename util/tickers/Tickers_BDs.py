
def tickers_dj30():
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


def tickers_ibex35():
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


def tickers_ftse100():
    """Para obtener los tickers del FTSE100.

    Returns:
        (list): lista con los tickers del FTSE100.
    """
    # Tickers del FTSE100
    ftse100 = ['III.L', 'ADM.L', 'AAF.L', 'AAL.L', 'ANTO.L', 
               'AHT.L', 'ABF.L', 'AZN.L', 'AUTO.L', 'AV.L', 
               'BME.L', 'BA.L', 'BARC.L', 'BDEV.L', 'BEZ.L', 
               'BKG.L', 'BP.L', 'BATS.L', 'BT-A.L', 'BNZL.L', 
               'BRBY.L', 'CNA.L', 'CCH.L', 'CPG.L', 'CTEC.L', 
               'CRDA.L', 'DCC.L', 'DGE.L', 'DPLM.L', 'EDV.L', 
               'ENT.L', 'EXPN.L', 'FCIT.L', 'FLTR.L', 'FRAS.L', 
               'FRES.L', 'GLEN.L', 'GSK.L', 'HLN.L', 'HLMA.L', 
               'HIK.L', 'HWDN.L', 'HSBA.L', 'IMI.L', 'IMB.L', 
               'INF.L', 'IHG.L', 'ICP.L', 'ITRK.L', 'IAG.L', 
               'JD.L', 'KGF.L', 'LAND.L', 'LGEN.L', 'LLOY.L', 
               'LSEG.L', 'MNG.L', 'MKS.L', 'MRO.L', 'MNDI.L', 
               'NG.L', 'NWG.L', 'NXT.L', 'OCDO.L', 'PSON.L', 
               'PSH.L', 'PSN.L', 'PHNX.L', 'PRU.L', 'RKT.L', 
               'REL.L', 'RTO.L', 'RMV.L', 'RIO.L', 'RR.L', 
               'RS1.L', 'SGE.L', 'SBRY.L', 'SDR.L', 'SMT.L', 
               'SGRO.L', 'SVT.L', 'SHEL.L', 'SN.L', 'SMDS.L', 
               'SMIN.L', 'SKG.L', 'SPX.L', 'SSE.L', 'STJ.L', 
               'STAN.L', 'TW.L', 'TSCO.L', 'ULVR.L', 'UTG.L', 
               'UU.L', 'VOD.L', 'WEIR.L', 'WTB.L', 'WPP.L', '^FTSE']

    return ftse100


def tickers_indices():
    """Para obtener los tickers de los índices separados
    del resto de tickers.

    Returns:
        (list): lista con los tickers de los índices
    """
    indices = ['^DJI', '^IBEX', '^FTSE']

    return indices


def tickers_adaptados_dj30():
    """Para obtener los tickers del DJ30 con
    formato adaptado y evitar la notación de '^' del 
    ínidice porque puede dar problemas al acceder a 
    las tablas de la BD.

    Returns:
        (list): lista con los tickers del DJ30 adaptados.
    """
    dj30 = tickers_dj30()

    dj30adaptado = []
    # Para evitar conflictos en BDs con la notación 
    # de '^' del índice
    for ticker in dj30:
        dj30adaptado.append(ticker.replace("^", ""))

    return dj30adaptado


def tickers_adaptados_ibex35():
    """Para obtener los tickers del IBEX35 con
    formato adaptado y evitar la notación de punto,
    así como la de '^' del índice, porque puede dar 
    problemas al acceder a las tablas de la BD.

    Returns:
        (list): lista con los tickers del IBEX35 adaptados.
    """
    ibex35 = tickers_ibex35()

    ibex35_adaptado = []
    # Para evitar conflictos en BDs con la notación 
    # de '.' y con el '^' del índice
    for ticker in ibex35:
        ticker = ticker.replace("^","")
        ibex35_adaptado.append(ticker.replace(".", "_"))

    return ibex35_adaptado


def tickers_adaptados_ftse100():
    """Para obtener los tickers del FTSE100 con
    formato adaptado y evitar la notación de punto,
    así como la de '^' del índice, porque puede dar 
    problemas al acceder a las tablas de la BD.

    Returns:
        (list): lista con los tickers del FTSE100 adaptados.
    """
    ftse100 = tickers_ftse100()

    fte100_adaptado = []
    # Para evitar conflictos en BDs con la notación 
    # de '.' y con el '^' del índice
    for ticker in ftse100:
        ticker = ticker.replace("^","")
        fte100_adaptado.append(ticker.replace(".", "_"))

    return fte100_adaptado


def tickers_adaptados_indices():
    """Para obtener los tickers de los índices con
    formato adaptado y evitar la notación de '^'.

    Returns:
        (list): lista con los tickers de los índices adaptados.
    """
    indices = tickers_indices()

    indicesAdaptado = []

    for ticker in indices:
        indicesAdaptado.append(ticker.replace("^", ""))

    return indicesAdaptado 


def ruta_bd_dj30():
    """Para obtener el path y nombre de la BD
    del DJ30.

    Returns:
        (str): path y nombre de la BD del DJ30.
    """
    # BD del DJ30
    return 'databases/dj30.sqlite3'


def ruta_bd_ibex35():
    """Para obtener el path y nombre de la BD
    del IBEX35.

    Returns:
        (str): path y nombre de la BD del IBEX35.
    """
    # BD del IBEX35
    return 'databases/ibex35.sqlite3'


def ruta_bd_ftse100():
    """Para obtener el path y nombre de la BD
    del FTSE100.

    Returns:
        (str): path y nombre de la BD del FTSE100.
    """
    # BD del FTSE100
    return 'databases/ftse100.sqlite3'


def nombre_bd_dj30():
    """Para obtener sólo el nombre registrado 
    en el settings como base de datos.

    Returns:
        (str): nombre de la BD en settings
    """
    return 'dj30'



def nombre_bd_ibex35():
    """Para obtener sólo el nombre registrado 
    en el settings como base de datos.

    Returns:
        (str): nombre de la BD en settings
    """
    return 'ibex35'


def nombre_bd_ftse100():
    """Para obtener sólo el nombre registrado 
    en el settings como base de datos.

    Returns:
        (str): nombre de la BD en settings
    """
    return 'ftse100'


def obtener_nombre_bd(stock):
    """Para obtener el nombre de la BD a la que pertenece un 
    stock. No hay problema de identificación porque todos los 
    stocks tienen un sufijo (excepto los del DJ30).

    Args:
        stock (str): string con el nombre del stock.

    Returns:
        (str): nombre de la BD a la que pertenece el stock.
    """
    if stock in (tickers_ibex35() + tickers_adaptados_ibex35()):
        return nombre_bd_ibex35()
    elif stock in (tickers_dj30() + tickers_adaptados_dj30()):
        return nombre_bd_dj30()
    elif stock in (tickers_ftse100() + tickers_adaptados_ftse100()):
        return nombre_bd_ftse100()
    else:
        return None
    

def tickers_disponibles():
    """Para obtener todos los tickers disponibles, con
    índices y sin adaptar. 

    Returns:
        (list): lista con todos los tickers disponibles.
    """
    return tickers_dj30() + tickers_ibex35() + tickers_ftse100()


def tickers_adaptados_disponibles():
    """Para obtener todos los tickers adaptados disponibles, con
    índices y sin adaptar. 

    Returns:
        (list): lista con todos los tickers adaptados disponibles.
    """
    return tickers_adaptados_dj30() + tickers_adaptados_ibex35() + tickers_adaptados_ftse100()


def bases_datos_disponibles():
    """Para obtener las bases de datos disponibles en la aplicación.

    Returns:
        (set): conjunto con las bases de datos disponibles.
    """
    return {nombre_bd_dj30(), nombre_bd_ibex35(), nombre_bd_ftse100()}
