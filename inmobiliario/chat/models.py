from django.conf import settings
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.email


class Conversation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profile.name} - {self.title}"


def conversation_files_path(instance, filename):
    # TODO: Ineficiente en la DB.
    return f"files/{instance.conversation.profile.user.id}/{instance.conversation.id}/{filename}"


class Question(models.Model):
    # conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.created_at}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        null=True,
        blank=True,
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confidence = models.FloatField(null=True, blank=True, default=0.8)

    def __str__(self):
        return f"Answer saved on: {self.created_at}"


class Advice(models.Model):
    text = models.TextField()
    advice = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Advice given on: {self.created_at}"


class ConversationFile(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=conversation_files_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.conversation.title} - {self.file.name}"
