"""
Métodos de vistas para usar con Lab.
"""
import math
import matplotlib.pyplot as plt
# Para el buffer y las imágenes
from io import BytesIO
import base64
from django.shortcuts import render
from django.apps import apps
# Para pasar str a literales
import ast
import pandas as pd
# Para evitar todos los warnings de convergencia y de datos no estacionarios
# al aplicar los modelos ARIMA
import warnings
warnings.filterwarnings("ignore")
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima
from util.tickers.Tickers_BDs import obtener_nombre_bd, tickers_disponibles
# Mis formularios
from .forms import ArimaAutoForm, ArimaRejillaForm, ArimaManualForm



def lab(request):
    """Para mostrar los modelos disponibles que se
    pueden aplicar. El usuario verá la vista de 'lab.html'
    con la información necesaria. 

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'lab.html' con datos de contexto.
    """
    # Obtener el nombre del usuario
    usuario = request.user.username

    context = {
        "usuario": usuario,
    }
    return render(request, "lab.html", context)


def arima_auto(request):
    """Para mostrar el resultado de un modelo ARIMA
    cuyos parámetros (p,d,q) son calculados automáticamente
    con 'auto_arima'. 

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'arima_auto.html' con datos
            de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": ArimaAutoForm,
        }
        return render(request, "arima_auto.html", context)

    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")

    # Uso el resto del formulario (sin el ticker)
    form = ArimaAutoForm(request.POST)
    if form.is_valid():
        # Hago un preprocesado común a todas formas de cálculo
        # de los parámetros (p,d,q)

        order, fechas, tam_entrenamiento, datos, context = _preprocesar_p_d_q(ticker, form, request)

        # Al preprocesar el context debe ser None si todo ha ido bien
        if context is None:
            # Hago una validación diaria para los datos de test
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward(tam_entrenamiento, datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_auto.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario(form, ticker, request)
    return render(request, "arima_auto.html", context)


def arima_rejilla(request):
    """Para mostrar el resultado de un modelo ARIMA
    cuyos parámetros (p,d,q) son calculados a través de 
    una búsqueda por rejilla predefinida por el usuario. 

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'arima_rejilla.html' con datos
            de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": ArimaRejillaForm,
        }
        return render(request, "arima_rejilla.html", context)

    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")

    # Uso el resto del formulario (sin el ticker)
    form = ArimaRejillaForm(request.POST)

    if form.is_valid():
        # Hago un preprocesado común a todas formas de cálculo
        # de los parámetros (p,d,q)
        order, fechas, tam_entrenamiento, datos, context = _preprocesar_p_d_q(ticker, form, request)

        # Al preprocesar el context debe ser None si todo ha ido bien
        if context is None:
            # Hago una validación diaria para los datos de test
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward(tam_entrenamiento, datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_rejilla.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario(form, ticker, request)
    return render(request, "arima_rejilla.html", context)


def arima_manual(request):
    """Para mostrar el resultado de un modelo ARIMA
    cuyos parámetros (p,d,q) son conocidos por el usuario. 

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'arima_manual.html' con datos
            de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": ArimaManualForm,
        }
        return render(request, "arima_manual.html", context)

    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")

    # Uso el resto del formulario (sin el ticker)
    form = ArimaManualForm(request.POST)

    if form.is_valid():
        # Hago un preprocesado común a todas formas de cálculo
        # de los parámetros (p,d,q)
        order, fechas, tam_entrenamiento, datos, context = _preprocesar_p_d_q(ticker, form, request)

        # Al preprocesar el context debe ser None si todo ha ido bien
        if context is None:
            # Hago una validación diaria para los datos de test
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward(tam_entrenamiento, datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_manual.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario(form, ticker, request)
    return render(request, "arima_manual.html", context)


def _preprocesar_p_d_q(ticker, form, request):
    """Para preprocesar la información y no saturar de código los
    métodos de ARIMA. 

    Args:
        ticker (str): nombre del ticker. 
        form (Lab.forms.Form): formulario utilizado para recabar datos. 
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        order (tuple): tupla con los parámetros (p, d, q)
        fechas (pandas.core.series.Series): fechas asociadas a los precios
            de cierre que hay en 'datos'.
        tam_entrenamiento (int): tamaño de los datos (%) dedicados a entrenamiento. 
        datos (pandas.core.series.Series): conjunto total de datos (entrenamiento
            y test) con los cierres del valor seleccionado.
        context (dict / None): diccionario con los datos del contexto o None
            en caso de que no haya errores en formulario. 
    """
    # Obtengo datos del form
    num_sesiones = form.cleaned_data['num_sesiones']
    porcentaje_entren = form.cleaned_data['porcentaje_entrenamiento']
    auto = form.cleaned_data['auto']
    manual = form.cleaned_data['manual']
    rejilla = form.cleaned_data['rejilla']

    if isinstance(form, ArimaRejillaForm):
        valores_p = form.cleaned_data['valores_p']
        valores_d = form.cleaned_data['valores_d']
        valores_q = form.cleaned_data['valores_q']
        # Paso a listas
        valores_p = ast.literal_eval(valores_p)
        valores_d = ast.literal_eval(valores_d)
        valores_q = ast.literal_eval(valores_q)

    if isinstance(form, ArimaManualForm):
        valor_p = form.cleaned_data['valor_p']
        valor_d = form.cleaned_data['valor_d']
        valor_q = form.cleaned_data['valor_q']

    # Compruebo existencia de ticker
    context = _comprobar_formulario(form, ticker, request)

    if context is not False:
        # Si hay datos en el contexto es porque algo está mal y se
        # añade un mensaje informativo al usuario
        return None, None, None, None, context
    # En otro caso, el contexto será nulo
    context = None

    # Busco la info para el nº de sesiones indicado por ususario
    modelo = apps.get_model('Analysis', ticker)
    bd = obtener_nombre_bd(ticker)
    entrada = modelo.objects.using(bd).order_by('-date')[:num_sesiones]
    df = pd.DataFrame(list(entrada.values()))
    # Y ordeno el resultado
    df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

    # Guardo las fechas para usarlas como índices
    datos = df['close']
    fechas = df['date']

    # Split 70/30 o lo que sea (uso el % indicado por el usuario adaptándolo)
    porcentaje_entren = int(porcentaje_entren.replace('%', ''))/100
    tam_entrenamiento = int(len(datos) * porcentaje_entren)
    datos_entrenamiento, datos_test = datos[:tam_entrenamiento], datos[tam_entrenamiento:]

    # El modelo se calcula con uno parámetros (order) que
    # dependen de la elección del usuario
    order = None

    if auto is True:
        # Calcular 'order' de forma automática con auto_arima. Uso todos
        # los datos para calcular order=(p,d,q) una única vez
        model = auto_arima(datos, seasonal=False)
        order = model.order

    if rejilla is True:
        # El mejor MSE es el menor MSE, lógicamente
        mejor_mse, mejor_order = math.inf, None
        for p in valores_p:
            for d in valores_d:
                for q in valores_q:
                    order = (p,d,q)
                    try:
                        # Se podría usar AIC, BIC o HQIC, pero MSE/RMSE es más fiable
                        mse = _evaluar_modelo_arima_mse(datos_entrenamiento, datos_test, order)
                        if mse < mejor_mse:
                            mejor_mse, mejor_order = mse, order
                    except:
                        continue
        order = mejor_order

    if manual is True:
        # Datos directamente introducidos por el usuario
        order = (valor_p, valor_d, valor_q)

    return order, fechas, tam_entrenamiento, datos, context


def _evaluar_modelo_arima_mse(datos_entrenamiento, datos_test, order):
    """Para evaluar la calidad del modelo aplicado en función del
    error cuadrático medio (mse) entre los datos de test y los datos
    estimados. Se pueden usar otras métricas como AIC, BIC o HQIC,
    pero esta es muy fiable. 

    Args:
        datos_entrenamiento (pandas.core.series.Series): datos de 
            entrenamiento del modelo. 
        datos_test (pandas.core.series.Series): datos para testear
            el modelo. 
        order (tuple): tupla con los parámetros (p, d, q)

    Returns:
        mse (numpy.float64): error cuadrático medio calculado entre
            los datos reales (datos_test) y las predicciones. 
    """
    conjunto_total = list(datos_entrenamiento)
    lista_predicciones = []

    # Validación 'walk-forward' para comprobar MSE (y RMSE)
    for t in range(len(datos_test)):
        modelo = ARIMA(conjunto_total, order=order)
        modelo_fit = modelo.fit()
        # Por defecto, el forecast es de un step, podría omitirlo
        output = modelo_fit.forecast(steps=1)
        estimado = output[0]
        lista_predicciones.append(estimado)
        # El dato real es el que está en datos_test
        # y se usa para la siguiente iteración
        conjunto_total.append(datos_test.iloc[t])

    mse = mean_squared_error(datos_test, lista_predicciones)

    # NOTA: se puede hacer Validación directa con aic, bic y hqic.
    # Cuanto menores son, mejor. Pero MSE/RMSE es más fiable.
    #
    # modelo_directo = ARIMA(datos_test, order=order)
    # output = modelo_directo.fit()
    # aic, bic, hqic = output.aic, output.bic, output.hqic

    return mse



def _comprobar_formulario(form, ticker, request):
    """Permite comprobar si los datos introducidos por
    el usuario en cualquiera de los formularios disponibles
    son coherentes.

    Args:
        bd (str): nombre de la base de datos.
        ticker (str): nombre del ticker.
        num_sesiones (int): número de sesiones que se quieren analizar. 
        porcentaje_entren (int): % de datos para el entrenamiento del modelo.
        caso (int): indicador del caso a tratar.

    Returns:
        False / context (boolean / dict): False o diccionario con datos del 
            cotexto en caso de fallo en formulario.
    """
    context = {
        "form": type(form),
        "lista_tickers": tickers_disponibles(),
    }

    bd = obtener_nombre_bd(ticker)

    # Obtengo datos del form, para formularios NO válidos no puedo usar
    # form.cleaned_data['...'] y, por tanto, los datos serán 'str'
    num_sesiones = request.POST.get('num_sesiones')
    porcentaje_entren = request.POST.get('porcentaje_entrenamiento')

    if bd is None:
        context["msg_error"] = f'El ticker {ticker} no está disponibe'
        return context

    if num_sesiones.isdigit():
        num_sesiones = int(num_sesiones)
        if not 100 <= num_sesiones <= 500:
            context["msg_error"] = 'Valor no válido para el nº de sesiones'
            return context
    else:
        context["msg_error"] = 'Valor no válido para el nº de sesiones'
        return context

    if porcentaje_entren not in ['50%', '66%', '70%', '80%', '90%']:
        context["msg_error"] = 'Porcentaje indicado no válido'
        return context

    if isinstance(form, ArimaRejillaForm):
        valores_p = request.POST.get('valores_p')
        valores_d = request.POST.get('valores_d')
        valores_q = request.POST.get('valores_q')
        admitidos = ['[0, 1]', '[1, 2]', '[0, 1, 2]', '[1, 2, 3]', '[2, 3, 4]']
        if valores_p not in admitidos:
            context["msg_error"] = "Valores para 'p' no válidos"
            return context
        if valores_d not in admitidos:
            context["msg_error"] = "Valores para 'd' no válidos"
            return context
        if valores_q not in admitidos:
            context["msg_error"] = "Valores para 'q' no válidos"
            return context

    if isinstance(form, ArimaManualForm):
        valor_p = request.POST.get('valor_p')
        valor_d = request.POST.get('valor_d')
        valor_q = request.POST.get('valor_q')
        if int(valor_p) not in list(range(0, 11)):
            context["msg_error"] = "Valor para 'p' no válido [0 - 10]"
            return context
        if int(valor_d) not in list(range(0, 4)):
            context["msg_error"] = "Valor para 'd' no válido [0 - 3]"
            return context
        if int(valor_q) not in list(range(0, 11)):
            context["msg_error"] = "Valor para 'q' no válido [0 - 10]"
            return context

    # Si no hay errores
    return False


def _validacion_walk_forward(tam_entrenamiento, datos, order):
    """Para realizar la validación basada en el MSE. Se realiza 
    una validación de un paso hacia atrás, i.e., se comprueba el
    error cuadrático medio (mse) cometido entre la predicción
    para el día siguiente y el resultado real de cierre en ese día.

    Args:
        tam_entrenamiento (int): tamaño de los datos (%) dedicados a entrenamiento. 
        datos (pandas.core.series.Series): conjunto total de datos (entrenamiento
            y test) con los cierres del valor seleccionado. 
        order (tuple): tupla con los valores (p, d, q).

    Returns:
        modelo_fit (statsmodels.tsa.arima.model.ARIMAResultsWrapper): modelo. 
        aciertos_tendencia (list): cantidad de aciertos/fallos en la predicción
            con los datos de test.
        predicciones (lista): lista con predicciones realizadas. 
    """
    predicciones = []
    aciertos_tendencia = []

    datos_entrenamiento = datos[:tam_entrenamiento]
    datos_test = datos[tam_entrenamiento:]

    # Separo en 'conjunto_total' porque lo voy actualizando para los
    # subsecuentes análisis
    conjunto_total = list(datos_entrenamiento)

    # Validación 'walk-forward'
    for t in range(len(datos_test)):
        modelo = ARIMA(conjunto_total, order=order)
        modelo_fit = modelo.fit()
        # Por defecto, el forecast es de un step, podría omitirlo
        output = modelo_fit.forecast(steps=1)
        estimado = output[0]
        predicciones.append(estimado)
        # El dato real es el que está en datos_test
        # y se usa para la siguiente iteración
        conjunto_total.append(datos_test.iloc[t])
        if t>0:
            previo = datos_test.iloc[t-1]
        else:
            # Cuando t=0 el dato anterior corresponde a los de entrenamiento
            previo = datos_entrenamiento.iloc[-1]

        # Comprobación de aciertos vs fallos para mostrar al usuario
        real = datos_test.iloc[t]
        if (previo < estimado and previo < real) or (previo > estimado and previo > real) or (previo == estimado and previo == real):
            acierta_tendencia = True
        else:
            acierta_tendencia = False

        aciertos_tendencia.append(acierta_tendencia)

    return modelo_fit, aciertos_tendencia, predicciones


def _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia):
    """Para generar los resultados gráficos y textuales
    que se mostrarán al usuario en la plantilla HTML para
    informarle sobre los resultados del modelo ARIMA elegido.

    Args:
        form (Lab.forms.Form): formulario creado para recabar información. 
        modelo_fit (statsmodels.tsa.arima.model.ARIMAResultsWrapper): modelo. 
        fechas (pandas.core.series.Series): fechas asociadas a los precios de cierre
            que hay en 'datos'.
        predicciones (list): lista con las predicciones realizadas. 
        tam_entrenamiento (int): tamaño de los datos dedicados a entrenamiento. 
        datos (pandas.core.series.Series): conjunto total de datos (entrenamiento
            y test) con los cierres del valor seleccionado. 
        aciertos_tendencia (list): cantidad de aciertos/fallos en la predicción
            con los datos de test. 

    Returns:
        context (dict): diccionario con los datos del contexto.
    """
    datos_test = datos[tam_entrenamiento:]

    datos.index = fechas
    predicciones = pd.DataFrame(predicciones)
    predicciones.index = fechas[tam_entrenamiento:]

    # Preparar figura y buffer
    plt.figure(figsize=(7, 5))
    buffer = BytesIO()
    # Gráfica con los datos reales y las predicciones
    plt.plot(datos.index, datos, color='blue', label='Original')
    plt.plot(predicciones.index, predicciones, color='red', label=f'Predicción últimos {len(datos_test)} días')
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.legend()
    plt.savefig(buffer, format='PNG')
    plt.close()
    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    forecast_arima = base64.b64encode(buffer.read()).decode()

    # # Se pueden ver los residuos y su densidad:
    # residuos = pd.DataFrame(modelo_fit.resid)
    # residuos.plot()
    # plt.savefig('linea_residuos.png', format="PNG")
    # # Gráfica de densidad de los residuos
    # residuos.plot(kind='kde')
    # plt.savefig('densidad_residuos.png', format="PNG")
    # # Resumen estadístico de los residuos
    # print(residuos.describe())

    # Hago una predicción adicional para la próxima sesión
    prediccion = modelo_fit.forecast(steps=1)

    context = {
        "lista_tickers": tickers_disponibles(),
        "form": type(form),
        "forecast_arima": forecast_arima,
        "resumen": modelo_fit.summary(),
        "mse": mean_squared_error(datos_test, predicciones),
        "rmse": math.sqrt(mean_squared_error(datos_test, predicciones)),
        "prediccion_prox_sesion": prediccion,
        "aciertos_tendencia": aciertos_tendencia.count(True),
        "fallos_tendencia": aciertos_tendencia.count(False),
    }
    return context
