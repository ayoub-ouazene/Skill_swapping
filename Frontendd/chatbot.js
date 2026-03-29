document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatBody = document.getElementById('chatBody');

    // Retrieve token
    const token = localStorage.getItem('skillswap_token');

    // Function to add a text message to the screen
    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role === 'user' ? 'user-msg' : 'agent-msg'}`;
        
        msgDiv.innerHTML = `
            <div class="bubble">
                ${text}
            </div>
        `;
        
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
    }

    // Function to generate the HTML for a teacher card & handle the Enroll click
    function createTeacherCardHTML(teacher) {
        const displayRating = teacher.rating ? teacher.rating : "New";
        
        const cardDiv = document.createElement('div');
        cardDiv.className = "mentor-card"; 
        cardDiv.style.flexDirection = "column"; 
        
        // We do NOT use onclick in the HTML anymore. We attach an event listener below.
        cardDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; width: 100%;">
                <div>
                    <h4 style="margin: 0 0 5px 0; color: #111; font-size: 16px;">
                        👤 ${teacher.first_name} ${teacher.last_name}
                    </h4>
                    <span class="badge-expert">⭐ ${displayRating}</span>
                </div>
            </div>
            
            <p style="margin: 10px 0 0 0; font-size: 13px; color: #666;">
                Expertise Match: <strong>${teacher.matched_skill}</strong>
            </p>
            
            <div class="chat-actions" style="margin-top: 15px;">
                <button class="btn btn-teal enroll-btn">
                    Enroll Now
                </button>
            </div>
        `;

        // Grab the button we just created inside this specific card
        const enrollBtn = cardDiv.querySelector('.enroll-btn');

        // Attach the enrollment logic directly to this button
        enrollBtn.addEventListener('click', async () => {
            
            // 1. Safety check: Did the backend provide a skill_id?
            if (!teacher.skill_id) {
                appendMessage('agent', "⚠️ Developer Error: The backend did not return a `skill_id` for this teacher. Please update your `/Search_skills` endpoint to include it.");
                return;
            }

            // 2. UI Update: Show loading state
            enrollBtn.innerText = "Enrolling...";
            enrollBtn.disabled = true;

            try {
                // 3. Make the API Call
                // IMPORTANT: Replace the URL if your router has a prefix (e.g., /sessions/enroll)
                const response = await fetch('http://127.0.0.1:8000/enroll', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        teacher_id: teacher.teacher_id,
                        skill_id: teacher.skill_id
                    })
                });

                const data = await response.json();

                // 4. Handle Success
                if (response.ok) {
                    enrollBtn.innerText = "✅ Enrolled";
                    enrollBtn.style.backgroundColor = "#4caf50"; // Turn button green
                    enrollBtn.style.color = "white";
                    
                    // Display success message directly in the chat!
                    appendMessage('agent', `🎉 **Success!** ${data.message}`);
                } 
                // 5. Handle Errors (e.g., enrolling with yourself, teacher not found)
                else {
                    enrollBtn.innerText = "Enroll Now"; // Reset button
                    enrollBtn.disabled = false;
                    
                    // Display the specific FastAPI HTTP Exception in the chat
                    appendMessage('agent', `❌ **Could not enroll:** ${data.detail}`);
                }
            } catch (error) {
                console.error("Enrollment Error:", error);
                enrollBtn.innerText = "Enroll Now";
                enrollBtn.disabled = false;
                appendMessage('agent', "⚠️ Network error while trying to enroll. The server might be unreachable.");
            }
        });

        return cardDiv;
    }

    // Function to send search message to Backend
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        chatInput.value = '';

        try {
            const response = await fetch('http://127.0.0.1:8000/matching/Search_skills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ user_query: message }) 
            });

            if (response.ok) {
                const data = await response.json();

                if (data.message) {
                    appendMessage('agent', data.message);
                }
                
                if (data.response_type === "MATCH_RESULTS" && Array.isArray(data.data) && data.data.length > 0) {
                    const cardsContainer = document.createElement('div');
                    cardsContainer.style.display = 'flex';
                    cardsContainer.style.flexDirection = 'column';
                    cardsContainer.style.gap = '10px';
                    cardsContainer.style.alignSelf = 'flex-start';
                    cardsContainer.style.maxWidth = '85%';
                    cardsContainer.style.marginTop = '-10px'; 
                    
                    data.data.forEach(teacher => {
                        const card = createTeacherCardHTML(teacher);
                        cardsContainer.appendChild(card);
                    });

                    chatBody.appendChild(cardsContainer);
                    chatBody.scrollTop = chatBody.scrollHeight;
                }
                
            } else {
                const errorData = await response.json();
                appendMessage('agent', `Oops! Error: ${errorData.detail || "Technical difficulty"}`);
            }
        } catch (error) {
            console.error("Chat Error:", error);
            appendMessage('agent', "A frontend error occurred or the server is unreachable. Check console.");
        }
    }

    // Events
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            sendMessage();
        }
    });
});