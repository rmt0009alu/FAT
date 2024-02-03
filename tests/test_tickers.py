from django.test import SimpleTestCase
from util.tickers.Tickers_BDs import tickersDJ30, tickersIBEX35, tickersIndices, tickersAdaptadosIBEX35, tickersAdaptadosDJ30, tickersAdaptadosIndices, ruta_bdDJ30, ruta_bdIBEX35, nombre_bdDJ30, nombre_bdIBEX35, obtenerNombreBD, tickersDisponibles


class TestRSS(SimpleTestCase):
    
    def test_tickers_dj30(self):
        tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','^DJI']                           
        self.assertEquals(tickers, tickersDJ30())
        

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
        self.assertEquals(tickers, tickersIBEX35())


    def test_tickers_índices(self):
        índices = ['^DJI', '^IBEX']
        self.assertEquals(índices, tickersIndices())

    
    def test_tickers_adaptados_dj30(self):
        tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','DJI']  
        self.assertEquals(tickers, tickersAdaptadosDJ30())


    def test_tickers_adaptados_inex35(self):
        tickers = ['ACS_MC', 'ACX_MC', 'AENA_MC', 'AMS_MC', 
            'ANA_MC', 'ANE_MC', 'BBVA_MC', 'BKT_MC', 
            'CABK_MC', 'CLNX_MC', 'COL_MC', 'ELE_MC', 
            'ENG_MC', 'FDR_MC', 'FER_MC', 'GRF_MC', 
            'IAG_MC', 'IBE_MC', 'IDR_MC', 'ITX_MC', 
            'LOG_MC', 'MAP_MC', 'MEL_MC', 'MRL_MC', 
            'MTS_MC', 'NTGY_MC', 'RED_MC', 'REP_MC', 
            'ROVI_MC', 'SAB_MC', 'SAN_MC', 'SCYR_MC', 
            'SLR_MC', 'TEF_MC', 'UNI_MC', 'IBEX']
        self.assertEquals(tickers, tickersAdaptadosIBEX35())

    
    def test_tickers_adaptados_índices(self):
        índices = ['DJI', 'IBEX']
        self.assertEquals(índices, tickersAdaptadosIndices())

    
    def test_ruta_bd_dj30(self):
        self.assertEquals('databases/dj30.sqlite3', ruta_bdDJ30())

    
    def test_ruta_bd_ibex35(self):
        self.assertEquals('databases/ibex35.sqlite3', ruta_bdIBEX35())

    
    def test_nombre_bd_dj30(self):
        self.assertEquals('dj30', nombre_bdDJ30())

    
    def test_nombre_bd_ibex35(self):
        self.assertEquals('ibex35', nombre_bdIBEX35())

    
    def test_obtener_nombre_bd_de_ticker(self):
        for _ in tickersDJ30():
            self.assertEquals(obtenerNombreBD(_), nombre_bdDJ30())
        for _ in tickersAdaptadosDJ30():
            self.assertEquals(obtenerNombreBD(_), nombre_bdDJ30())
        for _ in tickersIBEX35():
            self.assertEquals(obtenerNombreBD(_), nombre_bdIBEX35())
        for _ in tickersAdaptadosIBEX35():
            self.assertEquals(obtenerNombreBD(_), nombre_bdIBEX35())

        self.assertEquals(obtenerNombreBD('testTicker'), None)


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
        self.assertEquals(tickers_1 + tickers_2, tickersDisponibles())