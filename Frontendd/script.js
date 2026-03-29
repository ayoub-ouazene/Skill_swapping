document.addEventListener('DOMContentLoaded', function() {

    const swapModal = document.getElementById('swapModal');
    const successPopup = document.getElementById('successPopup');
    
    const openModalBtns = document.querySelectorAll('.btn-open-modal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const continueBtn = document.getElementById('continueBtn');
    const backToExploreBtn = document.querySelector('.btn-main');

   
    openModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            swapModal.style.display = 'flex';
        });
    });


    closeModalBtn.addEventListener('click', () => {
        swapModal.style.display = 'none';
    });


    continueBtn.addEventListener('click', function() {
        const isChecked = document.querySelector('input[name="swap_type"]:checked');

        if (isChecked) {
            swapModal.style.display = 'none';
   
            successPopup.style.display = 'flex';
            
            successPopup.style.opacity = '0';
            setTimeout(() => {
                successPopup.style.transition = 'opacity 0.5s ease';
                successPopup.style.opacity = '1';
            }, 10);
        } else {
            alert("S'il vous plaît, sélectionnez une option de swap !");
        }
    });

    backToExploreBtn.addEventListener('click', () => {
        successPopup.style.display = 'none';
        const radio = document.querySelector('input[name="swap_type"]:checked');
        if(radio) radio.checked = false;
    });

    window.addEventListener('click', (e) => {
        if (e.target === swapModal) swapModal.style.display = 'none';
        if (e.target === successPopup) successPopup.style.display = 'none';
    });
});
