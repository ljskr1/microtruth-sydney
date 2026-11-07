# 🔍 MicroTruth Sydney — The Property Reality Engine & Negotiation Weapon

> **The Microburbs Hackathon 2026 Entry**  
> **Team**: Oneshot (`team-29`)  
> **Repository**: [https://github.com/ljskr1/microtruth-sydney](https://github.com/ljskr1/microtruth-sydney)  
> **Pitch Video**: `submission/pitch.mp4` (40 seconds, 1080p, <95 MB)  
> **Demo Walkthrough**: `submission/demo.mp4` (2 minutes 15 seconds, 1080p, <95 MB)  
> **Written Report**: `report.html` (Full comparative report & held-out validation)

---

## 🎯 What We Built

**MicroTruth Sydney** is a dual-tier property intelligence weapon designed to end asymmetric information in the Sydney housing market:
1. **Manifest V3 Chrome Extension**: Injects directly beside property listings on `Domain.com.au` and `Realestate.com.au`, displaying an in-page **Reality Badge** and launching a full-featured **Side Panel**.
2. **Viral Social Card Studio (Task 1 Engine)**: Automatically generates high-contrast 1:1 and 9:16 shareable graphic cards (*"The Advert vs The Facts"*) formatted for **r/ausfinance**, **r/sydney**, and Instagram to drive organic viral adoption.
3. **Data-Backed Negotiation Letter Generator**: Transforms Microburbs AVM confidence ranges and 90-day suburb comps into formal, unyielding buyer/renter offer letters with 1-click clipboard export.
4. **Standalone Web Showcase**: A zero-install responsive web application at `http://localhost:8000` allowing judges and mobile users to explore any City of Sydney address instantly.

---

## 👥 Who It Helps

- **First-Home Buyers**: Protected against deliberate real estate agent underquoting (often by 15%–25%) that causes prospective buyers to waste thousands on building inspections for properties they cannot afford.
- **Everyday Renters**: Empowers tenants facing arbitrary rent hikes by arming them with true gross yield dynamics and historical lease comps.
- **Buyer's Agents & Property Analysts**: Provides instantaneous 1-second municipal hazard checks (floods, public housing clusters, height/FSR development overlays, and traffic corridors) while browsing.

---

## 📊 The Data

MicroTruth integrates directly with the **Microburbs Hackathon API** (`api-ht.microburbs.com.au`), tapping into 176 endpoints across all 29 suburbs in the City of Sydney:
- `GET /v1/geocode/address`: Resolves messy scraped page addresses to official G-NAF IDs.
- `GET /v1/properties/{gnaf}/valuation/avm`: Independent automated valuation, 80% range, and model confidence score.
- `GET /v1/properties/{gnaf}/risks/all`: Municipal flood overlays, bushfire risks, and distance to nearest hazard.
- `GET /v1/properties/{gnaf}/surroundings/public-housing`: 200m radius social housing density calculation.
- `GET /v1/properties/{gnaf}/development/all`: Planning zoning codes, floor space ratios (FSR), and height overlays.
- `GET /v1/suburbs/{suburb}/shapes/noise-heatmap`: Arterial road and venue noise intensity vectors.
- `GET /v1/suburbs/{suburb}/market/all`: 12-month capital growth, gross yields, and median days on market.

---

## 🧠 The Clever Step (Judges' Primary Factor)

> *"A clever, non-obvious step beats polish."* — Microburbs Hackathon Guide

Rather than merely displaying static property figures, MicroTruth implements **The Asymmetric Information Arbitrage Engine**:
1. **Empirical Underquote Probability Index**: Compares the agent's guide price against Microburbs AVM predicted price and historical precinct volatility. If the guide is $>15\%$ below the AVM, it flags `SEVERE_UNDERQUOTE`, calculates the expected realistic auction clearance range, and alerts the buyer.
2. **The Hazard & Livability Radar**: Cross-references municipal flood layers with upcoming zoning overlays to alert buyers if high-density construction or environmental risks will devalue their property within 24 months.
3. **The Viral Contrast Arbitrage (Task 1 Synergy)**: Bridges Task 3 (Chrome Extension) and Task 1 (Social Post) by turning every listing into an emotional *“Advert Pitch vs Microburbs Facts”* infographic, tapping into Australia's highest-engagement real estate communities.

---

## 🚀 How to Run It

### Prerequisites
- Python 3.10+
- Google Chrome (or any Chromium browser)
- `ffmpeg` (for video generation, optional)

### 1. Launch the Backend & Web Showcase
```bash
# Clone the repository
git clone https://github.com/ljskr1/microtruth-sydney.git
cd microtruth-sydney

# Setup virtual environment and dependencies
uv venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt

# Configure your API key
cp .env.example .env
# Edit .env and paste your MICROBURBS_API_KEY=...

# Start the server (serves API + Web Showcase)
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser to: **`http://localhost:8000`** to interact with the live web showcase and test any Sydney address!

### 2. Load the Chrome Extension
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked**.
4. Select the `extension/` folder inside this repository.
5. Visit any property listing on `domain.com.au` or `realestate.com.au` (or use the built-in demo switcher in the Side Panel).
6. Click the extension icon in your toolbar or click **Inspect Full Truth** on the in-page badge to open the Side Panel!

---

## 📦 Submission Deliverables Verification

| Requirement | Status | File Location |
| :--- | :--- | :--- |
| **Public GitHub Repo** | ✅ Verified | `https://github.com/ljskr1/microtruth-sydney` |
| **Pitch Video** | ✅ $\le 40$s, $<95$ MB | `submission/pitch.mp4` |
| **Demo Walkthrough** | ✅ $\le 2$m15s, $<95$ MB | `submission/demo.mp4` |
| **Written Report** | ✅ Structured HTML | `report.html` & `submission/report.html` |
| **API Key Privacy** | ✅ Zero Leaked Keys | Protected via `.env` and server-side proxy |
| **City of Sydney Scope** | ✅ 29 Suburbs Covered | Fully tested across Waterloo, Surry Hills, Pyrmont |

---

## 🏆 Hackathon Attribution
- **Team**: Oneshot (`team-29`)
- **Event**: The Microburbs Hackathon · Saturday 7 November 2026
- **Host**: Microburbs & UTS Business School (14 Ultimo Rd, Ultimo, Level 2)
- **License**: MIT
