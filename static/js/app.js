// SISSOT Frontend Logic

let map;
const API_URL = ''; // Relative to the server

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    await fetchStats();
    await fetchCommunes();
    await fetchAlerts();
    await fetchPatients(); // Added
    initCharts();
    initMap();
    
    // Set up form submission
    document.getElementById('patient-form').addEventListener('submit', handlePatientSubmit);
}

// Section management
window.showSection = (sectionId) => {
    // Hide all
    ['dashboard', 'patients', 'map', 'alerts', 'reports'].forEach(s => {
        document.getElementById(`section-${s}`).classList.add('hidden');
        document.getElementById(`nav-${s}`).classList.remove('active');
    });
    
    // Show target
    document.getElementById(`section-${sectionId}`).classList.remove('hidden');
    document.getElementById(`nav-${sectionId}`).classList.add('active');
    
    // Update title
    const titles = {
        'dashboard': 'Dashboard General',
        'patients': 'Gestión de Pacientes',
        'map': 'Mapa Epidemiológico',
        'alerts': 'Centro de Alertas',
        'reports': 'Generación de Reportes'
    };
    document.getElementById('section-title').innerText = titles[sectionId];
    
    // Resize map if visible
    if (sectionId === 'map' && map) {
        setTimeout(() => map.invalidateSize(), 200);
    }
};

// API Calls
async function fetchStats() {
    try {
        const res = await fetch(`${API_URL}/api/stats`);
        const data = await res.json();
        document.getElementById('stat-patients').innerText = data.total_patients || 0;
        document.getElementById('stat-alerts').innerText = data.active_alerts || 0;
        document.getElementById('stat-alerts-badge').innerText = data.active_alerts || 0;
        
        // Update charts if data exists
        updateCharts(data.pathology_distribution);
    } catch (e) {
        console.error("Error fetching stats", e);
    }
}

async function fetchCommunes() {
    try {
        const res = await fetch(`${API_URL}/api/communes`);
        const data = await res.json();
        const select = document.getElementById('commune-select');
        select.innerHTML = data.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    } catch (e) {
        console.error("Error fetching communes", e);
    }
}

async function fetchPatients() {
    try {
        const res = await fetch(`${API_URL}/api/patients`);
        const data = await res.json();
        
        // Update Dashboard Table (Recent 5)
        const recentTable = document.getElementById('recent-patients-table');
        recentTable.innerHTML = data.slice(-5).reverse().map(p => `
            <tr>
                <td class="px-6 py-4 font-medium">${p.first_name} ${p.last_name}</td>
                <td class="px-6 py-4 text-slate-500">Consulta Inicial</td>
                <td class="px-6 py-4">${p.commune_id}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 bg-medical-50 text-medical-600 rounded-lg text-xs">Estable</span>
                </td>
                <td class="px-6 py-4 text-xs">${new Date().toLocaleDateString()}</td>
            </tr>
        `).join('');

        // Update Patients Section Table
        const fullTable = document.getElementById('patients-full-table');
        fullTable.innerHTML = data.map(p => `
            <tr>
                <td class="px-6 py-4 font-medium">${p.first_name} ${p.last_name}</td>
                <td class="px-6 py-4 text-slate-500">${p.dni}</td>
                <td class="px-6 py-4">Comuna ${p.commune_id}</td>
                <td class="px-6 py-4 text-medical-600 font-medium">General</td>
                <td class="px-6 py-4">
                    <div class="flex gap-2">
                        <button onclick="downloadPDF(${p.id})" class="p-2 text-medical-600 hover:bg-medical-50 rounded-lg" title="Descargar Ficha">
                            <i class="fas fa-file-pdf"></i>
                        </button>
                        <button class="p-2 text-slate-400 hover:bg-slate-50 rounded-lg">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Error fetching patients", e);
    }
}

window.downloadPDF = async (patientId) => {
    window.open(`${API_URL}/api/patients/${patientId}/pdf`, '_blank');
};

async function fetchAlerts() {
    try {
        const res = await fetch(`${API_URL}/api/alerts`);
        const data = await res.json();
        const container = document.getElementById('alerts-container');
        
        if (data.length === 0) {
            container.innerHTML = '<p class="text-sm text-slate-500 italic">No hay alertas activas.</p>';
            return;
        }
        
        container.innerHTML = data.map(alert => `
            <div class="p-3 bg-${alert.level === 'Critico' ? 'rose' : 'amber'}-50 dark:bg-${alert.level === 'Critico' ? 'rose' : 'amber'}-900/20 border-l-4 border-${alert.level === 'Critico' ? 'danger' : 'warning'} rounded-r-lg">
                <div class="flex justify-between items-start">
                    <h4 class="font-bold text-sm text-${alert.level === 'Critico' ? 'danger' : 'warning'}">${alert.type}</h4>
                    <span class="text-[10px] text-slate-500">${new Date(alert.created_at).toLocaleDateString()}</span>
                </div>
                <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">${alert.description}</p>
            </div>
        `).join('');
    } catch (e) {
        console.error("Error fetching alerts", e);
    }
}

// Charts Logic
let trendChart, pathologyChart;

function initCharts() {
    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
            datasets: [{
                label: 'Casos Registrados',
                data: [12, 19, 15, 8, 22, 14, 10],
                borderColor: '#0ea5e9',
                backgroundColor: 'rgba(14, 165, 233, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });

    const ctxPath = document.getElementById('pathologyChart').getContext('2d');
    pathologyChart = new Chart(ctxPath, {
        type: 'doughnut',
        data: {
            labels: ['Gripe', 'Dengue', 'Diabetes', 'Hipertensión', 'Otros'],
            datasets: [{
                data: [30, 20, 15, 25, 10],
                backgroundColor: ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#64748b']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } },
            cutout: '70%'
        }
    });
}

function updateCharts(pathologyData) {
    if (!pathologyData || Object.keys(pathologyData).length === 0) return;
    
    pathologyChart.data.labels = Object.keys(pathologyData);
    pathologyChart.data.datasets[0].data = Object.values(pathologyData);
    pathologyChart.update();
}

// Map Logic
function initMap() {
    // Center of Puerto La Cruz / Sotillo
    map = L.map('map').setView([10.2167, -64.6333], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Mock markers for communes
    const locations = [
        { name: "Pozuelos", lat: 10.21, lng: -64.62, risk: "High" },
        { name: "Chuparín", lat: 10.22, lng: -64.64, risk: "Medium" },
        { name: "Molorca", lat: 10.19, lng: -64.65, risk: "Low" }
    ];

    locations.forEach(loc => {
        const color = loc.risk === "High" ? "#ef4444" : (loc.risk === "Medium" ? "#f59e0b" : "#10b981");
        L.circleMarker([loc.lat, loc.lng], {
            radius: 10,
            fillColor: color,
            color: "#fff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup(`<b>${loc.name}</b><br>Riesgo: ${loc.risk}`);
    });
}

// Form management
window.openPatientForm = () => {
    document.getElementById('patient-modal').classList.remove('hidden');
    document.getElementById('patient-modal').classList.add('flex');
};

window.closePatientForm = () => {
    document.getElementById('patient-modal').classList.add('hidden');
    document.getElementById('patient-modal').classList.remove('flex');
};

async function handlePatientSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const res = await fetch(`${API_URL}/api/patients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (res.ok) {
            alert('Paciente registrado exitosamente');
            closePatientForm();
            e.target.reset();
            fetchStats();
        } else {
            const error = await res.json();
            alert('Error: ' + JSON.stringify(error));
        }
    } catch (e) {
        console.error("Error submitting patient", e);
    }
}

// UI Helpers
window.toggleDarkMode = () => {
    document.documentElement.classList.toggle('dark');
};
