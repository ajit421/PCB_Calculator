// Trace Width Calculator
(function () {
  let currentMode = "width";

  function initializeTraceCalculator() {
    setupModeToggle();
    setupInputListeners();
    updateTraceResults();
  }

  function setupModeToggle() {
    const modeButtons = document.querySelectorAll("#trace .mode-btn");
    modeButtons.forEach((btn) => {
      btn.addEventListener("click", function () {
        currentMode = this.getAttribute("data-mode");
        modeButtons.forEach((b) => b.classList.remove("active"));
        this.classList.add("active");
        updateUIForMode(currentMode);
        updateTraceResults();
      });
    });
  }

  function setupInputListeners() {
    const inputs = document.querySelectorAll("#trace input, #trace select");
    inputs.forEach((input) => {
      input.addEventListener("input", updateTraceResults);
    });
  }

  function updateUIForMode(mode) {
    const riseInput = document.querySelector("#trace .rise-input");
    const parametersRiseInput = document.querySelector(
      "#trace .parameters-rise-input"
    );
    const widthInput = document.querySelector("#trace .width-input");
    const widthResults = document.querySelector("#trace .width-results");
    const riseResults = document.querySelector("#trace .rise-results");
    const parametersResults = document.querySelector(
      "#trace .parameters-results"
    );

    // Reset all
    [riseInput, parametersRiseInput, widthInput].forEach((el) => {
      if (el) el.classList.add("hidden");
    });
    [widthResults, riseResults, parametersResults].forEach((el) => {
      if (el) el.classList.add("hidden");
    });

    switch (mode) {
      case "width":
        if (riseInput) riseInput.classList.remove("hidden");
        if (widthResults) widthResults.classList.remove("hidden");
        break;
      case "rise":
        if (widthInput) widthInput.classList.remove("hidden");
        if (riseResults) riseResults.classList.remove("hidden");
        break;
      case "parameters":
        if (parametersRiseInput) parametersRiseInput.classList.remove("hidden");
        if (widthInput) widthInput.classList.remove("hidden");
        if (parametersResults) parametersResults.classList.remove("hidden");
        break;
    }
  }

  function updateTraceResults() {
    const inputs = getTraceInputs();
    const convertedInputs = convertTraceUnits(inputs);
    const results = calculateTraceResults(convertedInputs);

    displayTraceResults(results, inputs);

    // Store results globally
    window.traceResults = results;
    window.traceInputs = inputs;

    // instant synchronization
    if (typeof perfectSync === "function") {
      perfectSync();
    }
  }

  function getTraceInputs() {
    const getValue = (id) => {
      const element = document.querySelector(`#trace #${id}`);
      return element ? parseFloat(element.value) || 0 : 0;
    };

    const getUnit = (id) => {
      const element = document.querySelector(`#trace #${id}`);
      return element ? element.value : "";
    };

    return {
      current: getValue("tracecurrent"),
      ambient: getValue("traceambient"),
      ambientUnit: getUnit("traceambientUnit"),
      rise: getValue("tracerise"),
      riseUnit: getUnit("traceriseUnit"),
      parametersRise: getValue("traceparametersrise"),
      parametersRiseUnit: getUnit("traceparametersriseUnit"),
      length: getValue("tracelengthinput"),
      lengthUnit: getUnit("tracetraceUnit"),
      thickness: getValue("tracethickness"),
      thicknessUnit: getUnit("tracethicknessUnit"),
      widthInternal: getValue("tracewidthinternal"),
      widthUnitInternal: getUnit("tracewidthUnitinternal"),
      widthExternal: getValue("tracewidthexternal"),
      widthUnitExternal: getUnit("tracewidthUnitexternal"),
      isWidthMode: currentMode === "width",
      isRiseMode: currentMode === "rise",
      isParametersMode: currentMode === "parameters",
    };
  }

  function convertTraceUnits(inputs) {
    let {
      thickness,
      length,
      rise,
      parametersRise,
      ambient,
      widthInternal,
      widthExternal,
    } = inputs;

    // Convert thickness to mil
    if (inputs.thicknessUnit === "ozft") thickness = ozToMil(thickness);

    // Convert length to cm
    const CM_PER_IN = 2.54;
    const CM_PER_FT = 30.48;
    const CM_PER_MIL = 0.00254;

    switch (inputs.lengthUnit) {
      case "in":
        length *= CM_PER_IN;
        break;
      case "ft":
        length *= CM_PER_FT;
        break;
      case "mil":
        length *= CM_PER_MIL;
        break;
      case "mm":
        length *= 0.1;
        break;
      case "m":
        length *= 100;
        break;
    }

    // Convert temperatures to Celsius
    if (inputs.riseUnit === "F") rise = fToC(rise);
    if (inputs.ambientUnit === "F") ambient = fToC(ambient);
    if (inputs.parametersRiseUnit === "F")
      parametersRise = fToC(parametersRise);

    // Convert widths to mil
    if (inputs.widthUnitInternal === "mm")
      widthInternal = mmToMil(widthInternal);
    if (inputs.widthUnitExternal === "mm")
      widthExternal = mmToMil(widthExternal);

    return {
      ...inputs,
      thickness,
      length,
      rise,
      parametersRise,
      ambient,
      widthInternal,
      widthExternal,
    };
  }

  // Calculation functions
  const externalArea = (current, riseC) =>
    Math.pow(current / (0.048 * Math.pow(riseC, 0.44)), 1 / 0.725);

  const internalArea = (current, riseC) =>
    Math.pow(current / (0.024 * Math.pow(riseC, 0.44)), 1 / 0.725);

  const externalRise = (current, areaMil2) =>
    Math.pow(current / (0.048 * Math.pow(areaMil2, 0.725)), 1 / 0.44);

  const internalRise = (current, areaMil2) =>
    Math.pow(current / (0.024 * Math.pow(areaMil2, 0.725)), 1 / 0.44);

  function calculateResistance(
    current,
    areaMil2,
    lengthCm,
    ambientTempC,
    tempRiseC = 0
  ) {
    const RHO = 1.7e-6;
    const ALPHA = 0.0039;
    const AREAMIL2TOCM2 = 6.4516e-6;
    const areaCm2 = areaMil2 * AREAMIL2TOCM2;

    if (!isFinite(areaCm2) || areaCm2 <= 0) {
      return {
        resistance: Infinity,
        voltageDrop: Infinity,
        powerLoss: Infinity,
      };
    }

    const operatingTempC = ambientTempC + tempRiseC;
    const resistance =
      (RHO * lengthCm * (1 + ALPHA * (operatingTempC - 25))) / areaCm2;
    const voltageDrop = current * resistance;
    const powerLoss = current * voltageDrop;

    return { resistance, voltageDrop, powerLoss };
  }

  function calculateTraceResults(data) {
    if (data.isWidthMode) {
      return calculateWidth(data);
    } else if (data.isRiseMode) {
      return calculateRise(data);
    } else if (data.isParametersMode) {
      return calculateParameters(data);
    }
    return null;
  }

  function calculateWidth(data) {
    const { current, rise, thickness, length, ambient } = data;
    if (current <= 0 || rise <= 0 || thickness <= 0) return null;

    const areaI = internalArea(current, rise);
    const widthI = areaI / thickness;
    const resI = calculateResistance(current, areaI, length, ambient, rise);

    const areaE = externalArea(current, rise);
    const widthE = areaE / thickness;
    const resE = calculateResistance(current, areaE, length, ambient, rise);

    return {
      internal: { width: widthI, ...resI },
      external: { width: widthE, ...resE },
    };
  }

  function calculateRise(data) {
    const {
      current,
      thickness,
      widthInternal,
      widthExternal,
      length,
      ambient,
    } = data;
    if (
      current <= 0 ||
      thickness <= 0 ||
      widthInternal <= 0 ||
      widthExternal <= 0
    )
      return null;

    const areaI = widthInternal * thickness;
    const riseI = internalRise(current, areaI);
    const resI = calculateResistance(current, areaI, length, ambient, riseI);

    const areaE = widthExternal * thickness;
    const riseE = externalRise(current, areaE);
    const resE = calculateResistance(current, areaE, length, ambient, riseE);

    return {
      internal: { rise: riseI, ...resI },
      external: { rise: riseE, ...resE },
    };
  }

  function calculateParameters(data) {
    const {
      current,
      thickness,
      widthInternal,
      widthExternal,
      length,
      ambient,
      parametersRise,
    } = data;
    if (thickness <= 0 || widthInternal <= 0 || widthExternal <= 0) return null;

    const areaInternalMil2 = widthInternal * thickness;
    const areaExternalMil2 = widthExternal * thickness;

    const MIL2TOMM2 = 0.00064516;
    const areaInternalMm2 = areaInternalMil2 * MIL2TOMM2;
    const areaExternalMm2 = areaExternalMil2 * MIL2TOMM2;

    const areaInternalCm2 = areaInternalMm2 / 100;
    const areaExternalCm2 = areaExternalMm2 / 100;
    const areaInternalM2 = areaInternalMm2 / 1e6;
    const areaExternalM2 = areaExternalMm2 / 1e6;

    const lengthM = length / 100;
    const volumeInternalM3 = areaInternalM2 * lengthM;
    const volumeExternalM3 = areaExternalM2 * lengthM;

    const resI = calculateResistance(
      current,
      areaInternalMil2,
      length,
      ambient,
      parametersRise
    );
    const resE = calculateResistance(
      current,
      areaExternalMil2,
      length,
      ambient,
      parametersRise
    );

    return {
      internal: {
        area: {
          mm2: areaInternalMm2,
          cm2: areaInternalCm2,
          m2: areaInternalM2,
        },
        volume: {
          mm3: volumeInternalM3 * 1e9,
          cm3: volumeInternalM3 * 1e6,
          m3: volumeInternalM3,
        },
        ...resI,
      },
      external: {
        area: {
          mm2: areaExternalMm2,
          cm2: areaExternalCm2,
          m2: areaExternalM2,
        },
        volume: {
          mm3: volumeExternalM3 * 1e9,
          cm3: volumeExternalM3 * 1e6,
          m3: volumeExternalM3,
        },
        ...resE,
      },
    };
  }

  function displayTraceResults(result, data) {
    const format = (val, prec = 11) =>
      val !== null && isFinite(val) ? Number(val).toFixed(prec) : "Error";

    // Helper to safely update input field without triggering infinite loop
    const updateInputValue = (id, value) => {
      const input = document.querySelector(`#trace #${id}`);
      if (input && parseFloat(input.value) !== parseFloat(value)) {
        input.value = value;
      }
    };

    if (data.isWidthMode && result) {
      updateElement(
        "#internalWidth",
        `Width: ${format(result.internal.width)} mil<br>${format(
          milToMm(result.internal.width)
        )} mm`
      );
      updateElement(
        "#externalWidth",
        `Width: ${format(result.external.width)} mil<br>${format(
          milToMm(result.external.width)
        )} mm`
      );
      updateElement(
        "#internalResistance",
        format(result.internal.resistance) + " Ω"
      );
      updateElement(
        "#internalVoltage",
        format(result.internal.voltageDrop) + " V"
      );
      updateElement("#internalPower", format(result.internal.powerLoss) + " W");
      updateElement(
        "#externalResistance",
        format(result.external.resistance) + " Ω"
      );
      updateElement(
        "#externalVoltage",
        format(result.external.voltageDrop) + " V"
      );
      updateElement("#externalPower", format(result.external.powerLoss) + " W");
      updateInputValue("tracewidthinternal", milToMm(result.internal.width).toFixed(8));
      updateInputValue("tracewidthexternal", milToMm(result.external.width).toFixed(8));

    } else if (data.isRiseMode && result) {
      updateElement(
        "#internalRise",
        `Rise: ${format(result.internal.rise)} °C<br>${format(
          cToF(result.internal.rise)
        )} °F`
      );
      updateElement(
        "#externalRise",
        `Rise: ${format(result.external.rise)} °C<br>${format(
          cToF(result.external.rise)
        )} °F`
      );
      updateElement(
        "#internalRiseResistance",
        format(result.internal.resistance) + " Ω"
      );
      updateElement(
        "#internalRiseVoltage",
        format(result.internal.voltageDrop) + " V"
      );
      updateElement(
        "#internalRisePower",
        format(result.internal.powerLoss) + " W"
      );
      updateElement(
        "#externalRiseResistance",
        format(result.external.resistance) + " Ω"
      );
      updateElement(
        "#externalRiseVoltage",
        format(result.external.voltageDrop) + " V"
      );
      updateElement(
        "#externalRisePower",
        format(result.external.powerLoss) + " W"
      );
    } else if (data.isParametersMode && result) {
      displayParametersResults(result);
    }

    // Add animation
    document.querySelectorAll("#trace .result-category").forEach((card) => {
      card.classList.add("pulse");
      setTimeout(() => card.classList.remove("pulse"), 1000);
    });
  }

  function displayParametersResults(result) {
    const formatSci = (val, prec = 11) =>
      val !== null && isFinite(val) ? Number(val).toExponential(prec) : "Error";
    const formatFixed = (val, prec = 11) =>
      val !== null && isFinite(val) ? Number(val).toFixed(prec) : "Error";

    // Internal
    updateElement(
      "#internalAreamm2",
      formatFixed(result.internal.area.mm2) + " mm²"
    );
    updateElement(
      "#internalAreacm2",
      formatSci(result.internal.area.cm2) + " cm²"
    );
    updateElement(
      "#internalAream2",
      formatSci(result.internal.area.m2) + " m²"
    );
    updateElement(
      "#internalVolumemm3",
      formatFixed(result.internal.volume.mm3) + " mm³"
    );
    updateElement(
      "#internalVolumecm3",
      formatSci(result.internal.volume.cm3) + " cm³"
    );
    updateElement(
      "#internalVolumem3",
      formatSci(result.internal.volume.m3) + " m³"
    );
    updateElement(
      "#internalParamResistance",
      formatFixed(result.internal.resistance) + " Ω"
    );
    updateElement(
      "#internalParamVoltage",
      formatFixed(result.internal.voltageDrop) + " V"
    );
    updateElement(
      "#internalParamPower",
      formatFixed(result.internal.powerLoss) + " W"
    );

    // External
    updateElement(
      "#externalAreamm2",
      formatFixed(result.external.area.mm2) + " mm²"
    );
    updateElement(
      "#externalAreacm2",
      formatSci(result.external.area.cm2) + " cm²"
    );
    updateElement(
      "#externalAream2",
      formatSci(result.external.area.m2) + " m²"
    );
    updateElement(
      "#externalVolumemm3",
      formatFixed(result.external.volume.mm3) + " mm³"
    );
    updateElement(
      "#externalVolumecm3",
      formatSci(result.external.volume.cm3) + " cm³"
    );
    updateElement(
      "#externalVolumem3",
      formatSci(result.external.volume.m3) + " m³"
    );
    updateElement(
      "#externalParamResistance",
      formatFixed(result.external.resistance) + " Ω"
    );
    updateElement(
      "#externalParamVoltage",
      formatFixed(result.external.voltageDrop) + " V"
    );
    updateElement(
      "#externalParamPower",
      formatFixed(result.external.powerLoss) + " W"
    );
  }

  function updateElement(selector, content) {
    const element = document.querySelector(`#trace ${selector}`);
    if (element) element.innerHTML = content;
  }

  // Expose update function globally
  window.updateTraceResults = updateTraceResults;

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", initializeTraceCalculator);
})();
