from django import forms

class CareerForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100)
    interest = forms.CharField(label="Your Area of Interest", max_length=200)
