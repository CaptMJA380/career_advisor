from django.test import TestCase, Client
from django.urls import reverse
from .models import Conversation, Message


class ConversationModelTests(TestCase):
    def test_conversation_creation(self):
        conv = Conversation.objects.create(title="Software Engineering")
        self.assertEqual(conv.title, "Software Engineering")
        self.assertEqual(conv.state, "new")
        self.assertEqual(str(conv), "Software Engineering")

    def test_conversation_str_fallback(self):
        conv = Conversation.objects.create()
        self.assertEqual(str(conv), f"Conversation {conv.id}")


class MessageModelTests(TestCase):
    def test_message_creation(self):
        conv = Conversation.objects.create(title="Data Science")
        msg = Message.objects.create(
            conversation=conv,
            sender="user",
            text="I want to learn machine learning"
        )
        self.assertEqual(msg.sender, "user")
        self.assertEqual(msg.conversation, conv)
        self.assertIn("User: I want to learn", str(msg))


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_renders_ok(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advisor/home.html")

    def test_new_conversation_param(self):
        response = self.client.get(reverse("home") + "?new=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Conversation.objects.count(), 1)
        conv = Conversation.objects.first()
        self.assertEqual(conv.state, "await_interest")
        self.assertEqual(conv.messages.count(), 1)

    def test_clear_conversations_param(self):
        Conversation.objects.create(title="Sample 1")
        Conversation.objects.create(title="Sample 2")
        response = self.client.get(reverse("home") + "?clear=1")
        self.assertEqual(response.status_code, 200)
        # All old conversations cleared, a fresh one started
        self.assertEqual(Conversation.objects.count(), 1)
