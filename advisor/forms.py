from django import forms

class CareerForm(forms.Form):
    interest = forms.CharField(
        label="Enter Your Area of Interest",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control", 
            "placeholder": "e.g. Technology, Medicine, Arts"
        })
    )
