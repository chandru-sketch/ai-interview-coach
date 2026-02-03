from django.contrib import admin
from django.urls import path
from core import views as core_views

urlpatterns = [
    # Home
    path('', core_views.home, name='home'),

    # Authentication
    path('register/', core_views.register, name='register'),
    path('login/', core_views.login, name='login'),
    path('logout/',  core_views.logout, name='logout'),

    # Profile
    path('profile/', core_views.profile, name='profile'),


    # AI Chat / Interview
    path('chat/', core_views.chat, name='chat'),
    path('chat/start/', core_views.start_chat, name='start_chat'),
    path('chat/message/', core_views.send_message, name='send_message'),

    # API endpoints
    path('api/chat/', core_views.api_chat, name='api_chat'),
    path('api/upload_resume/', core_views.api_upload_resume, name='api_upload_resume'),
    path('api/generate-questions/', core_views.generate_resume_questions, name='generate_questions'),
    path('api/feedback/', core_views.api_feedback, name='api_feedback'),
    path('api/session/', core_views.api_session, name='api_session'),
    path('api/answer/', core_views.api_answer, name='api_answer'),

    # Ajax / Forgot Password
    path('ajax/forgot-password/generate/', core_views.forgot_password_generate_code, name='forgot_password_generate_code'),
    path('ajax/forgot-password/verify/', core_views.forgot_password_verify_code, name='forgot_password_verify_code'),
    path('ajax/forgot-password/reset/', core_views.forgot_password_reset, name='forgot_password_reset'),

    path('daily_mission/', core_views.daily_mission, name='daily_mission'),
    path('scoreboard/', core_views.scoreboard, name='scoreboard'),
    path('faq/', core_views.faq, name='faq'),
    path('feedback/', core_views.feedback_view, name='feedback'),
]

