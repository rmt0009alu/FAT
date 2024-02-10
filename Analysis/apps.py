"""
Módulo para la aplicación de Analysis.
"""
from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    """Configuración de la app de Analysis.

    Args:
        AppConfig (django.apps): configurador de aplicaciones
            en Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Analysis'
