// Magnet Calculator
function calculateMagneticField() {
  try {
    const activeTab = getActiveMagnetTab();
    const inputs = getMagnetInputs(activeTab);

    // Validate inputs
    if (!validateMagnetInputs(activeTab, inputs)) return;

    const result = performMagnetCalculation(activeTab, inputs);

    displayMagnetResult(result, activeTab, inputs);

    // Store results globally
    window.magnetResults = {
      activeTab,
      result,
      inputs,
    };

    // instant synchronization
    if (typeof instantSync === "function") {
      setTimeout(instantSync, 10);
    }
  } catch (error) {
    console.error("Magnet calculation error:", error);
    displayMagnetError("Calculation error: " + error.message);
  }
}

function getActiveMagnetTab() {
  const activeSection = document.querySelector(
    "#magnet .calculator-section.active"
  );
  return activeSection ? activeSection.id : "block";
}

function getMagnetInputs(activeTab) {
  if (activeTab === "block") {
    return {
      remanence: getSafeNumber("blockremanence"),
      height: getSafeNumber("blockheight"),
      length: getSafeNumber("blocklength"),
      widthOD: getSafeNumber("blockwidthod"),
      widthID: getSafeNumber("blockwidthid"),
      blockParallelConstant: getSafeNumber("blockParallelConstant"),
    };
  } else {
    return {
      remanence: getSafeNumber("ringremanence"),
      height: getSafeNumber("ringheight"),
      od: getSafeNumber("ringod"),
      id: getSafeNumber("ringid"),
    };
  }
}

function validateMagnetInputs(activeTab, inputs) {
  if (activeTab === "block") {
    if (inputs.remanence <= 0) {
      displayMagnetError("Remanence must be greater than 0");
      return false;
    }
    if (inputs.height <= 0) {
      displayMagnetError("Height must be greater than 0");
      return false;
    }
    if (inputs.length <= 0) {
      displayMagnetError("Length must be greater than 0");
      return false;
    }
    if (inputs.widthOD <= 0 || inputs.widthID <= 0) {
      displayMagnetError("Width values must be greater than 0");
      return false;
    }
    if (
      inputs.blockParallelConstant < 0.1 ||
      inputs.blockParallelConstant > 2.0
    ) {
      displayMagnetError(
        "Parallel Stacking Constant must be between 0.1 and 2.0"
      );
      return false;
    }
  } else {
    if (inputs.remanence <= 0) {
      displayMagnetError("Remanence must be greater than 0");
      return false;
    }
    if (inputs.height <= 0) {
      displayMagnetError("Height must be greater than 0");
      return false;
    }
    if (inputs.od <= inputs.id) {
      displayMagnetError("Outer diameter must be greater than inner diameter");
      return false;
    }
  }
  return true;
}

function performMagnetCalculation(activeTab, inputs) {
  if (activeTab === "block") {
    return calculateBlockMagnet(inputs);
  } else {
    return calculateRingMagnet(inputs);
  }
}

function calculateBlockMagnet(inputs) {
  const { remanence, height, length, widthOD, widthID, blockParallelConstant } =
    inputs;

  // Validate inputs
  if (
    [remanence, height, length, widthOD, widthID, blockParallelConstant].some(
      (v) => isNaN(v) || v <= 0
    )
  ) {
    return "Error: All values must be positive numbers.";
  }

  const averageWidth = (widthOD + widthID) / 2;
  if (averageWidth === 0 || length === 0) {
    return "Error: Length and average width must be greater than zero.";
  }

  const sqrtInnerTerm =
    Math.pow(length, 2) + Math.pow(averageWidth, 2) + 4 * Math.pow(height, 2);
  const numerator = 2 * height * Math.sqrt(sqrtInnerTerm);
  const denominator = length * averageWidth;

  if (denominator === 0) {
    return "Error: Division by zero in block magnet calculation.";
  }

  const arctanArgument = numerator / denominator;
  const magneticField =
    (remanence / Math.PI) * Math.atan(arctanArgument) * blockParallelConstant;

  return magneticField;
}

function calculateRingMagnet(inputs) {
  const { remanence, height, od, id } = inputs;

  // Validate inputs
  if ([remanence, height, od, id].some((v) => isNaN(v) || v <= 0)) {
    return "Error: All values must be positive numbers.";
  }

  if (od <= id) {
    return "Error: Outer diameter must be greater than inner diameter.";
  }

  const heightM = height / 1000;
  const ODM = od / 1000;
  const IDM = id / 1000;
  const rOuterM = ODM / 2;
  const rInnerM = IDM / 2;

  if (
    Math.pow(rOuterM, 2) + Math.pow(heightM, 2) === 0 ||
    Math.pow(rInnerM, 2) + Math.pow(heightM, 2) === 0
  ) {
    return "Error: Invalid geometry for ring magnet calculation.";
  }

  const outerTerm =
    heightM / Math.sqrt(Math.pow(rOuterM, 2) + Math.pow(heightM, 2));
  const innerTerm =
    heightM / Math.sqrt(Math.pow(rInnerM, 2) + Math.pow(heightM, 2));
  const magneticField = (remanence / 2) * (outerTerm - innerTerm);

  return magneticField;
}

function displayMagnetResult(result, activeTab, inputs) {
  const resultElement = document.getElementById("resultvalue");
  const errorElement = document.getElementById("error");
  const resultSection = document.querySelector("#magnet .result-category");

  if (!resultElement || !errorElement || !resultSection) return;

  if (typeof result === "string") {
    // Error case
    errorElement.textContent = result;
    errorElement.style.display = "block";
    resultSection.style.display = "none";
  } else {
    // Success case
    resultElement.textContent = isFinite(result) ? result.toFixed(6) : "NaN";
    errorElement.style.display = "none";
    resultSection.style.display = "block";

    // Add animation
    resultSection.classList.remove("pulse");
    void resultSection.offsetWidth; // Trigger reflow
    resultSection.classList.add("pulse");
  }
}

function displayMagnetError(message) {
  const errorElement = document.getElementById("error");
  const resultSection = document.querySelector("#magnet .result-category");

  if (errorElement && resultSection) {
    errorElement.textContent = message;
    errorElement.style.display = "block";
    resultSection.style.display = "none";
  }
}

function switchMagnetTab(tabName) {
  // Update tab buttons
  document.querySelectorAll("#magnet .magnet-tab-btn").forEach((btn) => {
    btn.classList.remove("active");
    btn.setAttribute("aria-pressed", "false");
    btn.setAttribute("aria-selected", "false");
    if (btn.getAttribute("data-tab") === tabName) {
      btn.classList.add("active");
      btn.setAttribute("aria-pressed", "true");
      btn.setAttribute("aria-selected", "true");
    }
  });

  // Update calculator sections
  document
    .querySelectorAll("#magnet .calculator-section")
    .forEach((section) => {
      section.classList.remove("active");
    });
  document.getElementById(tabName).classList.add("active");

  // Recalculate
  calculateMagneticField();
}

// Initialize magnet calculator
document.addEventListener("DOMContentLoaded", function () {
  // Tab switching for magnet calculator
  document
    .querySelector("#magnet .magnet-tabs")
    .addEventListener("click", function (e) {
      if (e.target.classList.contains("magnet-tab-btn")) {
        switchMagnetTab(e.target.getAttribute("data-tab"));
      }
    });

  // Input validation and listeners
  document.querySelectorAll("#magnet .input-field").forEach((input) => {
    input.addEventListener("input", function () {
      // Remove previous validation classes
      this.classList.remove("invalid", "valid");

      // Add validation classes
      if (this.value === "" || isNaN(this.value)) {
        // Do nothing for empty or invalid
      } else if (parseFloat(this.value) <= 0) {
        this.classList.add("invalid");
      } else {
        this.classList.add("valid");
      }

      // Recalculate
      calculateMagneticField();
    });
  });

  // Initial calculation
  setTimeout(calculateMagneticField, 100);
});
