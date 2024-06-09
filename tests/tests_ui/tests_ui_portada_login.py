import os
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.urls import reverse
from datetime import datetime, timezone
from django.apps import apps
from Analysis.models import Sectores
from datetime import timedelta
from selenium.webdriver import Keys
from util.tickers.Tickers_BDs import tickers_adaptados_dj30, tickers_adaptados_ibex35, tickers_adaptados_ftse100, tickers_adaptados_dax40, bases_datos_disponibles


class PruebasUI(LiveServerTestCase):

    databases = '__all__'

    def setUp(self):
        # Obtener la ruta completa del directorio actual
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Construir la ruta completa al chromedriver
        chromedriver_path = os.path.join(current_directory, 'chromedriver.exe')

        chrome_options = Options()
        # Descomentar esta línea para ejecutar en modo headless
        # chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Abrir a pantalla completa para evitar problemas de checkeo de desplegables
        # de bootstrap
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disk-cache-size=0")

        # Inicializar el webdriver de Chrome utilizando la ruta especificada y opciones
        try:
            self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
        except Exception as e:
            print(f"Error con el Chrome WebDriver: {e}")

        for ticker in tickers_adaptados_dj30():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='USD', sector=f'sector{ticker}'
            )

        for ticker in tickers_adaptados_ibex35():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ibex35').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='EUR', sector=f'sector{ticker}'
            )

        for ticker in tickers_adaptados_ftse100():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('ftse100').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='GBp', sector=f'sector{ticker}'
            )

        for ticker in tickers_adaptados_dax40():
            model = apps.get_model('Analysis', ticker)
            self.ficticio = model.objects.using('dax40').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker=ticker, previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name=f'nombre{ticker}', 
                currency='EUR', sector=f'sector{ticker}'
            )


    def tearDown(self):
        # Cerrar el navegador después de la prueba
        self.driver.quit()


    def test_01_pagina_principal(self):
        # Navegar a la página del servidor de prueba de Django
        self.driver.get(self.live_server_url)

        # Verifica que el título de la página contiene "FAT: Financial Analysis Tool"
        self.assertIn("FAT: Financial Analysis Tool", self.driver.title)


    def test_02_pagina_principal_artículos(self):
        # self.client.login(username='testuser', password='testpassword')
        self.driver.get(self.live_server_url + reverse('home'))
        
        wait = WebDriverWait(self.driver, 10)
        _ = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carousel-item")))

        items_carrusel = self.driver.find_elements(By.CLASS_NAME, 'carousel-item')
        self.assertGreater(len(items_carrusel), 0, "No hay items en el carrusel")

        item_1_carrusel = items_carrusel[0]
        self.assertIn('active', item_1_carrusel.get_attribute('class'), "Carrusel con artículo no exsistente")

        imagen = item_1_carrusel.find_element(By.TAG_NAME, 'img')
        self.assertTrue(imagen.get_attribute('src'), "Src de imagen vacía")
        
        titulo = item_1_carrusel.find_element(By.TAG_NAME, 'h4')
        self.assertTrue(titulo.text, "Título de artículo vacío")

        desc_art = item_1_carrusel.find_element(By.XPATH, './div/div[2]')
        self.assertTrue(desc_art.text, "Descripción de artículo vacía")

        link_leer_mas = item_1_carrusel.find_element(By.LINK_TEXT, 'Leer más')
        self.assertTrue(link_leer_mas.get_attribute('href'), "Link de 'lee más' vacío")


    def test_03_pagina_principal_mejores_peores(self):
        # Se comprueba el primero únicamente, porque los demás van en la misma lista
        # y usan las mismas plantillas
        self.driver.get(self.live_server_url + reverse('home'))
        wait = WebDriverWait(self.driver, 10)

        # Verify "Mejores y peores del DJ30" title
        titulo_dj30 = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "barra")))
        self.assertEqual(titulo_dj30.text, "Mejores y peores del DJ30")
        carousel_dj30 = wait.until(EC.presence_of_element_located((By.ID, "stockCarousels")))
        self.assertTrue(carousel_dj30.is_displayed())

    
    def test_04_login(self):
        # Usuario de tests
        user = User.objects.create_user(username='testuser', password='testpassword')

        self.driver.get(self.live_server_url + reverse('login'))

        login_form = self.driver.find_element(By.TAG_NAME, 'form')

        username_input = login_form.find_element(By.NAME, 'username')
        password_input = login_form.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        login_form.submit()

        # Al hacer login se carga el DashBoard
        self.assertIn("DashBoard", self.driver.page_source)
    
    
    def test_05_logout(self):
        # Usuario de tests
        user = User.objects.create_user(username='testuser', password='testpassword')

        self.driver.get(self.live_server_url + reverse('login'))

        login_form = self.driver.find_element(By.TAG_NAME, 'form')

        username_input = login_form.find_element(By.NAME, 'username')
        password_input = login_form.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        login_form.submit()

        # Al hacer login se carga el DashBoard
        self.assertIn("DashBoard", self.driver.page_source)

        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/logout')]"))).click()

        self.assertEqual(self.live_server_url + reverse('home'), self.driver.current_url)
    
    
    def test_06_registro(self):
        self.driver.get(self.live_server_url + reverse('signup'))

        # Coger los campos del formulario
        signup_form = self.driver.find_element(By.TAG_NAME, 'form')
        username_input = signup_form.find_element(By.NAME, 'username')
        password1_input = signup_form.find_element(By.NAME, 'password1')
        password2_input = signup_form.find_element(By.NAME, 'password2')

        # Rellenar el formulario
        username_input.send_keys('nuevoUsuario')
        password1_input.send_keys('PasswordL@rga')
        password2_input.send_keys('PasswordL@rga')

        # Enviar el formulario
        signup_form.submit()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Usuario creado correctamente.')]"))
        )

        self.assertIn("Usuario creado correctamente.", self.driver.page_source)


    def test_07_mostrar_tabla_de_valores(self):
        lista_dbs = ['dj30', 'ibex35', 'ftse100', 'dax40']
        for idx in lista_dbs:
            url = f"{self.live_server_url}/mapa/{idx}"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)

            tabla_stocks = wait.until(EC.presence_of_element_located((By.ID, "tablaStocks")))
            self.assertTrue(tabla_stocks.is_displayed())

            headers = tabla_stocks.find_elements(By.TAG_NAME, "th")
            self.assertEqual(len(headers), 8)
            headers_esperados = ["Nombre", "Último", "Máximo", "Mínimo", "Var.", "Var.(%)", "Volumen", "Fecha"]
            for i, header in enumerate(headers):
                self.assertEqual(header.text, headers_esperados[i])

            # Comprobar que hay filas (saltando la primera)
            filas = tabla_stocks.find_elements(By.TAG_NAME, "tr")[1:]
            self.assertGreater(len(filas), 0)

    def test_08_consultar_un_valor_de_indice(self):
        
        # Se crean dos valores del mismo sector y con datos suficientes
        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )
        model = apps.get_model('Analysis', 'AAPL')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='AAPL', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='Apple Inc.', 
                currency = 'USD', sector = 'Technology'
            )

        # Y creo la tabla ficticia de sectores:
        Sectores.objects.create(ticker_bd='IBM', bd='dj30', ticker='IBM',
                                nombre='International Business Machines Corporation',
                                sector='Technology')  
        Sectores.objects.create(ticker_bd='AAPL', bd='dj30', ticker='AAPL',
                                nombre='Apple Inc.',
                                sector='Technology')

        _ = User.objects.create_user(username='testuser', password='testpassword')

        self.driver.get(self.live_server_url + reverse('login'))

        login_form = self.driver.find_element(By.TAG_NAME, 'form')

        username_input = login_form.find_element(By.NAME, 'username')
        password_input = login_form.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        login_form.submit()

        url = f"{self.live_server_url}/{'dj30'}/{'IBM'}/chart"
        self.driver.get(url)

        self.assertEqual(self.driver.title, 'FAT: Financial Analysis Tool') 

        cabecera = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.cabecera")))
        self.assertEqual(cabecera.text, "(IBM) International Business Machines Corporation")

        plotly_chart = self.driver.find_element(By.ID, "plotly-chart")
        self.assertTrue(plotly_chart.is_displayed())

        comparador_valores = self.driver.find_element(By.ID, "comparador")
        self.assertTrue(comparador_valores.is_displayed())

        grafica_retornos = self.driver.find_element(By.ID, "grafica_retornos")
        self.assertTrue(grafica_retornos.is_displayed())
    

    def test_09_dashboard_nueva_compra(self):
        # Se crea un valor para añadir como compra
        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )

        user = User.objects.create_user(username='testuser', password='testpassword')

        self.driver.get(self.live_server_url + reverse('login'))

        login_form = self.driver.find_element(By.TAG_NAME, 'form')

        username_input = login_form.find_element(By.NAME, 'username')
        password_input = login_form.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        login_form.submit()

        # Al hacer login se carga el DashBoard
        self.assertIn("DashBoard", self.driver.page_source)

        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/nueva_compra')]"))).click()

        self.assertIn('Añadir un nuevo stock a la cartera', self.driver.page_source)

        self.driver.get(f"{self.live_server_url}/dashboard/nueva_compra/")

        # Formulario ok
        form = self.driver.find_element(By.CSS_SELECTOR, "form.card-body")
        self.assertTrue(form.is_displayed())

        ticker_autocomplete = self.driver.find_element(By.ID, "ticker_autocomplete")
        fecha_compra = self.driver.find_element(By.ID, "fecha_compra")
        num_acciones = self.driver.find_element(By.NAME, "num_acciones")
        precio_compra = self.driver.find_element(By.NAME, "precio_compra")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        self.assertTrue(ticker_autocomplete.is_displayed())
        self.assertTrue(fecha_compra.is_displayed())
        self.assertTrue(num_acciones.is_displayed())
        self.assertTrue(precio_compra.is_displayed())
        self.assertTrue(submit_button.is_displayed())

        # Búsqueda de tickers
        ticker_autocomplete.send_keys("IBM")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-autocomplete li")))
        autocomplete_items = self.driver.find_elements(By.CSS_SELECTOR, ".ui-autocomplete li")
        self.assertTrue(len(autocomplete_items) > 0)  # Expect at least one suggestion

        # Simular creación de formulario
        ticker_autocomplete.send_keys("IBM")
        ticker_autocomplete.send_keys(Keys.DOWN)
        ticker_autocomplete.send_keys(Keys.ENTER)

        fecha_compra.send_keys("01/01/2025")
        fecha_compra.send_keys(Keys.ENTER)

        num_acciones.send_keys('50')
        precio_compra.send_keys('105')
        submit_button.click()
    

    
    def test_10_dashboard_nuevo_seguimiento(self):
        # Se crea un valor para añadir como compra
        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )

        user = User.objects.create_user(username='testuser', password='testpassword')

        self.driver.get(self.live_server_url + reverse('login'))

        login_form = self.driver.find_element(By.TAG_NAME, 'form')

        username_input = login_form.find_element(By.NAME, 'username')
        password_input = login_form.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        login_form.submit()

        # Al hacer login se carga el DashBoard
        self.assertIn("DashBoard", self.driver.page_source)

        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/nuevo_seguimiento')]"))).click()

        self.assertIn('Añadir un nuevo valor a seguir', self.driver.page_source)

        self.driver.get(f"{self.live_server_url}/dashboard/nuevo_seguimiento/")

        # Formulario ok
        form = self.driver.find_element(By.CSS_SELECTOR, "form.card-body")
        self.assertTrue(form.is_displayed())

        ticker_autocomplete = self.driver.find_element(By.ID, "ticker_autocomplete")
        precio_entrada_deseado = self.driver.find_element(By.NAME, "precio_entrada_deseado")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        self.assertTrue(ticker_autocomplete.is_displayed())
        self.assertTrue(precio_entrada_deseado.is_displayed())
        self.assertTrue(submit_button.is_displayed())

        # Búsqueda de tickers
        ticker_autocomplete.send_keys("IBM")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-autocomplete li")))
        autocomplete_items = self.driver.find_elements(By.CSS_SELECTOR, ".ui-autocomplete li")
        self.assertTrue(len(autocomplete_items) > 0)

        # Simular creación de formulario
        ticker_autocomplete.send_keys("IBM")
        ticker_autocomplete.send_keys(Keys.DOWN)
        ticker_autocomplete.send_keys(Keys.ENTER)

        precio_entrada_deseado.send_keys('105')

        # No tiene que haber resultados porque no se crean datos
        submit_button.click()
    
    
    def test_11_arima_manual(self):
        user = User.objects.create_user(username='testuser', password='testpassword')

        self.driver.get(self.live_server_url + reverse('login'))

        login_form = self.driver.find_element(By.TAG_NAME, 'form')

        username_input = login_form.find_element(By.NAME, 'username')
        password_input = login_form.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        login_form.submit()

        model = apps.get_model('Analysis', 'IBM')
        for i in range(220):
            model.objects.using('dj30').create(date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)+timedelta(days=i),
                open=100.0, high=110.0, low=90.0, close=105.0, volume=10000,
                dividends=1.0, stock_splits=2.0, ticker='IBM', previous_close=100.0,
                percent_variance=5.0, mm20=102.0, mm50=104.0, mm200=98.0, name='International Business Machines Corporation', 
                currency = 'USD', sector = 'Technology'
            )

        self.driver.get(f"{self.live_server_url}/lab/arima_manual/")

        form = self.driver.find_element(By.CSS_SELECTOR, "form.card-body")
        self.assertTrue(form.is_displayed())

        ticker_autocomplete = self.driver.find_element(By.ID, "ticker_autocomplete")
        num_sesiones_input = self.driver.find_element(By.ID, "id_num_sesiones")
        porcentaje_entrenamiento_input = self.driver.find_element(By.ID, "id_porcentaje_entrenamiento")
        valor_p_input = self.driver.find_element(By.ID, "id_valor_p")
        valor_d_input = self.driver.find_element(By.ID, "id_valor_d")
        valor_q_input = self.driver.find_element(By.ID, "id_valor_q")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        self.assertTrue(ticker_autocomplete.is_displayed())
        self.assertTrue(num_sesiones_input.is_displayed())
        self.assertTrue(porcentaje_entrenamiento_input.is_displayed())
        self.assertTrue(valor_p_input.is_displayed())
        self.assertTrue(valor_d_input.is_displayed())
        self.assertTrue(valor_q_input.is_displayed())
        self.assertTrue(submit_button.is_displayed())

        ticker_autocomplete.send_keys("IBM")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-autocomplete li")))
        autocomplete_items = self.driver.find_elements(By.CSS_SELECTOR, ".ui-autocomplete li")
        self.assertTrue(len(autocomplete_items) > 0)

        ticker_autocomplete.send_keys("IBM")
        ticker_autocomplete.send_keys(Keys.DOWN)
        ticker_autocomplete.send_keys(Keys.ENTER)

        num_sesiones_input.send_keys("200")
        porcentaje_entrenamiento_input.send_keys("66%")
        valor_p_input.send_keys("2")
        valor_d_input.send_keys("0")
        valor_q_input.send_keys("1")