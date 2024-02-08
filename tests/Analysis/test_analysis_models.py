from django.test import TestCase
from Analysis.models import StockBase, Sectores, modelos_de_stocks
from util.tickers.Tickers_BDs import tickersIBEX35, tickersDJ30, tickersAdaptadosDJ30, tickersAdaptadosIBEX35, tickersAdaptadosDisponibles, tickersAdaptadosIndices, obtenerNombreBD
from log.logger.logger import get_logger_configurado
from datetime import datetime, timezone
# from django.utils import timezone
# Para usar los modelos creados de forma dinámica
from django.apps import apps


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('AnalysisModels')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS ANALYSIS MODELS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance


# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestAnalysisModels(TestCase):
    
    databases = '__all__'

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('AnalysisModels')

        self.listaStocks = []
        for ticker in tickersAdaptadosDisponibles():
            if ticker not in tickersAdaptadosIndices():
                model = apps.get_model('Analysis', ticker)
                bd = obtenerNombreBD(ticker)
                stock = model.objects.using(bd).create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                    open=100.0,
                    high=110.0,
                    low=90.0,
                    close=105.0,
                    volume=10000,
                    dividends=1.0,
                    stock_splits=2.0,
                    ticker=ticker,
                    previous_close=100.0,
                    percent_variance=5.0,
                    mm20=102.0,
                    mm50=104.0,
                    mm200=98.0,
                    name='Nombre ficticio',
                    currency = 'EUR',
                    sector = 'Pruebas')
                self.listaStocks.append(stock)

        self.sector = Sectores.objects.create(ticker_bd='RED_MC', bd='ibex35', ticker='RED.MC', 
                                         nombre='Redeia Corporación, S.A.', sector='Utilities')


    def test_models_StockBase_instance(self):
        stock = self.listaStocks[0]
        self.assertTrue(isinstance(stock, StockBase), " - [NO OK] Crear instancia de StockBase")
        self.log.info(" - [OK] Crear instancia de StockBase")
    

    def test_models_StockBase_str(self):
        # self.assertEquals(str(self.stock), 'AAPL - Apple Inc. . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 105.0', " - [NO OK] StockBase str")
        # self.log.info(" - [OK] StockBase str")
        for stock in self.listaStocks:
            self.assertEquals(str(stock), f'{stock.ticker} - Nombre ficticio . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 105.0', " - [NO OK] StockBase str")
        self.log.info(" - [OK] StockBase str")


    def test_models_StockBase_diccionario(self):
        self.assertEquals(len(modelos_de_stocks), len(tickersDJ30() + tickersIBEX35()), " - [NO OK] StockBase diccionario de 'modelos_de_stocks'")

        for _ in modelos_de_stocks:
            self.assertTrue(_ in (tickersAdaptadosDJ30() + tickersAdaptadosIBEX35()))
        self.log.info(" - [OK] StockBase diccionario de 'modelos_de_stocks'")


    def test_models_Sectores_instance(self):
        self.assertTrue(isinstance(self.sector, Sectores), " - [NO OK] Objeto 'sector' instancia de Sectores")
        self.log.info(" - [OK] Objeto 'sector' instancia de Sectores")


    def test_models_Sectores_str(self):
        self.assertEquals(str(self.sector), '1 - Redeia Corporación, S.A. - Utilities', " - [NO OK] Sectores str")
        self.log.info(" - [OK] Sectores str")
    

    def test_models_Sectores_autoincremental(self):
        self.sector2 = Sectores.objects.create(ticker_bd='AAPL', bd='dj30', ticker='AAPL', 
                                         nombre='Apple Inc.', sector='Technology')
        # Tiene que ser 2 porque creo otro en el setUp()
        self.assertEquals(self.sector2.id, 2, " - [NO OK] Registro con 'id' autoincremental de Sectores")
        self.log.info(" - [OK] Registro con 'id' autoincremental de Sectores")


    def test_models_Sectores_filtrado(self):
        self.sector3 = Sectores.objects.create(ticker_bd='ACS_MC', bd='ibex35', ticker='ACS.MC', 
                                         nombre='ACS, Actividades de Construcción y Servicios, S.A.', 
                                         sector='Industrials')
        self.sector4 = Sectores.objects.create(ticker_bd='AENA_MC', bd='ibex35', ticker='AENA.MC', 
                                         nombre='Aena S.M.E., S.A.', 
                                         sector='Industrials')
        valoresIndustriales = Sectores.objects.filter(sector='Industrials')
        self.assertEqual(valoresIndustriales.count(), 2, " - [NO OK] Filtrado por Sectores")

        # Elimino uno para ver que de nuevo se filtra bien
        self.sector3.delete()
        self.assertEqual(Sectores.objects.filter(sector='Industrials').count(), 1, " - [NO OK] Filtrado por Sectores")
        self.log.info(" - [OK] Filtrado por Sectores")
