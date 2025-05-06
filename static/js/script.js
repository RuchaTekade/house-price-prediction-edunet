document.getElementById('predictionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const priceDisplay = document.getElementById('priceDisplay');
    const resultText = document.getElementById('resultText');
    
    // Show loading state
    priceDisplay.innerHTML = '<div class="loader"></div>';
    resultText.innerHTML = 'Calculating...';
    
    // Convert form values to numbers before sending
const formData = {
    size: parseFloat(document.getElementById('size').value),
    bedrooms: parseInt(document.getElementById('bedrooms').value),
    bathrooms: parseInt(document.getElementById('bathrooms').value),
    parking: parseInt(document.getElementById('parking').value),
    location: document.getElementById('location').value,
    furnish_status: document.getElementById('furnish_status').value,
    guest_room: document.getElementById('guest_room').value
};

if (isNaN(formData.size) || isNaN(formData.bedrooms) || 
        isNaN(formData.bathrooms) || isNaN(formData.parking) ||
        !formData.location || !formData.furnish_status || !formData.guest_room) {
        priceDisplay.innerHTML = '!';
        resultText.innerHTML = '<span style="color:red">Please fill all fields correctly!</span>';
        return; // Stop if validation fails
    }

    
    // Send prediction request
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            // Handle validation errors
            if (data.details) {
                let errorMsg = "Please fix: ";
                for (const [field, msg] of Object.entries(data.details)) {
                    errorMsg += `${field} (${msg}). `;
                }
                resultText.innerHTML = `<span style="color:red">${errorMsg}</span>`;
            } else {
                resultText.innerHTML = `<span style="color:red">${data.error}</span>`;
            }
            priceDisplay.innerHTML = '!';
            return;
        }
        
        // Format price nicely
        const formattedPrice = new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(data.prediction);
        
        // Display result
        priceDisplay.innerHTML = formattedPrice;
        resultText.textContent = 'Estimated market price';
        
        // Celebration animation
        priceDisplay.classList.add('animate__animated', 'animate__tada');
        setTimeout(() => {
            priceDisplay.classList.remove('animate__animated', 'animate__tada');
        }, 1000);
    })
    .catch(error => {
        console.error('Error:', error);
        priceDisplay.innerHTML = '!';
        resultText.innerHTML = '<span style="color:red">Server error. Please try again.</span>';
    });
});