const readline = require("readline");
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Helper function for asynchronous question
function questionAsync(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

// Magnet calculation functions
function blockMagnet(remanenceTesla, heightMm, lengthMm, widthODMm, widthIDMm) {
  const averageWidth = (widthODMm + widthIDMm) / 2;

  if (averageWidth === 0 || lengthMm === 0) {
    return "Error: Division by zero in block_magnet calculation.";
  }

  const sqrtInnerTerm = lengthMm ** 2 + averageWidth ** 2 + 4 * heightMm ** 2;
  const numerator = 2 * heightMm * Math.sqrt(sqrtInnerTerm);
  const denominator = lengthMm * averageWidth;

  if (denominator === 0) {
    return "Error: Division by zero in block_magnet calculation.";
  }

  const arctanArgument = numerator / denominator;
  const magneticField = (remanenceTesla / Math.PI) * Math.atan(arctanArgument);
  return magneticField;
}

function ringMagnet(remanenceTesla, heightMm, ODmm, IDmm) {
  const heightM = heightMm / 1000;
  const ODM = ODmm / 1000;
  const IDM = IDmm / 1000;

  const rOuterM = ODM / 2;
  const rInnerM = IDM / 2;

  if (rOuterM ** 2 + heightM ** 2 === 0 || rInnerM ** 2 + heightM ** 2 === 0) {
    return "Error: Division by zero in ring_magnet calculation.";
  }

  const outerTerm = heightM / Math.sqrt(rOuterM ** 2 + heightM ** 2);
  const innerTerm = heightM / Math.sqrt(rInnerM ** 2 + heightM ** 2);
  const magneticField = (remanenceTesla / 2) * (outerTerm - innerTerm);
  return magneticField;
}

// User interface functions
async function getFloatInput(promptText) {
  while (true) {
    try {
      const input = await questionAsync(promptText);
      return parseFloat(input);
    } catch (error) {
      console.log("Invalid input. Please enter a numeric value.");
    }
  }
}

async function runBlockCalculator() {
  console.log("\n--- Block Magnet Calculator ---");
  const remanenceTesla = await getFloatInput("Enter Remanence (Br) in Tesla: ");
  const heightMm = await getFloatInput("Enter Height (H) in mm: ");
  const lengthMm = await getFloatInput("Enter Length (L) in mm: ");
  const widthODMm = await getFloatInput("Enter First Width (W1_OD) in mm: ");
  const widthIDMm = await getFloatInput("Enter Second Width (W2_ID) in mm: ");

  const result = blockMagnet(
    remanenceTesla,
    heightMm,
    lengthMm,
    widthODMm,
    widthIDMm
  );
  printResult(result);
}

async function runRingCalculator() {
  console.log("\n--- Ring Magnet Calculator ---");
  const remanenceTesla = await getFloatInput("Enter Remanence (Br) in Tesla: ");
  const heightMm = await getFloatInput("Enter Height (H) in mm: ");
  const ODmm = await getFloatInput("Enter Outer Diameter (OD) in mm: ");
  const IDmm = await getFloatInput("Enter Inner Diameter (ID) in mm: ");

  const result = ringMagnet(remanenceTesla, heightMm, ODmm, IDmm);
  printResult(result);
}

function printResult(result) {
  console.log("-".repeat(25));
  if (typeof result === "string") {
    console.log(`Error: ${result}`);
  } else {
    console.log(`Calculated Magnetic Field: ${result.toFixed(6)} T`);
  }
  console.log("-".repeat(25));
}

// Main function
async function main() {
  while (true) {
    console.log("\n===== Magnet Calculator Menu =====");
    console.log("1. Calculate for Block Magnet");
    console.log("2. Calculate for Ring Magnet");

    const choice = await questionAsync("Enter your choice (1-2): ");

    switch (choice) {
      case "1":
        await runBlockCalculator();
        break;
      case "2":
        await runRingCalculator();
        break;

      default:
        console.log("Invalid choice. Please enter a number between 1 and 2");
    }
  }
}

// Start the program
if (require.main === module) {
  main().catch((err) => {
    console.error("An error occurred:", err);
    rl.close();
  });
}
