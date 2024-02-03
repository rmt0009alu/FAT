from django.test import SimpleTestCase
from django.urls import reverse, resolve
from News.views import home

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestNewsUrls(SimpleTestCase):
    
    def test_url_home(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, home)
