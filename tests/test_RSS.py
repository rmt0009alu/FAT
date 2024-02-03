from django.test import SimpleTestCase
from util.rss.RSS import RSSDj30, RSSIbex35


class TestRSS(SimpleTestCase):
    
    def test_rss_ibex35(self):
        RSS = ["https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada",    
                "https://www.estrategiasdeinversion.com/rss/rssnoticias.xml",                           
                "https://www.bolsasymercados.es/bme-exchange/en/RSS/Indices",                         
                "https://e00-expansion.uecdn.es/rss/mercados.xml"]                                      
        self.assertEquals(RSS, RSSIbex35())
        

    def test_rss_dj30(self):
        RSS = ["https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en",   
                "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",                                         
                "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",                                                     
                "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069"]                                      
        self.assertEquals(RSS, RSSDj30())
