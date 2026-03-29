document.addEventListener("DOMContentLoaded", () => {
   
    const modal = document.getElementById("swapModal");
    const closeBtn = document.getElementById("closeModalBtn");
    const openBtns = document.querySelectorAll(".btn-open-modal");

    if (!modal) console.error("ERREUR : L'élément #swapModal est introuvable dans le HTML !");
    if (!closeBtn) console.error("ERREUR : L'élément #closeModalBtn est introuvable dans le HTML !");
    
    console.log("Nombre de boutons d'ouverture trouvés :", openBtns.length);

    if (openBtns.length > 0 && modal) {
        openBtns.forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                modal.style.display = "flex";
                console.log("Popup ouverte");
            });
        });
    }


    if (closeBtn && modal) {
        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });
    }

  
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });
    }
});