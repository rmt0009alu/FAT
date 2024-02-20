"""
Modelos para usar con la app Analysis.
"""
from django.db import models
from util.tickers.Tickers_BDs import tickers_adaptados_disponibles


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
    sector = models.TextField(db_column='Sector', blank=True, null=True)
    currency = models.TextField(db_column='Currency', blank=True, null=True)
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
            (str): cadena descriptiva.
        """
        return f"{self.ticker} - {self.name} . Fecha: {self.date}. Cierre: {self.close}"


###########################################################################
# Diccionario para los modelos creados de forma dinámica
modelos_de_stocks = {}

# Crear los modelos de forma dinámica
for ticker in tickers_adaptados_disponibles():
    clase_dinamica = type(
        ticker,
        (StockBase,),
        {
            '__module__': __name__,
            'Meta': type('Meta', (), {'db_table': ticker}),
        }
    )
    modelos_de_stocks[ticker] = clase_dinamica
###########################################################################

class Sectores(models.Model):
    """Clase para crear una tabla que almacene todos los tickers
    juntos con sus correspondientes sectores.

    Args:
        models.Model (django.db.models.base.Model'): clase base
            para los modelos de Django.
    """
    id = models.AutoField(primary_key=True)
    ticker_bd = models.TextField(db_column='Ticker_bd')
    bd = models.TextField(db_column='BaseDatos')
    # Ticker con notación de punto 'ALGO.XX'
    ticker = models.TextField(db_column='Ticker')
    nombre = models.TextField(db_column='Nombre', blank=True, null=True)
    sector = models.TextField(db_column='Sector')
    objects = models.Manager()

    class Meta:
        """Clase que sirve para indicar atributos
        adicionales.
        """
        # Para que la tabla/modelo sea gestionada por
        # Django. Esta tabla se crea en dq.sqlite3
        # para que sea común a todas las demás
        managed = True

    def __str__(self) -> str:
        """Método magic, para representación en strings.

        Returns:
            (str): cadena descriptiva.
        """
        return f"{self.id} - {self.nombre} - {self.sector}"


class CambioMoneda(models.Model):
    """Clase para crear una tabla que almacene todos los tickers
    forex con info. sobre el cambio de moneda.

    Args:
        models.Model (django.db.models.base.Model'): clase base
            para los modelos de Django.
    """
    id = models.AutoField(primary_key=True)
    ticker_forex = models.TextField(db_column='Ticker_forex')
    date = models.DateField(db_column='Date')
    ultimo_cierre = models.FloatField(db_column='Ultimo_cierre')
    objects = models.Manager()

    class Meta:
        """Clase que sirve para indicar atributos
        adicionales.
        """
        # Para que la tabla/modelo sea gestionada por
        # Django. Esta tabla se crea en dq.sqlite3
        # para que sea común a todas las demás
        managed = True

    def __str__(self) -> str:
        """Método magic, para representación en strings.

        Returns:
            (str): cadena descriptiva.
        """
        return f"{self.id} - {self.ticker_forex}"
