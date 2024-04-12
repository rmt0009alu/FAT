"""
Archivo de configuración de Sphinx.
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys
import django
import sphinx_rtd_theme
sys.path.insert(0, os.path.abspath('../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAT.settings'
django.setup()


# -- Información del proyecto -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'FAT: Financial Analysis Tool'
copyright = '2024, Rodrigo Merino Tovar'
author = 'Rodrigo Merino Tovar'
release = 'v3.0.0'

# -- Configuración general --------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

extensions = [
    'sphinx.ext.autodoc',
    # Para métodos privados typehints
    'sphinx.ext.autodoc.typehints',
    # Para autodocumentar, pero no me convence
    # 'sphinx.ext.autosummary',
    # 'sphinx.ext.doctest',
    # 'sphinx.ext.todo',
    # 'sphinx.ext.coverage',
    # 'sphinx.ext.imgmath',
    'sphinxcontrib_django',
]

# Para que los métodos aparezcan en el orden del source
autodoc_member_order = 'bysource'

# Extensión de autodoc de Sphinx
# autodoc_mock_imports = ['django']

# Para métodos privados
autodoc_typehints = 'description'
autodoc_class_signature = 'separated'

# Extensión de coverage de Sphinx
# coverage_ignore_functions = ['runserver', 'runtest', 'test']


# -- Configurar el tema de Read The Docs ------------------------------------------
# ---------------------------------------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']

# Configurar opciones del tema
html_theme_options = {
    'canonical_url': '',
    # 'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#262b2e',
    # 'style_nav_header_bottom_border': '1px solid #262b2e',
}

