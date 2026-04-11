// Smart Irrigation Dashboard Script

// --- Clock & Date ---
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
}
setInterval(updateTime, 1000);
updateTime();

// --- Chart Initialization ---
const ctx = document.getElementById('moistureChart').getContext('2d');
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = 'Outfit';

// Generate some initial mock data for the last 24 hours
const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
let moistureData = Array.from({length: 24}, () => 40 + Math.random() * 40);

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Soil Moisture (%)',
            data: moistureData,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            tension: 0.4, // Smooth curves
            fill: true,
            pointBackgroundColor: '#0f172a',
            pointBorderColor: '#10b981',
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleFont: { size: 14 },
                bodyFont: { size: 14 },
                padding: 12,
                cornerRadius: 8,
                displayColors: false
            }
        }
    }
});

// --- Mock Data Generator (Simulating ESP32 Sensor readings) ---
let currentTemp = 28.5;
let currentHumid = 65;
let currentSoil = moistureData[23];
let currentRainProb = 15;

const manualToggle = document.getElementById('manual-pump-toggle');
const pumpIndicatorContainer = document.getElementById('pump-indicator');
const pumpText = document.getElementById('pump-text');
const pumpReason = document.getElementById('pump-reason');
const soilStatusBadge = document.getElementById('soil-status');

// Pump Logic State
let isPumpOn = false;

function updateDashboardUI() {
    // Inject slight noise for realism
    currentTemp += (Math.random() - 0.5) * 0.5;
    currentHumid += (Math.random() - 0.5) * 1.5;
    currentRainProb += (Math.random() - 0.5) * 2;
    
    // Clamp constraints
    currentTemp = Math.max(15, Math.min(45, currentTemp));
    currentHumid = Math.max(30, Math.min(100, currentHumid));
    currentRainProb = Math.max(0, Math.min(100, currentRainProb));

    let autoReason = "";

    // Evaporation simulation
    currentSoil -= (currentTemp / 40.0) * 0.2;

    // Is the user overriding?
    if (manualToggle.checked) {
        isPumpOn = true;
        autoReason = "Manual Override Active";
    } else {
        // Auto logic based on fuzzy rule (simplified here)
        if (currentSoil < 40 && currentRainProb < 60) {
            isPumpOn = true;
            autoReason = "Soil too dry, no rain expected";
        } else if (currentSoil > 75) {
            isPumpOn = false;
            autoReason = "Soil is sufficiently wet";
        } else if (currentRainProb >= 60) {
            isPumpOn = false;
            autoReason = "Rain is expected soon";
        } else {
            isPumpOn = false;
            autoReason = "System is Idle";
        }
    }

    // Effect of watering
    if (isPumpOn) {
        currentSoil += 2.5; // Pump increases moisture quickly
    }
    
    currentSoil = Math.max(0, Math.min(100, currentSoil));

    // Update DOM texts
    document.getElementById('temp-val').textContent = currentTemp.toFixed(1);
    document.getElementById('air-humid-val').textContent = currentHumid.toFixed(0);
    document.getElementById('soil-moisture-val').textContent = currentSoil.toFixed(1);
    document.getElementById('rain-prob-val').textContent = currentRainProb.toFixed(0);

    // Update Soil Badge
    if (currentSoil < 40) {
        soilStatusBadge.textContent = "Dry";
        soilStatusBadge.style.background = "rgba(239, 68, 68, 0.2)";
        soilStatusBadge.style.color = "var(--accent-danger)";
    } else if (currentSoil > 75) {
        soilStatusBadge.textContent = "Wet";
        soilStatusBadge.style.background = "rgba(59, 130, 246, 0.2)";
        soilStatusBadge.style.color = "var(--accent-blue)";
    } else {
        soilStatusBadge.textContent = "Optimal";
        soilStatusBadge.style.background = "rgba(16, 185, 129, 0.2)";
        soilStatusBadge.style.color = "var(--accent-green)";
    }

    // Update Pump State
    if (isPumpOn) {
        pumpIndicatorContainer.classList.add('active');
        pumpText.textContent = "ON";
        pumpText.style.color = "var(--accent-blue)";
    } else {
        pumpIndicatorContainer.classList.remove('active');
        pumpText.textContent = "OFF";
        pumpText.style.color = "var(--text-main)";
    }
    pumpReason.textContent = autoReason;
    
    // Smoothly update the very last node on the chart
    chart.data.datasets[0].data[23] = currentSoil;
    chart.update('none'); // Update without full animation
}

// Tick every 2 seconds to simulate incoming MQTT/Socket data
setInterval(updateDashboardUI, 2000);
updateDashboardUI();
