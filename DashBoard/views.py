"""
Métodos de vistas para usar con el DashBoard.
"""
# Para procesar las fechas recibidas con el DatePicker
from datetime import datetime, date
from django.shortcuts import render, redirect
# Para proteger rutas. Las funciones que tienen este decorador
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required
# Para usar los modelos creados de forma dinámica
from django.apps import apps
from django.utils import timezone
from Analysis.models import Sectores, CambioMoneda
from util.tickers import Tickers_BDs
from .models import StockComprado, StockSeguimiento
from .forms import StockCompradoForm, StockSeguimientoForm


@login_required
def dashboard(request):
    """Para mostrar un dashboard al usuario.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (dict): diccionario con valores del contexto.
    """
    # Obtener el nombre del usuario
    usuario = request.user.username

    # Obtener compras del usuario actual
    compras_usuario = StockComprado.objects.filter(usuario=request.user)
    seguimiento_usuario = StockSeguimiento.objects.filter(usuario=request.user)
    eur_usd = CambioMoneda.objects.filter(ticker_forex='EURUSD')
    eur_gbp = CambioMoneda.objects.filter(ticker_forex='EURGBP')
    monedas = CambioMoneda.objects.all()

    if compras_usuario.exists() and seguimiento_usuario.exists():
        # Obtener la evolución de la cartera
        evol_cartera, evol_total = _evolucion_cartera(compras_usuario)
        stocks_en_seg = _stocks_en_seguimiento(seguimiento_usuario)
        context = {
            "usuario": usuario,
            "comprasUsuario": compras_usuario,
            "eur_usd": eur_usd[0].ultimo_cierre,
            "eur_gbp": eur_gbp[0].ultimo_cierre,
            "monedas": monedas,
            "evolCartera": evol_cartera,
            "evolTotal": evol_total,
            "seguimientoUsuario": seguimiento_usuario,
            "stocksEnSeg": stocks_en_seg,
            "comTieneDatos": True,
            "segTieneDatos": True,
        }
    elif compras_usuario.exists():
        evol_cartera, evol_total = _evolucion_cartera(compras_usuario)
        context = {
            "usuario": usuario,
            "comprasUsuario": compras_usuario,
            "eur_usd": eur_usd[0].ultimo_cierre,
            "eur_gbp": eur_gbp[0].ultimo_cierre,
            "monedas": monedas,
            "evolCartera": evol_cartera,
            "evolTotal": evol_total,
            "comTieneDatos": True,
        }
    elif seguimiento_usuario.exists():
        stocks_en_seg = _stocks_en_seguimiento(seguimiento_usuario)
        context = {
            "usuario": usuario,
            "monedas": monedas,
            "seguimientoUsuario": seguimiento_usuario,
            "stocksEnSeg": stocks_en_seg,
            "segTieneDatos": True,
        }
    else:
        context = {
            "usuario": usuario,
            "monedas": monedas,
            "comTieneDatos": False,
            "segTieneDatos": False,
        }

    return render(request, "dashboard.html", context)


@login_required
def nueva_compra(request):
    """Para registrar una nueva compra.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'nueva_compra.html' con datos de contexto.
        (redirect): plantilla de dashboard.
    """
    # El contexto siempre va a tener, mínimo, estos dos campos:
    # Formulario y lista para mostrar sugerencias de búsqueda
    context = {
        "form": StockCompradoForm,
        "listaTickers": Tickers_BDs.tickers_disponibles(),
    }

    if request.method == "GET":
        return render(request, "nueva_compra.html", context)

    # POST
    # ----
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

        # Indico el formato con el que llega desde el HTML,
        # para transformar a DateTime
        format_str = "%d/%m/%Y"
        fecha = datetime.strptime(fecha, format_str)

        # Comprobación de base de datos y fecha
        bd = Tickers_BDs.obtener_nombre_bd(ticker)
        context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='1')
        if context is not False:
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
        if context is not False:
            return render(request, "nueva_compra.html", context)

        nueva_comp = form.save(commit=False)
        # Como en el form no están los nombres de usuario
        # nombre del stock, etc., es necesario añadirlo aquí
        nueva_comp.usuario = request.user
        nueva_comp.ticker_bd = ticker_bd
        # nueva_compra.bd = bd
        nueva_comp.bd = bd
        nueva_comp.ticker = ticker
        nueva_comp.nombre_stock = entrada[0].name
        nueva_comp.fecha_compra = fecha
        # Lo mismo para la moneda y el sector, pero aprovechando
        # el acceso a la BD
        nueva_comp.moneda = entrada[0].currency
        nueva_comp.sector = entrada[0].sector
        nueva_comp.save()

        # Retorno al dashboard para mostrar lo guardado
        return redirect("dashboard")

    # Si el formulario no es válido
    context["msg_error"] = "Error inesperado en el formulario"
    return render(request, "nueva_compra.html", context)


@login_required
def eliminar_compras(request):
    """Para eliminar las compras (posiciones abiertas) asociadas
    a un usuario.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'eliminar_compras.html' con datos de contexto.
        (redirect): plantilla de dashboard.
    """
    if request.method == "GET":
        # Filtrar por usuario
        compras_usuario = StockComprado.objects.filter(usuario=request.user)

        context = {
            "compras_usuario": compras_usuario,
        }
        return render(request, "eliminar_compras.html", context)

    # POST
    # ----
    seleccionados = request.POST.getlist('eliminar_stocks')
    # Eliminar todos aquellos cuyo id esté en 'seleccionados'
    StockComprado.objects.filter(id__in=seleccionados).delete()
    return redirect("dashboard")


@login_required
def nuevo_seguimiento(request):
    """Para registrar un nuevo valor en seguimiento.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'nuevo_seguimiento.html' con datos de contexto.
        (redirect): plantilla de dashboard.
    """
    # El contexto siempre va a tener, mínimo, estos dos campos:
    # Formulario y lista para mostrar sugerencias de búsqueda
    context = {
        "form": StockSeguimientoForm,
        "listaTickers": Tickers_BDs.tickers_disponibles(),
    }

    if request.method == "GET":
        return render(request, "nuevo_seguimiento.html", context)

    # POST
    # ----
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

        # Comprobación de base de datos
        bd = Tickers_BDs.obtener_nombre_bd(ticker)
        context = _hay_errores(fecha, bd, ticker, entrada=None, precio_compra=None, caso='3')
        if context is not False:
            return render(request, "nuevo_seguimiento.html", context)

        # Adaptación del sufijo para coincidir con los modelos
        # de las BDs creados de forma dinámica
        ticker_bd = ticker.replace(".", "_")
        model = apps.get_model('Analysis', ticker_bd)

        # Los datos en la BD
        entrada = model.objects.using(bd)[:1]

        nuevo_seg = form.save(commit=False)
        # Como en el form no están los nombres de usuario
        # ni el nombre del stock, es necesario añadirlo aquí
        nuevo_seg.usuario = request.user
        nuevo_seg.ticker_bd = ticker_bd
        nuevo_seg.bd = bd
        nuevo_seg.ticker = ticker
        nuevo_seg.nombre_stock = entrada[0].name
        nuevo_seg.fecha_inicio_seguimiento = fecha
        # Lo mismo para la moneda y el sector, pero aprovechando
        # el acceso a la BD
        nuevo_seg.moneda = entrada[0].currency
        nuevo_seg.sector = entrada[0].sector
        nuevo_seg.save()

        # Retorno al dashboard para mostrar lo guardado
        return redirect("dashboard")

    # Si el formulario no es válido
    context["msg_error"] = "Error inesperado en el formulario"
    return render(request, "nuevo_seguimiento.html", context)


@login_required
def eliminar_seguimientos(request):
    """Para eliminar valores en seguimiento asociados
    a un usuario.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'eliminar_compras.html' con datos de contexto.
        (redirect): plantilla de dashboard.
    """
    if request.method == "GET":
        # Filtrar por usuario
        lista_seguimiento = StockSeguimiento.objects.filter(usuario=request.user)

        context = {
            "lista_seguimiento": lista_seguimiento,
        }
        return render(request, "eliminar_seguimientos.html", context)

    # POST
    # ----
    seleccionados = request.POST.getlist('eliminar_seguimientos')
    # Eliminar todos aquellos cuyo id esté en 'seleccionados'
    StockSeguimiento.objects.filter(id__in=seleccionados).delete()
    return redirect("dashboard")


def _stocks_en_seguimiento(seguimiento_usuario):
    """Para caclular la evolución de las posiciones abiertas y
    del total de la cartera.

    Args:
        seguimiento_usuario (QuerySet): objetos StockSeguimiento del usuario.

    Returns:
        (list): stocks en seguimiento con info. adicional como
            los valores que son similares según el sector al que pertenecen.
    """
    stocks_en_seg = []

    for stock_seguido in seguimiento_usuario:
        model = apps.get_model('Analysis', stock_seguido.ticker_bd)
        bd = Tickers_BDs.obtener_nombre_bd(stock_seguido.ticker)
        entrada = model.objects.using(bd).order_by('-date')[:1]

        stock = {}
        stock['ticker_bd'] = stock_seguido.ticker_bd
        stock['bd'] = bd
        stock['ticker'] = stock_seguido.ticker_bd.replace("_", ".")
        stock['nombre'] = entrada[0].name
        stock['fecha_inicio_seguimiento'] = stock_seguido.fecha_inicio_seguimiento
        stock['precio_entrada_deseado'] = stock_seguido.precio_entrada_deseado
        stock['moneda'] = stock_seguido.moneda
        stock['cierre'] = entrada[0].close
        # Lista con objetos de tipo 'Sectores' (uso exclude
        # para que no se coja el propio stock con el que se compara)
        lista_similares = Sectores.objects.filter(sector=entrada[0].sector).exclude(nombre=entrada[0].name)
        stock['listaSimilares'] = lista_similares

        stocks_en_seg.append(stock)

    return stocks_en_seg


def _evolucion_cartera(compras_usuario):
    """Para calular la evolución de las posiciones abiertas y
    del total de la cartera.

    Args:
        compras_usuario (QuerySet): objetos StockComprado del usuario.

    Returns:
        evol_cartera (list): stocks comprados con info. adicional como
            la evolución desde la fecha de compra.
        evol_total (float): valor de la evolución total de la cartera.
    """
    evol_cartera = []
    total_inicial = 0
    total_actual = 0
    evol_total = 0

    for compra in compras_usuario:
        model = apps.get_model('Analysis', compra.ticker_bd)
        bd = Tickers_BDs.obtener_nombre_bd(compra.ticker)
        entrada = model.objects.using(bd).order_by('-date')[:1]

        evol_stock = {}
        evol_stock['ticker_bd'] = compra.ticker_bd
        evol_stock['bd'] = bd
        evol_stock['ticker'] = compra.ticker_bd.replace("_", ".")
        evol_stock['nombre'] = entrada[0].name
        evol_stock['fecha_compra'] = compra.fecha_compra
        evol_stock['num_acciones'] = compra.num_acciones
        evol_stock['precio_compra'] = compra.precio_compra
        evol_stock['moneda'] = compra.moneda
        evol_stock['cierre'] = entrada[0].close
        evol = (entrada[0].close - float(compra.precio_compra))/float(compra.precio_compra) * 100
        evol_stock['evol'] = evol

        evol_cartera.append(evol_stock)

        total_inicial += compra.num_acciones * float(compra.precio_compra)
        total_actual += compra.num_acciones * entrada[0].close

    # Para evitar DivisionZero
    if total_inicial != 0:
        evol_total = (total_actual - total_inicial)/total_inicial * 100

    return evol_cartera, evol_total


def _hay_errores(fecha, bd, ticker, entrada, precio_compra, caso):
    """Permite comprobar si los datos introducidos por
    el usuario son coherentes.

    Args:
        fecha (django.utils.timezone): timezone actual.
        bd (str): nombre de la base de datos.
        ticker (str): nombre del ticker.
        entrada (QuerySet): registro en la bd del stock seleccionado
            en el formulario (en la fecha indicada).
        precio_compra (float): precio de compra a comprobar.
        caso (int): indicador del caso a tratar.

    Returns:
        (dict): diccionario con datos del cotexto.
    """
    context = {
        "form": StockCompradoForm,
        "listaTickers": Tickers_BDs.tickers_disponibles(),
    }

    # Fecha con formato para mostrar en caso de error
    fecha_con_formato = fecha.strftime("%d/%m/%Y")

    match caso:
        case "1":
            if bd is None:
                context["msg_error"] = f'El ticker {ticker} no está disponibe'
                return context
            if fecha.date() > date.today():
                context["msg_error"] = 'No se pueden introducir fechas futuras'
                return context
        case "2":
            if not entrada.exists():
                context["msg_error"] = f'El {fecha_con_formato} (d/m/Y) corresponde a un festivo, fin de semana o no existen registros.'
                return context
            if precio_compra < entrada[0].low or precio_compra > entrada[0].high:
                context["msg_error_2"] = f'Ese precio no es posible para el día {fecha_con_formato} (d/m/Y).'
                context["min"] = entrada[0].low
                context["max"] = entrada[0].high
                return context
        case "3":
            if bd is None:
                context["form"] = StockSeguimientoForm
                context["msg_error"] = f'El ticker {ticker} no está disponibe'
                return context
    # Si no hay errores
    return False
