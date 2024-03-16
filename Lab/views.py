from django.shortcuts import render
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from django.apps import apps
from pmdarima.arima import auto_arima
from util.tickers.Tickers_BDs import obtener_nombre_bd, tickers_disponibles
import warnings
# Para evitar todos los warnings de convergencia y de datos no estacionarios
# al aplicar los modelos ARIMA
warnings.filterwarnings("ignore")


def lab(request):
    # Por defecto order=None, i.e., se calcula el 'order' (p,d,q)
    # automáticamente con auto_arima
    # forecast_con_arima(ticker, order=None)

    # forecast_con_arima(ticker, order=(4,1,2))

    # grid_search_arima(ticker)

    # Obtener el nombre del usuario
    usuario = request.user.username

    context = {
        "usuario": usuario,
    }
    return render(request, "lab.html", context)


def arima(request):
    """
    """
    if request.method == 'GET':
        context = {
            "usuario": request.user.username,
            "lista_tickers": tickers_disponibles(),
        }
        return render(request, "arima.html", context)
    
    # POST
    # ----
    ticker = request.POST.get("ticker_a_buscar")
    order=None

    bd = obtener_nombre_bd(ticker)
    modelo = apps.get_model('Analysis', ticker)
    # Último año aprox.
    entrada = modelo.objects.using(bd).order_by('-date')[:220]
    df = pd.DataFrame(list(entrada.values()))
    
    df.sort_values(by='date', ascending=True, inplace=True, ignore_index=True)

    # Guardo las fechas para usarlas como índices
    datos = df['close']
    fechas = df['date']

    # Split 70/30
    tam_entrenamiento = int(len(datos) * 0.7)
    datos_entrenamiento, datos_test = datos[:tam_entrenamiento], datos[tam_entrenamiento:]

    # Separo en history porque lo voy actualizando para los 
    # subsecuentes análisis
    conjunto_total = [_ for _ in datos_entrenamiento]
    lista_predicciones = []
    prediccion = 0

    # Calcular 'order' de forma automática con auto_arima. En otro 
    # caso, 'order' será lo que hay indicado el usuario. Se calcula
    # el mejor modelo con auto_arima
    if order==None:
        # Uso todos los datos para calcular order=(p,d,q)
        # una única vez
        model = auto_arima(datos, seasonal=False)
        order = model.order
    else:
        # Comprobación de que los datos introducidos por 
        # el usuario son válidos
        for _ in order:
            if type(_) != int:
                print("ERROR")
                return

    lista_aciertos_tendencia = []
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

        real = datos_test.iloc[t]
        if previo < real:
            tendencia = 'alcista'
        elif previo > real:
            tendencia = 'bajista'
        else:
            tendencia = 'sin tendencia'
        if (previo < estimado and previo < real) or (previo > estimado and previo > real) or (previo == estimado and previo == real):
            acierta_tendencia = True
        else:
            acierta_tendencia = False
        
        print(f'Cierre previo:{previo} - Estimado: {estimado} - Cierre real: {real} - Tendencia: {tendencia} - Acierta: {acierta_tendencia}')
        lista_aciertos_tendencia.append(acierta_tendencia)
    
    # Hago una predicción adicional para el próximo día
    prediccion = modelo_fit.forecast(steps=1)
    
    # Evaluar con RMSE cómo ha sido el forecast
    print(modelo_fit.summary())
    rmse = sqrt(mean_squared_error(datos_test, lista_predicciones))
    print('Test RMSE: %.3f' % rmse)
    print("Predicciones: ", prediccion)
    print(f'Total aciertos de tendencia: {lista_aciertos_tendencia.count(True)}')
    print(f'Total fallos de tendencia: {lista_aciertos_tendencia.count(False)}')

    # datos_test.index = fechas[tam_entrenamiento:]
    datos.index = fechas
    lista_predicciones = pd.DataFrame(lista_predicciones)
    lista_predicciones.index = fechas[tam_entrenamiento:]

    # plt.plot(datos_test.index, datos_test, color='blue', label='Original')
    plt.plot(datos.index, datos, color='blue', label='Original')
    plt.plot(lista_predicciones.index, lista_predicciones, color='red', label=f'Predicción últimos {len(datos_test)} días')
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.legend()
    plt.savefig('pruebas.png', format='PNG')

    return


def grid_search_arima(ticker):

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