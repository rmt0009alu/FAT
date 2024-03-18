from django.shortcuts import render
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from django.apps import apps
from pmdarima.arima import auto_arima
from util.tickers.Tickers_BDs import obtener_nombre_bd, tickers_disponibles
# Mis formularios
from .forms import ArimaForm
# Para el buffer y las imágenes
from io import BytesIO
import base64
# Para evitar todos los warnings de convergencia y de datos no estacionarios
# al aplicar los modelos ARIMA
import warnings
warnings.filterwarnings("ignore")


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


def arima_parametros_auto(request):
    """Para mostrar el resultado de un modelo ARIMA
    cuyos parámetros (p,d,q) son calculados automáticamente
    con 'auto_arima'. 

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): solicitud
            HTTP encapsulada por Django.

    Returns:
        (render): renderiza la plantilla 'arima.html' con datos de contexto.
    """
    if request.method == 'GET':
        context = {
            "lista_tickers": tickers_disponibles(),
            "form": ArimaForm,
        }
        return render(request, "arima.html", context)
    
    # POST
    # ----
    # El 'ticker' no está en el form para poder usar
    # una caja de búsqueda autocompletable.
    ticker = request.POST.get("ticker_a_buscar")        
    # Adaptación a la notación de los tickers en las BDs
    ticker = ticker.replace(".", "_")
    ticker = ticker.replace("^", "")
    
    # Uso el resto del formulario (sin el ticker)
    form = ArimaForm(request.POST)
    if form.is_valid():
        # Obtengo datos del form
        num_sesiones = form.cleaned_data['num_sesiones']
        porcentaje_entren = form.cleaned_data['porcentaje_entrenamiento']

        # Compruebo existencia de ticker
        bd = obtener_nombre_bd(ticker)
        context = _comprobar_formulario(bd, ticker, num_sesiones, porcentaje_entren, caso='1')
        if context is not False:
            # Si hay datos en el contexto es porque algo está mal y se 
            # añade un mensaje informativo al usuario
            return render(request, "arima.html", context)

        # Busco la info para el nº de sesiones indicado por ususario
        modelo = apps.get_model('Analysis', ticker)
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
        
        # Calcular 'order' de forma automática con auto_arima. Uso todos 
        # los datos para calcular order=(p,d,q) una única vez
        model = auto_arima(datos, seasonal=False)
        order = model.order

        # Hago una validación diaría para los datos de test
        prediccion, modelo_fit, lista_aciertos_tendencia, lista_predicciones = _validacion_walk_forward(datos_test, order, datos_entrenamiento)
        
        # Mostrar datos textuales
        # _mostrar_datos_textuales(modelo_fit, datos_test, lista_predicciones, lista_aciertos_tendencia, prediccion)

        # Generar la gráfica con el forecast en los datos de test
        context = _generar_resultados(modelo_fit, fechas, lista_predicciones, tam_entrenamiento, datos, datos_test, prediccion, lista_aciertos_tendencia)

        # Si todo ha ido muestro la info. al usuario
        return render(request, "arima.html", context)
    
    # Si el formulario no es válido, busco el motivo e informo al usuario
    bd = obtener_nombre_bd(ticker)
    # Obtengo datos del form, como es un form NO válido no puedo usar 
    # form.cleaned_data['...'] y, por tanto, los datos serán 'str'
    num_sesiones = request.POST.get('num_sesiones')
    porcentaje_entren = request.POST.get('porcentaje_entrenamiento')
    context = _comprobar_formulario(bd, ticker, num_sesiones, porcentaje_entren, caso='2')

    return render(request, "arima.html", context)



def arima_parametros_rejilla(request):
    if request.method == 'GET':
        context = {
            "usuario": request.user.username,
            "lista_tickers": tickers_disponibles(),
        }
        return render(request, "arima.html", context)

    # POST
    # ----
    ticker = request.POST.get("ticker_a_buscar")
    
    # LA BÚSQUEDA POR REJILLA SE HACE SOBRE LOS DATOS 
    # DE ENTRENAMIENTO Y SE EVALÚA, LUEGO, SOBRE LOS
    # DATOS DE TEST

    bd = obtener_nombre_bd(ticker)
    modelo = apps.get_model('Analysis', ticker)
    # Último año aprox.
    entrada = modelo.objects.using(bd).order_by('-date')[:220]
    df = pd.DataFrame(list(entrada.values()))
    
    df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

    # Guardo las fechas para usarlas como índices
    datos = df['close']
    # fechas = df['date']

    # Split 70/30
    tam_entrenamiento = int(len(datos) * 0.7)
    datos_entrenamiento, datos_test = datos[:tam_entrenamiento], datos[tam_entrenamiento:]

    best_score, best_cfg = float("inf"), None
    p_values = range(1,5)
    d_values = range(1,3)
    q_values = range(1,5)
    for p in p_values:
        for d in d_values:
             for q in q_values:
                order = (p,d,q)
                try:
                    mse, aic = _evaluar_modelo_arima(datos_entrenamiento, datos_test, order)
                    if mse < best_score:
                        best_score, best_cfg = mse, order
                    print('ARIMA%s MSE=%.3f AIC=%.3f' % (order,mse, aic))
                except:
                    continue
    print('Best ARIMA%s MSE=%.3f' % (best_cfg, best_score))

    # rmse = sqrt(mean_squared_error(datos_test, lista_predicciones))
    # print('Test RMSE: %.3f' % rmse)
    # print("Predicciones: ", prediccion)
    # print(f'Total aciertos de tendencia: {lista_aciertos_tendencia.count(True)}')
    # print(f'Total fallos de tendencia: {lista_aciertos_tendencia.count(False)}')
    return


def _evaluar_modelo_arima(datos_entrenamiento, datos_test, order):
    conjunto_total = [_ for _ in datos_entrenamiento]
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

    # Validación directa con aic, bic y hqic
    modelo_directo = ARIMA(datos_test, order=order)
    output = modelo_directo.fit()
    aic = output.aic
    
    return mse, aic



def _comprobar_formulario(bd, ticker, num_sesiones, porcentaje_entren, caso):
    """Permite comprobar si los datos introducidos por
    el usuario son coherentes.

    Args:
        bd (str): nombre de la base de datos.
        ticker (str): nombre del ticker.
        num_sesiones (int): número de sesiones que se quieren analizar. 
        porcentaje_entren (int): % de datos para el entrenamiento del modelo.
        caso (int): indicador del caso a tratar.

    Returns:
        (dict): diccionario con datos del cotexto.
    """
    context = {
        "form": ArimaForm,
        "lista_tickers": tickers_disponibles(),
    }

    match caso:
        case "1":
            if bd is None:
                context["msg_error"] = f'El ticker {ticker} no está disponibe'
                return context
        
        case "2":
            if num_sesiones.isdigit():
                num_sesiones = int(num_sesiones)
                if (not 100 <= num_sesiones <= 500):
                    context["msg_error"] = f'Valor no válido para el nº de sesiones'
                    return context
            else:
                context["msg_error"] = f'Valor no válido para el nº de sesiones'
                return context
            
            if porcentaje_entren not in ['50%', '66%', '70%', '80%', '90%']:
                context["msg_error"] = f'Porcentaje indicado no válido'
                return context

    # Si no hay errores
    return False


def _validacion_walk_forward(datos_test, order, datos_entrenamiento):

    lista_predicciones = []
    prediccion = 0  
    lista_aciertos_tendencia = []
    # Separo en 'conjunto_total' porque lo voy actualizando para los 
    # subsecuentes análisis
    conjunto_total = [_ for _ in datos_entrenamiento]
    
    # Validación 'walk-forward'
    for t in range(len(datos_test)):
        modelo = ARIMA(conjunto_total, order=order)
        modelo_fit = modelo.fit()
        # Por defecto, el forecast es de un step, podría omitirlo
        output = modelo_fit.forecast(steps=1)
        estimado = output[0]
        lista_predicciones.append(estimado)
        # El dato real es el que está en datos_test
        # y se uas para la siguiente iteración
        conjunto_total.append(datos_test.iloc[t])
        if (t>0):
            previo = datos_test.iloc[t-1]
        else:
            # Cuando t=0 el dato anterior corresponde a los de 
            # entrenamiento
            previo = datos_entrenamiento.iloc[-1]

        # Comprobación de aciertos vs fallos para mostrar al usuario
        real = datos_test.iloc[t]
        if (previo < estimado and previo < real) or (previo > estimado and previo > real) or (previo == estimado and previo == real):
            acierta_tendencia = True
        else:
            acierta_tendencia = False
        
        lista_aciertos_tendencia.append(acierta_tendencia)

    # Hago una predicción adicional para la próxima sesión
    prediccion = modelo_fit.forecast(steps=1)

    return prediccion, modelo_fit, lista_aciertos_tendencia, lista_predicciones
    

def _generar_resultados(modelo_fit, fechas, lista_predicciones, tam_entrenamiento, datos, datos_test, prediccion, lista_aciertos_tendencia):

    datos.index = fechas
    lista_predicciones = pd.DataFrame(lista_predicciones)
    lista_predicciones.index = fechas[tam_entrenamiento:]

    fig = plt.figure(figsize=(7, 5))
    buffer = BytesIO()
    # plt.plot(datos_test.index, datos_test, color='blue', label='Original')
    plt.plot(datos.index, datos, color='blue', label='Original')
    plt.plot(lista_predicciones.index, lista_predicciones, color='red', label=f'Predicción últimos {len(datos_test)} días')
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.legend()
    plt.savefig(buffer, format='PNG')

    plt.close()
    
    # Obtener los datos de la imagen del buffer
    buffer.seek(0)
    forecast_arima = base64.b64encode(buffer.read()).decode()

    context = {
        "lista_tickers": tickers_disponibles(),
        "form": ArimaForm,
        "forecast_arima": forecast_arima,
        "resumen": modelo_fit.summary(),
        "mse": mean_squared_error(datos_test, lista_predicciones),
        "rmse": sqrt(mean_squared_error(datos_test, lista_predicciones)),
        "prediccion_prox_sesion": prediccion,
        "aciertos_tendencia": lista_aciertos_tendencia.count(True),
        "fallos_tendencia": lista_aciertos_tendencia.count(False),
    }
    return context

"""
    # Fitting ARIMA model with order (p, d, q) = (1, 1, 1)
    modelo = ARIMA(datos_entrenamiento, order=(5, 1, 1))
    modelo_fit = modelo.fit()

    # Resumen del modelo ajustado:
    # print(modelo_fit.summary())

    # Predict the next 3 values
    forecast_steps = 5
    prediccion = modelo_fit.forecast(steps=forecast_steps)

    datos.index = fechas
    prediccion.index = fechas[tam_entrenamiento:(tam_entrenamiento+forecast_steps)]

    # Print or visualize the predicted values
    print("Predicted Values:", prediccion)

    # Visualize original data and predicted values
    plt.plot(datos.index, datos, label='Original Data')
    plt.plot(prediccion.index, prediccion, label='Predictions', color='red')
        
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))  # Adjust the maximum number of ticks displayed

    plt.legend()
    plt.savefig('prediccion.png', format="PNG")
    """

# def _pruebas_ARIMA_pronostico_estatico(ticker):

#     bd = obtener_nombre_bd(ticker)
#     model = apps.get_model('Analysis', ticker)
#     # Último año aprox.
#     entrada = model.objects.using(bd).order_by('-date')[:220]
#     df = pd.DataFrame(list(entrada.values()))
    
#     df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

#     datos = df['close']
#     fechas = df['date']
#     # Para trabajar con modelos de statsmodels hay que indicar una 
#     # frecuencia en índices temporales. Aquí no se puede usar porque
#     # las fechas de las cotizaciones no tienen una frecuencia diaria
#     # ya que hay festivos y/o fines de semana. Por tanto, el índice
#     # será un entero y se hacen luego las adaptaciones oportunas. 
#     # datos.set_index('date', inplace=True)

#     tam_entrenamiento = int(len(datos) * 0.7)
#     datos_entrenamiento, datos_test = datos[:tam_entrenamiento], datos[tam_entrenamiento:]

#     # Fitting ARIMA model with order (p, d, q) = (1, 1, 1)
#     modelo = ARIMA(datos_entrenamiento, order=(5, 1, 1))
#     modelo_fit = modelo.fit()

#     # Resumen del modelo ajustado:
#     # print(modelo_fit.summary())

#     # Predict the next 3 values
#     forecast_steps = 5
#     prediccion = modelo_fit.forecast(steps=forecast_steps)

#     datos.index = fechas
#     prediccion.index = fechas[tam_entrenamiento:(tam_entrenamiento+forecast_steps)]

#     # Print or visualize the predicted values
#     print("Predicted Values:", prediccion)

#     # Visualize original data and predicted values
#     plt.plot(datos.index, datos, label='Original Data')
#     plt.plot(prediccion.index, prediccion, label='Predictions', color='red')
        
#     plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))  # Adjust the maximum number of ticks displayed

#     plt.legend()
#     plt.savefig('prediccion.png', format="PNG")
    
#     """
#     residuals = pd.DataFrame(modelo_fit.resid)
#     residuals.plot()
#     plt.savefig('linea_residuos.png', format="PNG")
#     # density plot of residuals
#     residuals.plot(kind='kde')
#     plt.savefig('densidad_residuos.png', format="PNG")
#     # summary stats of residuals
#     print(residuals.describe())
#     """

#     return