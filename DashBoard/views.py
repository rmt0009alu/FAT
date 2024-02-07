from django.shortcuts import render, redirect
# Para proteger rutas. Las funciones que tienen este decorador 
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required

from .models import StockComprado, StockSeguimiento
from .forms import StockCompradoForm, StockSeguimientoForm
from util.tickers import Tickers_BDs

# Para usar los modelos creados de forma dinámica
from django.apps import apps

# Para procesar las fechas recibidas con el DatePicker
from datetime import datetime, date
from django.utils import timezone

# from Analysis.models import StockBase
# from django.db.models import Q
from Analysis.models import Sectores


from django.core.exceptions import ValidationError


@login_required
def dashboard(request):

    # Obtener el nombre del usuario
    usuario = request.user.username

    # Obtener compras del usuario actual
    comprasUsuario = StockComprado.objects.filter(usuario=request.user)
    seguimientoUsuario = StockSeguimiento.objects.filter(usuario=request.user)

    if comprasUsuario.exists() and seguimientoUsuario.exists():
        # Obtener la evolución de la cartera
        evolCartera, evolTotal = _evolucion_cartera(comprasUsuario)
        stocksEnSeg = _stocks_en_seguimiento(seguimientoUsuario)
        context = {
            "usuario": usuario,
            "comprasUsuario": comprasUsuario,
            "evolCartera": evolCartera,
            "evolTotal": evolTotal,
            "seguimientoUsuario": seguimientoUsuario,
            "stocksEnSeg": stocksEnSeg,
            "comTieneDatos": True,
            "segTieneDatos": True,
        }
    elif comprasUsuario.exists():
        evolCartera, evolTotal = _evolucion_cartera(comprasUsuario)
        context = {
            "usuario": usuario,
            "comprasUsuario": comprasUsuario,
            "evolCartera": evolCartera,
            "evolTotal": evolTotal,
            "comTieneDatos": True,
        }
    elif seguimientoUsuario.exists():
        stocksEnSeg = _stocks_en_seguimiento(seguimientoUsuario)
        context = {
            "usuario": usuario,
            "seguimientoUsuario": seguimientoUsuario,
            "stocksEnSeg": stocksEnSeg,
            "segTieneDatos": True,
        }
    else:
        context = {
            "usuario": usuario,
            "comTieneDatos": False,
            "segTieneDatos": False,
        }

    return render(request, "dashboard.html", context)



@login_required
def nueva_compra(request):

    # El contexto siempre va a tener, mínimo, estos dos campos:
    # Formulario y lista para mostrar sugerencias de búsqueda
    context = {
        "form": StockCompradoForm,
        "listaTickers": Tickers_BDs.tickersDisponibles(),
    }

    if request.method == "GET":    
        return render(request, "nueva_compra.html", context)
    
    else:
        # Django genera un formulario por mí, para guardar los 
        # datos desde el 'form':
        form = StockCompradoForm(request.POST)
        
        if form.is_valid():
            # El 'ticker' no está en el form para poder usar
            # una caja de búsqueda autocompletable con JS y 
            # la fecha se recoge con un calendario:
            ticker = request.POST.get('ticker')
            fecha = request.POST.get('fecha_compra')
            # Obtengo el resto de info del form directamente.
            # Con el número de acciones no hago operaciones internas y
            # lo guardo directamente si no hay errores
            precio_compra = form.cleaned_data['precio_compra']
            
            try:
                # Indico el formato con el que llega desde el HTML,
                # para transformar a DateTime
                format_str = "%d/%m/%Y"
                fecha = datetime.strptime(fecha, format_str)

                # Comprobación de base de datos y fecha
                bd = Tickers_BDs.obtenerNombreBD(ticker)
                context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='1')
                if context != False:
                    return render(request, "nueva_compra.html", context)
                
                # Adaptación del sufijo para coincidir con los modelos 
                # de las BDs, creados de forma dinámica
                ticker_bd = ticker.replace(".", "_")
                model = apps.get_model('Analysis', ticker_bd)

                # Los datos en la BD están con formato DateTime, para coger 
                # sólo la fecha utilizo date__date
                entrada = model.objects.using(bd).filter(date__date=fecha)
                
                # Comprobar posibles errores en la introducción 
                # de datos en el formulario
                context = _hay_errores(fecha, bd, ticker, entrada, precio_compra, caso='2')
                if context != False:
                    return render(request, "nueva_compra.html", context)
           
                nueva_compra = form.save(commit=False)
                # Como en el form no están los nombres de usuario
                # nombre del stock, etc., es necesario añadirlo aquí
                nueva_compra.usuario = request.user
                nueva_compra.ticker_bd = ticker_bd
                # nueva_compra.bd = bd
                nueva_compra.bd = bd
                nueva_compra.ticker = ticker
                nueva_compra.nombre_stock = entrada[0].name
                nueva_compra.fecha_compra = fecha
                # Lo mismo para la moneda y el sector, pero aprovechando
                # el acceso a la BD
                nueva_compra.moneda = entrada[0].currency
                nueva_compra.sector = entrada[0].sector
                nueva_compra.save()

            except Exception as ex:
                context["msg_error"] = "Error al guardar"
                return render(request, "nueva_compra.html", context)

            # Retorno al dashboard para mostrar lo guardado
            return redirect("dashboard")
        
        else:
            context["msg_error"] = "Error inesperado en el formulario"
            return render(request, "nueva_compra.html", context)
    


@login_required
def eliminar_compras(request):
    """Para eliminar las compras (posiciones abiertas) asociadas
    a un usuario.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "GET":
        # Filtrar por usuario
        comprasUsuario = StockComprado.objects.filter(usuario=request.user)
    
        context = {
            "comprasUsuario": comprasUsuario,
        }
        return render(request, "eliminar_compras.html", context)

    else:
        seleccionados = request.POST.getlist('eliminar_stocks')
        # Eliminar todos aquellos cuyo id esté en 'seleccionados'
        StockComprado.objects.filter(id__in=seleccionados).delete()
        return redirect("dashboard")
    


@login_required
def nuevo_seguimiento(request):

    # El contexto siempre va a tener, mínimo, estos dos campos:
    # Formulario y lista para mostrar sugerencias de búsqueda
    context = {
        "form": StockSeguimientoForm,
        "listaTickers": Tickers_BDs.tickersDisponibles(),
    }

    if request.method == "GET":
        return render(request, "nuevo_seguimiento.html", context)
    
    else:
        # Django genera un formulario por mí con este
        # método. Esto me permite guardar los datos, 
        # directamente, desde el formulario:
        form = StockSeguimientoForm(request.POST)
                
        if form.is_valid():
            # El 'ticker' no está en el form para poder usar
            # una caja de búsqueda autocompletable.
            ticker = request.POST.get('ticker')
            # La fecha de inicio de seguimiento (timezone en lugar de datetime
            # para evitar warning de 'naive datetime'). Almaceno como datetime
            # aunque sólo use la fecha (date())
            fecha = timezone.now()
            # Obtendría el resto de info del form directamente.
            # precio_entrada_deseado = form.cleaned_data['precio_entrada_deseado']
            
            try:
                # Comprobación de base de datos
                bd = Tickers_BDs.obtenerNombreBD(ticker)
                context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='3')
                if context != False:
                    return render(request, "nuevo_seguimiento.html", context)
            
                # Adaptación del sufijo para coincidir con los modelos 
                # de las BDs creados de forma dinámica
                ticker_bd = ticker.replace(".", "_")
                model = apps.get_model('Analysis', ticker_bd)

                # Los datos en la BD
                entrada = model.objects.using(bd)[:1]
            
                nuevo_seguimiento = form.save(commit=False)
                # Como en el form no están los nombres de usuario
                # ni el nombre del stock, es necesario añadirlo aquí
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.ticker_bd = ticker_bd
                nuevo_seguimiento.bd = bd
                nuevo_seguimiento.ticker = ticker
                nuevo_seguimiento.nombre_stock = entrada[0].name
                nuevo_seguimiento.fecha_inicio_seguimiento = fecha
                # Lo mismo para la moneda y el sector, pero aprovechando
                # el acceso a la BD
                nuevo_seguimiento.moneda = entrada[0].currency
                nuevo_seguimiento.sector = entrada[0].sector
                nuevo_seguimiento.save()
            
            except Exception:
                context["msg_error"] = "Error al guardar"
                return render(request, "nuevo_seguimiento.html", context)
            
            # Retorno al dashboard para mostrar lo guardado
            return redirect("dashboard")
        else:
            context["msg_error"] = "Error inesperado en el formulario"
            return render(request, "nuevo_seguimiento.html", context)
       


@login_required
def eliminar_seguimiento(request):
    pass

# @login_required
# def eliminar_seguimiento(request):
#     """Para eliminar valores seguidos por un usuario.

#     Args:
#         request (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     if request.method == "GET":
#         # Filtrar por usuario
#         listaSeguimiento = StockComprado.objects.filter(usuario=request.user)
    
#         context = {
#             "comprasUsuario": comprasUsuario,
#         }
#         return render(request, "eliminar_compras.html", context)

#     else:
#         seleccionados = request.POST.getlist('eliminar_stocks')
#         # Eliminar todos aquellos cuyo id esté en 'seleccionados'
#         StockComprado.objects.filter(id__in=seleccionados).delete()
#         return redirect("dashboard")



def _stocks_en_seguimiento(seguimientoUsuario):
    """Para caclular la evolución de las posiciones abiertas y 
    del total de la cartera. 

    Args:
        comprasUsuario (_type_): _description_

    Returns:
        _type_: _description_
    """
    stocksEnSeg = []

    for stockSeguido in seguimientoUsuario:
        model = apps.get_model('Analysis', stockSeguido.ticker_bd)
        bd = Tickers_BDs.obtenerNombreBD(stockSeguido.ticker)
        entrada = model.objects.using(bd).order_by('-date')[:1]

        stock = {}
        stock['ticker_bd'] = stockSeguido.ticker_bd
        stock['bd'] = bd
        stock['ticker'] = stockSeguido.ticker_bd.replace("_",".")
        stock['nombre'] = entrada[0].name
        stock['fecha_inicio_seguimiento'] = stockSeguido.fecha_inicio_seguimiento
        stock['precio_entrada_deseado'] = stockSeguido.precio_entrada_deseado
        stock['cierre'] = entrada[0].close
        # Lista con objetos de tipo 'Sectores' (uso exclude)
        # para que no se coja el propio stock con el que se compara
        listaSimilares = Sectores.objects.filter(sector=entrada[0].sector).exclude(nombre=entrada[0].name)
        stock['listaSimilares'] = listaSimilares

        stocksEnSeg.append(stock)

    return stocksEnSeg



def _evolucion_cartera(comprasUsuario):
    """Para caclular la evolución de las posiciones abiertas y 
    del total de la cartera. 

    Args:
        comprasUsuario (_type_): _description_

    Returns:
        _type_: _description_
    """
    evolCartera = []
    totalInicial = 0
    totalActual = 0
    evolTotal = 0

    for compra in comprasUsuario:
        model = apps.get_model('Analysis', compra.ticker_bd)
        bd = Tickers_BDs.obtenerNombreBD(compra.ticker)
        entrada = model.objects.using(bd).order_by('-date')[:1]

        evolStock = {}
        evolStock['ticker_bd'] = compra.ticker_bd
        evolStock['bd'] = bd
        evolStock['ticker'] = compra.ticker_bd.replace("_",".")
        evolStock['nombre'] = entrada[0].name
        evolStock['fecha_compra'] = compra.fecha_compra
        evolStock['num_acciones'] = compra.num_acciones
        evolStock['precio_compra'] = compra.precio_compra
        evolStock['cierre'] = entrada[0].close
        evol = (entrada[0].close - float(compra.precio_compra))/float(compra.precio_compra) * 100
        evolStock['evol'] = evol
        
        evolCartera.append(evolStock)
        
        totalInicial += compra.num_acciones * float(compra.precio_compra)
        totalActual += compra.num_acciones * entrada[0].close

    # Para evitar DivisionZero
    if totalInicial != 0:
        evolTotal = (totalActual - totalInicial)/totalInicial * 100
    
    return evolCartera, evolTotal
    


def _hay_errores(fecha, bd, ticker, entrada, precio_compra, caso):
    """Permite comprobar si los datos introducidos por
    el usuario son coherentes.

    Args:
        entrada (_type_): _description_
        fechaConFormato (_type_): _description_
        request (_type_): _description_
        precio_compra (_type_): _description_

    Returns:
        _type_: _description_
    """
    context = {
        "form": StockCompradoForm,
        "listaTickers": Tickers_BDs.tickersDisponibles(),
    }

    # Fecha con formato para mostrar en caso de error
    fechaConFormato = fecha.strftime("%d/%m/%Y")
    
    match caso:
        case "1":
            if bd == None:
                context["msg_error"] = f'El ticker {ticker} no está disponibe'
                return context
            elif fecha.date() > date.today():
                context["msg_error"] = 'No se pueden introducir fechas futuras'
                return context
        case "2":
            if not entrada.exists():
                context["msg_error"] = f'El {fechaConFormato} (d/m/Y) corresponde a un festivo, fin de semana o no existen registros.'
                return context
            elif precio_compra < entrada[0].low or precio_compra > entrada[0].high:
                context["msg_error_2"] = f'Ese precio no es posible para el día {fechaConFormato} (d/m/Y).'
                context["min"] = entrada[0].low
                context["max"] = entrada[0].high
                return context
        case "3":
            if bd == None:
                context["form"] = StockSeguimientoForm
                context["msg_error"] = f'El ticker {ticker} no está disponibe'
                return context
    # Si no hay errores
    return False