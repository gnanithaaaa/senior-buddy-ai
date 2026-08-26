/**
 * Senior Buddy - AI Career & Academic Assistant
 * Frontend Application Controller with Authentication & Dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Application State ---
    let currentUser = null; // { id, name, email, profile, total_chats }
    let studentProfile = {
        name: "Guest Student",
        degree: "Computer Science",
        year: "3rd Year",
        target_role: "Software Engineer",
        skills: "Python, Problem Solving",
        interests: "Software Development"
    };

    let chatHistory = [];
    let isWaitingForResponse = false;
    let isSpeechRecording = false;
    let recognition = null;

    // --- DOM Elements ---
    const sidebar = document.getElementById('sidebar');
    const openSidebarBtn = document.getElementById('openSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');

    // Auth Navigation & UI Elements
    const loggedOutNav = document.getElementById('loggedOutNav');
    const loggedInNav = document.getElementById('loggedInNav');
    const navLoginBtn = document.getElementById('navLoginBtn');
    const navSignupBtn = document.getElementById('navSignupBtn');
    const navDashboardBtn = document.getElementById('navDashboardBtn');
    const navLogoutBtn = document.getElementById('navLogoutBtn');
    const navUserName = document.getElementById('navUserName');

    // Auth Modal Elements
    const authModal = document.getElementById('authModal');
    const closeAuthModalBtn = document.getElementById('closeAuthModalBtn');
    const tabLoginBtn = document.getElementById('tabLoginBtn');
    const tabSignupBtn = document.getElementById('tabSignupBtn');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginEmail = document.getElementById('loginEmail');
    const loginPassword = document.getElementById('loginPassword');
    const signupName = document.getElementById('signupName');
    const signupEmail = document.getElementById('signupEmail');
    const signupPassword = document.getElementById('signupPassword');
    const signupDegree = document.getElementById('signupDegree');
    const signupYear = document.getElementById('signupYear');
    const signupTargetRole = document.getElementById('signupTargetRole');
    const signupSkills = document.getElementById('signupSkills');

    // Dashboard Modal Elements
    const dashboardModal = document.getElementById('dashboardModal');
    const closeDashboardModalBtn = document.getElementById('closeDashboardModalBtn');
    const dashAvatar = document.getElementById('dashAvatar');
    const dashStudentName = document.getElementById('dashStudentName');
    const dashStudentMeta = document.getElementById('dashStudentMeta');
    const dashChatCount = document.getElementById('dashChatCount');
    const dashTargetRole = document.getElementById('dashTargetRole');
    const dashSkillsCount = document.getElementById('dashSkillsCount');
    const dashEditProfileBtn = document.getElementById('dashEditProfileBtn');
    const dashStartChatBtn = document.getElementById('dashStartChatBtn');

    // Profile elements
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
    const welcomeHeading = document.getElementById('welcomeHeading');
    const messagesList = document.getElementById('messagesList');
    const typingIndicator = document.getElementById('typingIndicator');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
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

    async function init() {
        setupEventListeners();
        setupSpeechRecognition();
        checkBackendHealth();
        await checkAuthSession();
    }

    // --- Authentication & Session Check ---
    async function checkAuthSession() {
        try {
            const res = await fetch('/api/auth/me');
            const data = await res.json();
            if (data.authenticated && data.user) {
                currentUser = data.user;
                if (currentUser.profile) {
                    studentProfile = {
                        name: currentUser.name,
                        degree: currentUser.profile.degree || "Computer Science",
                        year: currentUser.profile.year || "3rd Year",
                        target_role: currentUser.profile.target_role || "Software Engineer",
                        skills: currentUser.profile.skills || "",
                        interests: currentUser.profile.interests || ""
                    };
                } else {
                    studentProfile.name = currentUser.name;
                }
                updateAuthUI(true);
                await loadSavedUserHistory();
            } else {
                currentUser = null;
                updateAuthUI(false);
                loadProfileFromLocalStorage();
            }
            renderProfileView();
        } catch (e) {
            console.error("Session check error", e);
            updateAuthUI(false);
            renderProfileView();
        }
    }

    function updateAuthUI(isLoggedIn) {
        if (isLoggedIn && currentUser) {
            loggedOutNav.classList.add('hidden');
            loggedInNav.classList.remove('hidden');
            navUserName.textContent = currentUser.name.split(' ')[0];
            welcomeHeading.textContent = `Hey ${currentUser.name.split(' ')[0]}! I'm your Senior Buddy. 👋`;
        } else {
            loggedOutNav.classList.remove('hidden');
            loggedInNav.classList.add('hidden');
            welcomeHeading.textContent = "Hey there! I'm your Senior Buddy. 👋";
        }
    }

    // --- Auth Actions ---
    async function handleLogin(email, password) {
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (!data.success) {
                showToast(data.error || "Login failed.", "error");
                return;
            }
            currentUser = data.user;
            if (currentUser.profile) {
                studentProfile = {
                    name: currentUser.name,
                    degree: currentUser.profile.degree || "Computer Science",
                    year: currentUser.profile.year || "3rd Year",
                    target_role: currentUser.profile.target_role || "Software Engineer",
                    skills: currentUser.profile.skills || "",
                    interests: currentUser.profile.interests || ""
                };
            }
            updateAuthUI(true);
            renderProfileView();
            closeAuthModal();
            showToast(`Welcome back, ${currentUser.name}!`, "success");
            await loadSavedUserHistory();
        } catch (err) {
            showToast("Network error logging in.", "error");
        }
    }

    async function handleSignup(signupData) {
        try {
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signupData)
            });
            const data = await res.json();
            if (!data.success) {
                showToast(data.error || "Sign up failed.", "error");
                return;
            }
            currentUser = data.user;
            studentProfile = {
                name: currentUser.name,
                degree: signupData.degree,
                year: signupData.year,
                target_role: signupData.target_role,
                skills: signupData.skills,
                interests: signupData.interests || ""
            };
            updateAuthUI(true);
            renderProfileView();
            closeAuthModal();
            showToast(`Account created! Welcome, ${currentUser.name}!`, "success");
            openDashboardModal();
        } catch (err) {
            showToast("Network error creating account.", "error");
        }
    }

    async function handleLogout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            currentUser = null;
            updateAuthUI(false);
            chatHistory = [];
            messagesList.innerHTML = '';
            welcomeCard.classList.remove('hidden');
            loadProfileFromLocalStorage();
            renderProfileView();
            showToast("Logged out successfully.", "success");
        } catch (err) {
            showToast("Error logging out.", "error");
        }
    }

    // --- History Loading ---
    async function loadSavedUserHistory() {
        if (!currentUser) return;
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            if (data.success && data.messages && data.messages.length > 0) {
                messagesList.innerHTML = '';
                chatHistory = [];
                welcomeCard.classList.add('hidden');
                data.messages.forEach(msg => {
                    chatHistory.push({ role: msg.sender === 'user' ? 'user' : 'model', content: msg.content });
                    appendMessage(msg.sender === 'user' ? 'user' : 'ai', msg.content);
                });
            }
        } catch (e) {
            console.error("Error loading chat history from DB", e);
        }
    }

    // --- Profile Management ---
    function loadProfileFromLocalStorage() {
        const saved = localStorage.getItem('senior_buddy_profile');
        if (saved) {
            try {
                studentProfile = { ...studentProfile, ...JSON.parse(saved) };
            } catch (e) {
                console.error("Error parsing saved profile", e);
            }
        }
    }

    function renderProfileView() {
        const initial = studentProfile.name ? studentProfile.name.charAt(0).toUpperCase() : 'S';
        avatarInitial.textContent = initial;
        viewName.textContent = studentProfile.name || "Student";
        viewDegree.textContent = studentProfile.degree || "College Student";
        viewYear.innerHTML = `<i class="fa-solid fa-calendar"></i> ${studentProfile.year || "3rd Year"}`;
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

    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        studentProfile = {
            name: inputName.value.trim(),
            degree: inputDegree.value.trim(),
            year: inputYear.value,
            target_role: inputTargetRole.value.trim(),
            skills: inputSkills.value.trim(),
            interests: inputInterests.value.trim()
        };

        if (currentUser) {
            currentUser.name = studentProfile.name;
            navUserName.textContent = currentUser.name.split(' ')[0];
            try {
                await fetch('/api/profile/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(studentProfile)
                });
            } catch (e) {
                console.error("Error saving profile to DB", e);
            }
        } else {
            localStorage.setItem('senior_buddy_profile', JSON.stringify(studentProfile));
        }

        renderProfileView();
        closeProfileModal();
        showToast("Profile updated successfully! Senior Buddy customized your context.", "success");
    });

    // --- Dashboard ---
    function openDashboardModal() {
        dashAvatar.textContent = studentProfile.name ? studentProfile.name.charAt(0).toUpperCase() : 'S';
        dashStudentName.textContent = currentUser ? currentUser.name : studentProfile.name;
        dashStudentMeta.textContent = `${studentProfile.degree} | ${studentProfile.year}`;
        dashChatCount.textContent = chatHistory.length > 0 ? Math.floor(chatHistory.length / 2) : (currentUser ? (currentUser.total_chats || 0) : 0);
        dashTargetRole.textContent = studentProfile.target_role || "Software Engineer";
        dashSkillsCount.textContent = studentProfile.skills || "Not specified";

        dashboardModal.classList.remove('hidden');
    }

    function closeDashboardModal() {
        dashboardModal.classList.add('hidden');
    }

    // --- Auth Modals ---
    function openAuthModal(mode = 'login') {
        if (mode === 'signup') {
            tabSignupBtn.classList.add('active');
            tabLoginBtn.classList.remove('active');
            signupForm.classList.remove('hidden');
            loginForm.classList.add('hidden');
        } else {
            tabLoginBtn.classList.add('active');
            tabSignupBtn.classList.remove('active');
            loginForm.classList.remove('hidden');
            signupForm.classList.add('hidden');
        }
        authModal.classList.remove('hidden');
    }

    function closeAuthModal() {
        authModal.classList.add('hidden');
    }

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

        // Nav Auth Triggers
        navLoginBtn?.addEventListener('click', () => openAuthModal('login'));
        navSignupBtn?.addEventListener('click', () => openAuthModal('signup'));
        navLogoutBtn?.addEventListener('click', handleLogout);
        navDashboardBtn?.addEventListener('click', openDashboardModal);

        // Auth Tabs
        tabLoginBtn?.addEventListener('click', () => openAuthModal('login'));
        tabSignupBtn?.addEventListener('click', () => openAuthModal('signup'));
        closeAuthModalBtn?.addEventListener('click', closeAuthModal);

        // Auth Forms
        loginForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            handleLogin(loginEmail.value.trim(), loginPassword.value.trim());
        });

        signupForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            handleSignup({
                name: signupName.value.trim(),
                email: signupEmail.value.trim(),
                password: signupPassword.value.trim(),
                degree: signupDegree.value.trim(),
                year: signupYear.value,
                target_role: signupTargetRole.value.trim(),
                skills: signupSkills.value.trim()
            });
        });

        // Dashboard Actions
        closeDashboardModalBtn?.addEventListener('click', closeDashboardModal);
        dashEditProfileBtn?.addEventListener('click', () => {
            closeDashboardModal();
            openProfileModal();
        });
        dashStartChatBtn?.addEventListener('click', closeDashboardModal);

        // Profile Modal triggers
        editProfileBtn?.addEventListener('click', openProfileModal);
        headerProfileBtn?.addEventListener('click', () => {
            if (currentUser) {
                openDashboardModal();
            } else {
                openProfileModal();
            }
        });
        closeModalBtn?.addEventListener('click', closeProfileModal);
        cancelModalBtn?.addEventListener('click', closeProfileModal);

        // Click outside modal to close
        [authModal, dashboardModal, profileModal].forEach(modal => {
            modal?.addEventListener('click', (e) => {
                if (e.target === modal) modal.classList.add('hidden');
            });
        });

        // Form Submission
        chatForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            handleUserSend();
        });

        // Textarea Auto-resize and Enter Key
        userInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleUserSend();
            }
        });

        userInput?.addEventListener('input', () => {
            userInput.style.height = 'auto';
            userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
        });

        // Suggested Prompts & Quick Actions
        document.addEventListener('click', (e) => {
            const promptChip = e.target.closest('.prompt-chip');
            if (promptChip) {
                const promptText = promptChip.getAttribute('data-prompt');
                if (promptText) {
                    userInput.value = promptText;
                    handleUserSend();
                }
            }

            const actionCard = e.target.closest('[data-action]');
            if (actionCard) {
                const actionType = actionCard.getAttribute('data-action');
                triggerQuickAction(actionType);
            }
        });

        // Clear Chat
        clearChatBtn?.addEventListener('click', async () => {
            if (confirm("Are you sure you want to clear this conversation session?")) {
                chatHistory = [];
                messagesList.innerHTML = '';
                welcomeCard.classList.remove('hidden');
                if (currentUser) {
                    try {
                        await fetch('/api/history', { method: 'DELETE' });
                    } catch (e) { console.error("Error clearing DB history", e); }
                }
                showToast("Conversation cleared.", "success");
            }
        });
    }

    // --- Speech Recognition ---
    function setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            if (micBtn) micBtn.style.display = 'none';
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
            showToast("Speech recognition error: " + event.error, "error");
        };

        recognition.onend = () => {
            isSpeechRecording = false;
            micBtn.classList.remove('recording');
        };

        micBtn?.addEventListener('click', () => {
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
            history: chatHistory.slice(-8)
        };

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fullPayload)
            });

            const data = await response.json();

            if (!data.success) {
                appendMessage('ai', `⚠️ **Senior Buddy Error:** ${data.error || "Unable to fetch advice."}`);
                return;
            }

            const aiText = data.response;

            chatHistory.push({ role: 'user', content: payload.message || payload.action_type });
            chatHistory.push({ role: 'model', content: aiText });

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
            window.speechSynthesis.cancel();
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
