from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib import admin
from django.views.static import serve
from django.conf import settings

# Refactoring:
# ------------
# No me he percatado de la necesidad de realizar estos tests
# hasta que he empezado a seguir la metodología TDD en la app
# DashBoard
class TestFATUrls(SimpleTestCase):

    def test_url_static(self):
        # No se puede usar reverse() porque no tengo url de static
        # url = reverse('static', kwargs={'path': 'Logo.png'})
        url = f'/static/Test.png'
        self.assertEquals(resolve(url).func, serve)
        self.assertEquals(resolve(url).kwargs['document_root'], settings.STATIC_ROOT)

    def test_url_media(self):
        url = f'/media/Test.jpg'
        self.assertEquals(resolve(url).func, serve)
        self.assertEquals(resolve(url).kwargs['document_root'], settings.MEDIA_ROOT)
    
    def test_url_admin(self):
        url = reverse('admin:index')
        self.assertEquals(resolve(url).func.__name__, admin.site.index.__name__)

    # Las URLs de las apps con 'include' se testean en sus 
    # correspondientes archivos de test

    
