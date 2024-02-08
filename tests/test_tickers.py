from django.test import SimpleTestCase
from util.tickers.Tickers_BDs import tickersDJ30, tickersIBEX35, tickersIndices, tickersAdaptadosIBEX35, tickersAdaptadosDJ30, tickersAdaptadosIndices, ruta_bdDJ30, ruta_bdIBEX35, nombre_bdDJ30, nombre_bdIBEX35, obtenerNombreBD, tickersDisponibles, tickersAdaptadosDisponibles
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('Tickers')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS TICKERS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance


class TestTickers(SimpleTestCase):
    
    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('Tickers')

    def test_tickers_dj30(self):
        tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','^DJI']                           
        self.assertEquals(tickers, tickersDJ30(), " - [NO OK] Tickers dj30")
        self.log.info(" - [OK] Tickers dj30")
        

    def test_tickers_ibex35(self):
        tickers = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
            'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
            'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
            'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
            'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
            'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
            'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
            'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
            'SLR.MC', 'TEF.MC', 'UNI.MC', '^IBEX']                        
        self.assertEquals(tickers, tickersIBEX35(), " - [NO OK] Tickers ibex35")
        self.log.info(" - [OK] Tickers ibex35")


    def test_tickers_índices(self):
        índices = ['^DJI', '^IBEX']
        self.assertEquals(índices, tickersIndices(), " - [NO OK] Tickers índices")
        self.log.info(" - [OK] Tickers índices")

    
    def test_tickers_adaptados_dj30(self):
        tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','DJI']  
        self.assertEquals(tickers, tickersAdaptadosDJ30(), " - [NO OK] Tickers adaptados dj30")
        self.log.info(" - [OK] Tickers adaptados dj30")

    def test_tickers_adaptados_ibex35(self):
        tickers = ['ACS_MC', 'ACX_MC', 'AENA_MC', 'AMS_MC', 
            'ANA_MC', 'ANE_MC', 'BBVA_MC', 'BKT_MC', 
            'CABK_MC', 'CLNX_MC', 'COL_MC', 'ELE_MC', 
            'ENG_MC', 'FDR_MC', 'FER_MC', 'GRF_MC', 
            'IAG_MC', 'IBE_MC', 'IDR_MC', 'ITX_MC', 
            'LOG_MC', 'MAP_MC', 'MEL_MC', 'MRL_MC', 
            'MTS_MC', 'NTGY_MC', 'RED_MC', 'REP_MC', 
            'ROVI_MC', 'SAB_MC', 'SAN_MC', 'SCYR_MC', 
            'SLR_MC', 'TEF_MC', 'UNI_MC', 'IBEX']
        self.assertEquals(tickers, tickersAdaptadosIBEX35(), " - [NO OK] Tickers adaptados ibex35")
        self.log.info(" - [OK] Tickers adaptados ibex35")

    
    def test_tickers_adaptados_indices(self):
        índices = ['DJI', 'IBEX']
        self.assertEquals(índices, tickersAdaptadosIndices())
        self.log.info(" - [OK] Tickers adaptados índices")

    
    def test_ruta_bd_dj30(self):
        self.assertEquals('databases/dj30.sqlite3', ruta_bdDJ30(), " - [NO OK] Ruta bd dj30")
        self.log.info(" - [OK] Ruta bd dj30")
    
    def test_ruta_bd_ibex35(self):
        self.assertEquals('databases/ibex35.sqlite3', ruta_bdIBEX35(), " - [NO OK] Ruta bd ibex35")
        self.log.info(" - [OK] Ruta bd ibex35")

    def test_nombre_bd_dj30(self):
        self.assertEquals('dj30', nombre_bdDJ30(), " - [NO OK] Nombre bd dj30")
        self.log.info(" - [OK] Nombre bd dj30")

    
    def test_nombre_bd_ibex35(self):
        self.assertEquals('ibex35', nombre_bdIBEX35(), " - [NO OK] Nombre bd ibex35")
        self.log.info(" - [OK] Nombre bd ibex35")

    
    def test_obtener_nombre_bd_de_ticker(self):
        for _ in tickersDJ30():
            self.assertEquals(obtenerNombreBD(_), nombre_bdDJ30(), " - [NO OK] Obtener nombre de bd en dj30")
        for _ in tickersAdaptadosDJ30():
            self.assertEquals(obtenerNombreBD(_), nombre_bdDJ30(), " - [NO OK] Obtener nombre de bd en dj30")
        self.log.info(" - [OK] Obtener nombre de bd en dj30")

        for _ in tickersIBEX35():
            self.assertEquals(obtenerNombreBD(_), nombre_bdIBEX35(), " - [NO OK] Obtener nombre de bd en ibex35")
        for _ in tickersAdaptadosIBEX35():
            self.assertEquals(obtenerNombreBD(_), nombre_bdIBEX35(), " - [NO OK] Obtener nombre de bd en ibex35")
        self.log.info(" - [OK] Obtener nombre de bd en ibex35")

        self.assertEquals(obtenerNombreBD('testTicker'), None, " - [NO OK] Obtener None con nombre falso")
        self.log.info(" - [OK] Obtener None con nombre falso")


    def test_tickers_disponibles(self):
        tickers_1 = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','^DJI']  
        tickers_2 = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
            'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
            'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
            'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
            'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
            'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
            'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
            'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
            'SLR.MC', 'TEF.MC', 'UNI.MC', '^IBEX']     
        self.assertEquals(tickers_1 + tickers_2, tickersDisponibles(), " - [NO OK] Obtener tickers disponibles")
        self.log.info(" - [OK] Obtener tickers disponibles")

    
    def test_tickers_adaptados_disponibles(self):
        tickers_1 = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','DJI']  
        tickers_2 = ['ACS_MC', 'ACX_MC', 'AENA_MC', 'AMS_MC', 
            'ANA_MC', 'ANE_MC', 'BBVA_MC', 'BKT_MC', 
            'CABK_MC', 'CLNX_MC', 'COL_MC', 'ELE_MC', 
            'ENG_MC', 'FDR_MC', 'FER_MC', 'GRF_MC', 
            'IAG_MC', 'IBE_MC', 'IDR_MC', 'ITX_MC', 
            'LOG_MC', 'MAP_MC', 'MEL_MC', 'MRL_MC', 
            'MTS_MC', 'NTGY_MC', 'RED_MC', 'REP_MC', 
            'ROVI_MC', 'SAB_MC', 'SAN_MC', 'SCYR_MC', 
            'SLR_MC', 'TEF_MC', 'UNI_MC', 'IBEX']     
        self.assertEquals(tickers_1 + tickers_2, tickersAdaptadosDisponibles(), " - [NO OK] Obtener tickers disponibles")
        self.log.info(" - [OK] Obtener tickers disponibles")
