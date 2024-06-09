from django.test import TestCase
from django.contrib.auth.models import User
# Para comprobar exception que lanza con usuarios repetidos
from django.db.transaction import TransactionManagementError
from django.urls import reverse
from log.logger.logger import get_logger_configurado
from datetime import datetime, timezone
import logging
import pandas as pd
import base64
from datetime import timedelta
# Alias 'tz' para no confundir con datetime.timezone
from django.utils import timezone as tz
from DashBoard.models import StockComprado
from Analysis.views import _formatear_volumen, _get_lista_rss, _get_datos, _generar_correlaciones, _crear_grafos, _normalizar_dataframes, _generar_graficas_comparacion
from Analysis.models import Sectores
from django.apps import apps
from util.tickers.Tickers_BDs import tickers_adaptados_dj30, tickers_adaptados_ibex35, tickers_adaptados_ftse100, tickers_adaptados_dax40, bases_datos_disponibles


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('AnalysisViews')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS ANALYSIS VIEWS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

class TestAnalysisViews(TestCase):

    # NOTA: Posibles códigos HTML para algunos de los tests de esta clase.
    # 200 OK, 201 Created, 204 No Content, 302 Redirect, 400 Bad Request, 401 Unauthorized, 
    # 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 500 Internal Server Error
    
    databases = '__all__'

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('AnalysisViews')
        self.usuarioTest = User.objects.create_user(username='usuarioTest', password='p@ssw0rdLarga')   
        # self.usuarioTest = User.objects.create_user(username='usuarioTest', password='p@ssword')
        self.datosUsuarioTest = {
            'username': 'usuarioTest',
            'password': 'p@ssw0rdLarga',
        }
        self.datosUsuarioFalso = {
            'username': 'usuarioFalso',
            'password': 'p@ssw0rdLarga',
        }
        self.datosOtroUsuario = {
            'username': 'otroUsuario',
            'password1': 'p@ssw0rdLarga',
            'password2': 'p@ssw0rdLarga',
        }    
    
    # ------
    # SIGNUP
    # ------
    def test_views_signup_status_code(self):        
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de signup retorne '200 ok'")
        self.log.info(" - [OK] Que página de signup retorne '200 ok'")


    def test_views_signup_templates_válidas(self):   
        response = self.client.get('/signup/')   
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Asignar 'template' de signup y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de signup y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de signup y cargar base.html")


    def test_views_signup_templates_no_válidas(self):   
        response = self.client.get('/signup/')      
        self.assertTemplateNotUsed(response, 'home.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'login.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'mapa_stocks.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'chart_y_datos.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")


    def test_views_signup_con_usuario(self):      
        response = self.client.post('/signup/', self.datosOtroUsuario)
        self.assertEqual(response.status_code, 200, " - [NO OK] Hacer signup con usuario de forma adecuada")
        # Necesario pasarlo a str()
        self.assertEqual(str(User.objects.get(username='otroUsuario')), 'otroUsuario', " - [NO OK] Hacer signup con usuario de forma adecuada")
        # En este punto tiene que haber 2 usuarios: el de 
        # ahora y el de setUp()
        self.assertEqual(User.objects.count(), 2, " - [NO OK] Hacer signup con usuario de forma adecuada")
        self.log.info(" - [OK] Hacer signup con usuario de forma adecuada")


    def test_views_signup_con_login_a_la_vez(self):
        self.client.post('/signup/', self.datosOtroUsuario)
        self.assertTrue('_auth_user_id' in self.client.session, " - [NO OK] A la vez que se hace signup hacer login")
        self.log.info(" - [OK] A la vez que se hace signup hacer login")


    def test_views_signup_con_plantilla_de_espera(self):
        response = self.client.post('/signup/', self.datosOtroUsuario)
        self.assertTemplateUsed(response, 'signup_ok.html', " - [NO OK] Devolver página de espera e info. al usuario tras signup adecuado")
        self.log.info(" - [OK] Devolver página de espera e info. al usuario tras signup adecuado")


    def test_views_signup_usuarios_mismo_nombre(self):
        # Para que no me meta todo el mensaje de la excepción tengo que
        # deshabilitar el log y usar 'try-except' en lugar de 'with assertRaises()'
        self.client.post('/signup/', self.datosOtroUsuario)
        logging.disable(logging.CRITICAL)
        try:
            self.client.post('/signup/', self.datosOtroUsuario)
        except TransactionManagementError:
            # Habilito el log de nuevo
            logging.disable(logging.NOTSET)
            self.log.info(" - [OK] No permite usuarios con el mismo nombre")


    def test_views_signup_usuario_sin_letras_numeros(self):
        response = self.client.post('/signup/', {'username': 'no!', 'password1': 'password', 'password2': 'password'})
        self.assertEqual(response.status_code, 200, " - [NO OK] Detectar signup incorrecto con nombre con caracteres especiales")
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Detectar signup incorrecto con nombre con caracteres especiales")
        self.assertIn('form', response.context, " - [NO OK] Detectar signup incorrecto con nombre con caracteres especiales")
        self.assertIn('error', response.context, " - [NO OK] Detectar signup incorrecto con nombre con caracteres especiales")
        self.assertEqual(response.context['error'], 
                         'Error: el nombre sólo puede tener letras y números', 
                         " - [NO OK] Detectar signup incorrecto con nombre con caracteres especiales")
        self.log.info(" - [OK] Detectar signup incorrecto con nombre con caracteres especiales")


    def test_views_signup_usuario_corto(self):
        response = self.client.post('/signup/', {'username': 'abc', 'password1': 'password', 'password2': 'password'})
        self.assertEqual(response.status_code, 200, " - [NO OK] Detectar signup incorrecto con nombre corto")
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Detectar signup incorrecto con nombre corto")
        self.assertIn('form', response.context, " - [NO OK] Detectar signup incorrecto con nombre corto")
        self.assertIn('error', response.context, " - [NO OK] Detectar signup incorrecto con nombre corto")
        self.assertEqual(response.context['error'], 'Error: nombre demasiado corto', " - [NO OK] Detectar signup incorrecto con nombre corto")
        self.log.info(" - [OK] Detectar signup incorrecto con nombre corto")

    
    def test_views_signup_sin_usuario(self):
        response = self.client.post('/signup/', {'username': '', 'password1': 'password', 'password2': 'password'})
        self.assertEqual(response.status_code, 200, " - [NO OK] Detectar signup incorrecto con nombre vacío")
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Detectar signup incorrecto con nombre vacío")
        self.assertIn('form', response.context, " - [NO OK] Detectar signup incorrecto con nombre vacío")
        self.assertIn('error', response.context, " - [NO OK] Detectar signup incorrecto con nombre vacío")
        self.assertEqual(response.context['error'], 
                         'Error: se requiere un nombre de usuario', 
                         " - [NO OK] Detectar signup incorrecto con nombre vacío")
        self.log.info(" - [OK] Detectar signup incorrecto con nombre vacío")


    def test_views_signup_password_no_valida(self):
        response = self.client.post('/signup/', {'username': 'valid_user', 'password1': 'short', 'password2': 'short'})
        self.assertEqual(response.status_code, 200, " - [NO OK] Detectar signup incorrecto con password no válida")
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Detectar signup incorrecto con password no válida")
        self.assertIn('form', response.context, " - [NO OK] Detectar signup incorrecto con password no válida")
        self.assertIn('error', response.context, " - [NO OK] Detectar signup incorrecto con password no válida")
        self.assertTrue(any(error.startswith('Error:') for error in response.context['error'].split(', ')), 
                        " - [NO OK] Detectar signup incorrecto con password no válida")
        self.log.info(" - [OK] Detectar signup incorrecto con password no válida")


    def test_views_signup_passwords_diferentes(self):
        response = self.client.post('/signup/', {'username': 'usuario', 'password1': 'contraseña1', 'password2': 'contraseña2diferente'})
        self.assertEqual(response.status_code, 200, " - [NO OK] Detectar signup incorrecto con passwords diferentes")
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Detectar signup incorrecto con passwords diferentes")
        self.assertIn('form', response.context, " - [NO OK] Detectar signup incorrecto con passwords diferentes")
        self.assertIn('error', response.context, " - [NO OK] Detectar signup incorrecto con passwords diferentes")
        self.assertEqual(response.context['error'], 
                         'Error: contraseñas no coinciden', 
                         " - [NO OK] Detectar signup incorrecto con passwords diferentes")
        self.log.info(" - [OK] Detectar signup incorrecto con passwords diferentes")


    def test_views_signup_password_habitual(self):
        response = self.client.post('/signup/', {'username': 'usuario', 'password1': 'password', 'password2': 'password'})
        self.assertEqual(response.status_code, 200, " - [NO OK] Detectar signup incorrecto con password habitual")
        self.assertTemplateUsed(response, 'signup.html', " - [NO OK] Detectar signup incorrecto con password habitual")
        self.assertIn('form', response.context, " - [NO OK] Detectar signup incorrecto con password habitual")
        self.assertIn('error', response.context, " - [NO OK] Detectar signup incorrecto con password habitual")
        self.assertEqual(response.context['error'], 
                         'Error: This password is too common.', 
                         " - [NO OK] Detectar signup incorrecto con password habitual")
        self.log.info(" - [OK] Detectar signup incorrecto con password habitual")

    # ------
    # SIGNIN
    # ------
    def test_views_signin_status_code(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de signin retorne '200 ok'")
        self.log.info(" - [OK] Que página de signin retorne '200 ok'")


    def test_views_signin_templates_válidas(self):
        response = self.client.get('/login/')
        self.assertTemplateUsed(response, 'login.html', " - [NO OK] Asignar 'template' de signin y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de signin y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de signin y cargar base.html")


    def test_views_signin_templates_no_válidas(self): 
        response = self.client.get('/login/')  
        self.assertTemplateNotUsed(response, 'home.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'signup.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'signup_ok.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'mapa_stocks.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'chart_y_datos.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")


    def test_views_signin_con_usuario(self):          
        self.client.post('/login/', self.datosUsuarioTest)
        self.assertTrue('_auth_user_id' in self.client.session, " - [NO OK] Hacer login de forma adecuada")
        self.log.info(" - [OK] Hacer login de forma adecuada")


    def test_views_signin_usuario_falso(self):
        self.client.post('/login/', self.datosUsuarioFalso)
        self.assertFalse('_auth_user_id' in self.client.session," - [NO OK] No permitir login a usuarios inexistentes")
        self.log.info(" - [OK] No permitir login a usuarios inexistentes")


    def test_views_signin_usuario_o_pass_incorrectos(self):
        response = self.client.post('/login/', self.datosUsuarioFalso)
        self.assertContains(response, 'Usuario o contraseña incorrectos')
        self.log.info(" - [OK] Informar al usuario con mensaje de usuario no correcto")


    def test_views_signin_redireccionar_tras_user_pass_incorrectos(self):
        response = self.client.post('/login/', self.datosUsuarioFalso)
        self.assertEqual(response.status_code, 200, " - [NO OK] No redireccionar si usuario o pass incorrectos")
        self.log.info(" - [OK] No redireccionar si usuario o pass incorrectos")

    def test_views_signin_actualizar_ulimos_precios_valores_usuario(self):
        model = apps.get_model('Analysis', 'ACS_MC')
        self.stock = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='ACS_MC', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='ACS, Actividades de Construcción y Servicios, S.A.', 
            currency = 'EUR', sector = 'Industrials'
        )

        self.stockComprado = StockComprado.objects.create(
            usuario=self.usuarioTest, ticker_bd='ACS_MC',
            bd='ibex35', ticker='ACS.MC',
            nombre_stock='ACS, Actividades de Construcción y Servicios, S.A.',
            fecha_compra=tz.now() - timedelta(days=365), 
            num_acciones=10,
            precio_compra=100.0, moneda='EUR',
            sector='Industrials',
            ult_cierre=100.00
        )
        self.client.post('/login/', self.datosUsuarioTest)
        self.assertTrue('_auth_user_id' in self.client.session, " - [NO OK] Hacer login de forma adecuada con valores en cartera")
        self.log.info(" - [OK] Hacer login de forma adecuada con valores en cartera")


    # -------
    # SIGNOUT
    # -------
    def test_views_signout(self):
        # Instancias de datos para cargar el 'home' de forma adecuada
        for ticker in tickers_adaptados_dj30():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='USD', sector=f'sector{ticker}'
            )
        for ticker in tickers_adaptados_ibex35():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='EUR', sector=f'sector{ticker}'
            )
        for ticker in tickers_adaptados_ftse100():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ftse100').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='GBp', sector=f'sector{ticker}'
            )
        for ticker in tickers_adaptados_dax40():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('dax40').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='EUR', sector=f'sector{ticker}'
            )       
        # Hago login válido, compruebo que está ok y
        # hago logout comprobando cookie de sesión
        self.client.post('/login/', self.datosUsuarioTest)
        self.assertTrue('_auth_user_id' in self.client.session)
        # Hacer el logout
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse('_auth_user_id' in self.client.session, " - [NO OK] Hacer logout")
        self.log.info(" - [OK] Hacer logout")

    # -----------
    # MAPA STOCKS
    # -----------
    def test_views_mapa_stocks_dj30_parametros_validos(self):
        # Simulo la creación de todos los modelos de los valores del 
        # dj30, para poder acceder al mapa de ese índice:
        for ticker in tickers_adaptados_dj30():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='USD', sector=f'sector{ticker}'
            )
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('mapa_stocks', args=['dj30']))
        self.assertEqual(response.status_code, 200, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertTemplateUsed(response, 'mapa_stocks.html', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertIn('nombre_bd', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertEqual(response.context['nombre_bd'], 'dj30', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertIn('datosFinStocks', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertIn('figura', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertIn('nombreIndice', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.assertIn('listaRSS', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")
        self.log.info(" - [OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dj30")


    def test_views_mapa_stocks_ibex35_parametros_validos(self):
        # Simulo la creación de todos los modelos de los valores del 
        # ibex35, para poder acceder al mapa de ese índice:
        for ticker in tickers_adaptados_ibex35():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='EUR', sector=f'sector{ticker}'
            )
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('mapa_stocks', args=['ibex35']))
        self.assertEqual(response.status_code, 200, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertTemplateUsed(response, 'mapa_stocks.html', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertIn('nombre_bd', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertEqual(response.context['nombre_bd'], 'ibex35', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertIn('datosFinStocks', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertIn('figura', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertIn('nombreIndice', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.assertIn('listaRSS', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
        self.log.info(" - [OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ibex35")
    

    def test_views_mapa_stocks_ftse100_parametros_validos(self):
        # Simulo la creación de todos los modelos de los valores del 
        # ftse100, para poder acceder al mapa de ese índice:
        for ticker in tickers_adaptados_ftse100():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ftse100').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='GBp', sector=f'sector{ticker}'
            )
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('mapa_stocks', args=['ftse100']))
        self.assertEqual(response.status_code, 200, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertTemplateUsed(response, 'mapa_stocks.html', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertIn('nombre_bd', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertEqual(response.context['nombre_bd'], 'ftse100', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertIn('datosFinStocks', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertIn('figura', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertIn('nombreIndice', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.assertIn('listaRSS', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")
        self.log.info(" - [OK] Respuesta adecuada de mapa_stocks con parámetros válidos en ftse100")


    def test_views_mapa_stocks_dax40_parametros_validos(self):
        # Simulo la creación de todos los modelos de los valores del 
        # ibex35, para poder acceder al mapa de ese índice:
        for ticker in tickers_adaptados_dax40():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('dax40').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='EUR', sector=f'sector{ticker}'
            )
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('mapa_stocks', args=['dax40']))
        self.assertEqual(response.status_code, 200, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertTemplateUsed(response, 'mapa_stocks.html', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertIn('nombre_bd', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertEqual(response.context['nombre_bd'], 'dax40', " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertIn('datosFinStocks', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertIn('figura', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertIn('nombreIndice', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.assertIn('listaRSS', response.context, " - [NO OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")
        self.log.info(" - [OK] Respuesta adecuada de mapa_stocks con parámetros válidos en dax40")


    def test_views_mapa_stocks_con_bd_falsa(self):
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('mapa_stocks', kwargs={'nombre_bd': 'bd_falsa'}))
        self.assertTemplateUsed(response, '404.html', " - [NO OK] Respuesta 404 de mapa_stocks con bd falsa")
        self.assertIn('Epa! Esta página no existe', response.content.decode())
        self.log.info(" - [OK] Respuesta 404 de mapa_stocks con bd falsa")


    def test_views_mapa_stocks_con_bd_vacia(self):
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('mapa_stocks', kwargs={'nombre_bd': []}))
        self.assertTemplateUsed(response, '404.html', " - [NO OK] Respuesta 404 de mapa_stocks con bd vacía")
        self.assertIn('Epa! Esta página no existe', response.content.decode())
        self.log.info(" - [OK] Respuesta 404 de mapa_stocks con bd vacía")

    
    # -------------
    # CHART Y DATOS
    # -------------    
    def test_views_chart_y_datos_datos_validos(self):
        model = apps.get_model('Analysis', 'IBM')
        # Creo 25 registros (días) del mismo modelo/stock para consultar
        # los último 22 datos que es lo que cogería en '_get_datos()'
        # dentro de chart_y_datos
        for i in range(25):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1+i, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )
        
        # Creo un stock ficticio con el mismo sector para que 
        # se prueben indirectamente los métodos _grafica_evolucion_sector() 
        # y _calcular_media_sector()
        model = apps.get_model('Analysis', 'AAPL')
        for i in range(25):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1+i, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
                currency = 'USD', sector = 'Technology'
            )
        
        # Y creo la tabla ficticia de sectores:
        Sectores.objects.create(ticker_bd='IBM', bd='dj30', ticker='IBM',
                                nombre='International Business Machines Corporation',
                                sector='Technology')  
        Sectores.objects.create(ticker_bd='AAPL', bd='dj30', ticker='AAPL',
                                nombre='Apple Inc.',
                                sector='Technology')   
        
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('chart_y_datos', kwargs={'ticker': 'IBM', 'nombre_bd': 'dj30'}))
        self.assertEqual(response.status_code, 200, " - [NO OK] Respuesta adecuada de chart_y_datos con datos válidos")
        self.assertTemplateUsed(response, 'chart_y_datos.html', " - [NO OK] Respuesta adecuada de chart_y_datos con datos válidos")
        self.log.info(" - [OK] Respuesta adecuada de chart_y_datos con datos válidos")


    def test_views_chart_y_datos_ticker_falso(self):
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('chart_y_datos', kwargs={'ticker': 'ticker_falso', 'nombre_bd': 'dj30'}))
        self.assertTemplateUsed(response, '404.html', " - [NO OK] Respuesta 404 de chart_y_datos con ticker falso")
        self.log.info(" - [OK] Respuesta 404 de chart_y_datos con ticker falso")

    
    def test_views_chart_y_datos_bd_falsa(self):
        self.client.post('/login/', self.datosUsuarioTest)
        response = self.client.get(reverse('chart_y_datos', kwargs={'ticker': 'IBM', 'nombre_bd': 'bd_falsa'}))
        self.assertTemplateUsed(response, '404.html', " - [NO OK] Respuesta 404 de chart_y_datos con bd falsa")
        self.log.info(" - [OK] Respuesta 404 de chart_y_datos con bd falsa")


    def test_views_chart_y_datos_post(self):
        # Creo 220 registros (días) de dos modelos/stocks para consultar
        # los último datos que es lo que cogería en '_generar_graficas_comparacion()'
        # dentro de chart_y_datos
        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )
        model = apps.get_model('Analysis', 'AAPL')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
                currency = 'USD', sector = 'Technology'
            )

        # Y creo la tabla ficticia de sectores:
        Sectores.objects.create(ticker_bd='IBM', bd='dj30', ticker='IBM',
                                nombre='International Business Machines Corporation',
                                sector='Technology')  
        Sectores.objects.create(ticker_bd='AAPL', bd='dj30', ticker='AAPL',
                                nombre='Apple Inc.',
                                sector='Technology')   
        
        self.client.post('/login/', self.datosUsuarioTest)
        # url = reverse('chart_y_datos', args=('IBM', 'dj30'))
        # response = self.client.post(url, {'ticker': 'AAPL'})
        # self.assertEqual(response.status_code, 200)
        url = reverse('chart_y_datos', kwargs={'ticker': 'IBM', 'nombre_bd': 'dj30'})
        response = self.client.post(url, {'ticker_a_comparar': 'ticker_falso'})
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'chart_y_datos.html', " - [NO OK] POST en _chart_y_datos con ticker falso")
        self.assertTrue('msg_error' in response.context, " - [NO OK] POST en _chart_y_datos con ticker falso")
        self.assertEqual(response.context['msg_error'], 'El ticker no existe', " - [NO OK] POST en _chart_y_datos con ticker falso")
        self.log.info(" - [OK] POST en _chart_y_datos con ticker falso")

        url = reverse('chart_y_datos', kwargs={'ticker': 'IBM', 'nombre_bd': 'dj30'})
        response = self.client.post(url, {'ticker_a_comparar': 'AAPL'})
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'chart_y_datos.html', " - [NO OK] POST en _chart_y_datos con ticker existente")
        self.assertTrue('graficas_comparacion' in response.context, " - [NO OK] POST en _chart_y_datos con ticker existente")
        self.assertTrue(isinstance(response.context["graficas_comparacion"], str), " - [NO OK] POST en _chart_y_datos con ticker existente")
        self.log.info(" - [OK] POST en _chart_y_datos con ticker existente")


    # -------------
    # CORRELACIONES
    # -------------
    def test_views_generar_correlaciones(self):
        # Creo registros de todos los stocks del ftse100
        for ticker in tickers_adaptados_ftse100():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ftse100').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='GBp', sector=f'sector{ticker}'
            )
        grafo = _generar_correlaciones('ULVR_L')
        self.assertIsNotNone(grafo, " - [NO OK] Generar grafo correlaciones no vacío")
        self.log.info(" - [OK] Generar grafo correlaciones no vacío")


    def test_views_generar_correlaciones_positivas(self):
        # Create a sample correlation matrix with a positive correlation
        matriz_correl = {
            'AAPL': {'AAPL': 1.0, 'IBM': 0.8},
            'IBM': {'AAPL': 0.8, 'ticker2': 1.0}
        }
        matriz_correl = pd.DataFrame(matriz_correl)
        tickers = ['AAPL', 'IBM']
        ticker_objetivo = 'AAPL'
        # Grafo ficticio que deberá ser una figura
        grafo = _crear_grafos(matriz_correl, tickers, ticker_objetivo)
        self.assertTrue(base64.b64decode(grafo), " - [NO OK] Generar grafo correlaciones positivas")
        self.log.info(" - [OK] Generar grafo correlaciones positivas")

    def test_views_generar_correlaciones_negativas(self):
        matriz_correl = {
            'AAPL': {'AAPL': 1.0, 'IBM': -0.8},
            'IBM': {'AAPL': -0.8, 'IBM': 1.0}
        }
        matriz_correl = pd.DataFrame(matriz_correl)
        tickers = ['AAPL', 'IBM']
        ticker_objetivo = 'AAPL'
        # Grafo ficticio que deberá ser una figura
        grafo = _crear_grafos(matriz_correl, tickers, ticker_objetivo)
        self.assertTrue(base64.b64decode(grafo), " - [NO OK] Generar grafo correlaciones negativas")
        self.log.info(" - [OK] Generar grafo correlaciones negativas")
    
    # ------------------
    # MÉTODOS AUXILIARES
    # ------------------
    def test_views_formatear_volumen(self):
        result = _formatear_volumen(1500000)
        self.assertEqual(result, '1.5M', " - [NO OK] Formateo adecuado con _formatear_volumen")
        result = _formatear_volumen(5000)
        self.assertEqual(result, '5.0K', " - [NO OK] Formateo adecuado con _formatear_volumen")
        result = _formatear_volumen(500)
        self.assertEqual(result, '500', " - [NO OK] Formateo adecuado con _formatear_volumen")
        result = _formatear_volumen(12345.67)
        self.assertEqual(result, '12.3K', " - [NO OK] Formateo adecuado con _formatear_volumen")
        result = _formatear_volumen(10000)
        self.assertEqual(result, '10.0K', " - [NO OK] Formateo adecuado con _formatear_volumen")
        self.log.info(" - [OK] Formateo adecuado con _formatear_volumen")


    def test_views_get_lista_rss(self):
        for nombre_bd in bases_datos_disponibles():
            lista_rss = _get_lista_rss(nombre_bd)
            self.assertEqual(type(lista_rss), list, " - [NO OK] Obtener listas RSS")
            # Todas las BDs deben tener 4 fuentes de RSS y se 
            # utilizan 2 noticias por fuente
            self.assertEqual(len(lista_rss), 8, " - [NO OK] Obtener listas RSS")
            for item in lista_rss:
                self.assertEqual(type(item), dict, " - [NO OK] Obtener listas RSS")
                self.assertIn('title', item, " - [NO OK] Obtener listas RSS")
                self.assertIn('href', item, " - [NO OK] Obtener listas RSS")
        self.log.info(" - [OK] Obtener listas RSS")


    def test_views_get_datos(self):
        model = apps.get_model('Analysis', 'IBM')
        # Creo 25 registros (días) del mismo modelo/stock para consultar
        # los último 22 datos que es lo que cogería en '_get_datos()'
        for i in range(25):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1+i, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )
        query_set = _get_datos('IBM', 'dj30')
        self.assertEqual(len(query_set), 22, " - [NO OK] Respuesta adecuada de _get_datos")
        for data in query_set:
            self.assertEqual(data.ticker, 'IBM', " - [NO OK] Respuesta adecuada de _get_datos")
            self.assertEqual(data.close, 105.0, " - [NO OK] Respuesta adecuada de _get_datos")
        self.log.info(" - [OK] Respuesta adecuada de _get_datos")

    
    def test_views_normalizar_dataframes_1(self):
        df_ticker = pd.DataFrame({'close': [100, 110, 120]})
        df_ticker_comparar = pd.DataFrame({'close': [90, 100, 110]})
        ratio = 120/110
        df_ticker_esperado = pd.DataFrame({'close': [100, 110, 120], 'normalizado': [100, 110, 120]})
        df_ticker_comparar_esperado = pd.DataFrame({'close': [90, 100, 110], 'normalizado': [90*ratio, 100*ratio, 110*ratio]})
        df_ticker_normalizado, df_ticker_comparar_normalizado = _normalizar_dataframes(df_ticker, df_ticker_comparar)
        self.assertTrue(df_ticker_esperado.equals(df_ticker_normalizado), " - [NO OK] Respuesta adecuada de _normalizar_dataframes para caso 1")
        self.assertTrue(df_ticker_comparar_esperado.equals(df_ticker_comparar_normalizado), " - [NO OK] Respuesta adecuada de _normalizar_dataframes para caso 1")
        self.log.info(" - [OK] Respuesta adecuada de _normalizar_dataframes para caso 1")


    def test_views_normalizar_dataframes_2(self):
        df_ticker = pd.DataFrame({'close': [90, 100, 110]})
        df_ticker_comparar = pd.DataFrame({'close': [100, 110, 120]})
        ratio = 120/110
        df_ticker_esperado = pd.DataFrame({'close': [90, 100, 110], 'normalizado': [90*ratio, 100*ratio, 110*ratio]})
        df_ticker_comparar_esperado = pd.DataFrame({'close': [100, 110, 120], 'normalizado': [100, 110, 120]})
        df_ticker_normalizado, df_ticker_comparar_normalizado = _normalizar_dataframes(df_ticker, df_ticker_comparar)
        self.assertTrue(df_ticker_esperado.equals(df_ticker_normalizado), " - [NO OK] Respuesta adecuada de _normalizar_dataframes para caso 2")
        self.assertTrue(df_ticker_comparar_esperado.equals(df_ticker_comparar_normalizado), " - [NO OK] Respuesta adecuada de _normalizar_dataframes para caso 2")
        self.log.info(" - [OK] Respuesta adecuada de _normalizar_dataframes para caso 2")


    def test_views_generar_graficas_comparacion(self):
        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )
        model = apps.get_model('Analysis', 'AAPL')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
                currency = 'USD', sector = 'Technology'
            )
        imagen_ficticia = _generar_graficas_comparacion('IBM', 'AAPL')
        # Se espera una imagen en una cadena str que viene del buffer
        self.assertTrue(isinstance(imagen_ficticia, str), " - [NO OK] Respuesta adecuada de _generar_graficas_comparacion")
        self.log.info(" - [OK] Respuesta adecuada de _generar_graficas_comparacion")