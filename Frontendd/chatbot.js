document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('skillswap_token');
    const API =
        (typeof window !== 'undefined' && window.SKILLSWAP_API_BASE) ||
        'http://127.0.0.1:8000';
    const HISTORY_KEY = 'skillswap_ai_match_history';
    const MAX_STORED_TURNS = 40;

    /** @type {{ role: 'user'|'assistant', content: string }[]} */
    let matchHistory = [];

    function loadHistory() {
        try {
            const raw = sessionStorage.getItem(HISTORY_KEY);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    matchHistory = parsed.filter(
                        (x) =>
                            x &&
                            (x.role === 'user' || x.role === 'assistant') &&
                            typeof x.content === 'string'
                    );
                }
            }
        } catch (e) {
            console.warn('match history load', e);
            matchHistory = [];
        }
    }

    function saveHistory() {
        const slice = matchHistory.slice(-MAX_STORED_TURNS);
        matchHistory = slice;
        try {
            sessionStorage.setItem(HISTORY_KEY, JSON.stringify(slice));
        } catch (e) {
            console.warn('match history save', e);
        }
    }

    function renderMarkdown(md) {
        if (!md || typeof md !== 'string') return '';
        if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
            const d = document.createElement('div');
            d.textContent = md;
            return d.innerHTML;
        }
        marked.setOptions({ gfm: true, breaks: true });
        const raw = marked.parse(md);
        return DOMPurify.sanitize(raw, {
            ADD_ATTR: ['target', 'rel'],
        });
    }

    loadHistory();

    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatBody = document.getElementById('chatBody');

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role === 'user' ? 'user-msg' : 'agent-msg'}`;

        const bubble = document.createElement('div');
        bubble.className = 'bubble' + (role === 'agent' ? ' bubble-md' : '');

        if (role === 'user') {
            bubble.textContent = text;
        } else {
            bubble.innerHTML = renderMarkdown(text);
            bubble.querySelectorAll('a[href^="http"]').forEach((a) => {
                a.setAttribute('target', '_blank');
                a.setAttribute('rel', 'noopener noreferrer');
            });
        }

        msgDiv.appendChild(bubble);
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    if (matchHistory.length > 0 && chatBody) {
        chatBody.innerHTML = '';
        matchHistory.forEach((t) => {
            appendMessage(t.role === 'user' ? 'user' : 'agent', t.content);
        });
    }

    function formatMatchResults(data) {
        let reply =
            data.message ||
            data.answer ||
            data.response ||
            '';

        if (
            data.response_type === 'MATCH_RESULTS' &&
            Array.isArray(data.data) &&
            data.data.length > 0
        ) {
            const blocks = data.data.map((u, i) => {
                const handle =
                    u.teacher_handle ||
                    `${u.first_name || ''} ${u.last_name || ''}`.trim() ||
                    'membre';
                const name =
                    `${u.first_name || ''} ${u.last_name || ''}`.trim() || 'Enseignant';
                const skill = u.matched_skill || '—';
                const tid = u.teacher_id || '';
                const sid = u.skill_id || '';
                const profileUrl = `member.html?id=${encodeURIComponent(tid)}`;
                const msgUrl = `messages.html?peer=${encodeURIComponent(tid)}${
                    sid ? `&skill=${encodeURIComponent(sid)}` : ''
                }`;
                const rating =
                    typeof u.rating === 'number' && !Number.isNaN(u.rating)
                        ? u.rating.toFixed(1)
                        : '—';
                return (
                    `### ${i + 1}. @${handle}\n` +
                    `**${name}** · note ${rating}\n\n` +
                    `- **Compétence proposée :** *${skill}*\n` +
                    `- [**Voir le profil public**](${profileUrl})\n` +
                    `- [**Envoyer un message**](${msgUrl})\n`
                );
            });
            const intro = reply
                ? `${reply}\n\n---\n\n**Enseignants trouvés :**\n\n`
                : '**Enseignants trouvés :**\n\n';
            reply = intro + blocks.join('\n');
        }

        return reply || 'Réponse reçue.';
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        chatInput.value = '';

        const headers = {
            'Content-Type': 'application/json',
        };
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${API}/matching/Search_skills`, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    user_query: message,
                    history: matchHistory,
                }),
            });

            const raw = await response.text();
            let data = null;
            if (raw) {
                try {
                    data = JSON.parse(raw);
                } catch (parseErr) {
                    console.error('JSON invalide:', parseErr, raw.slice(0, 200));
                    appendMessage(
                        'agent',
                        'Réponse du serveur illisible. Vérifiez les logs du backend (erreur 500 / proxy).'
                    );
                    return;
                }
            }

            if (response.ok) {
                const replyText = formatMatchResults(data || {});
                appendMessage('agent', replyText);
                matchHistory.push({ role: 'user', content: message });
                matchHistory.push({ role: 'assistant', content: replyText });
                saveHistory();
            } else {
                let errText = 'Désolé, une erreur est survenue.';
                if (data && typeof data.detail === 'string') errText = data.detail;
                appendMessage('agent', errText);
            }
        } catch (error) {
            console.error('Erreur Chat:', error);
            const hint =
                error && error.message
                    ? error.message
                    : 'réseau ou CORS (API éteinte, mauvaise URL, etc.)';
            appendMessage(
                'agent',
                `Impossible de joindre l'API : **${hint}**. Vérifiez que uvicorn tourne (port 8000).`
            );
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    const walletEl = document.getElementById('chatbot-wallet');
    if (walletEl && token) {
        fetch(`${API}/users/me`, { headers: { Authorization: `Bearer ${token}` } })
            .then((r) => (r.ok ? r.json() : null))
            .then((me) => {
                if (me && typeof me.credit === 'number') {
                    walletEl.innerHTML = `<i class="fas fa-wallet"></i> Time Wallet: ${me.credit}h`;
                }
            })
            .catch(() => {});
    }
});
