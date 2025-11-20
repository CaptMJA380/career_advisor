from django.db import models


class Conversation(models.Model):
	title = models.CharField(max_length=200, blank=True)
	# track conversation progress: new -> asked_interest -> asked_subtopics -> detailed
	state = models.CharField(max_length=30, default="new")
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title or f"Conversation {self.id}"


class Message(models.Model):
	SENDER_CHOICES = (
		("user", "User"),
		("ai", "AI"),
	)

	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
	sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
	text = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["timestamp"]

	def __str__(self):
		return f"{self.get_sender_display()}: {self.text[:50]}"
