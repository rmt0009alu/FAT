"""
Formularios para usar con Lab.
"""
from django import forms

# NOTA: aquí no se hereda de ModelForm porque no hay modelo asociado

class ArimaAutoForm(forms.Form):
    """Clase que define el fomrulario para introducir los datos
    necearios para aplicar un modelo ARIMA cuyos parámetros (p,d,q)
    se obtienen de forma automática con 'arima_auto' de 'pmdarima'.

    Args:
        Form (django.forms.Form): tipo formulario de Django. 
    """
    # Validación de datos de cantidad de días
    num_sesiones = forms.IntegerField(
        min_value=100,
        max_value=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de últimas sesiones que se quiere analizar [100-500]'
        })
    )

    # Campo para indicar el % de datos de entrenamiento
    porcentaje_entrenamiento = forms.ChoiceField(
        choices=(
            ('50%', 50),
            ('66%', 66),
            ('70%', 70),
            ('80%', 80),
            ('90%', 90),
        ),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Porcentaje de datos para el entrenamiento'
        })
    )

    # Campos para indicar el tipo de cálculo para (p,d,q). Obligatorio
    # indicar que no son 'required' porque no se van a mostrar en el 'form'
    auto = forms.BooleanField(initial=True, required=False)
    manual = forms.BooleanField(initial=False, required=False)
    rejilla = forms.BooleanField(initial=False, required=False)


# Aquí no se hereda de ModelForm porque no hay modelo asociado
class ArimaRejillaForm(forms.Form):
    """Clase que define el fomrulario para introducir los datos
    necearios para aplicar un modelo ARIMA cuyos parámetros (p,d,q)
    se obtienen mediante búsqueda por rejilla. 

    Args:
        Form (django.forms.Form): tipo formulario de Django. 
    """
    # Validación de datos de cantidad de días
    num_sesiones = forms.IntegerField(
        min_value=100,
        max_value=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de últimas sesiones que se quiere analizar [100-500]'
        })
    )

    # Campo para indicar el % de datos de entrenamiento
    porcentaje_entrenamiento = forms.ChoiceField(
        choices=(
            ('50%', 50),
            ('66%', 66),
            ('70%', 70),
            ('80%', 80),
            ('90%', 90),
        ),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Porcentaje de datos para el entrenamiento'
        })
    )
    
    valores_p = forms.ChoiceField(
        choices=[
            ([0,1], '[0, 1]'),
            ([1,2], '[1, 2]'),
            ([0, 1, 2], '[0, 1, 2]'),
            ([1, 2, 3], '[1, 2, 3]'),
            ([2, 3, 4], '[2, 3, 4]'),
        ],
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Rango de posibles valores de 'p'"
        })
    )

    valores_d = forms.ChoiceField(
        choices=[
            ([0,1], '[0, 1]'),
            ([1,2], '[1, 2]'),
            ([0, 1, 2], '[0, 1, 2]'),
            ([1, 2, 3], '[1, 2, 3]'),
            ([2, 3, 4], '[2, 3, 4]'),
        ],
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Rango de posibles valores de 'd'"
        })
    )

    valores_q = forms.ChoiceField(
        choices=[
            ([0,1], '[0, 1]'),
            ([1,2], '[1, 2]'),
            ([0, 1, 2], '[0, 1, 2]'),
            ([1, 2, 3], '[1, 2, 3]'),
            ([2, 3, 4], '[2, 3, 4]'),
        ],
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Rango de posibles valores de 'q'"
        })
    )
    
    # Campos para indicar el tipo de cálculo para (p,d,q). Obligatorio
    # indicar que no son 'required' porque no se van a mostrar en el 'form'
    auto = forms.BooleanField(initial=False, required=False)
    manual = forms.BooleanField(initial=False, required=False)
    rejilla = forms.BooleanField(initial=True, required=False)


class ArimaManualForm(forms.Form):
    """Clase que define el fomrulario para introducir los datos
    necearios para aplicar un modelo ARIMA cuyos parámetros (p,d,q)
    son previamente conocidos por el usuario. 

    Args:
        Form (django.forms.Form): tipo formulario de Django. 
    """
    # Validación de datos de cantidad de días
    num_sesiones = forms.IntegerField(
        min_value=100,
        max_value=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de últimas sesiones que se quiere analizar [100-500]'
        })
    )

    # Campo para indicar el % de datos de entrenamiento
    porcentaje_entrenamiento = forms.ChoiceField(
        choices=(
            ('50%', 50),
            ('66%', 66),
            ('70%', 70),
            ('80%', 80),
            ('90%', 90),
        ),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Porcentaje de datos para el entrenamiento'
        })
    )
    
    valor_p = forms.IntegerField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Valor  de 'p' [0 - 10]"
        })
    )

    valor_d = forms.IntegerField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Valor  de 'd' [0 - 3]"
        })
    )

    valor_q = forms.IntegerField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Valor  de 'q' [0 - 10]"
        })
    )
    
    # Campos para indicar el tipo de cálculo para (p,d,q). Obligatorio
    # indicar que no son 'required' porque no se van a mostrar en el 'form'
    auto = forms.BooleanField(initial=False, required=False)
    manual = forms.BooleanField(initial=True, required=False)
    rejilla = forms.BooleanField(initial=False, required=False)


class LstmForm(forms.Form):
    """Clase que define el fomrulario para introducir los datos
    necearios para aplicar una red LSTM automáticamente. 

    Args:
        Form (django.forms.Form): tipo formulario de Django. 
    """
    # Validación de datos de cantidad de días
    num_sesiones = forms.IntegerField(
        min_value=400,
        max_value=1000,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de últimas sesiones que se quiere analizar [400-1000]'
        })
    )

    # Campo para indicar el % de datos de entrenamiento
    porcentaje_entrenamiento = forms.ChoiceField(
        choices=(
            ('50%', 50),
            ('66%', 66),
            ('70%', 70),
            ('80%', 80),
            ('90%', 90),
        ),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Porcentaje de datos para el entrenamiento'
        })
    )