import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from microburbs_client import MicroburbsClient
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return MicroburbsClient()

@pytest.fixture
def api_test_client():
    return TestClient(app)

def test_health_check(api_test_client):
    res = api_test_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["service"] == "MicroTruth Sydney"
    assert "team-29" in data["team"]

def test_demo_listings(api_test_client):
    res = api_test_client.get("/api/demo-listings")
    assert res.status_code == 200
    listings = res.json().get("data", [])
    assert len(listings) >= 4
    first = listings[0]
    assert "Waterloo" in first["address"]
    assert first["advertised_guide"] > 0

def test_web_showcase_served(api_test_client):
    res = api_test_client.get("/")
    assert res.status_code == 200
    assert "MicroTruth Sydney" in res.text
    assert "viral-canvas" in res.text

def test_negotiation_letter_generation(client):
    analysis_mock = {
        "display_name": "Unit 105, 8 Sam Sing Street, Waterloo (NSW)",
        "suburb": "Waterloo",
        "basics": {"bedrooms": 1, "bathrooms": 1, "parking": 0},
        "pricing": {
            "guide_price": 720000,
            "avm_predicted_price": 805500,
            "avm_range_low": 628290,
            "avm_range_high": 982710
        }
    }
    letter = client.generate_negotiation_letter(analysis_mock, user_name="Jane Doe", target_offer=750000)
    assert "Subject: Formal Expression of Interest & Offer" in letter
    assert "$750,000" in letter
    assert "Jane Doe" in letter
    assert "MicroTruth Sydney Intelligence Engine" in letter

@pytest.mark.asyncio
async def test_underquoting_classification(client):
    # Test property analysis with live AVM comparison
    # 8 Cooper St Surry Hills has live AVM of ~$697k
    # When guide is $550k -> underquoted by +26%
    res_underquote = await client.analyze_property_full("Unit 105, 8 Cooper Street, Surry Hills", guide_price=550000)
    assert res_underquote.get("success") is True
    pricing_u = res_underquote.get("pricing", {})
    assert pricing_u.get("underquote_percentage") > 15.0
    assert pricing_u.get("verdict") == "SEVERE_UNDERQUOTE"

    # When guide is $950k -> overpriced by -26%
    res_overprice = await client.analyze_property_full("Unit 105, 8 Cooper Street, Surry Hills", guide_price=950000)
    assert res_overprice.get("success") is True
    pricing_o = res_overprice.get("pricing", {})
    assert pricing_o.get("underquote_percentage") < -10.0
    assert pricing_o.get("verdict") == "OVERPRICED"

def test_social_card_data(api_test_client):
    res = api_test_client.get("/api/social-card-data?address=Unit%20105,%208%20Sam%20Sing%20Street,%20Waterloo&guide_price=720000")
    assert res.status_code == 200
    data = res.json()
    assert data["headline"] == "Sydney Property Reality Check"
    assert "advert" in data
    assert "facts" in data
    assert "viral_hook" in data

def test_building_comps_endpoint(api_test_client):
    res = api_test_client.get("/api/building-comps?address=Unit%20105,%208%20Sam%20Sing%20Street,%20Waterloo")
    assert res.status_code == 200
    data = res.json()
    assert data["normalized_building_street"] == "8 SAM SING STREET"
    assert data["building_stats"]["sales_count"] > 0
    assert data["building_stats"]["leases_count"] > 0
    assert len(data["recent_sales"]) > 0
    assert len(data["recent_leases"]) > 0
