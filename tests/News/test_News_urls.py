from django.test import SimpleTestCase
from django.urls import reverse, resolve
from News.views import home
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('NewsURLs')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS NEWS URLs")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestNewsUrls(SimpleTestCase):
    
    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('NewsURLs')

    def test_url_home(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, home, " - [NO OK] URL home")
        self.log.info(" - [OK] URL home")
