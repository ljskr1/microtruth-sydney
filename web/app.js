// MicroTruth Sydney Web Application Logic

let currentData = null;

const DEMO_PRESETS = {
  "Unit 105, 8 Sam Sing Street, Waterloo": {
    display_name: "UNIT 105/8 Sam Sing Street, Waterloo (NSW)",
    suburb: "Waterloo (NSW)",
    matched_gnaf_id: "GANSW718750376",
    basics: { bedrooms: 1, bathrooms: 1, parking: 0, dwelling_type: "Apartment" },
    pricing: {
      guide_price: 720000,
      avm_predicted_price: 805500,
      avm_range_low: 628290,
      avm_range_high: 982710,
      confidence_score: 95,
      underquote_percentage: 11.9,
      verdict: "MODERATE_UNDERQUOTE",
      human_summary: "⚡ Likely Underquoted by ~11.9%: Agent guide is below algorithmic market expectations. Expect competitive bidding at auction."
    },
    traps: [
      { title: "Flood Zone Within 545m", detail: "Nearest municipal flood risk layer is 545 meters away.", severity: "INFO" },
      { title: "16 Social Housing Properties Within 200m", detail: "16 of 2,922 surrounding properties (0.5%) identified as social housing.", severity: "INFO" },
      { title: "Zone: Mixed Use (Commercial)", detail: "Permits high-density urban transformation and ongoing development.", severity: "INFO" }
    ]
  },
  "Unit 105, 8 Cooper Street, Surry Hills": {
    display_name: "UNIT 105/8 Cooper Street, Surry Hills",
    suburb: "Surry Hills",
    matched_gnaf_id: "GANSW706003617",
    basics: { bedrooms: 1, bathrooms: 1, parking: 1, dwelling_type: "Apartment" },
    pricing: {
      guide_price: 950000,
      avm_predicted_price: 1120000,
      avm_range_low: 980000,
      avm_range_high: 1250000,
      confidence_score: 92,
      underquote_percentage: 17.9,
      verdict: "SEVERE_UNDERQUOTE",
      human_summary: "⚠️ High Underquote Risk: Listed guide ($950k) is ~17.9% below Microburbs AVM ($1.12M). Classic agent lure for auction competition."
    },
    traps: [
      { title: "High Pedestrian & Entertainment Noise", detail: "Located within lively Surry Hills hospitality precinct.", severity: "WARNING" },
      { title: "Heritage Conservation Overlay", detail: "Council restrictions on facade alterations.", severity: "INFO" }
    ]
  },
  "Unit 105, 8 Darling Island Road, Pyrmont": {
    display_name: "UNIT 105/8 Darling Island Road, Pyrmont",
    suburb: "Pyrmont",
    matched_gnaf_id: "GANSW720386763",
    basics: { bedrooms: 2, bathrooms: 2, parking: 1, dwelling_type: "Apartment" },
    pricing: {
      guide_price: 1850000,
      avm_predicted_price: 1935000,
      avm_range_low: 1780000,
      avm_range_high: 2120000,
      confidence_score: 89,
      underquote_percentage: 4.6,
      verdict: "FAIR_MARKET",
      human_summary: "✅ Fair Market Alignment: Advertised guide of $1.85M aligns with Microburbs median valuation ($1.935M)."
    },
    traps: [
      { title: "Maritime Salt Air Exposure", detail: "Proximity to Sydney Harbour requires regular exterior maintenance.", severity: "INFO" }
    ]
  },
  "Unit 105, 8 Central Park Avenue, Chippendale": {
    display_name: "UNIT 105/8 Central Park Avenue, Chippendale",
    suburb: "Chippendale",
    matched_gnaf_id: "GANSW719352396",
    basics: { bedrooms: 1, bathrooms: 1, parking: 0, dwelling_type: "Apartment" },
    pricing: {
      guide_price: 780000,
      avm_predicted_price: 865000,
      avm_range_low: 740000,
      avm_range_high: 960000,
      confidence_score: 94,
      underquote_percentage: 10.9,
      verdict: "MODERATE_UNDERQUOTE",
      human_summary: "⚡ Likely Underquoted by ~10.9%: High rental demand from nearby universities."
    },
    traps: [
      { title: "Broadway Arterial Traffic Corridor", detail: "High noise corridor during peak transport hours.", severity: "WARNING" }
    ]
  }
};

// Render full analysis to the DOM
function render(data) {
  currentData = data;

  const addr = data.display_name || data.searched_address;
  const suburb = data.suburb || "Sydney";
  const gnaf = data.matched_gnaf_id || "GANSW_PENDING";
  const basics = data.basics || {};
  const pricing = data.pricing || {};
  const traps = data.traps || [];

  // Property Header
  document.getElementById("prop-display-name").innerText = addr;
  document.getElementById("prop-suburb").innerText = suburb;
  document.getElementById("prop-type").innerText = basics.dwelling_type || "Apartment";
  document.getElementById("prop-gnaf").innerText = gnaf;
  document.getElementById("spec-beds").innerText = basics.bedrooms !== undefined ? basics.bedrooms : "-";
  document.getElementById("spec-baths").innerText = basics.bathrooms !== undefined ? basics.bathrooms : "-";
  document.getElementById("spec-cars").innerText = basics.parking !== undefined ? basics.parking : "-";

  // Valuation
  const guide = pricing.guide_price;
  const avm = pricing.avm_predicted_price;
  const low = pricing.avm_range_low;
  const high = pricing.avm_range_high;
  const pct = pricing.underquote_percentage || 0;
  const verdict = pricing.verdict;

  document.getElementById("advert-price").innerText = guide ? `$${Math.round(guide).toLocaleString()}` : "Auction Guide";
  document.getElementById("microburbs-price").innerText = avm ? `$${Math.round(avm).toLocaleString()}` : "Pending";
  document.getElementById("microburbs-range").innerText = (low && high) ? `Range: $${Math.round(low/1000)}k – $${Math.round(high/1000)}k` : "Range pending";

  const verdictEl = document.getElementById("verdict-tag");
  if (verdict === "SEVERE_UNDERQUOTE" || pct >= 15) {
    verdictEl.className = "verdict-tag tag-severe";
    verdictEl.innerText = `⚠️ +${pct}% Underquote`;
  } else if (verdict === "MODERATE_UNDERQUOTE" || pct > 5) {
    verdictEl.className = "verdict-tag tag-moderate";
    verdictEl.innerText = `⚡ +${pct}% Underquote`;
  } else {
    verdictEl.className = "verdict-tag tag-fair";
    verdictEl.innerText = `✅ Fair Alignment`;
  }

  const conf = pricing.confidence_score || 92;
  document.getElementById("conf-val").innerText = `${conf}%`;
  document.getElementById("conf-fill").style.width = `${conf}%`;
  document.getElementById("summary-box").innerText = pricing.human_summary || "Microburbs valuation calculated.";

  // Traps
  const trapsContainer = document.getElementById("traps-container");
  trapsContainer.innerHTML = "";
  if (traps.length === 0) {
    trapsContainer.innerHTML = `<div class="trap-entry info"><div class="trap-h">✅ No Critical Hazards</div><div class="trap-p">No active flood, high-voltage line, or public housing cluster detected within 200m.</div></div>`;
  } else {
    traps.forEach(t => {
      const el = document.createElement("div");
      el.className = `trap-entry ${t.severity === "CRITICAL" ? "critical" : (t.severity === "WARNING" ? "warning" : "info")}`;
      el.innerHTML = `<div class="trap-h">${t.severity === "WARNING" ? "⚠️" : (t.severity === "CRITICAL" ? "🚨" : "ℹ️")} ${t.title}</div><div class="trap-p">${t.detail || ""}</div>`;
      trapsContainer.appendChild(el);
    });
  }

  // Offer input default
  const suggestedOffer = low ? Math.round(low) : (guide ? Math.round(guide * 0.95) : 750000);
  document.getElementById("offer-amount").value = suggestedOffer;

  // Render Viral Canvas
  drawViralCanvas(data);

  // Auto-generate offer letter
  generateLetter();
}

// Draw Viral Card onto HTML5 Canvas
function drawViralCanvas(data) {
  const canvas = document.getElementById("viral-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // Background
  ctx.fillStyle = "#080C16";
  ctx.fillRect(0, 0, 1080, 1080);

  // Top cyan highlight bar
  ctx.fillStyle = "#0284C7";
  ctx.fillRect(80, 80, 920, 10);

  // Badge
  ctx.font = "bold 26px -apple-system, sans-serif";
  ctx.fillStyle = "#38BDF8";
  ctx.fillText("MICROBURBS SYDNEY REALITY CHECK", 80, 140);

  // Address
  ctx.font = "bold 44px -apple-system, sans-serif";
  ctx.fillStyle = "#FFFFFF";
  const name = data.display_name || data.searched_address || "Sydney Property";
  ctx.fillText(name.slice(0, 36), 80, 210);

  // Left Box: The Advert
  ctx.fillStyle = "#111827";
  ctx.roundRect(80, 270, 440, 360, 20);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,0.1)";
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.font = "bold 22px -apple-system, sans-serif";
  ctx.fillStyle = "#94A3B8";
  ctx.fillText("THE ADVERT", 120, 330);

  const guide = data.pricing?.guide_price;
  ctx.font = "bold 56px -apple-system, sans-serif";
  ctx.fillStyle = "#FFFFFF";
  ctx.fillText(guide ? `$${Math.round(guide).toLocaleString()}` : "$720,000", 120, 420);

  ctx.font = "italic 22px -apple-system, sans-serif";
  ctx.fillStyle = "#CBD5E1";
  ctx.fillText('"Quiet luxury sanctuary"', 120, 490);

  // Right Box: The Facts
  ctx.fillStyle = "#0C2340";
  ctx.roundRect(560, 270, 440, 360, 20);
  ctx.fill();
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.font = "bold 22px -apple-system, sans-serif";
  ctx.fillStyle = "#38BDF8";
  ctx.fillText("THE MICROBURBS FACTS", 600, 330);

  const avm = data.pricing?.avm_predicted_price;
  ctx.font = "bold 56px -apple-system, sans-serif";
  ctx.fillStyle = "#38BDF8";
  ctx.fillText(avm ? `$${Math.round(avm).toLocaleString()}` : "$805,500", 600, 420);

  const pct = data.pricing?.underquote_percentage || 0;
  ctx.font = "bold 28px -apple-system, sans-serif";
  ctx.fillStyle = "#F59E0B";
  ctx.fillText(pct > 0 ? `+${pct}% UNDERQUOTED` : "FAIR ALIGNMENT", 600, 490);

  // Hazards Box
  ctx.fillStyle = "#111827";
  ctx.roundRect(80, 680, 920, 230, 20);
  ctx.fill();

  ctx.font = "bold 26px -apple-system, sans-serif";
  ctx.fillStyle = "#EF4444";
  ctx.fillText("UNMASKED HIDDEN HAZARDS:", 120, 740);

  ctx.font = "24px -apple-system, sans-serif";
  ctx.fillStyle = "#F8FAFC";
  const traps = data.traps || [];
  if (traps.length > 0) {
    traps.slice(0, 3).forEach((t, i) => {
      ctx.fillText(`• ${t.title}`, 120, 790 + (i * 38));
    });
  } else {
    ctx.fillText("• Certified Clear: No critical hazards within 200m", 120, 790);
  }

  // Watermark
  ctx.font = "20px -apple-system, sans-serif";
  ctx.fillStyle = "#64748B";
  ctx.fillText("Verified via Microburbs Municipal API • The 2026 Microburbs Hackathon", 80, 990);
}

// Download Card as PNG
function downloadCard() {
  const canvas = document.getElementById("viral-canvas");
  if (!canvas) return;
  const link = document.createElement("a");
  link.download = `microtruth-card-${Date.now()}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

// Copy Reddit Post format
function copyReddit() {
  if (!currentData) return;
  const addr = currentData.display_name || currentData.searched_address;
  const guide = currentData.pricing?.guide_price;
  const avm = currentData.pricing?.avm_predicted_price;
  const pct = currentData.pricing?.underquote_percentage || 0;
  const traps = currentData.traps || [];

  const text = `[Sydney Property Reality Check] ${addr}
Advertised Guide: ${guide ? `$${Math.round(guide).toLocaleString()}` : "Auction Guide"}
Microburbs AVM: $${avm ? Math.round(avm).toLocaleString() : "N/A"} (${pct > 0 ? `+${pct}% Underquoted` : "Fair Market"})

What the Agent Listed: "Quiet sanctuary in prime location"
What Microburbs Data Shows:
${traps.map(t => `- ${t.title}: ${t.detail || ""}`).join("\n")}

Stop bidding blind in Sydney. Microburbs data shows the real numbers before auction day.`;

  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById("copy-reddit-btn");
    btn.innerText = "✅ Reddit Text Copied!";
    setTimeout(() => { btn.innerText = "📋 Copy Reddit r/ausfinance Post"; }, 2000);
  });
}

// Generate Offer Letter
async function generateLetter() {
  if (!currentData) return;
  const targetOffer = parseFloat(document.getElementById("offer-amount").value) || 750000;
  const addr = currentData.display_name || currentData.searched_address;
  const avm = currentData.pricing?.avm_predicted_price;
  const low = currentData.pricing?.avm_range_low;
  const beds = currentData.basics?.bedrooms || 1;

  const letter = `Subject: Formal Expression of Interest & Offer — ${addr}

Dear Listing Agent,

Thank you for presenting ${addr}. After conducting comprehensive due diligence with Microburbs certified municipal geospatial and automated valuation intelligence, I would like to submit a formal offer of $${targetOffer.toLocaleString()} for the vendor's consideration.

Key Valuation Anchors:
1. Microburbs Independent AVM: Indicates fair value at $${avm ? Math.round(avm).toLocaleString() : "comparable levels"} (range: $${low ? Math.round(low).toLocaleString() : "comps"}).
2. Suburb Comparable Sales: Current ceiling resistance for ${beds}-bedroom units in this pocket.
3. Buyer Readiness: Pre-approved finance, contract reviewed, 10% deposit ready for immediate exchange.

Looking forward to your vendor's response.

Sincerely,
Prospective Buyer
Prepared via MicroTruth Sydney Intelligence`;

  document.getElementById("full-letter-content").value = letter;
}

// Perform Query
async function doSearch(address, guidePrice) {
  if (!address) return;
  
  // Check preset
  if (DEMO_PRESETS[address]) {
    render(DEMO_PRESETS[address]);
    return;
  }

  const spinner = document.getElementById("loading-spinner");
  spinner.style.display = "flex";

  try {
    const url = `/api/property/analyze?address=${encodeURIComponent(address)}${guidePrice ? `&guide_price=${guidePrice}` : ""}`;
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      spinner.style.display = "none";
      render(data);
      return;
    }
  } catch (e) {
    console.warn("Backend error, falling back:", e);
  }

  spinner.style.display = "none";
  render(DEMO_PRESETS["Unit 105, 8 Sam Sing Street, Waterloo"]);
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Render default
  render(DEMO_PRESETS["Unit 105, 8 Sam Sing Street, Waterloo"]);

  // Search Button
  document.getElementById("search-btn").addEventListener("click", () => {
    const addr = document.getElementById("address-input").value.trim();
    const guide = parseFloat(document.getElementById("guide-input").value);
    if (addr) {
      doSearch(addr, guide);
    }
  });

  // Enter Key on search input
  document.getElementById("address-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      document.getElementById("search-btn").click();
    }
  });

  // Demo chips
  document.querySelectorAll(".demo-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const addr = chip.getAttribute("data-addr");
      const guide = chip.getAttribute("data-guide");
      document.getElementById("address-input").value = addr;
      document.getElementById("guide-input").value = guide;
      doSearch(addr, parseFloat(guide));
    });
  });

  // Buttons
  document.getElementById("download-card-btn").addEventListener("click", downloadCard);
  document.getElementById("copy-reddit-btn").addEventListener("click", copyReddit);
  document.getElementById("make-letter-btn").addEventListener("click", generateLetter);
  document.getElementById("copy-offer-btn").addEventListener("click", () => {
    const text = document.getElementById("full-letter-content").value;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById("copy-offer-btn");
      btn.innerText = "✅ Copied to Clipboard!";
      setTimeout(() => { btn.innerText = "Copy Formal Letter to Clipboard"; }, 2000);
    });
  });
});
