from django.test import TestCase
from Lab.views import lab, arima_auto, arima_rejilla, arima_manual, lstm
from log.logger.logger import get_logger_configurado
from datetime import datetime, timezone, timedelta
import pandas as pd
from django.contrib.auth.models import User
# Para usar los modelos creados de forma dinámica
from django.apps import apps



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


    # -------------------------------------------------------------------
    # def test_views_arima_auto_post_con_login(self):
    #     self.client.force_login(self.usuarioTest)
    #     response = self.client.post('/lab/arima_auto/', data=self.form_arima_auto_ok)
    #     self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'arima_auto' retorne '200 ok' con login")
    #     self.log.info(" - [OK] Que POST a 'arima_auto' retorne '200 ok' con login")
    # -------------------------------------------------------------------
        

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
    
    # -------------------------------------------------------------------
    # def test_views_arima_rejilla_post_con_login(self):
    #     self.client.force_login(self.usuarioTest)
    #     response = self.client.post('/lab/arima_rejilla/', data=self.form_arima_rejilla_ok)
    #     self.assertEqual(response.status_code, 200, " - [NO OK] Que POST a 'arima_rejilla' retorne '200 ok' con login")
    #     self.log.info(" - [OK] Que POST a 'arima_rejilla' retorne '200 ok' con login")
    # -------------------------------------------------------------------

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
    