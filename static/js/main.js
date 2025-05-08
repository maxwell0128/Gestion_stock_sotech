document.addEventListener('DOMContentLoaded', function() {
    // Gestion du menu déroulant
    const dropdowns = document.querySelectorAll('.sidebar-dropdown > a');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Ferme tous les autres menus déroulants
            dropdowns.forEach(other => {
                if (other !== dropdown) {
                    other.parentElement.classList.remove('active');
                }
            });
            
            // Bascule l'état du menu cliqué
            this.parentElement.classList.toggle('active');
        });
    });

    // Activer le lien actif dans la sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
    
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            // Si le lien est dans un sous-menu, active aussi le menu parent
            const parentDropdown = link.closest('.sidebar-dropdown');
            if (parentDropdown) {
                parentDropdown.classList.add('active');
            }
        }
    });

    // Gestion des messages flash
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000);
    });

    // Validation des formulaires
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Gestion du menu mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
}); 