// PDF Generation System
function generateCombinedPDF() {
  if (!window.motorResults && !window.traceResults && !window.magnetResults) {
    showToast("No calculation results available.", true);
    return;
  }

  showLoading();

  setTimeout(() => {
    try {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      generatePDFContent(doc);

      doc.save("PCB_Full_Calculator_Report.pdf");
      showToast("Full PDF report generated successfully!");
    } catch (error) {
      console.error("PDF generation error:", error);
      showToast("Error generating PDF: " + error.message, true);
    } finally {
      hideLoading();
    }
  }, 100);
}

function generatePDFContent(doc) {
  // Title
  doc.setFontSize(20);
  doc.setTextColor(40, 40, 40);
  doc.text("PCB Calculator - Full Report", 105, 20, { align: "center" });

  doc.setFontSize(12);
  doc.setTextColor(100, 100, 100);
  doc.text(`Generated on: ${new Date().toLocaleString()}`, 105, 28, {
    align: "center",
  });

  let yPos = 40;

  // === MOTOR REPORT ===
  if (window.motorResults) {
    yPos = addMotorSection(doc, yPos);
    yPos += 10;
  }

  // === TRACE REPORT ===
  if (window.traceResults && window.traceInputs) {
    yPos = addTraceSection(doc, yPos);
    yPos += 10;
  }

  // === MAGNET REPORT ===
  if (window.magnetResults && typeof window.magnetResults.result === "number") {
    yPos = addMagnetSection(doc, yPos);
  }

  // Footer
  addFooter(doc);
}

function addMotorSection(doc, yPos) {
  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(40, 40, 40);
  doc.text("1. PCB Motor Calculator", 14, yPos);
  yPos += 10;

  const motorData = [
    ["Parameter", "Value"],
    ["Number of PCB", formatVal(window.motorResults.numPCB)],
    ["Stackup Height", formatVal(window.motorResults.stackupHeight, "mm")],
    ["Number of Stator Coil", formatVal(window.motorResults.numStatorCoil)],
    ["Magnet Poles", formatVal(window.motorResults.magnetPoles)],
    [
      "Surface Magnetic Value",
      formatVal(window.motorResults.surfaceMagneticValue, "T"),
    ],
    ["Voltage", formatVal(window.motorResults.voltage, "V")],
    ["Power In", formatVal(window.motorResults.powerIn, "kW")],
    ["Force", formatVal(window.motorResults.force, "N")],
    ["Torque", formatVal(window.motorResults.torque, "Nm")],
    ["RPM", formatVal(window.motorResults.rpm)],
    ["Power Out", formatVal(window.motorResults.powerOut, "kW")],
    ["kV", formatVal(window.motorResults.kv, "RPM/V")],
    ["Copper Loss", formatVal(window.motorResults.copperLoss, "W")],
    ["Core Loss", formatVal(window.motorResults.coreLoss, "W")],
    ["Mechanical Loss", formatVal(window.motorResults.mechanicalLoss, "W")],
    ["Stray Loss", formatVal(window.motorResults.strayLoss, "W")],
    ["Total Loss", formatVal(window.motorResults.totalLoss, "W")],
    ["Actual Efficiency", formatVal(window.motorResults.actualEfficiency, "%")],
  ];

  doc.autoTable({
    startY: yPos,
    head: [motorData[0]],
    body: motorData.slice(1),
    theme: "grid",
    styles: {
      fontSize: 9,
      cellPadding: 3,
      lineColor: [200, 200, 200],
      lineWidth: 0.1,
    },
    headStyles: {
      fillColor: [52, 152, 219],
      textColor: [255, 255, 255],
      fontStyle: "bold",
    },
    alternateRowStyles: {
      fillColor: [245, 245, 245],
    },
    margin: { left: 14, right: 14 },
  });

  return doc.lastAutoTable.finalY + 10;
}

function addTraceSection(doc, yPos) {
  const mode = window.traceInputs.isWidthMode
    ? "Width"
    : window.traceInputs.isRiseMode
    ? "Temp Rise"
    : "Parameters";

  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(40, 40, 40);
  doc.text(`2. Trace Width Calculator (${mode})`, 14, yPos);
  yPos += 10;

  let traceData = [["Layer", "Metric", "Value"]];
  const internal = window.traceResults.internal || {};
  const external = window.traceResults.external || {};

  const addTraceRow = (layer, metric, value) => {
    traceData.push([layer, metric, value]);
  };

  if (window.traceInputs.isWidthMode || window.traceInputs.isRiseMode) {
    if (window.traceInputs.isWidthMode) {
      addTraceRow("Internal", "Trace Width", formatTraceWidth(internal.width));
      addTraceRow("External", "Trace Width", formatTraceWidth(external.width));
    } else {
      addTraceRow("Internal", "Temp Rise", formatVal(internal.rise, "°C"));
      addTraceRow("External", "Temp Rise", formatVal(external.rise, "°C"));
    }
    addTraceRow("Internal", "Resistance", formatVal(internal.resistance, "Ω"));
    addTraceRow(
      "Internal",
      "Voltage Drop",
      formatVal(internal.voltageDrop, "V")
    );
    addTraceRow("Internal", "Power Loss", formatVal(internal.powerLoss, "W"));
    addTraceRow("External", "Resistance", formatVal(external.resistance, "Ω"));
    addTraceRow(
      "External",
      "Voltage Drop",
      formatVal(external.voltageDrop, "V")
    );
    addTraceRow("External", "Power Loss", formatVal(external.powerLoss, "W"));
  } else if (window.traceInputs.isParametersMode) {
    addTraceRow("Internal", "Area (mm²)", formatVal(internal.area?.mm2));
    addTraceRow("Internal", "Volume (mm³)", formatVal(internal.volume?.mm3));
    addTraceRow("Internal", "Resistance", formatVal(internal.resistance, "Ω"));
    addTraceRow("Internal", "Power Loss", formatVal(internal.powerLoss, "W"));
    addTraceRow("External", "Area (mm²)", formatVal(external.area?.mm2));
    addTraceRow("External", "Volume (mm³)", formatVal(external.volume?.mm3));
    addTraceRow("External", "Resistance", formatVal(external.resistance, "Ω"));
    addTraceRow("External", "Power Loss", formatVal(external.powerLoss, "W"));
  }

  doc.autoTable({
    startY: yPos,
    head: [traceData[0]],
    body: traceData.slice(1),
    theme: "grid",
    styles: {
      fontSize: 8,
      cellPadding: 2,
      lineColor: [200, 200, 200],
      lineWidth: 0.1,
    },
    headStyles: {
      fillColor: [52, 152, 219],
      textColor: [255, 255, 255],
      fontStyle: "bold",
    },
    alternateRowStyles: {
      fillColor: [245, 245, 245],
    },
    margin: { left: 14, right: 14 },
    columnStyles: {
      0: { cellWidth: 30 },
      1: { cellWidth: 60 },
      2: { cellWidth: 80 },
    },
  });

  return doc.lastAutoTable.finalY + 10;
}

function addMagnetSection(doc, yPos) {
  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(40, 40, 40);
  doc.text("3. Magnet Calculator", 14, yPos);
  yPos += 10;

  const type = window.magnetResults.activeTab === "block" ? "Block" : "Ring";

  // SAFE ACCESS: Check if inputs exist before accessing
  const inputs = window.magnetResults.inputs
    ? window.magnetResults.inputs[window.magnetResults.activeTab]
    : null;

  let magnetData = [["Parameter", "Value"]];

  if (inputs) {
    if (type === "Block") {
      magnetData.push(
        ["Type", "Block Magnet"],
        ["Remanence Br", formatVal(inputs.remanence, "T")],
        ["Height H", formatVal(inputs.height, "mm")],
        ["Length L", formatVal(inputs.length, "mm")],
        ["Width OD", formatVal(inputs.widthOD, "mm")],
        ["Width ID", formatVal(inputs.widthID, "mm")],
        ["Parallel Stacking Constant", formatVal(inputs.blockParallelConstant)]
      );
    } else {
      magnetData.push(
        ["Type", "Ring Magnet"],
        ["Remanence Br", formatVal(inputs.remanence, "T")],
        ["Height H", formatVal(inputs.height, "mm")],
        ["Outer Diameter", formatVal(inputs.od, "mm")],
        ["Inner Diameter", formatVal(inputs.id, "mm")]
      );
    }
  } else {
    // Fallback if inputs are not available
    magnetData.push(
      ["Type", `${type} Magnet`],
      ["Note", "Input parameters not available"]
    );
  }

  magnetData.push([
    "Surface Magnetic Value",
    formatVal(window.magnetResults.result, "T"),
  ]);

  doc.autoTable({
    startY: yPos,
    head: [magnetData[0]],
    body: magnetData.slice(1),
    theme: "grid",
    styles: {
      fontSize: 9,
      cellPadding: 3,
      lineColor: [200, 200, 200],
      lineWidth: 0.1,
    },
    headStyles: {
      fillColor: [52, 152, 219],
      textColor: [255, 255, 255],
      fontStyle: "bold",
    },
    alternateRowStyles: {
      fillColor: [245, 245, 245],
    },
    margin: { left: 14, right: 14 },
  });

  return doc.lastAutoTable.finalY + 10;
}

function addFooter(doc) {
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(9);
    doc.setTextColor(120);
    doc.text(`Page ${i} of ${pageCount}`, 105, 290, { align: "center" });
    doc.text("AirBuddy Aerospace - PCB Calculator", 105, 295, {
      align: "center",
    });
    doc.setTextColor(0);
  }
}

// Utility functions for PDF
function formatVal(val, unit = "") {
  if (val == null || !isFinite(val)) return "N/A";
  const num = parseFloat(val);
  if (unit === "%" || unit === "kW") {
    return `${num.toFixed(2)} ${unit}`;
  } else {
    return `${num.toFixed(4)} ${unit}`.trim();
  }
}

function formatTraceWidth(mil) {
  if (!isFinite(mil)) return "N/A";
  const mm = mil * 0.0254;
  return `${mil.toFixed(2)} mil / ${mm.toFixed(3)} mm`;
}
