#!/usr/bin/env python3
"""
Generate a professional 16:9 PowerPoint pitch deck with speaker notes matching the 2-minute voiceover.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide
    
    # Theme Colors
    BG_COLOR = RGBColor(9, 13, 22)         # Deep slate navy
    CARD_BG = RGBColor(19, 27, 46)        # Card surface
    ACCENT = RGBColor(16, 185, 129)       # Emerald green
    TEXT_LIGHT = RGBColor(248, 250, 252)  # White
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate gray

    slides_data = [
        {
            "slide_num": 1,
            "eyebrow": "SLIDE 1 OF 7 · THE PROBLEM",
            "title": "The Asymmetric Trap in Sydney Real Estate",
            "bullets": [
                "Deliberate Underquoting: Listing agents guide 15%–25% below reserve to create artificial auction frenzy.",
                "Hidden Strata History: Critical building defects, past unit sales, and strata disputes hidden from buyers.",
                "Wasted Sunk Costs: Everyday first-home buyers waste $600–$1,000 per inspection on out-of-reach properties."
            ],
            "metric_val": "15%–25%",
            "metric_lbl": "Typical agent underquote margin below realistic auction reserve across Sydney.",
            "notes": "[00:00 - 00:16] In Sydney real estate, buyers are flying blind. Listing agents routinely underquote price guides by fifteen percent to lure crowds to auction, while hiding strata history, leaving buyers to waste thousands on building inspections for homes they can never afford."
        },
        {
            "slide_num": 2,
            "eyebrow": "SLIDE 2 OF 7 · ARCHITECTURAL INSIGHT",
            "title": "In-Situ Reality: Meet Buyers Where They Are",
            "bullets": [
                "Zero Fake Localhost Dashboards: Buyers never visit detached third-party portals during real search.",
                "Manifest V3 Chrome Extension: Injected directly on Domain.com.au & Realestate.com.au.",
                "Instant In-Page Truth: Underquote reality badge appears directly under the agent's price guide in <1s."
            ],
            "metric_val": "< 1 Sec",
            "metric_lbl": "In-situ injection latency directly into the buyer's active browsing session.",
            "notes": "[00:16 - 00:34] We didn't build another localhost dashboard that nobody visits. MicroTruth is a Chrome extension that meets buyers where they actually search: directly on Domain and Real Estate dot com dot au. The moment you view a listing, the truth is injected right beneath the agent's price guide."
        },
        {
            "slide_num": 3,
            "eyebrow": "SLIDE 3 OF 7 · THE UNDERQUOTE DETECTOR",
            "title": "The In-Page Underquote Reality Badge",
            "bullets": [
                "Real-Time AVM Comparison: Compares quoted guide against Microburbs Automated Valuation Models.",
                "Auction Clearance Corridor: Predicts realistic auction clearing price range ($790k–$835k on $720k guide).",
                "1-Click Slide-In Drawer: 'Inspect Full Truth' launches side drawer without losing listing context."
            ],
            "metric_val": "+11.9%",
            "metric_lbl": "Severe underquote detected on sample Waterloo unit ($720k Guide vs $805.5k Microburbs Reality).",
            "notes": "[00:34 - 00:52] Here, the agent quotes seven hundred and twenty thousand dollars. MicroTruth queries Microburbs valuation models in real time, exposing an estimated value of eight hundred and five thousand dollars—a twelve percent underquote. We establish a realistic auction clearance corridor so buyers know their true competition before spending a dime on legal review."
        },
        {
            "slide_num": 4,
            "eyebrow": "SLIDE 4 OF 7 · THE SECRET WEAPON (TASKS 2 & 3)",
            "title": "Inside The Building Ledger",
            "bullets": [
                "Massive Municipal Ingestion: 112,457 leases, 81,079 sales, 6,597 public housing properties, 213,239 addresses.",
                "Sub-2ms SQLite WAL Queries: High-speed local address lookup directly in client/server architecture.",
                "What Agents Hide: Instantly surfaces 5 past unit sales ($1.38M) and 5 active leases ($1,700/wk) in the exact building."
            ],
            "metric_val": "213,239",
            "metric_lbl": "City of Sydney addresses indexed with inside-the-building transactions and public housing flags.",
            "notes": "[00:52 - 01:12] Click 'Inspect', and the side drawer slides in. We indexed over one hundred and twelve thousand leases and eighty-one thousand sales across Sydney in a high-speed SQLite engine. Browsing Unit 105 immediately surfaces the last five sales and leases inside this exact building that the agent chose not to mention."
        },
        {
            "slide_num": 5,
            "eyebrow": "SLIDE 5 OF 7 · MACHINE LEARNING RIGOR (TASKS 4 & 5)",
            "title": "Tasks 4 & 5 Machine Learning Rigor",
            "bullets": [
                "Task 4 Rents Model: Trained on 103,919 leases, validated on held-out 8,538 2026 leases.",
                "31.2% Error Reduction: Median Dollar Error slashed to $59.16/wk vs Microburbs baseline $86.00/wk.",
                "Task 5 City-Wide Valuation: Repeat-sales index + Hedonic GBDT valuing all 181,711 properties."
            ],
            "metric_val": "$59.16/wk",
            "metric_lbl": "Median Dollar Error achieved (vs $86.00 baseline). 69.83% of predictions within <= $100 error.",
            "notes": "[01:12 - 01:32] Behind the UI sits serious machine learning. For Task 4, our rental pricing model trained on one hundred and four thousand leases cut the median dollar error to fifty-nine dollars per week—beating the Microburbs baseline by over thirty-one percent. For Task 5, we valued all one hundred and eighty-one thousand properties across the City of Sydney."
        },
        {
            "slide_num": 6,
            "eyebrow": "SLIDE 6 OF 7 · TURNING INSIGHT INTO ACTION",
            "title": "The 1-Click Negotiation Weapon",
            "bullets": [
                "Automated Legal Offer Letters: Transforms Microburbs AVM figures and 90-day building comps into formal offers.",
                "Unyielding Evidence: Directly cites gross yields, recent block comps, and median auction clearance times.",
                "Instant Export: 1-click clipboard copy ready to paste into an email to the listing agent."
            ],
            "metric_val": "1 Click",
            "metric_lbl": "To generate an unyielding, data-backed buyer or tenant counter-offer letter.",
            "notes": "[01:32 - 01:48] Information without action is useless. MicroTruth turns suburb trends and inside-the-building comps into a formal, unyielding offer letter in one click. Buyers export a data-backed counter-offer directly to their clipboard ready to email the listing agent."
        },
        {
            "slide_num": 7,
            "eyebrow": "SLIDE 7 OF 7 · CONCLUSION",
            "title": "Leveling The Playing Field Before You Bid",
            "bullets": [
                "Full-Stack Craftsmanship: Working Manifest V3 extension, FastAPI backend, SQLite WAL engine.",
                "Rigorous Data Science: 31.2% error reduction on rents; 181,711 verified valuations.",
                "Real Human Utility: Eliminates asymmetric information for everyday Sydney buyers and tenants."
            ],
            "metric_val": "MicroTruth",
            "metric_lbl": "The property reality engine & negotiation weapon. Built for the Microburbs Hackathon 2026.",
            "notes": "[01:48 - 02:00] Production-grade machine learning, zero fake dashboards, and real human leverage. MicroTruth Sydney levels the playing field before you bid."
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)
        
        # Dark slide background
        bg_shape = slide.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5)) # 1 = MSO_SHAPE.RECTANGLE
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = BG_COLOR
        bg_shape.line.fill.background()

        # Eyebrow
        eyebrow_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11), Inches(0.4))
        tf = eyebrow_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = data["eyebrow"]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.5), Inches(1.1))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = data["title"]
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

        # Left Column: Bullets
        bullets_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(7.2), Inches(4.5))
        tf = bullets_box.text_frame
        tf.word_wrap = True
        for i, bullet in enumerate(data["bullets"]):
            p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
            p.text = "• " + bullet
            p.font.size = Pt(16)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(22)

        # Right Column: Metric Card
        card = slide.shapes.add_shape(1, Inches(8.3), Inches(2.2), Inches(4.2), Inches(3.8))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = RGBColor(40, 55, 85)
        card.line.width = Pt(1.5)

        card_tf = card.text_frame
        card_tf.word_wrap = True
        p_val = card_tf.paragraphs[0]
        p_val.text = data["metric_val"]
        p_val.font.size = Pt(44)
        p_val.font.bold = True
        p_val.font.color.rgb = ACCENT
        p_val.alignment = PP_ALIGN.CENTER
        p_val.space_after = Pt(14)

        p_lbl = card_tf.add_paragraph()
        p_lbl.text = data["metric_lbl"]
        p_lbl.font.size = Pt(14)
        p_lbl.font.color.rgb = TEXT_MUTED
        p_lbl.alignment = PP_ALIGN.CENTER

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.4))
        tf_f = footer_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "MicroTruth Sydney — Team Oneshot (team-29) · Microburbs Hackathon 2026"
        p_f.font.size = Pt(11)
        p_f.font.color.rgb = TEXT_MUTED

        # Speaker Notes (Verbatim Kokoro Voiceover)
        notes_slide = slide.notes_slide
        tf_notes = notes_slide.notes_text_frame
        tf_notes.text = data["notes"]

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation", "pitch_deck.pptx"))
    prs.save(out_path)
    print(f"Presentation saved to {out_path}")
    return out_path

if __name__ == "__main__":
    build_deck()
