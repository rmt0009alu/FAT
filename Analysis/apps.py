"""
Módulo para la aplicación de Analysis.
"""
from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    """Configuración de la app de Analysis.

    Parameters
    ----------
        AppConfig : django.apps
            Configurador de aplicaciones en Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Analysis'
