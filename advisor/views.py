import google.generativeai as genai
from django.conf import settings
from django.shortcuts import render

genai.configure(api_key=settings.GOOGLE_API_KEY)

def home(request):
    response_text = ""
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        model = genai.GenerativeModel("gemini-2.5-flash")
        try:
            response = model.generate_content(
    f"You are a concise career advisor chatbot. Give a short and practical career suggestion (under 6 sentences),provide career options in bullet points and explaining each in deatil (should not exceed 4 lines) make sure to list all texr properly for: {user_input}"
)

            response_text = response.text
        except Exception as e:
            response_text = f"Error: {e}"

    return render(request, "advisor/home.html", {"response": response_text})
