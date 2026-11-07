import { chromium } from "playwright";

async function testUI() {
  console.log("Starting Headless UI & Extension Integrity Test...");
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-gpu"]
  });

  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  const consoleErrors = [];
  page.on("console", msg => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });

  console.log("1. Navigating to http://127.0.0.1:8000/domain-listing.html...");
  await page.goto("http://127.0.0.1:8000/domain-listing.html", { waitUntil: "networkidle" });

  // 1. Check in-page reality badge
  console.log("2. Checking Underquote Reality Badge...");
  const badge = page.locator("#microtruth-inpage-badge");
  await badge.waitFor({ state: "visible", timeout: 5000 });
  const badgeText = await badge.innerText();
  console.log("   Badge text found:", badgeText.replace(/\n+/g, " "));
  if (!badgeText.includes("720,000") || !badgeText.includes("805,500")) {
    throw new Error("Badge missing price numbers!");
  }

  // 2. Click inspect button
  console.log("3. Clicking 'Inspect Full Truth →'...");
  const inspectBtn = page.locator("#microtruth-inspect-btn");
  await inspectBtn.click();
  await page.waitForTimeout(1000);

  // 3. Check drawer iframe
  console.log("4. Verifying side drawer frame...");
  const drawerFrame = page.frameLocator(".microtruth-drawer-frame");
  const drawerBody = drawerFrame.locator("body");
  await drawerBody.waitFor({ state: "visible", timeout: 5000 });

  // 4. Verify Suburb Boundary Map & Market Metrics
  console.log("5. Verifying Suburb Map & Market Metrics...");
  const marketGrid = drawerFrame.locator(".market-metrics-grid");
  await marketGrid.waitFor({ state: "visible", timeout: 5000 });
  const marketText = await marketGrid.innerText();
  console.log("   Market metrics:", marketText.replace(/\n+/g, " | "));

  // 5. Verify Building Ledger tabs
  console.log("6. Verifying Building Ledger...");
  const salesTab = drawerFrame.locator("#tab-sales");
  const leasesTab = drawerFrame.locator("#tab-leases");
  await salesTab.click();
  await page.waitForTimeout(300);
  const salesList = drawerFrame.locator("#comps-sales-list");
  const salesCount = await salesList.locator(".comp-row").count();
  console.log(`   Past sales count: ${salesCount}`);

  await leasesTab.click();
  await page.waitForTimeout(300);
  const leasesList = drawerFrame.locator("#comps-leases-list");
  const leasesCount = await leasesList.locator(".comp-row").count();
  console.log(`   Past leases count: ${leasesCount}`);

  if (salesCount === 0 || leasesCount === 0) {
    throw new Error("Building ledger empty!");
  }

  // 6. Test Offer Letter Generator
  console.log("7. Verifying Offer Letter Generator...");
  const offerBtn = drawerFrame.locator("#btn-generate-letter");
  await offerBtn.click();
  await page.waitForTimeout(500);
  const letterBox = drawerFrame.locator("#letter-text");
  await letterBox.waitFor({ state: "visible", timeout: 5000 });
  const letterText = await letterBox.inputValue();
  console.log("   Generated letter preview:", letterText.slice(0, 120) + "...");

  if (!letterText.includes("Waterloo") || !letterText.includes("Microburbs")) {
    throw new Error("Offer letter incomplete!");
  }

  await browser.close();

  if (consoleErrors.length > 0) {
    console.warn("⚠️ Console errors detected:", consoleErrors);
  } else {
    console.log("✅ Zero Console Errors! All UI Integrity Checks PASSED!");
  }
}

testUI().catch(err => {
  console.error("UI Test Failed:", err);
  process.exit(1);
});
