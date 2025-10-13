// SmartRide Custom JavaScript

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize Application
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize auto-hide alerts
    initializeAutoHideAlerts();
    
    // Initialize loading states
    initializeLoadingStates();
    
    // Initialize data tables if present
    initializeDataTables();
    
    console.log('SmartRide application initialized successfully');
}

// Initialize Bootstrap Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form Validations
function initializeFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Auto-hide alerts after 5 seconds
function initializeAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert[role="alert"]');
    
    alerts.forEach(function(alert) {
        if (!alert.classList.contains('alert-important')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

// Loading States for Forms
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                showLoading(submitButton);
            }
        });
    });
}

// Show loading state on button
function showLoading(button) {
    button.disabled = true;
    button.classList.add('loading');
    
    // Re-enable button after 10 seconds to prevent permanent disable
    setTimeout(function() {
        hideLoading(button);
    }, 10000);
}

// Hide loading state on button
function hideLoading(button) {
    button.disabled = false;
    button.classList.remove('loading');
}

// Initialize DataTables if present
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    if (tables.length > 0 && typeof DataTable !== 'undefined') {
        tables.forEach(function(table) {
            new DataTable(table, {
                pageLength: 25,
                responsive: true,
                language: {
                    search: "Search records:",
                    lengthMenu: "Show _MENU_ records per page",
                    info: "Showing _START_ to _END_ of _TOTAL_ records",
                    paginate: {
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Previous"
                    }
                }
            });
        });
    }
}

// Utility Functions

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    return new Date(dateString).toLocaleDateString('en-US', finalOptions);
}

// Show confirmation dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Show success message
function showSuccess(message) {
    showAlert(message, 'success');
}

// Show error message
function showError(message) {
    showAlert(message, 'danger');
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || document.body;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.insertBefore(alertElement, alertContainer.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertElement);
        bsAlert.close();
    }, 5000);
}

// AJAX Helper Functions
function makeRequest(url, method = 'GET', data = null, headers = {}) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(data);
    }
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            showError('An error occurred while processing your request.');
            throw error;
        });
}

// Vehicle Management Functions
const VehicleManager = {
    // Update vehicle status
    updateStatus: function(vehicleId, status) {
        return makeRequest(`/admin/vehicles/${vehicleId}/status`, 'POST', { status: status });
    },
    
    // Send vehicle to maintenance
    sendToMaintenance: function(vehicleId, reason = '') {
        return makeRequest(`/admin/vehicles/${vehicleId}/maintenance`, 'POST', { reason: reason });
    },
    
    // Delete vehicle
    delete: function(vehicleId) {
        return makeRequest(`/admin/vehicles/${vehicleId}`, 'DELETE');
    }
};

// Rental Management Functions
const RentalManager = {
    // Process return
    processReturn: function(rentalId, returnData = {}) {
        return makeRequest(`/admin/rentals/${rentalId}/return`, 'POST', returnData);
    },
    
    // Calculate fine
    calculateFine: function(rentalId) {
        return makeRequest(`/admin/rentals/${rentalId}/calculate-fine`, 'GET');
    },
    
    // Send reminder
    sendReminder: function(rentalId) {
        return makeRequest(`/admin/rentals/${rentalId}/reminder`, 'POST');
    }
};

// Customer Functions
const CustomerManager = {
    // Get customer details
    getDetails: function(customerId) {
        return makeRequest(`/admin/customers/${customerId}`, 'GET');
    },
    
    // Update customer
    update: function(customerId, data) {
        return makeRequest(`/admin/customers/${customerId}`, 'PUT', data);
    }
};

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(function() {
                performSearch(input.value, input.dataset.target);
            }, 300);
        });
    });
}

function performSearch(query, target) {
    const targetElement = document.querySelector(target);
    if (!targetElement) return;
    
    const rows = targetElement.querySelectorAll('tbody tr');
    
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        const match = text.includes(query.toLowerCase());
        
        row.style.display = match ? '' : 'none';
    });
}

// Export functions
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        
        cols.forEach(function(col) {
            let cellData = col.textContent.trim();
            cellData = cellData.replace(/"/g, '""'); // Escape quotes
            rowData.push(`"${cellData}"`);
        });
        
        csv.push(rowData.join(','));
    });
    
    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    window.URL.revokeObjectURL(url);
}

// Print functionality
function printPage() {
    window.print();
}

function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Print</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    @media print { 
                        .no-print { display: none !important; }
                        body { margin: 0; padding: 20px; }
                    }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
    printWindow.close();
}

// Local Storage helpers
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Failed to read from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Failed to remove from localStorage:', e);
        }
    }
};

// Theme management
const ThemeManager = {
    init: function() {
        const savedTheme = Storage.get('theme', 'light');
        this.setTheme(savedTheme);
    },
    
    setTheme: function(theme) {
        document.body.setAttribute('data-theme', theme);
        Storage.set('theme', theme);
    },
    
    toggleTheme: function() {
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
};

// Initialize theme on load
ThemeManager.init();

// Dashboard Functions
const Dashboard = {
    refreshStats: function() {
        makeRequest('/api/dashboard/stats')
            .then(data => {
                this.updateStats(data);
            })
            .catch(error => {
                console.error('Failed to refresh stats:', error);
            });
    },
    
    updateStats: function(stats) {
        Object.keys(stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = stats[key];
            }
        });
    }
};

// Auto-refresh dashboard every 5 minutes
if (document.querySelector('.dashboard-stats')) {
    setInterval(() => {
        Dashboard.refreshStats();
    }, 300000); // 5 minutes
}

// Initialize search on load
initializeSearch();