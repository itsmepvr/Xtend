// Modal interactions
document.getElementById("select-close-popup").addEventListener("click", () => {
    document.getElementById('select-app-popup').classList.add("hidden");
});

document.getElementById("select-app").addEventListener("click", () => {
    document.getElementById("select-app-popup").classList.remove("hidden");
});

// Application selection
document.getElementById("select-app").addEventListener("click", () => {
    const popup = document.getElementById("select-app-popup");
    const loading = document.getElementById("loading-indicator");
    const grid = popup.querySelector(".grid");

    // Clear previous results
    grid.innerHTML = '';
    loading.classList.remove("hidden");
    popup.classList.remove("hidden");

    fetch("/get-applications")
        .then(response => response.json())
        .then(data => {
            loading.classList.add("hidden");
            data.applications.forEach(app => {
                const html = `
            <div class="select-app group relative bg-gray-800/50 rounded-lg cursor-pointer transition-all border border-transparent hover:border-blue-500/30 overflow-hidden"
                data-app="${app.name}">
                <div class="flex flex-col items-center h-32 relative">
                    ${app.thumbnail ?
                        `<img src="data:image/jpeg;base64,${app.thumbnail}" 
                            class="w-full h-full object-cover rounded-t-lg scale-100 transform transition-transform duration-300 group-hover:scale-105"
                            alt="${app.name} thumbnail">` :
                        `<div class="w-full h-full bg-gray-700 flex items-center justify-center">
                            <svg class="w-8 h-8 text-gray-400 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>`}
                    <span class="absolute bottom-0 left-0 right-0 px-2 py-1 text-sm font-medium text-white bg-gray-900/80 text-center truncate">
                        ${app.name}
                    </span>
                </div>
            </div>`;
                grid.insertAdjacentHTML('beforeend', html);
            });

            // Re-attach event listeners to new elements
            document.querySelectorAll(".select-app").forEach(el => {
                el.addEventListener("click", function () {
                    preLoader();
                    const preloader = document.getElementById("preloader");
                    const mainContent = document.getElementById("main-content");

                    preloader.style.opacity = 0;
                    // setTimeout(() => {
                    //     preloader.style.display = "none";
                    //     mainContent.classList.remove("opacity-0");
                    // }, 300);
                    const appName = this.dataset.app;
                    fetch("/select-app", {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: new URLSearchParams({ application: appName })
                    }).then(response => {
                        if (response.ok) window.location.reload();
                        else console.error("Failed to start session");
                    }).catch(console.error);
                });
            });
        })
        .catch(error => {
            console.error("Error fetching applications:", error);
            loading.classList.add("hidden");
        });
});

// Entire Screen capture
document.querySelectorAll("#select-screen").forEach(el => {
    el.addEventListener("click", function () {
        preLoader();
        fetch("/select-screen", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        }).then(response => {
            if (response.ok) window.location.reload();
            else console.error("Failed to start session");
        }).catch(console.error);
    });
});

function fallbackCopyTextToClipboard(text) {
    var textArea = document.createElement("textarea");
    textArea.value = text;

    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        var successful = document.execCommand('copy');
        var msg = successful ? 'successful' : 'unsuccessful';
        console.log('Fallback: Copying text command was ' + msg);
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }

    document.body.removeChild(textArea);
}
function copyToClipboard(text) {
    if (!navigator.clipboard) {
        fallbackCopyTextToClipboard(text);
        return;
    }
    navigator.clipboard.writeText(text).then(function () {
        console.log('Async: Copying to clipboard was successful!');
    }, function (err) {
        console.error('Async: Could not copy text: ', err);
    });
}

function preLoader() {
    const preloader = document.getElementById("preloader");
    preloader.style.display = "flex";
    preloader.style.opacity = 1;
}