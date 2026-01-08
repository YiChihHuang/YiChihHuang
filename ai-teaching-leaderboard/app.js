/**
 * AI Teaching Leaderboard: 教學怪物
 * Main Application JavaScript
 */

// ============================================
// Mock Data
// ============================================

const mockModels = [
    {
        id: 1,
        name: 'DragonTeach Pro',
        icon: '🐉',
        team: 'Dragon AI Labs',
        elo: 1847,
        winRate: 78,
        battles: 1234,
        trend: 'up',
        trendValue: 32,
        specialties: ['📐 數學', '💻 CS']
    },
    {
        id: 2,
        name: 'FoxMentor AI',
        icon: '🦊',
        team: 'FoxTech Inc.',
        elo: 1792,
        winRate: 71,
        battles: 987,
        trend: 'up',
        trendValue: 18,
        specialties: ['💻 CS', '📊 商業']
    },
    {
        id: 3,
        name: 'WisdomOwl',
        icon: '🦉',
        team: 'Owl Academy',
        elo: 1756,
        winRate: 68,
        battles: 856,
        trend: 'stable',
        trendValue: 0,
        specialties: ['⚛️ 物理', '🧪 化學']
    },
    {
        id: 4,
        name: 'TigerSensei',
        icon: '🐯',
        team: 'Tiger Learning',
        elo: 1721,
        winRate: 65,
        battles: 743,
        trend: 'up',
        trendValue: 24,
        specialties: ['📖 語言', '🎨 藝術']
    },
    {
        id: 5,
        name: 'PhoenixTutor',
        icon: '🦅',
        team: 'Phoenix Education',
        elo: 1698,
        winRate: 63,
        battles: 691,
        trend: 'down',
        trendValue: -12,
        specialties: ['🧬 生物', '🧪 化學']
    },
    {
        id: 6,
        name: 'PandaProf',
        icon: '🐼',
        team: 'Panda Studios',
        elo: 1654,
        winRate: 59,
        battles: 612,
        trend: 'up',
        trendValue: 8,
        specialties: ['📐 數學', '⚛️ 物理']
    },
    {
        id: 7,
        name: 'RabbitRun',
        icon: '🐰',
        team: 'Quick Learn Co.',
        elo: 1632,
        winRate: 57,
        battles: 589,
        trend: 'stable',
        trendValue: 0,
        specialties: ['💻 CS']
    },
    {
        id: 8,
        name: 'BearBrain',
        icon: '🐻',
        team: 'BearTech',
        elo: 1598,
        winRate: 54,
        battles: 534,
        trend: 'down',
        trendValue: -8,
        specialties: ['📊 商業', '📖 語言']
    },
    {
        id: 9,
        name: 'WolfWisdom',
        icon: '🐺',
        team: 'Wolf Pack AI',
        elo: 1567,
        winRate: 52,
        battles: 498,
        trend: 'up',
        trendValue: 15,
        specialties: ['⚛️ 物理', '📐 數學']
    },
    {
        id: 10,
        name: 'EagleEye',
        icon: '🦅',
        team: 'Eagle Vision',
        elo: 1543,
        winRate: 50,
        battles: 467,
        trend: 'stable',
        trendValue: 0,
        specialties: ['🎨 藝術', '📖 語言']
    }
];

const personaPresets = {
    beginner: '我是完全的初學者，沒有相關背景知識，希望從最基礎的概念開始學習。',
    intermediate: '我有一些基礎知識，了解基本概念，希望能深入了解更多細節和應用。',
    advanced: '我已經有扎實的基礎，希望學習進階概念、最新發展和實際應用案例。'
};

// ============================================
// State Management
// ============================================

const state = {
    currentPage: 'home',
    battleStep: 1,
    learningRequest: {
        topic: '',
        persona: '',
        category: ''
    },
    currentBattle: {
        modelA: null,
        modelB: null,
        topic: ''
    },
    user: null
};

// ============================================
// Navigation
// ============================================

function navigateTo(page) {
    // Update state
    state.currentPage = page;

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });

    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(page).classList.add('active');

    // Reset battle if navigating to battle page
    if (page === 'battle') {
        resetBattle();
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

// Initialize navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(link.dataset.page);
    });
});

// ============================================
// Battle System
// ============================================

function setTopic(topic) {
    document.getElementById('topic').value = topic;
    state.learningRequest.topic = topic;
}

function setPersona(presetKey) {
    const textarea = document.getElementById('persona');
    textarea.value = personaPresets[presetKey];
    state.learningRequest.persona = personaPresets[presetKey];

    // Update button states
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        btn.style.color = 'var(--text-secondary)';
    });
    event.target.style.borderColor = 'var(--primary)';
    event.target.style.color = 'var(--primary-light)';
}

function startBattle() {
    const topic = document.getElementById('topic').value;
    const persona = document.getElementById('persona').value;
    const category = document.getElementById('category').value;

    if (!topic) {
        showToast('請輸入學習主題', 'error');
        return;
    }

    // Save learning request
    state.learningRequest = { topic, persona, category };

    // Show loading step
    showStep(2);

    // Simulate loading
    simulateLoading();
}

function simulateLoading() {
    const progressBar = document.getElementById('loadingProgress');
    const progressText = document.getElementById('progressText');
    const steps = [
        { progress: 20, text: '正在分析學習需求...' },
        { progress: 40, text: '配對教學 AI 模型...' },
        { progress: 60, text: 'AI 正在生成教學影片...' },
        { progress: 80, text: '優化影片品質...' },
        { progress: 100, text: '準備完成！' }
    ];

    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            progressBar.style.width = steps[currentStep].progress + '%';
            progressText.textContent = steps[currentStep].text;
            currentStep++;
        } else {
            clearInterval(interval);
            // Select random models for battle
            selectBattleModels();
            // Show battle arena
            setTimeout(() => showStep(3), 500);
        }
    }, 800);
}

function selectBattleModels() {
    // Randomly select two different models
    const shuffled = [...mockModels].sort(() => 0.5 - Math.random());
    state.currentBattle = {
        modelA: shuffled[0],
        modelB: shuffled[1],
        topic: state.learningRequest.topic
    };

    // Update battle topic display
    document.getElementById('battleTopic').textContent = state.learningRequest.topic;
}

function showStep(stepNum) {
    state.battleStep = stepNum;

    document.querySelectorAll('.battle-step').forEach((step, index) => {
        if (index + 1 === stepNum) {
            step.classList.remove('hidden');
        } else {
            step.classList.add('hidden');
        }
    });
}

function submitVote(choice) {
    // Animate vote buttons
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.style.pointerEvents = 'none';
        btn.style.opacity = '0.5';
    });

    if (choice === 'A') {
        document.querySelector('.vote-a').style.opacity = '1';
        document.querySelector('.vote-a').style.transform = 'scale(1.05)';
    } else if (choice === 'B') {
        document.querySelector('.vote-b').style.opacity = '1';
        document.querySelector('.vote-b').style.transform = 'scale(1.05)';
    } else {
        document.querySelector('.vote-tie').style.opacity = '1';
        document.querySelector('.vote-tie').style.transform = 'scale(1.05)';
    }

    // Show results after animation
    setTimeout(() => {
        showResults(choice);
    }, 1000);
}

function showResults(choice) {
    // Update reveal cards with actual model info
    const revealA = document.getElementById('revealA');
    const revealB = document.getElementById('revealB');

    revealA.querySelector('.model-icon').textContent = state.currentBattle.modelA.icon;
    revealA.querySelector('h3').textContent = state.currentBattle.modelA.name;

    revealB.querySelector('.model-icon').textContent = state.currentBattle.modelB.icon;
    revealB.querySelector('h3').textContent = state.currentBattle.modelB.name;

    // Update winner/loser styling based on vote
    if (choice === 'A') {
        revealA.classList.add('winner');
        revealA.classList.remove('loser');
        revealB.classList.add('loser');
        revealB.classList.remove('winner');
        revealA.querySelector('.reveal-badge').textContent = '你選擇的';
    } else if (choice === 'B') {
        revealB.classList.add('winner');
        revealB.classList.remove('loser');
        revealA.classList.add('loser');
        revealA.classList.remove('winner');
        revealB.querySelector('.reveal-badge').textContent = '你選擇的';
        revealA.querySelector('.reveal-badge').textContent = '';
    } else {
        revealA.classList.remove('winner', 'loser');
        revealB.classList.remove('winner', 'loser');
        revealA.querySelector('.reveal-badge').textContent = '平手';
        revealB.querySelector('.reveal-badge').textContent = '平手';
    }

    showStep(4);
    showToast('感謝你的投票！', 'success');
}

function skipBattle() {
    selectBattleModels();
    showToast('已跳過此場對決', 'success');
}

function newBattle() {
    resetBattle();
    showStep(1);
}

function resetBattle() {
    state.battleStep = 1;
    state.currentBattle = { modelA: null, modelB: null, topic: '' };

    // Reset form
    document.getElementById('topic').value = '';
    document.getElementById('persona').value = '';
    document.getElementById('category').value = '';

    // Reset loading progress
    document.getElementById('loadingProgress').style.width = '0%';
    document.getElementById('progressText').textContent = '正在分析學習需求...';

    // Reset vote buttons
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.style.pointerEvents = 'auto';
        btn.style.opacity = '1';
        btn.style.transform = 'scale(1)';
    });

    showStep(1);
}

// ============================================
// Leaderboard
// ============================================

function renderLeaderboard() {
    const tbody = document.getElementById('leaderboardBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    mockModels.forEach((model, index) => {
        const row = document.createElement('div');
        row.className = 'table-row';

        const rankClass = index < 3 ? `top-${index + 1}` : '';
        const rankEmoji = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';

        const trendIcon = model.trend === 'up' ? 'fa-arrow-up' :
                          model.trend === 'down' ? 'fa-arrow-down' : 'fa-minus';
        const trendClass = model.trend;
        const trendText = model.trendValue > 0 ? `+${model.trendValue}` :
                          model.trendValue < 0 ? model.trendValue : '-';

        row.innerHTML = `
            <div class="col-rank ${rankClass}">${rankEmoji || index + 1}</div>
            <div class="col-model">
                <span class="model-icon-small">${model.icon}</span>
                <div class="model-info">
                    <span class="name">${model.name}</span>
                    <span class="team">${model.team}</span>
                </div>
            </div>
            <div class="col-elo">${model.elo}</div>
            <div class="col-winrate">${model.winRate}%</div>
            <div class="col-battles">${model.battles}</div>
            <div class="col-trend ${trendClass}">
                <i class="fas ${trendIcon}"></i>
                ${trendText}
            </div>
            <div class="col-specialty">
                ${model.specialties.map(s => `<span class="specialty-tag">${s}</span>`).join('')}
            </div>
        `;

        tbody.appendChild(row);
    });
}

// ============================================
// Modals
// ============================================

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.body.style.overflow = '';
}

// Modal triggers
document.getElementById('loginBtn')?.addEventListener('click', () => openModal('loginModal'));
document.getElementById('registerBtn')?.addEventListener('click', () => openModal('registerModal'));

// Close modals on background click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal(modal.id);
        }
    });
});

// Role selector in register modal
document.querySelectorAll('.role-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');
    const toastIcon = toast.querySelector('.toast-icon');

    toastMessage.textContent = message;
    toastIcon.textContent = type === 'success' ? '✓' : '✗';

    toast.classList.remove('success', 'error');
    toast.classList.add(type, 'active');

    setTimeout(() => {
        toast.classList.remove('active');
    }, 3000);
}

// ============================================
// API Testing (Provider Page)
// ============================================

function testAPI() {
    const endpoint = document.getElementById('testEndpoint').value;
    const payload = document.getElementById('testPayload').textContent;

    if (!endpoint) {
        showToast('請輸入 API Endpoint', 'error');
        return;
    }

    // Show loading state
    const resultDiv = document.getElementById('testResult');
    const resultContent = document.getElementById('testResultContent');

    resultDiv.classList.remove('hidden');
    resultContent.textContent = '正在測試 API...';

    // Simulate API test (in real app, this would make an actual request)
    setTimeout(() => {
        const mockResponse = {
            request_id: 'test-001',
            status: 'success',
            video: {
                url: 'https://cdn.example.com/video/test-001.mp4',
                duration_seconds: 245,
                format: 'mp4',
                resolution: '1080p'
            },
            supplementary_materials: [
                {
                    type: 'slides',
                    url: 'https://cdn.example.com/slides/test-001.pdf',
                    title: '教學投影片'
                }
            ],
            metadata: {
                style: 'slides_voiceover',
                ai_model: 'test-model-v1',
                generation_time_seconds: 45
            }
        };

        resultContent.textContent = JSON.stringify(mockResponse, null, 2);
        showToast('API 測試成功！', 'success');
    }, 2000);
}

// ============================================
// Form Submissions
// ============================================

// Provider registration form
document.getElementById('providerForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    showToast('申請已提交！我們會盡快審核。', 'success');
});

// Auth forms
document.querySelectorAll('.auth-form').forEach(form => {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        showToast('功能開發中...', 'success');
        closeModal('loginModal');
        closeModal('registerModal');
    });
});

// ============================================
// Animated Counters
// ============================================

function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// ============================================
// Mobile Menu
// ============================================

document.querySelector('.mobile-menu-btn')?.addEventListener('click', () => {
    const navLinks = document.querySelector('.nav-links');
    const navAuth = document.querySelector('.nav-auth');

    // Toggle mobile menu (simplified - in production would have proper mobile menu)
    if (navLinks.style.display === 'flex') {
        navLinks.style.display = 'none';
        navAuth.style.display = 'none';
    } else {
        navLinks.style.display = 'flex';
        navLinks.style.position = 'absolute';
        navLinks.style.top = '70px';
        navLinks.style.left = '0';
        navLinks.style.right = '0';
        navLinks.style.background = 'var(--bg-dark)';
        navLinks.style.flexDirection = 'column';
        navLinks.style.padding = '20px';

        navAuth.style.display = 'flex';
        navAuth.style.position = 'absolute';
        navAuth.style.top = '200px';
        navAuth.style.left = '0';
        navAuth.style.right = '0';
        navAuth.style.background = 'var(--bg-dark)';
        navAuth.style.justifyContent = 'center';
        navAuth.style.padding = '20px';
    }
});

// ============================================
// Video Player Mock Interactions
// ============================================

document.querySelectorAll('.mock-video').forEach(video => {
    video.addEventListener('click', () => {
        const icon = video.querySelector('i');
        const text = video.querySelector('span');

        if (icon.classList.contains('fa-play-circle')) {
            icon.classList.remove('fa-play-circle');
            icon.classList.add('fa-pause-circle');
            text.textContent = '播放中...';
        } else {
            icon.classList.remove('fa-pause-circle');
            icon.classList.add('fa-play-circle');
            text.textContent = '點擊播放';
        }
    });
});

document.querySelectorAll('.control-btn').forEach(btn => {
    const icon = btn.querySelector('i');
    if (icon && icon.classList.contains('fa-play')) {
        btn.addEventListener('click', () => {
            if (icon.classList.contains('fa-play')) {
                icon.classList.remove('fa-play');
                icon.classList.add('fa-pause');
            } else {
                icon.classList.remove('fa-pause');
                icon.classList.add('fa-play');
            }
        });
    }
});

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', (e) => {
    // ESC to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            closeModal(modal.id);
        });
    }
});

// ============================================
// Initialize
// ============================================

function init() {
    // Render leaderboard
    renderLeaderboard();

    // Animate hero stats on page load
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(document.getElementById('totalBattles'), 12847);
                animateCounter(document.getElementById('totalVoters'), 3521);
                animateCounter(document.getElementById('totalModels'), 24);
                statsObserver.disconnect();
            }
        });
    });

    const heroStats = document.querySelector('.hero-stats');
    if (heroStats) {
        statsObserver.observe(heroStats);
    }

    // Handle URL hash navigation
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(hash)) {
        navigateTo(hash);
    }

    console.log('🐲 教學怪物 initialized!');
}

// Run on DOM ready
document.addEventListener('DOMContentLoaded', init);

// Export functions for global access
window.navigateTo = navigateTo;
window.setTopic = setTopic;
window.setPersona = setPersona;
window.startBattle = startBattle;
window.submitVote = submitVote;
window.skipBattle = skipBattle;
window.newBattle = newBattle;
window.testAPI = testAPI;
window.openModal = openModal;
window.closeModal = closeModal;
