// UNE SEULE DÉCLARATION ICI
const token = localStorage.getItem('skillswap_token');

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
                const response = await fetch('http://127.0.0.1:8000/certificates/skills/add', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                if (response.ok) {
                    alert("Certificat validé !");
                    location.reload();
                } else {
                    const errorData = await response.json();
                    alert("Erreur : " + (errorData.detail || "Refusé"));
                }
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
});


async function loadUserProfile() {
    if (!token) return;
    try {
        const response = await fetch('http://127.0.0.1:8000/users/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const user = await response.json();
            document.getElementById('userNameDisplay').textContent = user.full_name || "Utilisateur";
            
            const walletDiv = document.querySelector('.time-wallet');
            if (walletDiv) walletDiv.innerHTML = `<i class="fas fa-wallet"></i> Time Wallet: ${user.credits}h`;
        }
    } catch (e) {
        console.error("Erreur profil:", e);
    }
}


    const creditFileInput = document.getElementById('file-upload');
    const creditFileNameDisplay = document.getElementById('file-name');

  
    if (creditFileInput && creditFileNameDisplay) {
        creditFileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                creditFileNameDisplay.textContent = this.files[0].name;
                creditFileNameDisplay.style.color = "#6366f1";
                

                handleCreditUpload(this.files[0]);
            }
        });
    }

    
    async function handleCreditUpload(file) {
        const formData = new FormData();
        formData.append("file", file);

        try {
            console.log("Envoi du certificat pour crédit...");
            const response = await fetch('http://127.0.0.1:8000/certificates/credits/add', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });

            if (response.ok) {
                alert("Certificat de crédit envoyé avec succès !");
                location.reload();
            } else {
                const errorData = await response.json();
                alert("Erreur crédit : " + (errorData.detail || "Refusé"));
            }
        } catch (error) {
            console.error("Erreur serveur:", error);
            alert("Erreur de connexion au serveur pour les crédits.");
        }
    }


    document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('swapModal');
    const openButtons = document.querySelectorAll('.btn-open-modal');
    const closeBtn = document.getElementById('closeModalBtn');
    const continueBtn = document.getElementById('continueBtn');
    const successPopup = document.getElementById('successPopup');

    
    openButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modal.style.display = 'flex'; 
        });
    });


    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

   
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

  
    if(continueBtn) {
        continueBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            successPopup.style.display = 'flex';
        });
    }
});