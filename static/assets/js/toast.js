function showToast(message, type) {
    var toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = 1055;
        document.body.appendChild(toastContainer);
    }
    var toastEl = document.createElement('div');
    toastEl.className = 'toast show';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.setAttribute('data-bs-autohide', 'false');

    toastEl.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${type.includes('success') ? "Sucesso" : "Erro"}</strong>
            <small class="text-body-secondary">${new Date().toLocaleTimeString()}</small>
            <button class="btn ms-2 p-0" type="button" data-bs-dismiss="toast" aria-label="Close">
                <span class="uil uil-times fs-7"></span>
            </button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    toastContainer.prepend(toastEl);

    var bootstrapToast = new bootstrap.Toast(toastEl);
    bootstrapToast.show();
    

    toastEl.addEventListener('hidden.bs.toast', function () {
        toastEl.remove();
    });
}