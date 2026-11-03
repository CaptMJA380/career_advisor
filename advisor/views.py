import re
import google.generativeai as genai
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.html import escape
from django.utils.safestring import mark_safe
from .models import Conversation, Message

# Configure Google Generative AI if key is present
_api_key = getattr(settings, "GOOGLE_API_KEY", None)
if _api_key:
    genai.configure(api_key=_api_key)


def _get_or_create_conversation(request):
    """Retrieve existing conversation from query params/session or initialize a new one."""
    # Switch conversation if requested
    conv_id = request.GET.get("conversation_id")
    if conv_id:
        try:
            conv = Conversation.objects.get(id=int(conv_id))
            request.session["conversation_id"] = conv.id
            return conv
        except (Conversation.DoesNotExist, ValueError):
            pass

    # Clear all history if requested
    if request.GET.get("clear"):
        Conversation.objects.all().delete()
        request.session.pop("conversation_id", None)

    # New conversation requested
    if request.GET.get("new"):
        conv = Conversation.objects.create()
        greeting = "Hello! I am your AI Career Advisor. Tell me which field or career path you are interested in exploring (e.g., Software Engineering, Data Science, Product Management, UX Design)."
        conv.state = "await_interest"
        conv.save()
        Message.objects.create(conversation=conv, sender="ai", text=f"<p>{greeting}</p>")
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


def _format_inline_markdown(text):
    """Convert inline markdown like bold and italics to safe HTML."""
    escaped = escape(text)
    # Convert **bold** to <strong>bold</strong>
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    # Convert *italic* to <em>italic</em>
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)
    # Convert `code` to <code>code</code>
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def format_ai_response(text):
    """Convert structured AI text response to styled HTML with lists and headings."""
    if not text:
        return ""

    lines = text.splitlines()
    out = []
    in_ul = False
    in_ol = False

    for line in lines:
        s = line.strip()
        if not s:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            continue

        # Section Headings (e.g. Summary:, Subtopics:, Details:, Next Steps:, Roadmap:)
        heading_match = re.match(r"^(#+\s*)?(Summary|Subtopics|Details|Roadmap|Next Steps|Recommended Resources):?$", s, re.IGNORECASE)
        if heading_match:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            heading_title = heading_match.group(2)
            out.append(f'<h4 class="ai-heading">{escape(heading_title)}</h4>')
            continue

        # Numbered list / Roadmap steps (e.g., '1. Learn python (4 weeks): ...')
        num_match = re.match(r"^(\d+)\.\s+(.*)$", s)
        if num_match:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append('<ol class="ai-roadmap">')
                in_ol = True
            item_text = _format_inline_markdown(num_match.group(2))
            out.append(f"<li>{item_text}</li>")
            continue

        # Bullet items (- or *)
        bullet_match = re.match(r"^[-*•]\s+(.*)$", s)
        if bullet_match:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append('<ul class="ai-bullets">')
                in_ul = True
            item_text = _format_inline_markdown(bullet_match.group(1))
            out.append(f"<li>{item_text}</li>")
            continue

        # Standard paragraph
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

        formatted_line = _format_inline_markdown(s)
        out.append(f"<p>{formatted_line}</p>")

    if in_ul:
        out.append("</ul>")
    if in_ol:
        out.append("</ol>")

    return mark_safe("\n".join(out))


def home(request):
    conversation = _get_or_create_conversation(request)

    if request.method == "POST":
        user_input = (request.POST.get("user_input") or "").strip()
        if not user_input:
            return redirect("home")

        # Save user message
        Message.objects.create(conversation=conversation, sender="user", text=user_input)

        # Update title if not yet set
        if not conversation.title:
            title = user_input.replace("\n", " ").strip()
            conversation.title = (title[:47] + "...") if len(title) > 50 else title
            conversation.save()

        # Check for API key
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key or api_key == "your_gemini_api_key_here":
            error_msg = (
                "<div class='error-box'><strong>⚠️ Google Gemini API Key Not Configured</strong><br>"
                "Please set your valid <code>GOOGLE_API_KEY</code> in the <code>.env</code> file at the project root and restart the server.</div>"
            )
            Message.objects.create(conversation=conversation, sender="ai", text=mark_safe(error_msg))
            return redirect("home")

        # Configure API key dynamically
        genai.configure(api_key=api_key)
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)

        # Prompt generation based on state machine
        try:
            def structured_prompt_for_interest(area):
                return (
                    f"You are an expert career advisor. The user is interested in '{area}'. "
                    "Provide a structured response with these exact labeled sections:\n"
                    "Summary:\nSubtopics:\nDetails:\nNext Steps:\n\n"
                    "Under 'Subtopics:' list 5 concise bullet subtopics (one per line starting with '- '). "
                    "At the end, ask the user which subtopic they would like a detailed roadmap for. "
                    "Keep explanations clear, encouraging, and actionable."
                )

            def structured_prompt_for_subtopic(topic, area):
                return (
                    f"You are an expert career advisor. The user previously selected '{area}' and now wants to specialize in '{topic}'.\n"
                    "Provide ONLY the following labeled sections exactly:\n"
                    "Details:\nRoadmap:\nRecommended Resources:\n\n"
                    "In 'Details:' give a clear explanation of this specialization, core skills required, and job market outlook. "
                    "In 'Roadmap:' provide a numbered step-by-step learning roadmap of at least 5 practical milestones. "
                    "Format each step as '1. Milestone Name (estimated duration): Description'. "
                    "In 'Recommended Resources:' list 3 high-quality certifications, books, or platforms."
                )

            if conversation.state in ("new", "await_interest"):
                prompt = structured_prompt_for_interest(user_input)
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
                    f"You are a helpful career advisor. Provide a structured, helpful answer for: {user_input}. "
                    "Use labeled sections: Summary:, Details:, Next Steps:."
                )
                response = model.generate_content(prompt)
                response_text = response.text

            formatted = format_ai_response(response_text)
            Message.objects.create(conversation=conversation, sender="ai", text=formatted)

        except Exception as e:
            error_html = mark_safe(f"<div class='error-box'><strong>AI Service Error:</strong> {escape(str(e))}</div>")
            Message.objects.create(conversation=conversation, sender="ai", text=error_html)

        return redirect("home")

    # Fetch conversation history (only non-empty conversations)
    conversations = (
        Conversation.objects.filter(messages__isnull=False)
        .distinct()
        .order_by("-created_at")[:20]
    )
    messages = conversation.messages.all()

    return render(
        request,
        "advisor/home.html",
        {
            "conversation": conversation,
            "messages": messages,
            "conversations": conversations,
        },
    )
