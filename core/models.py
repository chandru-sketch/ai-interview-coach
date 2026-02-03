# core/models.py
from django.db import models
from django.contrib.auth.models import User


# --------------------------
# Chat Models
# --------------------------
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatSession {self.id} for {self.user.username}"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=10)  # 'user' | 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.content[:40]}..."


# --------------------------
# User Models
# --------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    skills = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)

    def __str__(self):
        return f"Resume of {self.user.username} ({self.uploaded_at.strftime('%Y-%m-%d')})"


# --------------------------
# Interview Models
# --------------------------
class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    field = models.CharField(max_length=100)
    questions = models.JSONField(default=list)  # List of questions
    answers = models.JSONField(default=list)    # List of answers
    feedback = models.JSONField(default=list)   # List of feedback strings

    def __str__(self):
        return f"Session {self.id} for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"


class InterviewAnswer(models.Model):
    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="interview_answers"
    )
    question_text = models.TextField()
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to '{self.question_text[:30]}...' in session {self.session.id}"


# --------------------------
# Performance & Dashboard
# --------------------------
class InterviewScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - Score: {self.score}"


class UserPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"Performance of {self.user.username}: {self.score}"


class DashboardSettings(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.value}"
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta

class QuizQuestion(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

    def __str__(self):
        return self.question

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta

class UserDailyMission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Daily quiz info
    score = models.IntegerField(default=0)        # Last daily score
    total_points = models.IntegerField(default=0) # Lifetime points
    streak = models.IntegerField(default=0)       # Consecutive days
    
    last_attempt = models.DateTimeField(null=True, blank=True)
    
    # Track attempted questions for the day
    attempted_questions = models.ManyToManyField(
        'QuizQuestion', blank=True, related_name='attempted_by_users'
    )
    
    def can_attempt(self):
        """
        Returns True if user can attempt the daily mission (24h since last attempt)
        """
        if not self.last_attempt:
            return True
        return (now() - self.last_attempt) >= timedelta(hours=24)
    
    def reset_attempts(self):
        """
        Clears attempted questions (call this after 24h)
        """
        self.attempted_questions.clear()
    
    def __str__(self):
        return f"{self.user.username} - Streak: {self.streak} - Points: {self.total_points}"

from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"


