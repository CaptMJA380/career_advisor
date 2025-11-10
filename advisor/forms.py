from django import forms

class CareerForm(forms.Form):
    INTEREST_CHOICES = [
        ("", "Select from list (or type below)"),
        ("ai", "Artificial Intelligence"),
        ("finance", "Finance"),
        ("design", "Design"),
        ("healthcare", "Healthcare"),
        ("law", "Law"),
        ("dance", "Dance"),
    ]
    
    
    interest_choice = forms.ChoiceField(
        choices=INTEREST_CHOICES,
        required=False,
        label="Choose an Interest",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    
    interest_text = forms.CharField(
        required=False,
        label="Or type your own interest",
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. AI, Robotics, Photography...",
            "class": "form-control"
        })
    )
