from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from django.apps import apps
from pmdarima.arima import auto_arima
from util.tickers.Tickers_BDs import obtener_nombre_bd


def forecast_con_arima(ticker, order=None):
    """
    """
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
    history = [x for x in datos_entrenamiento]
    predictions = list()
    prediccion = 0

    # Calcular 'order' de forma automática con auto_arima. En otro 
    # caso, 'order' será lo que hay indicado el usuario. Se calcula
    # el mejor modelo con auto_arima
    if order==None:
        model = auto_arima(datos, seasonal=False)
        order = model.order
        # print(model.summary())
        # print("\nParámetros:", model.order, "\n")
    else:
        # Comprobación de que los datos introducidos por 
        # el usuario son válidos
        for _ in order:
            if type(_) != int:
                print("ERROR")

    # Validación 'walk-forward'
    for t in range(len(datos_test)):
        modelo = ARIMA(history, order=order)
        modelo_fit = modelo.fit()
        # Por defecto, el forecast es de un step, podría omitirlo
        output = modelo_fit.forecast(steps=1)
        yhat = output[0]
        predictions.append(yhat)
        obs = datos_test.iloc[t]
        history.append(obs)
        # print(f'predicted={yhat}, expected={obs}')
    
    # Hago una predicción adicional para el próximo día
    prediccion = modelo_fit.forecast(steps=1)
    
    # Evaluar con RMSE cómo ha sido el forecast
    print(modelo_fit.summary())
    rmse = sqrt(mean_squared_error(datos_test, predictions))
    print('Test RMSE: %.3f' % rmse)
    print("Predicciones: ", prediccion)
    
    # datos_test.index = fechas[tam_entrenamiento:]
    datos.index = fechas
    predictions = pd.DataFrame(predictions)
    predictions.index = fechas[tam_entrenamiento:]

    # plt.plot(datos_test.index, datos_test, color='blue', label='Original')
    plt.plot(datos.index, datos, color='blue', label='Original')
    plt.plot(predictions.index, predictions, color='red', label=f'Predicción últimos {len(datos_test)} días')
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.legend()
    plt.savefig('pruebas.png', format='PNG')

    return




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