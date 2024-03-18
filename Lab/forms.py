from django import forms

# Aquí nose hereda de ModelForm porque no hay modelo asociado
class ArimaForm(forms.Form):

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