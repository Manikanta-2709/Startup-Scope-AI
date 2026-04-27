document.addEventListener('DOMContentLoaded', () => {
    const STORAGE_KEY = 'startupscope_onboarding_idea';

    const escapeHtml = (value = '') => String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');

    const setStatus = (element, message, type = 'info') => {
        if (!element) return;
        element.textContent = message;
        element.classList.remove('hidden', 'success-visible', 'error-visible');
        if (type === 'success') {
            element.classList.add('success-visible');
        } else if (type === 'error') {
            element.classList.add('error-visible');
        }
    };

    const getOnboardingIdea = () => {
        const params = new URLSearchParams(window.location.search);
        return params.get('idea') || localStorage.getItem(STORAGE_KEY) || '';
    };

    const buildDashboardUrl = () => {
        const idea = getOnboardingIdea();
        if (!idea) return '/dashboard';
        return `/dashboard?idea=${encodeURIComponent(idea)}`;
    };

    const renderOnboardingBanner = () => {
        const idea = getOnboardingIdea();
        const banner = document.getElementById('onboarding-idea-banner');
        if (!banner || !idea) return;

        banner.textContent = `Continuing with startup idea: ${idea}`;
        banner.classList.remove('hidden');

        const hiddenIdea = document.getElementById('auth-idea');
        if (hiddenIdea) hiddenIdea.value = idea;

        const registerLink = document.getElementById('login-to-register-link');
        if (registerLink) registerLink.href = `/register-page?idea=${encodeURIComponent(idea)}`;

        const loginLink = document.getElementById('register-to-login-link');
        if (loginLink) loginLink.href = `/login-page?idea=${encodeURIComponent(idea)}`;
    };

    const setupMobileMenu = () => {
        const toggle = document.getElementById('mobile-menu-toggle');
        const navLinks = document.getElementById('site-nav-links');
        if (!toggle || !navLinks) return;

        toggle.addEventListener('click', () => {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', String(!expanded));
            document.body.classList.toggle('nav-open', !expanded);
        });

        document.querySelectorAll('#site-nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                toggle.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('nav-open');
            });
        });
    };

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await fetch('/logout', { method: 'POST' });
            window.location.href = '/login-page';
        });
    }

    setupMobileMenu();
    renderOnboardingBanner();

    const loginForm = document.getElementById('standalone-login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('auth-email').value;
            const password = document.getElementById('auth-password').value;
            const submitBtn = document.getElementById('auth-submit-btn');
            const errorMsg = document.getElementById('auth-error');

            submitBtn.disabled = true;
            submitBtn.textContent = 'Authenticating...';
            errorMsg.classList.add('hidden');

            try {
                const res = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (res.ok) {
                    window.location.href = buildDashboardUrl();
                } else {
                    setStatus(errorMsg, data.error || 'Login failed', 'error');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Login';
                }
            } catch (err) {
                setStatus(errorMsg, 'Network error.', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Login';
            }
        });
    }

    const registerForm = document.getElementById('standalone-register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('auth-name').value;
            const email = document.getElementById('auth-email').value;
            const password = document.getElementById('auth-password').value;
            const submitBtn = document.getElementById('auth-submit-btn');
            const errorMsg = document.getElementById('auth-error');

            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating...';
            errorMsg.classList.add('hidden');

            try {
                const res = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                const data = await res.json();
                if (res.ok) {
                    window.location.href = buildDashboardUrl();
                } else {
                    setStatus(errorMsg, data.error || 'Registration failed', 'error');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create Account';
                }
            } catch (err) {
                setStatus(errorMsg, 'Network error.', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        });
    }

    const forgotPasswordForm = document.getElementById('forgot-password-form');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('forgot-email').value;
            const newPassword = document.getElementById('forgot-new-password').value;
            const confirmPassword = document.getElementById('forgot-confirm-password').value;
            const status = document.getElementById('forgot-password-status');

            status.classList.add('hidden');

            if (newPassword !== confirmPassword) {
                setStatus(status, 'Passwords do not match.', 'error');
                return;
            }

            try {
                const res = await fetch('/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, new_password: newPassword })
                });
                const data = await res.json();
                if (res.ok) {
                    setStatus(status, data.message, 'success');
                    forgotPasswordForm.reset();
                    setTimeout(() => {
                        window.location.href = '/login-page';
                    }, 1200);
                } else {
                    setStatus(status, data.error || 'Could not change password.', 'error');
                }
            } catch (err) {
                setStatus(status, 'Network error.', 'error');
            }
        });
    }

    const resetPasswordForm = document.getElementById('reset-password-form');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = resetPasswordForm.dataset.token;
            const newPassword = document.getElementById('reset-password').value;
            const confirmPassword = document.getElementById('reset-password-confirm').value;
            const status = document.getElementById('reset-password-status');

            if (newPassword !== confirmPassword) {
                setStatus(status, 'Passwords do not match.', 'error');
                return;
            }

            try {
                const res = await fetch(`/reset-password/${encodeURIComponent(token)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_password: newPassword })
                });
                const data = await res.json();
                if (res.ok) {
                    setStatus(status, data.message, 'success');
                    resetPasswordForm.reset();
                    setTimeout(() => {
                        window.location.href = '/login-page';
                    }, 1200);
                } else {
                    setStatus(status, data.error || 'Could not reset password.', 'error');
                }
            } catch (err) {
                setStatus(status, 'Network error.', 'error');
            }
        });
    }

    const accountProfileForm = document.getElementById('account-profile-form');
    if (accountProfileForm) {
        accountProfileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('account-name').value;
            const email = document.getElementById('account-email').value;
            const status = document.getElementById('account-profile-status');

            try {
                const res = await fetch('/account/profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email })
                });
                const data = await res.json();
                if (res.ok) {
                    setStatus(status, data.message, 'success');
                } else {
                    setStatus(status, data.error || 'Could not update profile.', 'error');
                }
            } catch (err) {
                setStatus(status, 'Network error.', 'error');
            }
        });
    }

    const accountPasswordForm = document.getElementById('account-password-form');
    if (accountPasswordForm) {
        accountPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const status = document.getElementById('account-password-status');

            if (newPassword !== confirmPassword) {
                setStatus(status, 'Passwords do not match.', 'error');
                return;
            }

            try {
                const res = await fetch('/account/password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        current_password: currentPassword,
                        new_password: newPassword
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    setStatus(status, data.message, 'success');
                    accountPasswordForm.reset();
                } else {
                    setStatus(status, data.error || 'Could not update password.', 'error');
                }
            } catch (err) {
                setStatus(status, 'Network error.', 'error');
            }
        });
    }

    const validateBtn = document.getElementById('validate-btn');
    let currentAnalysis = null;
    let chatHistory = [];
    let scoreGaugeChart = null;
    let radarChartInstance = null;

    const scoreGauge = document.getElementById('scoreGauge');
    const radarChart = document.getElementById('radarChart');
    const exportBtn = document.getElementById('download-pdf-btn');
    const historyBtn = document.getElementById('history-btn-dashboard');
    const chatInput = document.getElementById('chat-input');

    const updateActionButtons = () => {
        if (!currentAnalysis) return;
        const bookmarkBtn = document.getElementById('bookmark-btn');
        if (bookmarkBtn) {
            const isBookmarked = Boolean(currentAnalysis.bookmarked);
            bookmarkBtn.textContent = isBookmarked ? 'Bookmarked' : 'Bookmark';
            bookmarkBtn.style.background = isBookmarked ? 'rgba(99,102,241,0.15)' : 'var(--card-hover)';
        }
    };

    const applyDashboardPrefill = () => {
        const params = new URLSearchParams(window.location.search);
        const idea = params.get('idea') || localStorage.getItem(STORAGE_KEY) || '';
        if (idea) {
            document.getElementById('idea-name').value = idea;
            localStorage.removeItem(STORAGE_KEY);
        }
    };

    applyDashboardPrefill();
    refreshHistory();
    loadStats();
    loadMyBookings();
    loadMyRegistrations();

    // Dedicated Chat Page Logic
    if (window.location.pathname === '/chat-page') {
        initChatPage();
    }

    async function initChatPage() {
        try {
            console.log("Initializing Chat Page...");
            const res = await fetch('/history');
            const data = await res.json();
            console.log("History Data:", data);
            if (res.ok) {
                if (data && data.length > 0) {
                    currentAnalysis = data[data.length - 1]; // Latest
                    document.getElementById('current-idea-context').textContent = `Consulting for: ${currentAnalysis.idea_name}`;
                } else {
                    document.getElementById('current-idea-context').textContent = "No active startup session selected.";
                }
                renderChatHistoryList(data || []);
            }
        } catch (e) {
            console.error("Failed to load chat history", e);
        }
    }

    function renderChatHistoryList(data) {
        const container = document.getElementById('chat-session-list');
        if (!container) return;
        container.innerHTML = '';
        [...data].reverse().forEach(item => {
            const div = document.createElement('div');
            div.className = `session-item ${currentAnalysis && currentAnalysis._id === item._id ? 'active' : ''}`;
            div.innerHTML = `<strong>${escapeHtml(item.idea_name)}</strong><p>${escapeHtml(item.created_at.slice(0,10))}</p>`;
            div.onclick = () => {
                currentAnalysis = item;
                document.getElementById('current-idea-context').textContent = `Consulting for: ${item.idea_name}`;
                document.getElementById('chat-messages').innerHTML = `<div class="chat-msg ai"><div class="msg-content"><p>Switched to context: **${item.idea_name}**. How can I help?</p></div></div>`;
                renderChatHistoryList(data); // Refresh active state
            };
            container.appendChild(div);
        });
    }

    if (historyBtn) historyBtn.addEventListener('click', refreshHistory);
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            if (!currentAnalysis || !currentAnalysis.idea_name) {
                alert('Analyze or open an idea first.');
                return;
            }
            const url = `/report?idea_name=${encodeURIComponent(currentAnalysis.idea_name)}&autoprint=1`;
            window.open(url, '_blank', 'noopener');
        });
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    if (validateBtn) {
        validateBtn.addEventListener('click', async () => {
        const payload = {
            idea_name: document.getElementById('idea-name').value.trim(),
            target_users: document.getElementById('target-users').value.trim(),
            description: document.getElementById('description').value.trim()
        };

        if (!payload.idea_name || !payload.description) {
            alert('Please fill in the startup name and description.');
            return;
        }

        const loader = document.getElementById('loader');
        const resultsSection = document.getElementById('results-section');
        loader.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (response.ok) {
                currentAnalysis = data;
                renderResults(data);
                renderCharts(data.analysis);
                showChat();
                updateActionButtons();
                refreshHistory();
                loadStats();
            } else {
                alert(`Analysis failed: ${data.error}`);
            }
        } catch (error) {
            alert('Connection error.');
        } finally {
            loader.classList.add('hidden');
        }
    });
    }

    function createCard(grid, title, content, isList = false) {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `<h3>${escapeHtml(title)}</h3>${isList ? `<ul>${content}</ul>` : content}`;
        grid.appendChild(card);
    }

    function renderResults(data) {
        const resultsGrid = document.querySelector('.results-grid');
        const analysis = data.analysis || {};
        resultsGrid.innerHTML = '';

        const competitorsHtml = (analysis.competitors || []).map(item => (
            `<li><strong>${escapeHtml(item.name || 'Competitor')}</strong>: ${escapeHtml(item.description || 'No description')}</li>`
        )).join('');

        const listFormatter = item => {
            if (typeof item === 'object' && item !== null) {
                // If it's an object, try to find a descriptive field or just stringify
                const content = item.description || item.problem || item.gap || item.text || JSON.stringify(item);
                return `<li>${escapeHtml(content)}</li>`;
            }
            return `<li>${escapeHtml(item)}</li>`;
        };

        createCard(resultsGrid, 'Real-World Competitors', competitorsHtml || '<li>No competitors available yet.</li>', true);
        createCard(resultsGrid, 'Strengths', (analysis.strengths || []).map(listFormatter).join('') || '<li>No strengths available yet.</li>', true);
        createCard(resultsGrid, 'Weaknesses', (analysis.weaknesses || []).map(listFormatter).join('') || '<li>No weaknesses available yet.</li>', true);
        createCard(resultsGrid, 'Market Gaps', (analysis.market_gaps || []).map(listFormatter).join('') || '<li>No market gaps available yet.</li>', true);
        createCard(resultsGrid, 'Improvements', (analysis.improvements || []).map(listFormatter).join('') || '<li>No improvements available yet.</li>', true);

        // Advanced Insights Toggle
        const advancedContainer = document.createElement('div');
        advancedContainer.style.gridColumn = '1 / -1';
        advancedContainer.style.textAlign = 'center';
        advancedContainer.style.padding = '40px 0';
        advancedContainer.innerHTML = `
            <button id="toggle-advanced-btn" class="glow-button" style="background: var(--bg-card); border: 1px solid var(--primary); color: var(--primary);">
                ✨ View Advanced AI Insights (Pivots, Roadmap, Tech Stack)
            </button>
        `;
        resultsGrid.appendChild(advancedContainer);

        const advancedGrid = document.createElement('div');
        advancedGrid.className = 'results-grid';
        advancedGrid.style.gridColumn = '1 / -1';
        advancedGrid.style.display = 'none';
        advancedGrid.style.marginTop = '20px';
        resultsGrid.appendChild(advancedGrid);

        createCard(advancedGrid, 'Strategy Pivots', (analysis.pivots || []).map(listFormatter).join('') || '<li>No pivots suggested yet.</li>', true);
        createCard(advancedGrid, '30-Day Roadmap', (analysis.roadmap || []).map(listFormatter).join('') || '<li>No roadmap generated yet.</li>', true);
        createCard(advancedGrid, 'Tech Stack', (analysis.tech_stack || []).map(listFormatter).join('') || '<li>No tech stack recommended yet.</li>', true);

        advancedContainer.querySelector('button').onclick = function() {
            const isHidden = advancedGrid.style.display === 'none';
            advancedGrid.style.display = isHidden ? 'grid' : 'none';
            this.textContent = isHidden ? '🔼 Hide Advanced Insights' : '✨ View Advanced AI Insights (Pivots, Roadmap, Tech Stack)';
            if (isHidden) advancedGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        };

        createCard(resultsGrid, 'Assessment', `
            <div class="justification-box">
                <strong>Expert Justification:</strong>
                <p>${escapeHtml(analysis.justification || 'No assessment returned.')}</p>
            </div>
        `, false);

        document.getElementById('results-section').classList.remove('hidden');
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
    }

    function renderCharts(analysis) {
        if (!window.Chart || !scoreGauge || !radarChart) return;

        if (scoreGaugeChart) scoreGaugeChart.destroy();
        if (radarChartInstance) radarChartInstance.destroy();

        const score = Number(analysis.idea_score || 0);
        const scoreColor = score >= 8 ? '#10b981' : score >= 5 ? '#f59e0b' : '#ef4444';

        scoreGaugeChart = new Chart(scoreGauge, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, Math.max(0, 10 - score)],
                    backgroundColor: [scoreColor, 'rgba(255,255,255,0.05)'],
                    borderWidth: 0,
                    borderRadius: 6
                }]
            },
            options: {
                cutout: '75%',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw(chart) {
                    const { ctx, width, height } = chart;
                    ctx.save();
                    ctx.font = 'bold 28px Inter';
                    ctx.fillStyle = scoreColor;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(`${score}/10`, width / 2, height / 2 - 8);
                    ctx.font = '12px Inter';
                    ctx.fillStyle = '#a0a0aa';
                    ctx.fillText(analysis.confidence || '', width / 2, height / 2 + 18);
                    ctx.restore();
                }
            }]
        });

        radarChartInstance = new Chart(radarChart, {
            type: 'radar',
            data: {
                labels: ['Strengths', 'Market Gaps', 'Improvements', 'Competitors', 'Weaknesses'],
                datasets: [{
                    data: [
                        Math.min((analysis.strengths || []).length * 2.5, 10),
                        Math.min((analysis.market_gaps || []).length * 3, 10),
                        Math.min((analysis.improvements || []).length * 2.5, 10),
                        Math.min((analysis.competitors || []).length * 2.5, 10),
                        Math.min((analysis.weaknesses || []).length * 2.5, 10)
                    ],
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    borderColor: '#6366f1',
                    pointBackgroundColor: '#6366f1',
                    borderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: { display: false },
                        grid: { color: 'rgba(255,255,255,0.06)' },
                        angleLines: { color: 'rgba(255,255,255,0.06)' },
                        pointLabels: { color: '#a0a0aa', font: { size: 11, family: 'Inter' } }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    function showChat() {
        const section = document.getElementById('chat-section');
        if (section) section.classList.remove('hidden');
        chatHistory = [];
        const initialMsg = "I've reviewed your analysis. Ask me anything: competitors, positioning, next steps, or pivots.";
        const html = window.marked ? marked.parse(initialMsg) : `<p>${escapeHtml(initialMsg)}</p>`;
        document.getElementById('chat-messages').innerHTML = `<div class="chat-msg ai"><div class="msg-content">${html}</div></div>`;
    }

    window.sendChatMessage = async function() {
        const input = document.getElementById('chat-input');
        const msg = input.value.trim();
        if (!msg) return;
        
        if (!currentAnalysis) {
            alert('Please select a startup session from the sidebar (or start a new analysis) before chatting.');
            return;
        }

        const messagesEl = document.getElementById('chat-messages');
        messagesEl.innerHTML += `<div class="chat-msg user"><div class="msg-content"><p>${escapeHtml(msg)}</p></div></div>`;
        input.value = '';
        messagesEl.scrollTop = messagesEl.scrollHeight;

        messagesEl.innerHTML += '<div class="chat-msg ai typing" id="typing-indicator"><div class="msg-content"><p>Thinking...</p></div></div>';
        messagesEl.scrollTop = messagesEl.scrollHeight;
        chatHistory.push({ role: 'user', content: msg });

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    idea_context: {
                        idea_name: currentAnalysis.idea_name,
                        target_users: currentAnalysis.target_users,
                        description: currentAnalysis.description,
                        idea_score: currentAnalysis.analysis.idea_score
                    },
                    history: chatHistory
                })
            });
            const data = await res.json();
            const typingEl = document.getElementById('typing-indicator');
            if (typingEl) typingEl.remove();

            const reply = data.reply || 'Sorry, I could not process that.';
            chatHistory.push({ role: 'assistant', content: reply });
            const htmlReply = window.marked ? marked.parse(reply) : `<p>${escapeHtml(reply)}</p>`;
            messagesEl.innerHTML += `<div class="chat-msg ai"><div class="msg-content">${htmlReply}</div></div>`;
            messagesEl.scrollTop = messagesEl.scrollHeight;
        } catch (e) {
            const typingEl = document.getElementById('typing-indicator');
            if (typingEl) typingEl.remove();
            messagesEl.innerHTML += '<div class="chat-msg ai"><p>Connection error. Please try again.</p></div>';
        }
    };

    window.toggleBookmark = async function() {
        if (!currentAnalysis) return;

        try {
            const res = await fetch('/bookmark', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ idea_name: currentAnalysis.idea_name })
            });
            const data = await res.json();
            if (res.ok) {
                currentAnalysis.bookmarked = data.bookmarked;
                updateActionButtons();
                loadStats();
                refreshHistory();
            }
        } catch (e) {
            console.error(e);
        }
    };

    window.updateIdea = function() {
        if (!currentAnalysis) return;
        document.getElementById('idea-name').value = currentAnalysis.idea_name || '';
        document.getElementById('target-users').value = currentAnalysis.target_users || '';
        document.getElementById('description').value = currentAnalysis.description || '';
        document.querySelector('.submission-container').scrollIntoView({ behavior: 'smooth' });
        document.getElementById('validate-btn').textContent = 'Re-Analyze Updated Idea';
    };

    async function loadStats() {
        try {
            const res = await fetch('/history');
            if (!res.ok) return;
            const data = await res.json();

            document.getElementById('stat-total').textContent = data.length;

            const scores = data.map(item => item.analysis?.idea_score).filter(score => Number.isFinite(score));
            const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : '0';
            document.getElementById('stat-avg').textContent = avg;

            const bookmarked = data.filter(item => item.bookmarked).length;
            document.getElementById('stat-bookmarks').textContent = bookmarked;

            if (scores.length) {
                const best = data.reduce((a, b) => ((a.analysis?.idea_score || 0) > (b.analysis?.idea_score || 0) ? a : b));
                document.getElementById('stat-best').textContent = (best.idea_name || '-').slice(0, 15);
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function refreshHistory() {
        const historyList = document.getElementById('history-list');
        try {
            historyList.innerHTML = '<p style="color: var(--text-dim);">Loading...</p>';
            const res = await fetch('/history');
            const data = await res.json();
            if (res.ok && data.length > 0) {
                historyList.innerHTML = '';
                [...data].reverse().forEach(item => {
                    const bookmarkLabel = item.bookmarked ? 'Bookmarked' : 'Saved';
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `
                        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                            <div>
                                <strong>${escapeHtml(item.idea_name)}</strong>
                                <div class="mini-caption">${bookmarkLabel}</div>
                            </div>
                            <span style="color:var(--primary);font-weight:600;">${escapeHtml(item.analysis?.idea_score || '?')}/10</span>
                        </div>
                        <p style="font-size:0.8rem;color:var(--text-dim);margin-top:5px;">${escapeHtml((item.description || '').slice(0, 100))}...</p>
                        <span style="font-size:0.75rem;color:var(--text-dim);">${escapeHtml((item.created_at || '').slice(0, 10))}</span>
                    `;
                    div.onclick = () => {
                        currentAnalysis = item;
                        renderResults(item);
                        renderCharts(item.analysis || {});
                        showChat();
                        updateActionButtons();
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    };
                    historyList.appendChild(div);
                });
            } else {
                historyList.innerHTML = '<p style="color: var(--text-dim); padding: 20px 0;">No past validations yet. Analyze an idea above.</p>';
            }
        } catch (e) {
            historyList.innerHTML = '<p style="color: var(--danger);">Failed to load history.</p>';
        }
    }

    async function loadMyBookings() {
        const container = document.getElementById('my-bookings-list');
        if (!container) return;

        try {
            const res = await fetch('/my-bookings');
            const data = await res.json();
            container.innerHTML = '';
            container.className = 'tracking-grid';

            if (!Array.isArray(data) || data.length === 0) {
                container.innerHTML = '<div class="empty-state">No mentor sessions booked yet.</div>';
                return;
            }

            data.forEach(item => {
                const statusClass = `status-${item.status || 'pending'}`;
                const canEdit = !['cancelled', 'rejected'].includes(item.status);
                const dateLabel = item.preferred_date ? `${escapeHtml(item.preferred_date)} ${escapeHtml(item.preferred_time || '')}` : 'Not scheduled yet';
                const formatLabel = item.session_format ? `<div><strong>Format:</strong> ${escapeHtml(item.session_format)}</div>` : '';

                container.innerHTML += `
                    <div class="tracking-card">
                        <div class="tracking-header">
                            <h4>${escapeHtml(item.mentor_name || 'Mentor')}</h4>
                            <span class="tracking-status ${statusClass}">${escapeHtml(item.status || 'pending')}</span>
                        </div>
                        <div class="tracking-info">
                            <div><strong>Topic:</strong> ${escapeHtml(item.topic || 'General consultation')}</div>
                            <div><strong>Requested:</strong> ${dateLabel}</div>
                            ${formatLabel}
                            <div><strong>Created:</strong> ${escapeHtml(new Date(item.created_at).toLocaleDateString())}</div>
                        </div>
                        ${item.message ? `<div class="tracking-message">"${escapeHtml(item.message)}"</div>` : ''}
                        ${canEdit ? `
                            <div class="tracking-actions">
                                <button type="button" class="btn-small" onclick="requestBookingChange('${escapeHtml(item.id)}')">Request Changes</button>
                                <button type="button" class="btn-small btn-danger-soft" onclick="cancelBooking('${escapeHtml(item.id)}')">Cancel</button>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
        } catch (e) {
            container.innerHTML = '<div class="empty-state">Could not load your bookings right now.</div>';
        }
    }

    async function loadMyRegistrations() {
        const container = document.getElementById('my-events-list');
        if (!container) return;

        try {
            const res = await fetch('/my-registrations');
            const data = await res.json();
            container.innerHTML = '';
            container.className = 'tracking-grid';

            if (!Array.isArray(data) || data.length === 0) {
                container.innerHTML = '<div class="empty-state">You have not registered for any events yet.</div>';
                return;
            }

            data.forEach(item => {
                const statusClass = `status-${item.status || 'confirmed'}`;
                const canCancel = item.status !== 'cancelled';
                container.innerHTML += `
                    <div class="tracking-card">
                        <div class="tracking-header">
                            <h4>${escapeHtml(item.event_title || 'Event')}</h4>
                            <span class="tracking-status ${statusClass}">${escapeHtml(item.status || 'confirmed')}</span>
                        </div>
                        <div class="tracking-info">
                            <div><strong>Registered:</strong> ${escapeHtml(new Date(item.created_at).toLocaleDateString())}</div>
                        </div>
                        ${canCancel ? `
                            <div class="tracking-actions">
                                <button type="button" class="btn-small btn-danger-soft" onclick="cancelRegistration('${escapeHtml(item.id)}')">Cancel Registration</button>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
        } catch (e) {
            container.innerHTML = '<div class="empty-state">Could not load your registrations right now.</div>';
        }
    }

    window.cancelBooking = async function(bookingId) {
        if (!confirm('Cancel this booking request?')) return;
        await fetch(`/booking/${encodeURIComponent(bookingId)}/cancel`, { method: 'POST' });
        loadMyBookings();
    };

    window.requestBookingChange = async function(bookingId) {
        const preferredDate = prompt('Enter the new preferred date (YYYY-MM-DD):');
        if (!preferredDate) return;
        const preferredTime = prompt('Enter the new preferred time (HH:MM):') || '';
        const message = prompt('Add a note for the mentor (optional):') || '';

        await fetch(`/booking/${encodeURIComponent(bookingId)}/reschedule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ preferred_date: preferredDate, preferred_time: preferredTime, message })
        });
        loadMyBookings();
    };

    window.cancelRegistration = async function(regId) {
        if (!confirm('Cancel this event registration?')) return;
        await fetch(`/registration/${encodeURIComponent(regId)}/cancel`, { method: 'POST' });
        loadMyRegistrations();
    };

    window.compareVersions = async function() {
        if (!currentAnalysis || !currentAnalysis.idea_name) return;

        const modal = document.getElementById('comparison-modal');
        const content = document.getElementById('comparison-content');
        document.getElementById('compare-modal-name').textContent = currentAnalysis.idea_name;

        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        content.innerHTML = '<p>Loading versions...</p>';

        try {
            const res = await fetch(`/compare/${encodeURIComponent(currentAnalysis.idea_name)}`);
            if (!res.ok) throw new Error('Failed to fetch versions');
            const versions = await res.json();

            if (versions.length < 2) {
                content.innerHTML = '<p style="text-align:center; color: var(--text-dim); width: 100%;">You need at least two saved versions to compare this idea.</p>';
                return;
            }

            content.innerHTML = '';
            versions.forEach((version, index) => {
                const isLatest = index === versions.length - 1;
                const score = version.analysis?.idea_score || 0;
                const date = (version.created_at || '').slice(0, 16).replace('T', ' ');
                content.innerHTML += `
                    <div style="flex: 1; background: var(--bg-dark); padding: 20px; border-radius: 8px; border: 1px solid ${isLatest ? 'var(--primary)' : 'var(--border-light)'};">
                        <h4 style="margin-top:0; color: ${isLatest ? 'var(--primary)' : 'var(--text-main)'};">Version ${index + 1} ${isLatest ? '(Latest)' : ''}</h4>
                        <p style="font-size: 0.8rem; color: var(--text-dim); margin-bottom: 15px;">${escapeHtml(date)}</p>
                        <div style="font-size: 2rem; font-weight: 700; color: ${score >= 8 ? '#10b981' : score >= 5 ? '#f59e0b' : '#ef4444'}; margin-bottom: 15px;">${escapeHtml(score)}/10</div>
                        <p style="font-size: 0.85rem; color: var(--text-dim); margin-bottom: 10px;"><strong>Desc:</strong> ${escapeHtml((version.description || '').slice(0, 60))}...</p>
                        <p style="font-size: 0.85rem; color: var(--text-dim);"><strong>Strengths:</strong> ${escapeHtml(version.analysis?.strengths?.length || 0)}</p>
                        <p style="font-size: 0.85rem; color: var(--text-dim);"><strong>Weaknesses:</strong> ${escapeHtml(version.analysis?.weaknesses?.length || 0)}</p>
                    </div>
                `;
            });
        } catch (e) {
            content.innerHTML = '<p style="color: var(--danger);">Failed to load comparison.</p>';
        }
    };

    window.closeComparisonModal = function() {
        const modal = document.getElementById('comparison-modal');
        modal.classList.add('hidden');
        modal.style.display = 'none';
    };
});
