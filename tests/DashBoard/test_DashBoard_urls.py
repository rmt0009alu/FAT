from django.test import SimpleTestCase
from django.urls import reverse, resolve
from DashBoard.views import dashboard, nueva_compra, eliminar_compras, nuevo_seguimiento, eliminar_seguimiento
from log.logger.logger import get_logger_configurado

# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('DashBoardURLs')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS DASHBOARD URLS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance


class TestDashBoardUrls(SimpleTestCase):

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('DashBoardURLs')

        
    def test_url_dashboard(self):
        url = reverse('dashboard')
        self.assertEquals(resolve(url).func, dashboard, " - [NO OK] URL de 'dashboard'")
        self.log.info(" - [OK] URL de 'dashboard'")


    def test_url_nueva_compra(self):
        url = reverse('nueva_compra')
        self.assertEquals(resolve(url).func, nueva_compra, " - [NO OK] URL de 'nueva_compra'")
        self.log.info(" - [OK] URL de 'nueva_compra'")


    def test_url_eliminar_compras(self):
        url = reverse('eliminar_compras')
        self.assertEquals(resolve(url).func, eliminar_compras, " - [NO OK] URL de 'eliminar_compras'")
        self.log.info(" - [OK] URL de 'eliminar_compras'")


    def test_url_nuevo_seguimiento(self):
        url = reverse('nuevo_seguimiento')
        self.assertEquals(resolve(url).func, nuevo_seguimiento, " - [NO OK] URL de 'nuevo_seguimiento'")
        self.log.info(" - [OK] URL de 'nuevo_seguimiento'")


    def test_url_eliminar_seguimiento(self):
        url = reverse('eliminar_seguimiento')
        self.assertEquals(resolve(url).func, eliminar_seguimiento, " - [NO OK] URL de 'eliminar_seguimiento'")
        self.log.info(" - [OK] URL de 'eliminar_seguimiento'")