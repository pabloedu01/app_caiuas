function showToast(message, type) {
    var toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = 1055;
        document.body.appendChild(toastContainer);
    }
    
    var toastEl = document.createElement('div');
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.setAttribute('data-bs-autohide', 'true');
    toastEl.setAttribute('data-bs-delay', '3000');

    // Definir cores e ícones baseados no tipo
    let toastClass, headerClass, iconClass, title;
    
    switch (type) {
        case 'success':
            toastClass = 'toast show';
            headerClass = 'toast-header';
            iconClass = 'fas fa-check-circle me-2 text-success';
            title = '<span class="text-success">Sucesso</span>';
            break;
        case 'error':
            toastClass = 'toast show';
            headerClass = 'toast-header';
            iconClass = 'fas fa-exclamation-circle me-2 text-danger';
            title = '<span class="text-danger">Erro</span>';
            break;
        case 'warning':
            toastClass = 'toast show';
            headerClass = 'toast-header';
            iconClass = 'fas fa-exclamation-triangle me-2 text-warning';
            title = '<span class="text-warning">Aviso</span>';
            break;
        case 'info':
            toastClass = 'toast show';
            headerClass = 'toast-header';
            iconClass = 'fas fa-info-circle me-2 text-info';
            title = '<span class="text-info">Informação</span>';
            break;
        default:
            toastClass = 'toast show';
            headerClass = 'toast-header';
            iconClass = 'fas fa-bell me-2 text-secondary';
            title = '<span class="text-secondary">Notificação</span>';
    }

    toastEl.className = toastClass;

    toastEl.innerHTML = `
        <div class="${headerClass}">
            <i class="${iconClass}"></i>
            <strong class="me-auto">${title}</strong>
            <small class="opacity-75">${new Date().toLocaleTimeString()}</small>
            <button class="btn-close ms-2" type="button" data-bs-dismiss="toast" aria-label="Close"></button>
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