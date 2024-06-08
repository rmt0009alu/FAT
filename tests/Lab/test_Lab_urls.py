from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Lab.views import lab, arima_auto, arima_rejilla, arima_manual, lstm, cruce_medias, estrategia_machine_learning
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('LabURLs')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS LAB URLs")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestLabUrls(SimpleTestCase):
    
    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('LabURLs')


    def test_url_lab(self):
        url = reverse('lab')
        self.assertEquals(resolve(url).func, lab, " - [NO OK] URL lab")
        self.log.info(" - [OK] URL lab")


    def test_url_arima_auto(self):
        url = reverse('arima_auto')
        self.assertEquals(resolve(url).func, arima_auto, " - [NO OK] URL arima_auto")
        self.log.info(" - [OK] URL arima_auto")
    

    def test_url_arima_rejila(self):
        url = reverse('arima_rejilla')
        self.assertEquals(resolve(url).func, arima_rejilla, " - [NO OK] URL arima_rejilla")
        self.log.info(" - [OK] URL arima_rejilla")


    def test_url_maual(self):
        url = reverse('arima_manual')
        self.assertEquals(resolve(url).func, arima_manual, " - [NO OK] URL arima_manual")
        self.log.info(" - [OK] URL arima_manual")

    
    def test_url_lstm(self):
        url = reverse('lstm')
        self.assertEquals(resolve(url).func, lstm, " - [NO OK] URL lstm")
        self.log.info(" - [OK] URL lstm")

    
    def test_url_cruce_medias(self):
        url = reverse('cruce_medias')
        self.assertEquals(resolve(url).func, cruce_medias, " - [NO OK] URL cruce_medias")
        self.log.info(" - [OK] URL cruce_medias")


    def test_url_estrategia_ML(self):
        url = reverse('estrategia_ML')
        self.assertEquals(resolve(url).func, estrategia_machine_learning, " - [NO OK] URL estrategia_ML")
        self.log.info(" - [OK] URL estrategia_ML")
