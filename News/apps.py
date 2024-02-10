"""
Módulo para la aplicación de News.
"""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuración de la app de News.

    Args:
        AppConfig (django.apps): configurador de aplicaciones
            en Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'News'
