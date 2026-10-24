/* ============================================================
   IntelliSales — Frontend Application Logic
   All data comes from the verified backend API.
   ============================================================ */

"use strict";

// ---------------------------------------------------------------------------
// Chart.js global defaults — dark enterprise theme
// ---------------------------------------------------------------------------

Chart.defaults.color = "#94a3b8";
Chart.defaults.borderColor = "rgba(148, 163, 184, 0.1)";
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 8;

const chartColors = {
    accent: "#6366f1",
    accentLight: "#818cf8",
    purple: "#8b5cf6",
    green: "#10b981",
    amber: "#f59e0b",
    red: "#ef4444",
    cyan: "#22d3ee",
    pink: "#ec4899",
    grid: "rgba(148, 163, 184, 0.08)",
    tooltipBg: "#1a2338",
    tooltipBorder: "#2a3a5c",
};

/* ---------- State ---------- */

let state = {
    summary: null,
    productPerformance: [],
    regionPerformance: [],
    categoryPerformance: [],
    insights: [],
    trend: [],
    forecast: { historical: [], forecast: [] },
    forecastPeriods: 6,
    analyticsTab: "product",
    anomalies: { transactions: [], time_series: [], dimensions: { product: [], region: [], category: [] }, summary: {} },
    bigData: null,
};

/* ---------- Helpers ---------- */

function formatCurrency(value) {
    return "₹" + Number(value).toLocaleString("en-IN", {
        maximumFractionDigits: 0,
    });
}

function formatCurrencyCompact(value) {
    const num = Number(value);
    if (num >= 1e7) return "₹" + (num / 1e7).toFixed(1) + " Cr";
    if (num >= 1e5) return "₹" + (num / 1e5).toFixed(1) + " L";
    if (num >= 1e3) return "₹" + (num / 1e3).toFixed(1) + "K";
    return "₹" + num.toFixed(0);
}

function formatNumber(value) {
    return Number(value).toLocaleString("en-IN");
}

function monthLabel(monthStr) {
    const [year, month] = monthStr.split("-").map(Number);
    const date = new Date(year, month - 1, 1);
    return date.toLocaleString("en-US", { month: "short", year: "numeric" });
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed: ${response.status}`);
    }
    return response.json();
}

/* ---------- Navigation ---------- */

const PAGE_META = {
    overview: { title: "Overview", subtitle: "Sales intelligence at a glance" },
    analytics: { title: "Analytics", subtitle: "Detailed performance breakdown" },
    forecasting: { title: "Forecasting", subtitle: "Projected revenue from your data" },
    analyst: { title: "AI Analyst", subtitle: "Ask questions — get verified answers" },
    anomalies: { title: "Anomaly Detection", subtitle: "Statistical outlier analysis" },
    bigdata: { title: "Big Data Analysis", subtitle: "Dataset health & processing strategy" },
};

function switchPage(page) {
    document.querySelectorAll(".nav-item").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.page === page);
    });

    document.querySelectorAll(".page").forEach((section) => {
        section.classList.toggle("active", section.id === `page-${page}`);
    });

    const meta = PAGE_META[page] || PAGE_META.overview;
    document.getElementById("page-heading").textContent = meta.title;
    document.getElementById("page-subheading").textContent = meta.subtitle;

    // Refresh charts after layout becomes visible
    window.setTimeout(() => {
        if (page === "overview") {
            renderOverViewCharts();
        }
        if (page === "analytics") {
            renderAnalyticsTrendChart();
        }
        if (page === "forecasting") {
            renderForecastPage();
        }
        if (page === "anomalies") {
            loadAnomalies();
        }
        if (page === "bigdata") {
            renderBigDataPage();
        }
    }, 50);
}

/* ---------- Dataset ---------- */

async function loadDatasetInfo() {
    try {
        const info = await fetchJson("/api/dataset/info");

        const label = document.getElementById("dataset-label");
        const badge = document.getElementById("dataset-badge");

        label.textContent = `${info.rows.toLocaleString("en-IN")} rows · ${info.date_min.slice(0, 10)} → ${info.date_max.slice(0, 10)}`;

        badge.querySelector(".dot").style.background = "#10b981";
        badge.querySelector(".dot").style.boxShadow = "0 0 8px rgba(16,185,129,0.2)";
    } catch (error) {
        console.error("Failed to load dataset info:", error);
        document.getElementById("dataset-label").textContent = "Sample dataset";
    }
}

/* ---------- KPI Cards ---------- */

function renderKpis(summary) {
    document.getElementById("kpi-revenue").textContent = formatCurrencyCompact(summary.total_revenue);
    document.getElementById("kpi-revenue-sub").textContent = `${formatNumber(summary.total_revenue)} total`;

    document.getElementById("kpi-profit").textContent = formatCurrencyCompact(summary.total_profit);
    document.getElementById("kpi-profit-sub").textContent = `${summary.total_records} records`;

    document.getElementById("kpi-quantity").textContent = formatNumber(summary.total_quantity);
    document.getElementById("kpi-quantity-sub").textContent = "units sold";

    document.getElementById("kpi-margin").textContent = `${summary.profit_margin.toFixed(1)}%`;
    document.getElementById("kpi-margin-sub").textContent = "profit margin";
}

/* ---------- Product performance table ---------- */

function renderProductTable(records) {
    const tbody = document.getElementById("product-table-body");
    if (!records || records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="table-loading">No data available.</td></tr>';
        return;
    }

    tbody.innerHTML = records
        .map(
            (record, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${record.product}</strong></td>
                    <td>${formatCurrency(record.total_revenue)}</td>
                    <td>${formatCurrency(record.total_profit)}</td>
                    <td>${formatNumber(record.total_quantity)}</td>
                    <td>${record.profit_margin.toFixed(1)}%</td>
                </tr>
            `
        )
        .join("");
}

/* ---------- Insights ---------- */

function renderInsights(insights) {
    const container = document.getElementById("insights-list");
    if (!insights || insights.length === 0) {
        container.innerHTML = '<div class="insight-loading">No insights available.</div>';
        return;
    }

    container.innerHTML = insights
        .map(
            (insight) => `
                <div class="insight-item">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-message">${insight.message}</div>
                </div>
            `
        )
        .join("");
}

/* ---------- Chart tooltip options ---------- */

function chartTooltipOptions() {
    return {
        backgroundColor: chartColors.tooltipBg,
        borderColor: chartColors.tooltipBorder,
        borderWidth: 1,
        titleColor: "#e8edf7",
        bodyColor: "#94a3b8",
        padding: 12,
        cornerRadius: 8,
    };
}

/* ---------- Trend chart ---------- */

function renderTrendChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const chart = Chart.getChart(canvasId);
    if (chart) chart.destroy();

    const labels = data.map((d) => monthLabel(d.month));
    const values = data.map((d) => d.revenue);

    const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.35)");
    gradient.addColorStop(1, "rgba(99, 102, 241, 0)");

    return new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Revenue",
                data: values,
                borderColor: chartColors.accent,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 3,
                pointBackgroundColor: chartColors.accentLight,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: { label: (ctx) => ` Revenue: ${formatCurrency(ctx.raw)}` },
                },
            },
            scales: {
                x: { grid: { color: chartColors.grid } },
                y: {
                    grid: { color: chartColors.grid },
                    ticks: { callback: (value) => formatCurrencyCompact(value) },
                },
            },
        },
    });
}

/* ---------- Forecast chart (overview) ---------- */

function renderForecastChart() {
    const canvas = document.getElementById("forecast-chart");
    if (!canvas) return;

    const chart = Chart.getChart("forecast-chart");
    if (chart) chart.destroy();

    const historical = state.forecast.historical.slice(-18);
    const forecast = state.forecast.forecast;

    if (historical.length === 0 || forecast.length === 0) return;

    const labels = [...historical.map((h) => monthLabel(h.month)), ...forecast.map((f) => monthLabel(f.month))];
    const historicValues = [...historical.map((h) => h.revenue), ...forecast.map(() => null)];
    const forecastValues = [...historical.map(() => null), ...forecast.map((f) => f.forecast_revenue)];
    const upperBounds = [...historical.map(() => null), ...forecast.map((f) => f.upper_bound)];
    const lowerBounds = [...historical.map(() => null), ...forecast.map((f) => f.lower_bound)];

    new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Actual",
                    data: historicValues,
                    borderColor: chartColors.accent,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: chartColors.accentLight,
                },
                {
                    label: "Forecast",
                    data: forecastValues,
                    borderColor: chartColors.green,
                    borderDash: [6, 4],
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: chartColors.green,
                },
                {
                    label: "Upper",
                    data: upperBounds,
                    borderColor: "transparent",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    fill: "+1",
                    pointRadius: 0,
                },
                {
                    label: "Lower",
                    data: lowerBounds,
                    borderColor: "transparent",
                    backgroundColor: "transparent",
                    pointRadius: 0,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { position: "top", align: "end" },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: {
                        label: (ctx) => {
                            if (ctx.dataset.label === "Upper" || ctx.dataset.label === "Lower") return null;
                            return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`;
                        },
                    },
                },
            },
            scales: {
                x: { grid: { color: chartColors.grid } },
                y: {
                    grid: { color: chartColors.grid },
                    ticks: { callback: (value) => formatCurrencyCompact(value) },
                },
            },
        },
    });
}

/* ---------- Region bar chart (revenue / profit / units) ---------- */

function renderRegionChart(records) {
    const canvas = document.getElementById("region-chart");
    if (!canvas || !records.length) return;

    const chart = Chart.getChart("region-chart");
    if (chart) chart.destroy();

    const labels = records.map((r) => r.region);

    new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Revenue",
                    data: records.map((r) => r.total_revenue),
                    backgroundColor: "rgba(99, 102, 241, 0.8)",
                    borderRadius: 6,
                },
                {
                    label: "Profit",
                    data: records.map((r) => r.total_profit),
                    backgroundColor: "rgba(16, 185, 129, 0.8)",
                    borderRadius: 6,
                },
                {
                    label: "Units",
                    data: records.map((r) => r.total_quantity),
                    backgroundColor: "rgba(245, 158, 11, 0.8)",
                    borderRadius: 6,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "top", align: "end" },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: {
                        label: (ctx) => {
                            if (ctx.dataset.label === "Units") {
                                return ` Units: ${formatNumber(ctx.raw)}`;
                            }
                            return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`;
                        },
                    },
                },
            },
            scales: {
                x: { grid: { color: chartColors.grid } },
                y: {
                    grid: { color: chartColors.grid },
                    ticks: { callback: (value) => formatCurrencyCompact(value) },
                },
            },
        },
    });
}

/* ---------- Doughnut chart ---------- */

function renderPieChart(canvasId, records, labelKey, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !records.length) return;

    const chart = Chart.getChart(canvasId);
    if (chart) chart.destroy();

    const labels = records.map((r) => r[labelKey]);
    const values = records.map((r) => r.total_revenue);

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: "#151c2c",
                borderWidth: 3,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "62%",
            plugins: {
                legend: { position: "bottom" },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: {
                        label: (ctx) => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.raw / total) * 100).toFixed(1);
                            return ` ${ctx.label}: ${formatCurrency(ctx.raw)} (${pct}%)`;
                        },
                    },
                },
            },
        },
    });
}

/* ---------- Overview charts ---------- */

function renderOverViewCharts() {
    renderTrendChart("revenue-trend-chart", state.trend);
    renderForecastChart();
    renderRegionChart(state.regionPerformance);
    renderPieChart("category-chart", state.categoryPerformance, "category", [chartColors.purple, chartColors.cyan]);
}

/* ---------- Analytics table ---------- */

function renderAnalyticsTable(records, labelKey) {
    const tbody = document.getElementById("analytics-table-body");
    if (!records || records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="table-loading">No data available.</td></tr>';
        return;
    }

    tbody.innerHTML = records
        .map(
            (record, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${record[labelKey]}</strong></td>
                    <td>${formatCurrency(record.total_revenue)}</td>
                    <td>${formatCurrency(record.total_profit)}</td>
                    <td>${formatNumber(record.total_quantity)}</td>
                    <td>${formatNumber(record.total_records)}</td>
                    <td>${record.profit_margin.toFixed(1)}%</td>
                </tr>
            `
        )
        .join("");
}

/* ---------- Analytics trend chart ---------- */

function renderAnalyticsTrendChart() {
    if (!state.trend.length) return;
    renderTrendChart("analytics-trend-chart", state.trend);
}

/* ---------- Forecast page ---------- */

async function renderForecastPage() {
    try {
        const forecast = await fetchJson(`/api/forecast?periods=${state.forecastPeriods}`);
        state.forecast = forecast;

        const historical = forecast.historical;
        const next = forecast.forecast[0];
        const total = forecast.forecast.reduce((sum, f) => sum + f.forecast_revenue, 0);

        document.getElementById("forecast-next").textContent = formatCurrencyCompact(next.forecast_revenue);
        document.getElementById("forecast-next-range").textContent =
            `Range: ${formatCurrencyCompact(next.lower_bound)} – ${formatCurrencyCompact(next.upper_bound)}`;

        document.getElementById("forecast-total").textContent = formatCurrencyCompact(total);
        document.getElementById("forecast-total-period").textContent =
            `over ${state.forecastPeriods} months`;

        const lastHistorical = historical[historical.length - 1];
        const growth = ((next.forecast_revenue - lastHistorical.revenue) / lastHistorical.revenue) * 100;

        document.getElementById("forecast-growth").textContent = `${growth >= 0 ? "+" : ""}${growth.toFixed(1)}%`;
        document.getElementById("forecast-growth").style.color = growth >= 0 ? "#10b981" : "#ef4444";

        renderForecastPageChart(historical, forecast.forecast);
        renderForecastTable(forecast.forecast);
    } catch (error) {
        console.error("Failed to load forecast:", error);
    }
}

function renderForecastTable(forecast) {
    const tbody = document.getElementById("forecast-table-body");
    if (!forecast || forecast.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="table-loading">No forecast available.</td></tr>';
        return;
    }

    tbody.innerHTML = forecast
        .map(
            (f) => `
                <tr>
                    <td><strong>${monthLabel(f.month)}</strong></td>
                    <td>${formatCurrency(f.forecast_revenue)}</td>
                    <td>${formatCurrency(f.lower_bound)}</td>
                    <td>${formatCurrency(f.upper_bound)}</td>
                </tr>
            `
        )
        .join("");
}

function renderForecastPageChart(historical, forecast) {
    const canvas = document.getElementById("forecast-page-chart");
    if (!canvas) return;

    const chart = Chart.getChart("forecast-page-chart");
    if (chart) chart.destroy();

    const labels = [
        ...historical.slice(-18).map((h) => monthLabel(h.month)),
        ...forecast.map((f) => monthLabel(f.month)),
    ];

    const historicValues = [
        ...historical.slice(-18).map((h) => h.revenue),
        ...forecast.map(() => null),
    ];

    const forecastValues = [
        ...historical.slice(-18).map(() => null),
        ...forecast.map((f) => f.forecast_revenue),
    ];

    const upperBounds = [
        ...historical.slice(-18).map(() => null),
        ...forecast.map((f) => f.upper_bound),
    ];

    const lowerBounds = [
        ...historical.slice(-18).map(() => null),
        ...forecast.map((f) => f.lower_bound),
    ];

    new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Actual",
                    data: historicValues,
                    borderColor: chartColors.accent,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: chartColors.accentLight,
                },
                {
                    label: "Forecast",
                    data: forecastValues,
                    borderColor: chartColors.green,
                    borderDash: [6, 4],
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: chartColors.green,
                },
                {
                    label: "Confidence Upper",
                    data: upperBounds,
                    borderColor: "transparent",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    fill: "+1",
                    pointRadius: 0,
                    tension: 0.4,
                },
                {
                    label: "Confidence Lower",
                    data: lowerBounds,
                    borderColor: "transparent",
                    backgroundColor: "transparent",
                    pointRadius: 0,
                    tension: 0.4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { position: "top", align: "end" },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: {
                        label: (ctx) => {
                            if (ctx.dataset.label.startsWith("Confidence")) return null;
                            return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`;
                        },
                    },
                },
            },
            scales: {
                x: { grid: { color: chartColors.grid } },
                y: {
                    grid: { color: chartColors.grid },
                    ticks: { callback: (value) => formatCurrencyCompact(value) },
                },
            },
        },
    });
}

/* ---------- AI Analyst chat ---------- */

function addChatMessage(role, text) {
    const messages = document.getElementById("chat-messages");
    const message = document.createElement("div");
    message.className = `chat-message ${role}`;

    const avatarIcon =
        role === "user"
            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a8 8 0 0 1 16 0v1"/></svg>'
            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a7 7 0 0 1 7 7c0 2.4-1.2 4.5-3 5.7V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.3C6.2 13.5 5 11.4 5 9a7 7 0 0 1 7-7z"/><path d="M9 21h6"/></svg>';

    message.innerHTML = `
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-content">
            <p></p>
        </div>
    `;

    message.querySelector("p").textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
}

async function askAnalyst(question) {
    if (!question.trim()) return;

    addChatMessage("user", question);

    const input = document.getElementById("chat-input");
    input.value = "";

    // Show a temporary "typing" state
    const messages = document.getElementById("chat-messages");
    const typing = document.createElement("div");
    typing.className = "chat-message assistant";
    typing.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a7 7 0 0 1 7 7c0 2.4-1.2 4.5-3 5.7V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.3C6.2 13.5 5 11.4 5 9a7 7 0 0 1 7-7z"/><path d="M9 21h6"/></svg>
        </div>
        <div class="message-content"><p>Analyzing your data…</p></div>
    `;
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;

    try {
        const response = await fetchJson("/api/analyst/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        typing.querySelector("p").textContent = response.answer;

        // Append verified data insights as chips for insight tool
        if (response.data && Array.isArray(response.data) && response.data.length > 0 && response.data[0].message) {
            const insightsDiv = document.createElement("div");
            insightsDiv.className = "verified-insights";
            insightsDiv.innerHTML = response.data
                .map(
                    (insight) => `
                        <div class="insight-item">
                            <div class="insight-title">${insight.title}</div>
                            <div class="insight-message">${insight.message}</div>
                        </div>
                    `
                )
                .join("");
            typing.querySelector(".message-content").appendChild(insightsDiv);
        }

        // Append recommendations as a list
        if (response.data && Array.isArray(response.data) && response.data.length > 0 && typeof response.data[0] === "string") {
            const recDiv = document.createElement("div");
            recDiv.className = "verified-insights";
            recDiv.innerHTML = response.data
                .map((rec) => `<div class="insight-item"><div class="insight-message">• ${rec}</div></div>`)
                .join("");
            typing.querySelector(".message-content").appendChild(recDiv);
        }
    } catch (error) {
        typing.querySelector("p").textContent = `Sorry, I couldn't process that: ${error.message}`;
    }

    messages.scrollTop = messages.scrollHeight;
}

/* ---------- Data Loading ---------- */

async function loadAllData() {
    try {
        const [summary, product, region, category, insights, trend, forecast, anomalySummary, bigData] =
            await Promise.all([
                fetchJson("/api/summary"),
                fetchJson("/api/performance/product"),
                fetchJson("/api/performance/region"),
                fetchJson("/api/performance/category"),
                fetchJson("/api/insights"),
                fetchJson("/api/trends/revenue"),
                fetchJson(`/api/forecast?periods=${state.forecastPeriods}`),
                fetchJson("/api/anomalies/summary"),
                fetchJson("/api/big-data/analyze"),
            ]);

        state.summary = summary;
        state.productPerformance = product;
        state.regionPerformance = region;
        state.categoryPerformance = category;
        state.insights = insights;
        state.trend = trend;
        state.forecast = forecast;
        state.anomalies.summary = anomalySummary;
        state.bigData = bigData;

        renderKpis(summary);
        renderProductTable(product);
        renderInsights(insights);
        renderOverViewCharts();
        renderAnalyticsTable(product, "product");
        renderAnalyticsTrendChart();
        renderAnomalyKPIs();
        renderBigDataKPIs();
    } catch (error) {
        console.error("Failed to load data:", error);
        document.getElementById("insights-list").innerHTML =
            `<div class="insight-loading">Error loading data: ${error.message}</div>`;
    }
}

async function loadForecastWithPeriods() {
    try {
        const forecast = await fetchJson(`/api/forecast?periods=${state.forecastPeriods}`);
        state.forecast = forecast;
        renderOverViewCharts();
        renderForecastPage();
    } catch (error) {
        console.error("Failed to load forecast:", error);
    }
}

/* ---------- Anomaly Detection ---------- */

function renderAnomalyKPIs() {
    const summary = state.anomalies.summary;
    if (!summary || Object.keys(summary).length === 0) return;

    document.getElementById("anomaly-total").textContent = summary.total_anomalies ?? 0;
    document.getElementById("anomaly-total-sub").textContent = "detected";
    document.getElementById("anomaly-high").textContent = summary.high_severity ?? 0;
    document.getElementById("anomaly-high-sub").textContent = "needs attention";
    document.getElementById("anomaly-txn").textContent = summary.transaction_anomalies ?? 0;
    document.getElementById("anomaly-txn-sub").textContent = "unusual sales";
    document.getElementById("anomaly-ts").textContent = summary.time_series_anomalies ?? 0;
    document.getElementById("anomaly-ts-sub").textContent = "revenue spikes/drops";
}

async function loadAnomalies() {
    try {
        const anomalies = await fetchJson("/api/anomalies");
        state.anomalies = anomalies;
        renderAnomalyKPIs();
        renderAnomaliesPage();
    } catch (error) {
        console.error("Failed to load anomalies:", error);
    }
}

function renderAnomaliesPage() {
    const anomalies = state.anomalies;
    if (!anomalies) return;

    const all = [];

    for (const tx of anomalies.transactions || []) {
        all.push({
            ...tx,
            display_type: "Transaction",
            display_label: tx.context ? `${tx.context.product} · ${tx.context.region}` : "—",
        });
    }

    for (const ts of anomalies.time_series || []) {
        all.push({
            ...ts,
            display_type: "Time-Series",
            display_label: ts.context ? ts.context.month : "—",
        });
    }

    for (const dim of (anomalies.dimensions && anomalies.dimensions.product) || []) {
        all.push({ ...dim, display_type: "Dimension (Product)", display_label: dim.context ? dim.context.product : "—" });
    }
    for (const dim of (anomalies.dimensions && anomalies.dimensions.region) || []) {
        all.push({ ...dim, display_type: "Dimension (Region)", display_label: dim.context ? dim.context.region : "—" });
    }
    for (const dim of (anomalies.dimensions && anomalies.dimensions.category) || []) {
        all.push({ ...dim, display_type: "Dimension (Category)", display_label: dim.context ? dim.context.category : "—" });
    }

    all.sort((a, b) => {
        const order = { high: 0, medium: 1, low: 2, info: 3 };
        return (order[a.severity] || 99) - (order[b.severity] || 99);
    });

    const tbody = document.getElementById("anomaly-table-body");
    if (!all.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="table-loading">No anomalies detected.</td></tr>';
    } else {
        tbody.innerHTML = all
            .map(
                (a) => `
                <tr>
                    <td><span class="severity-badge severity-${a.severity}">${a.severity}</span></td>
                    <td><span class="anomaly-type-badge anomaly-type-${a.type.replace(/\s/g, "_")}">${a.display_type}</span></td>
                    <td>${a.description}</td>
                    <td>${formatCurrencyCompact(a.actual_value)}</td>
                    <td>${formatCurrencyCompact(a.expected_value)}</td>
                    <td class="${a.deviation_pct >= 0 ? "deviation-positive" : "deviation-negative"}">${a.deviation_pct >= 0 ? "+" : ""}${a.deviation_pct}%</td>
                </tr>
            `
            )
            .join("");
    }

    renderAnomalyChart(anomalies);
}

function renderAnomalyChart(anomalies) {
    const canvas = document.getElementById("anomaly-chart");
    if (!canvas) return;

    const chart = Chart.getChart("anomaly-chart");
    if (chart) chart.destroy();

    const tsAnomalies = anomalies.time_series || [];
    const labels = tsAnomalies.map((a) => (a.context && a.context.month ? a.context.month : "—"));
    const values = tsAnomalies.map((a) => a.actual_value);
    const expected = tsAnomalies.map((a) => a.expected_value);

    new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Actual Revenue",
                    data: values,
                    backgroundColor: values.map((v, i) => {
                        const sev = tsAnomalies[i]?.severity;
                        return sev === "high" ? "#ef4444" : sev === "medium" ? "#f59e0b" : "rgba(99, 102, 241, 0.6)";
                    }),
                    borderRadius: 6,
                },
                {
                    label: "Expected (Average)",
                    data: expected,
                    backgroundColor: "rgba(148, 163, 184, 0.2)",
                    borderRadius: 6,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "top", align: "end" },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: {
                        label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`,
                    },
                },
            },
            scales: {
                x: { grid: { color: chartColors.grid } },
                y: {
                    grid: { color: chartColors.grid },
                    ticks: { callback: (value) => formatCurrencyCompact(value) },
                },
            },
        },
    });
}

/* ---------- Big Data Analysis ---------- */

function renderBigDataKPIs() {
    const bd = state.bigData;
    if (!bd) return;

    document.getElementById("bd-rows").textContent = bd.rows?.toLocaleString("en-IN") ?? "–";
    document.getElementById("bd-rows-sub").textContent = "records";
    document.getElementById("bd-memory").textContent = `${bd.memory_mb ?? 0} MB`;
    document.getElementById("bd-memory-sub").textContent = "in memory";
    document.getElementById("bd-strategy").textContent = (bd.strategy ?? "unknown").charAt(0).toUpperCase() + (bd.strategy ?? "unknown").slice(1);
    document.getElementById("bd-strategy-sub").textContent = "recommended";
    document.getElementById("bd-nulls").textContent = bd.total_nulls ?? 0;
    document.getElementById("bd-nulls-sub").textContent = "missing values";
}

async function loadBigData() {
    try {
        const bigData = await fetchJson("/api/big-data/analyze");
        state.bigData = bigData;
        renderBigDataKPIs();
        renderBigDataPage();
    } catch (error) {
        console.error("Failed to load big data analysis:", error);
    }
}

function renderBigDataPage() {
    const bd = state.bigData;
    if (!bd) return;

    const strategyEl = document.getElementById("bd-strategy");
    if (strategyEl) {
        strategyEl.className = "kpi-value strategy-badge strategy-" + (bd.strategy || "full");
    }

    const recBody = document.getElementById("bd-recommendations-body");
    const recommendations = [];

    if (bd.strategy === "sampled") {
        recommendations.push({ text: `Sample dataset to ${bd.recommended_sample_rows?.toLocaleString("en-IN") ?? "10,000"} rows for visualization.`, type: "info" });
    }
    if (bd.strategy === "chunked") {
        recommendations.push({ text: "Use chunked aggregation for large-scale grouping operations.", type: "info" });
    }
    if (bd.total_nulls > 0) {
        recommendations.push({ text: `${bd.total_nulls} null values detected — handle before downstream analysis.`, type: "warn" });
    }
    if (bd.duplicate_rows > 0) {
        recommendations.push({ text: `${bd.duplicate_rows} duplicate rows found — consider deduplication.`, type: "warn" });
    }
    if (bd.memory_mb > 100) {
        recommendations.push({ text: `High memory usage (${bd.memory_mb} MB) — monitor during processing.`, type: "info" });
    }
    if (recommendations.length === 0) {
        recommendations.push({ text: "Dataset is well-sized for full in-memory processing.", type: "info" });
    }

    recBody.innerHTML = recommendations
        .map(
            (r, i) => `
            <tr>
                <td>${i + 1}</td>
                <td>${r.text}</td>
                <td><span class="severity-badge severity-${r.type === "warn" ? "high" : "low"}">${r.type}</span></td>
            </tr>
        `
        )
        .join("");

    renderColumnTypesChart(bd);
    renderNullsChart(bd);
    renderColumnProfilesTable(bd);
}

function renderColumnTypesChart(bd) {
    const canvas = document.getElementById("bd-column-types-chart");
    if (!canvas) return;

    const chart = Chart.getChart("bd-column-types-chart");
    if (chart) chart.destroy();

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Numeric", "DateTime", "Categorical"],
            datasets: [{
                data: [bd.numeric_columns ?? 0, bd.datetime_columns ?? 0, bd.categorical_columns ?? 0],
                backgroundColor: [chartColors.accent, chartColors.success, chartColors.amber],
                borderColor: "#151c2c",
                borderWidth: 3,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "62%",
            plugins: {
                legend: { position: "bottom" },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw} columns` },
                },
            },
        },
    });
}

function renderNullsChart(bd) {
    const canvas = document.getElementById("bd-nulls-chart");
    if (!canvas) return;

    const chart = Chart.getChart("bd-nulls-chart");
    if (chart) chart.destroy();

    const profiles = bd.column_profiles || [];
    const topNulls = profiles.filter((p) => p.null_count > 0).sort((a, b) => b.null_count - a.null_count).slice(0, 8);

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: topNulls.map((p) => p.name),
            datasets: [{
                label: "Null Count",
                data: topNulls.map((p) => p.null_count),
                backgroundColor: "rgba(239, 68, 68, 0.6)",
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    ...chartTooltipOptions(),
                    callbacks: { label: (ctx) => ` ${ctx.raw} null values` },
                },
            },
            scales: {
                x: { grid: { color: chartColors.grid } },
                y: { grid: { color: chartColors.grid }, beginAtZero: true, ticks: { stepSize: 1 } },
            },
        },
    });
}

function renderColumnProfilesTable(bd) {
    const tbody = document.getElementById("bd-columns-body");
    const profiles = bd.column_profiles || [];

    if (!profiles.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="table-loading">No column profiles available.</td></tr>';
        return;
    }

    tbody.innerHTML = profiles
        .map(
            (p) => `
            <tr>
                <td><strong>${p.name}</strong></td>
                <td>${p.dtype}</td>
                <td>${p.null_count}</td>
                <td>${p.unique_count}</td>
                <td>${(p.unique_ratio * 100).toFixed(1)}%</td>
                <td>${p.is_high_cardinality ? "Yes" : "No"}</td>
            </tr>
        `
        )
        .join("");
}

/* ---------- Event Listeners ---------- */

document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => switchPage(btn.dataset.page));
});

document.getElementById("global-search").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        const question = event.target.value.trim();
        if (question) {
            switchPage("analyst");
            window.setTimeout(() => askAnalyst(question), 200);
        }
    }
});

document.getElementById("file-upload").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const result = await fetchJson("/api/dataset/upload", {
            method: "POST",
            body: formData,
        });

        document.getElementById("dataset-label").textContent = `${result.rows.toLocaleString("en-IN")} rows from ${file.name}`;
        await loadAllData();
        await loadDatasetInfo();
    } catch (error) {
        alert(`Upload failed: ${error.message}`);
    }
});

document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.analyticsTab = btn.dataset.tab;

        const key = btn.dataset.tab;
        const records = state[`${key}Performance`];
        renderAnalyticsTable(records, key);
    });
});

document.querySelectorAll(".period-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".period-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.forecastPeriods = Number(btn.dataset.periods);
        loadForecastWithPeriods();
    });
});

document.querySelectorAll(".suggestion-chip").forEach((chip) => {
    chip.addEventListener("click", () => askAnalyst(chip.dataset.question));
});

document.getElementById("chat-send").addEventListener("click", () => {
    askAnalyst(document.getElementById("chat-input").value);
});

document.getElementById("chat-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        askAnalyst(event.target.value);
    }
});

/* ---------- Boot ---------- */

document.addEventListener("DOMContentLoaded", () => {
    loadDatasetInfo();
    loadAllData();
});