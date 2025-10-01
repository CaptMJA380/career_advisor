from django.shortcuts import render
from .forms import CareerForm

# Predefined career paths dictionary
career_paths = {
    "ai": ["Machine Learning Engineer", "Data Scientist", "AI Researcher", "AI Product Manager"],
    "finance": ["Investment Banker", "Financial Analyst", "Risk Manager", "Wealth Advisor"],
    "design": ["UI/UX Designer", "Graphic Designer", "Product Designer", "Game Designer"],
    "healthcare": ["Doctor", "Nurse", "Medical Researcher", "Healthcare Administrator"],
    "law": ["Corporate Lawyer", "Judge", "Legal Advisor", "Criminal Lawyer"],
    "Dance":["Choreographer","Dance Academy","Influencer","Background Dancer"],
}

def home(request):
    careers = []
    if request.method == "POST":
        form = CareerForm(request.POST)
        if form.is_valid():
            interest = form.cleaned_data["interest"].lower()
            # Suggest careers based on interest
            careers = career_paths.get(interest, ["Sorry, no suggestions available for this interest."])
    else:
        form = CareerForm()

    return render(request, "home.html", {"form": form, "careers": careers})
