from django.test import TestCase
from django.contrib.auth.models import User
from DashBoard.models import StockSeguimiento
from DashBoard.views import _stocks_en_seguimiento
from log.logger.logger import get_logger_dashboard
from datetime import datetime, timezone
from django.core.exceptions import ValidationError
import decimal
# Alias 'tz' para no confundir con datetime.timezone
from django.utils import timezone as tz
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
    
    databases = '__all__'

    def setUp(self):
        Singleton()
        self.log = get_logger_dashboard('DashBoardViews')      

        # Formularios básicos de prueba
        self.form_1_ok = {'ticker': 'AAPL','fecha_compra': '09/01/2024', 'num_acciones': 50, 'precio_compra': float(148)}
        self.form_2_ok = {'ticker': 'AAPL', 'precio_entrada_deseado': 130.72}
        self.form_vacío = {}       
        # Formulario en entorno real (no habrá registros en la BD)
        self.form_3_no_ok = {'ticker': 'AAPL','fecha_compra': '02/02/1930', 'num_acciones': 50, 'precio_compra': float(148)}

        self.usuarioTest = User.objects.create_user(username='usuario', password='p@ssword')

        # Creo un stock ficticio para que al consultar los datos
        # en stock seguimiento, haya info. del mismo
        model = apps.get_model('Analysis', 'AAPL')
        self.stockFicticio = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
            currency = 'USD', sector = 'Technology')

        self.fecha = tz.now()
        self.stockSeguimiento_1 = StockSeguimiento.objects.create(
            usuario=self.usuarioTest, ticker_bd='AAPL',
            bd='dj30', ticker='AAPL',
            nombre_stock='Apple Inc.',
            fecha_inicio_seguimiento=self.fecha,
            precio_entrada_deseado=99.5,
            moneda='USD', sector='Technology')
        
        
        
    """
    def test_views_dashboard_status_code_sin_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302, " - [OK] Que página de 'DashBoard' retorne '302...' sin login'")
        self.log.info(" - [OK] Que página de 'DashBoard' retorne '302...' sin login'")


    # ------------------
    # TESTS NUEVA COMPRA
    # ------------------
    def test_views_nueva_compra_status_code_sin_login(self):
        response = self.client.get('/dashboard/nueva_compra/')
        self.assertEqual(response.status_code, 302, " - [NO OK] Que página de 'nueva_compra' retorne '302...' sin login")
        self.log.info(" - [OK] Que página de 'nueva_compra' retorne '302...' sin login'")


    def test_views_nueva_compra_status_code_con_login(self):
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/nueva_compra/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de 'nueva_compra' retorne '200 ok' con login")
        self.log.info(" - [OK] Que página de 'nueva_compra' retorne '200 ok' con login")


    def test_views_nueva_compra_templates_válidas(self):   
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/nueva_compra/')   
        self.assertTemplateUsed(response, 'nueva_compra.html', " - [NO OK] Asignar 'template' de nueva_compra y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de nueva_compra y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de nueva_compra y cargar base.html")
    

    def test_views_nueva_compra_post_sin_login(self):
        response = self.client.post('/dashboard/nueva_compra/', data=self.form_1_ok)
        self.assertEqual(response.status_code, 302, " - [NO OK] Que POST a 'nueva_compra' retorne '302...' sin login")
        self.log.info(" - [OK] Que POST a 'nueva_compra' retorne '302...' sin login")


    def test_views_nueva_compra_post_con_login(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=self.form_1_ok)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'nueva_compra' retorne '200 ok' con login")
        self.log.info(" - [OK] Que POST a 'nueva_compra' retorne '200 ok' con login")


    def test_views_nueva_compra_post_con_datos_no_validos(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=self.form_3_no_ok)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'nueva_compra' retorne '200 ok' con datos no válidos")
        self.assertContains(response, 'no existen registros')
        self.log.info(" - [OK] Que post a 'nueva_compra' retorne '200 ok' con datos no válidos")


    # ----------------------
    # TESTS ELIMINAR COMPRAS
    # ----------------------
    def test_views_eliminar_compras_status_code_sin_login(self):
        response = self.client.get('/dashboard/eliminar_compras/')
        self.assertEqual(response.status_code, 302, " - [NO OK] Que página de 'eliminar_compras' retorne '302...' sin login")
        self.log.info(" - [OK] Que página de 'eliminar_compras' retorne '302...' sin login'")


    def test_views_eliminar_compras_status_code_con_login(self):
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/eliminar_compras/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de 'eliminar_compras' retorne '200 ok' con login")
        self.log.info(" - [OK] Que página de 'eliminar_compras' retorne '200 ok' con login")

    
    def test_views_eliminar_compras_templates_válidas(self):   
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/eliminar_compras/')   
        self.assertTemplateUsed(response, 'eliminar_compras.html', " - [NO OK] Asignar 'template' de eliminar_compras y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de eliminar_compras y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de eliminar_compras y cargar base.html")
    

    def test_views_eliminar_compras_post_sin_login(self):
        response = self.client.post('/dashboard/eliminar_compras/', data=self.form_1_ok)
        self.assertEqual(response.status_code, 302, " - [NO OK] Que POST a 'eliminar_compras' retorne '302...' sin login")
        self.log.info(" - [OK] Que POST a 'eliminar_compras' retorne '302...' sin login")
    

    # -----------------------
    # TESTS NUEVO SEGUIMIENTO
    # -----------------------
    def test_views_nuevo_seguimiento_status_code_sin_login(self):
        response = self.client.get('/dashboard/nuevo_seguimiento/')
        self.assertEqual(response.status_code, 302, " - [NO OK] Que página de 'nuevo_seguimiento' retorne '302...' sin login")
        self.log.info(" - [OK] Que página de 'nuevo_seguimiento' retorne '302...' sin login'")


    def test_views_nuevo_seguimiento_status_code_con_login(self):
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/nuevo_seguimiento/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de 'nuevo_seguimiento' retorne '200 ok' con login")
        self.log.info(" - [OK] Que página de 'nuevo_seguimiento' retorne '200 ok' con login")


    def test_views_nuevo_seguimiento_templates_válidas(self):   
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/nuevo_seguimiento/')   
        self.assertTemplateUsed(response, 'nuevo_seguimiento.html', " - [NO OK] Asignar 'template' de nuevo_seguimiento y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de nuevo_seguimiento y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de nuevo_seguimiento y cargar base.html")
    

    def test_views_nuevo_seguimiento_post_sin_login(self):
        response = self.client.post('/dashboard/nuevo_seguimiento/', data=self.form_1_ok)
        self.assertEqual(response.status_code, 302, " - [NO OK] Que POST a 'nuevo_seguimiento' retorne '302...' sin login")
        self.log.info(" - [OK] Que POST a 'nuevo_seguimiento' retorne '302...' sin login")


    def test_views_nuevo_seguimiento_post_con_datos_no_validos(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nuevo_seguimiento/', data=self.form_3_no_ok)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'nuevo_seguimiento' retorne '200 ok' con datos no válidos y haya 'Error'")
        self.assertContains(response, 'Error')
        self.log.info(" - [OK] Que post a 'nuevo_seguimiento' retorne '200 ok' con datos no válidos y haya 'Error'")

    
    # ------------------------
    # TESTS MÉTODOS AUXILIARES
    # ------------------------
    def test_views_stocks_seguimiento_lista_vacía(self):
        seguimientoUsuario = []
        stocksEnSeg = _stocks_en_seguimiento(seguimientoUsuario)
        self.assertEqual(stocksEnSeg, [], " - [NO OK] _stocks_en_seguimiento vacío si no hay stocks seguidos")
        self.log.info(" - [OK] _stocks_en_seguimiento vacío si no hay stocks seguidos")
    
    
    def test_views_stocks_seguimiento_lista_un_dato(self):
        seguimientoUsuario = []
        seguimientoUsuario.append(self.stockSeguimiento_1)
        stocksEnSeg = _stocks_en_seguimiento(seguimientoUsuario)
        self.assertEqual(len(stocksEnSeg), 1)
        self.assertEqual(stocksEnSeg[0]["ticker_bd"], "AAPL", " - [NO OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
        self.assertEqual(stocksEnSeg[0]["fecha_inicio_seguimiento"], self.fecha, " - [NO OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
        self.assertEqual(stocksEnSeg[0]["precio_entrada_deseado"], 99.5, " - [NO OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
        self.log.info(" - [OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
    """
    
    def test_views_stocks_seguimiento_datos_no_válidos(self):        
        seguimientoUsuario = []

        with self.assertRaises(ValidationError):
            # Dato de precio de entrada deseado no válido
            self.stockSeguimiento_2 = StockSeguimiento.objects.create(
                usuario=self.usuarioTest, ticker_bd='AAPL',
                bd='dj30', ticker='AAPL',
                nombre_stock='Apple Inc.',
                fecha_inicio_seguimiento=self.fecha,
                precio_entrada_deseado='abc',           
                moneda='USD', sector='Technology'
            )
            seguimientoUsuario.append(self.stockSeguimiento_2)
            with self.assertRaises(decimal.InvalidOperation):
                _stocks_en_seguimiento(seguimientoUsuario)
        # self.assertEqual(cm.exception.messages, ['“abc” value must be a decimal number.'])

            
