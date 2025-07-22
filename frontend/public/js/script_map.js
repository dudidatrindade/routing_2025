/**
 * script_map.js: Controla a interação do dashboard de rotas e sensores.
 */

const API_BASE = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', function () {
    // Carrega os dados dos sensores assim que a página é aberta
    loadSensorData();

    // Ao clicar no botão "Gerar Mapa"
    const generateMapBtn = document.getElementById('generateMapBtn');
    generateMapBtn.addEventListener('click', function () {
        // Monta URL absoluta para o endpoint de mapa
        let url = `${API_BASE}/api/mapa`;

        // Opção de pontos: "all" ou "filtered"
        let pointsOption = document.querySelector('input[name="points"]:checked').value;
        if (pointsOption === 'filtered') {
            let volumeThreshold = document.getElementById('volumeInput').value;
            if (volumeThreshold) {
                url += `?min_volume=${volumeThreshold}`;
            }
        }

        // Opção de prioridade: "recommended", "custom" ou "none"
        let priorityOption = document.querySelector('input[name="priority"]:checked').value;
        if (priorityOption === 'custom') {
            url += (url.includes('?') ? '&' : '?') + 'prioritize=1';
            let betaValue = document.getElementById('betaInput').value;
            url += `&beta=${betaValue}`;
        } else if (priorityOption === 'recommended') {
            url += (url.includes('?') ? '&' : '?') + 'prioritize=1';
        }

        // Chama loadMap com a URL completa e atualiza sensores
        loadMap(url);
        loadSensorData();
    });

    /**
     * Função para carregar o mapa
     */
    function loadMap(fullUrl) {
        const mapContainer = document.getElementById('mapFrame');
        const loading = document.getElementById('loading');

        loading.style.display = 'block';
        mapContainer.innerHTML = '';

        fetch(fullUrl, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    const iframe = document.createElement('iframe');
                    iframe.src = `${API_BASE}/static/${data.map_file}`;
                    iframe.width = "100%";
                    iframe.height = "600";
                    iframe.style.border = "none";
                    mapContainer.appendChild(iframe);
                } else {
                    mapContainer.innerText = "Erro ao carregar o mapa: " + data.message;
                }
            })
            .catch(error => {
                console.error('Erro ao carregar o mapa:', error);
                mapContainer.innerText = "Erro ao carregar o mapa.";
            })
            .finally(() => {
                loading.style.display = 'none';
            });
    }

    /**
     * Função para carregar os dados dos sensores do InfluxDB
     */
    function loadSensorData() {
        fetch(`${API_BASE}/api/sensor_control/sensores`, { method: 'GET' })
            .then(response => response.json())
            .then(sensorData => {
                renderSensorData(sensorData);
            })
            .catch(error => {
                console.error('Erro ao carregar os dados dos sensores:', error);
                document.getElementById('sensorData').innerText = "Erro ao carregar os dados dos sensores.";
            });
    }

    /**
     * Função para renderizar os dados dos sensores no dashboard
     */
    function renderSensorData(sensorData) {
        const viewMode = document.querySelector('input[name="sensorView"]:checked').value;
        const container = document.getElementById('sensorData');
        container.innerHTML = "";

        if (viewMode === 'list') {
            const ul = document.createElement('ul');
            ul.className = "sensor-list";
            sensorData.forEach(sensor => {
                let updateTime = new Date(sensor.time).toLocaleString();
                const li = document.createElement('li');
                li.className = "sensor-list-item";
                li.innerHTML = `
                  <span class="sensor-id" data-sensor-id="${sensor.sensor_id}" style="cursor:pointer; color: #7CCE00;">
                    <strong>${sensor.sensor_id}</strong>
                  </span>
                  - <span class="badge">${sensor.fill_percentage.toFixed(2)}%</span>
                  <br>
                  <small class="text-muted">Atualizado em: ${updateTime}</small>
                `;
                ul.appendChild(li);
            });
            container.appendChild(ul);
        } else {
            sensorData.forEach(sensor => {
                let updateTime = new Date(sensor.time).toLocaleString();
                const widget = document.createElement('div');
                widget.className = 'sensor-widget';
                widget.innerHTML = `
                  <h5 class="sensor-id" data-sensor-id="${sensor.sensor_id}" style="cursor:pointer; color: #7CCE00;">
                    ${sensor.sensor_id}
                  </h5>
                  <p>Volume: ${sensor.fill_percentage.toFixed(2)}%</p>
                  <small class="text-muted">Atualizado em: ${updateTime}</small>
                `;
                container.appendChild(widget);
            });
        }

        addSensorClickListeners();
    }

    /**
     * Adiciona os event listeners aos elementos de sensor para abrir o modal
     */
    function addSensorClickListeners() {
        document.querySelectorAll('.sensor-id').forEach(elem => {
            elem.addEventListener('click', () => {
                const sensorId = elem.getAttribute('data-sensor-id');
                openHistoryModal(sensorId);
            });
        });
    }

    /**
     * Função para abrir o modal e carregar o histórico do sensor
     */
    function openHistoryModal(sensorId) {
        document.getElementById('modalTitle').innerText = "Histórico de " + sensorId;
        const modal = document.getElementById('historyModal');
        modal.style.display = 'block';
        loadSensorHistory(sensorId);
    }

    /**
     * Função para fechar o modal
     */
    function closeHistoryModal() {
        const modal = document.getElementById('historyModal');
        modal.style.display = 'none';
        if (window.historyChart) {
            window.historyChart.destroy();
            window.historyChart = null;
        }
    }

    document.getElementById('closeModal').addEventListener('click', closeHistoryModal);
    window.addEventListener('click', event => {
        const modal = document.getElementById('historyModal');
        if (event.target === modal) closeHistoryModal();
    });

    /**
     * Função para carregar o histórico do sensor via endpoint
     */
    function loadSensorHistory(sensorId) {
        fetch(`${API_BASE}/api/sensor_control/historico?sensor_id=${sensorId}`)
            .then(response => response.json())
            .then(data => {
                const labels = data.map(item => new Date(item.time).toLocaleString());
                const values = data.map(item => item.fill_percentage);
                renderHistoryChart(labels, values);
            })
            .catch(error => {
                console.error("Erro ao carregar histórico:", error);
            });
    }

    /**
     * Função para renderizar o gráfico de histórico usando Chart.js
     */
    function renderHistoryChart(labels, values) {
        const ctx = document.getElementById('historyChart').getContext('2d');
        if (window.historyChart) {
            window.historyChart.destroy();
        }
        window.historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Fill Percentage (%)',
                    data: values,
                    borderColor: 'green',
                    backgroundColor: 'rgba(124, 206, 0, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Data/Hora' } },
                    y: {
                        title: { display: true, text: 'Fill Percentage (%)' },
                        suggestedMin: 0, suggestedMax: 100
                    }
                }
            }
        });
    }

    // Atualiza sensores quando muda a visualização
    document.querySelectorAll('input[name="sensorView"]').forEach(radio => {
        radio.addEventListener('change', loadSensorData);
    });

    // Botão "Atualizar Sensores"
    document.getElementById('updateSensorsBtn').addEventListener('click', function () {
        fetch(`${API_BASE}/api/sensor_control/atualizar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: "all" })
        })
            .then(response => response.json())
            .then(() => {
                alert("Comando enviado para atualizar os sensores!");
                setTimeout(loadSensorData, 5000);
            })
            .catch(error => {
                console.error("Erro ao enviar comando de atualização:", error);
                alert("Erro ao enviar comando de atualização!");
            });
    });
});
