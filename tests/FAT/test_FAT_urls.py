from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib import admin
from django.views.static import serve
from django.conf import settings
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('FATURLs')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS FAT URLs")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestFATUrls(SimpleTestCase):

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('FATURLs')

    def test_url_static(self):
        # No se puede usar reverse() porque no tengo url de static
        # url = reverse('static', kwargs={'path': 'Logo.png'})
        url = f'/static/Test.png'
        self.assertEquals(resolve(url).func, serve, " - [NO OK] URL static")
        self.assertEquals(resolve(url).kwargs['document_root'], settings.STATIC_ROOT, " - [NO OK] URL static")
        self.log.info(" - [OK] URL static")


    def test_url_media(self):
        url = f'/media/Test.jpg'
        self.assertEquals(resolve(url).func, serve, " - [NO OK] URL media")
        self.assertEquals(resolve(url).kwargs['document_root'], settings.MEDIA_ROOT, " - [NO OK] URL media")
        self.log.info(" - [OK] URL media")

    
    def test_url_admin(self):
        url = reverse('admin:index')
        self.assertEquals(resolve(url).func.__name__, admin.site.index.__name__, " - [NO OK] URL admin")
        self.log.info(" - [OK] URL admin")

    # Las URLs de las apps con 'include' se testean en sus 
    # correspondientes archivos de test
