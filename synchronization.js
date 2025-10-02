// INSTANT SYNCHRONIZATION SYSTEM - ZERO DELAY
let isSyncing = false;
const userModifiedInputs = new Set();

function initializeSynchronization() {
  console.log("Instant synchronization system initialized");

  // Track user modifications
  document.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", function () {
      if (!isSyncing) {
        userModifiedInputs.add(this.id);
        // INSTANT SYNC on every input change
        setTimeout(instantSync, 10);
      }
    });
  });
}

// INSTANT SYNC - No delays
function instantSync() {
  if (isSyncing) return;
  isSyncing = true;

  try {
    // SYNC ALL CALCULATORS IN BOTH DIRECTIONS
    syncAllCalculators();
  } catch (error) {
    console.warn("Sync error:", error);
  } finally {
    isSyncing = false;
  }
}

function syncAllCalculators() {
  // Get current input values from ALL calculators
  const motorCurrent = document.getElementById("current")?.value;
  const traceCurrent = document.getElementById("tracecurrent")?.value;
  const motorRemanence = document.getElementById("remanence")?.value;
  const magnetRemanence = document.getElementById("blockremanence")?.value;

  // SYNC CURRENT: Motor <-> Trace
  if (motorCurrent && !userModifiedInputs.has("tracecurrent")) {
    const traceCurrentEl = document.getElementById("tracecurrent");
    if (traceCurrentEl && traceCurrentEl.value !== motorCurrent) {
      traceCurrentEl.value = motorCurrent;
      if (typeof window.updateTraceResults === "function") {
        window.updateTraceResults();
      }
    }
  }

  if (traceCurrent && !userModifiedInputs.has("current")) {
    const motorCurrentEl = document.getElementById("current");
    if (motorCurrentEl && motorCurrentEl.value !== traceCurrent) {
      motorCurrentEl.value = traceCurrent;
      if (typeof calculateMotorParameters === "function") {
        calculateMotorParameters();
      }
    }
  }

  // SYNC REMANENCE: Motor <-> Magnet
  if (motorRemanence && !userModifiedInputs.has("blockremanence")) {
    const magnetRemanenceEl = document.getElementById("blockremanence");
    if (magnetRemanenceEl && magnetRemanenceEl.value !== motorRemanence) {
      magnetRemanenceEl.value = motorRemanence;
      if (typeof calculateMagneticField === "function") {
        calculateMagneticField();
      }
    }
  }

  if (magnetRemanence && !userModifiedInputs.has("remanence")) {
    const motorRemanenceEl = document.getElementById("remanence");
    if (motorRemanenceEl && motorRemanenceEl.value !== magnetRemanence) {
      motorRemanenceEl.value = magnetRemanence;
      if (typeof calculateMotorParameters === "function") {
        calculateMotorParameters();
      }
    }
  }

  // SYNC OTHER PARAMETERS
  syncOtherParameters();
}

function syncOtherParameters() {
  // Sync from Motor Results to other calculators
  if (window.motorResults) {
    const mr = window.motorResults;

    // Copper thickness sync
    if (
      mr.reqCopperThickness !== null &&
      isFinite(mr.reqCopperThickness) &&
      !userModifiedInputs.has("tracethickness")
    ) {
      const traceThickness = document.getElementById("tracethickness");
      if (traceThickness) {
        const newValue = mr.reqCopperThickness.toFixed(4);
        if (traceThickness.value !== newValue) {
          traceThickness.value = newValue;
          if (typeof window.updateTraceResults === "function") {
            window.updateTraceResults();
          }
        }
      }
    }

    // Trace length sync
    if (
      mr.twoPhase !== null &&
      isFinite(mr.twoPhase) &&
      !userModifiedInputs.has("tracelengthinput")
    ) {
      const traceLength = document.getElementById("tracelengthinput");
      if (traceLength) {
        const lenMm = (mr.twoPhase * 1000).toFixed(4);
        if (traceLength.value !== lenMm) {
          traceLength.value = lenMm;
          const traceUnit = document.getElementById("tracetraceUnit");
          if (traceUnit) traceUnit.value = "mm";
          if (typeof window.updateTraceResults === "function") {
            window.updateTraceResults();
          }
        }
      }
    }
  }

  // SYNC POWER LOSS: Trace -> Motor (THIS IS CRITICAL)
  if (window.traceResults && window.traceResults.internal) {
    const tracePowerLoss = window.traceResults.internal.powerLoss;
    if (tracePowerLoss !== null && isFinite(tracePowerLoss)) {
      window.syncedCopperLossFromTrace = tracePowerLoss;

      // Force motor recalculation with trace power loss
      if (typeof calculateMotorParameters === "function") {
        calculateMotorParameters();
      }
    }
  }
}

// Initialize synchronization
document.addEventListener("DOMContentLoaded", function () {
  initializeSynchronization();

  // Initial sync after everything loads
  setTimeout(() => {
    instantSync();
  }, 1000);
});
