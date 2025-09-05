/*
Fichier JavaScript pour le dashboard EBUSINESS AI
Fonctions utilitaires et interactions
*/

// Fonction pour rafraîchir les données automatiquement
function setupAutoRefresh(intervalMinutes = 5) {
    setInterval(() => {
        console.log('Rafraîchissement automatique des données...');
        
        // Émettre un événement personnalisé
        const event = new CustomEvent('dashboard:refresh', {
            detail: { timestamp: new Date().toISOString() }
        });
        
        document.dispatchEvent(event);
        
        // Rafraîchir la page
        window.location.reload();
    }, intervalMinutes * 60 * 1000);
}

// Fonction pour afficher une notification
function showNotification(message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `dashboard-notification dashboard-notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Ajouter un écouteur pour le bouton de fermeture
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Fonction pour confirmer une action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Fonction pour formater les nombres
function formatNumber(number) {
    return new Intl.NumberFormat('fr-FR').format(number);
}

// Fonction pour formater les dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Fonction pour copier dans le presse-papiers
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copié dans le presse-papiers', 'success');
    }).catch(err => {
        console.error('Erreur lors de la copie:', err);
        showNotification('Erreur lors de la copie', 'error');
    });
}

// Fonction pour télécharger un fichier
function downloadFile(content, filename, contentType = 'text/plain') {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Fonction pour créer un graphique simple
function createSimpleChart(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Configuration par défaut
    const defaultOptions = {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Statistiques'
                }
            }
        }
    };
    
    // Fusionner avec les options fournies
    const chartOptions = { ...defaultOptions, ...options };
    
    // Créer le graphique
    new Chart(ctx, chartOptions);
}

// Fonction pour initialiser les tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', (e) => {
            const tooltipText = e.target.getAttribute('data-tooltip');
            
            // Créer l'élément tooltip
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'dashboard-tooltip';
            tooltipElement.textContent = tooltipText;
            
            // Positionner le tooltip
            tooltipElement.style.position = 'absolute';
            tooltipElement.style.zIndex = '1000';
            tooltipElement.style.padding = '8px 12px';
            tooltipElement.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            tooltipElement.style.color = 'white';
            tooltipElement.style.borderRadius = '4px';
            tooltipElement.style.fontSize = '14px';
            tooltipElement.style.maxWidth = '300px';
            tooltipElement.style.pointerEvents = 'none';
            
            // Calculer la position
            const rect = e.target.getBoundingClientRect();
            tooltipElement.style.left = `${rect.left + window.scrollX}px`;
            tooltipElement.style.top = `${rect.top + window.scrollY - tooltipElement.offsetHeight - 10}px`;
            
            // Ajouter au DOM
            document.body.appendChild(tooltipElement);
            
            // Stocker la référence
            e.target.tooltipElement = tooltipElement;
        });
        
        tooltip.addEventListener('mouseleave', (e) => {
            if (e.target.tooltipElement) {
                e.target.tooltipElement.remove();
                e.target.tooltipElement = null;
            }
        });
    });
}

// Fonction pour initialiser les modales
function initModals() {
    const modals = document.querySelectorAll('.dashboard-modal');
    const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.getAttribute('data-modal-trigger');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                modal.classList.add('modal-active');
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    modals.forEach(modal => {
        const closeButtons = modal.querySelectorAll('.modal-close');
        
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                modal.classList.remove('modal-active');
                document.body.style.overflow = '';
            });
        });
        
        // Fermer en cliquant en dehors de la modale
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('modal-active');
                document.body.style.overflow = '';
            }
        });
    });
}

// Fonction pour initialiser les onglets
function initTabs() {
    const tabContainers = document.querySelectorAll('.dashboard-tabs');
    
    tabContainers.forEach(container => {
        const tabTriggers = container.querySelectorAll('.tab-trigger');
        const tabContents = container.querySelectorAll('.tab-content');
        
        tabTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                
                const tabId = trigger.getAttribute('data-tab');
                
                // Désactiver tous les onglets
                tabTriggers.forEach(t => t.classList.remove('tab-active'));
                tabContents.forEach(c => c.classList.remove('content-active'));
                
                // Activer l'onglet sélectionné
                trigger.classList.add('tab-active');
                const tabContent = document.getElementById(tabId);
                if (tabContent) {
                    tabContent.classList.add('content-active');
                }
            });
        });
    });
}

// Fonction pour initialiser les accordéons
function initAccordions() {
    const accordions = document.querySelectorAll('.dashboard-accordion');
    
    accordions.forEach(accordion => {
        const triggers = accordion.querySelectorAll('.accordion-trigger');
        
        triggers.forEach(trigger => {
            trigger.addEventListener('click', () => {
                const content = trigger.nextElementSibling;
                const isActive = trigger.classList.contains('accordion-active');
                
                // Fermer tous les accordéons
                triggers.forEach(t => {
                    t.classList.remove('accordion-active');
                    if (t.nextElementSibling) {
                        t.nextElementSibling.style.maxHeight = '0';
                    }
                });
                
                // Ouvrir l'accordéon cliqué s'il n'était pas déjà actif
                if (!isActive) {
                    trigger.classList.add('accordion-active');
                    if (content) {
                        content.style.maxHeight = content.scrollHeight + 'px';
                    }
                }
            });
        });
    });
}

// Fonction pour initialiser les menus déroulants
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dashboard-dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const isActive = dropdown.classList.contains('dropdown-active');
            
            // Fermer tous les menus déroulants
            dropdowns.forEach(d => d.classList.remove('dropdown-active'));
            
            // Ouvrir le menu déroulant cliqué s'il n'était pas déjà actif
            if (!isActive) {
                dropdown.classList.add('dropdown-active');
            }
        });
        
        // Fermer le menu en cliquant en dehors
        document.addEventListener('click', () => {
            dropdown.classList.remove('dropdown-active');
        });
    });
}

// Fonction pour initialiser les filtres
function initFilters() {
    const filterForms = document.querySelectorAll('.dashboard-filters');
    
    filterForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                // Soumettre le formulaire automatiquement
                form.dispatchEvent(new Event('submit', { bubbles: true }));
            });
        });
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Récupérer les données du formulaire
            const formData = new FormData(form);
            const params = new URLSearchParams();
            
            for (const [key, value] of formData.entries()) {
                params.append(key, value);
            }
            
            // Mettre à jour l'URL sans recharger la page
            const newUrl = `${window.location.pathname}?${params.toString()}`;
            window.history.pushState({}, '', newUrl);
            
            // Émettre un événement de filtre
            const event = new CustomEvent('dashboard:filter', {
                detail: { params: params.toString() }
            });
            
            document.dispatchEvent(event);
        });
    });
}

// Fonction pour initialiser la recherche
function initSearch() {
    const searchInputs = document.querySelectorAll('.dashboard-search');
    
    searchInputs.forEach(input => {
        let debounceTimer;
        
        input.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {
                const searchTerm = e.target.value;
                
                // Émettre un événement de recherche
                const event = new CustomEvent('dashboard:search', {
                    detail: { term: searchTerm }
                });
                
                document.dispatchEvent(event);
            }, 300); // Délai de 300ms
        });
    });
}

// Fonction pour initialiser le tri des tableaux
function initTableSort() {
    const tables = document.querySelectorAll('.dashboard-table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.getAttribute('data-sort');
                const currentSort = header.getAttribute('data-sort-order') || 'asc';
                const newSort = currentSort === 'asc' ? 'desc' : 'asc';
                
                // Mettre à jour l'attribut de tri
                header.setAttribute('data-sort-order', newSort);
                
                // Émettre un événement de tri
                const event = new CustomEvent('dashboard:sort', {
                    detail: { column: column, order: newSort }
                });
                
                document.dispatchEvent(event);
            });
        });
    });
}

// Fonction pour initialiser la pagination
function initPagination() {
    const paginationContainers = document.querySelectorAll('.dashboard-pagination');
    
    paginationContainers.forEach(container => {
        const pageButtons = container.querySelectorAll('.page-button');
        
        pageButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const page = button.getAttribute('data-page');
                
                // Émettre un événement de pagination
                const event = new CustomEvent('dashboard:paginate', {
                    detail: { page: parseInt(page) }
                });
                
                document.dispatchEvent(event);
            });
        });
    });
}

// Fonction pour initialiser les graphiques interactifs
function initCharts() {
    const chartContainers = document.querySelectorAll('.dashboard-chart');
    
    chartContainers.forEach(container => {
        const chartType = container.getAttribute('data-chart-type');
        const chartData = JSON.parse(container.getAttribute('data-chart-data') || '{}');
        
        // Créer le graphique en fonction du type
        switch (chartType) {
            case 'bar':
                createBarChart(container, chartData);
                break;
            case 'line':
                createLineChart(container, chartData);
                break;
            case 'pie':
                createPieChart(container, chartData);
                break;
            case 'doughnut':
                createDoughnutChart(container, chartData);
                break;
            default:
                console.warn(`Type de graphique non pris en charge: ${chartType}`);
        }
    });
}

// Fonction pour créer un graphique à barres
function createBarChart(container, data) {
    // Cette fonction dépend de la bibliothèque de graphiques utilisée
    // Par exemple, Chart.js, D3.js, etc.
    console.log('Création d\'un graphique à barres', data);
}

// Fonction pour créer un graphique linéaire
function createLineChart(container, data) {
    console.log('Création d\'un graphique linéaire', data);
}

// Fonction pour créer un graphique circulaire
function createPieChart(container, data) {
    console.log('Création d\'un graphique circulaire', data);
}

// Fonction pour créer un graphique en anneau
function createDoughnutChart(container, data) {
    console.log('Création d\'un graphique en anneau', data);
}

// Fonction d'initialisation principale
function initDashboard() {
    // Initialiser tous les composants
    setupAutoRefresh();
    initTooltips();
    initModals();
    initTabs();
    initAccordions();
    initDropdowns();
    initFilters();
    initSearch();
    initTableSort();
    initPagination();
    initCharts();
    
    // Écouter les événements personnalisés
    document.addEventListener('dashboard:refresh', (e) => {
        console.log('Rafraîchissement des données', e.detail);
        showNotification('Données rafraîchies', 'success');
    });
    
    document.addEventListener('dashboard:filter', (e) => {
        console.log('Filtre appliqué', e.detail);
    });
    
    document.addEventListener('dashboard:search', (e) => {
        console.log('Recherche effectuée', e.detail);
    });
    
    document.addEventListener('dashboard:sort', (e) => {
        console.log('Tri appliqué', e.detail);
    });
    
    document.addEventListener('dashboard:paginate', (e) => {
        console.log('Pagination changée', e.detail);
    });
    
    console.log('Dashboard initialisé');
}

// Initialiser le dashboard lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', initDashboard);
