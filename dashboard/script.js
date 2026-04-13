// Smart Irrigation Dashboard Script (AI-Powered Version)

// --- Clock & Date ---
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString('vi-VN', { hour12: false });
    document.getElementById('current-date').textContent = now.toLocaleDateString('vi-VN', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
}
setInterval(updateTime, 1000);
updateTime();

// --- Chart Initialization ---
const ctx = document.getElementById('moistureChart').getContext('2d');
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = 'Outfit';

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], 
        datasets: [{
            label: 'Độ ẩm đất (%)',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#0f172a',
            pointBorderColor: '#10b981',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
            x: { grid: { display: false } }
        },
        plugins: {
            legend: { display: false },
        }
    }
});

const manualToggle = document.getElementById('manual-pump-toggle');
const pumpIndicatorContainer = document.getElementById('pump-indicator');
const pumpText = document.getElementById('pump-text');
const pumpReason = document.getElementById('pump-reason');
const soilStatusBadge = document.getElementById('soil-status');

// --- Fetch DATA from Python Backend ---
async function refreshData() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const current = data.current;
        const history = data.history;

        // 1. Update Labels and Chart Data
        chart.data.labels = history.map(item => item.timestamp);
        chart.data.datasets[0].data = history.map(item => item.soil_moisture * 100);
        chart.update();

        // 2. Update UI Cards
        document.getElementById('temp-val').textContent = current.air_temp.toFixed(1);
        document.getElementById('air-humid-val').textContent = current.air_humidity.toFixed(0);
        document.getElementById('soil-moisture-val').textContent = (current.soil_moisture * 100).toFixed(1);
        
        // Rain - display predicted or actual rain
        document.getElementById('rain-prob-val').textContent = current.rain_mm.toFixed(1);

        // 3. Update Soil Status Badge
        const soil = current.soil_moisture * 100;
        if (soil < 40) {
            soilStatusBadge.textContent = "Khô";
            soilStatusBadge.style.background = "rgba(239, 68, 68, 0.2)";
            soilStatusBadge.style.color = "var(--accent-danger)";
        } else if (soil > 80) {
            soilStatusBadge.textContent = "Ẩm";
            soilStatusBadge.style.background = "rgba(59, 130, 246, 0.2)";
            soilStatusBadge.style.color = "var(--accent-blue)";
        } else {
            soilStatusBadge.textContent = "Tối ưu";
            soilStatusBadge.style.background = "rgba(16, 185, 129, 0.2)";
            soilStatusBadge.style.color = "var(--accent-green)";
        }

        // 4. Update Pump logic (AI from MLP results)
        const isAIPumpOn = current.pump_status === 1;
        const isPumpRunning = manualToggle.checked || isAIPumpOn;

        if (isPumpRunning) {
            pumpIndicatorContainer.classList.add('active');
            pumpText.textContent = "BẬT";
            pumpText.style.color = "var(--accent-blue)";
            pumpReason.textContent = manualToggle.checked ? "Điều khiển tay" : `AI MLP: Đang ra lệnh tưới`;
        } else {
            pumpIndicatorContainer.classList.remove('active');
            pumpText.textContent = "TẮT";
            pumpText.style.color = "var(--text-main)";
            pumpReason.textContent = "AI MLP: Đất đủ ẩm, không cần tưới";
        }

    } catch (err) {
        console.error("Failed to fetch statistics:", err);
    }
}

// Update every 5 seconds
setInterval(refreshData, 5000);
refreshData();
