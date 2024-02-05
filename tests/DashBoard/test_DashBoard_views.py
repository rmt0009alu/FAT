from django.test import TestCase
from django.contrib.auth.models import User# Lo importo como 'tz' para no confundir con timezone de datetime
from log.logger.logger import get_logger_dashboard


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