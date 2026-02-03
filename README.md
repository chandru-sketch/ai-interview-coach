# 🤖 AI Interview Coach

AI Interview Coach is a Django-based web application designed to help users prepare for technical and HR interviews. The system generates interview questions, evaluates responses, and provides intelligent feedback using NLP techniques and a local Large Language Model (LLM).

---

## 🚀 Features
- AI-based interview question generation
- Technical and HR interview practice
- Intelligent feedback and suggestions
- Local LLM integration (LLaMA 3.2 – 3B)
- Simple and clean user interface
- Admin panel for management

---

## 🛠️ Technologies Used
- Frontend: HTML, CSS, JavaScript
- Backend: Django (Python)
- Database: SQLite
- AI / NLP: TextBlob, NLTK
- LLM: LLaMA 3.2 (3B) via Ollama

---

## 📂 Project Structure
ai_interview_coach/
├── manage.py
├── requirements.txt
├── README.md
├── ai_interview_coach/
├── templates/
├── static/
├── media/
└── db.sqlite3

---

## ⚙️ Installation & Setup

1. Clone the Repository  
git clone https://github.com/your-username/ai-interview-coach.git  
cd ai-interview-coach  

2. (Optional) Create Virtual Environment  
python -m venv venv  
venv\Scripts\activate  

3. Install Python Dependencies  
pip install -r requirements.txt  

4. Download NLP Corpora (Optional)  
python -m textblob.download_corpora  

5. Install & Run LLaMA 3.2 (3B) Model  

Install Ollama:  
https://ollama.com  

Pull the model:  
ollama pull llama3.2:3b  

Run the model:  
ollama run llama3.2:3b  

Keep Ollama running in the background before starting the Django server.

6. Apply Migrations  
python manage.py migrate  

7. Run the Development Server  
python manage.py runserver  

Open in browser:  
http://127.0.0.1:8000/

---

## 👤 Admin Panel

Create admin user:  
python manage.py createsuperuser  

Admin URL:  
http://127.0.0.1:8000/admin/

---

## 📌 Notes
- LLaMA model runs locally (no paid API required)
- Internet needed only for first-time model download
- Minimum 8GB RAM recommended for LLM usage

---

## 🎓 Academic Purpose
This project is developed for educational purposes to demonstrate Django, NLP, and local LLM integration.

---

## 👨‍💻 Author
Chandru
