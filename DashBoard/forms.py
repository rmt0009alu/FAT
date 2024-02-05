from django.forms import ModelForm
from .models import StockComprado, StockSeguimiento
from django import forms


class StockCompradoForm(ModelForm):
    """Clase que hace uso del ModelForm para crear
    un formulario para los stocks comprados siguiendo 
    el modelo definido en 'models'.

    Args:
        ModelForm (_type_): _description_
    """
    class Meta:
        # Modelo en el que está basado este formulario
        model = StockComprado
        # El usuario, por defecto, está auto indicado, así que no es 
        # necesario añadirlo a los campos del form. Además, el 'nombre_stock'
        # no lo uso directamente en el form para poder utilizar una caja de 
        # búsqueda autocompletada con JS. La 'fecha_compra' tampoco va en
        # en el form, para poder usar un DatePicker (calendario)
        fields = ['num_acciones', 'precio_compra']

        # Para que no aparezcan los nombres, porque quiero que se vean
        # sólo los placeholder
        labels = {
            'num_acciones': '',
            'precio_compra': '',
        }

        # Aprovecho los widgets para dar estilos
        widgets = {
            'num_acciones': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de acciones (valores enteros)'
        }),
            'precio_compra': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Precio de compra (máx. 10 dígitos con 4 decimales)'
        }),
    }



class StockSeguimientoForm(ModelForm):
    """Clase que hace uso del ModelForm para crear
    un formulario para los stocks en seguimiento.
    Hago uso del modelo definido en 'models'.

    Args:
        ModelForm (_type_): _description_
    """
    class Meta:
        # Modelo en el que está basado este formulario
        model = StockSeguimiento
        # El usuario, por defecto, está auto indicado, así que no es 
        # necesario añadirlo a los campos del form. Además, el 'nombre_stock'
        # no lo uso directamente en el form para poder utilizar una caja de 
        # búsqueda autocompletada con JS. 
        fields = ['precio_entrada_deseado']

        # Para que no aparezcan los nombres, porque quiero que se vean
        # sólo los placeholder
        labels = {
            'precio_entrada_deseado': '',
        }

        # Aprovecho los widgets para dar estilos
        widgets = {
            'precio_entrada_deseado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Precio entrada deseado (máx. 10 dígitos con 4 decimales)'
        }),
    }
