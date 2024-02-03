from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Analysis.views import mapa_stocks, signup, signout, signin, chart_y_datos

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestAnalysisUrls(SimpleTestCase):
    
    def test_url_dashboard(self):
        url = reverse('mapa_stocks')
        self.assertEquals(resolve(url).func, mapa_stocks)

    def test_url_nueva_compra(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, signup)

    def test_url_eliminar_compras(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, signout)

    def test_url_nuevo_seguimiento(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, signin)

    def test_url_nuevo_seguimiento(self):
        url = reverse('chart_y_datos')
        self.assertEquals(resolve(url).func, chart_y_datos)