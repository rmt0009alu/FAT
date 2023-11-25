from django.urls import path
from .views import hello, stock_data

urlpatterns = [
     
    path('', hello, name="hello"),

    # http://127.0.0.1:8000
    # path('', views.index),
    # path('', stock_data, name='stock_data'),

    # path('prueba/', stock_data, name='prueba'),
    # path('stock_data/<str:ticker>/', stock_data, name='stock_data'),
    path('stock_data/<str:ticker>/', stock_data, name='stock_data'),
    
]
