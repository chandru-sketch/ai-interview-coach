import io
import json
import random
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textblob import TextBlob

from .models import UserProfile, Resume, InterviewSession
from ai_interview_coach.ai_llm import chat_with_model

# --------------------------
# AUTH VIEWS
# --------------------------
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('/login')

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('/login')


# --------------------------
# PASSWORD RESET
# --------------------------
@csrf_exempt
def forgot_password_generate_code(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        try:
            user = User.objects.get(email=username_or_email) if '@' in username_or_email else User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found.'})

        code = str(random.randint(1000, 9999))
        request.session['fp_code'] = code
        request.session['fp_user_id'] = user.id

        send_mail(
            'Your Password Reset Code',
            f'Your code is: {code}',
            'no-reply@aiinterviewcoach.com',
            [user.email],
            fail_silently=True
        )
        return JsonResponse({'success': True, 'code': code})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


@csrf_exempt
def forgot_password_verify_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        session_code = request.session.get('fp_code')
        return JsonResponse({'success': code == session_code, 'error': '' if code == session_code else 'Incorrect code.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


@csrf_exempt
def forgot_password_reset(request):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        user_id = request.session.get('fp_user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'Session expired.'})
        try:
            user = User.objects.get(id=user_id)
            user.password = make_password(new_password)
            user.save()
            request.session.pop('fp_code', None)
            request.session.pop('fp_user_id', None)
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


# --------------------------
# PROFILE
# --------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile, Resume, InterviewSession


@login_required
def profile(request):
    user = request.user
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    user_resume = Resume.objects.filter(user=user).order_by('-uploaded_at').first()

    # Stats for dashboard
    stats = {'answered': 0, 'correct': 0, 'mock_interviews': 0}
    sessions = InterviewSession.objects.filter(user=user)
    stats['mock_interviews'] = sessions.count()
    stats['answered'] = sum(len(s.questions) for s in sessions)
    stats['correct'] = sum(len([a for a in s.answers if a and 'good' in a.lower()]) for s in sessions)

    if request.method == "POST":
        # Update only allowed fields
        user_profile.bio = request.POST.get("bio", user_profile.bio)
        user_profile.phone = request.POST.get("phone", user_profile.phone)
        user_profile.skills = request.POST.get("skills", user_profile.skills)

        if "avatar" in request.FILES:
            user_profile.avatar = request.FILES["avatar"]

        user_profile.save()

        if "resume" in request.FILES:
            Resume.objects.create(user=user, file=request.FILES["resume"])

        return redirect("profile")

    return render(
        request,
        "profile.html",
        {
            "user": user,
            "user_profile": user_profile,
            "user_resume": user_resume,
            "stats": stats,
        },
    )


# --------------------------
# HOME
# --------------------------
@login_required(login_url='/login')
def home(request):
    return render(request, 'home.html')


# --------------------------
# AI CHAT / INTERVIEW
# --------------------------
@login_required
def chat(request):
    """Render chat page."""
    return render(request, 'chat.html')


@login_required
def start_chat(request):
    """Initialize chat session."""
    request.session['chat_history'] = []
    return JsonResponse({"session_id": 1, "question": "Session started. Ask the first question!", "score": 0})


@login_required
@csrf_exempt
def send_message(request):
    """Send message to AI."""
    if request.method == 'POST':
        data = json.loads(request.body or "{}")
        user_msg = data.get('message', '').strip()
        history = request.session.get('chat_history', [])

        try:
            assistant_msg = chat_with_model(history, user_msg)
        except Exception as e:
            return JsonResponse({"reply": "AI engine unavailable", "error": str(e)}, status=500)

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": assistant_msg})
        request.session['chat_history'] = history[-40:]
        request.session.modified = True

        return JsonResponse({"reply": assistant_msg})
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def api_chat(request):
    """Legacy API endpoint for chat (used in async JS)."""
    if request.method != 'POST':
        return JsonResponse({'reply': 'Invalid request.'}, status=400)

    data = json.loads(request.body or "{}") if 'application/json' in (request.content_type or '') else request.POST
    user_msg = data.get('message', '').strip() or "Start the interview. Ask the first question only."
    field = data.get('field', 'General')
    difficulty = data.get('difficulty', 'Any')
    tag = data.get('tag', '')

    if user_msg == "RESET_SESSION":
        request.session['chat_history'] = []
        return JsonResponse({'reply': "Session cleared. Click Send to begin again.", 'suggestion': "Select a field and start."})

    history = request.session.get('chat_history', [])
    try:
        assistant_text = chat_with_model(history, user_msg, field, difficulty, tag)
    except Exception as e:
        return JsonResponse({'reply': "Sorry, I couldn't reach the AI engine.", 'suggestion': "Check that Ollama is running and the model is pulled.", 'error': str(e)}, status=500)

    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": assistant_text})
    request.session['chat_history'] = history[-40:]
    request.session.modified = True

    return JsonResponse({'reply': assistant_text})


# --------------------------
# FEEDBACK
# --------------------------
@csrf_exempt
def api_feedback(request):
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        answer = data.get('answer', '')
        if not answer:
            return JsonResponse({'feedback': 'No answer provided.'}, status=400)

        blob = TextBlob(answer)
        sentiment = blob.sentiment.polarity
        grammar_errors = [str(c) for c in blob.correct().split() if c not in answer.split()]

        feedback = []
        if sentiment > 0.2:
            feedback.append('Your answer sounds positive.')
        elif sentiment < -0.2:
            feedback.append('Your answer sounds negative. Try to be more positive.')
        else:
            feedback.append('Your answer is neutral.')
        feedback.append('Possible grammar/spelling issues detected.' if grammar_errors else 'No major grammar issues detected.')

        return JsonResponse({'feedback': ' '.join(feedback)})
    return JsonResponse({'feedback': 'Invalid request.'}, status=400)


# --------------------------
# RESUME QUESTION GENERATOR
# --------------------------
@csrf_exempt
def generate_resume_questions(request):
    if request.method != "POST" or "resume" not in request.FILES:
        return JsonResponse({"error": "Upload a resume via POST"}, status=400)

    file = request.FILES["resume"]
    field = request.POST.get("field", "General")

    hr = [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Why should we hire you?",
    ]

    technical_map = {
        "Software": ["What is Django ORM?", "Explain REST API.", "How do you manage version control with Git?"],
        "Data Science": ["What is supervised vs unsupervised learning?", "How do you handle missing data?", "Explain overfitting and how to prevent it."],
        "Marketing": ["What is digital marketing?", "Explain SEO vs SEM.", "How do you measure campaign performance?"],
        "Finance": ["Explain NPV and IRR.", "What is ROI?", "How do you evaluate financial statements?"],
        "HR": ["How do you handle workplace conflict?", "Explain the recruitment process.", "How do you motivate employees?"],
        "Sales": ["What is the sales funnel?", "How do you handle client objections?", "Explain your biggest sales achievement."],
        "Design": ["What is the difference between UI and UX?", "Explain design thinking.", "How do you test usability?"],
        "Teaching": ["What is your teaching philosophy?", "How do you engage students?", "How do you adapt to different learning styles?"],
        "General": ["Explain problem-solving skills.", "How do you work in a team?", "What motivates you?"],
    }
    technical = technical_map.get(field, technical_map["General"])

    project = [
        f"Explain your {field} project mentioned in your resume.",
        f"What challenges did you face in your {field} project?",
        f"If given more time, how would you improve your {field} project?",
    ]

    return JsonResponse({"field": field, "questions": {"hr": hr, "technical": technical, "project": project}})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Resume

@csrf_exempt
@login_required
def api_upload_resume(request):
    if request.method != 'POST' or 'resume' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No resume uploaded.'}, status=400)

    resume_file = request.FILES['resume']
    Resume.objects.create(user=request.user, file=resume_file)

    return JsonResponse({'success': True, 'message': 'Resume uploaded successfully.'})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def api_session(request):
    """
    Returns the current user's latest interview session info.
    """
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    if not sessions.exists():
        return JsonResponse({'success': False, 'error': 'No sessions found.'})

    session = sessions.first()
    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'questions': [q.text for q in session.questions],
        'answers': [a.text if a else '' for a in getattr(session, 'answers', [])]
    })
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import InterviewSession, InterviewAnswer

@csrf_exempt
@login_required
def api_answer(request):
    """
    Receives a user's answer to a question and saves it to the latest session.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required."}, status=400)

    user = request.user
    question_id = request.POST.get("question_id")
    answer_text = request.POST.get("answer")

    if not question_id or not answer_text:
        return JsonResponse({"success": False, "error": "Missing question or answer."}, status=400)

    # Get the latest session
    session = InterviewSession.objects.filter(user=user).order_by("-created_at").first()
    if not session:
        return JsonResponse({"success": False, "error": "No active session."})

    # Save the answer
    answer = InterviewAnswer.objects.create(
        session=session,
        question_id=question_id,
        text=answer_text
    )

    return JsonResponse({"success": True, "answer_id": answer.id})

from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required
from .models import QuizQuestion, UserDailyMission

@login_required
def daily_mission(request):
    user = request.user

    # Get or create mission for user
    mission, created = UserDailyMission.objects.get_or_create(user=user)

    # Check if user can attempt the daily quiz
    if not mission.can_attempt():
        remaining_seconds = int((mission.last_attempt + timedelta(hours=24) - now()).total_seconds())
        return render(request, "daily_mission_locked.html", {"remaining_seconds": remaining_seconds})

    score = None  # Will hold the quiz score if submitted
    correct_ids = []  # Keep track of correct questions for optional highlight

    if request.method == "POST":
        score = 0
        for q_id, answer in request.POST.items():
            if q_id == "csrfmiddlewaretoken":
                continue
            try:
                q = QuizQuestion.objects.get(id=int(q_id))
                # Check answer
                if answer == q.correct_answer:
                    score += 1
                    correct_ids.append(q.id)
                # Mark question as attempted
                mission.attempted_questions.add(q)
            except QuizQuestion.DoesNotExist:
                continue

        # Update points (10 points per correct answer)
        mission.total_points += score * 10
        mission.score = score

        # Update streak
        if mission.last_attempt and (now().date() - mission.last_attempt.date()).days == 1:
            mission.streak += 1
        else:
            mission.streak = 1

        # Update last_attempt timestamp
        mission.last_attempt = now()
        mission.save()

    # Get 5 random questions excluding already attempted ones
    attempted_qs = mission.attempted_questions.all()
    questions = QuizQuestion.objects.exclude(id__in=attempted_qs).order_by("?")[:5]

    # If less than 5 questions left and user hasn't submitted yet, reset attempted questions
    if questions.count() < 5 and score is None:
        mission.attempted_questions.clear()
        questions = QuizQuestion.objects.order_by("?")[:5]

    return render(request, "daily_mission.html", {
        "questions": questions,
        "score": score,
        "mission": mission,
        "correct_ids": correct_ids  # Optional for highlighting answers
    })


@login_required
def scoreboard(request):
    # Top 10 users sorted by total points
    scores = UserDailyMission.objects.order_by("-total_points", "last_attempt")[:10]
    return render(request, "scoreboard.html", {"scores": scores})

def faq(request):
    return render(request, 'faq.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import FeedbackForm

@login_required
def feedback_view(request):
    submitted = False
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            submitted = True
    else:
        form = FeedbackForm()
    return render(request, 'feedback_form.html', {'form': form, 'submitted': submitted})
