# MicroTruth Sydney

Property pricing, building comps, and geospatial risk extension for the City of Sydney.

Microburbs Hackathon 2026 entry by Team Oneshot (`team-29`).  
Repository: [https://github.com/ljskr1/microtruth-sydney](https://github.com/ljskr1/microtruth-sydney)

---

## Submission Deliverables

| Deliverable | Specification | File Location |
| :--- | :--- | :--- |
| Pitch Video | 29.06s, 1080p Full HD, 22.1 MB | `submission/pitch.mp4` |
| Demo Video | 2m15s, 1080p Full HD, 1.1 MB | `submission/demo.mp4` |
| Task 4 Rents CSV | Exactly 65,777 rows, verified format | `submission/rents_oneshot.csv` |
| Task 5 Valuation CSV | Exactly 181,711 rows, verified format | `submission/valuation_oneshot.csv` |
| Technical Report | Structured HTML validation report | `submission/report.html` (also at `report.html`) |
| Submission Verification | Automated validation script | `scripts/verify_submissions.py` |

---

## Overview

Prospective property buyers and renters in Sydney navigate significant information asymmetry. Advertised price guides on major portals are often set 10% to 20% below realistic auction clearance levels, historical sales and leases within the same building complex are rarely surfaced in one place, and localized spatial risks (such as flood catchments, public housing density, and development zoning overlays) require manual cross-referencing across multiple council databases.

MicroTruth Sydney operates directly in-situ on Domain.com.au and Realestate.com.au listings through a Manifest V3 Chrome Extension. It compares advertised figures against Microburbs algorithmic automated valuations (AVMs), surfaces historical transactions from the same apartment block, and provides geospatial context within an integrated side panel.

---

## System Architecture

The application consists of three primary components:

### 1. In-Situ Chrome Extension (Manifest V3)
- **Content Script Overlay**: Injects directly beneath the advertised price guide on property listing pages, displaying an underquoting reality check with expected auction clearance bands.
- **Side Panel**: Opens a persistent panel with a macOS-inspired interface, providing detailed pricing breakdowns, cash flow estimates, and negotiation tools without navigating away from the listing.

### 2. Geospatial Cockpit and Google Maps Integration
- **Boundary Map Layer**: Embedded map displaying the official suburb polygon (e.g. Waterloo), target property coordinates, and neighboring comparable building markers. Delivered via a local backend proxy to ensure compliance with Chrome Extension Content Security Policy (CSP).
- **Satellite 3D Layer**: High-resolution hybrid aerial imagery via the Google Maps Static API.
- **Street View Layer**: Ground-level street imagery capturing property curb conditions.

### 3. Local SQLite Municipal Store & Python Backend
- Ingested 112,457 historical residential leases, 81,079 sales records, 6,597 public housing properties, and 213,239 City of Sydney G-NAF address points into an optimized SQLite database (<2ms query latency in WAL mode).
- Powers immediate building-level comp queries for any selected unit address.
- Serves financial cash flow modeling: combines Task 4 rental estimates with mortgage amortization (principal and interest), strata levies, and council rates.
- Offers an automated counter-offer generator that compiles recent building comps and valuation confidence intervals into formal offer letters.

---

## Machine Learning Benchmarks

### Task 4: Weekly Rent Prediction
- **Training Set**: 103,919 residential leases across the City of Sydney (2020 to 2025).
- **Validation Set**: 8,538 held-out 2026 leases.
- **Model**: Hedonic Gradient Boosting Regressor trained on physical attributes (bedrooms, bathrooms, parking spaces), temporal trends, and spatial proximity metrics.

| Metric | Microburbs Baseline | MicroTruth Sydney | Improvement |
| :--- | :--- | :--- | :--- |
| Median Dollar Error | $86.00 / wk | **$59.16 / wk** | **-31.2% error reduction** |
| Share &le; $100 Error | 55.21% | **69.83%** | **+14.62% accuracy gain** |
| Validation MAE | — | **$94.90 / wk** | $R^2 = 0.8159$ |
| Evaluated Records | Required format | **65,777 rows** | Zero missing values |

### Task 5: Property Valuation
- **Model**: Repeat-sales index combined with hedonic feature modeling across historical City of Sydney sales.
- **Submission Scope**: Generated market valuations for 181,711 residential properties (median: $773,041; range: $250,000 to $25,000,000).

---

## Project Structure

```text
microtruth-sydney/
├── backend/
│   ├── main.py                  # FastAPI proxy, maps routes, and analysis pipeline
│   ├── microburbs_client.py     # Microburbs API client with parallel async lookups
│   ├── building_store.py        # SQLite address matching and building comps lookup
│   ├── data_ingest.py           # Ingestion script for leases, sales, and public housing
│   ├── requirements.txt         # Python dependencies
│   └── tests/                   # Automated backend test suite
├── extension/
│   ├── manifest.json            # Manifest V3 extension configuration
│   ├── content.js               # In-page listing detector and badge injection
│   ├── content.css              # Styling for in-page listing badges
│   ├── background.js            # Extension service worker and side panel handler
│   └── sidepanel/
│       ├── sidepanel.html       # Side panel interface
│       ├── sidepanel.js         # Panel interaction logic, tab controls, and calculators
│       └── sidepanel.css        # Apple HIG dark mode design system
├── scripts/
│   ├── verify_submissions.py    # Automated validation of CSV deliverables
│   ├── train_task4_model.py     # Hedonic rental model training pipeline
│   └── record_showcase.mjs      # Playwright showcase recording script
├── submission/
│   ├── pitch.mp4                # 29-second pitch video
│   ├── demo.mp4                 # 2-minute walkthrough video
│   ├── rents_oneshot.csv        # Task 4 submission file (65,777 rows)
│   ├── valuation_oneshot.csv    # Task 5 submission file (181,711 rows)
│   └── report.html              # Technical validation report
└── web/
    └── domain-listing.html      # Local reference listing page for offline evaluation
```

---

## Local Setup and Usage

### Prerequisites
- Python 3.10 or newer
- Google Chrome (or Chromium-based browser)
- Node.js 18 or newer (optional, for running Playwright scripts)

### 1. Start the Backend Service
```bash
# Clone the repository
git clone https://github.com/ljskr1/microtruth-sydney.git
cd microtruth-sydney

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Install the Chrome Extension
1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** using the toggle in the upper right.
3. Click **Load unpacked**.
4. Select the `extension/` directory from this repository.
5. Navigate to any property on `domain.com.au`, or test locally using `http://127.0.0.1:8000/domain-listing.html`.
6. Click **Inspect Full Truth** on the in-page badge to open the side panel.

### 3. Verify Submissions
To verify that the submission CSV files strictly comply with the hackathon validation rules:
```bash
python scripts/verify_submissions.py
```

### 4. Run Automated Tests
```bash
pytest backend/tests/test_microtruth.py
```

---

## Security & Privacy Note

External API keys (including the Google Maps API key and Microburbs credentials) are managed strictly on the backend through environment variables (`.env`). The Chrome extension requests map layers and proxy intelligence exclusively from the authenticated local server (`127.0.0.1:8000`), ensuring that no private credentials or client keys are bundled into extension assets or exposed in public commits.
