"""
Módulo para la aplicación de Lab.
"""
from django.apps import AppConfig


class LabConfig(AppConfig):
    """Configuración de la app de Lab.

    Parameters
    ----------
        AppConfig : django.apps
            Configurador de aplicaciones en Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Lab'
