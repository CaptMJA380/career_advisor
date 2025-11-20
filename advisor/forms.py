from django import forms

from django.contrib.auth.models import User


class SimpleSignupForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="Username",
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(required=True, label="Password",
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(required=True, label="Confirm Password",
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned

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
