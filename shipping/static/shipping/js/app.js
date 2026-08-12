document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadOrdersList();
  loadBoxesList();
  loadProductsList();
  initSimulator();
  initApiInspector();
});

// State Store
const state = {
  orders: [],
  boxes: [],
  products: [],
  simulatorItems: []
};

// Tab Controller
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  const views = document.querySelectorAll(".tab-view");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      views.forEach(v => v.classList.remove("active"));

      tab.classList.add("active");
      const viewId = tab.dataset.tab;
      document.getElementById(viewId).classList.add("active");
    });
  });
}

// Load Orders for Recommender Dropdown
async function loadOrdersList() {
  try {
    const response = await fetch("/api/orders/");
    const data = await response.json();
    state.orders = data.orders || [];

    const selectEl = document.getElementById("order-select");
    if (!selectEl) return;

    selectEl.innerHTML = '<option value="">-- Select an Order --</option>';
    state.orders.forEach(order => {
      const opt = document.createElement("option");
      opt.value = order.id;
      opt.textContent = `Order #${order.id} (${order.items_count} items - ${order.total_weight} kg)`;
      selectEl.appendChild(opt);
    });

    selectEl.addEventListener("change", (e) => {
      const selectedId = e.target.value;
      if (selectedId) {
        renderOrderDetails(selectedId);
        runRecommendation(selectedId);
      } else {
        clearRecommendationView();
      }
    });

    // Auto-select first order if available
    if (state.orders.length > 0) {
      selectEl.value = state.orders[0].id;
      renderOrderDetails(state.orders[0].id);
      runRecommendation(state.orders[0].id);
    }
  } catch (err) {
    console.error("Failed to load orders:", err);
  }
}

// Render Order Items Table
function renderOrderDetails(orderId) {
  const order = state.orders.find(o => o.id == orderId);
  const container = document.getElementById("order-items-tbody");
  if (!order || !container) return;

  container.innerHTML = "";
  order.items.forEach(item => {
    const tr = document.createElement("tr");
    const itemVol = (parseFloat(item.length) * parseFloat(item.width) * parseFloat(item.height) * item.quantity).toFixed(0);
    tr.innerHTML = `
      <td><strong>${item.product_name}</strong></td>
      <td>${item.quantity}</td>
      <td>${item.length} × ${item.width} × ${item.height} cm</td>
      <td>${item.weight} kg</td>
      <td>${itemVol} cm³</td>
    `;
    container.appendChild(tr);
  });

  document.getElementById("order-total-weight").textContent = `${order.total_weight} kg`;
  document.getElementById("order-total-volume").textContent = `${order.total_volume} cm³`;
}

// Run Recommendation API Call
async function runRecommendation(orderId) {
  const resultPanel = document.getElementById("recommendation-result");
  if (!resultPanel) return;

  resultPanel.innerHTML = '<div class="card" style="text-align:center; padding:2rem;">Calculating optimal box recommendation...</div>';

  try {
    const startTime = performance.now();
    const response = await fetch(`/orders/${orderId}/recommend/`);
    const duration = Math.round(performance.now() - startTime);
    const data = await response.json();

    if (response.ok && data.recommended_box) {
      renderSuccessRecommendation(data, duration, resultPanel);
    } else {
      renderErrorRecommendation(data.error || "No suitable box found", resultPanel);
    }
  } catch (err) {
    renderErrorRecommendation("Failed to connect to recommendation service", resultPanel);
  }
}

function renderSuccessRecommendation(data, duration, container) {
  const b = data.box_details;
  const m = data.metrics;

  container.innerHTML = `
    <div class="box-hero-card">
      <div class="box-hero-header">
        <div>
          <span class="box-tag">Optimal Box Recommendation</span>
          <h2 class="box-title">${data.recommended_box}</h2>
        </div>
        <div style="text-align:right;">
          <div class="box-price">$${data.cost}</div>
          <span style="font-size:0.75rem; color:#94a3b8;">${duration}ms response time</span>
        </div>
      </div>

      <div class="visual-box-stage">
        <div class="cube-3d">
          <div class="cube-face front">${b.internal_length} cm</div>
          <div class="cube-face back">${b.internal_length} cm</div>
          <div class="cube-face right">${b.internal_width} cm</div>
          <div class="cube-face left">${b.internal_width} cm</div>
          <div class="cube-face top">${b.internal_height} cm H</div>
          <div class="cube-face bottom">FIT</div>
        </div>
      </div>

      <div class="metrics-section">
        <div class="metric-bar-group">
          <div class="metric-header">
            <span>Weight Capacity Utilization</span>
            <span>${m.total_weight} kg / ${b.max_weight} kg (${m.weight_utilization_pct}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill weight" style="width: ${Math.min(m.weight_utilization_pct, 100)}%;"></div>
          </div>
        </div>

        <div class="metric-bar-group">
          <div class="metric-header">
            <span>Volumetric Capacity Utilization</span>
            <span>${m.total_volume} cm³ / ${b.volume} cm³ (${m.volume_utilization_pct}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill volume" style="width: ${Math.min(m.volume_utilization_pct, 100)}%;"></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderErrorRecommendation(errorMsg, container) {
  container.innerHTML = `
    <div class="error-card">
      <h3>⚠️ No Suitable Box Found</h3>
      <p>${errorMsg}</p>
      <p style="font-size:0.8rem; margin-top:0.5rem; opacity:0.8;">The order exceeds the max weight capacity or dimensions of all available boxes in inventory.</p>
    </div>
  `;
}

function clearRecommendationView() {
  document.getElementById("order-items-tbody").innerHTML = '<tr><td colspan="5" style="text-align:center;">Select an order to view items</td></tr>';
  document.getElementById("recommendation-result").innerHTML = '';
}

// Load Boxes Inventory List
async function loadBoxesList() {
  try {
    const res = await fetch("/api/boxes/");
    const data = await res.json();
    state.boxes = data.boxes || [];

    const container = document.getElementById("boxes-grid");
    if (!container) return;

    container.innerHTML = "";
    state.boxes.forEach(b => {
      const card = document.createElement("div");
      card.className = "item-card";
      card.innerHTML = `
        <div class="item-card-header">
          <div class="item-card-title">${b.name}</div>
          <div class="item-badge">$${b.cost}</div>
        </div>
        <div class="item-specs">
          <div><span class="spec-label">Dimensions:</span></div>
          <div><span class="spec-val">${b.internal_length} × ${b.internal_width} × ${b.internal_height} cm</span></div>
          <div><span class="spec-label">Max Weight:</span></div>
          <div><span class="spec-val">${b.max_weight} kg</span></div>
          <div><span class="spec-label">Volume:</span></div>
          <div><span class="spec-val">${b.volume} cm³</span></div>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load boxes:", err);
  }
}

// Load Products Catalog List
async function loadProductsList() {
  try {
    const res = await fetch("/api/products/");
    const data = await res.json();
    state.products = data.products || [];

    const container = document.getElementById("products-grid");
    if (!container) return;

    container.innerHTML = "";
    state.products.forEach(p => {
      const card = document.createElement("div");
      card.className = "item-card";
      card.innerHTML = `
        <div class="item-card-header">
          <div class="item-card-title">${p.name}</div>
          <div class="item-badge" style="background:#e0e7ff; color:#3730a3;">${p.weight} kg</div>
        </div>
        <div class="item-specs">
          <div><span class="spec-label">Dimensions:</span></div>
          <div><span class="spec-val">${p.length} × ${p.width} × ${p.height} cm</span></div>
          <div><span class="spec-label">Unit Volume:</span></div>
          <div><span class="spec-val">${p.volume} cm³</span></div>
        </div>
      `;
      container.appendChild(card);
    });

    populateSimulatorDropdown();
  } catch (err) {
    console.error("Failed to load products:", err);
  }
}

// Simulator Controller
function initSimulator() {
  const addBtn = document.getElementById("sim-add-item-btn");
  const runBtn = document.getElementById("sim-run-btn");

  if (addBtn) {
    addBtn.addEventListener("click", () => {
      const pId = document.getElementById("sim-product-select").value;
      const qty = parseInt(document.getElementById("sim-qty-input").value) || 1;

      if (!pId || qty <= 0) return;

      const product = state.products.find(p => p.id == pId);
      if (!product) return;

      const existing = state.simulatorItems.find(i => i.product_id == pId);
      if (existing) {
        existing.quantity += qty;
      } else {
        state.simulatorItems.push({
          product_id: pId,
          product_name: product.name,
          length: product.length,
          width: product.width,
          height: product.height,
          weight: product.weight,
          quantity: qty
        });
      }

      renderSimulatorItems();
    });
  }

  if (runBtn) {
    runBtn.addEventListener("click", runSimulation);
  }
}

function populateSimulatorDropdown() {
  const sel = document.getElementById("sim-product-select");
  if (!sel) return;
  sel.innerHTML = '<option value="">-- Choose Product --</option>';
  state.products.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.name} (${p.length}x${p.width}x${p.height} cm - ${p.weight} kg)`;
    sel.appendChild(opt);
  });
}

function renderSimulatorItems() {
  const container = document.getElementById("sim-items-tbody");
  if (!container) return;

  container.innerHTML = "";
  let totWeight = 0;
  let totVol = 0;

  state.simulatorItems.forEach((item, index) => {
    const itemWeight = parseFloat(item.weight) * item.quantity;
    const itemVol = parseFloat(item.length) * parseFloat(item.width) * parseFloat(item.height) * item.quantity;

    totWeight += itemWeight;
    totVol += itemVol;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${item.product_name}</strong></td>
      <td>${item.quantity}</td>
      <td>${item.length} × ${item.width} × ${item.height} cm</td>
      <td>${itemWeight.toFixed(2)} kg</td>
      <td><button class="btn-secondary" style="padding:0.2rem 0.5rem; color:#ef4444;" onclick="removeSimItem(${index})">Remove</button></td>
    `;
    container.appendChild(tr);
  });

  document.getElementById("sim-total-weight").textContent = `${totWeight.toFixed(2)} kg`;
  document.getElementById("sim-total-volume").textContent = `${totVol.toFixed(0)} cm³`;
}

window.removeSimItem = function(index) {
  state.simulatorItems.splice(index, 1);
  renderSimulatorItems();
};

async function runSimulation() {
  const resultPanel = document.getElementById("sim-result-panel");
  if (!resultPanel) return;

  if (state.simulatorItems.length === 0) {
    resultPanel.innerHTML = '<div class="error-card">Please add at least one product to the custom order.</div>';
    return;
  }

  resultPanel.innerHTML = '<div class="card" style="text-align:center;">Calculating recommendation for custom order...</div>';

  try {
    const res = await fetch("/api/simulate/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: state.simulatorItems })
    });
    const data = await res.json();

    if (res.ok && data.recommended_box) {
      renderSuccessRecommendation(data, 0, resultPanel);
    } else {
      renderErrorRecommendation(data.error || "No suitable box found", resultPanel);
    }
  } catch (err) {
    renderErrorRecommendation("Failed to simulate recommendation", resultPanel);
  }
}

// API Inspector Controller
function initApiInspector() {
  const sendBtn = document.getElementById("api-send-btn");
  const inputEl = document.getElementById("api-url-input");
  const presets = document.querySelectorAll(".preset-btn");

  presets.forEach(btn => {
    btn.addEventListener("click", () => {
      inputEl.value = btn.dataset.url;
      triggerApiInspectorCall(btn.dataset.url);
    });
  });

  if (sendBtn) {
    sendBtn.addEventListener("click", () => {
      triggerApiInspectorCall(inputEl.value);
    });
  }
}

async function triggerApiInspectorCall(url) {
  const outEl = document.getElementById("api-json-output");
  const timeEl = document.getElementById("api-time-tag");
  const statusEl = document.getElementById("api-status-tag");

  if (!outEl) return;
  outEl.textContent = "Loading response...";

  try {
    const t0 = performance.now();
    const res = await fetch(url);
    const ms = Math.round(performance.now() - t0);
    const data = await res.json();

    timeEl.textContent = `${ms} ms`;
    statusEl.textContent = `${res.status} ${res.statusText || (res.ok ? "OK" : "Error")}`;
    statusEl.style.backgroundColor = res.ok ? "#10b981" : "#ef4444";

    outEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    outEl.textContent = `Error fetching API endpoint: ${err.message}`;
  }
}
