from django.shortcuts import render
from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from .forms import CreateNewTaskForm, CreateNewProjectForm
from django.db import connection, connections
# from .models import StockData
# from django.apps import apps


def hello(request):
    """Función que retorna un mensaje al cliente/navegador
    y devuelve una respuesta HTTP al cleinte (para ello, se 
    importa HTTPresponse)

    Args:
        request (request): Variable pasada por Django en la
                          que se recibe info. que el cliente
                          esté enviando cuando visite esta función.
    
    Returns:
        HttpResponse: 
    """
    # Este el mensaje que se envía al navegador cuando se
    # ejecute esta función
    return HttpResponse("<h1>BIENVENIDO A FAT: Financial Analysis Tool</h1>")


def stock_data(request, ticker, nombre_bd):
    """Método que no usa los modelos/clases sino que accede 
    directamente a la BD, busca el nombre de la tabla con
    el ticker pasado a través de la barra de direcciones
    y recoge toda su info.

    Args:
        request (request): Variable pasada por Django en la
                          que se recibe info. que el cliente
                          esté enviando cuando visite esta función.
        ticker (str): nombre del ticker del que quiero obtener la info.
        nombre_bd (str): nombre de la BD a la que me quiero conectar.

    Returns:
        render: 
    """
    # Para llamar a la tabla que se pase como ticker
    table_name = f"{ticker.lower()}"
    
    # Sentencia SQL para acceder a la tabla deseada
    query = f"SELECT * FROM {table_name};"

    # Necesito indicar la BD a la que conectarme porque no estoy
    # usando la que viene por defecto (además de que las BD las he
    # puesto en una ruta distinta a la de por defecto, porque 
    # están es "./databases")
    with connections[nombre_bd].cursor() as cursor:
        cursor.execute(query)
        # Fetch
        results = cursor.fetchall()
    
    # Convertir los resultados a una lista de diccionarios
    columns = [col[0] for col in cursor.description]
    ticker_data = [dict(zip(columns, row)) for row in results]

    # Contexto para el render
    context = {
        'ticker_data': ticker_data,
        'nombre_ticker': ticker,
    }

    return render(request, 'stock_data.html', context)

