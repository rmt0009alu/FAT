from django.test import TestCase
from django.contrib.auth.models import User
# Para comprobar exception que lanza con usuarios repetidos
from django.db.transaction import TransactionManagementError
from log.logger.logger import get_logger_configurado
import logging

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
    
    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('AnalysisViews')
        self.usuarioTest = User.objects.create_user(username='usuarioTest', password='p@ssw0rd')   
        self.datosUsuarioTest = {
            'username': 'usuarioTest',
            'password': 'p@ssw0rd',
        }
        self.datosUsuarioFalso = {
            'username': 'usuarioFalso',
            'password': 'p@ssw0rd',
        }
        self.datosOtroUsuario = {
            'username': 'otroUsuario',
            'password1': 'p@ssw0rd',
            'password2': 'p@ssw0rd',
        }    


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


    def test_views_login_tras_signup(self):
        self.client.post('/signup/', self.datosOtroUsuario)
        self.assertTrue('_auth_user_id' in self.client.session, " - [NO OK] A la vez que se hace signup hacer login")
        self.log.info(" - [OK] A la vez que se hace signup hacer login")


    def test_views_espera_tras_sinup(self):
        response = self.client.post('/signup/', self.datosOtroUsuario)
        self.assertTemplateUsed(response, 'signup_ok.html', " - [NO OK] Devolver página de espera e info. al usuario tras signup adecuado")
        self.log.info(" - [OK] Devolver página de espera e info. al usuario tras signup adecuado")


    def test_views_evitar_usuarios_mismo_nombre(self):
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


    def test_views_usuario_o_pass_incorrectos(self):
        response = self.client.post('/login/', self.datosUsuarioFalso)
        self.assertContains(response, 'Usuario o contraseña incorrectos')
        self.log.info(" - [OK] Informar al usuario con mensaje de usuario no correcto")


    def test_views_redireccionar_tras_user_pass_incorrectos(self):
        response = self.client.post('/login/', self.datosUsuarioFalso)
        self.assertEqual(response.status_code, 200, " - [NO OK] No redireccionar si usuario o pass incorrectos")
        self.log.info(" - [OK] No redireccionar si usuario o pass incorrectos")


    def test_views_signout(self):       
        # Hago login válido, compruebo que está ok y
        # hago logout comprobando cookie de sesión
        self.client.post('/login/', self.datosUsuarioTest)
        self.assertTrue('_auth_user_id' in self.client.session)
        self.client.logout()
        self.assertFalse('_auth_user_id' in self.client.session, " - [NO OK] Hacer logout")
        self.log.info(" - [OK] Hacer logout")