from django.shortcuts import render
from .forms import CareerForm

career_paths = {
    "ai": ["Machine Learning Engineer", "Data Scientist", "AI Researcher", "AI Product Manager"],
    "finance": ["Investment Banker", "Financial Analyst", "Risk Manager", "Wealth Advisor"],
    "design": ["UI/UX Designer", "Graphic Designer", "Product Designer", "Game Designer"],
    "healthcare": ["Doctor", "Nurse", "Medical Researcher", "Healthcare Administrator"],
    "law": ["Corporate Lawyer", "Judge", "Legal Advisor", "Criminal Lawyer"],
    "dance": ["Choreographer", "Dance Academy", "Influencer", "Background Dancer"],
}

def career_advice(request):
    careers = []
    advice_text = ""
    if request.method == "POST":
        form = CareerForm(request.POST)
        if form.is_valid():
            interest = form.cleaned_data["interest"].lower()
            careers = career_paths.get(interest, [])
            if careers:
                advice_text = f"Career options for {interest.capitalize()}:"
            else:
                advice_text = "Sorry, no suggestions available for this interest."
    else:
        form = CareerForm()
    
    context = {
        "form": form,
        "careers": careers,
        "advice_text": advice_text
    }
    return render(request, "advisor/home.html", context)
