from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Analysis.views import mapa_stocks, signup, signout, signin, chart_y_datos

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestAnalysisUrls(SimpleTestCase):
    
    def test_url_mapa_stocks(self):
        url = reverse('mapa_stocks', args=['dj30'])
        self.assertEquals(resolve(url).func, mapa_stocks)

    def test_url_signup(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, signup)

    def test_url_logout(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, signout)

    def test_url_login(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, signin)

    def test_url_chart_y_datos(self):
        url = reverse('chart_y_datos', args=['SAN_MC', 'ibex35'])
        self.assertEquals(resolve(url).func, chart_y_datos)