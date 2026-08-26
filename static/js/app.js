/**
 * Senior Buddy - AI Career & Academic Assistant
 * Frontend Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Application State ---
    let studentProfile = {
        name: "Alex Johnson",
        degree: "B.Tech Computer Science",
        year: "3rd Year",
        target_role: "Software Engineering Intern",
        skills: "Python, React, Data Structures, Problem Solving",
        interests: "Backend Engineering, Open Source, Cloud Apps"
    };

    let chatHistory = [];
    let isWaitingForResponse = false;
    let isSpeechRecording = false;
    let recognition = null;

    // --- DOM Elements ---
    const sidebar = document.getElementById('sidebar');
    const openSidebarBtn = document.getElementById('openSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');

    // Profile elements
    const profileSummaryCard = document.getElementById('profileSummaryCard');
    const editProfileBtn = document.getElementById('editProfileBtn');
    const headerProfileBtn = document.getElementById('headerProfileBtn');
    const profileModal = document.getElementById('profileModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const profileForm = document.getElementById('profileForm');

    // Views inside profile card
    const avatarInitial = document.getElementById('avatarInitial');
    const viewName = document.getElementById('viewName');
    const viewDegree = document.getElementById('viewDegree');
    const viewYear = document.getElementById('viewYear');
    const viewRole = document.getElementById('viewRole');
    const viewSkills = document.getElementById('viewSkills');

    // Profile form inputs
    const inputName = document.getElementById('inputName');
    const inputDegree = document.getElementById('inputDegree');
    const inputYear = document.getElementById('inputYear');
    const inputTargetRole = document.getElementById('inputTargetRole');
    const inputSkills = document.getElementById('inputSkills');
    const inputInterests = document.getElementById('inputInterests');

    // Chat elements
    const chatContainer = document.getElementById('chatContainer');
    const welcomeCard = document.getElementById('welcomeCard');
    const messagesList = document.getElementById('messagesList');
    const typingIndicator = document.getElementById('typingIndicator');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const micBtn = document.getElementById('micBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    // Configure Marked.js options
    if (window.marked) {
        marked.setOptions({
            gfm: true,
            breaks: true,
            headerIds: false
        });
    }

    // --- Initialize Application ---
    init();

    function init() {
        loadProfileFromStorage();
        renderProfileView();
        checkBackendHealth();
        loadChatHistoryFromStorage();
        setupEventListeners();
        setupSpeechRecognition();
    }

    // --- Profile Management ---
    function loadProfileFromStorage() {
        const saved = localStorage.getItem('senior_buddy_profile');
        if (saved) {
            try {
                studentProfile = { ...studentProfile, ...JSON.parse(saved) };
            } catch (e) {
                console.error("Error parsing saved profile", e);
            }
        }
    }

    function saveProfileToStorage() {
        localStorage.setItem('senior_buddy_profile', JSON.stringify(studentProfile));
    }

    function renderProfileView() {
        const initial = studentProfile.name ? studentProfile.name.charAt(0).toUpperCase() : 'S';
        avatarInitial.textContent = initial;
        viewName.textContent = studentProfile.name || "Student";
        viewDegree.textContent = studentProfile.degree || "College Student";
        viewYear.innerHTML = `<i class="fa-solid fa-calendar"></i> ${studentProfile.year || "Student"}`;
        viewRole.innerHTML = `<i class="fa-solid fa-bullseye"></i> ${studentProfile.target_role || "Career Seeker"}`;
        viewSkills.textContent = studentProfile.skills || "Not specified yet";

        // Pre-fill form fields
        inputName.value = studentProfile.name || "";
        inputDegree.value = studentProfile.degree || "";
        inputYear.value = studentProfile.year || "3rd Year";
        inputTargetRole.value = studentProfile.target_role || "";
        inputSkills.value = studentProfile.skills || "";
        inputInterests.value = studentProfile.interests || "";
    }

    function openProfileModal() {
        renderProfileView();
        profileModal.classList.remove('hidden');
    }

    function closeProfileModal() {
        profileModal.classList.add('hidden');
    }

    profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        studentProfile = {
            name: inputName.value.trim(),
            degree: inputDegree.value.trim(),
            year: inputYear.value,
            target_role: inputTargetRole.value.trim(),
            skills: inputSkills.value.trim(),
            interests: inputInterests.value.trim()
        };
        saveProfileToStorage();
        renderProfileView();
        closeProfileModal();
        showToast("Profile updated successfully! Senior Buddy will now customize guidance.", "success");
    });

    // --- Health Check ---
    async function checkBackendHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            if (data.has_api_key) {
                statusDot.className = "status-dot dot-green";
                statusText.textContent = "Live Gemini AI Active";
            } else {
                statusDot.className = "status-dot dot-green";
                statusText.textContent = "Senior Buddy Active (Demo Mode)";
            }
        } catch (err) {
            statusDot.className = "status-dot dot-red";
            statusText.textContent = "Backend Offline";
            console.error("Health check error:", err);
        }
    }


    // --- Event Listeners ---
    function setupEventListeners() {
        // Mobile Sidebar toggles
        openSidebarBtn?.addEventListener('click', () => sidebar.classList.add('active'));
        closeSidebarBtn?.addEventListener('click', () => sidebar.classList.remove('active'));

        // Profile Modal triggers
        editProfileBtn?.addEventListener('click', openProfileModal);
        headerProfileBtn?.addEventListener('click', openProfileModal);
        closeModalBtn?.addEventListener('click', closeProfileModal);
        cancelModalBtn?.addEventListener('click', closeProfileModal);

        // Click outside modal to close
        profileModal.addEventListener('click', (e) => {
            if (e.target === profileModal) closeProfileModal();
        });

        // Form Submission
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleUserSend();
        });

        // Textarea Auto-resize and Enter Key
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleUserSend();
            }
        });

        userInput.addEventListener('input', () => {
            userInput.style.height = 'auto';
            userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
        });

        // Suggested Prompts & Quick Actions
        document.addEventListener('click', (e) => {
            // Suggested Prompt Pills
            const promptChip = e.target.closest('.prompt-chip');
            if (promptChip) {
                const promptText = promptChip.getAttribute('data-prompt');
                if (promptText) {
                    userInput.value = promptText;
                    handleUserSend();
                }
            }

            // Quick Action Buttons
            const actionCard = e.target.closest('[data-action]');
            if (actionCard) {
                const actionType = actionCard.getAttribute('data-action');
                triggerQuickAction(actionType);
            }
        });

        // Clear Chat
        clearChatBtn.addEventListener('click', () => {
            if (confirm("Are you sure you want to clear this conversation session?")) {
                chatHistory = [];
                localStorage.removeItem('senior_buddy_history');
                messagesList.innerHTML = '';
                welcomeCard.classList.remove('hidden');
                showToast("Conversation cleared.", "success");
            }
        });
    }

    // --- Speech Recognition Setup ---
    function setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            micBtn.style.display = 'none';
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isSpeechRecording = true;
            micBtn.classList.add('recording');
            showToast("Listening... speak your question now.", "success");
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            userInput.style.height = 'auto';
            userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            showToast("Speech recognition error: " + event.error, "error");
        };

        recognition.onend = () => {
            isSpeechRecording = false;
            micBtn.classList.remove('recording');
        };

        micBtn.addEventListener('click', () => {
            if (!recognition) return;
            if (isSpeechRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    }

    // --- Chat Logic ---
    async function handleUserSend() {
        const text = userInput.value.trim();
        if (!text || isWaitingForResponse) return;

        userInput.value = '';
        userInput.style.height = 'auto';

        welcomeCard.classList.add('hidden');
        appendMessage('user', text);

        await sendChatRequest({ message: text });
    }

    async function triggerQuickAction(actionType) {
        if (isWaitingForResponse) return;

        welcomeCard.classList.add('hidden');
        const actionTitles = {
            "career_guidance": "🎯 Requesting personalized Career Guidance...",
            "resume_help": "📄 Requesting Resume & Portfolio Help...",
            "interview_prep": "💼 Requesting Technical & Behavioral Interview Prep...",
            "internship_advice": "🚀 Requesting Internship & Cold Emailing Advice..."
        };

        const displayLabel = actionTitles[actionType] || "Requesting Mentorship...";
        appendMessage('user', displayLabel);

        await sendChatRequest({ action_type: actionType });
    }

    async function sendChatRequest(payload) {
        isWaitingForResponse = true;
        showTypingIndicator(true);

        const fullPayload = {
            ...payload,
            profile: studentProfile,
            history: chatHistory.slice(-8) // Send recent context
        };

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fullPayload)
            });

            const data = await response.json();

            if (!data.success) {
                if (data.is_config_error) {
                    showToast("API Key Error: Check your .env file for GEMINI_API_KEY", "error");
                }
                appendMessage('ai', `⚠️ **Senior Buddy Error:** ${data.error || "Unable to fetch advice."}`);
                return;
            }

            const aiText = data.response;

            // Save into session context history
            chatHistory.push({ role: 'user', content: payload.message || payload.action_type });
            chatHistory.push({ role: 'model', content: aiText });
            saveChatHistoryToStorage();

            appendMessage('ai', aiText);

        } catch (error) {
            console.error("Chat API fetch error:", error);
            appendMessage('ai', "⚠️ **Network Error:** Could not reach the Senior Buddy server. Make sure Flask app is running.");
            showToast("Network error communicating with server", "error");
        } finally {
            isWaitingForResponse = false;
            showTypingIndicator(false);
        }
    }

    // --- Message Rendering ---
    function appendMessage(sender, text) {
        const msgRow = document.createElement('div');
        msgRow.className = `message-row message-${sender}`;

        const isUser = sender === 'user';
        const initial = studentProfile.name ? studentProfile.name.charAt(0).toUpperCase() : 'S';

        const avatarHtml = isUser
            ? `<div class="avatar user-avatar">${initial}</div>`
            : `<div class="avatar ai-avatar"><i class="fa-solid fa-graduation-cap"></i></div>`;

        let formattedContent = text;
        if (!isUser && window.marked) {
            formattedContent = marked.parse(text);
        } else {
            formattedContent = text.replace(/\n/g, '<br>');
        }

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const toolsHtml = !isUser ? `
            <div class="msg-tools">
                <button class="msg-btn copy-btn" title="Copy response"><i class="fa-regular fa-copy"></i> Copy</button>
                <button class="msg-btn speak-btn" title="Read aloud"><i class="fa-solid fa-volume-high"></i> Read</button>
            </div>
        ` : '';

        msgRow.innerHTML = `
            ${avatarHtml}
            <div class="message-bubble">
                <div class="message-body">${formattedContent}</div>
                <div class="message-footer">
                    <span>${timestamp}</span>
                    ${toolsHtml}
                </div>
            </div>
        `;

        messagesList.appendChild(msgRow);

        // Attach copy & speak event handlers if AI message
        if (!isUser) {
            const copyBtn = msgRow.querySelector('.copy-btn');
            const speakBtn = msgRow.querySelector('.speak-btn');

            copyBtn?.addEventListener('click', () => {
                navigator.clipboard.writeText(text);
                showToast("Copied response to clipboard!", "success");
            });

            speakBtn?.addEventListener('click', () => {
                speakText(text);
            });
        }

        scrollToBottom();
    }

    function showTypingIndicator(show) {
        if (show) {
            typingIndicator.classList.remove('hidden');
        } else {
            typingIndicator.classList.add('hidden');
        }
        scrollToBottom();
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // --- Speech Synthesis ---
    function speakText(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop ongoing
            // Clean markdown tokens for clear speech
            const cleanText = text.replace(/[#*`_~]/g, '');
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
            showToast("Reading advice aloud...", "success");
        } else {
            showToast("Text-to-speech not supported in this browser.", "error");
        }
    }

    // --- Storage Helpers ---
    function saveChatHistoryToStorage() {
        localStorage.setItem('senior_buddy_history', JSON.stringify(chatHistory));
    }

    function loadChatHistoryFromStorage() {
        const saved = localStorage.getItem('senior_buddy_history');
        if (saved) {
            try {
                chatHistory = JSON.parse(saved);
                if (chatHistory.length > 0) {
                    welcomeCard.classList.add('hidden');
                    chatHistory.forEach(item => {
                        appendMessage(item.role === 'user' ? 'user' : 'ai', item.content);
                    });
                }
            } catch (e) {
                console.error("Error loading chat history", e);
            }
        }
    }

    // --- Toast Notifications ---
    function showToast(message, type = "info") {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const iconClass = type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-check';
        toast.innerHTML = `
            <i class="fa-solid ${iconClass}"></i>
            <span>${message}</span>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
