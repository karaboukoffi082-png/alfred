<!-- ============================================================
   DK-PRESS — Script principal (Version corrigée & propre)
   ============================================================ -->
<script>

// ================== AJOUT AU PANIER ==================
async function addToCart(productId) {
    try {
        const response = await fetch(`/panier/ajouter/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });

        const data = await response.json();

        if (data.success) {
            console.log("Produit ajouté :", data);

            // Option UX simple
            alert("Produit ajouté au panier ✅");

            // (Option pro) mettre à jour compteur panier si tu en as un
            const cartCount = document.getElementById("cart-count");
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }

        } else {
            alert(data.error || "Erreur ❌");
        }

    } catch (error) {
        console.error("Erreur serveur :", error);
        alert("Erreur serveur ❌");
    }
}


// ================== CSRF TOKEN ==================
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}


// ================== MENU UTILISATEUR ==================
function initUserMenu() {
    const toggle = document.getElementById('userMenuToggle');
    const menu = document.getElementById('userMenu');

    if (!toggle || !menu) return;

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!menu.contains(e.target) && !toggle.contains(e.target)) {
            menu.classList.add('hidden');
        }
    });
}


// ================== RECHERCHE MOBILE ==================
function initMobileSearch() {
    const toggle = document.getElementById('mobileSearchToggle');
    const form = document.getElementById('mobileSearchForm');

    if (!toggle || !form) return;

    toggle.addEventListener('click', () => {
        form.classList.toggle('hidden');

        if (!form.classList.contains('hidden')) {
            const input = form.querySelector('input');
            if (input) input.focus();
        }
    });
}


// ================== CHAT WIDGET ==================
function initChatWidget() {
    const openBtn = document.getElementById('chatOpenBtn');
    const closeBtn = document.getElementById('chatCloseBtn');
    const window_ = document.getElementById('chatWindow');
    const form = document.getElementById('chatWidgetForm');
    const input = document.getElementById('chatWidgetInput');
    const messagesDiv = document.getElementById('chatMessages');

    if (!openBtn || !window_) return;

    // Ouvrir
    openBtn.addEventListener('click', () => {
        window_.classList.remove('hidden');
        openBtn.classList.add('hidden');
        if (input) input.focus();
    });

    // Fermer
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            window_.classList.add('hidden');
            openBtn.classList.remove('hidden');
        });
    }

    // Envoyer message
    if (form && input && messagesDiv) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const content = input.value.trim();
            if (!content) return;

            const msgHtml = `
                <div class="flex justify-end">
                    <div class="bg-gray-900 text-white rounded-xl rounded-br-sm px-3 py-2 max-w-[75%] shadow-sm">
                        <p class="text-sm">${content}</p>
                        <span class="text-[10px] text-gray-400 mt-1 block text-right">Maintenant</span>
                    </div>
                </div>
            `;

            messagesDiv.insertAdjacentHTML('beforeend', msgHtml);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            input.value = '';
        });
    }
}


// ================== INITIALISATION ==================
document.addEventListener('DOMContentLoaded', () => {
    initUserMenu();
    initMobileSearch();
    initChatWidget();
});

document.addEventListener('DOMContentLoaded', function() {
    fetch("{% url 'shop:cart_count' %}")
        .then(response => response.json())
        .then(data => {
            const cartBadge = document.getElementById('cartBadge');
            if (cartBadge) {
                cartBadge.textContent = data.cart_count;
                if (data.cart_count > 0) {
                    cartBadge.classList.remove('hidden');
                }
            }
        });
});


 (function() {
        // Attendre que Swiper soit disponible
        function initSwiper() {
            if (typeof Swiper === 'undefined') {
                setTimeout(initSwiper, 100);
                return;
            }
            new Swiper('.adSwiper', {
                direction: 'horizontal',
                slidesPerView: 1,
                spaceBetween: 16,
                loop: true,
                autoplay: {
                    delay: 3500,
                    disableOnInteraction: false,
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                breakpoints: {
                    640: {
                        slidesPerView: 2,
                        spaceBetween: 20,
                    },
                    1024: {
                        slidesPerView: 3,
                        spaceBetween: 24,
                    },
                }
            });
        }
        initSwiper();
    })();

</script>