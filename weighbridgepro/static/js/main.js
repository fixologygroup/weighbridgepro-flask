document.addEventListener('DOMContentLoaded', function() {
    // Populate item dropdown based on selected category
    const categorySelect = document.getElementById('category');
    const itemSelect = document.getElementById('item');
    
    if (categorySelect && itemSelect) {
        categorySelect.addEventListener('change', function() {
            const categoryId = this.value;
            
            if (categoryId) {
                // Clear current options
                itemSelect.innerHTML = '<option value="">Loading...</option>';
                
                // Fetch items for the selected category
                fetch(`/get-items/${categoryId}`)
                    .then(response => response.json())
                    .then(data => {
                        itemSelect.innerHTML = '';
                        
                        // Add the items to the dropdown
                        data.items.forEach(item => {
                            const option = document.createElement('option');
                            option.value = item.id;
                            option.textContent = item.name;
                            itemSelect.appendChild(option);
                        });
                        
                        // Enable the item select
                        itemSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching items:', error);
                        itemSelect.innerHTML = '<option value="">Error loading items</option>';
                    });
            } else {
                // If no category selected, disable item select
                itemSelect.innerHTML = '<option value="">Select a category first</option>';
                itemSelect.disabled = true;
            }
        });
    }
    
    // Simulate weight reading for tare weight
    const simulateWeightBtn = document.getElementById('simulate-weight-btn');
    const tareWeightInput = document.getElementById('tare_weight');
    
    if (simulateWeightBtn && tareWeightInput) {
        simulateWeightBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            simulateWeightBtn.disabled = true;
            simulateWeightBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Reading...';
            
            // Simulate delay and fetch weight
            setTimeout(() => {
                fetch('/simulate-weight')
                    .then(response => response.json())
                    .then(data => {
                        tareWeightInput.value = data.weight;
                        simulateWeightBtn.innerHTML = 'Get Weight';
                        simulateWeightBtn.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error simulating weight:', error);
                        simulateWeightBtn.innerHTML = 'Try Again';
                        simulateWeightBtn.disabled = false;
                    });
            }, 1000);
        });
    }
    
    // Simulate weight reading for loaded weight
    const simulateLoadedWeightBtn = document.getElementById('simulate-loaded-weight-btn');
    const loadedWeightInput = document.getElementById('loaded_weight');
    
    if (simulateLoadedWeightBtn && loadedWeightInput) {
        simulateLoadedWeightBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            simulateLoadedWeightBtn.disabled = true;
            simulateLoadedWeightBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Reading...';
            
            // Simulate delay and fetch weight
            setTimeout(() => {
                fetch('/simulate-weight')
                    .then(response => response.json())
                    .then(data => {
                        loadedWeightInput.value = data.weight;
                        simulateLoadedWeightBtn.innerHTML = 'Get Weight';
                        simulateLoadedWeightBtn.disabled = false;
                        
                        // Trigger calculation preview if token field exists
                        const tokenField = document.getElementById('token_number');
                        if (tokenField && tokenField.value) {
                            updateCalculations(tokenField.value, data.weight);
                        }
                    })
                    .catch(error => {
                        console.error('Error simulating weight:', error);
                        simulateLoadedWeightBtn.innerHTML = 'Try Again';
                        simulateLoadedWeightBtn.disabled = false;
                    });
            }, 1000);
        });
    }
    
    // Preview calculations based on loaded weight input changes
    const loadedWeightPreview = document.getElementById('loaded_weight');
    const tokenField = document.getElementById('token_number');
    
    if (loadedWeightPreview && tokenField) {
        loadedWeightPreview.addEventListener('input', function() {
            const tokenNumber = tokenField.value;
            const loadedWeight = parseFloat(this.value) || 0;
            
            if (tokenNumber && loadedWeight > 0) {
                updateCalculations(tokenNumber, loadedWeight);
            }
        });
    }
    
    // Function to update calculation previews
    function updateCalculations(tokenNumber, loadedWeight) {
        fetch(`/preview-calculations?token_number=${tokenNumber}&loaded_weight=${loadedWeight}`)
            .then(response => response.json())
            .then(data => {
                // Update preview fields if they exist
                if (document.getElementById('net_weight_preview')) {
                    document.getElementById('net_weight_preview').textContent = data.net_weight.toFixed(2) + ' kg';
                }
                if (document.getElementById('foc_weight_preview')) {
                    document.getElementById('foc_weight_preview').textContent = data.foc_weight.toFixed(2) + ' kg';
                }
                if (document.getElementById('difference_weight_preview')) {
                    const diff = data.difference_weight.toFixed(2);
                    const element = document.getElementById('difference_weight_preview');
                    element.textContent = diff + ' kg';
                    
                    // Add color based on positive/negative value
                    if (parseFloat(diff) > 0) {
                        element.classList.remove('text-danger');
                        element.classList.add('text-success');
                    } else if (parseFloat(diff) < 0) {
                        element.classList.remove('text-success');
                        element.classList.add('text-danger');
                    } else {
                        element.classList.remove('text-success', 'text-danger');
                    }
                }
            })
            .catch(error => {
                console.error('Error updating calculations:', error);
            });
    }
    
    // Initialize datatable if it exists
    if ($.fn.DataTable && document.getElementById('report-table')) {
        $('#report-table').DataTable({
            responsive: true,
            order: [[8, 'desc']], // Sort by in-time (descending) by default
            dom: 'Bfrtip',
            buttons: [
                'copy', 'excel', 'pdf'
            ]
        });
    }
    
    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            card.classList.add('animate-fade-in');
            card.style.animationDelay = (index * 0.1) + 's';
        });
    }
    
    // Tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});
