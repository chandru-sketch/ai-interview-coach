from django.contrib import admin
from core.models import (UserProfile,Resume,QuizQuestion,Feedback,)

# Existing registrations
admin.site.register(UserProfile)
admin.site.register(Resume)
@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer')
    search_fields = ('question',)
    admin.site.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at')
    list_filter = ('created_at', 'user')