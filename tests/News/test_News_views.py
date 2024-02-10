from django.test import TestCase
from News.views import _mejores_peores
from log.logger.logger import get_logger_configurado
import pandas as pd
from datetime import datetime, timezone
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
            
            log = get_logger_configurado('NewsViews')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS NEWS VIEWS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestNewsViews(TestCase):

    databases = '__all__'

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('NewsViews')

        # Creo unos registros de stocks para que al consultar los datos
        # en stock seguimiento/comprado haya info. de los mismos:
        model = apps.get_model('Analysis', 'AAPL')
        self.stock_1 = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
            currency = 'USD', sector = 'Technology'
        )

        model = apps.get_model('Analysis', 'IBM')
        self.stock_3 = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
            currency = 'USD', sector = 'Technology'
        )


    def test_views_home_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, " - [NO OK] No necesario login para acceder a home")
        self.log.info(" - [OK] No necesario login para acceder a home")
        
    
    def test_views_mejores_peores_sin_tickers(self):
        tickers = []
        result = _mejores_peores(tickers)
        self.assertIsInstance(result, pd.DataFrame, " - [NO OK] No obtener datos de _mejores_peores si no hay tickers")
        self.assertTrue(result.empty, " - [NO OK] No obtener datos de _mejores_peores si no hay tickers")
        self.log.info(" - [OK] No obtener datos de _mejores_peores si no hay tickers")


    def test_views_mejores_peores_con_tickers_validos(self):
        tickers = ['AAPL', 'IBM']
        result = _mejores_peores(tickers)
        self.assertIsInstance(result, pd.DataFrame, " - [NO OK] Obtener datos de _mejores_peores si hay tickers válidos")
        self.assertFalse(result.empty, " - [NO OK] Obtener datos de _mejores_peores si hay tickers válidos")
        self.log.info(" - [OK] Obtener datos de _mejores_peores si hay tickers válidos")

    