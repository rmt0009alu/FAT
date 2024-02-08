from django.test import TestCase
from django.conf import settings
from log.logger.logger import get_logger_configurado
# Para usar los modelos creados de forma dinámica
from django.apps import apps


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('FATSettings')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS FAT SETTINGS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

class TestFATSettings(TestCase):

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('FATSettings')


    def test_settings_debug_de_static(self):
        self.assertIsNot(True, settings.STATICFILES_DIRS, " - [NO OK] Devolver desde FAT.settings el valor adecuado de static")
        self.assertTrue(settings.STATIC_ROOT, " - [NO OK] Devolver desde FAT.settings el valor adecuado de static")

        settings.DEBUG = True
        self.assertEqual(settings.STATICFILES_DIRS, [], " - [NO OK] Devolver desde FAT.settings el valor adecuado de static")
        self.assertIsNot(True, settings.STATIC_ROOT, " - [NO OK] Devolver desde FAT.settings el valor adecuado de static")
            
        self.log.info(" - [OK] Devolver desde FAT.settings el valor adecuado de static")