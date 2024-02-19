from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['file',]
        widgets={
            'file': forms.FileInput(attrs={'class':'form-control','multiple': False,'onchange':'validateFileInput(this)'}),
            }
