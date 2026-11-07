import { chromium } from "playwright";
import path from "path";
import fs from "fs";

const RECORDINGS_DIR = path.resolve("recordings");
if (!fs.existsSync(RECORDINGS_DIR)) {
  fs.mkdirSync(RECORDINGS_DIR, { recursive: true });
}

async function record() {
  console.log("Launching Playwright Chromium at 1920x1080 for 44-second showcase...");
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
  
  // 1. Initial view: User scrolls smoothly down the Domain listing (0.0s - 5.5s)
  console.log("Step 1: Exploring Domain listing (0.0s - 5.5s)...");
  await page.waitForTimeout(2000);
  await page.mouse.move(960, 320, { steps: 20 });
  await page.mouse.wheel(0, 320);
  await page.waitForTimeout(2500);

  // 2. Cursor glides to the price guide and the MicroTruth Reality Badge (5.5s - 12.0s)
  console.log("Step 2: Inspecting MicroTruth Underquote Reality Badge (5.5s - 12.0s)...");
  const badgeBox = await page.locator("#microtruth-inpage-badge").boundingBox();
  if (badgeBox) {
    await page.mouse.move(badgeBox.x + 220, badgeBox.y + 45, { steps: 25 });
    await page.waitForTimeout(3500);
    
    // Hover over the inspect button
    const btnBox = await page.locator("#microtruth-inspect-btn").boundingBox();
    if (btnBox) {
      await page.mouse.move(btnBox.x + btnBox.width / 2, btnBox.y + btnBox.height / 2, { steps: 20 });
      await page.waitForTimeout(2000);
      
      // 3. Click 'Inspect Full Truth →' (12.0s - 16.5s)
      console.log("Step 3: Clicking 'Inspect Full Truth →' (12.0s - 16.5s)...");
      await page.mouse.click(btnBox.x + btnBox.width / 2, btnBox.y + btnBox.height / 2);
    }
  }

  // Drawer slides in and settles
  await page.waitForTimeout(3000);

  // 4. Interact with the side drawer: Suburb Map & 3 Market Signals (16.5s - 24.5s)
  console.log("Step 4: Interacting inside The Facts side drawer (16.5s - 24.5s)...");
  const frameElement = page.frameLocator(".microtruth-drawer-frame");

  await page.mouse.move(1650, 180, { steps: 20 });
  await page.waitForTimeout(1500);

  // Hover over the Suburb Polygon Map
  const mapLocator = frameElement.locator(".suburb-map-wrapper");
  if (await mapLocator.count() > 0) {
    const mapBox = await mapLocator.boundingBox();
    if (mapBox) {
      await page.mouse.move(mapBox.x + mapBox.width / 2, mapBox.y + mapBox.height / 2, { steps: 20 });
      await page.waitForTimeout(2500);
    }
  }

  // Hover over Market Metrics ($1.935M, +4.7%, 27 Days)
  const marketLocator = frameElement.locator(".market-metrics-grid");
  if (await marketLocator.count() > 0) {
    const mBox = await marketLocator.boundingBox();
    if (mBox) {
      await page.mouse.move(mBox.x + mBox.width / 2, mBox.y + mBox.height / 2, { steps: 20 });
      await page.waitForTimeout(3000);
    }
  }

  // 5. Scroll down inside the drawer to Inside The Building Ledger (24.5s - 33.5s)
  console.log("Step 5: Inspecting Building Sales & Leases (24.5s - 33.5s)...");
  await page.mouse.move(1650, 420, { steps: 15 });
  await page.mouse.wheel(0, 360);
  await page.waitForTimeout(2500);

  // Hover on recent unit sales
  const salesTable = frameElement.locator("#sales-list");
  if (await salesTable.count() > 0) {
    await page.mouse.move(1650, 480, { steps: 15 });
    await page.waitForTimeout(2000);
  }

  // Click 'Past Leases' tab
  const leasesTab = frameElement.locator("#tab-leases");
  if (await leasesTab.count() > 0) {
    const lBox = await leasesTab.boundingBox();
    if (lBox) {
      await page.mouse.move(lBox.x + lBox.width / 2, lBox.y + lBox.height / 2, { steps: 15 });
      await page.mouse.click(lBox.x + lBox.width / 2, lBox.y + lBox.height / 2);
      await page.waitForTimeout(3500);
    }
  }

  // 6. Scroll to Rental Reality Check & Formal Offer Letter (33.5s - 41.0s)
  console.log("Step 6: Rental Reality Check & Formal Offer Letter (33.5s - 41.0s)...");
  await page.mouse.wheel(0, 420);
  await page.waitForTimeout(2500);

  const offerBtn = frameElement.locator("#btn-generate-letter");
  if (await offerBtn.count() > 0) {
    const oBox = await offerBtn.boundingBox();
    if (oBox) {
      await page.mouse.move(oBox.x + oBox.width / 2, oBox.y + oBox.height / 2, { steps: 15 });
      await page.mouse.click(oBox.x + oBox.width / 2, oBox.y + oBox.height / 2);
      await page.waitForTimeout(4000);
    }
  }

  // 7. Final settling view (41.0s - 44.0s)
  console.log("Step 7: Final settling view (41.0s - 44.0s)...");
  await page.waitForTimeout(3000);

  console.log("Finishing 44-second recording session...");
  const video = page.video();
  await context.close();
  await browser.close();

  const videoPath = await video.path();
  console.log(`Video saved to: ${videoPath}`);

  // Copy to raw_take_45s.mp4 and raw_take.mp4
  const destWebm = path.join(RECORDINGS_DIR, "raw_take_45s.webm");
  const destMp4 = path.join(RECORDINGS_DIR, "raw_take_45s.mp4");
  fs.copyFileSync(videoPath, destWebm);
  
  // Transcode to MP4 with high quality H.264
  console.log("Transcoding to 1080p MP4...");
  const ffmpegCmd = `ffmpeg -y -i "${destWebm}" -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p "${destMp4}" -loglevel error`;
  const { execSync } = await import("child_process");
  execSync(ffmpegCmd);
  
  // Also update raw_take.mp4 for OpenScreen
  const mainRawMp4 = path.join(RECORDINGS_DIR, "raw_take.mp4");
  fs.copyFileSync(destMp4, mainRawMp4);
  console.log(`Successfully recorded and saved 44s take to ${destMp4} and ${mainRawMp4}`);
}

record().catch(err => {
  console.error("Recording failed:", err);
  process.exit(1);
});
