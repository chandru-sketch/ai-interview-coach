document.addEventListener('DOMContentLoaded', function() {
    // =========================================================
    // 1. DOM ELEMENTS & GLOBAL VARIABLES
    // =========================================================
    const chatLog = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const startMockBtn = document.getElementById('start-mock-btn');
    const fieldSelect = document.getElementById('field');
    const resumeUpload = document.getElementById('resume');
    const difficultySelect = document.getElementById('difficulty');

    let field = fieldSelect.value;
    let selectedDifficulty = null;
    let resumeData = null;
    let answeredCount = 0;
    let correctCount = 0;
    let mockMode = false;
    let mockQuestions = [];
    let mockAnswers = [];
    let mockCurrent = 0;
    let mockTimer = null;
    let mockTimeLeft = 0;

    const MOCK_QUESTION_COUNT = 5;
    const MOCK_TIME_PER_Q = 60;

    // Track duplicates
    const shownCoachMessages = new Set();
    const shownSuggestions = new Set();

    // Enable chat input
    userInput.disabled = false;
    sendBtn.disabled = false;


    // =========================================================
    // 2. CHAT HISTORY (LocalStorage)
    // =========================================================
    function saveChatHistory() {
        const history = Array.from(chatLog.querySelectorAll('.chat-message')).map(msg => ({
            role: msg.classList.contains('user') ? 'user' : 'coach',
            text: msg.textContent.replace(/^You:|Coach:/, '').trim()
        }));
        localStorage.setItem('chatHistory', JSON.stringify(history));
    }

    function loadChatHistory() {
        const history = JSON.parse(localStorage.getItem('chatHistory')) || [];
        chatLog.innerHTML = '';
        history.forEach(item => addMessage(item.role, item.text));
    }
    loadChatHistory();


    // =========================================================
    // 3. CHAT MESSAGE HANDLING
    // =========================================================
    function addMessage(sender, text, suggestion = null) {
        if (sender === 'coach') {
            const lastCoachMsg = Array.from(chatLog.querySelectorAll('.chat-message.coach')).pop();
            if (lastCoachMsg && lastCoachMsg.textContent === `Coach: ${text}`) return;
        }

        const msg = document.createElement('div');
        msg.className = `chat-message ${sender}`;
        msg.innerHTML = `<b>${sender === 'user' ? 'You' : 'Coach'}:</b> ${text}`;
        chatLog.appendChild(msg);

        if (sender === 'coach' && suggestion) {
            const lastSuggestion = Array.from(chatLog.querySelectorAll('.suggestion-box')).pop();
            if (!lastSuggestion || lastSuggestion.textContent !== `Suggestion: ${suggestion}`) {
                addSuggestion(suggestion, msg);
            }
        }

        chatLog.scrollTop = chatLog.scrollHeight;
        if (sender === 'coach') speakText(text);
        saveChatHistory();
    }

    function addSuggestion(suggestion, afterElem = null) {
        const suggestionBox = document.createElement('div');
        suggestionBox.className = 'suggestion-box';
        suggestionBox.innerHTML = `<span class="suggestion-title">Suggestion:</span> ${suggestion}`;
        if (afterElem) afterElem.insertAdjacentElement('afterend', suggestionBox);
        else chatLog.appendChild(suggestionBox);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function speakText(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 1;
            window.speechSynthesis.speak(utterance);
        }
    }

    // --------------------------
    // Difficulty selection
    // --------------------------
    difficultySelect.addEventListener('change', function() {
        selectedDifficulty = this.value;
        if (!selectedDifficulty) return;
        addMessage('coach', `You have selected "${selectedDifficulty}"`);
    });

    // =========================================================
    // 4. FIELD & RESUME HANDLERS
    // =========================================================
    fieldSelect.addEventListener('change', function() {
        field = this.value;
        shownCoachMessages.clear();
        shownSuggestions.clear();
        addMessage('coach', `Field changed to ${field}.`);

        // Ask AI for a related question
        fetch('/api/chat/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: `Ask me a ${field} interview question.`,
                field: field,
                difficulty: selectedDifficulty || ''
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.reply) addMessage('coach', data.reply);
            else addMessage('coach', `Let's start with a ${field}-related question: Can you tell me about your experience?`);
        })
        .catch(() => addMessage('coach', 'Error getting a related question.'));
    });

    resumeUpload.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) return;

        shownCoachMessages.clear();
        shownSuggestions.clear();
        addMessage('coach', `Resume uploaded: ${file.name}`);

        const formData = new FormData();
        formData.append('resume', file);

        fetch('/api/upload_resume/', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                // 1. Show the analysis panel
                showResumeAnalysisPanel(data);

                // 2. After analysis, immediately ask a resume-related interview question
                return fetch('/api/chat/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: `Ask me an interview question based on this resume.`,
                        resume_context: data,   // pass parsed resume data (optional)
                        field: field,
                        difficulty: selectedDifficulty || ''
                    })
                });
            })
            .then(res => res.json())
            .then(data => {
                if (data.reply) {
                    addMessage('coach', data.reply);
                } else {
                    addMessage('coach', "Based on your resume, can you tell me more about one of your projects?");
                }
            })
            .catch(() => addMessage('coach', 'Resume upload or analysis failed.'));
    });

    function showResumeAnalysisPanel(data) {
        let oldPanel = document.getElementById('resume-analysis-panel');
        if (oldPanel) oldPanel.remove();

        const panel = document.createElement('div');
        panel.id = 'resume-analysis-panel';
        panel.className = 'resume-panel'; // better: use CSS instead of inline styles

        const title = document.createElement('h3');
        title.textContent = 'Resume Analysis Report';
        panel.appendChild(title);

        if (data.sections) {
            panel.innerHTML += `<b>Sections Found:</b> <span style="color: #28a745">${data.sections.join(', ') || 'None'}</span><br>`;
        }
        if (data.missing_sections?.length) {
            panel.innerHTML += `<b>Missing Sections:</b> <span style="color: #dc3545">${data.missing_sections.join(', ')}</span><br>`;
        }
        if (data.suggestions?.length) {
            panel.innerHTML += `<b>Suggestions:</b><ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>`;
        }
        if (typeof data.readability_score === 'number') {
            panel.innerHTML += `<b>Readability Score:</b> <span style="color: #007bff">${data.readability_score.toFixed(1)}</span> (Flesch Reading Ease)<br>`;
        }

        const chatContainer = document.getElementById('chat-container') || document.body;
        chatContainer.insertBefore(panel, chatContainer.firstChild);
    }


    // =========================================================
    // 5. SEND MESSAGE HANDLER
    // =========================================================
    function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        addMessage('user', text);
        userInput.value = '';

        // Increment answered count
        answeredCount++;
        const answeredCountElem = document.getElementById('answered-count');
        if (answeredCountElem) answeredCountElem.textContent = answeredCount;

        fetch('/api/chat/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                field: field,
                difficulty: selectedDifficulty || '',
                tag: document.getElementById('tag')?.value || ''
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.reply) addMessage('coach', data.reply, data.suggestion);
            else if (data.suggestion) addSuggestion(data.suggestion);

            // Check suggestion for positive keywords
            if (data.suggestion && /(positive|well|good|correct|excellent|great)/i.test(data.suggestion)) {
                correctCount++;
                score = correctCount;
                const correctCountElem = document.getElementById('correct-count');
                if (correctCountElem) correctCountElem.textContent = correctCount;
                const scoreElem = document.getElementById('score-count');
                if (scoreElem) scoreElem.textContent = score + ' / 10';
            }

            // Fetch AI feedback
            return fetch('/api/feedback/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer: text })
            });
        })
        .then(res => res.json())
        .then(fb => {
            if (fb.feedback) {
                addMessage('coach', '[AI Feedback] ' + fb.feedback);

                // Check feedback for positive keywords
                if (/(positive|well|good|correct|excellent|great)/i.test(fb.feedback)) {
                    correctCount++;
                    score = correctCount;

                    const correctCountElem = document.getElementById('correct-count');
                    if (correctCountElem) correctCountElem.textContent = correctCount;
                    const scoreElem = document.getElementById('score-count');
                    if (scoreElem) scoreElem.textContent = score + ' / 10';

                    // Highlight last user message as correct
                    const lastUserMsg = Array.from(chatLog.querySelectorAll('.chat-message.user')).pop();
                    if (lastUserMsg) lastUserMsg.classList.add('correct');
                }
            }
        })
        .catch(() => addMessage('coach', 'Error contacting AI coach.'));
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });

    // =========================================================
    // 6. MOCK INTERVIEW HANDLERS
    // =========================================================
    function resetChatSession() {
        fetch('/api/chat/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'RESET_SESSION' })
        })
        .then(() => clearChatHistory())
        .catch(() => {});
    }

    function startMockInterview() {
        mockMode = true;
        mockQuestions = [];
        mockAnswers = [];
        mockCurrent = 0;

        startMockBtn.disabled = true;
        sendBtn.disabled = false;
        userInput.disabled = false;

        document.getElementById("mock-timer").textContent = "";
        fetchMockQuestion("");
    }

    function fetchMockQuestion(msg) {
        fetch("/api/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg, field, difficulty: selectedDifficulty || '' })
        })
        .then(res => res.json())
        .then(data => {
            if (data.reply && data.reply !== "Interview complete!") {
                mockQuestions.push(data.reply);
                if (mockQuestions.length < MOCK_QUESTION_COUNT) {
                    fetchMockQuestion("next");
                } else {
                    showMockQuestion(0);
                }
            } else {
                showMockQuestion(0);
            }
        })
        .catch(() => addMessage("coach", "Error fetching mock question."));
    }

    function showMockQuestion(idx) {
        if (idx >= mockQuestions.length) {
            endMockInterview();
            return;
        }
        chatLog.innerHTML = "";
        addMessage("coach", mockQuestions[idx]);
        userInput.value = "";
        userInput.focus();
        startMockTimer();
    }

    function startMockTimer() {
        mockTimeLeft = MOCK_TIME_PER_Q;
        updateMockTimer();
        if (mockTimer) clearInterval(mockTimer);
        mockTimer = setInterval(() => {
            mockTimeLeft--;
            updateMockTimer();
            if (mockTimeLeft <= 0) {
                clearInterval(mockTimer);
                submitMockAnswer("(No answer - timed out)");
            }
        }, 1000);
    }

    function updateMockTimer() {
        const timerElem = document.getElementById("mock-timer");
        if (timerElem) timerElem.textContent = mockMode ? `Time left: ${mockTimeLeft}s` : "";
    }

    function submitMockAnswer(answer) {
        if (mockTimer) clearInterval(mockTimer);
        mockAnswers.push(answer);
        mockCurrent++;

        fetch("/api/feedback/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answer })
        })
        .then(res => res.json())
        .then(fb => {
            if (fb.feedback) addMessage("coach", "[AI Feedback] " + fb.feedback);
            setTimeout(() => showMockQuestion(mockCurrent), 1500);
        });
    }

    function endMockInterview() {
        mockMode = false;
        startMockBtn.disabled = false;
        sendBtn.disabled = true;
        userInput.disabled = true;

        const timerElem = document.getElementById("mock-timer");
        if (timerElem) timerElem.textContent = "Mock interview complete!";

        let summary = "<b>Mock Interview Summary:</b><br>";
        for (let i = 0; i < mockQuestions.length; i++) {
            summary += `<b>Q${i+1}:</b> ${mockQuestions[i]}<br><b>Your answer:</b> ${mockAnswers[i] || ""}<br><br>`;
        }
        addMessage("coach", summary);
    }

    if (startMockBtn) {
        startMockBtn.addEventListener('click', function() {
            resetChatSession();
            startMockInterview();
        });
    }


    // =========================================================
    // 7. INITIAL GREETING
    // =========================================================
    addMessage('coach', "👋 Hi! Welcome to AI Interview Coach. You can chat with me to practice, or click 'Start Mock Interview' when you're ready.");
    addMessage('coach', "Tell me about yourself.");
});

// =========================================================
// Also clear on page exit (redundant safety)
// =========================================================
window.addEventListener('beforeunload', function() {
    localStorage.removeItem('chatHistory');
    mockMode = false;
    mockQuestions = [];
    mockAnswers = [];
    mockCurrent = 0;
    if (mockTimer) clearInterval(mockTimer);
    mockTimeLeft = 0;
});


