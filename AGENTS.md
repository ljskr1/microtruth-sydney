# AGENTS.md — MicroTruth Sydney Engineering & Hackathon Conventions

## Project Overview
MicroTruth Sydney is the winning entry for the 2026 Microburbs Hackathon (Team Oneshot, key `team-29`).
It unites:
1. Manifest V3 Chrome Extension (`extension/`): Injects an in-page Reality Badge on `domain.com.au` and `realestate.com.au`, backed by a full-featured Side Panel.
2. FastAPI Backend & Intelligence Core (`backend/`): Proxies and enriches Microburbs Hackathon API (`api-ht.microburbs.com.au`) across all 29 City of Sydney suburbs.
3. Standalone Web Showcase (`web/`): A zero-install responsive web application at `http://localhost:8000` with 1-click live demo presets.
4. Viral Reality Card Studio (`web/app.js` & `extension/sidepanel/sidepanel.js`): Generates 1080p high-contrast infographic cards (*The Advert vs The Facts*) for r/ausfinance and Instagram.
5. High-Conversion Video Assets (`submission/`): `pitch.mp4` (40s, 1080p, 460KB) and `demo.mp4` (2m15s, 1080p, 1.09MB).

## Operational Rules
- Secret Hygiene: The `MICROBURBS_API_KEY` must never be hardcoded or committed to git. It is read from `.env` via `python-dotenv`.
- Suburb Coverage: Covers all 29 City of Sydney suburbs (e.g. Waterloo, Surry Hills, Pyrmont, Barangaroo, Chippendale). Suburb endpoints require exact URL encoding (e.g. `Waterloo%20(NSW)`).
- Video Constraints: `pitch.mp4` must strictly be $\le 45$ seconds and $<95$ MB. `demo.mp4` must strictly be $\le 3$ minutes and $<95$ MB.
- Test Suite: All changes must pass `pytest backend/tests/test_microtruth.py`.
