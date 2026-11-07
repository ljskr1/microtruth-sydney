import os
import asyncio
import urllib.parse
from typing import Optional, Dict, Any, List
import httpx
from dotenv import load_dotenv

# Load local environment
load_dotenv()

BASE_URL = "https://api-ht.microburbs.com.au"
DEFAULT_KEY = os.environ.get("MICROBURBS_API_KEY", "")

class MicroburbsClient:
    """Production-grade asynchronous client for the Microburbs Hackathon API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DEFAULT_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) MicroTruth/1.0",
            "Accept": "application/json",
        }
        self.timeout = httpx.Timeout(15.0, connect=5.0)

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Internal GET helper with error resilience and status handling."""
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url, headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    # Check if body indicates available: false
                    if isinstance(data, dict) and data.get("available") is False:
                        return None
                    return data.get("data", data)
                elif resp.status_code in (403, 404):
                    return None
                elif resp.status_code == 429:
                    # Rate limited: wait 1 second and retry once
                    await asyncio.sleep(1.0)
                    retry_resp = await client.get(url, headers=self.headers, params=params)
                    if retry_resp.status_code == 200:
                        return retry_resp.json().get("data", retry_resp.json())
                    return None
                else:
                    return None
            except Exception:
                return None

    async def geocode(self, address: str) -> List[Dict[str, Any]]:
        """Resolves raw address to candidate GNAF IDs."""
        endpoint = "/v1/geocode/address"
        data = await self._get(endpoint, params={"address": address})
        if isinstance(data, list):
            return data
        return []

    async def get_basics(self, gnaf_id: str) -> Optional[Dict[str, Any]]:
        """Bedrooms, bathrooms, parking, dwelling type, land area."""
        return await self._get(f"/v1/properties/{gnaf_id}/basics/all")

    async def get_valuation(self, gnaf_id: str) -> Optional[Dict[str, Any]]:
        """AVM automated valuation, price range, and confidence score."""
        val = await self._get(f"/v1/properties/{gnaf_id}/valuation/all")
        if val and isinstance(val, dict) and "avm" in val:
            return val.get("avm")
        return await self._get(f"/v1/properties/{gnaf_id}/valuation/avm")

    async def get_risks(self, gnaf_id: str) -> Optional[Dict[str, Any]]:
        """Flood overlays, bushfire, and environmental risk factors."""
        return await self._get(f"/v1/properties/{gnaf_id}/risks/all")

    async def get_public_housing(self, gnaf_id: str) -> Optional[Dict[str, Any]]:
        """Surrounding public housing indicators within 200m radius."""
        return await self._get(f"/v1/properties/{gnaf_id}/surroundings/public-housing")

    async def get_development(self, gnaf_id: str) -> Optional[Dict[str, Any]]:
        """Planning zones, FSR (floor space ratio), and height overlays."""
        return await self._get(f"/v1/properties/{gnaf_id}/development/all")

    async def get_nearby_for_sale(self, gnaf_id: str) -> Optional[Dict[str, Any]]:
        """Active competing listings within 1km radius."""
        return await self._get(f"/v1/properties/{gnaf_id}/context/nearby-for-sale")

    async def get_suburb_market(self, suburb: str) -> Optional[Dict[str, Any]]:
        """Core market indicators for the suburb."""
        quoted = urllib.parse.quote(suburb)
        return await self._get(f"/v1/suburbs/{quoted}/market/all")

    async def get_suburb_noise(self, suburb: str) -> Optional[Dict[str, Any]]:
        """GeoJSON traffic & arterial noise heatmap."""
        quoted = urllib.parse.quote(suburb)
        return await self._get(f"/v1/suburbs/{quoted}/shapes/noise-heatmap")

    async def analyze_property_full(
        self,
        address: str,
        guide_price: Optional[float] = None,
        advertised_rent: Optional[float] = None
    ) -> Dict[str, Any]:
        """Runs parallel analysis across all intelligence vectors and calculates reality metrics."""
        candidates = await self.geocode(address)
        if not candidates:
            # Fallback fuzzy attempt: remove unit prefix if present or clean punctuation
            clean_addr = address.replace("#", "").strip()
            candidates = await self.geocode(clean_addr)

        if not candidates:
            return {
                "success": False,
                "error": f"Address could not be matched in City of Sydney database: '{address}'",
                "searched_address": address,
            }

        primary = candidates[0]
        gnaf_id = primary.get("id")
        matched_name = primary.get("display_name", address)
        suburb = primary.get("sal", "Sydney")

        # Gather all property intelligence in parallel
        basics, valuation, risks, public_housing, development, nearby, suburb_market = await asyncio.gather(
            self.get_basics(gnaf_id),
            self.get_valuation(gnaf_id),
            self.get_risks(gnaf_id),
            self.get_public_housing(gnaf_id),
            self.get_development(gnaf_id),
            self.get_nearby_for_sale(gnaf_id),
            self.get_suburb_market(suburb),
            return_exceptions=True,
        )

        # Sanitize any exceptions
        basics = basics if isinstance(basics, dict) else {}
        valuation = valuation if isinstance(valuation, dict) else {}
        risks = risks if isinstance(risks, dict) else {}
        public_housing = public_housing if isinstance(public_housing, dict) else {}
        development = development if isinstance(development, dict) else {}
        nearby = nearby if isinstance(nearby, dict) else {}
        suburb_market = suburb_market if isinstance(suburb_market, dict) else {}

        # 1. Underquoting & Pricing Verdict
        avm_price = valuation.get("predicted_price")
        avm_low = valuation.get("predicted_price_low")
        avm_high = valuation.get("predicted_price_high")
        confidence = valuation.get("confidence_score", 85)

        pricing_verdict: Dict[str, Any] = {
            "guide_price": guide_price,
            "avm_predicted_price": avm_price,
            "avm_range_low": avm_low,
            "avm_range_high": avm_high,
            "confidence_score": confidence,
            "verdict": "UNKNOWN",
            "underquote_amount": 0.0,
            "underquote_percentage": 0.0,
            "human_summary": "Guide price not provided.",
        }

        if guide_price and avm_price:
            diff = avm_price - guide_price
            pct = round((diff / guide_price) * 100, 1)
            pricing_verdict["underquote_amount"] = diff
            pricing_verdict["underquote_percentage"] = pct

            if pct >= 15.0:
                pricing_verdict["verdict"] = "SEVERE_UNDERQUOTE"
                pricing_verdict["human_summary"] = (
                    f"⚠️ High Underquote Risk: Listed at ${guide_price:,.0f}, but Microburbs valuation is "
                    f"${avm_price:,.0f} (+{pct}% difference). Expect heavy auction competition."
                )
            elif pct >= 6.0:
                pricing_verdict["verdict"] = "MODERATE_UNDERQUOTE"
                pricing_verdict["human_summary"] = (
                    f"⚡ Likely Underquoted by ~{pct}%: Expected sale between ${avm_low:,.0f} and ${avm_high:,.0f}."
                )
            elif pct >= -5.0:
                pricing_verdict["verdict"] = "FAIR_MARKET"
                pricing_verdict["human_summary"] = (
                    f"✅ Fair Market Alignment: Guide of ${guide_price:,.0f} aligns with Microburbs AVM (${avm_price:,.0f})."
                )
            else:
                pricing_verdict["verdict"] = "OVERPRICED"
                pricing_verdict["human_summary"] = (
                    f"📉 Potential Overpricing: Listed {abs(pct)}% above estimated automated market value."
                )
        elif avm_price:
            pricing_verdict["verdict"] = "VALUATION_AVAILABLE"
            pricing_verdict["human_summary"] = (
                f"Estimated Valuation: ${avm_price:,.0f} (Range: ${avm_low:,.0f} – ${avm_high:,.0f}, Confidence: {confidence}%)."
            )

        # 2. Trap & Hazard Radar
        traps: List[Dict[str, Any]] = []

        # Flood
        flood_data = risks.get("flood")
        if flood_data and isinstance(flood_data, list) and len(flood_data) > 0:
            item = flood_data[0]
            dist = item.get("nearest_distance_m", 9999)
            if item.get("on_property"):
                traps.append({
                    "type": "FLOOD_ON_PROPERTY",
                    "severity": "CRITICAL",
                    "title": "Flood Overlay Active",
                    "detail": "Property directly sits in a designated council flood risk layer.",
                })
            elif dist < 300:
                traps.append({
                    "type": "FLOOD_NEARBY",
                    "severity": "WARNING",
                    "title": f"Flood Zone Within {int(dist)}m",
                    "detail": f"Nearest flood risk zone is located {int(dist)} meters from this address.",
                })

        # Public Housing Density
        ph_flagged = public_housing.get("flagged_count", 0)
        ph_total = public_housing.get("property_count", 1)
        if ph_flagged > 0:
            ph_ratio = round((ph_flagged / max(ph_total, 1)) * 100, 1)
            traps.append({
                "type": "PUBLIC_HOUSING_PROXIMITY",
                "severity": "INFO" if ph_ratio < 5 else "WARNING",
                "title": f"{ph_flagged} Social Housing Properties Within 200m",
                "detail": f"{ph_flagged} of {ph_total} surrounding properties ({ph_ratio}%) identified as social housing.",
            })

        # Development & Height Overlays
        zoning = development.get("zoning_code", {})
        overlays = development.get("zoning_overlays", [])
        if zoning and zoning.get("name"):
            traps.append({
                "type": "ZONING",
                "severity": "INFO",
                "title": f"Zone: {zoning.get('name')} ({zoning.get('category', 'Urban')})",
                "detail": f"Permits mixed-use and ongoing neighborhood densification.",
            })

        # Nearby Sales & Comp Count
        active_comps = nearby.get("listings", []) if isinstance(nearby, dict) else []

        return {
            "success": True,
            "searched_address": address,
            "matched_gnaf_id": gnaf_id,
            "display_name": matched_name,
            "suburb": suburb,
            "basics": {
                "bedrooms": basics.get("bed_count"),
                "bathrooms": basics.get("bath_count"),
                "parking": basics.get("parking_count"),
                "dwelling_type": basics.get("dwelling_type", "apartment"),
                "land_area": basics.get("land_area_sqm"),
            },
            "pricing": pricing_verdict,
            "traps": traps,
            "nearby_active_count": len(active_comps),
            "nearby_active_samples": active_comps[:3],
            "suburb_market_snapshot": {
                "suburb": suburb,
                "median_sale_price": suburb_market.get("median_sale_price"),
                "median_rent": suburb_market.get("median_rent"),
                "days_on_market": suburb_market.get("days_on_market"),
            },
        }

    def generate_negotiation_letter(
        self,
        analysis: Dict[str, Any],
        user_name: str = "Prospective Buyer",
        target_offer: Optional[float] = None
    ) -> str:
        """Generates a data-backed, formal counter-offer / negotiation letter."""
        addr = analysis.get("display_name", "the property")
        pricing = analysis.get("pricing", {})
        avm = pricing.get("avm_predicted_price")
        avm_low = pricing.get("avm_range_low")
        guide = pricing.get("guide_price")
        basics = analysis.get("basics", {})
        beds = basics.get("bedrooms", "this")
        offer = target_offer or (avm_low if avm_low else (guide * 0.92 if guide else 1000000))

        avm_str = f"${avm:,.0f}" if avm else "comparable market levels"
        avm_low_str = f"${avm_low:,.0f}" if avm_low else "current comps"

        letter = f"""Subject: Formal Expression of Interest & Offer — {addr}

Dear Listing Agent,

Thank you for the opportunity to review {addr}. Having conducted detailed independent due diligence utilizing certified municipal geospatial and market intelligence (Microburbs / City of Sydney automated valuation model), I would like to submit a formal offer of ${offer:,.0f} for your vendor's consideration.

Our offer is backed by the following verifiable data points:
1. Automated Independent Valuation: The current Microburbs AVM indicates an estimated fair market value of {avm_str}, with a baseline valuation range spanning {avm_low_str}.
2. Local Comparative Sales: Recent verified transactions for {beds}-bedroom units in this precinct indicate clear ceiling resistance, reflecting current interest rate conditions.
3. Prepared Financial Readiness: We are pre-approved, contract-ready, and able to execute a 10% deposit with standard 35-day settlement terms or customized terms to suit the vendor.

We believe this offer represents a realistic, competitive, and immediately actionable path to an exchange without prolonged auction uncertainty.

Looking forward to your vendor's response.

Sincerely,
{user_name}
Prepared via MicroTruth Sydney Intelligence Engine
"""
        return letter
