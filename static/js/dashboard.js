// Dashboard logic: draws charts from /api/stats and sends the form to /api/predict
Chart.defaults.color = '#cbd5e1';
Chart.defaults.borderColor = 'rgba(255,255,255,.08)';
Chart.defaults.maintainAspectRatio = false;
const COLORS = ['#22d3ee', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'];
const RISK_COLORS = {Low: '#22c55e', Moderate: '#f59e0b', High: '#ef4444'};
const ICONS = {Low: 'bi-brightness-high', Moderate: 'bi-cloud-rain', High: 'bi-cloud-lightning-rain-fill'};
let inputChart;

function makeChart(id, type, labels, data, label, extra) {
  new Chart(document.getElementById(id), {
    type: type,
    data: {labels: labels, datasets: [{label: label, data: data, backgroundColor: COLORS, borderColor: '#22d3ee', borderRadius: 6}]},
    options: Object.assign({plugins: {legend: {display: false}}}, extra || {})
  });
}

async function loadCharts() {
  const res = await fetch('/api/stats');
  if (!res.ok) return;                       // model not trained yet: page already shows a message
  const {stats, metrics} = await res.json();
  makeChart('distChart', 'bar', stats.distribution.labels, stats.distribution.counts, 'Days', {scales: {y: {type: 'logarithmic'}}});
  makeChart('trendChart', 'bar', Object.keys(stats.by_location), Object.values(stats.by_location), 'Avg mm/day', {indexAxis: 'y'});
  makeChart('evalChart', 'bar', metrics.classes, metrics.classes.map(c => +(metrics.per_class_recall[c] * 100).toFixed(1)), 'Recall %', {scales: {y: {max: 100}}});
  makeChart('impChart', 'bar', Object.keys(stats.importance), Object.values(stats.importance), 'Importance', {indexAxis: 'y'});
}

document.getElementById('fillBtn').addEventListener('click', () => {
  const sample = {MinTemp: 18, MaxTemp: 28, Humidity9am: 92, Humidity3pm: 88, Pressure3pm: 1004, WindGustSpeed: 65, Temp3pm: 24};
  for (const k in sample) document.querySelector(`[name=${k}]`).value = sample[k];
});

document.getElementById('form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {};
  document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
  const box = document.getElementById('formError');
  box.classList.add('d-none');
  new FormData(e.target).forEach((v, k) => body[k] = v === '' ? null : v);
  try {
    const res = await fetch('/api/predict', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
    const data = await res.json();
    if (!res.ok) {
      box.textContent = data.error; box.classList.remove('d-none');
      for (const k in (data.fields || {})) document.getElementById('err-' + k).textContent = data.fields[k];
      return;
    }
    showResult(data);
  } catch (err) {
    box.textContent = 'Could not reach the server. Is Flask running?'; box.classList.remove('d-none');
  }
});

function showResult(d) {
  document.getElementById('result').innerHTML =
    `<div class="result ${d.risk}"><i class="bi ${ICONS[d.risk]}" style="font-size:3rem;color:${RISK_COLORS[d.risk]}"></i>
     <h2 class="mt-2">${d.risk} Risk</h2><p class="mb-0">${d.explanation}</p></div>
     <p class="text-muted small mt-2 mb-0">Educational prototype based on historical daily data, not an official forecast.</p>`;
  document.getElementById('inputBox').classList.remove('d-none');
  if (inputChart) inputChart.destroy();
  inputChart = new Chart(document.getElementById('inputChart'), {
    type: 'bar',
    data: {labels: Object.keys(d.inputs), datasets: [{label: 'Entered value', data: Object.values(d.inputs), backgroundColor: RISK_COLORS[d.risk], borderRadius: 6}]},
    options: {plugins: {legend: {display: false}}}
  });
}
loadCharts();
