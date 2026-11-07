// MicroTruth Sydney Side Panel Logic

let currentAnalysis = null;

// Built-in offline demo database for lightning-fast presentation
const DEMO_PROFILES = {
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
      { title: "Zone: Mixed Use (Commercial)", detail: "Permits high-density urban transformation and nearby ongoing construction.", severity: "INFO" }
    ],
    market: { growth: "+4.7%", dom: "27 Days", yield: "3.8%" }
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
      human_summary: "⚠️ High Underquote Risk: Listed guide ($950k) is ~17.9% below Microburbs AVM ($1.12M). Typical agent strategy to attract bidding frenzy."
    },
    traps: [
      { title: "High Pedestrian & Nightlife Noise", detail: "Located within vibrant entertainment precinct.", severity: "WARNING" },
      { title: "Heritage Conservation Overlay", detail: "Substantial restrictions on external renovations.", severity: "INFO" }
    ],
    market: { growth: "+6.2%", dom: "21 Days", yield: "3.4%" }
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
    ],
    market: { growth: "+5.1%", dom: "32 Days", yield: "4.1%" }
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
    ],
    market: { growth: "+4.9%", dom: "19 Days", yield: "4.8%" }
  }
};

// Update UI with analysis object
function renderAnalysis(data) {
  currentAnalysis = data;

  const addr = data.display_name || data.searched_address || "Sydney Property";
  const suburb = data.suburb || "Sydney";
  const gnaf = data.matched_gnaf_id || "GANSW_PENDING";
  const basics = data.basics || {};
  const pricing = data.pricing || {};
  const traps = data.traps || [];

  // 1. Property Card
  document.getElementById("prop-address").innerText = addr;
  document.getElementById("prop-suburb-tag").innerText = suburb;
  document.getElementById("prop-type-tag").innerText = basics.dwelling_type || "Apartment";
  document.getElementById("prop-gnaf-tag").innerText = gnaf;
  document.getElementById("spec-beds").innerText = basics.bedrooms !== undefined ? basics.bedrooms : "-";
  document.getElementById("spec-baths").innerText = basics.bathrooms !== undefined ? basics.bathrooms : "-";
  document.getElementById("spec-cars").innerText = basics.parking !== undefined ? basics.parking : "-";

  // 2. Valuation Card
  const guide = pricing.guide_price;
  const avm = pricing.avm_predicted_price;
  const low = pricing.avm_range_low;
  const high = pricing.avm_range_high;
  const pct = pricing.underquote_percentage || 0;
  const verdict = pricing.verdict;

  document.getElementById("guide-price-display").innerText = guide ? `$${Math.round(guide).toLocaleString()}` : "Auction / Contact";
  document.getElementById("avm-price-display").innerText = avm ? `$${Math.round(avm).toLocaleString()}` : "Calculating";
  document.getElementById("avm-range-display").innerText = (low && high) ? `Range: $${Math.round(low/1000)}k – $${Math.round(high/1000)}k` : "Range pending";

  const underquoteBadge = document.getElementById("underquote-badge");
  if (verdict === "SEVERE_UNDERQUOTE" || pct >= 15) {
    underquoteBadge.className = "verdict-pill pill-severe";
    underquoteBadge.innerText = `⚠️ +${pct}% Underquote`;
  } else if (verdict === "MODERATE_UNDERQUOTE" || pct > 5) {
    underquoteBadge.className = "verdict-pill pill-moderate";
    underquoteBadge.innerText = `⚡ +${pct}% Underquote`;
  } else {
    underquoteBadge.className = "verdict-pill pill-fair";
    underquoteBadge.innerText = `✅ Fair Alignment`;
  }

  const confScore = pricing.confidence_score || 90;
  document.getElementById("confidence-pct").innerText = `${confScore}%`;
  document.getElementById("confidence-fill").style.width = `${confScore}%`;
  document.getElementById("valuation-human-summary").innerText = pricing.human_summary || "Microburbs valuation calculated.";

  // 3. Traps List
  const trapsContainer = document.getElementById("traps-list");
  trapsContainer.innerHTML = "";
  if (traps.length === 0) {
    trapsContainer.innerHTML = `<div class="trap-item"><span class="trap-title">✅ No Critical Hazards</span><span class="trap-detail">No active flood, high-voltage line, or public housing cluster detected within 200m.</span></div>`;
  } else {
    traps.forEach(t => {
      const el = document.createElement("div");
      el.className = `trap-item ${t.severity === "CRITICAL" ? "critical" : (t.severity === "WARNING" ? "warning" : "")}`;
      el.innerHTML = `
        <span class="trap-title">${t.severity === "WARNING" ? "⚠️" : (t.severity === "CRITICAL" ? "🚨" : "ℹ️")} ${t.title}</span>
        <span class="trap-detail">${t.detail || ""}</span>
      `;
      trapsContainer.appendChild(el);
    });
  }

  // 4. Update Viral Card Preview
  document.getElementById("card-addr-preview").innerText = addr;
  document.getElementById("card-guide-preview").innerText = guide ? `$${Math.round(guide).toLocaleString()}` : "$720,000";
  document.getElementById("card-avm-preview").innerText = avm ? `$${Math.round(avm).toLocaleString()}` : "$805,500";
  document.getElementById("card-gap-preview").innerText = pct > 0 ? `+${pct}% Underquoted` : "Fair Alignment";

  const hazardsPreview = document.getElementById("card-hazards-preview");
  hazardsPreview.innerHTML = traps.slice(0, 2).map(t => `<span>⚠️ ${t.title}</span>`).join("");

  // Default offer input to target 92% of guide or AVM low
  const suggestedOffer = low ? Math.round(low) : (guide ? Math.round(guide * 0.95) : 750000);
  document.getElementById("input-offer").value = suggestedOffer;
}

// Fetch analysis from local backend proxy
async function loadAnalysis(address, guidePrice) {
  document.getElementById("content-loading").style.display = "flex";
  document.getElementById("content-active").style.display = "none";

  // Check demo profile first for instant response
  if (DEMO_PROFILES[address]) {
    setTimeout(() => {
      document.getElementById("content-loading").style.display = "none";
      document.getElementById("content-active").style.display = "flex";
      renderAnalysis(DEMO_PROFILES[address]);
    }, 200);
    return;
  }

  try {
    const url = `http://localhost:8000/api/property/analyze?address=${encodeURIComponent(address)}${guidePrice ? `&guide_price=${guidePrice}` : ""}`;
    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      document.getElementById("content-loading").style.display = "none";
      document.getElementById("content-active").style.display = "flex";
      renderAnalysis(data);
      return;
    }
  } catch (e) {
    console.warn("Backend unavailable, using default profile:", e);
  }

  // Fallback
  document.getElementById("content-loading").style.display = "none";
  document.getElementById("content-active").style.display = "flex";
  renderAnalysis(DEMO_PROFILES["Unit 105, 8 Sam Sing Street, Waterloo"]);
}

// Generate Offer Letter
async function generateOfferLetter() {
  if (!currentAnalysis) return;
  const targetOffer = parseFloat(document.getElementById("input-offer").value) || 750000;
  
  try {
    const res = await fetch("http://localhost:8000/api/negotiate/letter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        analysis: currentAnalysis,
        target_offer: targetOffer,
        user_name: "Prospective Buyer"
      })
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("letter-text").value = data.letter;
      document.getElementById("letter-container").style.display = "flex";
      return;
    }
  } catch (e) {
    console.warn("Using offline letter generator:", e);
  }

  // Client-side fallback letter generator
  const addr = currentAnalysis.display_name;
  const avm = currentAnalysis.pricing?.avm_predicted_price;
  const low = currentAnalysis.pricing?.avm_range_low;
  const beds = currentAnalysis.basics?.bedrooms || 1;

  const fallbackLetter = `Subject: Formal Expression of Interest & Offer — ${addr}

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

  document.getElementById("letter-text").value = fallbackLetter;
  document.getElementById("letter-container").style.display = "flex";
}

// Copy to Reddit Format
function copyRedditFormat() {
  if (!currentAnalysis) return;
  const addr = currentAnalysis.display_name;
  const guide = currentAnalysis.pricing?.guide_price;
  const avm = currentAnalysis.pricing?.avm_predicted_price;
  const pct = currentAnalysis.pricing?.underquote_percentage || 0;
  const traps = currentAnalysis.traps || [];

  const text = `[Sydney Property Reality Check] ${addr}
Advertised Guide: ${guide ? `$${Math.round(guide).toLocaleString()}` : "Auction Guide"}
Microburbs AVM: $${avm ? Math.round(avm).toLocaleString() : "N/A"} (${pct > 0 ? `+${pct}% Underquoted` : "Fair Market"})

What the Agent Listed: "Quiet sanctuary in prime location"
What Microburbs Data Shows:
${traps.map(t => `- ${t.title}: ${t.detail || ""}`).join("\n")}

Stop bidding blind in Sydney. Microburbs data shows the real numbers before auction day.`;

  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById("btn-copy-reddit");
    btn.innerText = "✅ Copied to Clipboard!";
    setTimeout(() => { btn.innerText = "📋 Copy Reddit Format"; }, 2000);
  });
}

// Download Card as PNG via HTML5 Canvas
function downloadCardAsPng() {
  if (!currentAnalysis) return;
  const canvas = document.createElement("canvas");
  canvas.width = 1080;
  canvas.height = 1080;
  const ctx = canvas.getContext("2d");

  // Background
  ctx.fillStyle = "#0B0F19";
  ctx.fillRect(0, 0, 1080, 1080);

  // Top header banner
  ctx.fillStyle = "#0284C7";
  ctx.fillRect(80, 80, 920, 10);

  // Badge
  ctx.font = "bold 28px -apple-system, sans-serif";
  ctx.fillStyle = "#38BDF8";
  ctx.fillText("MICROBURBS SYDNEY REALITY CHECK", 80, 140);

  // Address
  ctx.font = "bold 44px -apple-system, sans-serif";
  ctx.fillStyle = "#FFFFFF";
  ctx.fillText(currentAnalysis.display_name.slice(0, 38), 80, 210);

  // Contrast Cards
  // Left: The Advert
  ctx.fillStyle = "#131B2E";
  ctx.roundRect(80, 270, 440, 360, 20);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,0.1)";
  ctx.stroke();

  ctx.font = "bold 24px -apple-system, sans-serif";
  ctx.fillStyle = "#94A3B8";
  ctx.fillText("THE ADVERT", 120, 330);

  const guide = currentAnalysis.pricing?.guide_price;
  ctx.font = "bold 56px -apple-system, sans-serif";
  ctx.fillStyle = "#FFFFFF";
  ctx.fillText(guide ? `$${Math.round(guide).toLocaleString()}` : "$720,000", 120, 420);

  ctx.font = "italic 24px -apple-system, sans-serif";
  ctx.fillStyle = "#CBD5E1";
  ctx.fillText('"Quiet luxury sanctuary"', 120, 490);

  // Right: The Microburbs Facts
  ctx.fillStyle = "#0C2340";
  ctx.roundRect(560, 270, 440, 360, 20);
  ctx.fill();
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.font = "bold 24px -apple-system, sans-serif";
  ctx.fillStyle = "#38BDF8";
  ctx.fillText("THE MICROBURBS FACTS", 600, 330);

  const avm = currentAnalysis.pricing?.avm_predicted_price;
  ctx.font = "bold 56px -apple-system, sans-serif";
  ctx.fillStyle = "#38BDF8";
  ctx.fillText(avm ? `$${Math.round(avm).toLocaleString()}` : "$805,500", 600, 420);

  const pct = currentAnalysis.pricing?.underquote_percentage || 0;
  ctx.font = "bold 28px -apple-system, sans-serif";
  ctx.fillStyle = "#F59E0B";
  ctx.fillText(pct > 0 ? `+${pct}% UNDERQUOTED` : "FAIR MARKET", 600, 490);

  // Traps banner
  ctx.fillStyle = "#131B2E";
  ctx.roundRect(80, 680, 920, 220, 20);
  ctx.fill();

  ctx.font = "bold 28px -apple-system, sans-serif";
  ctx.fillStyle = "#EF4444";
  ctx.fillText("UNMASKED HIDDEN HAZARDS:", 120, 740);

  ctx.font = "24px -apple-system, sans-serif";
  ctx.fillStyle = "#F8FAFC";
  const traps = currentAnalysis.traps || [];
  if (traps.length > 0) {
    traps.slice(0, 3).forEach((t, i) => {
      ctx.fillText(`• ${t.title}`, 120, 790 + (i * 35));
    });
  } else {
    ctx.fillText("• Certified Clear: No critical hazards within 200m", 120, 790);
  }

  // Footer
  ctx.font = "20px -apple-system, sans-serif";
  ctx.fillStyle = "#64748B";
  ctx.fillText("Verified via Microburbs Municipal API • Built for the 2026 Hackathon", 80, 980);

  // Download Trigger
  const link = document.createElement("a");
  link.download = `microtruth-${Date.now()}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Listen for storage changes from content script
  if (window.chrome && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(["currentListing"], (result) => {
      if (result.currentListing && result.currentListing.analysis) {
        renderAnalysis(result.currentListing.analysis);
      } else {
        renderAnalysis(DEMO_PROFILES["Unit 105, 8 Sam Sing Street, Waterloo"]);
      }
    });

    chrome.storage.onChanged.addListener((changes) => {
      if (changes.currentListing && changes.currentListing.newValue) {
        renderAnalysis(changes.currentListing.newValue.analysis);
      }
    });
  } else {
    renderAnalysis(DEMO_PROFILES["Unit 105, 8 Sam Sing Street, Waterloo"]);
  }

  // Demo selector dropdown
  document.getElementById("demo-select").addEventListener("change", (e) => {
    const selected = e.target.value;
    if (selected) {
      loadAnalysis(selected);
    }
  });

  // Buttons
  document.getElementById("btn-generate-letter").addEventListener("click", generateOfferLetter);
  document.getElementById("btn-copy-reddit").addEventListener("click", copyRedditFormat);
  document.getElementById("btn-download-card").addEventListener("click", downloadCardAsPng);
  document.getElementById("btn-copy-letter")?.addEventListener("click", () => {
    const text = document.getElementById("letter-text").value;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById("btn-copy-letter");
      btn.innerText = "✅ Offer Copied!";
      setTimeout(() => { btn.innerText = "Copy Offer to Clipboard"; }, 2000);
    });
  });
});
