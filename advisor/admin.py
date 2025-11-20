from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "created_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("id", "conversation", "sender", "timestamp")
	list_filter = ("sender",)

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
	list_display = ("id", "file", "uploaded_by", "uploaded_at")
	readonly_fields = ("uploaded_at",)
