"""
Métodos de vistas para usar con Lab.
"""
import sys
import base64
import os
# Para el buffer y las imágenes
from io import BytesIO, StringIO
import math
import warnings
# Para pasar str a literales
import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Para evitar todos los warnings de convergencia y de datos no estacionarios
from django.shortcuts import render
from django.apps import apps
# Para proteger rutas. Las funciones que tienen este decorador
# sólo son accesibles si se está logueado
from django.contrib.auth.decorators import login_required
# Para usar django-pandas y frames
from django_pandas.io import read_frame
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pmdarima.arima import auto_arima
# Keras utiliza la librería oneAPI Deep Neural Network Library (oneDNN)
# https://stackoverflow.com/questions/77921357/warning-while-using-tensorflow-tensorflow-core-util-port-cc113-onednn-custom
# para optimizar el rendimiento en arquitecturas Intel, pero arroja
# un warning constantemente. Para eliminarlo:
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from keras.models import Sequential
from keras.layers import Dense, LSTM
from util.tickers.Tickers_BDs import obtener_nombre_bd, tickers_disponibles
# Mis formularios
from .forms import FormBasico, ArimaAutoForm, ArimaRejillaForm, ArimaManualForm, EstrategiaMLForm, LstmForm
# from sklearn.metrics import confusion_matrix
# Para evitar warnings al aplicar los modelos ARIMA
warnings.filterwarnings("ignore")



@login_required
def lab(request):
    """Para mostrar los modelos disponibles que se
    pueden aplicar. El usuario verá la vista de 'lab.html'
    con la información necesaria. 

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'lab.html' con datos de contexto.
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

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest)
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render)
            Renderiza la plantilla 'buscar_paramateros_arima.html' con datos
            de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": FormBasico,
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
    form = FormBasico(request.POST)
    if form.is_valid():
        # Compruebo existencia de ticker y num_sesiones
        context = _comprobar_formularios(form, ticker, request)

        if context is not False:
            return render(request, "buscar_paramateros_arima.html", context)

        num_sesiones = form.cleaned_data['num_sesiones']

        model = apps.get_model('Analysis', ticker)
        bd = obtener_nombre_bd(ticker)
        entradas = model.objects.using(bd).order_by('-date')[:num_sesiones]
        df = read_frame(entradas.values('date', 'close', 'ticker', 'name'))

        df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

        # Calculo la diferenciación logarítmica y obtengo las gráficas oportunas
        graf_1 = _diferenciacion_logaritmica(df, 1)
        graf_2 = _diferenciacion_logaritmica(df, 2)
        graf_3 = _diferenciacion_logaritmica(df, 3)

        context = {
            'form': FormBasico(),
            "lista_tickers": tickers_disponibles(),
            'graf_1': graf_1,
            'graf_2': graf_2,
            'graf_3': graf_3,
        }
        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "buscar_paramateros_arima.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formularios(form, ticker, request)
    return render(request, "buscar_paramateros_arima.html", context)


def _diferenciacion_logaritmica(df, d):
    """Para hacer una diferenciación logarítmica como se haría de forma manual,
    para hacer la serie estacionaria y que podamos aplicar las funciones ACF y PACF. 
    Además, genera las gráficas necesarias para que el usuario interprete los datos. 

    Parameters
    ----------
        df : pandas.core.frame.DataFrame)
            Conjunto total de datos. 

        d : int
            Orden de diferenciación (la I_(d) de ARIMA).

    Returns
    -------
        grafica_acf_pacf : str
            Imagen con las gráficas de diferenciación de cierres, ACF y PACF.
    """
    log_close = np.log(df['close'])
    df['retorno'] = log_close.diff(d)

    nombre = df['ticker'].iloc[0]
    nombre = nombre.replace("_", ".")
    nombre = nombre.replace("^", "")

    _, axs = plt.subplots(1, 3, figsize=(15, 5))
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

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'arima_auto.html' con datos de contexto.
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
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento,
                                                                                          datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento,
                                                datos, aciertos_tendencia, order, ticker)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_auto.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formularios(form, ticker, request)
    return render(request, "arima_auto.html", context)


@login_required
def arima_rejilla(request):
    """Para mostrar el resultado de un modelo ARIMA
    cuyos parámetros (p,d,q) son calculados a través de 
    una búsqueda por rejilla predefinida por el usuario. 

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'arima_rejilla.html' con datos 
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
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento,
                                                                                          datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones,
                                                tam_entrenamiento, datos, aciertos_tendencia, order, ticker)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_rejilla.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formularios(form, ticker, request)
    return render(request, "arima_rejilla.html", context)


@login_required
def arima_manual(request):
    """Para mostrar el resultado de un modelo ARIMA
    cuyos parámetros (p,d,q) son conocidos por el usuario. 

    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'arima_manual.html' con datos
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
            modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento,
                                                                                          datos, order)

            # Generar la gráfica y texto con el forecast en los datos de test
            context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones,
                                                tam_entrenamiento, datos, aciertos_tendencia, order, ticker)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "arima_manual.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formularios(form, ticker, request)
    return render(request, "arima_manual.html", context)


def _preprocesar_p_d_q(ticker, form, request):
    """Para preprocesar la información y no saturar de código los
    métodos de ARIMA. 

    Parameters
    ----------
        ticker : str
            Nombre del ticker. 
        
        form : Lab.forms.Form
            Formulario utilizado para recabar datos. 

        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Tuple: Tupla con información relevante para modelar
            * order : tuple
                Tupla con los parámetros (p, d, q)
            * fechas : pandas.core.series.Series
                Fechas asociadas a los precios de cierre que hay en 'datos'.
            * tam_entrenamiento : int
                Tamaño de los datos (%) dedicados a entrenamiento. 
            * datos : pandas.core.series.Series
                Conjunto total de datos (entrenamiento y test) con los 
                cierres del valor seleccionado.
            * context : dict / None
                Diccionario con los datos del contexto o None en caso de 
                que no haya errores en formulario. 
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
    context = _comprobar_formularios(form, ticker, request)

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

    Parameters
    ----------
        datos_entrenamiento : pandas.core.series.Series
            Datos de  entrenamiento del modelo. 

        datos_test : pandas.core.series.Series
            Datos para testear el modelo. 

        order : tuple
            Tupla con los parámetros (p, d, q)

    Returns
    -------
        mse : numpy.float64
            Error cuadrático medio calculado entre los datos 
            reales (datos_test) y las predicciones. 
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


def _comprobar_formularios(form, ticker, request):
    """Permite comprobar si los datos introducidos por
    el usuario en cualquiera de los formularios disponibles
    son coherentes.

    Parameters
    ----------
        bd : str
            Nombre de la base de datos.

        ticker : str
            Nombre del ticker.

        num_sesiones : int
            Número de sesiones que se quieren analizar. 

        porcentaje_entren : int
            Porcentaje de datos para el entrenamiento del modelo.

        caso : int
            Indicador del caso a tratar.

    Returns
    -------
        Union[False, context]
            * False : bool
                Valor booleano.
            * context : dict
                Diccionario con datos del contexto.
    """
    # A partir de aquí se realiza la comprobación de resto de formularios.
    context = {
        "form": type(form),
        "lista_tickers": tickers_disponibles(),
    }
    bd = obtener_nombre_bd(ticker)

    # Este formulario es un poco distinto a los demás y requiere coprobarse completamente
    # por separado
    if isinstance(form, EstrategiaMLForm):
        context = {
            "form": type(form),
        }
        num_sesiones = request.POST.get('num_sesiones')
        porcentaje_entren = request.POST.get('porcentaje_entrenamiento')
        tipo_modelo = request.POST.get('tipo_modelo')
        # Comprobación de casos
        if bd is None:
            context["msg_error"] = f'El ticker no está disponibe'
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
        if tipo_modelo not in ['Regresión lineal', 'Clasificación']:
            context["msg_error"] = 'Modelo indicado no válido'
            return context
        return False

    # El resto de formularios tienen campos en común
    if isinstance(form, FormBasico):
        num_sesiones = request.POST.get('num_sesiones')
        # Comprobación de casos
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
    # Comprobación de casos comunes
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
        # Comprobación de casos
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
        # Comprobación de casos
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

    Parameters
    ----------
        tam_entrenamiento : int
            Tamaño de los datos (%) dedicados a entrenamiento. 

        datos : pandas.core.series.Series
            Conjunto total de datos (entrenamiento y test) con los 
            cierres del valor seleccionado. 

        order : tuple
            Tupla con los valores (p, d, q).

    Returns
    -------
        Tuple: Tupla con información relevante para modelar
            * modelo_fit : statsmodels.tsa.arima.model.ARIMAResultsWrapper
                Modelo. 
            * aciertos_tendencia : list
                Cantidad de aciertos/fallos en la predicción con los datos de test.
            * predicciones : lista
                Lista con predicciones realizadas. 
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


def _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos,
                              aciertos_tendencia, order, ticker):
    """Para generar los resultados gráficos y textuales
    que se mostrarán al usuario en la plantilla HTML para
    informarle sobre los resultados del modelo ARIMA elegido.

    Parameters
    ----------
        form : Lab.forms.Form
            Formulario creado para recabar información. 

        modelo_fit : statsmodels.tsa.arima.model.ARIMAResultsWrapper
            Modelo. 

        fechas : pandas.core.series.Series
            Fechas asociadas a los precios de cierre que hay en 'datos'.

        predicciones : list
            Lista con las predicciones realizadas. 

        tam_entrenamiento : int
            Tamaño de los datos dedicados a entrenamiento. 

        datos : pandas.core.series.Series
            Conjunto total de datos (entrenamiento y test) con los 
            cierres del valor seleccionado. 

        aciertos_tendencia : list
            Cantidad de aciertos/fallos en la predicción con los datos de test. 

        order : tuple
            Tupla con los valores (p, d, q).

        ticker : str
            Nombre del ticker con el que se va a trabajar.

    Returns
    -------
        context : dict
            Diccionario con los datos del contexto.
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
    plt.plot(predicciones.index, predicciones, color='red',
             label=f'Predicción últimos {len(datos_test)} días\n con validación "walk-forward"')
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
    # prediccion = modelo_fit.forecast(steps=1)

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
    plt.plot(predicciones.index, forecast, color='red',
             label=f'Predicción últimos {len(datos_test)} días\n sin validación "walk-forward"')
    plt.title(f'{ticker}')
    plt.fill_between(predicciones.index, confianzas[:,0], confianzas[:,1],
                     color='red', alpha=0.3, label='Intervalos de confianza')
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
        # "prediccion_prox_sesion": prediccion[0],
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
    
    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'arima_auto.html' con datos de contexto.
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
        look_back, x_norm, y_norm, df, tam_entrenamiento, scaler = _preprocesado_lstm(ticker, form, request)

        # Obtengo el modelo de la red LSTM (ya compilado y entrenado)
        modelo = _crear_modelo(look_back, x_norm, y_norm)

        # Hago una validación diaria para los datos de test
        predicciones, aciertos_tendencia = _validacion_walk_forward_lstm(df, tam_entrenamiento, scaler,
                                                                         look_back, modelo)

        # Generar un contexto con datos relevantes
        context = _generar_resultados_lstm(form, scaler, look_back, modelo, predicciones,
                                           tam_entrenamiento, df, aciertos_tendencia)

        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "lstm.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formulario_lstm(form, ticker, request)
    return render(request, "lstm.html", context)


def _preprocesado_lstm(ticker, form, request):
    """Para preprocesar la información y no saturar de código los
    métodos de LSTM. 

    Parameters
    ----------
        ticker : str
            Nombre del ticker. 

        form : Lab.forms.Form
            Formulario utilizado para recabar datos. 

        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Tuple: Tupla con información relevante para modelar
            * look_back : int
                Número de time_steps que se hacen hacia atrás. 
            * X_norm : numpy.ndarray
                Datos de entrada de la red. 
            * y_norm : numpy.ndarray
                Datos esperados en la salida de la red. 
            * df : pandas.core.frame.DataFrame
                Conjunto total de datos (entrenamiento y test) con sólo 
                cierres del valor seleccionado. 
            * tam_entrenamiento : int
                Tamaño de los datos dedicados a entrenamiento.
            * scaler : sklearn.preprocessing._data.MinMaxScaler
                Scaler para normalizar en [0,1].
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

    # x = input cierres / y = output días siguientes
    x = datos_entrenamiento['close'].values[:-1]
    y = datos_entrenamiento['siguiente_dia'].values[:-1]

    # Redimensionar para ajustar a valores esperados en la capa de
    # entrada de la red LSTM [samples, time_steps, features].
    # samples: nº de secuencias en el dataset (uso -1 para que Numpy
    #          lo busque automáticamente según el tamaño de la entrada)
    #          1 secuencia por día.
    # time_steps: nº de días previos a considerar en cada secuencia
    # features: nº de variables en cada día previo (time_step)
    x = x.reshape(-1, look_back, 1)

    # En LSTM es recomendable normalizar los datos
    scaler = MinMaxScaler(feature_range=(0, 1))
    x_norm = scaler.fit_transform(x.reshape(-1, 1))
    # El scaler usará la misma escala que la que tenga X, por eso
    # uso transform y no fit_transform (el final, son los mismos datos
    # pero con un día de retraso)
    y_norm = scaler.transform(y.reshape(-1, 1))

    return look_back, x_norm, y_norm, df, tam_entrenamiento, scaler


def _crear_modelo(look_back, x_norm, y_norm):
    """Para crear el modelo de la red, compilarla y entrenarla. 
    Devuelve el modelo de la red ya entrenado. 

    Parameters
    ----------
        look_back : int
            Número de time_steps que se hacen hacia atrás. 

        x_norm : numpy.ndarray
            Datos de entrada de la red. 

        y_norm : numpy.ndarray
            Datos esperados en la salida de la red. 
    
    Returns
    -------
        modelo : keras.src.models.sequential.Sequential)
            Modelo de la red LSTM.
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
    modelo.fit(x_norm, y_norm, epochs=100, batch_size=1, verbose=None, shuffle=False)

    return modelo


def _comprobar_formulario_lstm(form, ticker, request):
    """Permite comprobar si los datos introducidos por
    el usuario en cualquiera de los formularios disponibles
    son coherentes.

    Parameters
    ----------
        form : Lab.forms.Form
            Formulario que se quiere comrpobar. 

        ticker : str
            Nombre del ticker.

        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        Union[False, context]
            * False : bool
                Valor booleano.
            * context : dict
                Diccionario con datos del contexto.
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

    Parameters
    ----------
        df : pandas.core.frame.DataFrame
            Conjunto total de datos (entrenamiento y test) con sólo 
            cierres del valor seleccionado. 

        tam_entrenamiento : int
            Tamaño de los datos dedicados a entrenamiento. 

        scaler : sklearn.preprocessing._data.MinMaxScaler
            Scaler para normalizar en [0,1].

        look_back : int
            Número de time_steps que se hacen hacia atrás. 

        modelo : keras.src.models.sequential.Sequential
            Modelo de la red LSTM.

    Returns
    -------
        Tuple: Tupla con predicciones e indicadores de acierto
            * predicciones : lista
                Lista con predicciones realizadas. 
            * aciertos_tendencia : list
                Cantidad de aciertos/fallos en la predicción con 
                los datos de test.
    """
    datos_test = df[tam_entrenamiento:]
    datos_entrenamiento = df[:tam_entrenamiento]
    predicciones = []
    aciertos_tendencia = []
    acierta_tendencia = None

    for t in range(len(datos_test)):
        # Adaptar forma y normalizar el nuevo dato de test
        x_test = datos_test['close'].values[t].reshape(1, look_back, 1)
        x_test_norm = scaler.transform(x_test.reshape(-1, 1))

        # Predicción del siguiente time_step (1 día)
        predic_normalizada = modelo.predict(x_test_norm, verbose=None)
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

    Parameters
    ----------
        form : Lab.forms.Form
            Formulario creado para recabar información. 

        scaler : sklearn.preprocessing._data.MinMaxScaler
            Scaler para normalizar en [0,1].

        look_back : int
            Número de time_steps que se hacen hacia atrás. 

        modelo : keras.src.models.sequential.Sequential
            Modelo de la red LSTM.

        predicciones : list
            Lista con las predicciones realizadas. 

        tam_entrenamiento : int
            Tamaño de los datos dedicados a entrenamiento. 

        df : pandas.core.frame.DataFrame
            Conjunto total de datos (entrenamiento y test) con sólo 
            cierres del valor seleccionado. 

        aciertos_tendencia : list
            Cantidad de aciertos/fallos en la predicción con los datos 
            de test. 

    Returns
    -------
        context : dict
            Diccionario con los datos del contexto.
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
    x_test = datos_test['close'].iloc[-1].reshape(1, look_back, 1)
    x_test_norm = scaler.transform(x_test.reshape(-1, 1))
    predic_normalizada = modelo.predict(x_test_norm, verbose=None)
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


@login_required
def cruce_medias(request):
    """Para implementar el algoritmo de seguimiento de tendencias o cruce de medias. 
    
    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'arima_auto.html' con datos
            de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": FormBasico,
        }
        return render(request, "cruce_medias.html", context)

    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")
    nombre_ticker = ticker
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")

    # Uso el resto del formulario (sin el ticker)
    form = FormBasico(request.POST)
    if form.is_valid():
        # Compruebo existencia de ticker y num_sesiones
        context = _comprobar_formularios(form, ticker, request)
        if context is not False:
            return render(request, "cruce_medias.html", context)

        num_sesiones = form.cleaned_data['num_sesiones']

        # Obtengo los datos de las últimas sesiones
        model = apps.get_model('Analysis', ticker)
        bd = obtener_nombre_bd(ticker)
        entradas = model.objects.using(bd).order_by('-date')[:num_sesiones]
        df = read_frame(entradas.values('date', 'close', 'ticker', 'name'))
        # Ordeno el df para calcular los retornos logarítmicos y adecuarlo
        # a lo explicado en los conceptos teóricos
        df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

        # Aplico el algoritmo de seguimiento de tendencia o cruce de medias
        df, mms_len, mms_rap = _algoritmo_cruce_medias_automaticas(df)

        retorno_log_total_algo = df['retorno_log_algoritmo'].sum()
        # Calculo el retorno logarítmico como si se hubiera seguido
        # una estrategia de comprar y mantener desde la fecha del análisis
        retorno_log_total = df['retorno_log'].sum()

        df_resultados = _resultados_cruce_medias(df)
        cruce_medias_var = _generar_figura_cruce_medias(df, nombre_ticker, mms_len, mms_rap)

        context = {
            'form': FormBasico(),
            "lista_tickers": tickers_disponibles(),
            'cruce_medias': cruce_medias_var,
            'retorno_log_total_algo': retorno_log_total_algo,
            'retorno_log_total': retorno_log_total,
            'sharpe_retorno_log_algo': df['retorno_log_algoritmo'].mean() / df['retorno_log_algoritmo'].std(), 
            'sharpe_retorno_log': df['retorno_log'].mean() / df['retorno_log'].std(), 

            'df_resultados': df_resultados,
            'porcentaje_algo': df_resultados['porcentaje'].sum(),
            'porcentaje_manteniendo': (df.iloc[-1]['close'] - df.iloc[0]['close']) / df.iloc[0]['close'] * 100,
        }
        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "cruce_medias.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formularios(form, ticker, request)
    return render(request, "cruce_medias.html", context)


def _algoritmo_cruce_medias_automaticas(df):
    """Para aplicar el algoritmo de cruce de medias (o seguimiento de
    tendencia).

    Parameters
    ----------
        df : pandas.core.frame.DataFrame
            Conjunto de datos de las últimas sesiones de un valor.

    Returns
    -------
        Tuple: Tupla con datos de las medias
            * mejor : pandas.core.frame.DataFrame
                Conjunto de datos de las últimas sesiones de un valor junto
                con los mejores retornos posibles según el algoritmo.
            * mms_len : int
                Valor de la mejor media lenta.
            * mms_rap : int
                Valor de la mejor media rápida.
    """
    # Para realizar una búsqueda por rejilla que permita obtener las mejores
    # MMS (lenta y rápida). Se incluyen medias típicas de análisis técnico
    lista_mms_lenta = [30, 50, 200]
    lista_mms_rapida = [10, 15, 20, 50]

    mms_len = 0
    mms_rap = 0
    mejor = None
    mejor_retorno = -np.inf

    for mms_l in lista_mms_lenta:
        for mms_r in lista_mms_rapida:
            if mms_l != mms_r:
                df['MMS_len'] = df['close'].rolling(mms_l).mean()
                df['MMS_rap'] = df['close'].rolling(mms_r).mean()

                df['retorno_log'] = np.log(df['close']).diff()
                # Para alinearlo con los comandos de compra/venta que se crean más
                # adelante. Al hacer esto se pierde el último valor del df
                df['retorno_log'] = df['retorno_log'].shift(-1)

                # Inicializo la columna 'senal' con 0
                df['senal'] = 0

                # Creo una máscara que detecte cuando las dos medias empiezan a tener valores
                mascara = df['MMS_len'].notna()
                # Calculo la columna de señal aplicando la máscara
                df.loc[mascara, 'senal'] = np.where(df.loc[mascara, 'MMS_rap'] >= df.loc[mascara, 'MMS_len'], 1, 0)

                # Y hago las operaciones oportunas para las indicaciones de compra/venta
                df['senal_prev'] = df['senal'].shift(1)
                # MMS_rap < MMS_len , cambia a:  MMS_rap > MMS_len
                df['comprar'] = (df['senal_prev'] == 0) & (df['senal'] == 1)
                # MMS_rap > MMS_len , cambia a:  MMS_rap < MMS_len
                df['vender'] = (df['senal_prev'] == 1) & (df['senal'] == 0)

                # Calculo el estado invertido/no invertido
                df['invertido'] = False
                invertido = False
                for i in range(len(df)):
                    if invertido and df.loc[i, 'vender']:
                        invertido = False
                    if not invertido and df.loc[i, 'comprar']:
                        invertido = True
                    df.loc[i, 'invertido'] = invertido

                # Calculo el retorno logarítmico total según el algoritmo
                df['retorno_log_algoritmo'] = df['invertido'] * df['retorno_log']

                ret_log_algo = df['retorno_log_algoritmo'].sum()

                # Actualizo el mejor en caso de que el retorno sea mayor
                if ret_log_algo > mejor_retorno:
                    mejor_retorno = ret_log_algo
                    mejor = df.copy()
                    mms_len = mms_l
                    mms_rap = mms_r

    return mejor, mms_len, mms_rap


def _resultados_cruce_medias(df):
    """Para generar un DataFrame con algunos resultados relevantes que se mostrarán al 
    usuario. 

    Parameters
    ----------
        df : pandas.core.frame.DataFrame
            Conjunto de datos de las últimas sesiones de un valor junto
            con los mejores retornos posibles según el algoritmo.

    Returns
    -------
        df_resultados : pandas.core.frame.DataFrame
            Conjunto de datos de resultados.
    """
    df_resultados = pd.DataFrame(columns=['fecha_compra', 'fecha_venta', 'cierre_compra', 'cierre_venta', 'pordentaje'])
    i = 0
    for _, r in df.iterrows():
        if r['comprar']:
            df_resultados.loc[i, 'fecha_compra'] = r['date']
            df_resultados.loc[i, 'cierre_compra'] = r['close']
        if r['vender']:
            df_resultados.loc[i, 'fecha_venta'] = r['date']
            df_resultados.loc[i, 'cierre_venta'] = r['close']
            # Tras la primera venta se incrementa i
            i += 1

    # Si se sigue invertido no habrá precio de venta, así que se usa el
    # último cierre del valor
    if pd.isnull(df_resultados.iloc[-1]['fecha_venta']):
        df_resultados.iloc[-1]['fecha_venta'] = df.iloc[-1]['date']
        df_resultados.iloc[-1]['cierre_venta'] = df.iloc[-1]['close']

    # Puede haberse recibido una señal de venta sin haber compra, entonces,
    # quedará un NaN en la fecha precios de compra. Como tiene valor, se elimina
    if pd.isnull(df_resultados.iloc[0]['fecha_compra']):
        df_resultados = df_resultados.drop(0)

    # Calculos los porcentajes
    df_resultados['porcentaje'] = (df_resultados['cierre_venta'] -
                                   df_resultados['cierre_compra']) / df_resultados['cierre_compra'] * 100

    return df_resultados


def _generar_figura_cruce_medias(df, nombre_ticker, mms_len, mms_rap):
    """Para generar la figura del algoritmo de seguimiento de tendencia o cruce de medias. 

    Parameters
    ----------
        df : pandas.core.frame.DataFrame
            Conjunto de datos de las últimas sesiones de un valor junto
            con los mejores retornos posibles según el algoritmo.

        nombre_ticker : str
            Nombre del ticker del valor sobre el que se aplica el algoritmo.
            
        mms_len : int 
            Media móvil simple lenta.

        mms_rap : int
            Media móvil simple rápida.

    Returns
    -------
        cruce_medias_var : str
            Cadena de datos que guarda la gráfica con el cruce de medias.
    """
    # Preparar figura y buffer
    plt.figure(figsize=(7, 5))

    # Gráfica con los datos reales y las predicciones
    plt.plot(df['date'], df['close'], color='blue', label='Precios de cierre')
    plt.plot(df['date'], df['MMS_len'], color='green', label=f'MMS{mms_len} (lenta)')
    plt.plot(df['date'], df['MMS_rap'], color='orange', label=f'MMS{mms_rap} (rápida)')
    plt.title(f'{nombre_ticker}')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    interval = 6 if len(df['close']) > 252 else 3
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    plt.legend()
    plt.grid()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG')
    plt.close()
    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    cruce_medias_var = base64.b64encode(buffer.read()).decode()

    return cruce_medias_var


@login_required
def estrategia_machine_learning(request):
    """Para implementar los mecanismos de trading con técnicas de 
    machine learning. 
    
    Parameters
    ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Solicitud HTTP encapsulada por Django.

    Returns
    -------
        : render
            Renderiza la plantilla 'arima_auto.html' con datos de contexto.
    """
    if request.method == 'GET':
        context = {
            "form": EstrategiaMLForm,
        }
        return render(request, "estrategia_basada_en_ML.html", context)

    indice = request.POST.get("indice")
    # En caso de valores fuera de rango no pasa nada porque se
    # hace otra comprobación al final y se manda un mensaje al usuario
    valores, clase, tickers_unidos = _obtener_tickers_relevantes(indice)

    # Uso el resto del formulario (sin el ticker)
    form = EstrategiaMLForm(request.POST)
    if form.is_valid():
        num_sesiones = form.cleaned_data['num_sesiones']
        tipo_modelo = form.cleaned_data['tipo_modelo']
        porcentaje_entren = form.cleaned_data['porcentaje_entrenamiento']

        # Compruebo ticker/indice, num_sesiones, tipo_modelo y porcentajes
        context = _comprobar_formularios(form, clase, request)
        if context is not False:
            return render(request, "estrategia_basada_en_ML.html", context)

        df_retornos, df_resultado, tam_entrenamiento, train, test = _preprocesado_datos_ml(tickers_unidos,
                                                                                           num_sesiones,
                                                                                           porcentaje_entren)

        x_train = train[valores]
        y_train = train[clase]
        x_test = test[valores]
        y_test = test[clase]

        if tipo_modelo == 'Regresión lineal':
            context = _regresion_lineal(LinearRegression(), x_train, y_train, x_test, y_test, df_retornos,
                                        tam_entrenamiento, clase, df_resultado, valores)
        elif tipo_modelo == 'Clasificación':
            # Se pasa C al modelo. C sirve para controlar lo que se conoce
            # como 'sanción de regularización'. Es una manera de controlar
            # los pesos, para que no sean demasiado grandes (lo que podría
            # resultar en un problema). C es la inversa de la fuerza de
            # regularización, i.e., C = 1/λ
            context = _clasificacion_regresion_logistica(LogisticRegression(C=10), x_train, y_train, x_test, y_test,
                                                         df_retornos, tam_entrenamiento, clase, df_resultado, valores)
        else:
            context = {
                'form': EstrategiaMLForm(),
            }
        # Si todo ha ido bien muestro la info. al usuario
        return render(request, "estrategia_basada_en_ML.html", context)

    # Si el formulario no es válido, busco el motivo e informo al usuario
    context = _comprobar_formularios(form, clase, request)
    return render(request, "estrategia_basada_en_ML.html", context)


def _obtener_tickers_relevantes(indice):
    """Para obtener los tickers relevantes de cada índice y el propio índice. 

    Parameters
    ----------
        indice : str
            Nombre del índice con el que se va a trabajar. 

    Returns
    -------
        Tuple : Tupla con información del índice
            * valores : list
                Lista de los valores que rerpesentan al índice.
            * clase : str
                Nombre del índice con el formato de guardado en BDs,
                esta será la clase objetivo.
            * tickers_unidos : list
                Lista con todos los tickers.
    """
    valores = []
    clase = None
    tickers_unidos = []

    if indice == 'DJ30':
        valores = ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM']
        clase = 'DJI'
    elif indice == 'IBEX35':
        valores = ['ITX_MC', 'IBE_MC', 'SAN_MC', 'BBVA_MC', 'CABK_MC']
        clase = 'IBEX'
    elif indice == 'FTSE100':
        valores = ['SHEL_L', 'AZN_L', 'HSBA_L', 'ULVR_L', 'BP_L']
        clase = 'FTSE'
    elif indice == 'DAX40':
        valores = ['SAP_DE', 'SIE_DE', 'ALV_DE', 'AIR_DE', 'DTE_DE']
        clase = 'GDAXI'

    tickers_unidos = valores.copy()
    tickers_unidos.append(clase)
    return valores, clase, tickers_unidos


def _preprocesado_datos_ml(tickers_unidos, num_sesiones, porcentaje_entren):
    """Para preparar los datos de la estrategia ML con el formato adecuado. 

    Parameters
    ----------
        tickers_unidos : list
            Lista con los tickers de los valores más relevantes
            y el índice sobre el que se va a hacer una estimación. 

        num_sesiones : int
            Número de sesiones a tener en cuenta para entrenar los modelos.

        porcentaje_entren : str
            Porcentaje de datos que se usará para entrenar los modelos.

    Returns
    -------
        Tuple: Tupla con información de resultados de preprocesado
            * df_retornos : pandas.core.frame.DataFrame)
                df con los retornos logarítmicos. 
            * df_resultado : pandas.core.frame.DataFrame
                df con los valores de precios de cierre.
            tam_entrenamiento : int
                Número de datos dedicados al entrenamiento del modelo. 
            * train : pandas.core.frame.DataFrame
                Subconjunto de entrenamiento de df_retornos. 
            * test : pandas.core.frame.DataFrame
                Subconjunto de test de df_retornos. 
    """
    df_resultado = pd.DataFrame(columns=tickers_unidos)
    for ticker in tickers_unidos:
        # Obtengo los datos de las últimas sesiones
        model = apps.get_model('Analysis', ticker)
        bd = obtener_nombre_bd(ticker)
        entradas = model.objects.using(bd).order_by('-date')[:num_sesiones]
        df = read_frame(entradas.values('date', 'close', 'ticker', 'name'))
        # Ordeno el df para calcular los retornos logarítmicos y adecuarlo
        # a lo explicado en los conceptos teóricos
        df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

        df_resultado[ticker] = df['close']

    # Como todos los valores cotizan en el mismo mercado, tendrán las
    # mismas fechas, así que me aprovecho de ello para añadir una columna
    # de fechas común que podría ser de utilidad
    df_resultado['date'] = df['date']
    # Y la dejo como índice
    df_resultado.set_index('date', inplace=True)

    # Creo el df de retornos logarítmicos
    df_retornos = pd.DataFrame()
    for ticker in df_resultado.columns:
        df_retornos[ticker] = np.log(df_resultado[ticker]).diff()

    # Elimino la primera fila que tendrá NaN por hacer el diff()
    df_retornos.dropna(inplace=True)

    # Split 70/30 o lo que sea (uso el % indicado por el usuario adaptándolo)
    porcentaje_entren = int(porcentaje_entren.replace('%', ''))/100
    tam_entrenamiento = int(len(df_retornos) * porcentaje_entren)

    # Elimino la primera y última fila porque son valores
    # perdidos tras el diff()
    train = df_retornos.iloc[:tam_entrenamiento]
    test = df_retornos.iloc[tam_entrenamiento:]

    return df_retornos, df_resultado, tam_entrenamiento, train, test


def _regresion_lineal(model, x_train, y_train, x_test, y_test, df_retornos, tam_entrenamiento, clase,
                      df_resultado, valores):
    """Para aplicar un modelo de regresión lineal siguiendo la idea de que unos valores
    de un índice se comportan como atributos y el valor del día siguiente de ese índice
    se comporta como clase objetivo. 

    Parameters
    ----------
        model : sklearn.linear_model._base.LinearRegression)
            Modelo de regresión lineal.

        x_train : pandas.core.frame.DataFrame
            Datos de entrenamiento.

        y_train : pandas.core.series.Series
            Datos de resultado esperado en entrenamiento.

        x_test : pandas.core.frame.DataFrame
            Datos de test.

        y_test : pandas.core.series.Series
            Datos de resultado esperado en test.

        df_retornos : pandas.core.frame.DataFrame
            Conjunto de datos con retornos de la clase objetivo. 

        tam_entrenamiento : int
            Tamaño de los datos de entrenamiento.

        clase : str
            Clase objetivo. 

        df_resultado : pandas.core.frame.DataFrame
            Datos de resultado. 

        valores : list
            Lista de los valores que se usan como 'atributos' para entrenar el
            modelo y estimar la clase objetivo. 


    Returns
    -------
        context : dict
            Diccionario con datos del contexto.
    """
    # Para que en la web vaya más rápido no se hace validación cruzada
    model.fit(x_train, y_train)
    score_entren = model.score(x_train, y_train)
    score_test = model.score(x_test, y_test)

    # No me voy a preocupar por el valor de las predicciones, solo
    # me interesa saber si es un resultado positivo o negativo (predicción)
    # de siguiente día ascendente o descendente)
    pred_train = model.predict(x_train)
    pred_test = model.predict(x_test)

    # Obtengo unos arrays de [1, -1] que me indican la tendencia en ese
    # punto. Luego los comparo para obtener un array de bool y así puedo
    # calcular la exactitud (accuracy) con mean()
    media_aciertos_entren =  np.mean(np.sign(pred_train) == np.sign(y_train))
    media_aciertos_test = np.mean(np.sign(pred_test) == np.sign(y_test))

    # Creo una nueva columna que permite saber el estado en el que
    # está: alcista/basjista. Suponiendo que todas las veces que el algoritmo
    # ha indicado posición alcista nos hemos puesto alcistas, podré hacer una
    # suma de los retornos en esos días.
    # Esto es, si 'pred_train' es > 0 se asigna un True y False en otro caso
    posiciones = np.zeros(len(df_retornos), dtype=int)
    posiciones[:tam_entrenamiento] = (pred_train > 0).astype(int)
    posiciones[tam_entrenamiento:] = (pred_test > 0).astype(int)
    df_retornos['posicion'] = posiciones
    # Todas las veces que es alcista se multiplican por el retorno real
    # para ver lo que habría ocurrido.
    df_retornos['retorno_algoritmo'] = df_retornos['posicion'] * df_retornos[clase]

    ret_total_algo_entre = df_retornos.iloc[:tam_entrenamiento]['retorno_algoritmo'].sum()
    ret_total_algo_test = df_retornos.iloc[tam_entrenamiento:]['retorno_algoritmo'].sum()

    ret_total_buyhold_entre = y_train.sum()
    ret_total_buyhold_test = y_test.sum()

    # Los datos para realizar una predicción extra corresponden con los del último
    # día disponible. Entonces, creo un 'df' con esos datos (para darle la forma necesaria)
    datos_prediccion = df_resultado.iloc[-1][valores].copy()
    # Y, posteriormente, hago un diff() manual para obtener los retornos logarítmicos
    datos_prediccion = np.log(df_resultado.iloc[-1][valores]) - np.log(df_resultado.iloc[-2][valores])
    # Como sólo tengo una fila de datos, el df aparece como columna, así
    # que me aseguro de que estará bien transponiendo
    datos_prediccion = pd.DataFrame(datos_prediccion).T

    pred_siguiente = model.predict(datos_prediccion)
    pred_siguiente = 'BAJISTA' if pred_siguiente[0] <= 0 else 'ALCISTA'

    context = {
            'form': EstrategiaMLForm(),
            'score_entren': score_entren,
            'score_test': score_test,
            'media_aciertos_entren': media_aciertos_entren*100,
            'media_aciertos_test': media_aciertos_test*100,
            'ret_total_algo_entre': ret_total_algo_entre,
            'ret_total_algo_test': ret_total_algo_test,
            'ret_total_buyhold_entre': ret_total_buyhold_entre,
            'ret_total_buyhold_test': ret_total_buyhold_test,
            # Finalmente hago la predicción con el modelo que ya tenía entrenado
            'pred_siguiente': pred_siguiente,
            'regresion_lineal': True,
        }
    return context


def _clasificacion_regresion_logistica(model, x_train, y_train, x_test, y_test, df_retornos,
                                       tam_entrenamiento, clase, df_resultado, valores):
    """Para aplicar un modelo de clasificación siguiendo la idea de que unos valores
    de un índice se comportan como atributos y el valor del día siguiente de ese índice
    se comporta como clase objetivo. 

    Parameters
    ----------
        model : sklearn.linear_model._base.LinearRegression)
            Modelo de regresión lineal.

        x_train : pandas.core.frame.DataFrame
            Datos de entrenamiento.

        y_train : pandas.core.series.Series
            Datos de resultado esperado en entrenamiento.

        x_test : pandas.core.frame.DataFrame
            Datos de test.

        y_test : pandas.core.series.Series
            Datos de resultado esperado en test.

        df_retornos : pandas.core.frame.DataFrame
            Conjunto de datos con retornos de la clase objetivo. 

        tam_entrenamiento : int
            Tamaño de los datos de entrenamiento.

        clase : str
            Clase objetivo. 

        df_resultado : pandas.core.frame.DataFrame
            Datos de resultado. 

        valores : list
            Lista de los valores que se usan como 'atributos' para entrenar el
            modelo y estimar la clase objetivo. 


    Returns
    -------
        context : dict
            Diccionario con datos del contexto.
    """
    # Con este modelo, a diferencia de LinearRegression(), es necesario
    # convertir la clase objetivoo a valores binarios
    c_train = y_train > 0
    c_test = y_test > 0

    # Para que en la web vaya más rápido no se hace validación cruzada
    model.fit(x_train, c_train)
    score_entren = model.score(x_train, c_train)
    score_test = model.score(x_test, c_test)

    # No me voy a preocupar por el valor de las predicciones, solo
    # me interesa saber si es un resultado positivo o negativo (i.e.,
    # predicción de siguiente día ascendente o descendente)
    pred_train = model.predict(x_train)
    pred_test = model.predict(x_test)

    # Como se explica en el apartado teórico de la memoria, es posible
    # obtener una matriz de confusión y trabajar con ella si fuera necesario:
    # M = confusion_matrix(c_test, pred_test)

    # Obtengo unos arrays de [True, False] que me indican la tendencia en ese
    # punto
    media_aciertos_entren = np.mean(pred_train == c_train)
    media_aciertos_test = np.mean(pred_test == c_test)


    # Creo una nueva columna que permite saber el estado en el que
    # está: alcista/basjista. Suponiendo que todas las veces que el algoritmo
    # ha indicado posición alcista nos hemos puesto alcistas, podré hacer una
    # suma de los retornos en esos días.
    # Esto es, si 'pred_train' es > 0 se asigna un True y False en otro caso
    posiciones = np.zeros(len(df_retornos), dtype=bool)
    posiciones[:tam_entrenamiento] = pred_train
    posiciones[tam_entrenamiento:] = pred_test
    df_retornos['posicion'] = posiciones
    # Todas las veces que es alcista se multiplican por el retorno real
    # para ver lo que habría ocurrido.
    df_retornos['retorno_algoritmo'] = df_retornos['posicion'] * df_retornos[clase]

    ret_total_algo_entre = df_retornos.iloc[:tam_entrenamiento]['retorno_algoritmo'].sum()
    ret_total_algo_test = df_retornos.iloc[tam_entrenamiento:]['retorno_algoritmo'].sum()

    ret_total_buyhold_entre = y_train.sum()
    ret_total_buyhold_test = y_test.sum()

    # Los datos para realizar una predicción extra corresponden con los del último
    # día disponible. Entonces, creo un 'df' con esos datos (para darle la forma necesaria)
    datos_prediccion = df_resultado.iloc[-1][valores].copy()
    # Y, posteriormente, hago un diff() manual para obtener los retornos logarítmicos
    datos_prediccion = np.log(df_resultado.iloc[-1][valores]) - np.log(df_resultado.iloc[-2][valores])
    # Como sólo tengo una fila de datos, el df aparece como columna, así
    # que me aseguro de que estará bien transponiendo
    datos_prediccion = pd.DataFrame(datos_prediccion).T

    # Finalmente hago la predicción con el modelo que ya tenía entrenado
    pred_siguiente = model.predict(datos_prediccion)
    pred_siguiente = 'BAJISTA' if pred_siguiente[0] <= 0 else 'ALCISTA'

    context = {
            'form': EstrategiaMLForm(),
            'score_entren': score_entren,
            'score_test': score_test,
            'media_aciertos_entren': media_aciertos_entren*100,
            'media_aciertos_test': media_aciertos_test*100,
            'ret_total_algo_entre': ret_total_algo_entre,
            'ret_total_algo_test': ret_total_algo_test,
            'ret_total_buyhold_entre': ret_total_buyhold_entre,
            'ret_total_buyhold_test': ret_total_buyhold_test,
            # Finalmente hago la predicción con el modelo que ya tenía entrenado
            'pred_siguiente': pred_siguiente,
            'clasificacion': True,
        }
    return context
