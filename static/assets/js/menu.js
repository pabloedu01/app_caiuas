(function() {
    const currentUrl = window.location.pathname;
    const urlSegments = currentUrl.split('/').filter(segment => segment !== '');
    const currentPage = urlSegments[0] || 'dashboard';
    
    // Mapeamento de páginas para elementos do menu
    const menuMap = {
        'dashboard': 'menu_dashboard',
        'agendamento': 'menu_agendamento',
        'dashboard-ecommerce': 'menu_dashboard_ecommerce',
        'dashboard-analytics': 'menu_dashboard_analytics',
        'dashboard-projects': 'menu_dashboard_projects',
        'chatbot': 'menu_chatbot',
        'relatorios': 'menu_relatorios'
    };
    
    // Ativa o item do menu correspondente
    const menuElement = document.getElementById(menuMap[currentPage]);
    if (menuElement) {
        menuElement.classList.add('active');
    }
    
    // console.log('Página atual:', currentPage);
})();