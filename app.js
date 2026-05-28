document.addEventListener('DOMContentLoaded', () => {
    // App configuration matching your brand setup
    const appConfig = {
        name: 'weare.kitty.devs',
        version: '1.0.0'
    };

    // UI elements mapping
    const scanBtn = document.getElementById('scan-btn');
    const traitListNegatives = document.querySelector('.trait-list'); // target negatives section
    
    // Hardcoded dataset simulating the backend scanner response
    const mockAnalysisData = {
        productName: "Tangy Cheese Tortilla Chips",
        brand: "Doritos",
        score: 21,
        rating: "Bad",
        negatives: [
            { name: "Additives", desc: "Contains additives to avoid", value: "9", color: "red" },
            { name: "Energy", desc: "A bit too caloric", value: "501 kcal", color: "orange" },
            { name: "Salt", desc: "A bit too salty", value: "1.19g", color: "orange" }
        ],
        positives: [
            { name: "Fibre", desc: "Excellent amount of fibre", value: "5.6g", color: "green" },
            { name: "Protein", desc: "Some protein", value: "6.5g", color: "green" },
            { name: "Sugar", desc: "Low sugar", value: "2.7g", color: "green" }
        ]
    };

    /**
     * Updates the main analysis card with newly scanned data
     * @param {Object} data - The nutritional data structure
     */
    function renderAnalysis(data) {
        document.querySelector('.product-info h2').textContent = data.productName;
        document.querySelector('.brand').textContent = data.brand;
        document.querySelector('.score strong').textContent = `${data.score}/100`;
        document.querySelector('.score span').textContent = data.rating;

        // Clear existing static items and dynamically map new elements
        const lists = document.querySelectorAll('.trait-list');
        const negativesList = lists[0];
        const positivesList = lists[1];

        negativesList.innerHTML = data.negatives.map(item => `
            <li>
                <div class="trait-info">
                    <strong>${item.name}</strong>
                    <span>${item.desc}</span>
                </div>
                <div class="trait-score">${item.value} <span class="dot ${item.color}"></span></div>
            </li>
        `).join('');

        positivesList.innerHTML = data.positives.map(item => `
            <li>
                <div class="trait-info">
                    <strong>${item.name}</strong>
                    <span>${item.desc}</span>
                </div>
                <div class="trait-score">${item.value} <span class="dot ${item.color}"></span></div>
            </li>
        `).join('');
    }

    // Trigger state changes when execution occurs
    if (scanBtn) {
        scanBtn.addEventListener('click', () => {
            console.log(`[${appConfig.name}] Initializing image acquisition sequence...`);
            
            // UI Visual Feedback state change
            scanBtn.textContent = "Processing Stream...";
            scanBtn.disabled = true;

            setTimeout(() => {
                renderAnalysis(mockAnalysisData);
                scanBtn.textContent = "Scan Next Product";
                scanBtn.disabled = false;
            }, 1200);
        });
    }
});
