// PCB Motor Calculator
function calculateMotorParameters() {
  try {
    // Get input values
    const inputs = getMotorInputs();

    // Validate inputs
    if (!validateMotorInputs(inputs)) return;

    // Perform calculations
    const results = performMotorCalculations(inputs);

    // Display results
    displayMotorResults(results);

    // Store results globally
    window.motorResults = results;

    // instant synchronization
    if (typeof perfectSync === "function") {
      perfectSync();
    }
  } catch (error) {
    console.error("Motor calculation error:", error);
    displayMotorError("Calculation error: " + error.message);
  }
}

function getMotorInputs() {
  return {
    pcbStatorOD: getSafeNumber("pcbStatorOD"),
    pcbStatorID: getSafeNumber("pcbStatorID"),
    pcbBoardThickness: getSafeNumber("pcbBoardThickness"),
    traceWidthID: getSafeNumber("traceWidthID"),
    traceGap: getSafeNumber("traceGap"),
    pcbLayerOz: getSafeNumber("pcbLayerOz"),
    numPCBLayers: getSafeNumber("numPCBLayers"),
    numPCBLayersseries: getSafeNumber("numPCBLayersseries"),
    numPCBLayersParallel: getSafeNumber("numPCBLayersParallel"),
    pmRotorHeight: getSafeNumber("pmRotorHeight"),
    airGap: getSafeNumber("airGap"),
    remanence: getSafeNumber("remanence"),
    current: getSafeNumber("current"),
    numCells: getSafeNumber("numCells"),
    cellChargeUnit: getSafeNumber("cellChargeUnit"),
    motorParallelConstant: getSafeNumber("motorParallelConstant"),
  };
}

function validateMotorInputs(inputs) {
  if (inputs.pcbStatorOD <= inputs.pcbStatorID) {
    displayMotorError("PCB Stator OD must be greater than ID");
    return false;
  }
  if (inputs.numPCBLayers <= 0 || inputs.numPCBLayersseries <= 0) {
    displayMotorError("PCB layers cannot be zero");
    return false;
  }
  return true;
}

function calculateWindingResistance(
  results,
  current,
  pcbLayerOz,
  numPCBLayersParallel
) {
  try {
    const copperResistivity = 1.68e-8;
    const thicknessPerOz = 3.48e-5;
    const copperThickness = pcbLayerOz * thicknessPerOz;
    if (!results.avgTraceWidth || !results.conductorLengthAll3Phase) return 0.1;
    const avgTraceWidthM = results.avgTraceWidth / 1000;
    const crossSectionArea =
      avgTraceWidthM * copperThickness * numPCBLayersParallel;
    const totalConductorLengthM = results.conductorLengthAll3Phase;
    if (crossSectionArea <= 0 || totalConductorLengthM <= 0) return 0.1;
    return (copperResistivity * totalConductorLengthM) / crossSectionArea;
  } catch (e) {
    return 0.1;
  }
}

function calculateActualEfficiency(motorData) {
  const { powerIn, powerOut, totalLoss } = motorData;
  if (powerIn > 0 && powerOut > 0) {
    const efficiency = (powerOut / powerIn) * 100;
    return { calculated: true, value: efficiency };
  }
  if (powerIn > 0 && totalLoss >= 0) {
    const powerIn_W = powerIn * 1000;
    if (powerIn_W > totalLoss) {
      const efficiency = ((powerIn_W - totalLoss) / powerIn_W) * 100;
      return { calculated: true, value: efficiency };
    }
  }
  return { calculated: false, value: null };
}

function performMotorCalculations(inputs) {
  const results = {};

  // Initialize all properties
  const properties = [
    "statorIDCircumference",
    "numLines",
    "traceCircumferenceID",
    "traceRadiusID",
    "radialGapID",
    "radialGapOD",
    "curvedLineWidth",
    "traceRadiusOD",
    "traceCircumferenceOD",
    "traceWidthOD",
    "traceLengthRadial",
    "currentConductingRadial",
    "numPCB",
    "stackupHeight",
    "numLinesPerPhase",
    "numLinesPerPhase180",
    "coilPerPhase180",
    "perPhaseCoil",
    "numStatorCoil",
    "magnetPoles",
    "totalConductorLength",
    "onConductorLength",
    "all3Phase",
    "twoPhase",
    "conductorLength2Phase",
    "conductorLengthAll3Phase",
    "reqCopperThickness",
    "nonMagnetArea",
    "radiusOD",
    "avgTorqueRadius",
    "height",
    "widthOD",
    "widthID",
    "lengthIDtoOD",
    "surfaceMagneticValue",
    "voltage",
    "powerIn",
    "force",
    "torque",
    "powerOut",
    "rpm",
    "kv",
    "avgTraceWidth",
    "copperLoss",
    "coreLoss",
    "mechanicalLoss",
    "strayLoss",
    "totalLoss",
    "actualEfficiency",
  ];

  properties.forEach((prop) => (results[prop] = null));

  results.numPhase = 3;
  results.motorParallelConstant = inputs.motorParallelConstant;

  const maxIterations = 7;
  for (let i = 0; i < maxIterations; i++) {
    let changed = false;

    // PCB Dimensions calculations
    if (results.statorIDCircumference === null) {
      results.statorIDCircumference = (inputs.pcbStatorID + inputs.traceGap) * Math.PI;
      changed = true;
    }

    if (results.numLines === null && results.statorIDCircumference !== null) {
      results.numLines = Math.ceil( results.statorIDCircumference / (inputs.traceWidthID + inputs.traceGap) );
      results.numLines = Math.ceil(results.numLines / 6) * 6;
      changed = true;
    }

    if (results.traceCircumferenceID === null && results.numLines !== null) {
      results.traceCircumferenceID = results.numLines * (inputs.traceWidthID + inputs.traceGap);
      changed = true;
    }

    if ( results.traceRadiusID === null && results.traceCircumferenceID !== null) {
      results.traceRadiusID = results.traceCircumferenceID / (2 * Math.PI);
      changed = true;
    }

    if (results.radialGapID === null && results.traceRadiusID !== null) {
      results.radialGapID = results.traceRadiusID - inputs.pcbStatorID / 2;
      changed = true;
    }

    if (results.radialGapOD === null) {
      results.radialGapOD = inputs.traceGap;
      changed = true;
    }

    if (results.curvedLineWidth === null) {
      results.curvedLineWidth = inputs.traceGap;
      changed = true;
    }

    if (results.traceRadiusOD === null) {
      results.traceRadiusOD = inputs.pcbStatorOD / 2 - results.radialGapOD;
      changed = true;
    }

    if ( results.traceCircumferenceOD === null && results.traceRadiusOD !== null ) {
      results.traceCircumferenceOD = 2 * Math.PI * results.traceRadiusOD;
      changed = true;
    }

    if ( results.traceWidthOD === null && results.traceCircumferenceOD !== null ) {
      results.traceWidthOD = results.traceCircumferenceOD / results.numLines - inputs.traceGap;
      changed = true;
    }

    if ( results.traceLengthRadial === null && results.traceRadiusOD !== null && results.traceRadiusID !== null ) {
      results.traceLengthRadial = results.traceRadiusOD - results.traceRadiusID;
      changed = true;
    }

    if (
      results.currentConductingRadial === null && results.traceLengthRadial !== null
    ) {
      results.currentConductingRadial = results.traceLengthRadial - inputs.traceGap / 2;
      changed = true;
    }

    if (results.numPCB === null) {
      results.numPCB = (inputs.numPCBLayersseries / inputs.numPCBLayers) * inputs.numPCBLayersParallel;
      changed = true;
    }

    if (results.stackupHeight === null && results.numPCB !== null) {
      results.stackupHeight = results.numPCB * inputs.pcbBoardThickness + (results.numPCB + 1) * inputs.pmRotorHeight + results.numPCB * inputs.airGap;
      changed = true;
    }

    if (results.numLinesPerPhase === null && results.numLines !== null) {
      results.numLinesPerPhase = results.numLines / 3;
      changed = true;
    }

    if (
      results.numLinesPerPhase180 === null && results.numLinesPerPhase !== null
    ) {
      results.numLinesPerPhase180 = results.numLinesPerPhase / 2;
      changed = true;
    }

    if (
      results.coilPerPhase180 === null && results.numLinesPerPhase180 !== null
    ) {
      results.coilPerPhase180 = Math.max(0, results.numLinesPerPhase180 - 1);
      changed = true;
    }

    if (results.perPhaseCoil === null && results.coilPerPhase180 !== null) {
      results.perPhaseCoil = results.coilPerPhase180 * 2;
      changed = true;
    }

    if (results.numStatorCoil === null && results.perPhaseCoil !== null) {
      results.numStatorCoil = 3 * results.perPhaseCoil;
      changed = true;
    }

    if (results.magnetPoles === null && results.numStatorCoil !== null) {
      results.magnetPoles = results.numStatorCoil + 2;
      changed = true;
    }

    if ( results.totalConductorLength === null && results.currentConductingRadial !== null) {
      results.totalConductorLength = (results.currentConductingRadial * results.numLines) / 1000;
      changed = true;
    }

    if (results.onConductorLength === null && results.totalConductorLength !== null ) {
      results.onConductorLength = (results.totalConductorLength / 3) * 2;
      changed = true;
    }

    if (results.all3Phase === null && results.totalConductorLength !== null) {
      results.all3Phase = results.totalConductorLength * inputs.numPCBLayersseries;
      changed = true;
    }

    if (results.twoPhase === null && results.onConductorLength !== null) {
      results.twoPhase = results.onConductorLength * inputs.numPCBLayersseries;
      changed = true;
    }

    if (results.conductorLength2Phase === null) {
      results.conductorLength2Phase = results.onConductorLength;
      changed = true;
    }

    if (results.conductorLengthAll3Phase === null) {
      results.conductorLengthAll3Phase = results.totalConductorLength;
      changed = true;
    }

    if (results.reqCopperThickness === null) {
      results.reqCopperThickness = inputs.pcbLayerOz * inputs.numPCBLayersParallel;
      changed = true;
    }

    if (results.nonMagnetArea === null && results.traceRadiusID !== null) {
      results.nonMagnetArea = results.traceRadiusID;
      changed = true;
    }

    if (results.radiusOD === null && results.nonMagnetArea !== null) {
      results.radiusOD = results.nonMagnetArea + results.currentConductingRadial;
      changed = true;
    }

    if (results.avgTorqueRadius === null && results.currentConductingRadial !== null && results.nonMagnetArea !== null) {
      results.avgTorqueRadius = (results.currentConductingRadial / 2) + results.nonMagnetArea;
      changed = true;
    }

    if (results.height === null) {
      results.height = inputs.pmRotorHeight;
      changed = true;
    }

    if (results.widthOD === null && results.traceCircumferenceOD !== null && results.magnetPoles > 0) {
      results.widthOD = results.traceCircumferenceOD / results.magnetPoles - inputs.traceGap;
      changed = true;
    }

    if ( results.widthID === null && results.traceCircumferenceID !== null && results.magnetPoles > 0) {
      results.widthID = results.traceCircumferenceID / results.magnetPoles - inputs.traceGap;
      changed = true;
    }

    if (results.lengthIDtoOD === null) {
      results.lengthIDtoOD = results.traceLengthRadial;
      changed = true;
    }

    // Surface Magnetic Value Calculation
    if (results.surfaceMagneticValue === null && results.remanence !== null && results.lengthIDtoOD !== null && results.widthOD > 0 && results.widthID > 0 && results.height > 0) {
      try {
        const avgW = (results.widthID + results.lengthIDtoOD) / 2;
        const H = results.height;
        const sqrtTerm = Math.sqrt(
          results.widthOD ** 2 + (avgW ** 2 + 4 * H ** 2)
        );
        const arctanArgument = (2 * H * sqrtTerm) / (results.widthOD * avgW);
        results.surfaceMagneticValue =
          (inputs.remanence / Math.PI) *
          Math.atan(arctanArgument) *
          results.motorParallelConstant;
      } catch (e) {
        results.surfaceMagneticValue = 0;
      }
      changed = true;
    }

    // Electrical Calculations
    if (results.voltage === null) {
      results.voltage = inputs.numCells * inputs.cellChargeUnit;
      changed = true;
    }

    if (results.powerIn === null && results.voltage !== null) {
      results.powerIn = (inputs.current * results.voltage) / 1000;
      changed = true;
    }

    if (results.force === null && results.surfaceMagneticValue !== null) {
      results.force = inputs.current * results.surfaceMagneticValue * results.twoPhase;
      changed = true;
    }

    if ( results.torque === null && results.avgTorqueRadius !== null && results.force !== null) {
      results.torque = (results.avgTorqueRadius / 1000) * results.force;
      changed = true;
    }

    if ( results.avgTraceWidth === null && inputs.traceWidthID !== null && results.traceWidthOD !== null) {

      results.avgTraceWidth =
        (((inputs.traceWidthID + results.traceWidthOD) / 2) *
          results.traceLengthRadial +
          inputs.traceGap * inputs.traceGap) /
        (results.traceLengthRadial + inputs.traceGap);
      changed = true;
    }

    // ⚠️ CRITICAL FIX: Copper Loss Calculation
    let copperLossW = 0;
    try {
      // ALWAYS USE TRACE POWER LOSS - THIS IS THE KEY FIX
      if (
        window.syncedCopperLossFromTrace !== undefined &&
        window.syncedCopperLossFromTrace !== null &&
        isFinite(window.syncedCopperLossFromTrace) &&
        window.syncedCopperLossFromTrace > 0
      ) {
        copperLossW = window.syncedCopperLossFromTrace;
      } else {
        throw new Error("Using fallback calculation");
      }
    } catch (error) {
      // Fallback calculation with validation
      const windingResistance = calculateWindingResistance(
        results,
        inputs.current,
        inputs.pcbLayerOz,
        inputs.numPCBLayersParallel
      );
      copperLossW = inputs.current * inputs.current * windingResistance;
      console.warn("Using motor calculated copper loss:", copperLossW);
    }

    results.copperLoss = copperLossW;
    results.coreLoss = copperLossW * 0.63;
    results.mechanicalLoss = copperLossW * 0.5;
    results.strayLoss = copperLossW * 0.25;
    results.totalLoss =
      results.copperLoss +
      results.coreLoss +
      results.mechanicalLoss +
      results.strayLoss;

    // Efficiency Calculation
    const effResult = calculateActualEfficiency({
      powerIn: results.powerIn,
      powerOut: results.powerOut,
      totalLoss: results.totalLoss,
    });

    if (effResult.calculated) {
      results.actualEfficiency = effResult.value;
      changed = true;
    }

    if (
      results.powerOut === null &&
      results.powerIn !== null &&
      results.actualEfficiency !== null
    ) {
      results.powerOut = results.powerIn * (results.actualEfficiency / 100);
      changed = true;
    }

    if (
      results.rpm === null &&
      results.powerOut !== null &&
      results.torque > 0
    ) {
      const powerOutWatts = results.powerOut * 1000;
      results.rpm = (powerOutWatts * 60) / (results.torque * 2 * Math.PI);
      changed = true;
    }

    if (results.kv === null && results.rpm !== null && results.voltage > 0) {
      results.kv = results.rpm / results.voltage;
      changed = true;
    }

    if (!changed) break;
  }

  return results;
}

function displayMotorResults(results) {
  const resultsContainer = document.getElementById("resultsContainer");
  if (!resultsContainer) return;

  resultsContainer.innerHTML = "";

  const resultGroups = [
    {
      title: "PCB Dimensions",
      items: [
        { name: "Number of PCB", value: results.numPCB, unit: "" },
        { name: "Stackup Height", value: results.stackupHeight, unit: "mm" },
        {
          name: "Stator ID Circumference",
          value: results.statorIDCircumference,
          unit: "mm",
        },
        // {
        //   name: "Trace Circumference at ID",
        //   value: results.traceCircumferenceID,
        //   unit: "mm",
        // },
        { name: "Trace Radius ID", value: results.traceRadiusID, unit: "mm" },
        { name: "Radial Gap ID", value: results.radialGapID, unit: "mm" },
        { name: "Radial Gap OD", value: results.radialGapOD, unit: "mm" },
        { name: "Trace Radius OD", value: results.traceRadiusOD, unit: "mm" },
        // {
        //   name: "Trace Circumference at OD",
        //   value: results.traceCircumferenceOD,
        //   unit: "mm",
        // },
        // { name: "Trace Width OD", value: results.traceWidthOD, unit: "mm" },
        {
          name: "Average Trace Width",
          value: results.avgTraceWidth,
          unit: "mm",
        },
      ],
    },
    {
      title: "Stator and Rotor Configuration",
      items: [
        {
          name: "Number of Stator Coil",
          value: results.numStatorCoil,
          unit: "",
        },
        // { name: "Magnet Poles", value: results.magnetPoles, unit: "" },
        // { name: "Number of Phase", value: results.numPhase, unit: "" },
        // { name: "Per Phase Coil", value: results.perPhaseCoil, unit: "" },
        // {
        //   name: "Coil per Phase 180 Apart",
        //   value: results.coilPerPhase180,
        //   unit: "",
        // },
        { name: "Number of Lines", value: results.numLines, unit: "" },
        {
          name: "Number of Lines per Phase", 
          value: results.numLinesPerPhase, 
          unit: "",
        },
        // {
        //   name: "Number of Lines per Phase 180 Apart",
        //   value: results.numLinesPerPhase180,
        //   unit: "",
        // },
        // {
        //   name: "Trace Length Radial Line",
        //   value: results.traceLengthRadial,
        //   unit: "mm",
        // },
        { name: "Curved Line Width", value: results.curvedLineWidth, unit: "mm", },
        {
          name: "Current Conducting Radial Length",
          value: results.currentConductingRadial,
          unit: "mm",
        },
      ],
    },
    {
      title: "Electrical Parameters",
      items: [
        // {
        //   name: "Total Conductor Length all 3 phases",
        //   value: results.conductorLengthAll3Phase,
        //   unit: "m",
        // },
        // {
        //   name: "On Conductor Length (2 phases)",
        //   value: results.conductorLength2Phase,
        //   unit: "m",
        // },
        // {
        //   name: "2 Phase Switch On with series layers",
        //   value: results.twoPhase,
        //   unit: "m",
        // },
        // {
        //   name: "All 3 Phase with series layers",
        //   value: results.all3Phase,
        //   unit: "m",
        // },
        // {
        //   name: "Required Copper Thickness",
        //   value: results.reqCopperThickness,
        //   unit: "oz/ft²",
        // },
        // { name: "Non Magnet Area", value: results.nonMagnetArea, unit: "mm" },
        // { name: "Radius OD", value: results.radiusOD, unit: "mm" },
        {
          name: "Average Torque Radius",
          value: results.avgTorqueRadius,
          unit: "mm",
        },
        {
          name: "Surface Magnetic Value",
          value: results.surfaceMagneticValue,
          unit: "T",
        },
        { name: "Height (H)", value: results.height, unit: "mm" },
        { name: "Width (W) OD", value: results.widthOD, unit: "mm" },
        { name: "Width (w) ID", value: results.widthID, unit: "mm" },
        // {
        //   name: "Length (L) from ID to OD",
        //   value: results.lengthIDtoOD,
        //   unit: "mm",
        // },
        {
          name: "Parallel Stacking Constant",
          value: results.motorParallelConstant,
          unit: "",
        },
        { name: "Force", value: results.force, unit: "N" },
        { name: "Voltage", value: results.voltage, unit: "V" },
        { name: "Power In", value: results.powerIn, unit: "kW" },
        { name: "Torque", value: results.torque, unit: "Nm" },
        { name: "RPM", value: results.rpm, unit: "" },
        { name: "Power Out", value: results.powerOut, unit: "kW" },
        { name: "kV", value: results.kv, unit: "RPM/V" },
        {
          name: "Actual Efficiency",
          value: results.actualEfficiency,
          unit: "%",
        },
      ],
    },
    {
      title: "Losses and Efficiency",
      items: [
        { name: "Copper Loss (P = I²R)", value: results.copperLoss, unit: "W" },
        // { name: "Core Loss", value: results.coreLoss, unit: "W" },
        // { name: "Mechanical Loss", value: results.mechanicalLoss, unit: "W" },
        // { name: "Stray Loss", value: results.strayLoss, unit: "W" },
        { name: "Total Loss", value: results.totalLoss, unit: "W" },
      ],
    },
  ];

  resultGroups.forEach((group) => {
    const groupDiv = document.createElement("div");
    groupDiv.className = "result-group";

    const title = document.createElement("div");
    title.className = "result-group-title";
    title.textContent = group.title;
    groupDiv.appendChild(title);

    group.items.forEach((item) => {
      const row = document.createElement("div");
      row.className = "result-row";

      const label = document.createElement("div");
      label.className = "result-label";
      label.textContent = item.name;

      const value = document.createElement("div");
      value.className = "result-value";

      if (item.value !== null && !isNaN(item.value) && isFinite(item.value)) {
        if (item.unit === "%" || item.unit === "kW") {
          value.textContent = `${item.value.toFixed(4)} ${item.unit}`;
        } else {
          value.textContent = `${item.value.toFixed(4)} ${item.unit}`;
        }
      } else {
        value.textContent = "N/A";
      }

      row.appendChild(label);
      row.appendChild(value);
      groupDiv.appendChild(row);
    });

    resultsContainer.appendChild(groupDiv);
  });
}

function displayMotorError(message) {
  const resultsContainer = document.getElementById("resultsContainer");
  if (resultsContainer) {
    resultsContainer.innerHTML = `<div class="error-message">${message}</div>`;
  }
}

// Initialize motor calculator when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  // Add event listeners to motor inputs
  const motorInputs = document.querySelectorAll("#motor input");
  motorInputs.forEach((input) => {
    input.addEventListener("input", calculateMotorParameters);
  });

  // Initial calculation
  setTimeout(calculateMotorParameters, 100);
});
