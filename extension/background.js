// MicroTruth Sydney Background Service Worker (Manifest V3)

chrome.runtime.onInstalled.addListener(() => {
  console.log("MicroTruth Sydney Extension Installed.");
  // Configure side panel to open upon extension action click
  if (chrome.sidePanel && chrome.sidePanel.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(err => {
      console.warn("Could not set panel behavior:", err);
    });
  }
});

// Relay listing detection and storage across content script and side panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "LISTING_DETECTED") {
    chrome.storage.local.set({
      currentListing: message.data,
      lastUpdated: Date.now()
    }, () => {
      sendResponse({ status: "saved" });
    });
    return true; // async sendResponse
  }

  if (message.type === "OPEN_SIDEPANEL") {
    if (chrome.sidePanel && chrome.sidePanel.open && sender.tab?.id) {
      chrome.sidePanel.open({ tabId: sender.tab.id }).catch(err => {
        console.warn("Could not open side panel:", err);
      });
      sendResponse({ status: "opened" });
    } else {
      sendResponse({ status: "unsupported" });
    }
    return true;
  }
});
