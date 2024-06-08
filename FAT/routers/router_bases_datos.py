"""
Clase para enrutar hacias las bases de datos. 
"""
from util.tickers import Tickers_BDs


# https://docs.djangoproject.com/en/5.0/topics/db/multi-db/#topics-db-multi-db-routing
class RouterBDs:
    """Clase para enrutar hacia las BDs adecuadas
    cuando se hace 'makemigrations' y 'migrate'.
    Recordar que 'migrate' migra las BDs de una en una
    y es necesario hacer 'migrate' por cada BD ('makemigrations'
    hace todas las migraciones de modelos a la vez)
    """
    def __init__(self):
        """Constructor que sirve para indicar
        los tickers.
        """
        # Los 'model' se devuelven en lowercase
        # pero en mis listas están en uppercase
        # por eso se pasan aquí a lower()
        self.tickers_dj30 = [ticker.lower() for ticker in Tickers_BDs.tickers_adaptados_dj30()]
        self.tickers_ibex35 = [ticker.lower() for ticker in Tickers_BDs.tickers_adaptados_ibex35()]
        self.tickers_ftse100 = [ticker.lower() for ticker in Tickers_BDs.tickers_adaptados_ftse100()]
        self.tickers_dax40 = [ticker.lower() for ticker in Tickers_BDs.tickers_adaptados_dax40()]


    def db_for_read(self, model, **hints):
        """Para indicar las BDs en caso de lectura.

        Parameters
        ----------
             model : django.db.models.Model
                El modelo a leer.

        Returns
        -------
            : str
                Nombre de la bd tal y como está en settings.py
        """
        if model.__name__ in self.tickers_dj30:
            return 'dj30'
        elif model.__name__ in self.tickers_ibex35:
            return 'ibex35'
        elif model.__name__ in self.tickers_ftse100:
            return 'ftse100'
        elif model.__name__ in self.tickers_dax40:
            return 'dax40'
        return 'default'


    def db_for_write(self, model, **hints):
        """Para indicar las BDs en caso de escritura.

        Parameters
        ----------
            model : django.db.models.Model
                El modelo a leer.

        Returns
        -------
            : str
                Nombre de la bd tal y como está en settings.py.
        """
        return self.db_for_read(model, **hints)


    def allow_relation(self, obj1, obj2, **hints):
        """Siempre se permite la relación.

        Returns
        -------
            : bool
                Siempre de vuelve True.
        """
        return True


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Para indicar en qué BDs se hacen las migraciones.

        Parameters
        ----------
            db : django.db
                Base de datos.

            app_label : str
                Nombre de la aplicación si se usará con migraciones 
                dependientes de aplicaciones, pero no es el caso.

            model_name : str
                Opcional. Nombre del modelo. Por defecto None.

        Returns
        -------
            : django.db
                Nombre de la BD con la que se trabaja.
        """
        if model_name in self.tickers_dj30:
            return db == 'dj30'
        elif model_name in self.tickers_ibex35:
            return db == 'ibex35'
        elif model_name in self.tickers_ftse100:
            return db == 'ftse100'
        elif model_name in self.tickers_dax40:
            return db == 'dax40'
        return db == 'default'
