from django.contrib import admin

from .models import Advice, Answer, Conversation, ConversationFile, Profile, Question

# Register your models here.
admin.site.register(Profile)
admin.site.register(Conversation)
admin.site.register(ConversationFile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Advice)
