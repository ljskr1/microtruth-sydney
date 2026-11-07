import { chromium } from "playwright";
import path from "path";
import fs from "fs";

const RECORDINGS_DIR = path.resolve("recordings");
if (!fs.existsSync(RECORDINGS_DIR)) {
  fs.mkdirSync(RECORDINGS_DIR, { recursive: true });
}

async function record() {
  console.log("Launching Playwright Chromium at 1920x1080...");
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-gpu"]
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: RECORDINGS_DIR,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();
  console.log("Navigating to http://127.0.0.1:8000/domain-listing.html...");
  await page.goto("http://127.0.0.1:8000/domain-listing.html", { waitUntil: "networkidle" });
  await page.waitForTimeout(2000);

  // 1. Initial view: User scrolls down the Domain listing (0 - 6s)
  console.log("Step 1: Scrolling Domain listing...");
  await page.mouse.move(960, 300, { steps: 15 });
  await page.mouse.wheel(0, 250);
  await page.waitForTimeout(1500);

  // 2. Cursor glides to the price guide and the MicroTruth badge (6 - 14s)
  console.log("Step 2: Hovering over MicroTruth Reality Badge...");
  const badgeBox = await page.locator("#microtruth-inpage-badge").boundingBox();
  if (badgeBox) {
    await page.mouse.move(badgeBox.x + 200, badgeBox.y + 40, { steps: 25 });
    await page.waitForTimeout(2000);
    // Hover over the inspect button
    const btnBox = await page.locator("#microtruth-inspect-btn").boundingBox();
    if (btnBox) {
      await page.mouse.move(btnBox.x + btnBox.width / 2, btnBox.y + btnBox.height / 2, { steps: 20 });
      await page.waitForTimeout(1500);
      console.log("Step 3: Clicking 'Inspect Full Truth →'...");
      await page.mouse.click(btnBox.x + btnBox.width / 2, btnBox.y + btnBox.height / 2);
    }
  }

  // 3. Side drawer slides in (14 - 18s)
  await page.waitForTimeout(2500);

  // 4. Interact with the iframe drawer (18 - 38s)
  console.log("Step 4: Interacting inside The Facts side drawer...");
  const frameElement = page.frameLocator(".microtruth-drawer-frame");

  // Move cursor inside the side drawer
  await page.mouse.move(1650, 200, { steps: 20 });
  await page.waitForTimeout(1500);

  // Hover over the Suburb Polygon Map
  const mapLocator = frameElement.locator(".suburb-map-wrapper");
  if (await mapLocator.count() > 0) {
    const mapBox = await mapLocator.boundingBox();
    if (mapBox) {
      await page.mouse.move(mapBox.x + mapBox.width / 2, mapBox.y + mapBox.height / 2, { steps: 15 });
      await page.waitForTimeout(2000);
    }
  }

  // Hover over Market Metrics ($1.935M, +4.7%, 27 Days)
  const marketLocator = frameElement.locator(".market-metrics-grid");
  if (await marketLocator.count() > 0) {
    const mBox = await marketLocator.boundingBox();
    if (mBox) {
      await page.mouse.move(mBox.x + mBox.width / 2, mBox.y + mBox.height / 2, { steps: 15 });
      await page.waitForTimeout(2000);
    }
  }

  // Scroll down inside the drawer to Building Ledger
  console.log("Step 5: Inspecting Building Sales & Leases...");
  await page.mouse.move(1650, 400, { steps: 10 });
  await page.mouse.wheel(0, 350);
  await page.waitForTimeout(2000);

  // Click 'Past Leases' tab
  const leasesTab = frameElement.locator("#tab-leases");
  if (await leasesTab.count() > 0) {
    const lBox = await leasesTab.boundingBox();
    if (lBox) {
      await page.mouse.move(lBox.x + lBox.width / 2, lBox.y + lBox.height / 2, { steps: 15 });
      await page.mouse.click(lBox.x + lBox.width / 2, lBox.y + lBox.height / 2);
      await page.waitForTimeout(2500);
    }
  }

  // Scroll to Rental Reality Check & Offer Letter (32 - 40s)
  console.log("Step 6: Rental Reality Check & Formal Offer Letter...");
  await page.mouse.wheel(0, 450);
  await page.waitForTimeout(2000);

  const offerBtn = frameElement.locator("#btn-generate-letter");
  if (await offerBtn.count() > 0) {
    const oBox = await offerBtn.boundingBox();
    if (oBox) {
      await page.mouse.move(oBox.x + oBox.width / 2, oBox.y + oBox.height / 2, { steps: 15 });
      await page.mouse.click(oBox.x + oBox.width / 2, oBox.y + oBox.height / 2);
      await page.waitForTimeout(3000);
    }
  }

  console.log("Finishing recording session...");
  await page.waitForTimeout(2000);

  const video = page.video();
  await context.close();
  await browser.close();

  const videoPath = await video.path();
  console.log(`Video saved to: ${videoPath}`);

  // Rename to raw_take.webm
  const destPath = path.join(RECORDINGS_DIR, "raw_take.webm");
  fs.copyFileSync(videoPath, destPath);
  console.log(`Copied raw take to: ${destPath}`);
}

record().catch(err => {
  console.error("Recording failed:", err);
  process.exit(1);
});
