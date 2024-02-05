from django.test import TestCase
from django.contrib.auth.models import User
# Lo importo como 'tz' para no confundir con timezone de datetime
from django.utils import timezone as tz
from datetime import timedelta
from DashBoard.models import StockComprado, StockSeguimiento
from log.logger.logger import get_logger_dashboard
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
            
            log = get_logger_dashboard('DashBoardViews')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS DASHBOARD VIEWS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance



class TestDashBoardViews(TestCase):

    # NOTA: Posibles códigos HTML para algunos de los tests de esta clase.
    # 200 OK, 201 Created, 204 No Content, 302 Redirect, 400 Bad Request, 401 Unauthorized, 
    # 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 500 Internal Server Error

    def setUp(self):
        Singleton()
        self.log = get_logger_dashboard('DashBoardViews')      

        # Formularios básicos de prueba
        self.form_1_ok = {'num_acciones': 100, 'precio_compra': 10.5,}      
        self.form_2_ok = {'precio_entrada_deseado': 15.5,}
        self.form_vacío = {}       
        # Formulario en entorno real (no habrá registros en la BD)
        self.form_3_no_ok = {'ticker': 'AAPL','fecha_compra': '02/02/1930', 'num_acciones': 50, 'precio_compra': float(148)}

        self.usuarioTest = User.objects.create_user(username='usuario', password='p@ssword')

        self.fecha = tz.now() - timedelta(days=5)
        self.stockComprado_1 = StockComprado.objects.create(
            usuario=self.usuarioTest,
            ticker_bd='ACS_MC',
            bd='ibex35',
            ticker='ACS.MC',
            nombre_stock='ACS, Actividades de Construcción y Servicios, S.A.',
            fecha_compra=self.fecha,
            num_acciones=10,
            precio_compra=100.5,
            moneda='EUR',
            sector='Industrials'
        )

        self.stockSeguimiento_1 = StockSeguimiento.objects.create(
            usuario=self.usuarioTest,
            ticker_bd='ACS_MC',
            bd='ibex35',
            ticker='ACS.MC',
            nombre_stock='ACS, Actividades de Construcción y Servicios, S.A.',
            fecha_inicio_seguimiento=tz.now(),
            precio_entrada_deseado=15.5,
            moneda='EUR',
            sector='Industrials'
        )
    

    def test_views_nueva_compra_sin_login(self):
        response = self.client.get('/dashboard/nueva_compra/')
        self.assertEqual(response.status_code, 302, " - [NO OK] Que página de 'nueva_compra' retorne '302...' sin login")
        self.log.info(" - [OK] Que página de 'nueva_compra' retorne '302...' sin login'")


    def test_views_nueva_compra_con_login(self):
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/nueva_compra/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de 'nueva_compra' retorne '200 ok' con login")
        self.log.info(" - [OK] Que página de 'nueva_compra' retorne '200 ok' con login")


    def test_views_template_válida_nueva_compra(self):
        response = self.client.get('/dashboard/nueva_compra/')
        self.assertTemplateUsed(response, 'nueva_compra.html', " - [NO OK] Asignar 'template' de nueva compra")
        self.log.info(" - [OK] Asignar 'template' de nueva compra")


    