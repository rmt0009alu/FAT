from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from DashBoard.models import StockComprado, StockSeguimiento
from DashBoard.views import _stocks_en_seguimiento, _evolucion_cartera, _hay_errores, nueva_compra, nuevo_seguimiento, eliminar_compras, eliminar_seguimientos, dashboard
from log.logger.logger import get_logger_configurado
from datetime import datetime, timezone
from django.core.exceptions import ValidationError
import decimal
from datetime import timedelta
from DashBoard.forms import StockCompradoForm, StockSeguimientoForm
from util.tickers import Tickers_BDs
# Alias 'tz' para no confundir con datetime.timezone
from django.utils import timezone as tz
# Para usar los modelos creados de forma dinámica
from django.apps import apps
# Para evitar los warning de DateTimeField en nueva_compra
import warnings





# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('DashBoardViews')
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
        self.log = get_logger_configurado('DashBoardViews')      

        # Formularios básicos de prueba
        self.form_1_ok = {'ticker': 'AAPL','fecha_compra': '09/01/2024', 'num_acciones': 50, 'precio_compra': float(148)}
        self.form_2_ok = {'ticker': 'AAPL', 'precio_entrada_deseado': 130.72}
        self.form_vacío = {}       
        # Formulario en entorno real (no habrá registros en la BD)
        self.form_3_no_ok = {'ticker': 'AAPL','fecha_compra': '02/02/1930', 'num_acciones': 50, 'precio_compra': float(148)}
        self.form_4_no_ok = {'ticker': 'tickerFalso','fecha_compra': '09/01/2024', 'num_acciones': 50, 'precio_compra': float(148)}
        self.form_5_no_ok = {'ticker': 'tickerFalso', 'precio_entrada_deseado': float(135.3)}

        self.usuarioTest = User.objects.create_user(username='usuarioTest', password='p@ssword')

        # Creo unos registros de stocks para que al consultar los datos
        # en stock seguimiento/comprado haya info. de los mismos:
        model = apps.get_model('Analysis', 'AAPL')
        self.stock_1 = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
            currency = 'USD', sector = 'Technology'
        )
        
        model = apps.get_model('Analysis', 'ACS_MC')
        self.stock_2 = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='ACS_MC', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='ACS, Actividades de Construcción y Servicios, S.A.', 
            currency = 'EUR', sector = 'Industrials'
        )

        model = apps.get_model('Analysis', 'IBM')
        self.stock_3 = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
            currency = 'USD', sector = 'Technology'
        )
        
        model = apps.get_model('Analysis', 'ELE_MC')
        self.stock_4 = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=10.0, high=11.0, low=9.0, close=10.5, volume=1000,
            dividends=0.0, stock_splits=0.0, ticker='ELE_MC', previous_close=10.0,
            percent_variance=0.5, mm20=10.2, mm50=10.4, mm200=9.8, name='Endesa, S.A.', 
            currency = 'EUR', sector = 'Utilities'
        )

        model = apps.get_model('Analysis', 'MAP_MC')
        self.stock_5 = model.objects.using('ibex35').create(date=datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc),
            open=2.03, high=2.064, low=2.024, close=2.028, volume=100000,
            dividends=0.0, stock_splits=0.0, ticker='MAP_MC', previous_close=2.0,
            percent_variance=0.14, mm20=2, mm50=2.1, mm200=1.98, name='Mapfre, S.A.', 
            currency = 'EUR', sector = 'Financial Services'
        )

        self.fecha1 = tz.now() - timedelta(days=5)
        self.fecha2 = tz.now()
        
    
    def test_views_dashboard_status_code_sin_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302, " - [OK] Que página de 'DashBoard' retorne '302...' sin login'")
        self.log.info(" - [OK] Que página de 'DashBoard' retorne '302...' sin login'")

    
    def test_views_dashboard_con_compras_y_seguimiento(self):
        self._crear_stockComprado_1()
        self._crear_stockComprado_2()
        self._crear_stockSeguimiento_1()
        self._crear_stockSeguimiento_2()
        request = RequestFactory().post("/dashboard/")
        request.user = self.usuarioTest      
        response = dashboard(request)
        self.assertEqual(response.status_code, 200, " - [NO OK] Datos DashBoard con compras y seguimiento")
        self.assertTrue(self.stockComprado_1.ticker in response.content.decode(), " - [NO OK] Datos DashBoard con compras y seguimiento")
        self.assertTrue(self.stockComprado_2.ticker in response.content.decode(), " - [NO OK] Datos DashBoard con compras y seguimiento")
        self.assertTrue(self.stockSeguimiento_1.ticker in response.content.decode(), " - [NO OK] Datos DashBoard con compras y seguimiento")
        self.assertTrue(self.stockSeguimiento_2.ticker in response.content.decode(), " - [NO OK] Datos DashBoard con compras y seguimiento")
        self.log.info(" - [OK] Datos DashBoard con compras y seguimiento")

    
    def test_views_dashboard_con_compras_y_sin_seguimiento(self):
        self._crear_stockComprado_1()
        self._crear_stockComprado_2()
        request = RequestFactory().post("/dashboard/")
        request.user = self.usuarioTest      
        response = dashboard(request)
        self.assertEqual(response.status_code, 200, " - [NO OK] Datos DashBoard con compras y sin seguimiento")
        self.assertTrue(self.stockComprado_1.ticker in response.content.decode(), " - [NO OK] Datos DashBoard con compras y sin seguimiento")
        self.assertTrue(self.stockComprado_2.ticker in response.content.decode(), " - [NO OK] Datos DashBoard con compras y sin seguimiento")
        # No puede haber otros datos como los de seguimiento
        self.assertTrue('AAPL' not in response.content.decode(), " - [NO OK] Datos DashBoard con compras y sin seguimiento")
        self.assertTrue('ELE.MC' not in response.content.decode(), " - [NO OK] Datos DashBoard con compras y sin seguimiento")
        self.log.info(" - [OK] Datos DashBoard con compras y sin seguimiento")


    def test_views_dashboard_sin_compras_y_con_seguimiento(self):
        self._crear_stockSeguimiento_1()
        self._crear_stockSeguimiento_2()
        request = RequestFactory().post("/dashboard/")
        request.user = self.usuarioTest      
        response = dashboard(request)
        self.assertEqual(response.status_code, 200, " - [NO OK] Datos DashBoard sin compras y con seguimiento")
        self.assertTrue(self.stockSeguimiento_1.ticker in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y con seguimiento")
        self.assertTrue(self.stockSeguimiento_2.ticker in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y con seguimiento")
        # No puede haber otros datos como los de coprados
        self.assertTrue('IBM' not in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y con seguimiento")
        self.assertTrue('ACS.MC' not in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y con seguimiento")
        self.log.info(" - [OK] Datos DashBoard sin compras y con seguimiento")

    
    def test_views_dashboard_sin_compras_y_sin_seguimiento(self):
        request = RequestFactory().post("/dashboard/")
        request.user = self.usuarioTest      
        response = dashboard(request)
        self.assertEqual(response.status_code, 200, " - [NO OK] Datos DashBoard sin compras y sin seguimiento")
        # No puede haber otros datos de comprados ni de seguimiento
        self.assertTrue('AAPL' not in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y sin seguimiento")
        self.assertTrue('ELE.MC' not in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y sin seguimiento")
        self.assertTrue('IBM' not in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y sin seguimiento")
        self.assertTrue('ACS.MC' not in response.content.decode(), " - [NO OK] Datos DashBoard sin compras y sin seguimiento")
        self.log.info(" - [OK] Datos DashBoard sin compras y sin seguimiento")

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


    def test_views_nueva_compra_post_con_fecha_no_válida(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=self.form_3_no_ok)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'nueva_compra' retorne mensaje con fecha no válida")
        self.assertContains(response, 'no existen registros')
        self.log.info(" - [OK] Que post a 'nueva_compra' retorne mensaje con fecha no válida")


    def test_views_nueva_compra_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=self.form_4_no_ok)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'nueva_compra' retorne mensaje con ticker no válido")
        self.assertContains(response, 'El ticker tickerFalso no está disponibe')
        self.log.info(" - [OK] Que post a 'nueva_compra' retorne mensajecon ticker no válido")
    

    def test_views_nueva_compra_datos_válidos(self):
        # Para evitar el warning de naive DateTime... ya que 
        # la entrada en el formulario se transforma en views.py
        # así el usuario puede usar un calendario
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        # Datos iguales a los del self.stock_5
        data = {
            "ticker": "MAP.MC",
            "fecha_compra": '01/02/2024',
            "num_acciones": 50,
            "precio_compra": 2.04,
        }
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=data)
        self.assertEqual(response.status_code, 302, " - [NO OK] Redirigir a 'dashboard' con datos válidos en 'nueva_compra'")
        self.assertEqual(response.url, "/dashboard/", " - [NO OK] Redirigir a 'dashboard' con datos válidos en 'nueva_compra'")
        self.log.info(" - [OK] Redirigir a 'dashboard' con datos válidos en 'nueva_compra'")


    def test_views_nueva_compra_fecha_si_registro(self):
        # Datos iguales a los del self.stock_5
        data = {
            "ticker": "MAP.MC",
            "fecha_compra": '01/02/1930',
            "num_acciones": 50,
            "precio_compra": 2.04,
        }
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'nueva_compra' retorne mensaje con ticker no válido")
        self.assertContains(response, 'no existen registros')
        self.log.info(" - [OK] Redirigir a 'dashboard' con datos válidos en 'nueva_compra'")


    def test_views_nueva_compra_precio_fuera_de_rango_posible(self):
        # Datos iguales a los del self.stock_5
        data = {
            "ticker": "MAP.MC",
            "fecha_compra": '01/02/2024',
            "num_acciones": 50,
            "precio_compra": 12.04,
        }
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nueva_compra/', data=data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Precio fuera de rango posible en 'nueva_compra'")
        self.assertContains(response, 'Ese precio no es posible para el día')
        self.log.info(" - [OK] Precio fuera de rango posible en 'nueva_compra'")


    def test_views_nueva_compra_context_datos_no_válidos(self):
        request = RequestFactory().post("/nueva_compra/")
        request.user = self.usuarioTest
        # Datos válidos para el request. simulo formulario con errores
        request.POST = {
            "ticker": "tickerInventado",
            "precio_compra": 16.5,
        }
        response = nueva_compra(request)
        self.assertEqual(response.status_code, 200, " - [NO OK] No redirigir y seguir en 'nueva_compra' con formulario no válido")
        self.assertContains(response, "Error inesperado en el formulario")
        self.log.info(" - [OK] No redirigir y seguir en 'nueva_compra' con formulario no válido")

    
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
    

    def test_views_eliminar_compras_post(self):
        request = RequestFactory().post('/dashboard/eliminar_compras/')
        request.user = self.usuarioTest
        response = eliminar_compras(request)
        self.assertEqual(response.status_code, 302, " - [NO OK] Redirigir a 'dashboard' tras eliminar compras")
        self.assertEqual(response.url, '/dashboard/', " - [NO OK] Redirigir a 'dashboard' tras eliminar compras")
        self.log.info(" - [OK] Redirigir a 'dashboard' tras eliminar compras")
    
    
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
    

    def test_views_nuevo_seguimiento_datos_válidos(self):
        request = RequestFactory().post("/nuevo_seguimiento/")
        request.user = self.usuarioTest
        # Datos válidos para el request
        request.POST = {
            "ticker": "AAPL",
            "precio_entrada_deseado": 100.00,
        }
        context = nuevo_seguimiento(request)
        self.assertEqual(context.status_code, 302, " - [NO OK] Redirigir a 'dashboard' con datos válidos en '_nuevo_seguimiento'")
        self.assertEqual(context.url, "/dashboard/", " - [NO OK] Redirigir a 'dashboard' con datos válidos en '_nuevo_seguimiento'")
        self.log.info(" - [OK] Redirigir a 'dashboard' con datos válidos en '_nuevo_seguimiento'")


    def test_views_nuevo_seguimiento_datos_no_válidos(self):
        request = RequestFactory().post("/nuevo_seguimiento/")
        request.user = self.usuarioTest
        # Datos válidos para el request. simulo formulario con errores
        request.POST = {
            "ticker": "tickerInventado",
            "precio_entrada_deseado": 'abc',
        }
        response = nuevo_seguimiento(request)
        self.assertEqual(response.status_code, 200, " - [NO OK] No redirigir y seguir en '_nuevo_seguimiento' con formulario no válido")
        self.assertContains(response, "Error inesperado en el formulario")
        self.log.info(" - [OK] No redirigir y seguir en '_nuevo_seguimiento' con formulario no válido")
    

    def test_views_nuevo_seguimiento_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/dashboard/nuevo_seguimiento/', data=self.form_5_no_ok)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'nuevo_seguimiento' retorne mensaje con ticker no válido")
        self.assertContains(response, 'El ticker tickerFalso no está disponibe')
        self.log.info(" - [OK] Que post a 'nuevo_seguimiento' retorne mensaje con ticker no válido")
    

    # ---------------------------
    # TESTS ELIMINAR SEGUIMIENTOS
    # ---------------------------
    def test_views_eliminar_seguimientos_status_code_sin_login(self):
        response = self.client.get('/dashboard/eliminar_seguimientos/')
        self.assertEqual(response.status_code, 302, " - [NO OK] Que página de 'eliminar_seguimientos' retorne '302...' sin login")
        self.log.info(" - [OK] Que página de 'eliminar_seguimientos' retorne '302...' sin login'")


    def test_views_eliminar_seguimientos_status_code_con_login(self):
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/eliminar_seguimientos/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de 'eliminar_seguimientos' retorne '200 ok' con login")
        self.log.info(" - [OK] Que página de 'eliminar_seguimientos' retorne '200 ok' con login")

    
    def test_views_eliminar_seguimientos_templates_válidas(self):   
        # Fuerzo el login de un usuario
        self.client.force_login(self.usuarioTest)
        response = self.client.get('/dashboard/eliminar_seguimientos/')   
        self.assertTemplateUsed(response, 'eliminar_seguimientos.html', " - [NO OK] Asignar 'template' de eliminar_seguimientos y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de eliminar_seguimientos y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de eliminar_seguimientos y cargar base.html")
    

    def test_views_eliminar_seguimientos_post_sin_login(self):
        response = self.client.post('/dashboard/eliminar_seguimientos/', data=self.form_1_ok)
        self.assertEqual(response.status_code, 302, " - [NO OK] Que POST a 'eliminar_seguimientos' retorne '302...' sin login")
        self.log.info(" - [OK] Que POST a 'eliminar_seguimientos' retorne '302...' sin login")
    

    def test_views_eliminar_seguimientos_post(self):
        request = RequestFactory().post('/dashboard/eliminar_seguimientos/')
        request.user = self.usuarioTest
        response = eliminar_seguimientos(request)
        self.assertEqual(response.status_code, 302, " - [NO OK] Redirigir a 'dashboard' tras eliminar seguimientos")
        self.assertEqual(response.url, '/dashboard/', " - [NO OK] Redirigir a 'dashboard' tras eliminar seguimientos")
        self.log.info(" - [OK] Redirigir a 'dashboard' tras eliminar seguimientos")

    # ------------------------
    # TESTS MÉTODOS AUXILIARES
    # ------------------------
    def test_views_stocks_seguimiento_lista_vacía(self):
        seguimientoUsuario = []
        stocksEnSeg = _stocks_en_seguimiento(seguimientoUsuario)
        self.assertEqual(stocksEnSeg, [], " - [NO OK] _stocks_en_seguimiento vacío si no hay stocks seguidos")
        self.log.info(" - [OK] _stocks_en_seguimiento vacío si no hay stocks seguidos")
    
    
    def test_views_stocks_seguimiento_lista_un_dato(self):
        self._crear_stockSeguimiento_1()
        seguimientoUsuario = [self.stockSeguimiento_1]
        stocksEnSeg = _stocks_en_seguimiento(seguimientoUsuario)
        self.assertEqual(len(stocksEnSeg), 1)
        self.assertEqual(stocksEnSeg[0]["ticker_bd"], "AAPL", " - [NO OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
        self.assertEqual(stocksEnSeg[0]["fecha_inicio_seguimiento"], self.fecha2, " - [NO OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
        self.assertEqual(stocksEnSeg[0]["precio_entrada_deseado"], 99.5, " - [NO OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
        self.log.info(" - [OK] _stocks_en_seguimiento reconoce un dato de stocks seguidos")
    
    
    def test_views_stocks_seguimiento_datos_no_válidos(self):        
        # seguimientoUsuario = []
        with self.assertRaises(ValidationError):
            # Dato de precio de entrada deseado no válido
            self.stockSeguimiento_2 = StockSeguimiento.objects.create(
                usuario=self.usuarioTest, ticker_bd='AAPL',
                bd='dj30', ticker='AAPL',
                nombre_stock='Apple Inc.',
                fecha_inicio_seguimiento=self.fecha2,
                precio_entrada_deseado='abc',           
                moneda='USD', sector='Technology'
            )
            # Se podría hacer, pero va a ser inaccesible por el primer raise
            # seguimientoUsuario.append(self.stockSeguimiento_2)
            # with self.assertRaises(decimal.InvalidOperation):
            #     _stocks_en_seguimiento(seguimientoUsuario)
        self.log.info(" - [OK] _stocks_en_seguimiento no permite datos no válidos")
    
    
    def test_views_evolucion_cartera_lista_vacía(self):
        comprasUsuario = []
        evolCartera, evolTotal = _evolucion_cartera(comprasUsuario)
        self.assertEqual(evolCartera, [], " - [NO OK] _evolucion_cartera vacío si no hay stocks comprados")
        self.assertEqual(evolTotal, 0.0, " - [NO OK] _evolucion_cartera vacío si no hay stocks comprados")
        self.log.info(" - [OK] _evolucion_cartera vacío si no hay stocks comprados")
    

    def test_views_evolucion_cartera_lista_un_dato(self):
        self._crear_stockComprado_1()
        comprasUsuario = [self.stockComprado_1]
        evolCartera, evolTotal = _evolucion_cartera(comprasUsuario)
        self.assertEqual(len(evolCartera), 1)
        self.assertEqual(evolCartera[0]["ticker_bd"], "ACS_MC")
        self.assertEqual(evolCartera[0]["fecha_compra"], self.fecha1)
        self.assertEqual(evolCartera[0]["num_acciones"], 10)
        self.assertEqual(evolCartera[0]["precio_compra"], 100.00)
        self.assertEqual(evolCartera[0]["cierre"], 105.00)
        # Tiene que haber evolucionado de 100 a 105 -> 5%
        self.assertEqual(evolCartera[0]["evol"], 5.0)
        self.assertEqual(evolTotal, 5.0)
        self.log.info(" - [OK] _evolucion_cartera reconoce un dato de stocks comprado")
    

    def test_views_hay_errores_datos_ok(self):
        fecha = datetime.today()
        bd = "ibex35"
        ticker = "ACS_MC"
        model = apps.get_model('Analysis', ticker)
        entrada = model.objects.using(bd).order_by('-date')[:1]
        precio_compra = entrada[0].close
        caso = "1"
        context = _hay_errores(fecha, bd, ticker, entrada, precio_compra, caso)
        self.assertEqual(context, False, " - [NO OK] _hay_errores reconoce datos válidos")
        self.log.info(" - [OK] _hay_errores reconoce datos válidos")

    
    def test_views_hay_errores_datos_bd_none_caso_1(self):
        fecha = datetime.today()
        bd = None
        ticker = "ACS_MC"
        context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='1')
        self.assertEqual(context["msg_error"], f'El ticker {ticker} no está disponibe', " - [NO OK] _hay_errores reconoce bd none")
        self.assertEqual(context["form"], StockCompradoForm, " - [NO OK] _hay_errores reconoce bd none")
        self.assertEqual(context["listaTickers"], Tickers_BDs.tickersDisponibles(), " - [NO OK] _hay_errores reconoce bd none")
        self.log.info(" - [OK] _hay_errores reconoce bd none")

    
    def test_views_hay_errores_datos_fecha_futura_caso_1(self):
        fecha = datetime.today() + timedelta(days=1000)
        bd = 'ibex35'
        ticker = "ACS_MC"
        context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='1')
        self.assertEqual(context["msg_error"], 'No se pueden introducir fechas futuras', " - [NO OK] _hay_errores reconoce fecha futura")
        self.assertEqual(context["form"], StockCompradoForm, " - [NO OK] _hay_errores reconoce fecha futura")
        self.assertEqual(context["listaTickers"], Tickers_BDs.tickersDisponibles(), " - [NO OK] _hay_errores reconoce fecha futura")
        self.log.info(" - [OK] _hay_errores reconoce fecha futura")

    
    def test_views_hay_errores_entrada_no_existe_caso_2(self):
        fecha = datetime.today()
        fechaConFormato = fecha.strftime("%d/%m/%Y")
        bd = "ibex35"
        ticker = "ACS_MC"
        model = apps.get_model('Analysis', ticker)
        entrada = model.objects.using(bd).filter(date=tz.now() - timedelta(days=500))
        precio_compra = 100
        caso = "2"
        context = _hay_errores(fecha, bd, ticker, entrada, precio_compra, caso)
        self.assertEqual(context["msg_error"], 
                         f'El {fechaConFormato} (d/m/Y) corresponde a un festivo, fin de semana o no existen registros.', 
                         " - [NO OK] _hay_errores reconoce entrada inexistente")
        self.assertEqual(context["form"], StockCompradoForm, " - [NO OK] _hay_errores reconoce entrada inexistente")
        self.assertEqual(context["listaTickers"], Tickers_BDs.tickersDisponibles(), " - [NO OK] _hay_errores reconoce entrada inexistente")
        self.log.info(" - [OK] _hay_errores reconoce entrada inexistente")

    
    def test_views_hay_errores_entrada_existe_precio_no_caso_2(self):
        fecha = datetime.today()
        fechaConFormato = fecha.strftime("%d/%m/%Y")
        bd = "ibex35"
        ticker = "ACS_MC"
        model = apps.get_model('Analysis', ticker)
        entrada = model.objects.using(bd).order_by('-date')[:1]
        precio_compra = 10000
        caso = "2"
        context = _hay_errores(fecha, bd, ticker, entrada, precio_compra, caso)
        self.assertEqual(context["msg_error_2"], 
                         f'Ese precio no es posible para el día {fechaConFormato} (d/m/Y).', 
                         " - [NO OK] _hay_errores reconoce precio fuera de rango")
        self.assertEqual(context["form"], StockCompradoForm, " - [NO OK] _hay_errores reconoce precio fuera de rango")
        self.assertEqual(context["listaTickers"], Tickers_BDs.tickersDisponibles(), " - [NO OK] _hay_errores reconoce precio fuera de rango")
        self.assertEqual(context["min"], entrada[0].low, " - [NO OK] _hay_errores reconoce precio fuera de rango")
        self.assertEqual(context["max"], entrada[0].high, " - [NO OK] _hay_errores reconoce precio fuera de rango")
        self.log.info(" - [OK] _hay_errores reconoce precio fuera de rango")

    
    def test_views_hay_errores_datos_bd_none_caso_3(self):
        fecha = datetime.today()
        bd = None
        ticker = "ACS_MC"
        context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='3')
        self.assertEqual(context["msg_error"], f'El ticker {ticker} no está disponibe', " - [NO OK] _hay_errores reconoce bd none para stocks seguidos")
        self.assertEqual(context["form"], StockSeguimientoForm, " - [NO OK] _hay_errores reconoce bd none para stocks seguidos")
        self.assertEqual(context["listaTickers"], Tickers_BDs.tickersDisponibles(), " - [NO OK] _hay_errores reconoce bd none para stocks seguidos")
        self.log.info(" - [OK] _hay_errores reconoce bd none para stocks seguidos")

    
    # --------------------------------------
    # MÉTODOS AUXILIARES PARA AGILIZAR TESTS
    # --------------------------------------
    def _crear_stockComprado_1(self):
        # A partir de aquí simulo los StockComprados y los StockSeguimiento
        self.stockComprado_1 = StockComprado.objects.create(
            usuario=self.usuarioTest, ticker_bd='ACS_MC',
            bd='ibex35', ticker='ACS.MC',
            nombre_stock='ACS, Actividades de Construcción y Servicios, S.A.',
            fecha_compra=self.fecha1, num_acciones=10,
            precio_compra=100.0, moneda='EUR',
            sector='Industrials'
        )

    def _crear_stockComprado_2(self):
        self.stockComprado_2 = StockComprado.objects.create(
            usuario=self.usuarioTest, ticker_bd='IBM',
            bd='dj30', ticker='IBM',
            nombre_stock='International Business Machines Corporation',
            fecha_compra=self.fecha1, num_acciones=10,
            precio_compra=100.0, moneda='USD',
            sector='Technology'
        )

    def _crear_stockSeguimiento_1(self):
        self.stockSeguimiento_1 = StockSeguimiento.objects.create(
            usuario=self.usuarioTest, ticker_bd='AAPL',
            bd='dj30', ticker='AAPL',
            nombre_stock='Apple Inc.',
            fecha_inicio_seguimiento=self.fecha2,
            precio_entrada_deseado=99.5,
            moneda='USD', sector='Technology')
    
    def _crear_stockSeguimiento_2(self):
        self.stockSeguimiento_2 = StockSeguimiento.objects.create(
            usuario=self.usuarioTest, ticker_bd='ELE_MC',
            bd='ibex35', ticker='ELE.MC',
            nombre_stock='Endesa, S.A.',
            fecha_inicio_seguimiento=self.fecha2,
            precio_entrada_deseado=99.5,
            moneda='EUR', sector='Utilities')
    