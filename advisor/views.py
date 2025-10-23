from django.shortcuts import render
from django.http import JsonResponse

career_paths = {
    "ai": ["Machine Learning Engineer", "Data Scientist", "AI Researcher", "AI Product Manager"],
    "finance": ["Investment Banker", "Financial Analyst", "Risk Manager", "Wealth Advisor"],
    "design": ["UI/UX Designer", "Graphic Designer", "Product Designer", "Game Designer"],
    "healthcare": ["Doctor", "Nurse", "Medical Researcher", "Healthcare Administrator"],
    "law": ["Corporate Lawyer", "Judge", "Legal Advisor", "Criminal Lawyer"],
    "dance": ["Choreographer", "Dance Academy Owner", "Influencer", "Background Dancer"],
}

def home(request):
    return render(request, "advisor/home.html")

def get_careers(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        interest = request.POST.get("interest", "").lower()
        careers = career_paths.get(interest, ["Sorry, no suggestions available for this interest."])
        return JsonResponse({"careers": careers})
    return JsonResponse({"error": "Invalid request"}, status=400)
