import os
import sys
import django
sys.path.insert(0, os.path.abspath('../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAT.settings.py'
django.setup()

import sphinxcontrib_django
import sphinx_rtd_theme

# -- Configurar el tema de Read The Docs ----------------------------------
# -------------------------------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Configure the Sphinx RTD theme
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#262b2e',
    'style_nav_header_bottom_border': '1px solid #262b2e',
    'style_highlight_palette': [
        '#00495e', '#0086b3', '#c0504d', '#f79646', '#e0ab18', '#6d9e41', 
        '#d0b48e', '#fdfdc5'
    ],
    'style_copyright_background': '#2d2f33'
}


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FAT: Financial Analysis Tool'
copyright = '2024, Rodrigo Merino Tovar'
author = 'Rodrigo Merino Tovar'
release = 'v3.0.0.'


# Configure the Sphinxcontrib Django extension
# sphinxcontrib_django.extension(
#     settings_module='FAT.settings',
#     apps=['FAT'],
#     ignore_patterns=['migrations', 'templates']
# )

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
    'sphinxcontrib_django',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

# Configure the Sphinx autodoc extension
autodoc_mock_imports = ['django']

# Configure the Sphinx coverage extension
coverage_ignore_functions = ['runserver', 'runtest', 'test']