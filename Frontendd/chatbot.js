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

    // 1. Display user message and clear input
    appendMessage('user', message);
    chatInput.value = '';

    try {
        // 2. Call your FastAPI Smart Matching endpoint
        // NOTE: Replace 'http://127.0.0.1:8000' with your Render URL if deployed!
        const response = await fetch('http://127.0.0.1:8000/matching/Search_skills', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Ensure 'token' is defined in your scope
            },
            body: JSON.stringify({ user_query: message }) 
        });

        if (response.ok) {
            const data = await response.json();

            // 3. Always display the text message from the AI
            appendMessage('agent', data.message);
            
            // 4. If the intent was MATCH_RESULTS, handle the teacher list
            if (data.response_type === "MATCH_RESULTS" && data.data) {
                console.log("Found teachers:", data.data);
                
                // You can call a function here to render cards for each teacher
                data.data.forEach(teacher => {
                    displayTeacherCard(teacher); 
                });
            }
            
        } else {
            const errorData = await response.json();
            appendMessage('agent', `Error: ${errorData.detail || "Technical difficulty"}`);
        }
    } catch (error) {
        console.error("Chat Error:", error);
        appendMessage('agent', "The server is unreachable. Check your connection or backend status.");
    }
}


    // Événements
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});