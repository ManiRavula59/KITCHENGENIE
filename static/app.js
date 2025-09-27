// AI Smart Kitchen Meal Planner - Client-side JavaScript

// Global variables for application state
let isGenerating = false;
let dishSearchTimeout = null;
let currentQuery = null;

// DOM content loaded event
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupGroceryQuantityInputs();
});

// Initialize application
function initializeApp() {
    initializeFormHandlers();
    initializeDishSearch();
    initializeMealTypeFilter();
    setupLoadingStates();
    setupFormValidation();
    setupKeyboardShortcuts();
    
    // Set default date to today
    const startDateInput = document.getElementById('start_date');
    if (startDateInput && !startDateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        startDateInput.value = today;
    }
}

// Initialize form handlers
function initializeFormHandlers() {
    // Meal plan generation form
    const generateForm = document.getElementById('generateForm');
    if (generateForm) {
        generateForm.addEventListener('submit', handleMealPlanGeneration);
    }

    // Add dish form
    const addDishForm = document.querySelector('form[action="/add_dish"]');
    if (addDishForm) {
        addDishForm.addEventListener('submit', handleAddDish);
    }

    // Update preferences form
    const preferencesForm = document.querySelector('form[action="/update_preferences"]');
    if (preferencesForm) {
        preferencesForm.addEventListener('submit', handleUpdatePreferences);
    }

    // Cancel button
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', handleCancelGeneration);
    }
}

// Handle meal plan generation
function handleMealPlanGeneration(event) {
    event.preventDefault();
    
    if (isGenerating) {
        showNotification('Meal plan generation is already in progress', 'warning');
        return;
    }

    const formData = new FormData(event.target);
    const startDate = formData.get('start_date');

    // Validate inputs
    if (!startDate) {
        showNotification('Please select a start date', 'error');
        return;
    }

    // Validate start date is not in the past
    const selectedDate = new Date(startDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (selectedDate < today) {
        showNotification('Please select a start date from today onwards', 'warning');
        return;
    }

    startMealPlanGeneration();
    
    // Submit form
    event.target.submit();
}

// Handle add dish form
function handleAddDish(event) {
    const formData = new FormData(event.target);
    const dishName = formData.get('dish_name');
    const ingredients = formData.get('ingredients');

    // Client-side validation
    if (!dishName.trim()) {
        event.preventDefault();
        showNotification('Dish name is required', 'error');
        return;
    }

    if (!ingredients.trim()) {
        event.preventDefault();
        showNotification('Please provide at least one ingredient', 'error');
        return;
    }

    // Check for duplicate dish names
    const existingDishes = document.querySelectorAll('.dish-item');
    const normalizedNewName = dishName.toLowerCase().replace(/\s+/g, '_');
    
    for (let dishElement of existingDishes) {
        const existingName = dishElement.dataset.dishName;
        if (existingName === normalizedNewName) {
            event.preventDefault();
            showNotification('A dish with this name already exists', 'error');
            return;
        }
    }

    showNotification('Adding dish...', 'info');
}

// Handle update preferences form
function handleUpdatePreferences(event) {
    const formData = new FormData(event.target);
    const familySize = formData.get('family_size');
    
    if (familySize && (familySize < 1 || familySize > 20)) {
        event.preventDefault();
        showNotification('Family size must be between 1 and 20', 'error');
        return;
    }

    showNotification('Updating preferences...', 'info');
}

// Start meal plan generation UI state
function startMealPlanGeneration() {
    isGenerating = true;
    
    const generateBtn = document.getElementById('generateBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const loadingState = document.getElementById('loadingState');

    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    }

    if (cancelBtn) {
        cancelBtn.style.display = 'inline-block';
    }

    if (loadingState) {
        loadingState.style.display = 'block';
    }

    // Update loading message based on selected algorithm
    const loadingMessage = getLoadingMessage('combined');
    const loadingText = loadingState?.querySelector('p');
    if (loadingText) {
        loadingText.textContent = loadingMessage;
    }

    // Simulate progress updates
    simulateProgress();
}

// Get loading message based on algorithm
function getLoadingMessage(algorithm) {
    const messages = {
        'astar': 'A* algorithm is exploring optimal meal combinations using heuristic search...',
        'aostar': 'AO* algorithm is solving constraint satisfaction using AND-OR tree decomposition...',
        'basic': 'Prolog engine is processing rules and generating meal plan using logical inference...',
        'combined': 'Intelligent planner is combining A*, AO*, and Prolog to generate your weekly plan...'
    };
    return messages[algorithm] || 'Generating meal plan...';
}

// Simulate progress for better UX
function simulateProgress() {
    const progressBar = document.querySelector('#loadingState .progress-bar');
    if (!progressBar) return;

    let progress = 0;
    const interval = setInterval(() => {
        if (!isGenerating) {
            clearInterval(interval);
            return;
        }

        progress += Math.random() * 10;
        if (progress > 95) progress = 95;
        
        progressBar.style.width = `${progress}%`;
    }, 500);
}

// Handle cancel generation
function handleCancelGeneration() {
    if (!isGenerating) return;

    // Send cancel request
    fetch('/cancel_generation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            stopMealPlanGeneration();
            showNotification('Meal plan generation cancelled', 'info');
        }
    })
    .catch(error => {
        console.error('Error cancelling generation:', error);
        showNotification('Error cancelling generation', 'error');
    });
}

// Stop meal plan generation UI state
function stopMealPlanGeneration() {
    isGenerating = false;
    
    const generateBtn = document.getElementById('generateBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const loadingState = document.getElementById('loadingState');

    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-cogs"></i> Generate Meal Plan';
    }

    if (cancelBtn) {
        cancelBtn.style.display = 'none';
    }

    if (loadingState) {
        loadingState.style.display = 'none';
    }
}

// Initialize dish search functionality
function initializeDishSearch() {
    const searchInput = document.getElementById('dishSearch');
    if (!searchInput) return;

    searchInput.addEventListener('input', function() {
        clearTimeout(dishSearchTimeout);
        dishSearchTimeout = setTimeout(() => {
            filterDishes(this.value);
        }, 300);
    });
}

// Initialize meal type filter
function initializeMealTypeFilter() {
    const mealFilter = document.getElementById('mealFilter');
    if (!mealFilter) return;

    mealFilter.addEventListener('change', function() {
        filterDishesByMealType(this.value);
    });
}

// Filter dishes by search term
function filterDishes(searchTerm) {
    const dishItems = document.querySelectorAll('.dish-item');
    const normalizedSearch = searchTerm.toLowerCase().trim();

    let visibleCount = 0;

    dishItems.forEach(item => {
        const dishName = item.dataset.dishName || '';
        const dishText = item.textContent.toLowerCase();
        
        const isMatch = !normalizedSearch || 
                       dishName.includes(normalizedSearch) || 
                       dishText.includes(normalizedSearch);

        if (isMatch) {
            item.style.display = 'block';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    // Show no results message
    updateNoResultsMessage(visibleCount, 'search', searchTerm);
}

// Filter dishes by meal type
function filterDishesByMealType(mealType) {
    const dishItems = document.querySelectorAll('.dish-item');
    const searchTerm = document.getElementById('dishSearch')?.value || '';
    
    let visibleCount = 0;

    dishItems.forEach(item => {
        const itemMealType = item.dataset.mealType || '';
        const dishText = item.textContent.toLowerCase();
        const normalizedSearch = searchTerm.toLowerCase().trim();
        
        const matchesMealType = !mealType || itemMealType === mealType;
        const matchesSearch = !normalizedSearch || dishText.includes(normalizedSearch);
        const isMatch = matchesMealType && matchesSearch;

        if (isMatch) {
            item.style.display = 'block';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    // Show no results message
    updateNoResultsMessage(visibleCount, 'filter', mealType);
}

// Update no results message
function updateNoResultsMessage(visibleCount, filterType, filterValue) {
    let noResultsDiv = document.getElementById('noResultsMessage');
    
    if (visibleCount === 0) {
        if (!noResultsDiv) {
            noResultsDiv = document.createElement('div');
            noResultsDiv.id = 'noResultsMessage';
            noResultsDiv.className = 'alert alert-info text-center mt-3';
            document.getElementById('dishesAccordion').parentNode.appendChild(noResultsDiv);
        }
        
        const message = filterType === 'search' 
            ? `No dishes found matching "${filterValue}"`
            : `No ${filterValue} dishes found`;
            
        noResultsDiv.innerHTML = `
            <i class="fas fa-search"></i> ${message}
            <br><small class="text-muted">Try adjusting your search terms or filters</small>
        `;
        noResultsDiv.style.display = 'block';
    } else if (noResultsDiv) {
        noResultsDiv.style.display = 'none';
    }
}

// Setup loading states for various actions
function setupLoadingStates() {
    // Add loading states to all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !form.id === 'generateForm') {
                submitButton.disabled = true;
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable after 3 seconds as fallback
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 3000);
            }
        });
    });
}

// Setup form validation
function setupFormValidation() {
    // Real-time validation for dish name
    const dishNameInput = document.getElementById('dish_name');
    if (dishNameInput) {
        dishNameInput.addEventListener('input', function() {
            validateDishName(this);
        });
    }

    // Real-time validation for ingredients
    const ingredientsInput = document.getElementById('ingredients');
    if (ingredientsInput) {
        ingredientsInput.addEventListener('input', function() {
            validateIngredients(this);
        });
    }

    // Real-time validation for family size
    const familySizeInput = document.getElementById('family_size');
    if (familySizeInput) {
        familySizeInput.addEventListener('input', function() {
            validateFamilySize(this);
        });
    }
}

// Validate dish name
function validateDishName(input) {
    const value = input.value.trim();
    const feedback = getOrCreateFeedback(input);
    
    if (value.length < 2) {
        setValidationState(input, feedback, false, 'Dish name must be at least 2 characters long');
    } else if (value.length > 50) {
        setValidationState(input, feedback, false, 'Dish name must be less than 50 characters');
    } else if (!/^[a-zA-Z\s]+$/.test(value)) {
        setValidationState(input, feedback, false, 'Dish name can only contain letters and spaces');
    } else {
        setValidationState(input, feedback, true, 'Looks good!');
    }
}

// Validate ingredients
function validateIngredients(input) {
    const value = input.value.trim();
    const feedback = getOrCreateFeedback(input);
    const ingredients = value.split(',').map(ing => ing.trim()).filter(ing => ing);
    
    if (ingredients.length === 0) {
        setValidationState(input, feedback, false, 'At least one ingredient is required');
    } else if (ingredients.length > 20) {
        setValidationState(input, feedback, false, 'Maximum 20 ingredients allowed');
    } else {
        setValidationState(input, feedback, true, `${ingredients.length} ingredient${ingredients.length > 1 ? 's' : ''} added`);
    }
}

// Validate family size
function validateFamilySize(input) {
    const value = parseInt(input.value);
    const feedback = getOrCreateFeedback(input);
    
    if (isNaN(value) || value < 1) {
        setValidationState(input, feedback, false, 'Family size must be at least 1');
    } else if (value > 20) {
        setValidationState(input, feedback, false, 'Family size cannot exceed 20');
    } else {
        setValidationState(input, feedback, true, 'Valid family size');
    }
}

// Get or create validation feedback element
function getOrCreateFeedback(input) {
    let feedback = input.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.appendChild(feedback);
    }
    return feedback;
}

// Set validation state
function setValidationState(input, feedback, isValid, message) {
    input.classList.toggle('is-valid', isValid);
    input.classList.toggle('is-invalid', !isValid);
    
    feedback.className = isValid ? 'valid-feedback' : 'invalid-feedback';
    feedback.textContent = message;
    feedback.style.display = 'block';
}

// Setup keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + Enter to generate meal plan
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const generateBtn = document.getElementById('generateBtn');
            if (generateBtn && !generateBtn.disabled) {
                event.preventDefault();
                generateBtn.click();
            }
        }
        
        // Escape to cancel generation
        if (event.key === 'Escape' && isGenerating) {
            event.preventDefault();
            handleCancelGeneration();
        }
        
        // Ctrl/Cmd + F to focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
            const searchInput = document.getElementById('dishSearch');
            if (searchInput) {
                event.preventDefault();
                searchInput.focus();
            }
        }
    });
}

// Show notification to user
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingAlerts = document.querySelectorAll('.alert.notification');
    existingAlerts.forEach(alert => alert.remove());

    // Create new notification
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${getBootstrapAlertClass(type)} alert-dismissible fade show notification`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${getNotificationIcon(type)} ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    document.body.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }
    }, 5000);
}

// Get Bootstrap alert class
function getBootstrapAlertClass(type) {
    const mapping = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return mapping[type] || 'info';
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        'success': '<i class="fas fa-check-circle"></i>',
        'error': '<i class="fas fa-exclamation-triangle"></i>',
        'warning': '<i class="fas fa-exclamation-circle"></i>',
        'info': '<i class="fas fa-info-circle"></i>'
    };
    return icons[type] || icons['info'];
}

// Utility functions for results page (if present)
if (typeof toggleView === 'undefined') {
    window.toggleView = function(viewType) {
        const tableView = document.getElementById('tableView');
        const cardView = document.getElementById('cardView');
        
        if (tableView && cardView) {
            if (viewType === 'table') {
                tableView.style.display = 'block';
                cardView.style.display = 'none';
            } else {
                tableView.style.display = 'none';
                cardView.style.display = 'block';
            }
        }
    };
}

// Enhanced accordion functionality
document.addEventListener('DOMContentLoaded', function() {
    // Smooth accordion transitions
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon && icon.classList.contains('fas')) {
                setTimeout(() => {
                    if (this.classList.contains('collapsed')) {
                        icon.style.transform = 'rotate(0deg)';
                    } else {
                        icon.style.transform = 'rotate(90deg)';
                    }
                }, 50);
            }
        });
    });
});

// Enhanced ingredient input functionality
function enhanceIngredientInput() {
    const ingredientInput = document.getElementById('ingredients');
    if (!ingredientInput) return;

    // Add suggestion functionality
    let suggestionTimeout;
    ingredientInput.addEventListener('input', function() {
        clearTimeout(suggestionTimeout);
        suggestionTimeout = setTimeout(() => {
            showIngredientSuggestions(this.value);
        }, 500);
    });
}

// Show ingredient suggestions (mock for now)
function showIngredientSuggestions(input) {
    const commonIngredients = [
        'rice', 'dal', 'onion', 'tomato', 'garlic', 'ginger', 'turmeric', 'salt',
        'oil', 'curry_leaves', 'mustard_seeds', 'cumin_seeds', 'coriander',
        'green_chili', 'coconut', 'yogurt', 'lemon', 'tamarind'
    ];

    const lastWord = input.split(',').pop().trim().toLowerCase();
    if (lastWord.length < 2) return;

    const suggestions = commonIngredients.filter(ingredient => 
        ingredient.includes(lastWord) && !input.includes(ingredient)
    );

    // This could be enhanced to show actual suggestions UI
    if (suggestions.length > 0) {
        console.log('Suggestions:', suggestions.slice(0, 5));
    }
}

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function() {
    enhanceIngredientInput();
});

// Error handling for network requests
window.addEventListener('online', function() {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Connection lost. Some features may not work.', 'warning');
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            if (loadTime > 3000) {
                console.warn('Slow page load detected:', loadTime + 'ms');
            }
        }, 1000);
    });
}

// Accessibility enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add skip link
    const skipLink = document.createElement('a');
    skipLink.className = 'visually-hidden-focusable position-absolute top-0 start-0 bg-primary text-white p-2 text-decoration-none';
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.style.zIndex = '10000';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Add main content id if not present
    const container = document.querySelector('.container');
    if (container && !document.getElementById('main-content')) {
        container.id = 'main-content';
    }

    // Enhanced focus management
    document.querySelectorAll('button, a, input, select, textarea').forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid var(--bs-primary)';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
});

// Export functions for global access
window.MealPlannerApp = {
    showNotification,
    filterDishes,
    filterDishesByMealType,
    startMealPlanGeneration,
    stopMealPlanGeneration,
    handleCancelGeneration
};

// Grocery quantity/unit input logic
function setupGroceryQuantityInputs() {
    const saveBtn = document.getElementById('saveGroceryQtyBtn');
    const editBtn = document.getElementById('editGroceryQtyBtn');
    const qtyInputs = document.querySelectorAll('.grocery-qty-input');
    let savedQuantities = {};

    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            qtyInputs.forEach(input => {
                const ingredient = input.dataset.ingredient;
                const value = input.value.trim();
                savedQuantities[ingredient] = value;
                input.setAttribute('readonly', 'readonly');
                if (value) {
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                }
            });
            saveBtn.style.display = 'none';
            editBtn.style.display = 'inline-block';
        });
    }

    if (editBtn) {
        editBtn.addEventListener('click', function() {
            qtyInputs.forEach(input => {
                input.removeAttribute('readonly');
                input.classList.remove('is-valid');
            });
            saveBtn.style.display = 'inline-block';
            editBtn.style.display = 'none';
        });
    }
}

// Delete dish function (index page)
function deleteDish(dishName) {
    if (!confirm(`Delete dish "${dishName.replace('_',' ')}"?`)) return;
    const formData = new FormData();
    formData.append('dish_name', dishName);
    fetch('/delete_dish', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showNotification('Dish deleted', 'success');
                // Remove from UI
                document.querySelectorAll(`.dish-item[data-dish-name="${dishName}"]`).forEach(el => el.remove());
            } else {
                showNotification(data.error || 'Failed to delete dish', 'error');
            }
        })
        .catch(err => showNotification('Failed to delete dish: ' + err.message, 'error'));
}

// Export meal plan to PDF
function exportPlan() {
    // Gather grocery quantities
    const qtyInputs = document.querySelectorAll('.grocery-qty-input');
    let quantities = {};
    qtyInputs.forEach(input => {
        const ingredient = input.dataset.ingredient;
        const value = input.value.trim();
        if (ingredient) {
            quantities[ingredient] = value;
        }
    });

    fetch('/export_pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({quantities})
    })
    .then(response => {
        if (!response.ok) throw new Error('PDF export failed');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'meal_plan.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(err => {
        showNotification('PDF export failed: ' + err.message, 'error');
    });
}
