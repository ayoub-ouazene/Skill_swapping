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

document.addEventListener('DOMContentLoaded', () => {
   
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(section => {
        observer.observe(section);
    });

    
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 10px 30px rgba(0,0,0,0.08)';
            navbar.style.padding = '1rem 0';
        } else {
            navbar.style.boxShadow = 'none';
            navbar.style.padding = '1.25rem 0';
        }
    });
});

document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelector('.menu-item.active').classList.remove('active');
        this.classList.add('active');
    });
});

document.querySelector('.btn-login').addEventListener('click', () => {
    window.location.href = '#login';
});

document.querySelector('.btn-join').addEventListener('click', () => {
    window.location.href = '#join';
});
