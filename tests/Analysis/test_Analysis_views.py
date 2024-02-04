from django.test import TestCase
from django.contrib.auth.models import User
# Para comprobar exception que lanza con usuarios repetidos
from django.db.transaction import TransactionManagementError
from log.logger.logger import get_logger_analysis
import os
import sys

# Para que se detecten bien los paths desde los tests
# https://stackoverflow.com/questions/35636736/python-importing-modules-for-testing
# PROJECT_PATH = os.getcwd()
# sys.path.append(PROJECT_PATH)

# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_analysis('AnalysisViews')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS ANALYSIS VIEWS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

class TestAnalysisViews(TestCase):

    def setUp(self):
        Singleton()
        self.log = get_logger_analysis('AnalysisViews')
        self.usuarioTest = User.objects.create_user(username='usuario', password='p@ssw0rd')       


    def test_views_signup_status_code(self):        
        # Posibles códigos:
        # 200 OK, 201 Created, 204 No Content, 302 Redirect, 400 Bad Request, 401 Unauthorized, 
        # 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 500 Internal Server Error
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
        datos = {
            'username': 'otroUsuario',
            'password1': 'p@ssw0rd',
            'password2': 'p@ssw0rd',
        }
        response = self.client.post('/signup/', datos)
        self.assertEqual(response.status_code, 200, " - [NO OK] Hacer signup con usuario de forma adecuada")
        # Necesario pasarlo a str()
        self.assertEqual(str(User.objects.get(username='otroUsuario')), 'otroUsuario', " - [NO OK] Hacer signup con usuario de forma adecuada")
        # En este punto tiene que haber 2 usuarios: el de 
        # ahora y el de setUp()
        self.assertEqual(User.objects.count(), 2, " - [NO OK] Hacer signup con usuario de forma adecuada")
        self.log.info(" - [OK] Hacer signup con usuario de forma adecuada")



    #     self.assertTrue('_auth_user_id' in self.client.session, " - [NO OK] A la vez que se hace signup hacer login")
    #     self.logger_Usuarios.info(" - [OK] A la vez que se hace signup hacer login")

    #     self.assertTemplateUsed(response, 'signup_ok.html', " - [NO OK] Devolver página de espera e info. al usuario tras signup adecuado")
    #     self.logger_Usuarios.info(" - [OK] Devolver página de espera e info. al usuario tras signup adecuado")

    #     # No puedo usar assertRaises(), así que hago un try-except
    #     # self.assertRaises(TransactionManagementError, self.client.post('/signup/', datos))
    #     # Para que no me meta todo el mensaje de la excepción tengo que
    #     # deshabilitar el log:
    #     logging.disable(logging.CRITICAL)
    #     try:
    #         self.client.post('/signup/', datos)
    #     except TransactionManagementError:
    #         # Habilito el log de nuevo
    #         logging.disable(logging.NOTSET)
    #         self.logger_Usuarios.info(" - [OK] No permite usuarios con el mismo nombre")

        

    # def test_03_signin(self):
    #     self.logger_Usuarios.info("")
    #     self.logger_Usuarios.info("----------------------------------")
    #     self.logger_Usuarios.info("TEST SIGNIN")
    #     self.logger_Usuarios.info("----------------------------------")

    #     # Posibles códigos:
    #     # 200 OK, 201 Created, 204 No Content, 302 Redirect, 400 Bad Request, 401 Unauthorized, 
    #     # 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 500 Internal Server Error

    #     response = self.client.get('/login/')
    #     self.assertEqual(response.status_code, 200, " - [NO OK] Que página de singin retorne '200 ok'")
    #     self.logger_Usuarios.info(" - [OK] Que página de singin retorne '200 ok'")

    #     self.assertTemplateUsed(response, 'login.html', " - [NO OK] Asignar 'template' de signin y cargar base.html")
    #     self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de signin y cargar base.html")
    #     self.logger_Usuarios.info(" - [OK] Asignar 'template' de signin y cargar base.html")

    #     self.assertTemplateNotUsed(response, 'home.html', " - [NO OK] No utilizar otros 'templates' por error")
    #     self.assertTemplateNotUsed(response, 'signup.html', " - [NO OK] No utilizar otros 'templates' por error")
    #     self.assertTemplateNotUsed(response, 'signup_ok.html', " - [NO OK] No utilizar otros 'templates' por error")
    #     self.assertTemplateNotUsed(response, 'mapa_stocks.html', " - [NO OK] No utilizar otros 'templates' por error")
    #     self.assertTemplateNotUsed(response, 'chart_y_datos.html', " - [NO OK] No utilizar otros 'templates' por error")
    #     self.logger_Usuarios.info(" - [OK] No utilizar otros 'templates' por error")

    #     datos = {
    #         'username': 'usuario',
    #         'password': 'p@ssw0rd',
    #     }
    #     response = self.client.post('/login/', datos)
    #     self.assertTrue('_auth_user_id' in self.client.session, " - [NO OK] Hacer login de forma adecuada")
    #     self.logger_Usuarios.info(" - [OK] Hacer login de forma adecuada")

    #     # Fuerzo logout para hacer otros tests
    #     self.client.post('/logout/')
    #     datos = {
    #         'username': 'usuario_erróneo',
    #         'password': 'p@ssw0rd',
    #     }
    #     response = self.client.post('/login/', datos)
    #     self.assertFalse('_auth_user_id' in self.client.session," - [NO OK] No permitir login a usuarios inexistentes")
    #     self.logger_Usuarios.info(" - [OK] No permitir login a usuarios inexistentes")

    #     self.assertContains(response, 'Usuario o contraseña incorrectos')
    #     self.logger_Usuarios.info(" - [OK] Informar al usuario con mensaje de usuario no correcto")

    #     self.assertEqual(response.status_code, 200, " - [NO OK] No redireccionar si usuario o pass incorrectos")
    #     self.logger_Usuarios.info(" - [OK] No redireccionar si usuario o pass incorrectos")


    # def test_04_signout(self):
    #     self.logger_Usuarios.info("")
    #     self.logger_Usuarios.info("----------------------------------")
    #     self.logger_Usuarios.info("TEST SIGNOUT")
    #     self.logger_Usuarios.info("----------------------------------")
        
    #     # Hago login válido, compruebo que está ok y
    #     # hago logout comprobando cookie de sesión
    #     self.client.login(username='usuario', password='p@ssw0rd')
    #     self.assertTrue('_auth_user_id' in self.client.session)
    #     self.client.logout()
    #     self.assertFalse('_auth_user_id' in self.client.session, " - [NO OK] Hacer logout")
    #     self.logger_Usuarios.info(" - [OK] Hacer logout")