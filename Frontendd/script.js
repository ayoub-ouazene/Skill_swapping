// UNE SEULE DÉCLARATION ICI — include api-config.js before this script, or set window.SKILLSWAP_API_BASE
const token = localStorage.getItem('skillswap_token');
const API_BASE =
    typeof window !== 'undefined' && typeof window.SKILLSWAP_API_BASE === 'string'
        ? window.SKILLSWAP_API_BASE
        : 'http://127.0.0.1:8000';

/** FastAPI erreurs : detail string | liste de {msg,loc} | objet */
function formatApiDetail(payload) {
    if (!payload || typeof payload !== 'object') return 'Erreur inconnue';
    if (typeof payload.message === 'string' && payload.detail == null) return payload.message;
    var d = payload.detail;
    if (d == null) return payload.message || 'Erreur inconnue';
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) {
        return d.map(function (x) {
            if (typeof x === 'string') return x;
            if (x && typeof x.msg === 'string') return x.msg;
            return JSON.stringify(x);
        }).join('\n');
    }
    if (typeof d === 'object') try { return JSON.stringify(d); } catch (e) { return String(d); }
    return String(d);
}

/** Copy text: sync execCommand first (same user-gesture tick), then Clipboard API. */
function fallbackCopyText(text) {
    if (!text) return false;
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.setAttribute('aria-hidden', 'true');
    ta.style.cssText =
        'position:fixed;left:0;top:0;width:2px;height:2px;margin:0;padding:0;border:0;opacity:0;';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    ta.setSelectionRange(0, text.length);
    var ok = false;
    try {
        ok = document.execCommand('copy');
    } catch (e) {
        ok = false;
    }
    document.body.removeChild(ta);
    return ok;
}

function copyTextToClipboard(text) {
    if (!text) return Promise.resolve(false);
    if (fallbackCopyText(text)) {
        return Promise.resolve(true);
    }
    try {
        if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
            return navigator.clipboard.writeText(text).then(function () { return true; }).catch(function () {
                return false;
            });
        }
    } catch (e) {}
    return Promise.resolve(false);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, token présent :", !!token);

 
    const skillsModal = document.getElementById('skillsModal');
    const openSkillsBtn = document.getElementById('openSkillsModal');
    const closeSkillsBtn = document.getElementById('closeSkillsBtn');

    if (openSkillsBtn && skillsModal) {
        openSkillsBtn.addEventListener('click', () => {
            console.log("Clic sur le bouton + détecté !");
            skillsModal.style.display = 'flex';
        });
    }

    if (closeSkillsBtn && skillsModal) {
        closeSkillsBtn.addEventListener('click', () => {
            skillsModal.style.display = 'none';
        });
    }

    window.addEventListener('click', (e) => {
        if (e.target === skillsModal) {
            skillsModal.style.display = 'none';
        }
    });

   
    const skillFileInput = document.getElementById('skill-file-upload');
    const skillFileNameDisplay = document.getElementById('skill-file-name');

    if (skillFileInput && skillFileNameDisplay) {
        skillFileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                skillFileNameDisplay.textContent = this.files[0].name;
                skillFileNameDisplay.style.color = "#0d827c";
            }
        });
    }


    const submitSkillBtn = document.getElementById('submitSkillBtn');
    if (submitSkillBtn) {
        submitSkillBtn.addEventListener('click', async () => {
            if (!skillFileInput.files.length) {
                alert("Choisis un fichier d'abord !");
                return;
            }

            const formData = new FormData();
            formData.append("file", skillFileInput.files[0]);

            submitSkillBtn.innerText = "IA en cours...";
            submitSkillBtn.disabled = true;

            try {
                const response = await fetch(API_BASE + '/certificates/skills/add', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                const data = await response.json().catch(function () { return {}; });
                if (!response.ok) {
                    alert('Erreur : ' + formatApiDetail(data));
                    return;
                }
                if (data.success === false) {
                    alert(data.message || 'Certificat refusé ou illisible.');
                    return;
                }
                alert('Certificat validé !');
                location.reload();
            } catch (error) {
                alert("Le serveur ne répond pas.");
            } finally {
                submitSkillBtn.innerText = "Submit for Verification";
                submitSkillBtn.disabled = false;
            }
        });
    }

    if (document.getElementById('userNameDisplay')) {
        loadUserProfile();
    }

    const wantModal = document.getElementById('wantSkillsModal');
    const openWantBtn = document.getElementById('openWantSkillsModal');
    const closeWantBtn = document.getElementById('closeWantSkillsBtn');
    if (openWantBtn && wantModal) {
        openWantBtn.addEventListener('click', () => {
            wantModal.style.display = 'flex';
            const inp = document.getElementById('want-skill-input');
            if (inp) inp.focus();
        });
    }
    if (closeWantBtn && wantModal) {
        closeWantBtn.addEventListener('click', () => {
            wantModal.style.display = 'none';
        });
    }
    window.addEventListener('click', (e) => {
        if (wantModal && e.target === wantModal) wantModal.style.display = 'none';
    });

    const wantSkillInput = document.getElementById('want-skill-input');
    const saveWantBtn = document.getElementById('saveWantSkillBtn');
    if (wantSkillInput && saveWantBtn) {
        wantSkillInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveWantBtn.click();
            }
        });
    }
    if (saveWantBtn) {
        saveWantBtn.addEventListener('click', async () => {
            const inp = document.getElementById('want-skill-input');
            const name = (inp && inp.value || '').trim();
            if (!name) {
                alert('Entrez un nom de compétence.');
                return;
            }
            if (!token) return;
            saveWantBtn.disabled = true;
            try {
                const response = await fetch(API_BASE + '/users/me/desired-skills', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ skill_name: name }),
                });
                const data = await response.json().catch(() => ({}));
                if (response.ok) {
                    if (inp) inp.value = '';
                    if (wantModal) wantModal.style.display = 'none';
                    loadUserProfile();
                } else {
                    alert(typeof data.detail === 'string' ? data.detail : 'Impossible d’ajouter.');
                }
            } catch (err) {
                alert('Erreur réseau.');
            } finally {
                saveWantBtn.disabled = false;
            }
        });
    }

    const copyHandleBtn = document.getElementById('copyHandleBtn');
    if (copyHandleBtn) {
        copyHandleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var raw =
                (copyHandleBtn.getAttribute('data-copy-value') || '').trim() ||
                (function () {
                    var span = document.getElementById('userHandleDisplay');
                    if (span && span.dataset && span.dataset.handle) return String(span.dataset.handle).trim();
                    if (span && span.textContent) return span.textContent.replace(/^@/, '').trim();
                    return '';
                })();
            if (!raw) {
                alert('Pseudo indisponible — rechargez la page.');
                return;
            }
            copyTextToClipboard(raw).then(function (ok) {
                var prev = copyHandleBtn.innerHTML;
                if (ok) {
                    copyHandleBtn.innerHTML = '<i class="fas fa-check"></i>';
                    copyHandleBtn.title = 'Copié !';
                    setTimeout(function () {
                        copyHandleBtn.innerHTML = prev;
                        copyHandleBtn.title = 'Copy username';
                    }, 1400);
                } else {
                    window.prompt('Copiez ce pseudo (Ctrl+C puis OK) :', raw);
                }
            });
        });
    }

    const aboutModal = document.getElementById('aboutEditModal');
    const editAboutBtn = document.getElementById('editAboutBtn');
    const closeAboutBtn = document.getElementById('closeAboutBtn');
    const cancelAboutBtn = document.getElementById('cancelAboutBtn');
    const saveAboutBtn = document.getElementById('saveAboutBtn');
    const aboutBioInput = document.getElementById('about-bio-input');

    function closeAboutModal() {
        if (aboutModal) aboutModal.style.display = 'none';
    }

    function openAboutModal() {
        if (!aboutModal || !aboutBioInput) return;
        const bioEl = document.getElementById('profile-bio');
        aboutBioInput.value = bioEl && bioEl.dataset.rawBio != null ? bioEl.dataset.rawBio : '';
        aboutModal.style.display = 'flex';
        aboutBioInput.focus();
    }

    if (editAboutBtn) {
        editAboutBtn.addEventListener('click', () => {
            if (!token) {
                window.location.href = 'login.html';
                return;
            }
            openAboutModal();
        });
    }
    if (closeAboutBtn) closeAboutBtn.addEventListener('click', closeAboutModal);
    if (cancelAboutBtn) cancelAboutBtn.addEventListener('click', closeAboutModal);
    window.addEventListener('click', (e) => {
        if (aboutModal && e.target === aboutModal) closeAboutModal();
    });

    if (saveAboutBtn) {
        saveAboutBtn.addEventListener('click', async () => {
            if (!token) return;
            const bio = aboutBioInput ? aboutBioInput.value : '';
            saveAboutBtn.disabled = true;
            try {
                const response = await fetch(API_BASE + '/users/me', {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ bio: bio }),
                });
                const data = await response.json().catch(() => ({}));
                if (response.ok) {
                    closeAboutModal();
                    loadUserProfile();
                } else {
                    const msg =
                        typeof data.detail === 'string'
                            ? data.detail
                            : Array.isArray(data.detail)
                              ? data.detail.map((d) => d.msg || d).join(' ')
                              : 'Enregistrement impossible.';
                    alert(msg);
                }
            } catch (err) {
                alert('Erreur réseau.');
            } finally {
                saveAboutBtn.disabled = false;
            }
        });
    }

    const wantList = document.getElementById('skills-want-list');
    if (wantList) {
        wantList.addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-remove-want]');
            if (!btn || !token) return;
            const id = btn.getAttribute('data-remove-want');
            if (!id) return;
            e.preventDefault();
            try {
                const res = await fetch(`${API_BASE}/users/me/desired-skills/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` },
                });
                if (res.ok) loadUserProfile();
                else {
                    const err = await res.json().catch(() => ({}));
                    alert(typeof err.detail === 'string' ? err.detail : 'Suppression impossible.');
                }
            } catch (err) {
                alert('Erreur réseau.');
            }
        });
    }

    const creditFileInput = document.getElementById('file-upload');
    const creditFileNameDisplay = document.getElementById('file-name');
    const claimCreditsBtn = document.getElementById('claimCreditsBtn');
    var selectedCreditFile = null;

    if (creditFileInput && creditFileNameDisplay) {
        creditFileInput.addEventListener('change', function () {
            selectedCreditFile = this.files && this.files[0] ? this.files[0] : null;
            if (selectedCreditFile) {
                creditFileNameDisplay.textContent = selectedCreditFile.name;
                creditFileNameDisplay.style.color = '#6366f1';
            } else {
                creditFileNameDisplay.textContent = 'No file selected';
                creditFileNameDisplay.style.color = '';
            }
            if (claimCreditsBtn) claimCreditsBtn.disabled = !selectedCreditFile;
        });
    }

    if (claimCreditsBtn && creditFileInput) {
        claimCreditsBtn.addEventListener('click', async function () {
            if (!token || !selectedCreditFile) {
                alert('Choisissez un fichier PDF.');
                return;
            }
            claimCreditsBtn.disabled = true;
            try {
                await handleCreditUpload(selectedCreditFile);
            } finally {
                claimCreditsBtn.disabled = !selectedCreditFile;
            }
        });
    }

    const completeModal = document.getElementById('completeSessionModal');
    const closeCompleteBtn = document.getElementById('closeCompleteSessionBtn');
    const cancelCompleteBtn = document.getElementById('cancelCompleteSessionBtn');
    const submitCompleteBtn = document.getElementById('submitCompleteSessionBtn');
    const completeSessionIdInput = document.getElementById('complete-session-id');
    const completeSkillLabel = document.getElementById('complete-session-skill-label');

    function closeCompleteModal() {
        if (completeModal) completeModal.style.display = 'none';
    }

    if (closeCompleteBtn) closeCompleteBtn.addEventListener('click', closeCompleteModal);
    if (cancelCompleteBtn) cancelCompleteBtn.addEventListener('click', closeCompleteModal);
    window.addEventListener('click', function (e) {
        if (completeModal && e.target === completeModal) closeCompleteModal();
    });

    const ongoingListEl = document.getElementById('sessions-ongoing-list');
    if (ongoingListEl) {
        ongoingListEl.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-complete-session]');
            if (!btn || !completeModal || !completeSessionIdInput) return;
            var sid = btn.getAttribute('data-complete-session');
            var sname = btn.getAttribute('data-skill-name') || 'this session';
            completeSessionIdInput.value = sid;
            if (completeSkillLabel) {
                completeSkillLabel.textContent =
                    'Session: ' +
                    sname +
                    '. Enter the hours you spent and rate your teacher. Your wallet will be debited; your teacher receives the certificate by email.';
            }
            completeModal.style.display = 'flex';
        });
    }

    if (submitCompleteBtn && completeSessionIdInput) {
        submitCompleteBtn.addEventListener('click', async function () {
            if (!token) return;
            var sid = completeSessionIdInput.value;
            var durEl = document.getElementById('complete-duration');
            var rateEl = document.getElementById('complete-rating');
            var hours = durEl ? parseFloat(durEl.value, 10) : NaN;
            var rating = rateEl ? parseInt(rateEl.value, 10) : NaN;
            if (!sid || !(hours > 0) || rating < 1 || rating > 5) {
                alert('Durée (heures) et note valides requises.');
                return;
            }
            submitCompleteBtn.disabled = true;
            try {
                var res = await fetch(API_BASE + '/economy/Complete_Course', {
                    method: 'POST',
                    headers: {
                        Authorization: 'Bearer ' + token,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: sid,
                        student_rating: rating,
                        duration_hours: hours,
                    }),
                });
                var data = await res.json().catch(function () {
                    return {};
                });
                if (res.ok) {
                    alert(data.message || 'Session terminée.');
                    closeCompleteModal();
                    loadUserProfile();
                    loadSessions();
                } else {
                    alert(formatApiDetail(data));
                }
            } catch (err) {
                alert('Erreur réseau.');
            } finally {
                submitCompleteBtn.disabled = false;
            }
        });
    }

    const swapModal = document.getElementById('swapModal');
    if (swapModal) {
        var openSwapBtns = document.querySelectorAll('.btn-open-modal');
        var closeSwapBtn = document.getElementById('closeModalBtn');
        var continueBtn = document.getElementById('continueBtn');
        var successPopup = document.getElementById('successPopup');
        openSwapBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                swapModal.style.display = 'flex';
            });
        });
        if (closeSwapBtn) {
            closeSwapBtn.addEventListener('click', function () {
                swapModal.style.display = 'none';
            });
        }
        window.addEventListener('click', function (event) {
            if (event.target === swapModal) swapModal.style.display = 'none';
        });
        if (continueBtn && successPopup) {
            continueBtn.addEventListener('click', function () {
                swapModal.style.display = 'none';
                successPopup.style.display = 'flex';
            });
        }
    }

    if (document.getElementById('sessions-ongoing-list')) {
        loadSessions();
    }
});


function escapeHtmlProfile(text) {
    if (text == null) return '';
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

async function loadUserProfile() {
    if (!token) return;
    try {
        const response = await fetch(API_BASE + '/users/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const user = await response.json();
            const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
            const nameEl = document.getElementById('userNameDisplay');
            if (nameEl) nameEl.textContent = fullName || 'Utilisateur';

            const handleEl = document.getElementById('userHandleDisplay');
            if (handleEl) {
                if (user.handle) {
                    handleEl.textContent = `@${user.handle}`;
                    handleEl.dataset.handle = user.handle;
                } else {
                    handleEl.textContent = '';
                    handleEl.dataset.handle = '';
                }
            }
            const copyBtn = document.getElementById('copyHandleBtn');
            if (copyBtn) {
                copyBtn.hidden = !user.handle;
                if (user.handle) {
                    copyBtn.setAttribute('data-copy-value', user.handle);
                } else {
                    copyBtn.removeAttribute('data-copy-value');
                }
            }

            const bioEl = document.getElementById('profile-bio');
            if (bioEl) {
                const raw = user.bio == null ? '' : String(user.bio);
                bioEl.dataset.rawBio = raw;
                const b = raw.trim();
                bioEl.textContent =
                    b ||
                    'Aucune bio pour le moment. Cliquez sur le crayon pour en ajouter une.';
            }

            const sessEl = document.getElementById('sessions-count');
            if (sessEl) {
                sessEl.textContent = String(user.sessions_total ?? 0);
            }

            const skillsGrid = document.getElementById('skills-teach-grid');
            if (skillsGrid) {
                skillsGrid.innerHTML = '';
                const skills = user.skills || [];
                if (!skills.length) {
                    skillsGrid.innerHTML =
                        '<p style="padding:12px;color:#64748b;">Aucune compétence enregistrée. Utilisez + pour soumettre un certificat.</p>';
                } else {
                    skills.forEach(function (s) {
                        const div = document.createElement('div');
                        div.className = 'skill-item';
                        div.innerHTML =
                            '<div class="skill-item-header"><i class="fas fa-certificate"></i><span class="tag advanced">OFFERT</span></div>' +
                            '<h3>' + escapeHtmlProfile(s.skill_name) + '</h3>' +
                            '<p>Liste des compétences que vous enseignez sur SkillSwap.</p>';
                        skillsGrid.appendChild(div);
                    });
                }
            }

            const balanceStrong = document.querySelector('.credits-card .balance-row strong');
            if (balanceStrong && typeof user.credit === 'number') {
                balanceStrong.textContent = `${user.credit} Hours`;
            }

            const walletDiv = document.querySelector('.time-wallet');
            if (walletDiv && typeof user.credit === 'number') {
                walletDiv.innerHTML = `<i class="fas fa-wallet"></i> Time Wallet: ${user.credit}h`;
            }

            const wantListEl = document.getElementById('skills-want-list');
            if (wantListEl) {
                wantListEl.innerHTML = '';
                const wants = user.desired_skills || [];
                if (!wants.length) {
                    wantListEl.innerHTML =
                        '<p style="padding:12px;color:#64748b;">Aucune compétence souhaitée. Cliquez sur + pour en ajouter.</p>';
                } else {
                    wants.forEach(function (d) {
                        const row = document.createElement('div');
                        row.className = 'skill-row';
                        row.innerHTML =
                            '<div class="skill-icon-wrap"><i class="fas fa-book-open"></i></div>' +
                            '<div class="skill-row-text"><h3>' +
                            escapeHtmlProfile(d.skill_name) +
                            '</h3><p>Compétence à apprendre</p></div>' +
                            '<button type="button" class="want-remove-btn" data-remove-want="' +
                            String(d.id) +
                            '" title="Retirer">×</button>';
                        wantListEl.appendChild(row);
                    });
                }
            }
        }
    } catch (e) {
        console.error("Erreur profil:", e);
    }
}

async function handleCreditUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    try {
        const response = await fetch(API_BASE + '/economy/Claim_Credit', {
            method: 'POST',
            headers: { Authorization: 'Bearer ' + token },
            body: formData,
        });
        const credData = await response.json().catch(function () {
            return {};
        });
        if (response.ok) {
            if (credData.success === false) {
                alert(credData.message || 'Demande refusée.');
                return;
            }
            var rec = credData.receipt;
            var msg = credData.message || 'Crédits ajoutés.';
            if (rec && typeof rec.final_credits_earned !== 'undefined') {
                msg +=
                    '\n\n+' +
                    rec.final_credits_earned +
                    ' h credited (market ×' +
                    rec.market_multiplier +
                    ').\nNew balance: ' +
                    rec.new_wallet_balance +
                    ' h';
            }
            alert(msg);
            location.reload();
        } else {
            alert('Erreur crédit : ' + formatApiDetail(credData));
        }
    } catch (error) {
        console.error('Erreur serveur:', error);
        alert('Erreur de connexion au serveur pour les crédits.');
    }
}

async function loadSessions() {
    if (!token) return;
    var ongoingEl = document.getElementById('sessions-ongoing-list');
    var pastEl = document.getElementById('sessions-past-list');
    if (!ongoingEl || !pastEl) return;
    ongoingEl.innerHTML = '<p class="sessions-empty">Chargement…</p>';
    pastEl.innerHTML = '<p class="sessions-empty">Chargement…</p>';
    try {
        var meRes = await fetch(API_BASE + '/users/me', {
            headers: { Authorization: 'Bearer ' + token },
        });
        if (!meRes.ok) return;
        var me = await meRes.json();
        var meId = String(me.id);
        var ongoingRes = await fetch(API_BASE + '/sessions/ongoing', {
            headers: { Authorization: 'Bearer ' + token },
        });
        var pastRes = await fetch(API_BASE + '/sessions', {
            headers: { Authorization: 'Bearer ' + token },
        });
        var ongoingData = ongoingRes.ok ? await ongoingRes.json() : { items: [] };
        var pastData = pastRes.ok ? await pastRes.json() : { items: [] };
        var ongoingItems = ongoingData.items || [];
        var pastItems = pastData.items || [];

        function roleLine(s) {
            var stu = String(s.student_id) === meId;
            var tea = String(s.teacher_id) === meId;
            if (stu && tea) return 'Vous';
            if (stu) return 'Vous apprenez';
            if (tea) return 'Vous enseignez';
            return '';
        }

        function renderOngoingItem(s) {
            var skill = escapeHtmlProfile(s.skill_name || 'Compétence');
            var role = escapeHtmlProfile(roleLine(s));
            var rawName = String(s.skill_name || 'Session').replace(/"/g, '&quot;');
            var canFinalize = String(s.student_id) === meId && s.status === 'ONGOING';
            var btn = canFinalize
                ? '<button type="button" class="session-action-btn" data-complete-session="' +
                  String(s.id) +
                  '" data-skill-name="' +
                  rawName +
                  '">End session &amp; certificate</button>'
                : '';
            return (
                '<div class="session-row">' +
                '<div class="session-row-main"><strong>' +
                skill +
                '</strong><span class="session-role">' +
                role +
                '</span></div>' +
                '<span class="session-status-tag">' +
                escapeHtmlProfile(s.status) +
                '</span>' +
                btn +
                '</div>'
            );
        }

        ongoingEl.innerHTML = ongoingItems.length
            ? ongoingItems.map(renderOngoingItem).join('')
            : '<p class="sessions-empty">Aucune session en cours.</p>';

        function renderPastItem(s) {
            var skill = escapeHtmlProfile(s.skill_name || '—');
            var role = escapeHtmlProfile(roleLine(s));
            var dur = s.duration_hours != null ? ' · ' + s.duration_hours + 'h' : '';
            var rat = s.rating ? ' · ★' + s.rating : '';
            return (
                '<div class="session-row session-row-past">' +
                '<div class="session-row-main"><strong>' +
                skill +
                '</strong><span class="session-role">' +
                role +
                dur +
                rat +
                '</span></div>' +
                '<span class="session-status-tag">' +
                escapeHtmlProfile(s.status) +
                '</span></div>'
            );
        }

        pastEl.innerHTML = pastItems.length
            ? pastItems.map(renderPastItem).join('')
            : '<p class="sessions-empty">Aucun historique.</p>';
    } catch (e) {
        console.error('sessions:', e);
        ongoingEl.innerHTML = '<p class="sessions-empty">Impossible de charger les sessions.</p>';
        pastEl.innerHTML = '';
    }
}