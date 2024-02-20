from django.test import TestCase
from django.contrib.auth.models import User
# Lo importo como 'tz' para no confundir con timezone de datetime
from django.utils import timezone as tz
from datetime import timedelta
from DashBoard.models import StockComprado, StockSeguimiento
from log.logger.logger import get_logger_configurado
# Refactoring:
# ------------
# No puedo usar ValueError ni ValidationError, el error
# que se devuelve con la fecha y bd no válidas es IntegrityError
# from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('DashBoardModels')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS DASHBOARD MODELS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance



class TestDashBoardModels(TestCase):

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('DashBoardModels')      

        self.user = User.objects.create_user(username='usuario', password='p@ssword')

        self.fecha = tz.now() - timedelta(days=5)
        self.stockComprado_1 = StockComprado.objects.create(
            usuario=self.user,
            ticker_bd='ACS_MC',
            bd='ibex35',
            ticker='ACS.MC',
            nombre_stock='ACS, Actividades de Construcción y Servicios, S.A.',
            fecha_compra=self.fecha,
            num_acciones=10,
            precio_compra=100.0,
            moneda='EUR',
            sector='Industrials'
        )

        self.stockComprado_2 = StockComprado.objects.create(
            usuario=self.user,
            ticker_bd='RIO_L',
            bd='ftse100',
            ticker='RIO.L',
            nombre_stock='Rio Tinto Group',
            fecha_compra=self.fecha,
            num_acciones=10,
            precio_compra=1000.0,
            moneda='GBp',
            sector='Basic Materials'
        )

        self.stockSeguimiento_1 = StockSeguimiento.objects.create(
            usuario=self.user,
            ticker_bd='ACS_MC',
            bd='ibex35',
            ticker='ACS.MC',
            nombre_stock='ACS, Actividades de Construcción y Servicios, S.A.',
            fecha_inicio_seguimiento=tz.now(),
            precio_entrada_deseado=15.5,
            moneda='EUR',
            sector='Industrials'
        )



    def test_models_StockComprado_posicion(self):
        # La posición no será un campo, sino que se calculará
        res = self.stockComprado_1.posicion()
        self.assertEqual(res, 100*10, " - [NO OK] Calcular posición de StockComprado")
        self.log.info(" - [OK] Calcular posición de StockComprado")

    
    def test_models_StockComprado_posicion_GBp(self):
        # La posición no será un campo, sino que se calculará
        res = self.stockComprado_2.posicion()
        self.assertEqual(res, 1000*10 / 100, " - [NO OK] Calcular posición de StockComprado en GBp")
        self.log.info(" - [OK] Calcular posición de StockComprado en GBp")


    def test_models_StockComprado_fecha_futura(self):
        # No se podrán meter fechas futuras al guardar 
        # un stock como comprado
        with self.assertRaises(IntegrityError):
            StockComprado.objects.create(
                usuario=self.user,
                ticker_bd='AAPL',
                bd='dj30',
                ticker='AAPL',
                nombre_stock='Apple Inc.',
                fecha_compra=tz.now() + timedelta(days=100),
                num_acciones=5,
                precio_compra=50.0,
                moneda='USD',
                sector='Technology'
            )
        self.log.info(" - [OK] Evitar fechas futuras de StockComprado")


    def test_models_StockComprado_bd_falsa(self):
        # Habrá limitación para el campo de las BDs, para que no se
        # puedan usar unas diferentes a las que indique
        with self.assertRaises(IntegrityError):
            StockComprado.objects.create(
                usuario=self.user,
                ticker_bd='AAPL',
                bd='bd_falsa',
                ticker='AAPL',
                nombre_stock='Apple Inc.',
                fecha_compra=self.fecha,
                num_acciones=5,
                precio_compra=50.0,
                moneda='USD',
                sector='Technology'
            )
        self.log.info(" - [OK] Evitar bases de datos falsas de StockComprado")


    def test_models_StockComprado_str(self):
        # Habrá un __str__ que me permita ver si el objeto
        # está bien creado (nombre - usuario - fecha - moneda)
        self.assertEqual(str(self.stockComprado_1), 
                         f"ACS, Actividades de Construcción y Servicios, S.A. - usuario - {self.fecha} - EUR",
                         " - [NO OK] StockComprado str")
        self.log.info(" - [OK] StockComprado str")


    def test_models_StockComprado_crear_borrar(self):
        self.assertEqual(StockComprado.objects.count(), 2, " - [NO OK] Crear/borrar StockComprado")
        self.assertEqual(self.stockComprado_1.ticker, 'ACS.MC', " - [NO OK] Crear/borrar StockComprado")
        self.stockComprado_1.delete()
        self.stockComprado_2.delete()
        self.assertEqual(StockComprado.objects.count(), 0, " - [NO OK] Crear/borrar StockComprado")
        self.log.info(" - [OK] Crear/borrar StockComprado")


    def test_models_StockSeguimiento_str(self):
        # Habrá un __str__ que me permita ver si el objeto
        # está bien creado (nombre - usuario - moneda)
        self.assertEqual(str(self.stockSeguimiento_1), 
                         "ACS, Actividades de Construcción y Servicios, S.A. - usuario - EUR",
                         " - [NO OK] StockSeguimiento str")
        self.log.info(" - [OK] StockSeguimiento str")


    def test_models_StockSeguimiento_crear_borrar(self):
        self.assertEqual(StockSeguimiento.objects.count(), 1, " - [NO OK] Crear/borrar StockSeguimiento")
        self.assertEqual(self.stockSeguimiento_1.ticker, 'ACS.MC', " - [NO OK] Crear/borrar StockSeguimiento")
        self.stockSeguimiento_1.delete()
        self.assertEqual(StockSeguimiento.objects.count(), 0, " - [NO OK] Crear/borrar StockSeguimiento")
        self.log.info(" - [OK] Crear/borrar StockSeguimiento")