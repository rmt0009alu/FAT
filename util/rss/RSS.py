
def rss_dj30():
    """Para obtener los enlaces de RSS de noticias
    relacionadas con el Dj30 y/o noticias de otros
    mercados.

    Returns:
        (list): lista con los RSS
    """
    rss = ["https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en",    # Bloomberg
           "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",                                         # New York Times
           "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",                                                     # Wall Street Journal
           "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069"]               # CNBC
    
    return rss


def rss_ibex35():
    """Para obtener los enlaces de RSS de noticias
    relacionadas con el Ibex35 y/o noticias de otros
    mercados.

    Returns:
        (list): lista con los RSS
    """
    rss = ["https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada",     # El País
           "https://www.estrategiasdeinversion.com/rss/rssnoticias.xml",                            # Estrategias de inversión
           "https://www.bolsasymercados.es/bme-exchange/en/RSS/Indices",                            # BME
           "https://e00-expansion.uecdn.es/rss/mercados.xml"]                                       # Expansión
    
    return rss


def rss_ftse100():
    """Para obtener los enlaces de RSS de noticias
    relacionadas con el FTSE100 y/o noticias de otros
    mercados.

    Returns:
        (list): lista con los RSS
    """
    rss = ["https://uk.finance.yahoo.com/rss/topstories",                       # Yahoo finance UK
           "https://www.theguardian.com/uk/business/rss",                       # The Guardian Business
           "https://www.ft.com/rss/home/uk",                                    # Financial Times UK
           "https://www.business-live.co.uk/?service=rss"]                      # Business-live
    
    return rss


def rss_dax40():
    """Para obtener los enlaces de RSS de noticias
    relacionadas con el DAX40 y/o noticias de otros
    mercados.

    Returns:
        (list): lista con los RSS
    """
    rss = [#"https://www.finanzen.net/rss/analysen",                             # finanzen.net
           "https://uk.finance.yahoo.com/rss/topstories",                       # Yahoo finance UK
           "https://www.theguardian.com/uk/business/rss",                       # The Guardian Business
           "https://www.ft.com/rss/home/uk",                                    # Financial Times UK
           "https://www.business-live.co.uk/?service=rss"]                      # Business-live
    
    return rss
