document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatBody = document.getElementById('chatBody');

    // Fonction pour ajouter un message à l'écran
    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role === 'user' ? 'user-msg' : 'agent-msg'}`;
        
        msgDiv.innerHTML = `
            <div class="bubble">
                ${text}
            </div>
        `;
        
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight; // Scroll vers le bas
    }

    // Fonction pour envoyer le message au Backend
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // 1. Afficher le message de l'utilisateur
        appendMessage('user', message);
        chatInput.value = '';

        try {
            // 2. Appel à l'endpoint Smart Matching (vu dans ta capture)
            const response = await fetch('http://127.0.0.1:8000/matching/Search_skills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ query: message }) 
            });

            if (response.ok) {
                const data = await response.json();
                // 3. Afficher la réponse de l'IA
                // On suppose que ton backend renvoie un champ "response" ou "answer"
                appendMessage('agent', data.answer || data.response || "J'ai trouvé des correspondances pour vous !");
                
                // Si le backend renvoie un mentor, on pourrait générer la carte ici
            } else {
                appendMessage('agent', "Désolé, je rencontre une petite difficulté technique.");
            }
        } catch (error) {
            console.error("Erreur Chat:", error);
            appendMessage('agent', "Le serveur ne répond pas.");
        }
    }

    // Événements
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});