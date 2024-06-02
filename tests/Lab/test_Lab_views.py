from django.test import TestCase
from django.http import HttpResponse
from log.logger.logger import get_logger_configurado
from datetime import datetime, timezone, timedelta
from django.http import HttpRequest
from Lab.forms import ArimaRejillaForm, ArimaManualForm, ArimaAutoForm, LstmForm, EstrategiaMLForm, FormBasico
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import keras
from Lab.views import _preprocesar_p_d_q, _evaluar_modelo_arima_mse, _comprobar_formularios, _validacion_walk_forward_arima, _generar_resultados_arima, _preprocesado_lstm, _crear_modelo, _comprobar_formulario_lstm, _validacion_walk_forward_lstm, _generar_resultados_lstm, cruce_medias, _obtener_tickers_relevantes, _preprocesado_datos_ML
import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse

# Para usar los modelos creados de forma dinámica
from django.apps import apps
# Para evitar todos los warnings de convergencia y de datos no estacionarios
# al aplicar los modelos ARIMA
import warnings
warnings.filterwarnings("ignore")



# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('NewsViews')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS LAB VIEWS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance
    

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestLabViews(TestCase):

    databases = '__all__'

    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('LabViews')

        # Formularios auto_arima
        self.form_arima_auto_ok = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%'}
        self.form_arima_auto_no_ok_1 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 501, 'porcentaje_entrenamiento': '70%'}
        self.form_arima_auto_no_ok_2 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 99, 'porcentaje_entrenamiento': '70%'}
        self.form_arima_auto_no_ok_3 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '100%'}
        self.form_arima_auto_no_ok_4 = {'ticker_a_buscar': 'tickerFalso', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%'}

        # Formularios auto_rejilla
        self.form_arima_rejilla_ok = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_1 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 501, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_2 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 99, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_3 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '100%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_4 = {'ticker_a_buscar': 'tickerFalso', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_5 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1, 7]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_6 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2, 55]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_rejilla_no_ok_7 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2, 7, 8, 9]'}

        # Formularios auto_manual
        self.form_arima_manual_ok = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_arima_manual_no_ok_1 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 501, 'porcentaje_entrenamiento': '70%', 'valor_p': '[0, 1]', 'valor_d': '[1, 2]', 'valor_q': '[0, 1, 2]'}
        self.form_arima_manual_no_ok_2 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 99, 'porcentaje_entrenamiento': '70%', 'valor_p': '[0, 1]', 'valor_d': '[1, 2]', 'valor_q': '[0, 1, 2]'}
        self.form_arima_manual_no_ok_3 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '100%', 'valor_p': '[0, 1]', 'valor_d': '[1, 2]', 'valor_q': '[0, 1, 2]'}
        self.form_arima_manual_no_ok_4 = {'ticker_a_buscar': 'tickerFalso', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valor_p': 1, 'valor_d': 1, 'valor_q': 5}
        self.form_arima_manual_no_ok_5 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valor_p': -1, 'valor_d': 2, 'valor_q': 5}
        self.form_arima_manual_no_ok_6 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valor_p': 1, 'valor_d': 100, 'valor_q': 5}
        self.form_arima_manual_no_ok_7 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%', 'valor_p': 1, 'valor_d': 2, 'valor_q': 50}

        # Formularios parámetros
        self.form_param_arima_ok = {'ticker_a_buscar': 'IBM', 'num_sesiones': 150}
        self.form_param_arima_no_ok_1 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 501}
        self.form_param_arima_no_ok_2 = {'ticker_a_buscar': 'tickerFalso', 'num_sesiones': 150}

        # Formularios lstm
        self.form_lstm_ok = {'ticker_a_buscar': 'IBM', 'num_sesiones': 550, 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1, 2]'}
        self.form_lstm_no_ok_1 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 399, 'porcentaje_entrenamiento': '70%'}
        self.form_lstm_no_ok_2 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 1001, 'porcentaje_entrenamiento': '70%'}
        self.form_lstm_no_ok_3 = {'ticker_a_buscar': 'IBM', 'num_sesiones': 550, 'porcentaje_entrenamiento': '100%'}
        self.form_lstm_no_ok_4 = {'ticker_a_buscar': 'tickerFalso', 'num_sesiones': 150, 'porcentaje_entrenamiento': '70%'}
        
        self.usuarioTest = User.objects.create_user(username='usuarioTest', password='p@ssw0rdLarga')   

        # Creo unos registros de stocks para que al consultar los datos
        # haya info. de los mismos:
        model = apps.get_model('Analysis', 'IBM')
        # Creo 250 registros (días) del mismo modelo/stock para consultar
        for i in range(250):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0+i, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )
        
        model = apps.get_model('Analysis', 'ACS_MC')
        self.stock_2 = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker='ACS_MC', previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='ACS, Actividades de Construcción y Servicios, S.A.', 
            currency = 'EUR', sector = 'Industrials'
        )


    # ---------
    # TESTS LAB
    # ---------
    def test_views_lab_status_code(self):       
        self.client.force_login(self.usuarioTest) 
        response = self.client.get('/lab/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de lab retorne '200 ok'")
        self.log.info(" - [OK] Que página de lab retorne '200 ok'")


    def test_views_lab_templates_válidas(self):
        self.client.force_login(self.usuarioTest)   
        response = self.client.get('/lab/')   
        self.assertTemplateUsed(response, 'lab.html', " - [NO OK] Asignar 'template' de lab y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de lab y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de lab y cargar base.html")


    def test_views_lab_templates_no_válidas(self):  
        self.client.force_login(self.usuarioTest) 
        response = self.client.get('/lab/')      
        self.assertTemplateNotUsed(response, 'arima_auto.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_rejilla.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_manual.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'lstm.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")


    # ----------------
    # TESTS ARIMA AUTO
    # ----------------
    def test_views_arima_auto_status_code(self):
        self.client.force_login(self.usuarioTest)        
        response = self.client.get('/lab/arima_auto/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de arima_auto retorne '200 ok'")
        self.log.info(" - [OK] Que página de arima_auto retorne '200 ok'")


    def test_views_arima_auto_templates_válidas(self):
        self.client.force_login(self.usuarioTest)   
        response = self.client.get('/lab/arima_auto/')   
        self.assertTemplateUsed(response, 'arima_auto.html', " - [NO OK] Asignar 'template' de arima_auto y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de arima_auto y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de arima_auto y cargar base.html")


    def test_views_arima_auto_templates_no_válidas(self): 
        self.client.force_login(self.usuarioTest)  
        response = self.client.get('/lab/arima_auto/')      
        self.assertTemplateNotUsed(response, 'lab.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_rejilla.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_manual.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'lstm.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")

    
    def test_views_arima_auto_post_sin_login(self):
        response = self.client.post('/lab/arima_auto/', data=self.form_arima_auto_ok)
        self.assertEqual(response.status_code, 302, " - [NO OK] Que POST a 'arima_auto' retorne '302...' sin login")
        self.log.info(" - [OK] Que POST a 'arima_auto' retorne '302...' sin login")
    

    def test_views_arima_auto_post_ok(self):
        self.client.force_login(self.usuarioTest)
        form_data = {
            'ticker_a_buscar': 'IBM',
            'num_sesiones': '200',
            'porcentaje_entrenamiento': '70%',
            'auto': True,
            'manual': False,
            'rejilla': False,
        }
        response = self.client.post('/lab/arima_auto/', data=form_data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'arima_auto' retorne '200 ok' con login")
        self.log.info(" - [OK] Que POST a 'arima_auto' retorne '200 ok' con login")
        

    def test_views_arima_auto_post_con_num_sesiones_no_válido_1(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_auto/', data=self.form_arima_auto_no_ok_1)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_auto' retorne mensaje con num_sesiones no válido")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'arima_auto' retorne mensaje con nº de sesiones no válida")


    def test_views_arima_auto_post_con_num_sesiones_no_válido_2(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_auto/', data=self.form_arima_auto_no_ok_2)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_auto' retorne mensaje con num_sesiones no válido")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'arima_auto' retorne mensaje con nº de sesiones no válida")


    def test_views_arima_auto_post_con_porcentaje_entrenamiento_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_auto/', data=self.form_arima_auto_no_ok_3)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_auto' retorne mensaje con porcentaje_entrenamiento no válido")
        self.assertContains(response, 'Porcentaje indicado no válido')
        self.log.info(" - [OK] Que post a 'arima_auto' retorne mensaje con porcentaje_entrenamiento no válido")


    def test_views_arima_auto_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_auto/', data=self.form_arima_auto_no_ok_4)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_auto' retorne mensaje con ticker no válida")
        self.assertContains(response, 'no está disponibe')
        self.log.info(" - [OK] Que post a 'arima_auto' retorne mensaje con ticker no válida")


    # -------------------
    # TRADING ALGORÍTMICO
    # -------------------
    def test_views_comprobar_formulario_ML_1(self):
        ticker = 'DJI'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 700, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 700, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'
        }
        form = EstrategiaMLForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones formulario ARIMA")
        self.assertEquals(contexto["msg_error"], 'Valor no válido para el nº de sesiones', 
                          " - [NO OK] Comprobar num_sesiones formulario ARIMA")
        self.log.info(" - [OK] Comprobar num_sesiones formulario ARIMA")
    
    
    def test_views_comprobar_formulario_ML_2(self):
        ticker = 'SP500'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 450, 
                                                              'indice': 'SP500', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 450, 
                                                              'indice': 'SP500', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'
        }
        form = EstrategiaMLForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones formulario ML")
        self.assertEquals(contexto["msg_error"], 'El ticker no está disponibe', 
                          " - [NO OK] Comprobar num_sesiones formulario ML")
        self.log.info(" - [OK] Comprobar num_sesiones formulario ML")


    def test_views_comprobar_formulario_ML_3(self):
        ticker = 'DJI'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 450, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión FALSA',
                                                              'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 450, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión FALSA',
                                                              'porcentaje_entrenamiento': '70%'
        }
        form = EstrategiaMLForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar tipo_modelo formulario ML")
        self.assertEquals(contexto["msg_error"], 'Modelo indicado no válido', 
                          " - [NO OK] Comprobar tipo_modelo formulario ML")
        self.log.info(" - [OK] Comprobar tipo_modelo formulario ML")


    def test_views_comprobar_formulario_ML_4(self):
        ticker = 'DJI'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 450, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '100%'})
        form_data = {
            'num_sesiones': 450, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '100%'
        }
        form = EstrategiaMLForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar pocentaje formulario ML")
        self.assertEquals(contexto["msg_error"], 'Porcentaje indicado no válido', 
                          " - [NO OK] Comprobar porcentaje formulario ML")
        self.log.info(" - [OK] Comprobar porcentaje formulario ML")


    def test_views_comprobar_formulario_ML_5(self):
        ticker = 'DJI'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 'valorFalso', 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 'valorFalso', 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'
        }
        form = EstrategiaMLForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones formulario ML")
        self.assertEquals(contexto["msg_error"], 'Valor no válido para el nº de sesiones', 
                          " - [NO OK] Comprobar num_sesiones formulario ML")
        self.log.info(" - [OK] Comprobar num_sesiones formulario ML")


    def test_views_comprobar_formulario_ML_6(self):
        ticker = 'DJI'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 450, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 450, 
                                                              'indice': 'DJ30', 
                                                              'tipo_modelo': 'Regresión lineal',
                                                              'porcentaje_entrenamiento': '70%'
        }
        form = EstrategiaMLForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar todo ok formulario ML")
        self.assertEquals(contexto, False)
        self.log.info(" - [OK] Comprobar todo ok formulario ML")
    

    def test_views_comprobar_formulario_basico(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/estrategia_ML', {'num_sesiones': 'valorFalso'})
        form_data = {'num_sesiones': 'valorFalso'}
        form = FormBasico(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones formulario básico")
        self.assertEquals(contexto["msg_error"], 'Valor no válido para el nº de sesiones', 
                          " - [NO OK] Comprobar num_sesiones formulario básico")
        self.log.info(" - [OK] Comprobar num_sesiones formulario básico")
    

    def test_views_cruce_medias_status_code(self):
        self.client.force_login(self.usuarioTest)        
        response = self.client.get('/lab/cruce_medias/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de cruce_medias retorne '200 ok'")
        self.log.info(" - [OK] Que página de cruce_medias retorne '200 ok'")


    def test_views_cruce_medias_get_request(self):
        self.client.force_login(self.usuarioTest)     
        url = reverse('cruce_medias')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cruce_medias.html')
        self.log.info(" - [OK] Comprobar URL de cruce_medias")


    def test_views_cruce_medias_post_request_datos_ok(self):
        self.client.force_login(self.usuarioTest)     
        url = reverse('cruce_medias')
        data = {
            'ticker_a_buscar': 'AAPL',  
            'num_sesiones': 10,  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cruce_medias.html')
        self.log.info(" - [OK] Comprobar cruce_medias con datos válidos")


    def test_views_cruce_medias_post_request_datos_no_ok(self):
        self.client.force_login(self.usuarioTest)     
        url = reverse('cruce_medias')
        data = {
            'ticker_a_buscar': '',  
            'num_sesiones': -5,  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cruce_medias.html')
        self.log.info(" - [OK] Comprobar cruce_medias con datos falsos")


    def test_views_cruce_medias_post_request_comprobar_context(self):
        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )

        self.client.force_login(self.usuarioTest)    
        url = reverse('cruce_medias')
        data = {
            'ticker_a_buscar': 'IBM',
            'num_sesiones': 220,
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cruce_medias.html')
        context = response.context
        self.assertIn('form', context)
        self.assertIn('cruce_medias', context)
        self.assertIn('retorno_log_total_algo', context)
        self.assertIn('retorno_log_total', context)
        self.assertIn('sharpe_retorno_log_algo', context)
        self.assertIn('sharpe_retorno_log', context)
        self.assertIn('df_resultados', context)
        self.assertIn('porcentaje_algo', context)
        self.assertIn('porcentaje_manteniendo', context)
        self.log.info(" - [OK] Comprobar contexto en cruce de medias")


    def test_views_estrategia_ML_status_code(self):
        self.client.force_login(self.usuarioTest)        
        response = self.client.get('/lab/estrategia_ML/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de estrategia_ML retorne '200 ok'")
        self.log.info(" - [OK] Que página de estrategia_ML retorne '200 ok'")


    def test_views_estrategia_ML_get_request(self):
        self.client.force_login(self.usuarioTest)     
        url = reverse('estrategia_ML')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estrategia_basada_en_ML.html')
        self.log.info(" - [OK] Estrategia ML obtener URL")


    def test_views_estrategia_ML_post_request_datos_ok(self):
        self.client.force_login(self.usuarioTest)     
        url = reverse('estrategia_ML')
        data = {
            'ticker_a_buscar': 'AAPL',  
            'num_sesiones': 10,  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estrategia_basada_en_ML.html')
        self.log.info(" - [OK] Estrategia ML con datos válidos")


    def test_views_estrategia_ML_post_request_datos_no_ok(self):
        self.client.force_login(self.usuarioTest)     
        url = reverse('estrategia_ML')
        data = {
            'ticker_a_buscar': '',  
            'num_sesiones': -5,  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estrategia_basada_en_ML.html')
        self.log.info(" - [OK] Estrategia ML con datos falsos")


    def test_views_estrategia_ML_post_request_comprobar_reg_lineal(self):
        self.client.force_login(self.usuarioTest)     
        tickers = ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM', 'DJI']
        num_sesiones = 220

        for ticker in tickers:
            for i in range(num_sesiones):
                model = apps.get_model('Analysis', ticker)
                model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='cualquiera', 
            currency = 'USD', sector = 'Industrials'
        )
        url = reverse('estrategia_ML')
        data = {
            'indice': 'DJ30',
            'tipo_modelo': 'Regresión lineal',
            'num_sesiones': 220,    
            'porcentaje_entrenamiento': '70%',  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('form', context)
        self.log.info(" - [OK] Comprobar direccionamiento a regresión lineal")

    
    def test_views_estrategia_ML_post_request_comprobar_clasificacion(self):
        self.client.force_login(self.usuarioTest)     
        tickers = ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM', 'DJI']
        num_sesiones = 220

        for ticker in tickers:
            for i in range(num_sesiones):
                model = apps.get_model('Analysis', ticker)
                model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0 + i, high=110.0 + i, low=90.0 + i, close=105.0 + i, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='cualquiera', 
            currency = 'USD', sector = 'Industrials'
        )
        url = reverse('estrategia_ML')
        data = {
            'indice': 'DJ30',
            'tipo_modelo': 'Clasificación',
            'num_sesiones': 220,    
            'porcentaje_entrenamiento': '70%',  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('form', context)
        self.log.info(" - [OK] Comprobar direccionamiento a clasificacion")


    def test_views_obtener_tickers_relevantes(self):
        valores, clase, tickers_unidos = _obtener_tickers_relevantes('DJ30')
        self.assertEqual(valores, ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM'], " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(clase, 'DJI', " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(tickers_unidos, ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM', 'DJI'], 
                         " - [NO OK] Obtener tickers relevantes")
        
        valores, clase, tickers_unidos = _obtener_tickers_relevantes('IBEX35')
        self.assertEqual(valores, ['ITX_MC', 'IBE_MC', 'SAN_MC', 'BBVA_MC', 'CABK_MC'], 
                         " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(clase, 'IBEX', " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(tickers_unidos, ['ITX_MC', 'IBE_MC', 'SAN_MC', 'BBVA_MC', 'CABK_MC', 'IBEX'], 
                         " - [NO OK] Obtener tickers relevantes")

        valores, clase, tickers_unidos = _obtener_tickers_relevantes('FTSE100')
        self.assertEqual(valores, ['SHEL_L', 'AZN_L', 'HSBA_L', 'ULVR_L', 'BP_L'], 
                         " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(clase, 'FTSE', " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(tickers_unidos, ['SHEL_L', 'AZN_L', 'HSBA_L', 'ULVR_L', 'BP_L', 'FTSE'], 
                         " - [NO OK] Obtener tickers relevantes")

        valores, clase, tickers_unidos = _obtener_tickers_relevantes('DAX40')
        self.assertEqual(valores, ['SAP_DE', 'SIE_DE', 'ALV_DE', 'AIR_DE', 'DTE_DE'], 
                         " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(clase, 'GDAXI', " - [NO OK] Obtener tickers relevantes")
        self.assertEqual(tickers_unidos, ['SAP_DE', 'SIE_DE', 'ALV_DE', 'AIR_DE', 'DTE_DE', 'GDAXI'], 
                         " - [NO OK] Obtener tickers relevantes")

        self.log.info(" - [OK] Obtener tickers relevantes")


    def test_views_preprocesado_datos_ML(self):
        tickers = ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM', 'DJI']
        num_sesiones = 10

        for ticker in tickers:
            for i in range(num_sesiones):
                model = apps.get_model('Analysis', ticker)
                model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
            dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
            percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='cualquiera', 
            currency = 'USD', sector = 'Industrials'
        )
        tickers_unidos = ['MSFT', 'AAPL', 'UNH', 'JNJ', 'JPM']
        num_sesiones = 10
        porcentaje_entren = '70%'

        df_retornos, df_resultado, tam_entrenamiento, train, test = _preprocesado_datos_ML(tickers_unidos, num_sesiones, porcentaje_entren)

        self.assertFalse(df_retornos.empty)
        self.assertFalse(df_resultado.empty)
        self.assertEqual(tam_entrenamiento, int(len(df_retornos) * 0.7))
        self.assertEqual(len(train), tam_entrenamiento)
        self.assertEqual(len(test), len(df_retornos) - tam_entrenamiento)

        expected_columns = tickers_unidos
        self.assertListEqual(list(df_retornos.columns), expected_columns)
        self.assertListEqual(list(df_resultado.columns), expected_columns)

        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_resultado.index))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_retornos.index))
        self.log.info(" - [OK] Preprocesado datos ML")
        

    # -------------------
    # TESTS PARAMS ARIMA
    # -------------------
    def test_views_params_arima_status_code(self):
        self.client.force_login(self.usuarioTest)        
        response = self.client.get('/lab/buscar_paramateros_arima/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de buscar_paramateros_arima retorne '200 ok'")
        self.log.info(" - [OK] Que página de buscar_paramateros_arima retorne '200 ok'")


    def test_views_params_arima_templates_válidas(self):
        self.client.force_login(self.usuarioTest)   
        response = self.client.get('/lab/buscar_paramateros_arima/')   
        self.assertTemplateUsed(response, 'buscar_paramateros_arima.html', " - [NO OK] Asignar 'template' de buscar_paramateros_arima y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de buscar_paramateros_arima y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de buscar_paramateros_arima y cargar base.html")


    def test_views_params_arima_templates_no_válidas(self): 
        self.client.force_login(self.usuarioTest)  
        response = self.client.get('/lab/buscar_paramateros_arima/')      
        self.assertTemplateNotUsed(response, 'lab.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_rejilla.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_manual.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'lstm.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")

    
    def test_views_params_arima_post_sin_login(self):
        response = self.client.post('/lab/buscar_paramateros_arima/', data=self.form_param_arima_ok)
        self.assertEqual(response.status_code, 302, " - [NO OK] Que POST a 'buscar_paramateros_arima' retorne '302...' sin login")
        self.log.info(" - [OK] Que POST a 'buscar_paramateros_arima' retorne '302...' sin login")
    

    def test_views_params_arima_post_ok(self):
        self.client.force_login(self.usuarioTest)
        form_data = {
            'ticker_a_buscar': 'IBM',
            'num_sesiones': '200',
        }
        response = self.client.post('/lab/buscar_paramateros_arima/', data=form_data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'buscar_paramateros_arima' retorne '200 ok' con login")
        self.log.info(" - [OK] Que POST a 'buscar_paramateros_arima' retorne '200 ok' con login")
        

    def test_views_params_arima_post_con_num_sesiones_no_válido_1(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/buscar_paramateros_arima/', data=self.form_param_arima_no_ok_1)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'buscar_paramateros_arima' retorne mensaje con num_sesiones no válido")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'buscar_paramateros_arima' retorne mensaje con nº de sesiones no válida")


    def test_views_params_arima_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/buscar_paramateros_arima/', data=self.form_param_arima_no_ok_2)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'buscar_paramateros_arima' retorne mensaje con ticker no válida")
        self.assertContains(response, 'no está disponibe')
        self.log.info(" - [OK] Que post a 'buscar_paramateros_arima' retorne mensaje con ticker no válida")

    # -------------------
    # TESTS ARIMA REJILLA
    # -------------------
    def test_views_arima_rejilla_status_code(self): 
        self.client.force_login(self.usuarioTest)       
        response = self.client.get('/lab/arima_rejilla/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de arima_rejilla retorne '200 ok'")
        self.log.info(" - [OK] Que página de arima_rejilla retorne '200 ok'")


    def test_views_arima_rejilla_templates_válidas(self):
        self.client.force_login(self.usuarioTest)   
        response = self.client.get('/lab/arima_rejilla/')   
        self.assertTemplateUsed(response, 'arima_rejilla.html', " - [NO OK] Asignar 'template' de arima_rejilla y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de arima_rejilla y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de arima_rejilla y cargar base.html")


    def test_views_arima_rejilla_templates_no_válidas(self):  
        self.client.force_login(self.usuarioTest) 
        response = self.client.get('/lab/arima_rejilla/')      
        self.assertTemplateNotUsed(response, 'lab.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_auto.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_manual.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'lstm.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")
    
    def test_views_arima_rejilla_post_ok(self):
        self.client.force_login(self.usuarioTest)
        form_data = {
            'ticker_a_buscar': 'IBM',
            'num_sesiones': '200',
            'porcentaje_entrenamiento': '70%',
            'auto': False,
            'manual': False,
            'rejilla': True,
            'valores_p': '[0, 1]',
            'valores_d': '[1, 2]',
            'valores_q': '[0, 1]'
        }
        response = self.client.post('/lab/arima_rejilla/', data=form_data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'arima_rejilla' retorne '200 ok' con login")
        self.log.info(" - [OK] Que POST a 'arima_rejilla' retorne '200 ok' con login")


    def test_views_arima_rejilla_post_con_num_sesiones_no_válido_1(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_1)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con num_sesiones no válido")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con nº de sesiones no válida")


    def test_views_arima_rejilla_post_con_num_sesiones_no_válido_2(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_2)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con num_sesiones no válida")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con nº de sesiones no válida")


    def test_views_arima_rejilla_post_con_porcentaje_entrenamiento_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_3)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con porcentaje_entrenamiento no válido")
        self.assertContains(response, 'Porcentaje indicado no válido')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con porcentaje_entrenamiento no válido")


    def test_views_arima_rejilla_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_4)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con ticker no válida")
        self.assertContains(response, 'no está disponibe')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con ticker no válida")


    def test_views_arima_rejilla_post_con_p_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_5)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con valores p no válidos")
        # print(response.content)
        self.assertContains(response, 'no válidos')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con valores p no válidos")

    
    def test_views_arima_rejilla_post_con_d_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_6)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con valores d no válidos")
        self.assertContains(response, 'no válidos')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con valores d no válidos")

    
    def test_views_arima_rejilla_post_con_q_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_no_ok_7)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_rejilla' retorne mensaje con valores q no válidos")
        self.assertContains(response, 'no válidos')
        self.log.info(" - [OK] Que post a 'arima_rejilla' retorne mensaje con valores q no válidos")
    
    
    # ------------------
    # TESTS ARIMA MANUAL
    # ------------------
    def test_views_arima_manual_status_code(self):   
        self.client.force_login(self.usuarioTest)     
        response = self.client.get('/lab/arima_manual/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de arima_manual retorne '200 ok'")
        self.log.info(" - [OK] Que página de arima_manual retorne '200 ok'")


    def test_views_arima_manual_templates_válidas(self):  
        self.client.force_login(self.usuarioTest) 
        response = self.client.get('/lab/arima_manual/')   
        self.assertTemplateUsed(response, 'arima_manual.html', " - [NO OK] Asignar 'template' de arima_manual y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de arima_manual y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de arima_manual y cargar base.html")


    def test_views_arima_manual_templates_no_válidas(self):  
        self.client.force_login(self.usuarioTest) 
        response = self.client.get('/lab/arima_manual/')      
        self.assertTemplateNotUsed(response, 'lab.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_auto.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_rejilla.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'lstm.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")


    def test_views_arima_manual_post_ok(self):
        self.client.force_login(self.usuarioTest)
        form_data = {
            'ticker_a_buscar': 'IBM',
            'num_sesiones': '200',
            'porcentaje_entrenamiento': '70%',
            'auto': False,
            'manual': True,
            'rejilla': False,
            'valor_p': 2,
            'valor_d': 1,
            'valor_q': 1
        }
        response = self.client.post('/lab/arima_manual/', data=form_data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'arima_manual' retorne '200 ok' con login")
        self.log.info(" - [OK] Que POST a 'arima_manual' retorne '200 ok' con login")


    def test_views_arima_manual_post_con_num_sesiones_no_válido_1(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_1)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con num_sesiones no válido")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con nº de sesiones no válida")


    def test_views_arima_manual_post_con_num_sesiones_no_válido_2(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_2)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con num_sesiones no válida")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con nº de sesiones no válida")


    def test_views_arima_manual_post_con_porcentaje_entrenamiento_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_3)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con porcentaje_entrenamiento no válido")
        self.assertContains(response, 'Porcentaje indicado no válido')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con porcentaje_entrenamiento no válido")


    def test_views_arima_manual_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_4)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con ticker no válida")
        self.assertContains(response, 'no está disponibe')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con ticker no válida")


    def test_views_arima_manual_post_con_p_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_5)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con valores p no válidos")
        # print(response.content)
        self.assertContains(response, 'no válido')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con valores p no válidos")

    
    def test_views_arima_manual_post_con_d_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_6)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con valores d no válidos")
        self.assertContains(response, 'no válido')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con valores d no válidos")

    
    def test_views_arima_manual_post_con_q_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/arima_manual/', data=self.form_arima_manual_no_ok_7)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'arima_manual' retorne mensaje con valores q no válidos")
        self.assertContains(response, 'no válido')
        self.log.info(" - [OK] Que post a 'arima_manual' retorne mensaje con valores q no válidos")
    

    # ----------
    # TESTS LSTM
    # ----------
    def test_views_lstm_status_code(self):
        self.client.force_login(self.usuarioTest)        
        response = self.client.get('/lab/lstm/')
        self.assertEqual(response.status_code, 200, " - [NO OK] Que página de lstm retorne '200 ok'")
        self.log.info(" - [OK] Que página de lstm retorne '200 ok'")


    def test_views_lstm_templates_válidas(self):
        self.client.force_login(self.usuarioTest)   
        response = self.client.get('/lab/lstm/')   
        self.assertTemplateUsed(response, 'lstm.html', " - [NO OK] Asignar 'template' de lstm y cargar base.html")
        self.assertTemplateUsed(response, 'base.html', " - [NO OK] Asignar 'template' de lstm y cargar base.html")
        self.log.info(" - [OK] Asignar 'template' de lstm y cargar base.html")


    def test_views_lstm_templates_no_válidas(self):
        self.client.force_login(self.usuarioTest)   
        response = self.client.get('/lab/lstm/')      
        self.assertTemplateNotUsed(response, 'lab.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_auto.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_rejilla.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.assertTemplateNotUsed(response, 'arima_rejilla.html', " - [NO OK] No utilizar otros 'templates' por error")
        self.log.info(" - [OK] No utilizar otros 'templates' por error")
    

    def test_views_lstm_post_ok(self):
        self.client.force_login(self.usuarioTest)
        form_data = {
            'ticker_a_buscar': 'IBM',
            'num_sesiones': '450',
            'porcentaje_entrenamiento': '70%',
        }
        response = self.client.post('/lab/lstm/', data=form_data)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'lstm' retorne '200 ok' con login")
        self.log.info(" - [OK] Que POST a 'lstm' retorne '200 ok' con login")


    def test_views_lstm_post_con_num_sesiones_no_válido_1(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/lstm/', data=self.form_lstm_no_ok_1)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'lstm' retorne mensaje con num_sesiones no válido")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'lstm' retorne mensaje con nº de sesiones no válida")


    def test_views_lstm_post_con_num_sesiones_no_válido_2(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/lstm/', data=self.form_lstm_no_ok_2)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'lstm' retorne mensaje con num_sesiones no válida")
        self.assertContains(response, 'Valor no válido para el nº de sesiones')
        self.log.info(" - [OK] Que post a 'lstm' retorne mensaje con nº de sesiones no válida")


    def test_views_lstm_post_con_porcentaje_entrenamiento_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/lstm/', data=self.form_lstm_no_ok_3)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'lstm' retorne mensaje con porcentaje_entrenamiento no válido")
        self.assertContains(response, 'Porcentaje indicado no válido')
        self.log.info(" - [OK] Que post a 'lstm' retorne mensaje con porcentaje_entrenamiento no válido")


    def test_views_lstm_post_con_ticker_no_válido(self):
        self.client.force_login(self.usuarioTest)
        response = self.client.post('/lab/lstm/', data=self.form_lstm_no_ok_4)
        self.assertEqual(response.status_code, 200, " - [NO OK] Que post a 'lstm' retorne mensaje con ticker no válida")
        self.assertContains(response, 'no está disponibe')
        self.log.info(" - [OK] Que post a 'lstm' retorne mensaje con ticker no válida")


    # ------------------
    # MÉTODOS AUXILIARES
    # ------------------
    def test_views_preprocesar_p_d_q_arima_auto(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/arima_auto', {'num_sesiones': '200', 'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': '200',
            'porcentaje_entrenamiento': '70%',
            'auto': True,
            'manual': False,
            'rejilla': False,
        }
        form = ArimaAutoForm(data=form_data)
        # Primero compruebo que el formulario sea válido
        self.assertTrue(form.is_valid(), " - [NO OK] Preprocesado ARIMA auto")
        order, fechas, tam_entrenamiento, datos, context = _preprocesar_p_d_q(ticker, form, request)
        self.assertIsNotNone(order, " - [NO OK] Preprocesado ARIMA auto")
        self.assertIsNotNone(fechas, " - [NO OK] Preprocesado ARIMA auto")
        self.assertIsNotNone(tam_entrenamiento, " - [NO OK] Preprocesado ARIMA auto")
        self.assertIsNotNone(datos, " - [NO OK] Preprocesado ARIMA auto")
        self.assertIsNone(context, " - [NO OK] Preprocesado ARIMA auto")
        self.log.info(" - [OK] Preprocesado ARIMA auto")
    

    def test_views_preprocesar_p_d_q_arima_manual(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/arima_manual', {'num_sesiones': '200', 'porcentaje_entrenamiento': '70%', 'valor_p': 1, 'valor_d': 2, 'valor_q': 1,})
        form_data = {
            'num_sesiones': '200',
            'porcentaje_entrenamiento': '70%',
            'auto': False,
            'manual': True,
            'rejilla': False,
            'valor_p': 1,
            'valor_d': 2,
            'valor_q': 1,
        }
        form = ArimaManualForm(data=form_data)
        # Primero compruebo que el formulario sea válido
        self.assertTrue(form.is_valid(), " - [NO OK] Preprocesado ARIMA manual")
        order, fechas, tam_entrenamiento, datos, context = _preprocesar_p_d_q(ticker, form, request)
        self.assertIsNotNone(order, " - [NO OK] Preprocesado ARIMA manual")
        self.assertIsNotNone(fechas, " - [NO OK] Preprocesado ARIMA manual")
        self.assertIsNotNone(tam_entrenamiento, " - [NO OK] Preprocesado ARIMA manual")
        self.assertIsNotNone(datos, " - [NO OK] Preprocesado ARIMA manual")
        self.assertIsNone(context, " - [NO OK] Preprocesado ARIMA manual")
        self.log.info(" - [OK] Preprocesado ARIMA manual")
    

    def test_views_preprocesar_p_d_q_arima_rejilla(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/arima_rejilla', {'num_sesiones': '200', 'porcentaje_entrenamiento': '70%', 'valores_p': '[0, 1]', 'valores_d': '[1, 2]', 'valores_q': '[0, 1]'})
        form_data = {
            'num_sesiones': '200',
            'porcentaje_entrenamiento': '70%',
            'auto': False,
            'manual': False,
            'rejilla': True,
            'valores_p': '[0, 1]',
            'valores_d': '[1, 2]',
            'valores_q': '[0, 1]',
        }
        form = ArimaRejillaForm(data=form_data)
        # Primero compruebo que el formulario sea válido
        self.assertTrue(form.is_valid(), " - [NO OK] Preprocesado ARIMA rejilla")
        order, fechas, tam_entrenamiento, datos, context = _preprocesar_p_d_q(ticker, form, request)
        # En este caso el order sí será None para evitar hacer todo el
        # proceso de evaluación walk forward durante los tests
        self.assertIsNotNone(order, " - [NO OK] Preprocesado ARIMA rejilla")
        self.assertIsNotNone(fechas, " - [NO OK] Preprocesado ARIMA rejilla")
        self.assertIsNotNone(tam_entrenamiento, " - [NO OK] Preprocesado ARIMA rejilla")
        self.assertIsNotNone(datos, " - [NO OK] Preprocesado ARIMA rejilla")
        self.assertIsNone(context, " - [NO OK] Preprocesado ARIMA rejilla")
        self.log.info(" - [OK] Preprocesado ARIMA rejilla")
    

    def test_views_evaluar_modelo_arima_mse(self):
        datos_entrenamiento = pd.Series([1, 2, 3, 4, 5])
        datos_test = pd.Series([6, 7, 8, 9, 10])
        order = (1, 0, 1)
        # Llamo a la función
        mse = _evaluar_modelo_arima_mse(datos_entrenamiento, datos_test, order)
        # He calculado el MSE esperado previamente
        self.assertAlmostEqual(mse, 0.4642512, delta=0.001)
        self.log.info(" - [OK] Evaluar ARIMA con MSE")

    
    def test_views_comprobar_formulario_arima_num_sesiones(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/arima_auto', {'num_sesiones': 'valorNoVálido', 'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 'valorNoVálido',
            'porcentaje_entrenamiento': '70%',
            'auto': True,
            'manual': False,
            'rejilla': False,
        }
        form = ArimaAutoForm(data=form_data)
        contexto = _comprobar_formularios(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones formulario ARIMA")
        self.assertEquals(contexto["msg_error"], 'Valor no válido para el nº de sesiones', 
                          " - [NO OK] Comprobar num_sesiones formulario ARIMA")
        self.log.info(" - [OK] Comprobar num_sesiones formulario ARIMA")
    
    
    def test_views_validacion_walk_forward_arima(self):
        tam_entrenamiento = 7
        datos = pd.Series([1, 7, 3, 43, 5, 6, 7, 81, 9, 17])
        order = (1, 0, 1)
        modelo_fit, aciertos_tendencia, predicciones = _validacion_walk_forward_arima(tam_entrenamiento, datos, order)
        # Comprobación de los tipos devueltos. No puedo conocer los
        # valores previamente:
        self.assertIsNotNone(modelo_fit, " - [NO OK] Validación walk forward ARIMA")
        self.assertIsInstance(aciertos_tendencia, list, " - [NO OK] Validación walk forward ARIMA")
        self.assertIsInstance(predicciones, list, " - [NO OK] Validación walk forward ARIMA")
        self.assertEqual(len(aciertos_tendencia), len(predicciones), " - [NO OK] Validación walk forward ARIMA")
        self.log.info(" - [OK] Validación walk forward ARIMA")
    

    def test_views_generar_resultados_arima(self):
        form_data = {
            'num_sesiones': 10,
            'porcentaje_entrenamiento': '70%',
            'auto': True,
            'manual': False,
            'rejilla': False,
        }
        form = ArimaAutoForm(data=form_data)
        conjunto_total = pd.Series([1, 7, 3, 43, 5, 6, 7, 81, 9, 17])
        modelo = ARIMA(conjunto_total, order=(1,0,1))
        modelo_fit = modelo.fit()
        fechas = pd.Series([1, 7, 3, 43, 5, 6, 7, 81, 9, 17])
        predicciones = [3, 4, 5]
        tam_entrenamiento = 7
        datos = pd.Series([1, 7, 3, 43, 5, 6, 7, 81, 9, 17]) 
        aciertos_tendencia = [True, False, True] 
        order = (1, 0, 1)
        ticker = 'IBM'
        # Genero unos resultados ficticios para comprobar qué se devuelve
        context = _generar_resultados_arima(form, modelo_fit, fechas, predicciones, tam_entrenamiento, datos, aciertos_tendencia, order, ticker)
        self.assertIsInstance(context, dict, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('lista_tickers', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('form', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('forecast_arima_walk_forward', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('resumen', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('mse', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('rmse', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('aciertos_tendencia', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('fallos_tendencia', context, " - [NO OK] Generar resultados ARIMA")

        self.assertIn('forecast_arima_intervalos_conf', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('mse_2', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('rmse_2', context, " - [NO OK] Generar resultados ARIMA")
        self.assertIn('rmse_naive', context, " - [NO OK] Generar resultados ARIMA")

        self.log.info(" - [OK] Generar resultados ARIMA")


    def test_views_preprocesado_lstm(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        form_data = {
            'num_sesiones': '450',
            'porcentaje_entrenamiento': '70%',
        }
        request = request_factory.post('/lab/lstm', form_data)
        form = LstmForm(form_data)
        # Primero compruebo que el formulario es válido
        self.assertTrue(form.is_valid(), " - [NO OK] Preprocesado LSTM")
        look_back, X_norm, y_norm, df, tam_entrenamiento, scaler = _preprocesado_lstm(ticker, form, request)
        self.assertIsInstance(look_back, int, " - [NO OK] Preprocesado LSTM")
        self.assertIsInstance(X_norm, np.ndarray, " - [NO OK] Preprocesado LSTM")
        self.assertIsInstance(y_norm, np.ndarray, " - [NO OK] Preprocesado LSTM")
        self.assertIsInstance(df, pd.DataFrame, " - [NO OK] Preprocesado LSTM")
        self.assertIsInstance(tam_entrenamiento, int, " - [NO OK] Preprocesado LSTM")
        self.assertIsInstance(scaler, MinMaxScaler, " - [NO OK] Preprocesado LSTM")
        self.log.info(" - [OK] Preprocesado LSTM")
    

    def test_views_preprocesado_lstm_con_fallos(self):
        ticker = 'tickerFalso'
        request_factory = RequestFactory()
        form_data = {
            'num_sesiones': '450',
            'porcentaje_entrenamiento': '70%',
        }
        request = request_factory.post('/lab/lstm', form_data)
        form = LstmForm(form_data)
        # Primero compruebo que el formulario es válido
        self.assertTrue(form.is_valid(), " - [NO OK] Preprocesado LSTM con fallos")
        response = _preprocesado_lstm(ticker, form, request)
        self.assertIsInstance(response, HttpResponse, " - [NO OK] Preprocesado LSTM con fallos")
        self.assertContains(response, 'El ticker tickerFalso no está disponibe')
        self.log.info(" - [OK] Preprocesado LSTM con fallos")
    

    def test_views_creacion_modelo(self):
        look_back = 3
        # X input del modelo, y output del modelo
        X_norm = np.random.rand(100, 1, look_back)
        y_norm = np.random.rand(100, 1)
        modelo = _crear_modelo(look_back, X_norm, y_norm)
        self.assertIsInstance(modelo, Sequential, " - [NO OK] Crear modelo LSTM")
        # Sólo hay 2 capas (entrada y salida)
        self.assertEqual(len(modelo.layers), 2, " - [NO OK] Crear modelo LSTM")
        # Comprobar características de las capas
        self.assertIsInstance(modelo.layers[0], LSTM, " - [NO OK] Crear modelo LSTM")
        self.assertEqual(modelo.layers[0].units, 5, " - [NO OK] Crear modelo LSTM")
        self.assertIsInstance(modelo.layers[1], Dense, " - [NO OK] Crear modelo LSTM")
        self.assertEqual(modelo.layers[1].units, 1, " - [NO OK] Crear modelo LSTM")
        # Comprobar otros parámetros
        self.assertEqual(modelo.loss, 'mean_squared_error', " - [NO OK] Crear modelo LSTM")
        self.log.info(" - [OK] Crear modelo LSTM")
    

    def test_views_comprobar_formulario_lstm_num_sesiones_mal_1(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/lstm', {'num_sesiones': 'valorNoVálido', 'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': 'valorNoVálido',
            'porcentaje_entrenamiento': '70%',
        }
        form = LstmForm(data=form_data)
        contexto = _comprobar_formulario_lstm(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones (1) formulario LSTM")
        self.assertEquals(contexto["msg_error"], 'Valor no válido para el nº de sesiones', 
                          " - [NO OK] Comprobar num_sesiones (1) formulario LSTM")
        self.log.info(" - [OK] Comprobar num_sesiones (1) formulario LSTM")
    

    def test_views_comprobar_formulario_lstm_num_sesiones_mal_2(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/lstm', {'num_sesiones': '1500', 'porcentaje_entrenamiento': '70%'})
        form_data = {
            'num_sesiones': '1500',
            'porcentaje_entrenamiento': '70%',
        }
        form = LstmForm(data=form_data)
        contexto = _comprobar_formulario_lstm(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones (2) formulario LSTM")
        self.assertEquals(contexto["msg_error"], 'Valor no válido para el nº de sesiones', 
                          " - [NO OK] Comprobar num_sesiones (2) formulario LSTM")
        self.log.info(" - [OK] Comprobar num_sesiones (2) formulario LSTM")
    

    def test_views_comprobar_formulario_lstm_porcentaje_mal(self):
        ticker = 'IBM'
        request_factory = RequestFactory()
        request = request_factory.post('/lab/lstm', {'num_sesiones': '750', 'porcentaje_entrenamiento': '150%'})
        form_data = {
            'num_sesiones': '750',
            'porcentaje_entrenamiento': '150%',
        }
        form = LstmForm(data=form_data)
        contexto = _comprobar_formulario_lstm(form, ticker, request)
        # False indicaría que no hay errores
        self.assertIsNotNone(contexto, " - [NO OK] Comprobar num_sesiones (2) formulario LSTM")
        self.assertEquals(contexto["msg_error"], 'Porcentaje indicado no válido', 
                          " - [NO OK] Comprobar num_sesiones (2) formulario LSTM")
        self.log.info(" - [OK] Comprobar num_sesiones (2) formulario LSTM")
    

    def test_views_validacion_walk_forward_lstm(self):
        tam_entrenamiento = 7
        df = pd.DataFrame(data={'close': [1, 7, 3, 43, 5, 6, 7, 81, 9, 17, 16], 'siguiente_dia': [7, 3, 43, 5, 6, 7, 81, 9, 17, 16, 1]})
        look_back = 1
        # X input del modelo, y output del modelo
        scaler = MinMaxScaler(feature_range=(0, 1))
        X = df['close'].values[:-1]
        X = X.reshape(-1, look_back, 1)
        X_norm = scaler.fit_transform(X.reshape(-1, 1))
        y_norm  = scaler.fit_transform(df['siguiente_dia'].values[:-1].reshape(-1, 1))
        modelo = _crear_modelo(look_back, X_norm, y_norm)
        predicciones, aciertos_tendencia = _validacion_walk_forward_lstm(df, tam_entrenamiento, scaler, look_back, modelo)
        # Comprobación de los tipos devueltos. No puedo conocer los
        # valores previamente:
        self.assertIsInstance(aciertos_tendencia, list, " - [NO OK] Validación walk forward LSTM")
        self.assertIsInstance(predicciones, list, " - [NO OK] Validación walk forward LSTM")
        self.assertEqual(len(aciertos_tendencia), len(predicciones), " - [NO OK] Validación walk forward LSTM")
        self.log.info(" - [OK] Validación walk forward LSTM")


    def test_views_generar_resultados_lstm(self):
        form = LstmForm
        tam_entrenamiento = 7
        df = pd.DataFrame(data={'close': [1, 7, 3, 43, 5, 6, 7, 81, 9, 17, 16], 'siguiente_dia': [7, 3, 43, 5, 6, 7, 81, 9, 17, 16, 1], 'date': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]})
        look_back = 1
        # X input del modelo, y output del modelo
        scaler = MinMaxScaler(feature_range=(0, 1))
        X = df['close'].values[:-1]
        X = X.reshape(-1, look_back, 1)
        X_norm = scaler.fit_transform(X.reshape(-1, 1))
        y_norm  = scaler.fit_transform(df['siguiente_dia'].values[:-1].reshape(-1, 1))
        modelo = _crear_modelo(look_back, X_norm, y_norm)
        predicciones, aciertos_tendencia = _validacion_walk_forward_lstm(df, tam_entrenamiento, scaler, look_back, modelo)
        # Genero unos resultados ficticios para comprobar qué se devuelve
        context = _generar_resultados_lstm(form, scaler, look_back, modelo, predicciones, tam_entrenamiento, df, aciertos_tendencia)
        self.assertIsInstance(context, dict, " - [NO OK] Generar resultados LSTM")
        self.assertIn('lista_tickers', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('form', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('forecast_lstm', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('resumen', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('mse', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('rmse', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('prediccion_prox_sesion', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('aciertos_tendencia', context, " - [NO OK] Generar resultados LSTM")
        self.assertIn('fallos_tendencia', context, " - [NO OK] Generar resultados LSTM")
        self.log.info(" - [OK] Generar resultados LSTM")
