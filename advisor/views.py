import google.generativeai as genai
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from .forms import SimpleSignupForm
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Conversation, Message, UploadedFile
from .forms import UploadCVForm

genai.configure(api_key=getattr(settings, "GOOGLE_API_KEY", None))


def format_ai_response(text):
    """Format model plain text into simple HTML (headings, lists, paragraphs, ordered lists)."""
    from django.utils.html import escape
    from django.utils.safestring import mark_safe
    if not text:
        return ""
    lines = text.splitlines()
    out = []
    in_list = False
    list_type = None
    for line in lines:
        s = line.strip()
        if not s:
            if in_list:
                out.append('</ol>' if list_type == 'ol' else '</ul>')
                in_list = False
                list_type = None
            continue
        if s.endswith(":") and s.split()[0].rstrip(':') in ("Summary", "Subtopics", "Details", "Next", "Next Steps", "Roadmap", "ATS", "ATS Assessment", "Top Job Suggestions", "Job Readiness"):
            if in_list:
                out.append('</ol>' if list_type == 'ol' else '</ul>')
                in_list = False
                list_type = None
            out.append(f"<h4 class=\"ai-heading\">{escape(s.rstrip(':'))}</h4>")
            continue
        # numbered roadmap lines like '1. Step description...'
        if s and s[0].isdigit() and s.split('.', 1)[0].isdigit() and s.split('.', 1)[1].strip().startswith(' '):
            if not in_list:
                out.append('<ol class="ai-roadmap">')
                in_list = True
                list_type = 'ol'
            content = s.split('.', 1)[1].strip()
            out.append(f"<li>{escape(content)}</li>")
            continue
        if s.startswith("- ") or s.startswith("* "):
            if not in_list:
                out.append('<ul class="ai-bullets">')
                in_list = True
                list_type = 'ul'
            out.append(f"<li>{escape(s[2:])}</li>")
            continue
        out.append(f"<p>{escape(s)}</p>")
    if in_list:
        out.append('</ol>' if list_type == 'ol' else '</ul>')
    return mark_safe('\n'.join(out))


def extract_text_from_file(path):
    """Extract text from txt, pdf, and docx files. Returns None on failure."""
    import os
    name = os.path.basename(path).lower()
    if name.endswith('.txt'):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                return fh.read()
        except Exception:
            return None
    if name.endswith('.pdf'):
        try:
            import PyPDF2
        except Exception:
            return None
        try:
            text_parts = []
            with open(path, 'rb') as fh:
                reader = PyPDF2.PdfReader(fh)
                for page in reader.pages:
                    try:
                        text_parts.append(page.extract_text() or '')
                    except Exception:
                        pass
            return '\n'.join(text_parts)
        except Exception:
            return None
    if name.endswith('.docx') or name.endswith('.doc'):
        try:
            import docx
        except Exception:
            return None
        try:
            doc = docx.Document(path)
            paragraphs = [p.text for p in doc.paragraphs]
            return '\n'.join(paragraphs)
        except Exception:
            return None
    return None


def _get_or_create_conversation(request):
    # Switch conversation if requested
    conv_id = request.GET.get("conversation_id")
    if conv_id:
        try:
            conv = Conversation.objects.get(id=int(conv_id))
            request.session["conversation_id"] = conv.id
            return conv
        except Conversation.DoesNotExist:
            pass

    # Clear all history if requested
    if request.GET.get("clear"):
        Conversation.objects.all().delete()

    # New conversation requested
    if request.GET.get("new"):
        conv = Conversation.objects.create()
        # Immediately add greeting AI message and set state
        greeting = "Hello — please enter which career you are interested in (brief)."
        conv.state = "await_interest"
        conv.save()
        Message.objects.create(conversation=conv, sender="ai", text=greeting)
        request.session["conversation_id"] = conv.id
        return conv

    # Use session-stored conversation or create one
    conv_id = request.session.get("conversation_id")
    if conv_id:
        try:
            return Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            pass

    conv = Conversation.objects.create()
    request.session["conversation_id"] = conv.id
    return conv


@login_required
def home(request):
    response_text = ""
    conversation = _get_or_create_conversation(request)

    if request.method == "POST":
        user_input = (request.POST.get("user_input") or "").strip()
        # Save user message
        Message.objects.create(conversation=conversation, sender="user", text=user_input)

        # If conversation has no title yet, use the first user input as the title
        if not conversation.title:
            title = user_input
            if title:
                conversation.title = title[:200]
                conversation.save()

        model = genai.GenerativeModel("gemini-2.5-flash")

        # Flow control based on conversation state
        response_text = ""
        try:
            # Helper to force structured output from the model
            def structured_prompt_for_interest(area):
                return (
                    f"You are a helpful career advisor. The user is interested in '{area}'. "
                    "Provide the response using these labeled sections exactly:\n"
                    "Summary:\nSubtopics:\nDetails:\nNext Steps:\n\n"
                    "Under 'Subtopics:' list 5 concise bullet subtopics (one per line starting with '- '). "
                    "At the end, ask the user which subtopic they'd like more details on. Reply in clear sentences."
                )

            def structured_prompt_for_subtopic(topic, area):
                # When user selects a subtopic, return only focused information about that subtopic
                # and a practical numbered roadmap with estimated durations per step.
                return (
                    f"You are a detailed career advisor. The user previously asked about '{area}' and now selected the subtopic '{topic}'.\n"
                    "Provide ONLY the following labeled sections exactly (use these labels and formatting):\n"
                    "Details:\nRoadmap:\n\n"
                    "In 'Details:' give a clear explanation of the subtopic: what it is and relevant career paths. "
                    "In 'Roadmap:' provide a numbered list of at least 5 practical steps the user can follow to pursue careers in this subtopic. "
                    "Format each roadmap step as a numbered line starting with '1. ' (e.g. '1. Learn the basics (2-4 weeks): ...'). "
                    "Include an estimated duration for each step in parentheses (e.g. '2-4 weeks', '3-6 months'). "
                    "Where appropriate include one recommended resource or action per step. Reply in clear sentences and do not repeat previous subtopics or other sections."
                )

            if conversation.state in ("new", "await_interest"):
                # Use a prompt that asks the user to "provide more details" after listing subtopics
                prompt = (
                    structured_prompt_for_interest(user_input)
                    + "\nPlease provide more details about which subtopic you'd like me to expand on."
                )
                response = model.generate_content(prompt)
                response_text = response.text
                conversation.state = "asked_subtopics"
                conversation.save()
            elif conversation.state == "asked_subtopics":
                prompt = structured_prompt_for_subtopic(user_input, conversation.title)
                response = model.generate_content(prompt)
                response_text = response.text
                conversation.state = "detailed"
                conversation.save()
            else:
                prompt = (
                    f"You are a concise career advisor. Provide a short structured response for: {user_input}. "
                    "Use the labeled sections: Summary:, Subtopics:, Details:, Next Steps:."
                )
                response = model.generate_content(prompt)
                response_text = response.text
        except Exception as e:
            response_text = f"Error: {e}"

        # Format AI response into simple HTML (basic markdown-like conversion)
        def format_ai_response(text):
            if not text:
                return ""
            lines = text.splitlines()
            out = []
            in_list = False
            for line in lines:
                s = line.strip()
                if not s:
                    if in_list:
                        out.append("</ul>")
                        in_list = False
                    continue
                # Heading labels (include Roadmap)
                if s.endswith(":") and s.split()[0].rstrip(':') in ("Summary", "Subtopics", "Details", "Next", "Next Steps", "Roadmap"):
                    if in_list:
                        out.append("</ul>")
                        in_list = False
                    out.append(f"<h4 class=\"ai-heading\">{escape(s.rstrip(':'))}</h4>")
                    continue
                # numbered roadmap lines like '1. Step description...'
                if s and s[0].isdigit() and s.split('.', 1)[0].isdigit() and s.split('.', 1)[1].strip().startswith(' '):
                    # start ordered list
                    if not in_list:
                        out.append('<ol class="ai-roadmap">')
                        in_list = True
                    # take text after the first dot
                    content = s.split('.', 1)[1].strip()
                    out.append(f"<li>{escape(content)}</li>")
                    continue
                # bullets
                if s.startswith("- ") or s.startswith("* "):
                    if not in_list:
                        out.append("<ul class=\"ai-bullets\">")
                        in_list = True
                    out.append(f"<li>{escape(s[2:])}</li>")
                    continue
                # default paragraph
                out.append(f"<p>{escape(s)}</p>")
            if in_list:
                # close either <ul> or <ol>
                # detect which was opened by checking last appended tag
                last = out[-1] if out else ''
                if last.startswith('<li>') or '<ol' in '\n'.join(out):
                    out.append('</ol>' if '<ol' in '\n'.join(out) else '</ul>')
            return mark_safe('\n'.join(out))

        formatted = format_ai_response(response_text)

        # Save AI response (store HTML-safe formatted string so template can render using |safe)
        Message.objects.create(conversation=conversation, sender="ai", text=formatted)

        # After POST, redirect to GET to avoid form re-submission
        return redirect("home")

    # show only conversations that have at least one message (actual history)
    conversations = Conversation.objects.filter(messages__isnull=False).distinct().order_by("-created_at")[:20]
    messages = conversation.messages.all()

    return render(request, "advisor/home.html", {"conversation": conversation, "messages": messages, "conversations": conversations})


@login_required
def upload_cv(request):
    """Simple CV upload + AI analysis endpoint."""
    result_html = None
    form = UploadCVForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        f = form.cleaned_data['file']
        # save uploaded file record
        uploaded = UploadedFile.objects.create(file=f, uploaded_by=request.user)
        path = uploaded.file.path

        # extract text from file
        text = extract_text_from_file(path)
        if not text:
            result_html = '<p>Could not extract text from this file format.</p>'
            return render(request, 'advisor/upload.html', {'form': form, 'result_html': result_html})

        # build structured prompt
        intro = text if len(text) <= 12000 else text[:12000]
        prompt = (
            "You are a helpful and practical career advisor. Analyze the candidate's CV below and provide ONLY the "
            "following labeled sections exactly (use these labels and formatting):\n\n"
            "ATS Assessment:\n"
            "Top Job Suggestions:\n"
            "Job Readiness:\n"
            "Roadmap:\n\n"
            "Instructions:\n"
            "- Under 'ATS Assessment:' state whether the CV is ATS-friendly (answer 'Yes' or 'No') and if 'No' give specific, actionable changes the candidate should make to make it ATS-friendly (file type, section titles, keywords, formatting, fonts, removing headers/footers, etc.).\n"
            "- Under 'Top Job Suggestions:' list up to 3 job roles or domains the candidate is best suited for; for each, give a one-line justification tied to the CV evidence. Use bullet lines starting with '- '.\n"
            "- Under 'Job Readiness:' state whether the candidate appears job-ready for the suggested roles (answer 'Yes' or 'No'). If 'No', briefly state the main gaps.\n"
            "- Under 'Roadmap:' if the candidate is not job-ready, provide a numbered roadmap of at least 5 practical steps with estimated durations (e.g., '2-4 weeks') and one recommended resource or action per step. Use numbered lines starting with '1. '.\n"
            "Keep the response concise and factual. Do NOT include anything besides the labeled sections above.\n\n"
            f"CV TEXT:\n{intro}"
        )

        model = genai.GenerativeModel("gemini-2.5-flash")
        try:
            resp = model.generate_content(prompt)
            ai_text = resp.text
        except Exception as e:
            ai_text = f"Error: {e}"

        # reuse existing formatter to turn model text into safe HTML
        result_html = format_ai_response(ai_text)

    return render(request, 'advisor/upload.html', {'form': form, 'result_html': result_html})


def signup(request):
    if request.method == 'POST':
        form = SimpleSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username, password=password)
            auth_login(request, user)
            return redirect('home')
    else:
        form = SimpleSignupForm()
    return render(request, 'registration/signup.html', {'form': form})
