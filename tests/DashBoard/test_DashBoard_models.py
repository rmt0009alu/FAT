from django.test import TestCase
from django.contrib.auth.models import User
# Lo importo como 'tz' para no confundir con timezone de datetime
from django.utils import timezone as tz
from datetime import timedelta
from DashBoard.models import StockComprado, StockSeguimiento
# from django.core.exceptions import ValidationError
# from django.db.utils import IntegrityError


class StockModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='usuario', password='p@ssword')

        self.fecha = tz.now()
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
        self.assertEqual(self.stockComprado_1.posicion(), 100*10)


    def test_models_StockComprado_fecha_futura(self):
        # No se podrán meter fechas futuras al guardar 
        # un stock como comprado
        with self.assertRaises(ValueError):
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


    def test_models_StockComprado_bd_falsa(self):
        # Habrá limitación para el campo de las BDs, para que no se
        # puedan usar unas diferentes a las que indique
        with self.assertRaises(ValueError):
            StockComprado.objects.create(
                usuario=self.user,
                ticker_bd='AAPL',
                bd='bd_falsa',
                ticker='AAPL',
                nombre_stock='Apple Inc.',
                fecha_compra=tz.now(),
                num_acciones=5,
                precio_compra=50.0,
                moneda='USD',
                sector='Technology'
            )


    def test_models_StockComprado_str(self):
        # Habrá un __str__ que me permita ver si el objeto
        # está bien creado (nombre - usuario - fecha - moneda)
        self.assertEqual(str(self.stockComprado_1), 
                         f"ACS, Actividades de Construcción y Servicios, S.A. - usuario - {self.fecha} - EUR")


    def test_models_StockComprado_crear_borrar(self):
        self.assertEqual(StockComprado.objects.count(), 1)
        self.assertEqual(self.stockComprado_1.ticker, 'ACS.MC')
        self.stockComprado_1.delete()
        self.assertEqual(StockComprado.objects.count(), 0)


    def test_models_StockSeguimiento_str(self):
        # Habrá un __str__ que me permita ver si el objeto
        # está bien creado (nombre - usuario - moneda)
        self.assertEqual(str(self.stockSeguimiento_1), 
                         "ACS, Actividades de Construcción y Servicios, S.A. - usuario - EUR")


    def test_models_StockSeguimiento_crear_borrar(self):
        self.assertEqual(StockSeguimiento.objects.count(), 1)
        self.assertEqual(self.stockSeguimiento_1.ticker, 'ACS.MC')
        self.stockSeguimiento_1.delete()
        self.assertEqual(StockSeguimiento.objects.count(), 0)
