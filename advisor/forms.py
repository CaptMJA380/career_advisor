from django import forms

INTEREST_CHOICES = [
    ('ai', 'Artificial Intelligence'),
    ('finance', 'Finance'),
    ('design', 'Design'),
    ('healthcare', 'Healthcare'),
    ('law', 'Law'),
    ('dance', 'Dance'),
    ('sports', 'Sports'),
    ('other', 'Other'),
]

class CareerForm(forms.Form):
    interest = forms.ChoiceField(
        choices=INTEREST_CHOICES,
        label="Select Your Area of Interest",
        widget=forms.Select(attrs={'class': 'form-select'})
    )