from django.test import TestCase
import os
import sys
import logging
from django.db import connections
from util.tickers.Tickers_BDs import tickers_adaptados_dj30, tickers_adaptados_ibex35
from datetime import datetime, timezone
# Para usar los modelos creados de forma dinámica
from django.apps import apps

# # Para que se detecten bien los paths desde los tests
# # https://stackoverflow.com/questions/35636736/python-importing-modules-for-testing
# PROJECT_PATH = os.getcwd()
# sys.path.append(PROJECT_PATH)
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('databases')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS BASES DE DATOS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

class TestDataBases(TestCase):

    # Como quiero probar diferentes bases de datos es necesario
    # especificar que quiero que se creen BDs de test para todos
    # los casos: https://stackoverflow.com/questions/38307523/test-isolation-broken-with-multiple-databases-in-django-how-to-fix-it
    databases = '__all__'

    def setUp(self): 
        Singleton()
        self.log = get_logger_configurado('databases')

        self.tickers_dj30 = tickers_adaptados_dj30()
        self.tickers_ibex35 = tickers_adaptados_ibex35()
        
        # Para obtener el nombre de todas las tablas en la BD (usando
        # SQLite3)
        with connections['dj30'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.nombresStocks_dj30 = cursor.fetchall()
            cursor.close()

        with connections['ibex35'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.nombresStocks_ibex35 = cursor.fetchall()
            cursor.close()

        self.columnas = ['id', 'Date', 'Open', 'High', 'Low', 'Close', 
                         'Volume', 'Dividends', 'Stock Splits', 'Ticker', 
                         'Previous_Close', 'Percent_Variance', 'MM20', 
                         'MM50', 'MM200', 'Name', 'Sector', 'Currency']



    def test_databases_tickers_en_listas(self):
        self.assertIsInstance(self.tickers_dj30, list, " - [NO OK] Los tickers del DJ30 están en una lista")
        self.log.info(" - [OK] Los tickers del DJ30 están en una lista")
        self.assertIsInstance(self.tickers_ibex35, list, " - [NO OK] Los tickers del IBEX35 están en una lista")
        self.log.info(" - [OK] Los tickers del IBEX35 están en una lista")
    

    def test_databases_listas_tickers_no_vacías(self):
        self.assertIsNotNone(self.tickers_dj30, " - [NO OK] Listas de tickers no vacías")
        self.assertIsNotNone(self.tickers_ibex35, " - [NO OK] Listas de tickers no vacías")
        self.log.info(" - [OK] Listas de tickers no vacías")
    

    def test_databases_tickers_son_string(self):
        for ticker in self.tickers_dj30:
            self.assertIsInstance(ticker, str, " - [NO OK] Todos los tickers deben de ser strings")
        for ticker in self.tickers_ibex35:
            self.assertIsInstance(ticker, str, " - [NO OK] Todos los tickers deben de ser strings")
        self.log.info(" - [OK] Todos los tickers deben de ser strings")


    def test_databases_longitud_lista(self):
        self.assertEqual(len(self.tickers_dj30), 30 + 1, " - [NO OK] Tener 30 tickers (+ índice) en la lista del DJ30")
        self.log.info(" - [OK] Tener 30 tickers (+ índice) en la lista del DJ30")
        self.assertEqual(len(self.tickers_ibex35), 35 + 1, " - [NO OK] Tener 35 tickers (+ índice) en la lista del IBEX35")
        self.log.info(" - [OK] Tener 35 tickers (+ índice) en la lista del IBEX35")


    def test_databases_cantidad_tablas_dj30(self):
        # En stock[0] tengo el nombre de la tabla
        tablas = [stock[0] for stock in self.nombresStocks_dj30 if stock[0] not in ['django_migrations', 'sqlite_sequence']]
        self.assertEqual(len(tablas), 30 + 1, " - [NO OK] Tener 31 tablas (tickers + índidce) en DJ30")
        self.log.info(" - [OK] Tener 31 (tickers + índidce) tablas en DJ30")


    def test_databases_tabla_en_bd_dj30(self):
        # En stock[0] tengo el nombre de la tabla
        tablas = [stock[0] for stock in self.nombresStocks_dj30 if stock[0] not in ['django_migrations', 'sqlite_sequence']]
        # Comprobar que todos los tickers tienen su 
        # correspondiente tabla en la BD
        for ticker in self.tickers_dj30:
            self.assertIn(ticker, tablas, f" - [NO OK] Todas las tablas en BD de dj30: {ticker}")
        self.log.info(" - [OK] Todas las tablas en BD de dj30")


    def test_databases_columnas_en_tablas_dj30(self):
            # Aprovecho para comprobar que las columnas también 
            # se crean de manera adecuada
        for ticker in self.tickers_dj30:
            with connections['dj30'].cursor() as cursor:
                # Obtener info. de columnas de una tabla (ticker)
                cursor.execute(f"PRAGMA table_info({ticker});")
                columnas = [_[1] for _ in cursor.fetchall()]
                cursor.close()
                self.assertEqual(self.columnas, columnas, f" - [NO OK] Todos los tickers con columnas adecuadas en su tabla {ticker}")
        self.log.info(" - [OK] Todos los tickers de dj30 con columnas adecuadas en su tabla")
    

    def test_databases_crear_objetos_en_dj30(self):
        model = apps.get_model('Analysis', 'AAPL')
        model.objects.using('dj30').create(
            date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
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
            name='Apple Inc.'
        )
        stock = model.objects.using('dj30').get(ticker='AAPL')
        # Aprovecho el magic __str__ creado en los modelos
        self.assertEqual(str(stock),
                         'AAPL - Apple Inc. . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 105.0', 
                         f" - [NO OK] Crear datos con el formato esperado")
        self.log.info(f" - [OK] Crear datos con el formato esperado en dj30")
        self.assertEqual(stock.id, 1, f" - [NO OK] Guardar 'id' autoincremental")
        self.log.info(f" - [OK] Guardar 'id' autoincremental en dj30")


    def test_databases_cantidad_tablas_ibex35(self):       
        # En stock[0] tengo el nombre de la tabla
        tablas = [stock[0] for stock in self.nombresStocks_ibex35 if stock[0] not in ['django_migrations', 'sqlite_sequence']]
        self.assertEqual(len(tablas), 35 + 1, " - [NO OK] Tener 36 tablas (tickers + índidce) en IBEX35")
        self.log.info(" - [OK] Tener 36 tablas (tickers + índidce) en IBEX35")
    

    def test_databases_tabla_en_bd_ibex35(self):
        # En stock[0] tengo el nombre de la tabla
        tablas = [stock[0] for stock in self.nombresStocks_ibex35 if stock[0] not in ['django_migrations', 'sqlite_sequence']]
        # Comprobar que todos los tickers tienen su 
        # correspondiente tabla en la BD
        for ticker in self.tickers_ibex35:
            self.assertIn(ticker, tablas, f" - [NO OK] Todas las tablas en BD de ibex35: {ticker}")
        self.log.info(" - [OK] Todas las tablas en BD de ibex35")


    def test_databases_columnas_en_tablas_ibex35(self):
        for ticker in self.tickers_ibex35:
            with connections['ibex35'].cursor() as cursor:
                # Obtener info. de columnas de una tabla (ticker)
                cursor.execute(f"PRAGMA table_info({ticker});")
                columnas = [_[1] for _ in cursor.fetchall()]
                cursor.close()
                self.assertEqual(self.columnas, 
                                 columnas, 
                                 f" - [NO OK] Todos los tickers de ibex35 con columnas adecuadas en su tabla: {ticker}")
        self.log.info(" - [OK] Todos los tickers de ibex35 con columnas adecuadas en su tabla")


    def test_databases_crear_objetos_en_ibex35(self):
        model = apps.get_model('Analysis', 'ITX_MC')
        model.objects.using('ibex35').create(
            date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=30.0,
            high=31.0,
            low=29.0,
            close=29.795,
            volume=10000,
            dividends=1.0,
            stock_splits=2.0,
            ticker='ITX_MC',
            previous_close=29.5,
            percent_variance=1.0,
            mm20=29.3,
            mm50=30,
            mm200=29.0,
            name='Industria de Diseño Textil, S.A.'
        )
        stock = model.objects.using('ibex35').get(ticker='ITX_MC')
        # Aprovecho el magic __str__ creado en los modelos
        self.assertEqual(str(stock),
                         'ITX_MC - Industria de Diseño Textil, S.A. . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 29.795',
                         f" - [NO OK] Crear datos con el formato esperado en ibex35")
        self.log.info(f" - [OK] Crear datos con el formato esperado en ibex35")
        self.assertEqual(stock.id, 1, f" - [NO OK] Hacer 'id' autoincremental en ibex35")
        self.log.info(f" - [OK] Hacer 'id' autoincremental en ibex35")