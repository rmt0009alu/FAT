from django.shortcuts import render
from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from .forms import CreateNewTaskForm, CreateNewProjectForm
from django.db import connection
# from .models import StockData
# from django.apps import apps


def hello(request):
    """Función que retorna un mensaje al cliente/navegador
    y devuelve una respuesta HTTP al cleinte (para ello, se 
    importa HTTPresponse)

    Args:
        request (request): Varaible pasada por Django en la
                          que se recibe info. que el cliente
                          esté enviando cuando visite esta función.
    """
    # Este el mensaje que se envía al navegador cuando se
    # ejecute esta función
    return HttpResponse("<h1>BIENVENIDO A FAT: Financial Analysis Tool</h1>")


def stock_data(request, ticker):
    """Método que no usa los modelos/clases sino que accede 
    directamente a la BD, busca el nombre de la tabla con
    el ticker pasado a través de la barra de direcciones
    y recoge toda su info.

    Args:
        request (_type_): _description_
        ticker (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Dynamically construct the table name based on the ticker
    table_name = f"{ticker.lower()}"
    
    # Use raw SQL to query the specific table
    query = f"SELECT * FROM {table_name};"
    with connection.cursor() as cursor:
        cursor.execute(query)
        # Fetch the results
        results = cursor.fetchall()
    
    # Convert the results to a list of dictionaries
    columns = [col[0] for col in cursor.description]
    ticker_data = [dict(zip(columns, row)) for row in results]

    context = {
        'ticker_data': ticker_data
    }

    return render(request, 'stock_data.html', context)
