from django.contrib import admin

# No importo modelos, sino el diccionario con los modelos
from .models import modelos_de_stocks

# Registro los modelos también de forma dinámica
for nombre_modelo, clase_modelo in modelos_de_stocks.items():
    admin.site.register(clase_modelo)