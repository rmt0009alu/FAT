from django.test import TestCase

import os
import sys
import logging
from django.db import connections
from util.tickers.Tickers_BDs import tickersDJ30, tickersAdaptadosIBEX35
from datetime import datetime, timezone

# Para usar los modelos creados de forma dinámica
from django.apps import apps

# Para que se detecten bien los paths desde los tests
# https://stackoverflow.com/questions/35636736/python-importing-modules-for-testing
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)


class TestsUnitarios_BDs(TestCase):

    # Como quiero probar diferentes bases de datos es necesario
    # especificar que quiero que se creen BDs de test para todos
    # los casos: https://stackoverflow.com/questions/38307523/test-isolation-broken-with-multiple-databases-in-django-how-to-fix-it
    databases = '__all__'

    def setUp(self): 
        self.tickers_dj30 = tickersDJ30()
        self.tickers_ibex35 = tickersAdaptadosIBEX35()
        self.columnas = ['id', 'Date', 'Open', 'High', 'Low', 'Close', 
                         'Volume', 'Dividends', 'Stock Splits', 'Ticker', 
                         'Previous_Close', 'Percent_Variance', 'MM20', 
                         'MM50', 'MM200', 'Name']
        
        archivoLog = 'log/Tests_unitarios_BDs.log'
        # Logger con un nombre específico
        self.logger_BDs = logging.getLogger("BDs")
        # Filemode=w para que se sobreescriba siempre
        logging.basicConfig(filename=archivoLog, level=logging.DEBUG, encoding='utf-8', filemode='w', format='%(levelname)s:%(name)s:%(message)s')


    def test_01_basico(self):
        self.logger_BDs.info("")
        self.logger_BDs.info("----------------------------------")
        self.logger_BDs.info("TEST BÁSICO")
        self.logger_BDs.info("----------------------------------")

        self.assertIsInstance(self.tickers_dj30, list, " - [NO OK] Los tickers del DJ30 están en una lista")
        self.logger_BDs.info(" - [OK] Los tickers del DJ30 están en una lista")
        self.assertIsInstance(self.tickers_ibex35, list, " - [NO OK] Los tickers del IBEX35 están en una lista")
        self.logger_BDs.info(" - [OK] Los tickers del IBEX35 están en una lista")
        self.assertIsNotNone(self.tickers_dj30, " - [NO OK] Listas de tickers no vacías")
        self.assertIsNotNone(self.tickers_ibex35, " - [NO OK] Listas de tickers no vacías")
        self.logger_BDs.info(" - [OK] Listas de tickers no vacías")
        for ticker in self.tickers_dj30:
            self.assertIsInstance(ticker, str, " - [NO OK] Todos los tickers deben de ser strings")
        for ticker in self.tickers_ibex35:
            self.assertIsInstance(ticker, str, " - [NO OK] Todos los tickers deben de ser strings")
        self.logger_BDs.info(" - [OK] Todos los tickers deben de ser strings")


    def test_02_longitudIndices(self):
        self.logger_BDs.info("")
        self.logger_BDs.info("----------------------------------")
        self.logger_BDs.info("TEST LONGITUD LISTAS TICKERS")
        self.logger_BDs.info("----------------------------------")

        self.assertEqual(len(self.tickers_dj30), 30, " - [NO OK] Tener 30 tickers en la lista del DJ30")
        self.logger_BDs.info(" - [OK] Tener 30 tickers en la lista del DJ30")
        self.assertEqual(len(self.tickers_ibex35), 35, " - [NO OK] Tener 35 tickers en la lista del IBEX35")
        self.logger_BDs.info(" - [OK] Tener 35 tickers en la lista del IBEX35")


    def test_03_tablasDJ30(self):
        self.logger_BDs.info("")
        self.logger_BDs.info("----------------------------------")
        self.logger_BDs.info("TEST TABLAS DJ30 BIEN CREADAS")
        self.logger_BDs.info("----------------------------------")

        # Para obtener el nombre de todas las tablas en la BD (usando
        # SQLite3, ojo)
        with connections['dj30'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.nombresStocks = cursor.fetchall()

        # En stock[0] tengo el nombre de la tabla
        tablas = [stock[0] for stock in self.nombresStocks if stock[0] not in ['django_migrations', 'sqlite_sequence']]
        
        self.assertEqual(len(tablas), 30, " - [NO OK] Tener 30 tablas en DJ30")
        self.logger_BDs.info(" - [OK] Tener 30 tablas en DJ30")
        self.logger_BDs.info("")
        # Comprobar que todos los tickers tienen su 
        # correspondiente tabla en la BD
        for ticker in self.tickers_dj30:
            self.assertIn(ticker, tablas, f" - [NO OK] Tener tabla en BD para {ticker}")
            self.logger_BDs.info(f" - [OK] Tener tabla en BD para {ticker}")
            # Aprovecho para comprobar que las columnas también 
            # se crean de manera adecuada
            with connections['dj30'].cursor() as cursor:
                # Obtener info. de columnas de una tabla (ticker)
                cursor.execute(f"PRAGMA table_info({ticker});")
                columnas = [_[1] for _ in cursor.fetchall()]
                cursor.close()
                self.assertEqual(self.columnas, columnas, f" - [NO OK] Tener columnas adecuadas para tabla de {ticker}")
                self.logger_BDs.info(f" - [OK] Tener columnas adecuadas para tabla de {ticker}")
    

    def test_04_crearObjetosDJ30(self):
        self.logger_BDs.info("")
        self.logger_BDs.info("----------------------------------")
        self.logger_BDs.info("TEST CREAR REGISTROS EN DJ30")
        self.logger_BDs.info("----------------------------------")

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
        self.assertEqual(str(stock),'AAPL - Apple Inc. . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 105.0', f" - [NO OK] Crear datos con el formato esperado")
        self.logger_BDs.info(f" - [OK] Crear datos con el formato esperado")
        self.assertEqual(stock.id, 1, f" - [NO OK] Guardar 'id' autoincremental")
        self.logger_BDs.info(f" - [OK] Guardar 'id' autoincremental")


    def test_05_tablasIBEX35(self):
        self.logger_BDs.info("")
        self.logger_BDs.info("----------------------------------")
        self.logger_BDs.info("TEST TABLAS IBEX35 BIEN CREADAS")
        self.logger_BDs.info("----------------------------------")

        # Para obtener el nombre de todas las tablas en la BD (usando
        # SQLite3, ojo)
        with connections['ibex35'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.nombresStocks = cursor.fetchall()
            cursor.close()

        # En stock[0] tengo el nombre de la tabla
        tablas = [stock[0] for stock in self.nombresStocks if stock[0] not in ['django_migrations', 'sqlite_sequence']]
        
        self.assertEqual(len(tablas), 35, " - [NO OK] Tener 35 tablas en IBEX35")
        self.logger_BDs.info(" - [OK] Tener 35 tablas en IBEX35")
        self.logger_BDs.info("")
        # Comprobar que todos los tickers tienen su 
        # correspondiente tabla en la BD
        for ticker in self.tickers_ibex35:
            self.assertIn(ticker, tablas, f" - [NO OK] Tener tabla en BD para {ticker}")
            self.logger_BDs.info(f" - [OK] Tener tabla en BD para {ticker}")
            # Aprovecho para comprobar que las columnas también 
            # se crean de manera adecuada
            with connections['ibex35'].cursor() as cursor:
                # Obtener info. de columnas de una tabla (ticker)
                cursor.execute(f"PRAGMA table_info({ticker});")
                columnas = [_[1] for _ in cursor.fetchall()]
                cursor.close()
                self.assertEqual(self.columnas, columnas, f" - [NO OK] Tener columnas adecuadas para tabla de {ticker}")
                self.logger_BDs.info(f" - [OK] Tener columnas adecuadas para tabla de {ticker}")


    def test_06_crearObjetosIBEX35(self):
        self.logger_BDs.info("")
        self.logger_BDs.info("----------------------------------")
        self.logger_BDs.info("TEST CREAR REGISTROS EN IBEX35")
        self.logger_BDs.info("----------------------------------")

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
        self.assertEqual(str(stock),'ITX_MC - Industria de Diseño Textil, S.A. . Fecha: 2025-01-01 12:00:00+00:00. Cierre: 29.795',f" - [NO OK] Crear datos con el formato esperado")
        self.logger_BDs.info(f" - [OK] Crear datos con el formato esperado")
        self.assertEqual(stock.id, 1, f" - [NO OK] Hacer 'id' autoincremental")
        self.logger_BDs.info(f" - [OK] Hacer 'id' autoincremental")