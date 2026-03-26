/* ============================================================
   MY KITCHENWARE SHOP – Main JS
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

    /* ---------- Navbar scroll effect ---------- */
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 30);
        });
    }

    /* ---------- Mobile nav toggle ---------- */
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            hamburger.classList.toggle('active');
        });
        // Close on link click
        navLinks.querySelectorAll('a').forEach(a =>
            a.addEventListener('click', () => navLinks.classList.remove('open'))
        );
    }

    /* ---------- Cart State ---------- */
    let cart = JSON.parse(localStorage.getItem('kwCart') || '[]');

    function saveCart() { localStorage.setItem('kwCart', JSON.stringify(cart)); }

    function cartTotal() { return cart.reduce((s, i) => s + i.price * i.qty, 0); }

    function cartCount() { return cart.reduce((s, i) => s + i.qty, 0); }

    function updateBadge() {
        const badge = document.querySelector('.cart-badge');
        if (badge) badge.textContent = cartCount();
    }

    /* ---------- Render cart items ---------- */
    function renderCart() {
        const list = document.getElementById('cartItems');
        const emptyMsg = document.getElementById('cartEmpty');
        const totalEl = document.getElementById('cartTotal');
        if (!list) return;

        list.innerHTML = '';
        if (cart.length === 0) {
            if (emptyMsg) emptyMsg.style.display = 'block';
        } else {
            if (emptyMsg) emptyMsg.style.display = 'none';
            cart.forEach((item, idx) => {
                const el = document.createElement('div');
                el.className = 'cart-item';
                el.innerHTML = `
          <img src="${item.img}" alt="${item.name}" class="cart-item-img">
          <div class="cart-item-info">
            <div class="cart-item-name">${item.name}</div>
            <div class="cart-item-price">KES ${(item.price * item.qty).toLocaleString()}</div>
            <div class="cart-item-qty">
              <button class="qty-btn" onclick="changeQty(${idx}, -1)">-</button>
              <span class="qty-num">${item.qty}</span>
              <button class="qty-btn" onclick="changeQty(${idx}, 1)">+</button>
            </div>
          </div>
          <button class="cart-item-remove" onclick="removeItem(${idx})" title="Remove">🗑</button>
        `;
                list.appendChild(el);
            });
        }
        if (totalEl) totalEl.textContent = 'KES ' + cartTotal().toLocaleString();
        updateBadge();
    }

    window.changeQty = function (idx, delta) {
        cart[idx].qty = Math.max(1, cart[idx].qty + delta);
        saveCart(); renderCart();
    };

    window.removeItem = function (idx) {
        cart.splice(idx, 1);
        saveCart(); renderCart();
        showToast('Item removed from cart', 'info');
    };

    /* ---------- Add to cart ---------- */
    window.addToCart = function (name, price, img) {
        const isLoggedIn = document.body.dataset.loggedIn === 'true';
        if (!isLoggedIn) {
            showToast('Please log in to add items to cart 🔒', 'error');
            setTimeout(() => { window.location.href = '/login/'; }, 1200);
            return;
        }
        const existing = cart.find(i => i.name === name);
        if (existing) {
            existing.qty++;
        } else {
            cart.push({ name, price, img, qty: 1 });
        }
        saveCart(); renderCart();
        openCart();
        showToast(`"${name}" added to cart! 🛒`, 'success');
    };

    /* ---------- Cart drawer ---------- */
    const cartOverlay = document.getElementById('cartOverlay');
    const cartDrawer = document.getElementById('cartDrawer');
    const cartTrigger = document.getElementById('cartTrigger');
    const cartClose = document.getElementById('cartClose');

    window.openCart = function () {
        if (cartOverlay) cartOverlay.classList.add('open');
        if (cartDrawer) cartDrawer.classList.add('open');
    };

    function closeCart() {
        if (cartOverlay) cartOverlay.classList.remove('open');
        if (cartDrawer) cartDrawer.classList.remove('open');
    }

    if (cartTrigger) cartTrigger.addEventListener('click', openCart);
    if (cartClose) cartClose.addEventListener('click', closeCart);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCart);

    /* ---------- Wishlist ---------- */
    let wishlist = JSON.parse(localStorage.getItem('kwWishlist') || '[]');

    window.toggleWishlist = function (btn, name) {
        if (wishlist.includes(name)) {
            wishlist = wishlist.filter(n => n !== name);
            btn.classList.remove('active');
            btn.textContent = '♡';
            showToast('Removed from wishlist', 'info');
        } else {
            wishlist.push(name);
            btn.classList.add('active');
            btn.textContent = '♥';
            showToast(`"${name}" saved to wishlist ♥`, 'success');
        }
        localStorage.setItem('kwWishlist', JSON.stringify(wishlist));
    };

    /* ---------- Product Filter ---------- */
    window.filterProducts = function (cat, btn) {
        // Update active cat card
        document.querySelectorAll('.cat-card').forEach(c => c.classList.remove('active'));
        if (btn) btn.classList.add('active');

        document.querySelectorAll('.product-card').forEach(card => {
            const match = cat === 'all' || card.dataset.cat === cat;
            card.style.display = match ? '' : 'none';
        });
    };

    /* ---------- Product Modal ---------- */
    const modalOverlay = document.getElementById('productModal');

    window.openModal = function (id, name, price, img, desc, cat) {
        if (!modalOverlay) return;
        modalOverlay.querySelector('.modal-name').textContent = name;
        modalOverlay.querySelector('.modal-price').textContent = 'KES ' + parseFloat(price).toLocaleString();
        modalOverlay.querySelector('.modal-img').src = img;
        modalOverlay.querySelector('.modal-img').alt = name;
        modalOverlay.querySelector('.modal-desc').textContent = desc;
        modalOverlay.querySelector('.modal-cat').textContent = cat;
        
        // Update review form action if it exists
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.action = `/submit-review/${id}/`;
        }

        modalOverlay.dataset.name = name;
        modalOverlay.dataset.price = price;
        modalOverlay.dataset.img = img;
        modalOverlay.querySelector('#modalQty').value = 1;
        modalOverlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    };

    window.closeModal = function () {
        if (!modalOverlay) return;
        modalOverlay.classList.remove('open');
        document.body.style.overflow = '';
    };

    if (modalOverlay) {
        modalOverlay.addEventListener('click', e => {
            if (e.target === modalOverlay) closeModal();
        });

        document.getElementById('modalAddToCart')?.addEventListener('click', () => {
            const qty = parseInt(document.getElementById('modalQty').value) || 1;
            const name = modalOverlay.dataset.name;
            const price = parseFloat(modalOverlay.dataset.price);
            const img = modalOverlay.dataset.img;
            const isLoggedIn = document.body.dataset.loggedIn === 'true';
            if (!isLoggedIn) {
                closeModal();
                showToast('Please log in to add items to cart 🔒', 'error');
                setTimeout(() => { window.location.href = '/login/'; }, 1200);
                return;
            }
            const existing = cart.find(i => i.name === name);
            if (existing) { existing.qty += qty; }
            else { cart.push({ name, price, img, qty }); }
            saveCart(); renderCart(); closeModal(); openCart();
            showToast(`"${name}" added to cart! 🛒`, 'success');
        });

        document.getElementById('modalQtyMinus')?.addEventListener('click', () => {
            const el = document.getElementById('modalQty');
            el.value = Math.max(1, parseInt(el.value) - 1);
        });
        document.getElementById('modalQtyPlus')?.addEventListener('click', () => {
            const el = document.getElementById('modalQty');
            el.value = parseInt(el.value) + 1;
        });
    }

    /* ---------- Checkout ---------- */
    // Checkout logic migrated to payment.html (handled via standard <a> link in base.html)

    /* ---------- Toast ---------- */
    window.showToast = function (msg, type = 'info') {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        const icons = { success: '✅', error: '❌', info: 'ℹ️' };
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${msg}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'toastOut 0.4s ease forwards';
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    };

    /* ---------- Newsletter form ---------- */
    document.getElementById('newsletterForm')?.addEventListener('submit', e => {
        e.preventDefault();
        const email = e.target.querySelector('input').value.trim();
        if (!email) return;
        showToast(`Subscribed with ${email}! 🎉`, 'success');
        e.target.reset();
    });

    /* ---------- Scroll fade animation ---------- */
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

    /* ---------- Search ---------- */
    document.getElementById('searchInput')?.addEventListener('input', function () {
        const q = this.value.toLowerCase().trim();
        document.querySelectorAll('.product-card').forEach(card => {
            const name = (card.querySelector('.product-name')?.textContent || '').toLowerCase();
            card.style.display = (!q || name.includes(q)) ? '' : 'none';
        });
    });

    /* ---------- Init ---------- */
    renderCart();
    updateBadge();
});
