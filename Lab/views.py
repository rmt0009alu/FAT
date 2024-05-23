"""
Métodos de vistas para usar con Lab.
"""
# Keras utiliza la librería oneAPI Deep Neural Network Library (oneDNN)
# https://stackoverflow.com/questions/77921357/warning-while-using-tensorflow-tensorflow-core-util-port-cc113-onednn-custom
# para optimizar el rendimiento en arquitecturas Intel, pero arroja 
# un warning constantemente. Para eliminarlo:
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
import math
# Para pasar str a literales
import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Para evitar todos los warnings de convergencia y de datos no estacionarios
# al aplicar los modelos ARIMA
import warnings
warnings.filterwarnings("ignore")
# Para el buffer y las imágenes
import base64
from io import BytesIO, StringIO
from django.shortcuts import render
from django.apps import apps
# Para proteger rutas. Las funciones que tienen este decorador
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required
# Para usar django-pandas y frames
from django_pandas.io import read_frame
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pmdarima.arima import auto_arima
from util.tickers.Tickers_BDs import obtener_nombre_bd, tickers_disponibles
# Mis formularios
from .forms import BuscarParametrosArimaForm, ArimaAutoForm, ArimaRejillaForm, ArimaManualForm, LstmForm
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler


@login_required
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



@login_required
def buscar_paramateros_arima(request):
    """Para buscar, a partir de gráficas, los mejores datos de los parámetros
    (p, d, q). Requiere que el usuario entienda lo que está viendo. 

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'buscar_paramateros_arima.html' con datos
            de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": BuscarParametrosArimaForm,
        }
        return render(request, "buscar_paramateros_arima.html", context)

    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")

    # Uso el resto del formulario (sin el ticker)
    form = BuscarParametrosArimaForm(request.POST)
    if form.is_valid():
        # Compruebo existencia de ticker y num_sesiones
        context = _comprobar_formulario_arima(form, ticker, request)

        if context is not False:
            return render(request, "buscar_paramateros_arima.html", context)

        num_sesiones = form.cleaned_data['num_sesiones']

        model = apps.get_model('Analysis', ticker)
        bd = obtener_nombre_bd(ticker)
        entradas = model.objects.using(bd).order_by('-date')[:num_sesiones]
        df = read_frame(entradas.values('date', 'close', 'ticker', 'name'))

        # Calculo la diferenciación logarítmica y obtengo las gráficas oportunas
        graf_1 = _diferenciacion_logaritmica(df, 1)
        graf_2 = _diferenciacion_logaritmica(df, 2)
        graf_3 = _diferenciacion_logaritmica(df, 3) 

        context = {
            'form': BuscarParametrosArimaForm(),
            "lista_tickers": tickers_disponibles(),
            'graf_1': graf_1,
            'graf_2': graf_2,
            'graf_3': graf_3,
        }
        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "buscar_paramateros_arima.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario_arima(form, ticker, request)
    return render(request, "buscar_paramateros_arima.html", context)


def _diferenciacion_logaritmica(df, d):
    """Para hacer una diferenciación logarítmica como se haría de forma manual,
    para hacer la serie estacionaria y que podamos aplicar las funciones ACF y PACF. 
    Además, genera las gráficas necesarias para que el usuario interprete los datos. 

    Args:
        df (pandas.core.frame.DataFrame): conjunto total de datos. 
        d (int): orden de diferenciación (la I_(d) de ARIMA).

    Returns:
        grafica_acf_pacf (str): imagen con las gráficas de diferenciación de cierres,
            ACF y PACF.
    """
    log_close = np.log(df['close'])
    df['retorno'] = log_close.diff(d)

    nombre = df['ticker'].iloc[0]
    nombre = nombre.replace("_", ".")
    nombre = nombre.replace("^", "")

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    # Primer plot = serie diferenciada
    axs[0].plot(df['date'], df['retorno'], 'b-')
    axs[0].set_title(f'Diferenciación de precios de cierre {nombre}')
    axs[0].set_xlabel('Tiempo')
    axs[0].set_ylabel('diff()')
    axs[0].xaxis.set_major_locator(mdates.YearLocator())
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axs[0].grid(True)

    # Segundo plot = ACF
    # Elimino tantas primeras filas como número de diferenciaciones se hayan 
    # realizado. Es decir, hago un dropna para los primeros 'd' NaN
    plot_acf(df['retorno'].dropna(), ax=axs[1])
    axs[1].set_title('ACF')
    axs[1].set_xlabel(r'$\tau$')
    axs[1].set_ylabel(r'$\hat{\rho}(\tau)$')
    axs[1].grid(True)

    # Tercer plot = PACF
    plot_pacf(df['retorno'].dropna(), ax=axs[2])
    axs[2].set_title('PACF')
    axs[2].set_xlabel(r'$\tau$')
    axs[2].set_ylabel(r'$\phi(\tau, \tau)$')
    axs[2].grid(True)

    plt.tight_layout()

    plt.savefig('ALGO.png', format='PNG')
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG')
    plt.close()

    # Obtener la imagen del buffer
    buffer.seek(0)
    grafica_acf_pacf = base64.b64encode(buffer.read()).decode()

    return grafica_acf_pacf


@login_required
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
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento, datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia, order, ticker)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_auto.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario_arima(form, ticker, request)
    return render(request, "arima_auto.html", context)


@login_required
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
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento, datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia, order, ticker)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_rejilla.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario_arima(form, ticker, request)
    return render(request, "arima_rejilla.html", context)


@login_required
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
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento, datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia, order, ticker)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_manual.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario_arima(form, ticker, request)
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
    context = _comprobar_formulario_arima(form, ticker, request)

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
        model = auto_arima(datos, seasonal=False, suppress_warnings=True)
        order = model.order

    if rejilla is True:
        # El mejor MSE es el menor MSE, lógicamente
        mejor_mse, mejor_order = math.inf, None
        for p in valores_p:
            for d in valores_d:
                for q in valores_q:
                    order = (p,d,q)
                    # En 'statsmodels', ARIMA utiliza internamente procedimientos de 
                    # optimización numérica para encontrar un conjunto de coeficientes 
                    # para el modelo. Estos procedimiento pueden fallar y lanzar una 
                    # excepción que se debe controlar. En este caso, hago que se continúe 
                    # con la evaluación
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


def _comprobar_formulario_arima(form, ticker, request):
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

    if isinstance(form, BuscarParametrosArimaForm):
        num_sesiones = request.POST.get('num_sesiones')
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
        return False
    
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


def _validacion_walk_forward_arima(tam_entrenamiento, datos, order):
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
    modelo_fit = None
    predicciones = []
    aciertos_tendencia = []

    datos_entrenamiento = datos[:tam_entrenamiento]
    datos_test = datos[tam_entrenamiento:]

    # Separo en 'conjunto_total' porque lo voy actualizando para los
    # subsecuentes análisis
    conjunto_total = list(datos_entrenamiento)

    # Validación 'walk-forward anchored'. Ojo, no se están cambiando los parátros
    # de ARIMA en cada recálculo, con lo cual, habrá sesgo.
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


def _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia, order, ticker):
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
        order (tuple): tupla con los valores (p, d, q).
        ticker (str): nombre del ticker con el que se va a trabajar.

    Returns:
        context (dict): diccionario con los datos del contexto.
    """
    datos_test = datos[tam_entrenamiento:]
    
    datos.index = fechas
    predicciones = pd.DataFrame(predicciones)
    predicciones.index = fechas[tam_entrenamiento:]

    ticker = ticker.replace("_", ".")
    ticker = ticker.replace("^", "")
    
    # Preparar figura y buffer con validadción walk-forward
    # -----------------------------------------------------
    plt.figure(figsize=(7, 5))
    # Gráfica con los datos reales y las predicciones
    plt.plot(datos.index, datos, color='blue', label='Original')
    plt.plot(predicciones.index, predicciones, color='red', label=f'Predicción últimos {len(datos_test)} días\n con validación "walk-forward"')
    plt.title(f'{ticker}')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    interval = 6 if len(datos) > 252 else 3
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    plt.legend()
    plt.grid()
    # Obtener los datos de la imagen del buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG')
    plt.close()
    # Obtener datos de la imagen desde el buffer
    buffer.seek(0)
    forecast_arima_walk_forward = base64.b64encode(buffer.read()).decode()
    #
    # Hago una predicción adicional para la próxima sesión
    prediccion = modelo_fit.forecast(steps=1)
    
    # Preparar figura y buffer con inetrvalos de confianza
    # ----------------------------------------------------
    datos_entrenamiento = list(datos[:tam_entrenamiento])
    # order[0], order[1], order[2]
    modelo = ARIMA(datos_entrenamiento, order=order)
    modelo_fit_2 = modelo.fit()
    # Por defecto, el forecast es de un step, así que lo adapto al tamaño de los datos de test
    res_forecast = modelo_fit_2.get_forecast(steps=len(datos_test))
    # Debido al proceso de diferenciación (I de ARIMA) es necesario ajustar los 
    # índices el número de datos. Cada vez que se diferencie habrá que asjustar los
    # tamaños (se elimina la primera fila del dataset) y por eso utilizo inicio como 'd'..
    # datos_entrenados = modelo_fit_2.predict(start=order[1], end=tam_entrenamiento-1, typ='levels')
    #
    # Calculo la predicción y los intervalos de confianza al 95% (alpha=0.05)
    forecast = res_forecast.predicted_mean
    confianzas = res_forecast.conf_int(alpha=0.05)
    # Gráfica con predicción directa de todos los días requeridos a la vez
    plt.plot(datos.index, datos, color='blue', label='Datos reales')
    # Aquí también ajusto al tamaño desde 'd' por la diferenciación
    # axes[1].plot(datos.index[d:tam_entrenamiento], datos_entrenados, color='green', label='Valores modelo entrenado')
    plt.plot(predicciones.index, forecast, color='red', label=f'Predicción últimos {len(datos_test)} días\n sin validación "walk-forward"')
    plt.title(f'{ticker}')
    plt.fill_between(predicciones.index, confianzas[:,0], confianzas[:,1], color='red', alpha=0.3, label='Intervalos de confianza')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    interval = 6 if len(datos) > 252 else 3
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    plt.legend()
    plt.grid()
    # Obtener los datos de la imagen del buffer
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='PNG')
    plt.close()
    # Obtener datos de la imagen desde el buffer
    buffer2.seek(0)
    forecast_arima_intervalos_conf = base64.b64encode(buffer2.read()).decode()

    # NOTA:
    #
    # # Se pueden ver los residuos y su densidad:
    # residuos = pd.DataFrame(modelo_fit.resid)
    # residuos.plot()
    # plt.savefig('linea_residuos.png', format="PNG")
    # # Gráfica de densidad de los residuos
    # residuos.plot(kind='kde')
    # plt.savefig('densidad_residuos.png', format="PNG")
    # # Resumen estadístico de los residuos
    # print(residuos.describe())

    # Comparar con una predicción Naïve
    # ---------------------------------
    # Simplemente establezco que el precio de cierre de hoy será el de mañana
    # y lo comparo con los datos reales de test (elimino el primer dato por el shift())
    naive_forecast = datos_test.shift(1)
    mse_naive = mean_squared_error(datos_test[1:], naive_forecast[1:])

    context = {
        "lista_tickers": tickers_disponibles(),
        "form": type(form),

        "forecast_arima_walk_forward": forecast_arima_walk_forward,
        "resumen": modelo_fit.summary(),
        "mse": mean_squared_error(datos_test, predicciones),
        "rmse": math.sqrt(mean_squared_error(datos_test, predicciones)),
        "prediccion_prox_sesion": prediccion[0],
        "aciertos_tendencia": aciertos_tendencia.count(True),
        "fallos_tendencia": aciertos_tendencia.count(False),

        "forecast_arima_intervalos_conf": forecast_arima_intervalos_conf,
        "mse_2": mean_squared_error(datos_test, forecast),
        "rmse_2": math.sqrt(mean_squared_error(datos_test, forecast)),
        "rmse_naive": math.sqrt(mse_naive)
    }
    return context


@login_required
def lstm(request):
    """Para crear una red neuronal LSTM. 
    
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
            "form": LstmForm,
        }
        return render(request, "lstm.html", context)

    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")

    # Uso el resto del formulario (sin el ticker)
    form = LstmForm(request.POST)
    if form.is_valid():
        # Hago un preprocesado para adaptar los datos
        look_back, X_norm, y_norm, df, tam_entrenamiento, scaler = _preprocesado_lstm(ticker, form, request)

        # Obtengo el modelo de la red LSTM (ya compilado y entrenado)
        modelo = _crear_modelo(look_back, X_norm, y_norm)
        
        # Hago una validación diaria para los datos de test
        predicciones, aciertos_tendencia = _validacion_walk_forward_lstm(df, tam_entrenamiento, scaler, look_back, modelo)

        # Generar un contexto con datos relevantes
        context = _generar_resultados_lstm(form, scaler, look_back, modelo, predicciones, tam_entrenamiento, df, aciertos_tendencia)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "lstm.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario_lstm(form, ticker, request)
    return render(request, "lstm.html", context)


def _preprocesado_lstm(ticker, form, request):
    """Para preprocesar la información y no saturar de código los
    métodos de LSTM. 

    Args:
        ticker (str): nombre del ticker. 
        form (Lab.forms.Form): formulario utilizado para recabar datos. 
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        look_back (int): número de time_steps que se hacen hacia atrás. 
        X_norm (numpy.ndarray): datos de entrada de la red. 
        y_norm (numpy.ndarray): datos esperados en la salida de la red. 
        df (pandas.core.frame.DataFrame): conjunto total de datos (entrenamiento
            y test) con sólo cierres del valor seleccionado. 
        tam_entrenamiento (int): tamaño de los datos dedicados a entrenamiento.
        scaler (sklearn.preprocessing._data.MinMaxScaler): scaler para normalizar en [0,1].
    """
    # Obtengo datos del form
    num_sesiones = form.cleaned_data['num_sesiones']
    porcentaje_entren = form.cleaned_data['porcentaje_entrenamiento']

    # Compruebo existencia de ticker
    context = _comprobar_formulario_lstm(form, ticker, request)

    if context is not False:
        # Si hay datos en el contexto es porque algo está mal y se
        # añade un mensaje informativo al usuario
        return render(request, "lstm.html", context)
        
    # Busco la info para el nº de sesiones indicado por ususario
    modelo = apps.get_model('Analysis', ticker)
    bd = obtener_nombre_bd(ticker)
    entrada = modelo.objects.using(bd).order_by('-date')[:num_sesiones]
    df = pd.DataFrame(list(entrada.values()))
    # Y ordeno el resultado
    df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

    datos = df['close']

    # Split 70/30 o lo que sea (uso el % indicado por el usuario adaptándolo)
    porcentaje_entren = int(porcentaje_entren.replace('%', ''))/100
    tam_entrenamiento = int(len(datos) * porcentaje_entren)

    # Nº de días previos para usar como input
    look_back = 1
    # Columna con los datos del día siguiente para usar como salida
    # esperada de la red. Es decir, se va a transformar una serie temporal
    # en un problema de aprendizaje supervisado
    df['siguiente_dia'] = df['close'].shift(-1)
    # Elimino el último cierre porque no habrá un resultado del siguiente
    # día (será NaN, lógicamente). Lo puedo estimar a posteriori
    df.dropna(inplace=True)
    # print(df[['date','close', 'siguiente_dia']])

    # Creo los datasets
    datos_entrenamiento = df[:tam_entrenamiento]
    
    # X = input cierres / y = output días siguientes
    X = datos_entrenamiento['close'].values[:-1]
    y = datos_entrenamiento['siguiente_dia'].values[:-1]
    
    # Redimensionar para ajustar a valores esperados en la capa de 
    # entrada de la red LSTM [samples, time_steps, features].
    # samples: nº de secuencias en el dataset (uso -1 para que Numpy 
    #          lo busque automáticamente según el tamaño de la entrada)
    #          1 secuencia por día. 
    # time_steps: nº de días previos a considerar en cada secuencia
    # features: nº de variables en cada día previo (time_step)
    X = X.reshape(-1, look_back, 1)

    # En LSTM es recomendable normalizar los datos
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_norm = scaler.fit_transform(X.reshape(-1, 1))
    # El scaler usará la misma escala que la que tenga X, por eso
    # uso transform y no fit_transform (el final, son los mismos datos
    # pero con un día de retraso)
    y_norm = scaler.transform(y.reshape(-1, 1))

    return look_back, X_norm, y_norm, df, tam_entrenamiento, scaler


def _crear_modelo(look_back, X_norm, y_norm):
    """Para crear el modelo de la red, compilarla y entrenarla. 
    Devuelve el modelo de la red ya entrenado. 

    Args:
        look_back (int): número de time_steps que se hacen hacia atrás. 
        X_norm (numpy.ndarray): datos de entrada de la red. 
        y_norm (numpy.ndarray): datos esperados en la salida de la red. 
    
    Returns:
        modelo (keras.src.models.sequential.Sequential): modelo de la red LSTM.
    """
    # Para crear capa a capa de forma secuencial (cada capa 
    # adicional se conecta a la anterior)
    modelo = Sequential()
    # Añadir la capa de LSTM (RNN) con 5 LSTM unit (5 neuronas), con
    # forma de (1, look_back). Las secuencias de entrada serán 
    # de longitud look_back (time_steps), i.e, los días que se mira 
    # hacia atrás en los datos para estimar la misma cantidad de días. 
    # Y sólo hay una variable que es el propio cierre
    modelo.add(LSTM(units=5, input_shape=(1, look_back)))
    # Añadir capa d esalida, completamente conectada, de 1 neurona
    modelo.add(Dense(units=1))

    # Compilar y entrenar
    modelo.compile(loss='mean_squared_error', optimizer='adam')
    # batch_size: nº de muestras que se procesan cada vez antes de ajustar
    #             los pesos de la red, i.e., factor del tamaño de los 
    #             conjuntos de datos de entrenamiento y prueba.
    # shuffle: desactivar la reproducción aleatoria de muestras 
    modelo.fit(X_norm, y_norm, epochs=100, batch_size=1, verbose=0, shuffle=False)

    return modelo


def _comprobar_formulario_lstm(form, ticker, request):
    """Permite comprobar si los datos introducidos por
    el usuario en cualquiera de los formularios disponibles
    son coherentes.

    Args:
        form (Lab.forms.Form): formulario que se quiere comrpobar. 
        ticker (str): nombre del ticker.
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

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
        if not 400 <= num_sesiones <= 1000:
            context["msg_error"] = 'Valor no válido para el nº de sesiones'
            return context
    else:
        context["msg_error"] = 'Valor no válido para el nº de sesiones'
        return context

    if porcentaje_entren not in ['50%', '66%', '70%', '80%', '90%']:
        context["msg_error"] = 'Porcentaje indicado no válido'
        return context

    # Si no hay errores
    return False


def _validacion_walk_forward_lstm(df, tam_entrenamiento, scaler, look_back, modelo):
    """Para realizar la validación basada en el MSE. Se realiza 
    una validación de un paso hacia atrás, i.e., se comprueba el
    error cuadrático medio (mse) cometido entre la predicción
    para el día siguiente y el resultado real de cierre en ese día.      

    Args:
        df (pandas.core.frame.DataFrame): conjunto total de datos (entrenamiento
            y test) con sólo cierres del valor seleccionado. 
        tam_entrenamiento (int): tamaño de los datos dedicados a entrenamiento. 
        scaler (sklearn.preprocessing._data.MinMaxScaler): scaler para normalizar en [0,1].
        look_back (int): número de time_steps que se hacen hacia atrás. 
        modelo (keras.src.models.sequential.Sequential): modelo de la red LSTM.

    Returns:
        predicciones (lista): lista con predicciones realizadas. 
        aciertos_tendencia (list): cantidad de aciertos/fallos en la predicción
            con los datos de test.
    """
    datos_test = df[tam_entrenamiento:]
    datos_entrenamiento = df[:tam_entrenamiento]
    predicciones = []
    aciertos_tendencia = []
    acierta_tendencia = None

    for t in range(len(datos_test)):
        # Adaptar forma y normalizar el nuevo dato de test
        X_test = datos_test['close'].values[t].reshape(1, look_back, 1)
        X_test_norm = scaler.transform(X_test.reshape(-1, 1))
        
        # Predicción del siguiente time_step (1 día)
        predic_normalizada = modelo.predict(X_test_norm)
        # Paso a su escala real (la de precios de cierre)
        estimado = scaler.inverse_transform(predic_normalizada)[0][0]
        predicciones.append(estimado)
        
        if t>0:
            previo = datos_test['siguiente_dia'].iloc[t-1]
        else:
            # Cuando t=0 el dato anterior corresponde a los de entrenamiento
            previo = datos_entrenamiento['siguiente_dia'].iloc[-1]

        # Comprobación de aciertos vs fallos para mostrar al usuario
        # El dato real es el que está en datos_test en el siguiente día
        real = datos_test['siguiente_dia'].iloc[t]
        #
        if (previo < estimado and previo < real) or (previo > estimado and previo > real) or (previo == estimado and previo == real):
            acierta_tendencia = True
        else:
            acierta_tendencia = False

        aciertos_tendencia.append(acierta_tendencia)

    return predicciones, aciertos_tendencia


def _generar_resultados_lstm(form, scaler, look_back, modelo, predicciones, tam_entrenamiento, df, aciertos_tendencia):
    """Para generar los resultados gráficos y textuales
    que se mostrarán al usuario en la plantilla HTML para
    informarle sobre los resultados de una red LSTM.

    Args:
        form (Lab.forms.Form): formulario creado para recabar información. 
        scaler (sklearn.preprocessing._data.MinMaxScaler): scaler para normalizar en [0,1].
        look_back (int): número de time_steps que se hacen hacia atrás. 
        modelo (keras.src.models.sequential.Sequential): modelo de la red LSTM.
        predicciones (list): lista con las predicciones realizadas. 
        tam_entrenamiento (int): tamaño de los datos dedicados a entrenamiento. 
        df (pandas.core.frame.DataFrame): conjunto total de datos (entrenamiento
            y test) con sólo cierres del valor seleccionado. 
        aciertos_tendencia (list): cantidad de aciertos/fallos en la predicción
            con los datos de test. 

    Returns:
        context (dict): diccionario con los datos del contexto.
    """
    datos_test = df[tam_entrenamiento:]
    datos = df['close']
    fechas = df['date']
    datos.index = fechas
    predicciones = pd.DataFrame(predicciones)
    # Resto un día porque hay una estimación menos por los datos
    # de test. La predicción adicional se calcula a posteriori
    predicciones.index = fechas[tam_entrenamiento:]

    # Preparar figura y buffer
    plt.figure(figsize=(7, 5))
    buffer = BytesIO()
    # Gráfica con los datos reales y las predicciones
    plt.plot(datos.index, datos, color='blue', label='Original')
    plt.plot(predicciones.index, predicciones, color='red', label=f'Predicción últimos {len(predicciones)} días')
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.legend()
    
    plt.savefig(buffer, format='PNG')
    plt.close()
    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    forecast_lstm = base64.b64encode(buffer.read()).decode()

    # Hago una predicción adicional con el último dato de test
    X_test = datos_test['close'].iloc[-1].reshape(1, look_back, 1)
    X_test_norm = scaler.transform(X_test.reshape(-1, 1))
    predic_normalizada = modelo.predict(X_test_norm)
    prediccion = scaler.inverse_transform(predic_normalizada)[0][0]

    # Creao un objeto StringIO para 'capturar' la salida
    buffer_resumen_modelo = StringIO()
    # Redirijo la salida a mi buffer
    sys.stdout = buffer_resumen_modelo
    # Resumen del modelo
    modelo.summary()
    # Reseteo la salida estándar
    sys.stdout = sys.__stdout__

    context = {
        "lista_tickers": tickers_disponibles(),
        "form": type(form),
        "forecast_lstm": forecast_lstm,
        "resumen": buffer_resumen_modelo.getvalue(),
        "mse": mean_squared_error(datos_test['siguiente_dia'], predicciones),
        "rmse": math.sqrt(mean_squared_error(datos_test['siguiente_dia'], predicciones)),
        "prediccion_prox_sesion": prediccion,
        "aciertos_tendencia": aciertos_tendencia.count(True),
        "fallos_tendencia": aciertos_tendencia.count(False),
    }

    return context