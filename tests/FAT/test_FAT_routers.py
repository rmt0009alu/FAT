from django.test import TestCase
from FAT.routers.router_bases_datos import RouterBDs
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
            
            log = get_logger_configurado('FATRouters')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS FAT ROUTERS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

class TestFATRouters(TestCase):

    # databases = '__all__'

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('FATRouters')

        self.router = RouterBDs()
        
        self.model_1 = apps.get_model('Analysis', 'AAPL')
        self.db_1 = 'dj30'
        self.model_2 = apps.get_model('Analysis', 'ACS_MC')
        self.db_2 = 'ibex35'
        self.model_3 = apps.get_model('Analysis', 'RIO_L')
        self.db_3 = 'ftse100'


    def test_db_for_read(self):
        # En los routers el nombre de los modelos llega en lowercase, ojo
        self.model_1.__name__ = self.model_1.__name__.lower()
        db = self.router.db_for_read(self.model_1)
        self.assertEqual(db, self.db_1, " - [NO OK] Enrutar a BD adecuada")
        
        self.model_2.__name__ = self.model_2.__name__.lower()
        db = self.router.db_for_read(self.model_2)
        self.assertEqual(db, self.db_2, " - [NO OK] Enrutar a BD adecuada")
        self.log.info(" - [OK] Enrutar a BD adecuada")

        self.model_3.__name__ = self.model_3.__name__.lower()
        db = self.router.db_for_read(self.model_3)
        self.assertEqual(db, self.db_3, " - [NO OK] Enrutar a BD adecuada")
        self.log.info(" - [OK] Enrutar a BD adecuada")