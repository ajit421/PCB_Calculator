// PERFECT SYNCHRONIZATION SYSTEM - REAL TIME
let isSyncing = false;
const userModifiedInputs = new Set();

// Track which calculator triggered the sync
let syncSource = null;

function initializeSynchronization() {
  console.log("Perfect synchronization system initialized");

  // Track user modifications on ALL inputs
  document.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", function (e) {
      if (!isSyncing) {
        userModifiedInputs.add(this.id);

        // Determine which calculator triggered the change
        const tab = findParentTab(this);
        syncSource = tab;

        // INSTANT SYNC - No delays
        perfectSync();
      }
    });
  });
}

function findParentTab(element) {
  let parent = element;
  while (parent && !parent.classList.contains("tab-content")) {
    parent = parent.parentElement;
  }
  return parent ? parent.id : null;
}

// PERFECT SYNC - Real-time bidirectional sync
function perfectSync() {
  if (isSyncing) return;
  isSyncing = true;

  try {
    // Get current active tab
    const activeTabElement = document.querySelector(".tab-link.active");
    const currentTab = activeTabElement
      ? activeTabElement.getAttribute("data-tab")
      : "motor";

    console.log("Sync triggered from:", syncSource, "Current tab:", currentTab);

    // SYNC BASED ON SOURCE
    if (syncSource === "motor" || !syncSource) {
      syncMotorToAll();
    }
    if (syncSource === "trace") {
      syncTraceToAll();
    }
    if (syncSource === "magnet") {
      syncMagnetToAll();
    }

    // Always sync power loss from trace to motor
    syncPowerLoss();
  } catch (error) {
    console.warn("Sync error:", error);
  } finally {
    isSyncing = false;
    syncSource = null;
  }
}

// SYNC MOTOR TO ALL OTHER CALCULATORS
function syncMotorToAll() {
  console.log("Syncing Motor to All...");

  // Get ALL motor input values
  const motorInputs = {
    current: getInputValue("current"),
    remanence: getInputValue("remanence"),
    height: getInputValue("pmRotorHeight"),
    parallelConstant: getInputValue("motorParallelConstant"),
  };

  // SYNC TO TRACE
  if (motorInputs.current && !userModifiedInputs.has("tracecurrent")) {
    setInputValue("tracecurrent", motorInputs.current, true);
  }

  // SYNC TO MAGNET
  if (motorInputs.remanence && !userModifiedInputs.has("blockremanence")) {
    setInputValue("blockremanence", motorInputs.remanence, true);
  }
  if (motorInputs.height && !userModifiedInputs.has("blockheight")) {
    setInputValue("blockheight", motorInputs.height, true);
  }
  if (
    motorInputs.parallelConstant &&
    !userModifiedInputs.has("blockParallelConstant")
  ) {
    setInputValue("blockParallelConstant", motorInputs.parallelConstant, true);
  }

  // Sync motor results to other calculators
  if (window.motorResults) {
    syncMotorResultsToOthers();
  }
}

// SYNC TRACE TO ALL OTHER CALCULATORS
function syncTraceToAll() {
  console.log("Syncing Trace to All...");

  // Get trace current
  const traceCurrent = getInputValue("tracecurrent");

  // SYNC TO MOTOR
  if (traceCurrent && !userModifiedInputs.has("current")) {
    setInputValue("current", traceCurrent, true);
  }

  // Force power loss sync
  syncPowerLoss();
}

// SYNC MAGNET TO ALL OTHER CALCULATORS
function syncMagnetToAll() {
  console.log("Syncing Magnet to All...");

  // Get magnet input values
  const magnetInputs = {
    remanence: getInputValue("blockremanence"),
    height: getInputValue("blockheight"),
    parallelConstant: getInputValue("blockParallelConstant"),
  };

  // SYNC TO MOTOR
  if (magnetInputs.remanence && !userModifiedInputs.has("remanence")) {
    setInputValue("remanence", magnetInputs.remanence, true);
  }
  if (magnetInputs.height && !userModifiedInputs.has("pmRotorHeight")) {
    setInputValue("pmRotorHeight", magnetInputs.height, true);
  }
  if (
    magnetInputs.parallelConstant &&
    !userModifiedInputs.has("motorParallelConstant")
  ) {
    setInputValue("motorParallelConstant", magnetInputs.parallelConstant, true);
  }
}

// SYNC MOTOR RESULTS TO OTHER CALCULATORS
function syncMotorResultsToOthers() {
  const mr = window.motorResults;

  // Copper thickness to trace
  if (
    mr.reqCopperThickness !== null &&
    isFinite(mr.reqCopperThickness) &&
    !userModifiedInputs.has("tracethickness")
  ) {
    setInputValue("tracethickness", mr.reqCopperThickness.toFixed(4), true);
  }

  // Trace length to trace
  if (
    mr.twoPhase !== null &&
    isFinite(mr.twoPhase) &&
    !userModifiedInputs.has("tracelengthinput")
  ) {
    const lenMm = (mr.twoPhase * 1000).toFixed(4);
    setInputValue("tracelengthinput", lenMm, true);

    // Also set unit to mm
    const traceUnit = document.getElementById("tracetraceUnit");
    if (traceUnit) traceUnit.value = "mm";
  }

  // Dimensions to magnet
  if (
    mr.widthOD !== null &&
    isFinite(mr.widthOD) &&
    !userModifiedInputs.has("blockwidthod")
  ) {
    setInputValue("blockwidthod", mr.widthOD.toFixed(4), true);
  }
  if (
    mr.widthID !== null &&
    isFinite(mr.widthID) &&
    !userModifiedInputs.has("blockwidthid")
  ) {
    setInputValue("blockwidthid", mr.widthID.toFixed(4), true);
  }
  if (
    mr.traceLengthRadial !== null &&
    isFinite(mr.traceLengthRadial) &&
    !userModifiedInputs.has("blocklength")
  ) {
    setInputValue("blocklength", mr.traceLengthRadial.toFixed(4), true);
  }
}

// SYNC POWER LOSS FROM TRACE TO MOTOR (CRITICAL)
function syncPowerLoss() {
  if (window.traceResults && window.traceResults.internal) {
    const tracePowerLoss = window.traceResults.internal.powerLoss;
    if (tracePowerLoss !== null && isFinite(tracePowerLoss)) {
      window.syncedCopperLossFromTrace = tracePowerLoss;
      console.log("Power Loss Synced to Motor:", tracePowerLoss, "W");

      // Force motor recalculation with updated power loss
      if (typeof calculateMotorParameters === "function") {
        calculateMotorParameters();
      }
    }
  }
}

// HELPER FUNCTIONS
function getInputValue(id) {
  const element = document.getElementById(id);
  return element ? element.value : null;
}

function setInputValue(id, value, triggerUpdate = false) {
  const element = document.getElementById(id);
  if (element && element.value !== value) {
    element.value = value;
    if (triggerUpdate) {
      // Trigger the appropriate calculator update
      if (id.includes("trace")) {
        if (typeof window.updateTraceResults === "function") {
          window.updateTraceResults();
        }
      } else if (id.includes("block") || id.includes("ring")) {
        if (typeof calculateMagneticField === "function") {
          calculateMagneticField();
        }
      }
    }
    return true;
  }
  return false;
}

// Force recalculation of all calculators
function recalculateAll() {
  if (typeof calculateMotorParameters === "function")
    calculateMotorParameters();
  if (typeof window.updateTraceResults === "function")
    window.updateTraceResults();
  if (typeof calculateMagneticField === "function") calculateMagneticField();
}

// Initialize synchronization
document.addEventListener("DOMContentLoaded", function () {
  initializeSynchronization();

  // Initial sync after everything loads
  setTimeout(() => {
    perfectSync();
    recalculateAll();
  }, 1500);
});

// Debug functions
window.perfectSync = perfectSync;
window.recalculateAll = recalculateAll;
window.getUserModifiedInputs = () => userModifiedInputs;
window.resetAllUserModified = () => {
  userModifiedInputs.clear();
  console.log("All user modifications reset");
  perfectSync();
};
