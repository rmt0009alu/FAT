"""
Métodos de vistas para usar con el DashBoard.
"""
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
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
# Para calcular los rendimientos mínimo y máximo posibles
from scipy.optimize import linprog
# Para calcular el óptimo de una cartera
from scipy.optimize import minimize
# Para el buffer y la imagen de la gráfica de Markowitz
from io import BytesIO
import base64


@login_required
def dashboard(request):
    """Para mostrar un dashboard al usuario.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        render
            Renderiza la plantilla 'dashboard.html' con datos de contexto.
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
        grafica_markowitz, sh_agregados, dist_pesos_agregadas = mostrar_markowitz_frontera_y_mejores(eur_usd, 
                                                                                                     eur_gbp, 
                                                                                                     compras_usuario)
        context = {
            "usuario": usuario,
            "comprasUsuario": compras_usuario,
            "eur_usd": eur_usd[0].ultimo_cierre,
            "eur_gbp": eur_gbp[0].ultimo_cierre,
            "monedas": monedas,
            "evolCartera": evol_cartera,
            "evolTotal": evol_total,
            "seguimientoUsuario": seguimiento_usuario,
            "stocksEnSeg": _stocks_en_seguimiento(seguimiento_usuario),
            "comTieneDatos": True,
            "segTieneDatos": True,
            "grafica_markowitz": grafica_markowitz,
            "sh_agregados": sh_agregados,
            "dist_pesos_agregadas": dist_pesos_agregadas,
        }
    elif compras_usuario.exists():
        evol_cartera, evol_total = _evolucion_cartera(compras_usuario)
        grafica_markowitz, sh_agregados, dist_pesos_agregadas = mostrar_markowitz_frontera_y_mejores(eur_usd, 
                                                                                                     eur_gbp, 
                                                                                                     compras_usuario)
        context = {
            "usuario": usuario,
            "comprasUsuario": compras_usuario,
            "eur_usd": eur_usd[0].ultimo_cierre,
            "eur_gbp": eur_gbp[0].ultimo_cierre,
            "monedas": monedas,
            "evolCartera": evol_cartera,
            "evolTotal": evol_total,
            "comTieneDatos": True,
            "grafica_markowitz": grafica_markowitz,
            "sh_agregados": sh_agregados,
            "dist_pesos_agregadas": dist_pesos_agregadas,
        }
    elif seguimiento_usuario.exists(): 
        context = {
            "usuario": usuario,
            "monedas": monedas,
            "seguimientoUsuario": seguimiento_usuario,
            "stocksEnSeg": _stocks_en_seguimiento(seguimiento_usuario),
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

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Union[render, redirect]: 
            * render
                Renderiza la plantilla 'nueva_compra.html' con datos de contexto (para GET).
            * redirect
                Plantilla de dashboard (para POST).
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
        nueva_comp.bd = bd
        nueva_comp.ticker = ticker
        nueva_comp.nombre_stock = entrada[0].name
        nueva_comp.fecha_compra = fecha
        # Lo mismo para la moneda y el sector, pero aprovechando
        # el acceso a la BD
        nueva_comp.moneda = entrada[0].currency
        nueva_comp.sector = entrada[0].sector
        nueva_comp.ult_cierre = model.objects.using(bd).order_by('-date')[:1][0].close
        nueva_comp.save()

        # Retorno al dashboard para mostrar lo guardado
        return redirect("dashboard")

    # Si el formulario no es válido
    context["msg_error"] = "Error inesperado en el formulario"
    return render(request, "nueva_compra.html", context)


@login_required
def eliminar_compras(request):
    """Para eliminar las compras (posiciones abiertas) asociadas a un usuario.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Union[render, redirect]:
            * render
                Renderiza la plantilla 'eliminar_compras.html' con datos de contexto (para GET).
            * redirect
                Plantilla de dashboard (para POST).
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

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Union[render, redirect]:
            * render
                Renderiza la plantilla 'nuevo_seguimiento.html' con datos de contexto (para GET)
            * redirect
                Plantilla de dashboard (para POST).
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
    """Para eliminar valores en seguimiento asociados a un usuario.

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Union[render, redirect]: 
            * render
                Renderiza la plantilla 'eliminar_compras.html' con datos de contexto (para GET).
            * redirect
                Plantilla de dashboard (para POST).
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
    """Para obtener una lista de los stocks en seguimiento de un usuario.

    Parameters
    ----------
        seguimiento_usuario : QuerySet
            objetos StockSeguimiento del usuario.

    Returns
    -------
        stocks_en_seg : list
            Stocks en seguimiento con información adicional (como los valores que son 
            similares según el sector al que pertenecen).
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
    """Para calular la evolución de las posiciones abiertas y del total de la cartera.

    Parameters
    ----------
        compras_usuario : QuerySet
            Objetos StockComprado del usuario.

    Returns
    -------
        tuple: Tupla que contiene las evoluciones.
            * evol_cartera : list
                Stocks comprados con info. adicional como la evolución desde la fecha de compra.
            * evol_total : float
                Valor de la evolución total de la cartera.
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
    """Permite comprobar si los datos introducidos por el usuario son coherentes.

    Parameters
    ----------
        fecha : django.utils.timezone
            Timezone actual.

        bd : str
            Nombre de la base de datos.

        ticker : str
            Nombre del ticker.

        entrada : QuerySet
            Registro en la bd del stock seleccionado en el formulario (en la fecha indicada).

        precio_compra : float
            Precio de compra a comprobar.

        caso : int
            Indicador del caso a tratar.

    Returns
    -------
        Union[dict, bool]: 
            * context : dict
                Diccionario con datos del cotexto.
            * bool 
                False en caso de que no haya errores.
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
                context["msg_error"] = f'El {fecha_con_formato} (d/m/Y) corresponde a un festivo,fin de semana o no existen registros.'
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


def mostrar_markowitz_frontera_y_mejores(eur_usd, eur_gbp, compras_usuario):
    
    # Calculo la volatilidad real de la cartera actual
    retornos_df, matriz_covarianza, volatilidad, pesos = _volatilidad_cartera(eur_usd, eur_gbp, compras_usuario)
    retornos_medios_reales = retornos_df.mean()
    # Pondero los retornos medios reales con los pesos correspondientes
    retorno_cartera_real = retornos_medios_reales*pesos

    # Realizo una simulación de Monte Carlo con miles de posibles carteras
    volatilidades_aleat, retornos_aleat, pesos_aleat = _simulacion_monte_carlo_markowitz(retornos_df,
                                                                                         matriz_covarianza)

    # Calculo los rendimientos mínimo y máximo posibles
    retorno_min, retorno_max, limites = _rendimientos_min_y_max(retornos_df)

    # Calculo la frontera eficiente
    riesgos_optimizados, retornos_objetivo = _frontera_eficiente_por_optimizacion(retorno_min, retorno_max, 
                                                                                  retornos_df, limites)
        
    # Calcular el mejor Sharpe ratio y los mejores pesos por optimización (- opt -)
    opt_mejor_sharpe_ratio, opt_mejores_pesos = _mejores_pesos_por_optimizacion(retornos_df, limites)
    
    # Además de calcular el mejor sharpe ratio utilizando minimización, se puede calcular
    # una aproximación (usando los datos de la simulación de Monte Carlo - mc -)
    mc_mejor_sharpe_ratio, mc_mejores_pesos = _mejores_pesos_por_monte_carlo(volatilidades_aleat, 
                                                                             retornos_aleat, 
                                                                             pesos_aleat)
    
    # Por último, preparo los datos de pesos y sharpe ratios de forma agregada
    # (aprovecho que calculo el sharpe ratio negativo y aquí lo negativizo de nuevo 
    # para hacerlo positivo)
    sharpe_ratio_real = - _opt_sharpe_ratio_negativo(pesos, retornos_df)
    sharpe_ratios_agregados, distribuciones_pesos_agregadas = _agregar_info_pesos(compras_usuario,
                                                                                  sharpe_ratio_real, pesos, 
                                                                                  opt_mejor_sharpe_ratio, 
                                                                                  opt_mejores_pesos, 
                                                                                  mc_mejor_sharpe_ratio, 
                                                                                  mc_mejores_pesos)

    fig = plt.figure(figsize=(7, 5))
    buffer = BytesIO()
    # Evolución de las variaciones diarias (nube de simulación de Monte Carlo)
    plt.scatter(volatilidades_aleat, retornos_aleat, c=retornos_aleat/volatilidades_aleat , alpha=0.5, s=3)
    plt.colorbar(label='Sharpe ratio')
    # Cartera actual (real)
    plt.scatter(volatilidad, retorno_cartera_real.sum(), c='black', label='Cartera actual (real)')
    # Frontera eficiente
    plt.plot(riesgos_optimizados, retornos_objetivo, color='black')
    # Mejor cartera según simulación de Monte Carlo
    mc_volatilidad = np.sqrt(mc_mejores_pesos.dot(matriz_covarianza).dot(mc_mejores_pesos))
    mc_retorno = retornos_medios_reales.dot(mc_mejores_pesos)
    plt.scatter([mc_volatilidad], [mc_retorno], color='red', marker='X', 
                label='Mejor cartera por simluación Monte Carlo', alpha=0.5)
    # Mejor cartera por optimización de funciones (minimizando)
    volatilidad_opt = np.sqrt(opt_mejores_pesos.dot(matriz_covarianza).dot(opt_mejores_pesos))
    retorno_opt = retornos_medios_reales.dot(opt_mejores_pesos)
    plt.scatter([volatilidad_opt], [retorno_opt], c='blue', marker='X', 
                label='Mejor cartera por optimización', alpha=0.5)
    plt.legend(fontsize='small')
    plt.xlabel('Volatilidad')
    plt.ylabel('Rendimiento esperado (en % diario)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title('Gráfica de Markowitz con curva de frontera eficiente')

    plt.savefig(buffer, format="PNG")
    plt.close()

    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    grafica_markowitz = base64.b64encode(buffer.read()).decode()

    return grafica_markowitz, sharpe_ratios_agregados, distribuciones_pesos_agregadas


def _volatilidad_cartera(eur_usd, eur_gbp, compras_usuario):
    ##################### PRUEBAS #####################
    # Calcular la volatilidad (std - desviación estándar) de los retornos
    # de los diferentes stocks desde el momento de compra
    
    # for key in precios_desde_compra.keys():
    #     # Media de los retornos
    #     retorno_medio = precios_desde_compra[key].aggregate(Avg('percent_variance'))
    #     print(retorno_medio)

    #     # Desviación estándar de los retornos
    #     std = precios_desde_compra[key].aggregate(StdDev('percent_variance'))
    #     print(std)

    precios_252_sesiones = {}
    retornos = {}
    
    # Obtener los datos de las últimas 252 sesiones de los valores comprados
    # por el usuario. Se cogen 252 sesiones porque es aprox. 1 año.
    for stock_comprado in compras_usuario:
        tick_bd = stock_comprado.ticker_bd
        bd = stock_comprado.bd
        mod = apps.get_model('Analysis', tick_bd)
        precios_252_sesiones[tick_bd] = mod.objects.using(bd).order_by('-date')[:252].values('date', 'ticker',
                                                                                             'percent_variance', 
                                                                                             'close')

    # Retornos de cada stock en las últimas 252 sesiones (aprox. 1 año)
    for key, datos_stock in precios_252_sesiones.items():
        retornos[key] = [dato['percent_variance'] for dato in datos_stock]
    # Los convierto a df para mayor comodidad
    retornos_df = pd.DataFrame.from_dict(retornos)
    
    # Posiciones en cartera calculadas en EUR
    posiciones_cartera = []
    for stock_comprado in compras_usuario:
        # Necesito hacer cast a float porque son de tipo 'Decimal'
        if stock_comprado.moneda == 'USD':
            posiciones_cartera.append(float(stock_comprado.posicion())/float(eur_usd[0].ultimo_cierre))
        elif stock_comprado.moneda == 'GBp':
            posiciones_cartera.append(float(stock_comprado.posicion())/float(eur_gbp[0].ultimo_cierre))
        else:
            posiciones_cartera.append(float(stock_comprado.posicion()))

    posiciones_cartera = np.array(posiciones_cartera)
    # Pesos de cada stock en cartera
    pesos = posiciones_cartera / posiciones_cartera.sum()
    pesos = np.array(pesos)

    # Matriz de covarianza
    matriz_covarianza = np.cov(retornos_df, rowvar=False)

    # Idea: https://medium.com/@FMZQuant/measuring-risk-and-return-an-introduction-to-markowitz-theory-49bca3135621
    # Varianza de la cartera. Como en Numpy se trabaja con vectores de 1 dimensión
    # no sería realmente necesario hacer la transposición de 'pesos', pero
    # lo hago porque resulta más intuitivo para asociar a la idea matemática
    varianza_cartera = np.dot(pesos.T, np.dot(matriz_covarianza, pesos))

    # Volatilidad de la cartera (si lo quiero anualizar: volatitilidad * sqrt(252))
    volatilidad = np.sqrt(varianza_cartera)

    return retornos_df, matriz_covarianza, volatilidad, pesos


def _simulacion_monte_carlo_markowitz(retornos_df, matriz_covarianza):
    # Para el gráfico de riesgo-rendimiento. Voy a generar una cantidad elevada 
    # de carteras con los mismos stocks pero pesos aleatorios para ver si la 
    # cartera del usuario está bien distribuida
    # -------------------------------------
    # Número de carteras aleatorias que voy a crear para comparar con la del usuario
    N = 10000
    # Número de stocks en las carteras
    D = len(retornos_df.columns)
    # Retornos y volatilidades aleatorias de las carteras ficticias
    retornos_aleatorios = np.zeros(N)
    volatilidades_aleatorias = np.zeros(N)
    # Retorno medio real de la cartera del usuario
    retornos_medios_reales = retornos_df.mean()
    # Pesos aleatorios
    pesos_aleatorios = []

    for i in range(N):
        # Al usar '- rand_range / 2' estoy considerando una cartera en la que
        # se puede hacer venta de activos (en corto) con el objetivo de obtener
        # una rentabilidad positiva
        rand_range = 1.0
        # Vector aleatorio con una distribución uniforme valores en [-0.5, 0.5]
        w = np.random.random(D)*rand_range - rand_range / 2
        # Cambio el último valor de 'w' para que sea 1 menos la suma del resto de
        # valores en 'w'. Así se mantiene la restricción de que 'w' debe sumar 1.
        w[-1] = 1 - w[:-1].sum()
        # Para evitar el bias
        np.random.shuffle(w)
        pesos_aleatorios.append(w)
        # Calcular el retorno y volatilidad de la cartera aleatoria que se está creando
        retornos_aleatorios[i] = retornos_medios_reales.dot(w)
        volatilidades_aleatorias[i] = np.sqrt(w.dot(matriz_covarianza).dot(w))
    
    return volatilidades_aleatorias, retornos_aleatorios, pesos_aleatorios


def _rendimientos_min_y_max(retornos_df):
    retornos_medios_reales = retornos_df.mean()
    # Número de valores en cartera
    D = len(retornos_df.columns)

    # Restricciones de igualdad del proceso de minimización del rendimiento
    A_eq = np.ones((1, D))
    b_eq = np.ones(1)
    # Límites (he usado -0.5 en otros casos como al calcular la gráfica de Markowitz)
    limites = [(-0.5, None)]*D
    
    # Se podría comprobar que el proceso de programación lineal funciona de forma esperada 
    # utilizando res.success, pero no voy a poner restricciones imposibles con lo cual, es 
    # de esperar que siempre funcione
    res = linprog(retornos_medios_reales, A_eq=A_eq, b_eq=b_eq, bounds=limites)
    retorno_min = res.fun
    res = linprog(-retornos_medios_reales, A_eq=A_eq, b_eq=b_eq, bounds=limites)
    retorno_max = -res.fun

    return retorno_min, retorno_max, limites


def _opt_funcion_objetivo_varianza(pesos, matriz_covarianza):
    """Devuelve la varianza de la cartera. Esta función se minimiza en el método
    _frontera_eficiente_por_optimizacion(retorno_min, retorno_max, retornos_df, limites).

    Args:
        pesos (_type_): _description_
        matriz_covarianza (_type_): _description_

    Returns:
        _type_: _description_
    """
    return pesos.dot(matriz_covarianza).dot(pesos)


def _opt_restriccion_retorno_objetivo(pesos, retornos_medios_reales, retorno_objetivo):
    """Función que sirve como restricción de igualdad. Devuleve 0 con se
    llega a la restricción. 
    """
    # Primero se calcula el retorno de la cartera y luego se resta el esperado
    # cuando sean iguales, devolverá 0, por eso sirve como retricción de igualdad. 
    return pesos.dot(retornos_medios_reales) - retorno_objetivo


def _opt_restriccion_cartera(pesos):
    # Será 0 cuando se cumpla la restricción, i.e., la suma de los pesos de los
    # valores en cartera será 1.
    return pesos.sum() - 1


def _frontera_eficiente_por_optimizacion(retorno_min, retorno_max, retornos_df, limites):
    D = len(retornos_df.columns)
    retornos_objetivo = np.linspace(retorno_min, retorno_max, num=100)
    retornos_medios_reales = retornos_df.mean()
    matriz_covarianza = np.cov(retornos_df, rowvar=False)
    restricciones = [
        {
            'type': 'eq',
            'fun': _opt_restriccion_retorno_objetivo,
            # Se pasan solo los argumentos extra que no se tienen que optimizar.
            # Como se tiene que optimizar los pesos, estos son los 'extra'
            'args': [retornos_medios_reales, retornos_objetivo[0]],
        },
        {
            'type': 'eq',
            'fun': _opt_restriccion_cartera,
        }
    ]

    # Nunca se llama a esta función cuando D < 1:
    if D == 1:
        # Con un único valor en cartera no hay pesos que optimizar, porque
        # ese valor tendrá siempre el 100% de peso
        pesos = np.array([1])
        varianza_cartera = np.dot(pesos.T, np.dot(matriz_covarianza, pesos))
        # Volatilidad de la cartera (si lo quiero anualizar: volatitilidad * sqrt(252))
        volatilidad = np.sqrt(varianza_cartera)
        riesgos_optimizados = [volatilidad for _ in retornos_objetivo]

        return riesgos_optimizados, retornos_objetivo
    
    # Recorro todos los rendimientos (entre mín. y máx.) para generar la frontera eficiente:
    riesgos_optimizados = []
    for objetivo in retornos_objetivo:
        restricciones[0]['args'] = [retornos_medios_reales, objetivo]

        res = minimize(fun = _opt_funcion_objetivo_varianza, 
                       x0 = np.ones(D) / D, 
                       method = 'SLSQP', 
                       args = matriz_covarianza,
                       constraints = restricciones,
                       bounds = limites)

        # Como estoy optimizando la varianza calculo su raíz, que sería la volatilidad (o riesgo)
        riesgos_optimizados.append(np.sqrt(res.fun))
        # if res.status != 0:
        #     print(res.success, res.message)

    return riesgos_optimizados, retornos_objetivo


def _opt_sharpe_ratio_negativo(pesos, retornos_df):
    """Función que va a pasar por un proceso de minimización de pesos
    para obtener el mínimo óptimo del sharpe ratio. Como quiero el sharpe 
    ratio máximo, lo que hago es que devuelva el mismo resultado pero en negativo. 

    Args:
        pesos (_type_): _description_
        retornos_df (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Se considera 0 porque se supone que al trabajar con valores cotizados no hay 
    # rendimiento libre de riesgo (los dividendos no se pueden considerar libre de riesgo)
    # Pongo la división entre 252 porque estoy usando datos diarios y, si quiero adaptar 
    # la tasa libre de riesgo debería mantener la división (con datos diarios)
    tasa_libre_riesgo = 0 / 252

    retornos_medios_reales = retornos_df.mean()
    matriz_covarianza = np.cov(retornos_df, rowvar=False)

    retorno_medio_cartera = pesos.dot(retornos_medios_reales)

    # Volatilidad = sqrt(varianza). No es necesario transponer 'pesos' en numpy
    # varianza = np.dot(pesos.T, np.dot(matriz_covarianza, pesos))
    volatilidad = np.sqrt(pesos.dot(matriz_covarianza).dot(pesos))

    return - (retorno_medio_cartera - tasa_libre_riesgo) / volatilidad


def _mejores_pesos_por_optimizacion(retornos_df, limites):
    
    D = len(retornos_df.columns)
    restricciones = {
        'type': 'eq',
        'fun': _opt_restriccion_cartera,
    }

    res = minimize(fun = _opt_sharpe_ratio_negativo, 
                   x0 = np.ones(D) / D, 
                   method = 'SLSQP', 
                   args = retornos_df,
                   constraints = restricciones,
                   bounds = limites)
    
    mejor_sharpe_ratio = -res.fun
    mejores_pesos = res.x

    return mejor_sharpe_ratio, mejores_pesos


def _mejores_pesos_por_monte_carlo(volatilidades_aleatorias, retornos_aleatorios, pesos_aleatorios):
    
    tasa_libre_riesgo = 0 / 252 

    monte_carlo_mejor_sharpe_ratio = -math.inf
    monte_carlo_mejores_pesos = -math.inf

    # Recorro todos los posibles valores aleatorios creados durante la simulación
    # de Monte Carlo y me quedo con el de mayor (mejor) Sharpe ratio:
    for i, (volatilidad, retorno) in enumerate(zip(volatilidades_aleatorias, retornos_aleatorios)):
        sharpe_ratio = (retorno - tasa_libre_riesgo) / volatilidad
        if sharpe_ratio > monte_carlo_mejor_sharpe_ratio:

            monte_carlo_mejor_sharpe_ratio = sharpe_ratio
            monte_carlo_mejores_pesos = pesos_aleatorios[i]

    return monte_carlo_mejor_sharpe_ratio, monte_carlo_mejores_pesos


def _agregar_info_pesos(compras_usuario, sharpe_ratio_real, pesos, 
                        opt_mejor_sharpe_ratio, opt_mejores_pesos, 
                        mc_mejor_sharpe_ratio, mc_mejores_pesos):
    
    # Tengo los valores en tipos numpy.float64 y prefiero float y estilo de %
    # para mostrar en HTML
    pesos = [float(100*_) for _ in pesos]
    opt_mejores_pesos = [float(100*_) for _ in opt_mejores_pesos]
    mc_mejores_pesos = [float(100*_) for _ in mc_mejores_pesos]
     
    sharpe_ratios_agregados = [sharpe_ratio_real, opt_mejor_sharpe_ratio, mc_mejor_sharpe_ratio]

    distribuciones_pesos_agregadas = []
    for i, compra in enumerate(compras_usuario):
        distribuciones_pesos_agregadas.append([compra.ticker, pesos[i], opt_mejores_pesos[i], mc_mejores_pesos[i]])
    
    sharpe_ratios_agregados = [None] + sharpe_ratios_agregados
    distribuciones_pesos_agregadas.append(sharpe_ratios_agregados)
    return sharpe_ratios_agregados, distribuciones_pesos_agregadas