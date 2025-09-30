/**
 * Laura-bot Dashboard JavaScript
 * Handles dashboard interactions and real-time updates
 */

// Global variables
let socket = null;
let subjects = [];
let hardwareStatus = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeDashboard();
    loadDashboardData();
});

function initializeSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('✅ Connected to Laura-bot server');
            updateConnectionStatus(true);
        });
        
        socket.on('disconnect', function() {
            console.log('⚠️ Disconnected from server');
            updateConnectionStatus(false);
        });
        
        socket.on('hardware_status', function(data) {
            updateHardwareStatus(data.status);
        });
        
        socket.on('learning_update', function(data) {
            updateLearningProgress(data);
        });
        
        socket.on('ai_response', function(data) {
            displayAIResponse(data.message);
        });
        
    } catch (error) {
        console.error('Socket.IO initialization failed:', error);
        updateConnectionStatus(false);
    }
}

function initializeDashboard() {
    // Initialize dashboard components
    setupEventListeners();
    startStatusUpdates();
    loadUserPreferences();
}

function setupEventListeners() {
    // Quick action buttons
    const quickLearnBtn = document.getElementById('quick-learn-btn');
    const quickQuizBtn = document.getElementById('quick-quiz-btn');
    const quickProgressBtn = document.getElementById('quick-progress-btn');
    const quickHardwareBtn = document.getElementById('quick-hardware-btn');
    
    if (quickLearnBtn) {
        quickLearnBtn.addEventListener('click', () => window.location.href = '/learn');
    }
    
    if (quickQuizBtn) {
        quickQuizBtn.addEventListener('click', startQuickQuiz);
    }
    
    if (quickProgressBtn) {
        quickProgressBtn.addEventListener('click', () => window.location.href = '/progress');
    }
    
    if (quickHardwareBtn) {
        quickHardwareBtn.addEventListener('click', () => window.location.href = '/hardware');
    }
    
    // Voice interaction
    const voiceBtn = document.getElementById('voice-interaction-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', startVoiceInteraction);
    }
    
    // AI chat
    const chatBtn = document.getElementById('ai-chat-btn');
    if (chatBtn) {
        chatBtn.addEventListener('click', toggleAIChat);
    }
}

function loadDashboardData() {
    // Load subjects from data attributes first, then from server
    const body = document.body;
    const dataSubjects = body.getAttribute('data-subjects');
    if (dataSubjects && dataSubjects.trim()) {
        subjects = dataSubjects.split(',').filter(s => s.trim());
        updateSubjectsList();
    }
    
    // Load subjects from server as backup
    fetch('/api/subjects')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.subjects && data.subjects.length > 0) {
                subjects = data.subjects;
                updateSubjectsList();
            }
        })
        .catch(error => {
            console.warn('Could not load subjects from server:', error.message);
            if (subjects.length === 0) {
                subjects = ['Mathematics', 'Science', 'Literature', 'History'];
                updateSubjectsList();
            }
        });
    
    // Load learning progress
    fetch('/api/progress/summary')
        .then(response => response.json())
        .then(data => {
            updateProgressSummary(data);
        })
        .catch(error => {
            console.error('Error loading progress:', error);
            showFallbackProgress();
        });
    
    // Load hardware status
    fetch('/api/hardware/status')
        .then(response => response.json())
        .then(data => {
            updateHardwareStatus(data.connected);
        })
        .catch(error => {
            console.error('Error loading hardware status:', error);
            updateHardwareStatus(false);
        });
}

function startQuickQuiz() {
    if (!subjects || subjects.length === 0) {
        showToast('No subjects available for quiz', 'warning');
        return;
    }
    
    const randomSubject = subjects[Math.floor(Math.random() * subjects.length)];
    
    fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            subject: randomSubject,
            difficulty: 'medium',
            num_questions: 5
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/quiz?subject=' + encodeURIComponent(randomSubject);
        } else {
            showToast('Error generating quiz: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Quiz generation error:', error);
        showToast('Quiz service unavailable. Please try again later.', 'error');
    });
}

function startVoiceInteraction() {
    if (!socket) {
        showToast('Connection not available', 'error');
        return;
    }
    
    const voiceBtn = document.getElementById('voice-interaction-btn');
    if (voiceBtn) {
        voiceBtn.textContent = '🎙️ Listening...';
        voiceBtn.disabled = true;
    }
    
    socket.emit('start_voice_interaction');
    
    // Reset button after timeout
    setTimeout(() => {
        if (voiceBtn) {
            voiceBtn.textContent = '🎙️ Voice Interaction';
            voiceBtn.disabled = false;
        }
    }, 5000);
}

function toggleAIChat() {
    const chatContainer = document.getElementById('ai-chat-container');
    if (chatContainer) {
        chatContainer.style.display = chatContainer.style.display === 'none' ? 'block' : 'none';
    }
}

function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connection-status');
    if (statusIndicator) {
        statusIndicator.className = connected ? 'status-online' : 'status-offline';
        statusIndicator.textContent = connected ? 'Online' : 'Offline';
    }
}

function updateHardwareStatus(connected) {
    hardwareStatus = connected;
    const statusIndicator = document.getElementById('hardware-status');
    if (statusIndicator) {
        statusIndicator.className = connected ? 'status-online' : 'status-offline';
        statusIndicator.textContent = connected ? 'Connected' : 'Disconnected';
    }
    
    // Update quick hardware button state
    const hardwareBtn = document.getElementById('quick-hardware-btn');
    if (hardwareBtn) {
        hardwareBtn.style.opacity = connected ? '1' : '0.6';
    }
}

function updateSubjectsList() {
    const subjectsList = document.getElementById('subjects-list');
    if (subjectsList && subjects.length > 0) {
        subjectsList.innerHTML = subjects.map(subject => 
            `<li class="subject-item">${subject}</li>`
        ).join('');
    }
}

function updateProgressSummary(data) {
    // Update progress statistics
    const sessionsCount = document.getElementById('sessions-count');
    const studyTime = document.getElementById('study-time');
    const achievementsCount = document.getElementById('achievements-count');
    
    if (sessionsCount) sessionsCount.textContent = data.sessions || '0';
    if (studyTime) studyTime.textContent = data.studyTime || '0h 0m';
    if (achievementsCount) achievementsCount.textContent = data.achievements || '0';
    
    // Update progress bars
    updateProgressBar('math-progress', data.mathProgress || 0);
    updateProgressBar('science-progress', data.scienceProgress || 0);
    updateProgressBar('overall-progress', data.overallProgress || 0);
}

function showFallbackProgress() {
    // Show sample progress data when real data is unavailable
    updateProgressSummary({
        sessions: '12',
        studyTime: '5h 30m',
        achievements: '8',
        mathProgress: 75,
        scienceProgress: 60,
        overallProgress: 68
    });
}

function updateProgressBar(id, percentage) {
    const progressBar = document.getElementById(id);
    if (progressBar) {
        const fill = progressBar.querySelector('.progress-fill');
        if (fill) {
            fill.style.width = percentage + '%';
        }
    }
}

function updateLearningProgress(data) {
    // Handle real-time learning progress updates
    if (data.subject && data.progress !== undefined) {
        updateProgressBar(data.subject.toLowerCase() + '-progress', data.progress);
    }
    
    if (data.message) {
        showToast(data.message, 'info');
    }
}

function displayAIResponse(message) {
    const chatContainer = document.getElementById('ai-chat-messages');
    if (chatContainer) {
        const messageElement = document.createElement('div');
        messageElement.className = 'ai-message';
        messageElement.innerHTML = `
            <div class="message-bubble ai-bubble">
                <p>${message}</p>
                <small>${new Date().toLocaleTimeString()}</small>
            </div>
        `;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function startStatusUpdates() {
    // Update status indicators every 30 seconds
    setInterval(() => {
        if (socket && socket.connected) {
            socket.emit('ping');
        }
    }, 30000);
    
    // Update time-based elements
    setInterval(updateTimeElements, 60000);
}

function updateTimeElements() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    timeElements.forEach(element => {
        element.textContent = now.toLocaleTimeString();
    });
}

function loadUserPreferences() {
    // Load user preferences from localStorage
    const preferences = JSON.parse(localStorage.getItem('laura-bot-preferences') || '{}');
    
    // Apply preferences
    if (preferences.theme) {
        document.body.classList.add(preferences.theme);
    }
    
    if (preferences.notifications !== undefined) {
        // Set notification preferences
        console.log('Notifications:', preferences.notifications ? 'enabled' : 'disabled');
    }
}

function showToast(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add to page
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Utility functions
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m`;
    }
}

function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        startQuickQuiz,
        updateHardwareStatus,
        updateProgressSummary,
        showToast,
        formatTime,
        formatDate
    };
}
