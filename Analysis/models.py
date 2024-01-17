from django.db import models
from util.tickers.Tickers_BDs import tickersAdaptadosDJ30, tickersAdaptadosIBEX35


class StockBase(models.Model):
    """Clase padre de la que heredan todas las tablas
    de los stocks. Da igual la BD en la que estén porque
    luego usaré un acceso dirigido a cada BD. Se utiliza
    herencia y creación de clases dinámicas porque, si no,
    tendría que repetir mucho código innecesario con cada
    ticker/stock que quiera utilizar. 

    Args:
        models.Model (django.db.models.base.Model'): clase base 
            para los modelos de Django.
    """
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  
    open = models.FloatField(db_column='Open', blank=True, null=True)  
    high = models.FloatField(db_column='High', blank=True, null=True)  
    low = models.FloatField(db_column='Low', blank=True, null=True)  
    close = models.FloatField(db_column='Close', blank=True, null=True)  
    volume = models.IntegerField(db_column='Volume', blank=True, null=True)  
    dividends = models.FloatField(db_column='Dividends', blank=True, null=True)  
    stock_splits = models.FloatField(db_column='Stock Splits', blank=True, null=True)  
    ticker = models.TextField(db_column='Ticker', blank=True, null=True)  
    previous_close = models.FloatField(db_column='Previous_Close', blank=True, null=True)  
    percent_variance = models.FloatField(db_column='Percent_Variance', blank=True, null=True)  
    mm20 = models.FloatField(db_column='MM20', blank=True, null=True)  
    mm50 = models.FloatField(db_column='MM50', blank=True, null=True)  
    mm200 = models.FloatField(db_column='MM200', blank=True, null=True)  
    name = models.TextField(db_column='Name', blank=True, null=True)
    objects = models.Manager() 


    class Meta:
        """Clase que sirve para indicar atributos 
        adicionales. 
        """
        # Para que la tabla/modelo no sea gestionada por 
        # Django. Así, en la dq.sqlite3 por defecto no se
        # crean tablas innecesarias de stocks
        managed = False

        # Para que no se cree una tabla 'BaseStock'
        # adicional en la BD, sino que sepa que es
        # la clase padre para el resto de tablas
        abstract = True
    

    def __str__(self):
        """Método magic, para representación en strings. 

        Returns:
            (str): cadena descriptiva
        """
        return f"{self.ticker} - {self.name} . Fecha: {self.date}. Cierre: {self.close}"



# Listas con los nombres de los modelos del DJ30 y el IBEX35
# para crearlos de forma dinámica
tickers_dj30 = tickersAdaptadosDJ30()
tickers_ibex35 = tickersAdaptadosIBEX35()

# Diccionario para los modelos creados de forma dinámica
modelos_de_stocks = {}

# Crear los modelos de forma dinámica
for ticker in tickers_dj30 + tickers_ibex35:
    clase_dinamica = type(
        ticker, 
        (StockBase,), 
        {
            '__module__': __name__,
            'Meta': type('Meta', (), {'db_table': ticker}),
        }
    )
    modelos_de_stocks[ticker] = clase_dinamica