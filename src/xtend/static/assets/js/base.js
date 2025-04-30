window.addEventListener("load", () => {
    const preloader = document.getElementById("preloader");
    const mainContent = document.getElementById("main-content");

    preloader.style.opacity = 0;
    setTimeout(() => {
        preloader.style.display = "none";
        mainContent.classList.remove("opacity-0");
    }, 300);
});

// Base Interactions
document.querySelectorAll('a, button').forEach(btn => {
    btn.addEventListener('click', function (e) {
        // Ripple Effect
        const rect = this.getBoundingClientRect();
        const ripple = document.createElement('div');
        ripple.style.left = (e.clientX - rect.left) + 'px';
        ripple.style.top = (e.clientY - rect.top) + 'px';
        ripple.classList.add('ripple-effect');
        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 500);
    });
});