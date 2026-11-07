# 🔍 MicroTruth Sydney — The Property Reality Engine & Negotiation Weapon

> **The Microburbs Hackathon 2026 Entry**  
> **Team**: Oneshot (`team-29`)  
> **Repository**: [https://github.com/ljskr1/microtruth-sydney](https://github.com/ljskr1/microtruth-sydney)  
> **Pitch Video**: `submission/pitch.mp4` (29.06s, 1080p Full HD, 21 MB, OpenScreen composited)  
> **Demo Walkthrough**: `submission/demo.mp4` (2m15s, 1080p, 1.1 MB)  
> **Written Report**: `report.html` & `submission/report.html` (Full comparative report & held-out validation)  
> **Task 4 Rents**: `submission/rents_oneshot.csv` (65,777 rows, MAE $59.16 vs $86.00 baseline)  
> **Task 5 Valuation**: `submission/valuation_oneshot.csv` (181,711 rows)

---

## 🎯 What We Built

**MicroTruth Sydney** is an end-to-end property intelligence weapon designed to end asymmetric information in the Sydney housing market:
1. **Manifest V3 Chrome Extension**: Injects directly beside property listings on `Domain.com.au` and `Realestate.com.au`, displaying an in-page **⚡ Underquote Reality Badge** and launching a full-featured **Side Panel** with real-time SVG suburb boundary polygons, 3 market signals, inside-the-building comps, and hidden trap radar.
2. **Inside The Building Ledger (Tasks 2 & 3 Integration)**: Ingested 112,457 historical leases, 81,079 sales, 6,597 public housing properties, and 213,239 City of Sydney addresses into a local SQLite database (WAL mode, <2ms lookup). Buyers browsing any unit instantly see past sales and leases in that exact building.
3. **Machine Learning Pricing Models (Tasks 4 & 5)**:
   - **Task 4 Rents Model**: Trained on 103,919 leases. On held-out 8,538 2026 leases, achieved **Median Dollar Error of $59.16** (beating Microburbs baseline of $86.00 by 31.2%), **Share &le; $100 Error of 69.83%** (beating baseline 55.21%), and $R^2 = 0.8159$.
   - **Task 5 Valuation Model**: Repeat-sales index + Hedonic GBDT generating 181,711 property valuations across City of Sydney.
4. **Task 1 Viral Pitch Video**: Automated high-resolution Playwright recording of authentic listing navigation paired with OpenScreen kinetic auto-zooms and viral hook annotations (`submission/pitch.mp4`: 29.06s, 21 MB).
5. **Data-Backed Negotiation Letter Generator**: Transforms Microburbs AVM confidence ranges and 90-day suburb comps into formal, unyielding buyer/renter offer letters with 1-click clipboard export.

---

## 📊 Benchmark & Accuracy Results

| Metric | Microburbs Baseline | MicroTruth Sydney (Our Model) | Improvement |
| :--- | :--- | :--- | :--- |
| **Task 4 Median Dollar Error** | $86.00 / wk | **$59.16 / wk** | **-31.2% error reduction** |
| **Task 4 Share &le; $100 Error** | 55.21% | **69.83%** | **+14.62% accuracy gain** |
| **Task 4 Validation MAE** | — | **$94.90 / wk** | $R^2 = 0.8159$ |
| **Task 4 Submissions** | Required | **65,777 rows** | Verified format & non-null |
| **Task 5 Submissions** | Required | **181,711 rows** | Verified format & positive ints |

---

## 👥 Who It Helps

- **First-Home Buyers**: Protected against deliberate real estate agent underquoting (often by 15%–25%) that causes prospective buyers to waste thousands on building inspections for properties they cannot afford.
- **Everyday Renters**: Empowers tenants facing arbitrary rent hikes by arming them with true gross yield dynamics and historical lease comps in the exact building.
- **Buyer's Agents & Property Analysts**: Provides instantaneous 1-second municipal hazard checks (floods, public housing clusters, height/FSR development overlays, and traffic corridors) while browsing.

---

## 🧠 The Clever Step (Judges' Primary Factor)

> *"A clever, non-obvious step beats polish."* — Microburbs Hackathon Guide

Rather than merely displaying static property figures or scaffolding a fake localhost dashboard, MicroTruth operates **in-situ where buyers already are**:
1. **Direct In-Page Reality Badge**: Compares the agent's guide price against Microburbs AVM predicted price. If the guide is $>15\%$ below the AVM, it flags `SEVERE_UNDERQUOTE`, calculates the expected realistic auction clearance range, and alerts the buyer right under the agent's price guide.
2. **True Building Ledger**: Ingests municipal addresses and transactions to expose past sales and leases in the *same building* that listing agents deliberately hide from marketing materials.
3. **Automated Showcasing with Playwright + OpenScreen**: Headless high-res recording and kinetic video compositing that highlights the exact human user experience under 30 seconds.

---

## 🚀 How to Run It

### Prerequisites
- Python 3.10+
- Google Chrome (or any Chromium browser)
- Node.js 18+

### 1. Launch the Backend
```bash
git clone https://github.com/ljskr1/microtruth-sydney.git
cd microtruth-sydney

# Setup virtual environment and dependencies
uv venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt

# Start the server (serves API + Extension static files)
.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 2. Load the Chrome Extension
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked**.
4. Select the `extension/` folder inside this repository.
5. Visit any property listing on `domain.com.au` or test with the built-in listing: `http://127.0.0.1:8000/web/domain-listing.html`.
6. See the in-page **⚡ Underquote Reality Badge** and click **Inspect Full Truth →** to open the drawer panel!

---

## 📦 Submission Deliverables Verification

| Requirement | Status | File Location |
| :--- | :--- | :--- |
| **Public GitHub Repo** | ✅ Verified | `https://github.com/ljskr1/microtruth-sydney` |
| **Task 1: Pitch Video** | ✅ $\le 45$s, $<95$ MB | `submission/pitch.mp4` (29.06s, 21 MB, 1080p) |
| **Task 1: Demo Video** | ✅ $\le 3$m, $<95$ MB | `submission/demo.mp4` (2m15s, 1.1 MB, 1080p) |
| **Task 2 & 3: Chrome Extension** | ✅ Manifest V3 | `extension/` (In-Page Badge + Sidepanel) |
| **Task 4: Rents CSV** | ✅ Exactly 65,777 rows | `submission/rents_oneshot.csv` |
| **Task 5: Valuation CSV** | ✅ Exactly 181,711 rows | `submission/valuation_oneshot.csv` |
| **Technical Report** | ✅ Structured HTML | `report.html` & `submission/report.html` |
| **Verification Script** | ✅ 100% Passed | `scripts/verify_submissions.py` |
| **API Key Privacy** | ✅ Zero Leaked Keys | Protected via `.env` and server-side proxy |
