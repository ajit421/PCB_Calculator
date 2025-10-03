// Global variables
window.motorResults = null;
window.traceResults = null;
window.traceInputs = null;
window.magnetResults = null;
window.syncedCopperLossFromTrace = null;

// DOM Content Loaded
document.addEventListener("DOMContentLoaded", function () {
  initializeDarkMode();
  initializeTabSystem();
  initializePDFDownload();
  initializeGlobalEventListeners();
});

// Dark Mode Toggle
function initializeDarkMode() {
  const darkModeToggle = document.getElementById("darkModeToggle");
  const body = document.body;

  if (!darkModeToggle) {
    console.warn("Dark mode toggle button not found");
    return;
  }

  darkModeToggle.addEventListener("click", () => {
    body.classList.toggle("dark-mode");
    darkModeToggle.textContent = body.classList.contains("dark-mode")
      ? "Light Mode"
      : "Dark Mode";

    // Save preference to localStorage
    localStorage.setItem("darkMode", body.classList.contains("dark-mode"));
  });

  // Load saved preference
  if (localStorage.getItem("darkMode") === "true") {
    body.classList.add("dark-mode");
    darkModeToggle.textContent = "Light Mode";
  }
}

// Tab Switching System
function initializeTabSystem() {
  const mainTabLinks = document.querySelectorAll(".tab-link");
  const mainTabContents = document.querySelectorAll(".tab-content");

  if (mainTabLinks.length === 0) {
    console.warn("No tab links found");
    return;
  }

  mainTabLinks.forEach((link) => {
    link.addEventListener("click", () => {
      const tabId = link.getAttribute("data-tab");

      if (!tabId) {
        console.warn("Tab link missing data-tab attribute");
        return;
      }

      // Update active tab
      mainTabLinks.forEach((item) => item.classList.remove("active"));
      mainTabContents.forEach((item) => item.classList.remove("active"));
      link.classList.add("active");

      const targetTab = document.getElementById(tabId);
      if (targetTab) {
        targetTab.classList.add("active");
      } else {
        console.warn(`Tab content with id '${tabId}' not found`);
        return;
      }

      // Trigger recalculation for active tab
      setTimeout(() => {
        switch (tabId) {
          case "motor":
            if (typeof calculateMotorParameters === "function") {
              calculateMotorParameters();
            }
            break;
          case "trace":
            if (typeof window.updateTraceResults === "function") {
              window.updateTraceResults();
            }
            break;
          case "magnet":
            if (typeof calculateMagneticField === "function") {
              calculateMagneticField();
            }
            break;
          default:
            console.warn(`Unknown tab: ${tabId}`);
        }

        // Sync after tab switch
        if (typeof syncGlobal === "function") {
          setTimeout(syncGlobal, 50);
        }
      }, 100);
    });
  });
}

// PDF Download Handler
function initializePDFDownload() {
  const downloadButton = document.getElementById("downloadFullReport");
  if (!downloadButton) {
    console.warn("PDF download button not found");
    return;
  }

  downloadButton.addEventListener("click", function () {
    if (typeof generateCombinedPDF === "function") {
      generateCombinedPDF();
    } else {
      showToast("PDF generation not available", true);
    }
  });
}

// Global Event Listeners
function initializeGlobalEventListeners() {
  // Add any global event listeners here
  console.log("Global event listeners initialized");
}

// Utility Functions
function showLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "flex";
}

function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "none";
}

function showToast(message, isError = false) {
  const toast = document.getElementById("toastNotification");
  if (!toast) {
    console.warn("Toast notification element not found");
    return;
  }

  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ✅ FIXED: Added = operator for default parameter
function getSafeNumber(id, defaultValue) {
  const element = document.getElementById(id);
  if (!element) {
    console.warn(`Element with id '${id}' not found`);
    return defaultValue;
  }

  const value = parseFloat(element.value);
  if (isNaN(value) || value < 0) {
    element.value = defaultValue;
    return defaultValue;
  }
  return value;
}

// Unit Conversion Utilities
const MM_PER_MIL = 0.0254;
const MIL_PER_OZ = 1.3779527559055116;

function milToMm(mil) {
  if (isNaN(mil)) return 0;
  return mil * MM_PER_MIL;
}

function mmToMil(mm) {
  if (isNaN(mm)) return 0;
  return mm / MM_PER_MIL;
}

function ozToMil(oz) {
  if (isNaN(oz)) return 0;
  return oz * MIL_PER_OZ;
}

function cToF(c) {
  if (isNaN(c)) return 0;
  return (c * 9) / 5 + 32;
}

function fToC(f) {
  if (isNaN(f)) return 0;
  return ((f - 32) * 5) / 9;
}

// Additional utility functions
function formatNumber(value, decimals = 6) {
  if (value === null || value === undefined || isNaN(value)) return "N/A";
  return Number(value).toFixed(decimals);
}

// Add to main.js
function validateInput(element, min = 0, max = Infinity) {
    const value = parseFloat(element.value);
    if (isNaN(value) || value < min || value > max) {
        element.style.borderColor = "#e74c3c";
        return false;
    }
    element.style.borderColor = "#27ae60";
    return true;
}

function validateNumber(value, min = 0, max = Infinity) {
  const num = parseFloat(value);
  return !isNaN(num) && num >= min && num <= max;
}

// Export for debugging
window.debugGlobals = () => {
  return {
    motorResults: window.motorResults,
    traceResults: window.traceResults,
    traceInputs: window.traceInputs,
    magnetResults: window.magnetResults,
    syncedCopperLoss: window.syncedCopperLossFromTrace,
  };
};
