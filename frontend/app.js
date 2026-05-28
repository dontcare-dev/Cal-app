import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scan-btn');
    const SERVER_URL = 'http://127.0.0.1:8000/api/v1/scan'; // Update this to your server IP later

    async function captureAndAnalyze() {
        try {
            // 1. Trigger the Native Device Camera
            const image = await Camera.getPhoto({
                quality: 90,
                allowEditing: false,
                resultType: CameraResultType.Base64,
                source: CameraSource.Camera
            });

            // UI Feedback
            scanBtn.textContent = "Analyzing Structure...";
            scanBtn.disabled = true;

            // 2. Transmit to Python Backend
            const response = await fetch(SERVER_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: "local_user_01",
                    image_base64: image.base64String
                })
            });

            if (!response.ok) throw new Error("Backend processing failed.");

            const data = await response.json();
            
            // 3. Render the dynamic UI
            renderAnalysis(data);

        } catch (error) {
            console.error("Camera/Network Error:", error);
            scanBtn.textContent = "Error. Try Again.";
        } finally {
            scanBtn.disabled = false;
            setTimeout(() => { scanBtn.textContent = "Scan Next Product"; }, 2000);
        }
    }

    function renderAnalysis(data) {
        document.querySelector('.product-info h2').textContent = data.productName;
        document.querySelector('.brand').textContent = data.brand;
        document.querySelector('.score strong').textContent = `${data.score}/100`;
        document.querySelector('.score span').textContent = data.rating;

        const lists = document.querySelectorAll('.trait-list');
        
        // Render Negatives
        lists[0].innerHTML = data.negatives.map(item => `
            <li>
                <div class="trait-info">
                    <strong>${item.name}</strong><span>${item.desc}</span>
                </div>
                <div class="trait-score">${item.value} <span class="dot ${item.color}"></span></div>
            </li>
        `).join('');

        // Render Positives
        lists[1].innerHTML = data.positives.map(item => `
            <li>
                <div class="trait-info">
                    <strong>${item.name}</strong><span>${item.desc}</span>
                </div>
                <div class="trait-score">${item.value} <span class="dot ${item.color}"></span></div>
            </li>
        `).join('');
    }

    if (scanBtn) {
        scanBtn.addEventListener('click', captureAndAnalyze);
    }
});
