from django.shortcuts import render
from .forms import CareerForm
import random

career_paths = {
    "ai": ["Machine Learning Engineer", "Data Scientist", "AI Researcher", "AI Product Manager"],
    "finance": ["Investment Banker", "Financial Analyst", "Risk Manager", "Wealth Advisor"],
    "design": ["UI/UX Designer", "Graphic Designer", "Product Designer", "Game Designer"],
    "healthcare": ["Doctor", "Nurse", "Medical Researcher", "Healthcare Administrator"],
    "law": ["Corporate Lawyer", "Judge", "Legal Advisor", "Criminal Lawyer"],
    "dance": ["Choreographer", "Dance Academy Instructor", "Influencer", "Background Dancer"],
    "sports": ["Sports Analyst", "Athletic Trainer", "Coach", "Sports Journalist"],
}

def ai_generate_careers(interest):
    # Simulated AI-like logic using keyword analysis
    interest = interest.lower()

    # Check if interest directly matches known categories
    if interest in career_paths:
        return career_paths[interest]

    # Partial matches
    for key in career_paths:
        if key in interest:
            return career_paths[key]

    # If nothing matches, generate creative suggestions
    creative_fields = [
        f"{interest.title()} Consultant",
        f"{interest.title()} Content Creator",
        f"{interest.title()} Researcher",
        f"{interest.title()} Product Specialist",
        f"{interest.title()} Analyst"
    ]
    random.shuffle(creative_fields)
    return creative_fields[:3]


def home(request):
    careers = []
    interest = ""
    if request.method == "POST":
        form = CareerForm(request.POST)
        if form.is_valid():
            interest = form.cleaned_data["interest"]
            careers = ai_generate_careers(interest)
    else:
        form = CareerForm()
    return render(request, "advisor/home.html", {"form": form, "careers": careers, "interest": interest})