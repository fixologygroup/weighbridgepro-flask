document.addEventListener('DOMContentLoaded', function() {
    const weightUnitSelect = document.getElementById('weight_unit');
    const unitDisplayElements = document.querySelectorAll('.unit-display');
    const alertInfoExample = document.querySelector('.alert-info');
    
    // Update unit displays when weight unit changes
    weightUnitSelect.addEventListener('change', function() {
        const selectedUnit = this.value;
        
        // Update unit labels in form fields
        unitDisplayElements.forEach(el => {
            el.textContent = `(${selectedUnit})`;
        });
        
        // Update example text based on selected unit
        if (selectedUnit === 'ton') {
            alertInfoExample.innerHTML = '<i class="fas fa-info-circle me-2"></i> Example: If FOC Weight is 0.5 tons and FOC Threshold is 10 tons, then 0.5 tons will be free for orders of 10 tons or more.';
        } else {
            alertInfoExample.innerHTML = '<i class="fas fa-info-circle me-2"></i> Example: If FOC Weight is 500kg and FOC Threshold is 10000kg, then 500kg will be free for orders of 10 tons or more.';
        }
    });
});