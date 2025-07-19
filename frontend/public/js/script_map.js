// js/script_map.js

/**
 * script_map.js: Controla a interação do dashboard de rotas e sensores.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Carrega os dados dos sensores assim que a página é aberta
    loadSensorData();

    // Ao clicar no botão "Gerar Mapa"
    const generateMapBtn = document.getElementById('generateMapBtn');
    generateMapBtn.addEventListener('click', function () {
        let url = 'http://localhost:5001/api/mapa';

        // Opção de pontos: "all" ou "filtered"
        let pointsOption = document.querySelector('input[name="points"]:checked').value;
        if (pointsOption === 'filtered') {
            let volumeThreshold = document.getElementById('volumeInput').value;
            if (volumeThreshold) {
                url += '?min_volume=' + volumeThreshold;
            }
        }

        // Opção de prioridade: "recommended" ou "custom" ou "none"
        let priorityOption = document.querySelector('input[name="priority"]:checked').value;
        if (priorityOption === 'custom') {
            url += (url.indexOf('?') >= 0 ? '&' : '?') + 'prioritize=1';
            let betaValue = document.getElementById('betaInput').value;
            url += '&beta=' + betaValue;
        } else if (priorityOption === 'recommended') {
            url += (url.indexOf('?') >= 0 ? '&' : '?') + 'prioritize=1';
        } // if none não adiciona parametro

        // Mostra loading e carrega mapa
        loadMap(url);
        // Atualiza dados dos sensores também
        loadSensorData();
    });

    /**
     * Função para carregar o mapa
     */
    function loadMap(url) {
        const mapContainer = document.getElementById('mapContainer');
        const loading = document.getElementById('loading');
        // mostra o loading
        loading.style.display = 'block';
        // limpa container antes de atualizar
        document.getElementById('mapFrame').innerHTML = '';

        fetch(url, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    const iframe = document.createElement('iframe');
                    iframe.src = "http://localhost:5001/static/" + data.map_file;
                    iframe.width = "100%";
                    iframe.height = "600";
                    iframe.style.border = "none";
                    // insere o mapa
                    document.getElementById('mapFrame').appendChild(iframe);
                } else {
                    document.getElementById('mapFrame').innerText = "Erro ao carregar o mapa: " + data.message;
                }
            })
            .catch(error => {
                console.error('Erro ao carregar o mapa:', error);
                document.getElementById('mapFrame').innerText = "Erro ao carregar o mapa.";
            })
            .finally(() => {
                // esconde o loading
                loading.style.display = 'none';
            });
    }

    /**
     * Função para carregar os dados dos sensores do InfluxDB
     */
    function loadSensorData() {
        fetch('http://localhost:5001/api/sensor_control/sensores', { method: 'GET' })
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
        const sensorDataContainer = document.getElementById('sensorData');
        sensorDataContainer.innerHTML = ""; // Limpa o conteúdo

        if (viewMode === 'list') {
            const ul = document.createElement('ul');
            ul.className = "sensor-list";
            sensorData.forEach(sensor => {
                let updateTime = new Date(sensor.time).toLocaleString();
                const li = document.createElement('li');
                li.className = "sensor-list-item";
                li.innerHTML = `
                  <span class="sensor-id" data-sensor-id="${sensor.sensor_id}" style="cursor:pointer; color: #7CCE00;"><strong>${sensor.sensor_id}</strong></span> 
                  - <span class="badge">${sensor.fill_percentage.toFixed(2)}%</span>
                  <br>
                  <small class="text-muted">Atualizado em: ${updateTime}</small>
                `;
                ul.appendChild(li);
            });
            sensorDataContainer.appendChild(ul);
        } else if (viewMode === 'widgets') {
            sensorData.forEach(sensor => {
                let updateTime = new Date(sensor.time).toLocaleString();
                const widget = document.createElement('div');
                widget.className = 'sensor-widget';
                widget.innerHTML = `
                  <h5 class="sensor-id" data-sensor-id="${sensor.sensor_id}" style="cursor:pointer; color: #7CCE00;">${sensor.sensor_id}</h5>
                  <p>Volume: ${sensor.fill_percentage.toFixed(2)}%</p>
                  <small class="text-muted">Atualizado em: ${updateTime}</small>
                `;
                sensorDataContainer.appendChild(widget);
            });
        }
        addSensorClickListeners();
    }

    /**
     * Adiciona event listeners aos elementos clicáveis (sensor-id) para abrir o modal
     */
    function addSensorClickListeners() {
        const sensorElements = document.querySelectorAll('.sensor-id');
        sensorElements.forEach(elem => {
            elem.addEventListener('click', function () {
                const sensorId = this.getAttribute('data-sensor-id');
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
        modal.style.display = "block";
        loadSensorHistory(sensorId);
    }

    /**
     * Função para fechar o modal
     */
    function closeHistoryModal() {
        const modal = document.getElementById('historyModal');
        modal.style.display = "none";
        if (window.historyChart && typeof window.historyChart.destroy === "function") {
            window.historyChart.destroy();
            window.historyChart = null;
        }
    }

    // Fecha o modal ao clicar no "x"
    document.getElementById('closeModal').addEventListener('click', closeHistoryModal);
    // Fecha o modal se clicar fora do conteúdo
    window.addEventListener('click', function (event) {
        const modal = document.getElementById('historyModal');
        if (event.target == modal) {
            closeHistoryModal();
        }
    });

    /**
     * Função para carregar o histórico do sensor via endpoint
     */
    function loadSensorHistory(sensorId) {
        fetch('http://localhost:5001/api/sensor_control/historico?sensor_id=' + sensorId)
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
     * Função para renderizar o gráfico utilizando Chart.js
     */
    function renderHistoryChart(labels, values) {
        const ctx = document.getElementById('historyChart').getContext('2d');
        if (window.historyChart && typeof window.historyChart.destroy === "function") {
            window.historyChart.destroy();
        }
        window.historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
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
                    y: { title: { display: true, text: 'Fill Percentage (%)' }, suggestedMin: 0, suggestedMax: 100 }
                }
            }
        });
    }

    // Atualiza os dados dos sensores quando a visualização muda
    const sensorViewRadios = document.querySelectorAll('input[name="sensorView"]');
    sensorViewRadios.forEach(radio => {
        radio.addEventListener('change', loadSensorData);
    });

    // Botão "Atualizar Sensores"
    const updateSensorsBtn = document.getElementById('updateSensorsBtn');
    updateSensorsBtn.addEventListener('click', function () {
        fetch('http://localhost:5001/api/sensor_control/atualizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: "all" })
        })
            .then(response => response.json())
            .then(data => {
                alert("Comando enviado para atualizar os sensores!");
                setTimeout(loadSensorData, 5000);
            })
            .catch(error => {
                console.error("Erro ao enviar comando de atualização:", error);
                alert("Erro ao enviar comando de atualização!");
            });
    });
});
