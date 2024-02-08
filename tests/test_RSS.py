from django.test import SimpleTestCase
from util.rss.RSS import RSSDj30, RSSIbex35
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('RSS')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS RSS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

class TestRSS(SimpleTestCase):
    
    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('RSS')

    def test_rss_ibex35(self):
        RSS = ["https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada",    
                "https://www.estrategiasdeinversion.com/rss/rssnoticias.xml",                           
                "https://www.bolsasymercados.es/bme-exchange/en/RSS/Indices",                         
                "https://e00-expansion.uecdn.es/rss/mercados.xml"]                                      
        self.assertEquals(RSS, RSSIbex35(), " - [NO OK] Obtener enlaces RSS de ibex35")
        self.log.info(" - [OK] Obtener enlaces RSS de ibex35")
        

    def test_rss_dj30(self):
        RSS = ["https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en",   
                "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",                                         
                "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",                                                     
                "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069"]                                      
        self.assertEquals(RSS, RSSDj30(), " - [NO OK] Obtener enlaces RSS de dj30")
        self.log.info(" - [OK] Obtener enlaces RSS de dj30")