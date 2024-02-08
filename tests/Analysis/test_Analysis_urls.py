from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Analysis.views import mapa_stocks, signup, signout, signin, chart_y_datos
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('AnalysisURLs')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS ANALYSIS URLs")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestAnalysisUrls(SimpleTestCase):

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('AnalysisURLs')


    def test_url_mapa_stocks(self):
        url = reverse('mapa_stocks', args=['dj30'])
        self.assertEquals(resolve(url).func, mapa_stocks, " - [NO OK] URL mapa_stocks")
        self.log.info(" - [OK] URL mapa_stocks")


    def test_url_signup(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, signup, " - [NO OK] URL signup")
        self.log.info(" - [OK] URL signup")


    def test_url_logout(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, signout, " - [NO OK] URL logout")
        self.log.info(" - [OK] URL logout")


    def test_url_login(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, signin, " - [NO OK] URL login")
        self.log.info(" - [OK] URL login")


    def test_url_chart_y_datos(self):
        url = reverse('chart_y_datos', args=['SAN_MC', 'ibex35'])
        self.assertEquals(resolve(url).func, chart_y_datos, " - [NO OK] URL chart_y_datos")
        self.log.info(" - [OK] URL chart_y_datos")
