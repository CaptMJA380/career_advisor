from django import forms

class CareerForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your name'
    }))
    interest = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'e.g., AI, Finance, Design, Healthcare, Law, Dance'
    }))