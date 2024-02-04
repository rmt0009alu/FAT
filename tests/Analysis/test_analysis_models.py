from django.test import TestCase
from Analysis.models import StockBase, Sectores, modelos_de_stocks
from util.tickers.Tickers_BDs import tickersIBEX35, tickersDJ30, tickersAdaptadosDJ30, tickersAdaptadosIBEX35
from datetime import datetime, timezone
# from django.utils import timezone
# Para usar los modelos creados de forma dinámica
from django.apps import apps

class TestAnalysisModels(TestCase):
    
    databases = '__all__'

    def setUp(self):
        model = apps.get_model('Analysis', 'AAPL')
        self.stock = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=10000,
            dividends=1.0,
            stock_splits=2.0,
            ticker='AAPL',
            previous_close=100.0,
            percent_variance=5.0,
            mm20=102.0,
            mm50=104.0,
            mm200=98.0,
            name='Apple Inc.',
            currency = 'USD',
            sector = 'Technology')
        
        self.sector = Sectores.objects.create(ticker_bd='RED_MC', bd='ibex35', ticker='RED.MC', 
                                         nombre='Redeia Corporación, S.A.', sector='Utilities')


    def test_models_StockBase_instance(self):
        self.assertTrue(isinstance(self.stock, StockBase))
    

    def test_models_StockBase_str(self):
        self.assertEquals(str(self.stock), 'AAPL - Apple Inc. . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 105.0')


    def test_models_StockBase_diccionario(self):
        self.assertEquals(len(modelos_de_stocks), len(tickersDJ30() + tickersIBEX35()))

        for _ in modelos_de_stocks:
            self.assertTrue(_ in (tickersAdaptadosDJ30() + tickersAdaptadosIBEX35()))


    def test_models_Sectores_instance(self):
        self.assertTrue(isinstance(self.sector, Sectores))


    def test_models_Sectores_str(self):
        self.assertEquals(str(self.sector), '1 - Redeia Corporación, S.A. - Utilities')
    

    def test_models_Sectores_autoincremental(self):
        self.sector2 = Sectores.objects.create(ticker_bd='AAPL', bd='dj30', ticker='AAPL', 
                                         nombre='Apple Inc.', sector='Technology')
        # Tiene que ser 2 porque creo otro en el setUp()
        self.assertEquals(self.sector2.id, 2)


    def test_models_Sectores_filtrado(self):
        self.sector3 = Sectores.objects.create(ticker_bd='ACS_MC', bd='ibex35', ticker='ACS.MC', 
                                         nombre='ACS, Actividades de Construcción y Servicios, S.A.', 
                                         sector='Industrials')
        self.sector4 = Sectores.objects.create(ticker_bd='AENA_MC', bd='ibex35', ticker='AENA.MC', 
                                         nombre='Aena S.M.E., S.A.', 
                                         sector='Industrials')
        valoresIndustriales = Sectores.objects.filter(sector='Industrials')
        self.assertEqual(valoresIndustriales.count(), 2)

        # Elimino uno para ver que de nuevo se filtra bien
        self.sector3.delete()
        self.assertEqual(Sectores.objects.filter(sector='Industrials').count(), 1)

