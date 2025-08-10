// Live calculation functionality
document.addEventListener('DOMContentLoaded', function () {
    // Get all input elements
    const inputs = document.querySelectorAll('input, select');

    // Add event listeners to all inputs
    inputs.forEach(input => {
        input.addEventListener('input', updateCalculations);
    });

    // Initial calculation
    updateCalculations();
});

// Constants and Configuration Data
const DEFAULT_AIR_GAP_MM = 0.1;
const DEFAULT_NUM_PHASE = 3;
const DEFAULT_PCB_THICKNESS_MM = 1.6;
const DEFAULT_PM_ROTOR_THICKNESS_MM = 3.0;
const DEFAULT_ONE_PCB_OZ_FT2 = 40; // Copper weight per layer
const DEFAULT_MAGNET_STRENGTH_T = 0.5;
const DEFAULT_CELL_UNIT_CHARGE_V = 4.2;
const DEFAULT_TRACE_GAP_MM = 0.225;
const DEFAULT_TRACE_WIDTH_CURVED_LINE = 0.225;

const PCB_OD_PARAMETERS = {
    50: {
        pcb_stator_id_mm: 8,
        trace_width_id_mm: 3,
        num_pcb_in_series: 15,
        layer_parallel: 2,
        cost_factor_pcb: 80,
        cost_factor_magnets: 80,
        miscellaneous_cost: 500,
        pcb_stator_od_mm: 50,
        weight_factor: 5 + 7,
    },
    100: {
        pcb_stator_id_mm: 49,
        trace_width_id_mm: 4.9,
        num_pcb_in_series: 5,
        layer_parallel: 6,
        cost_factor_pcb: 130,
        cost_factor_magnets: 130,
        miscellaneous_cost: 1000,
        pcb_stator_od_mm: 100,
        weight_factor: 8 + 10,
    },
    150: {
        pcb_stator_id_mm: 100,
        trace_width_id_mm: 5.3,
        num_pcb_in_series: 7,
        layer_parallel: 10,
        cost_factor_pcb: 200,
        cost_factor_magnets: 200,
        miscellaneous_cost: 1500,
        pcb_stator_od_mm: 150,
        weight_factor: 11 + 12,
    },
};

// Helper function to format numbers for display
function fmt(value, unit = '', decimals = 5) {
    if (value === null || value === undefined || isNaN(value)) {
        return "N/A";
    }
    
    // Check if the number is an integer or very close to an integer
    if (Math.abs(value - Math.round(value)) < 1e-9) { // Use a small epsilon for floating point comparison
        return `${Math.round(value)}${unit}`;
    }
    return `${value.toFixed(decimals)}${unit}`;
}

// Function to calculate winding resistance (adapted from original script)
function calculate_winding_resistance(results) {
    const requiredKeys = [
        "conductor_length_2phase_m",
        "trace_width_id_mm",
        "layer_parallel",
    ];

    if (!requiredKeys.every((key) => results[key] !== null && !isNaN(results[key]))) {
        return 0.2; // Default estimate if dependencies are missing
    }

    try {
        const resistivity = 1.68e-8; // Ω·m (copper)
        const copperThickness = DEFAULT_ONE_PCB_OZ_FT2 * 34.8e-6; // Convert oz/ft² to meters

        const traceWidthM = results.trace_width_id_mm * 1e-3;
        const crossSection = traceWidthM * copperThickness;

        if (crossSection === 0) return 0.2; // Avoid division by zero

        const totalResistance = (resistivity * results.conductor_length_2phase_m) / crossSection;
        const parallelResistance = totalResistance / results.layer_parallel;

        return Math.max(parallelResistance, 0.001); // Ensure non-zero value
    } catch (e) {
        console.error("Error in winding resistance calculation:", e);
        return 0.2; // Fallback on error
    }
}

// Update calculations when any input changes
function updateCalculations() {
    // Initialize results object with current input values (or null if empty/invalid)
    const results = {
        power_out_kw: parseFloat(document.getElementById('powerOut').value) || null,
        torque_nm: parseFloat(document.getElementById('torque').value) || null,
        rpm: parseFloat(document.getElementById('rpm').value) || null,
        current_a: parseFloat(document.getElementById('current').value) || null,
        voltage_v: parseFloat(document.getElementById('voltage').value) || null,
        num_cell_series: parseFloat(document.getElementById('numCellSeries').value) || null,
        efficiency_percent: parseFloat(document.getElementById('efficiency').value) || null,
        pcb_stator_od_mm: parseFloat(document.getElementById('customPcbOD').value) || parseFloat(document.getElementById('pcbOD').value) || null,

        // Initialize all calculated outputs to null
        power_in_kw: null,
        force_n: null,
        weight_g: null,
        power_density_kw_kg: null,
        kv_rating: null,
        cost_inr: null,
        conductor_length_2phase_m: null,
        total_pcb: null,
        num_coils_per_phase: null,
        pcb_stator_id_mm: null,
        trace_width_id_mm: null,
        number_of_lines: null,
        num_lines_per_phase: null,
        num_lines_180: null,
        coil_per_phase_180: null,
        trace_length_radial_mm: null,
        trace_radius_id_mm: null,
        trace_radius_od_mm: null,
        trace_od_circumference_mm: null,
        current_conducting_radial_mm: null,
        trace_id_circumference_mm: null,
        trace_thickness_od_mm: null,
        id_circumference_mm: null,
        non_magnet_area_mm: null,
        num_stator_coils: null,
        magnet_poles: null,
        average_trace_width_mm: null,
        total_conductor_length_m: null,
        on_conductor_length_m: null,
        required_copper_thickness_mm: null,
        radius_od_mm: null,
        stack_up_height_mm: null,
        pcb_diameter_mm: null,
        pcb_height_mm: null,
        radial_gap_id_mm: null,
        radial_gap_od_mm: null,
        avg_torque_radius_mm: null,
    };

    // Determine PCB parameters based on OD
    let pcb_params = null;
    if (results.pcb_stator_od_mm !== null) {
        if (PCB_OD_PARAMETERS.hasOwnProperty(results.pcb_stator_od_mm)) {
            pcb_params = PCB_OD_PARAMETERS[results.pcb_stator_od_mm];
        } else {
            // If custom OD, scale from 100mm parameters
            const base_params = PCB_OD_PARAMETERS[100]; // Use 100mm as the base for scaling
            if (base_params) {
                const factor = results.pcb_stator_od_mm / 100;
                pcb_params = {
                    pcb_stator_id_mm: base_params.pcb_stator_id_mm * factor,
                    trace_width_id_mm: base_params.trace_width_id_mm * factor,
                    num_pcb_in_series: Math.round(base_params.num_pcb_in_series * factor),
                    layer_parallel: Math.round(base_params.layer_parallel * factor),
                    cost_factor_pcb: base_params.cost_factor_pcb * factor,
                    cost_factor_magnets: base_params.cost_factor_magnets * factor,
                    miscellaneous_cost: base_params.miscellaneous_cost * factor,
                    pcb_stator_od_mm: results.pcb_stator_od_mm,
                    weight_factor: base_params.weight_factor * factor,
                };
            }
        }
    }

    // Merge PCB parameters into results if available
    if (pcb_params) {
        Object.assign(results, pcb_params);
    }

    // Iterative calculation loop to derive values
    const max_iterations = 10; // Increased iterations for more complex interdependencies
    for (let i = 0; i < max_iterations; i++) {
        let something_calculated_in_this_pass = false;

        // 1. Electrical Calculations
        if (results.voltage_v === null && results.num_cell_series !== null) {
            results.voltage_v = results.num_cell_series * DEFAULT_CELL_UNIT_CHARGE_V;
            something_calculated_in_this_pass = true;
        }

        if (results.power_in_kw === null && results.current_a !== null && results.voltage_v !== null) {
            results.power_in_kw = (results.current_a * results.voltage_v) / 1000;
            something_calculated_in_this_pass = true;
        }

        if (results.power_out_kw === null && results.efficiency_percent !== null && results.power_in_kw !== null && results.efficiency_percent > 0) {
            results.power_out_kw = (results.efficiency_percent / 100) * results.power_in_kw;
            something_calculated_in_this_pass = true;
        }

        if (results.power_in_kw === null && results.power_out_kw !== null && results.efficiency_percent !== null && results.efficiency_percent > 0) {
            results.power_in_kw = (results.power_out_kw / (results.efficiency_percent / 100));
            something_calculated_in_this_pass = true;
        }

        if (results.current_a === null && results.power_in_kw !== null && results.voltage_v !== null && results.voltage_v > 0) {
            results.current_a = (results.power_in_kw * 1000) / results.voltage_v;
            something_calculated_in_this_pass = true;
        }

        // 2. Mechanical Calculations
        if (results.power_out_kw === null && results.torque_nm !== null && results.rpm !== null) {
            const omega = (2 * Math.PI * results.rpm) / 60;
            results.power_out_kw = (results.torque_nm * omega) / 1000;
            something_calculated_in_this_pass = true;
        }

        if (results.rpm === null && results.power_out_kw !== null && results.torque_nm !== null && results.torque_nm !== 0) {
            results.rpm = (results.power_out_kw * 1000 * 60) / (results.torque_nm * (2 * Math.PI));
            something_calculated_in_this_pass = true;
        }

        if (results.torque_nm === null && results.power_out_kw !== null && results.rpm !== null && results.rpm > 0) {
            results.torque_nm = (results.power_out_kw * 1000 * 60) / (results.rpm * 2 * Math.PI);
            something_calculated_in_this_pass = true;
        }

        // Derived PCB Dimensions (dependent on pcb_params being set)
        if (pcb_params) {
            if (results.pcb_stator_id_mm !== null && results.id_circumference_mm === null) {
                results.id_circumference_mm = results.pcb_stator_id_mm * Math.PI;
                something_calculated_in_this_pass = true;
            }

            if (results.id_circumference_mm !== null && results.trace_width_id_mm !== null && results.number_of_lines === null) {
                const temp = results.id_circumference_mm / (results.trace_width_id_mm + DEFAULT_AIR_GAP_MM);
                const significance = 6;
                results.number_of_lines = parseInt(significance * Math.ceil(temp / significance));
                something_calculated_in_this_pass = true;
            }

            if (results.number_of_lines !== null && results.trace_width_id_mm !== null && results.trace_id_circumference_mm === null) {
                results.trace_id_circumference_mm = results.number_of_lines * (DEFAULT_TRACE_GAP_MM + results.trace_width_id_mm);
                something_calculated_in_this_pass = true;
            }

            if (results.trace_id_circumference_mm !== null && results.trace_radius_id_mm === null) {
                results.trace_radius_id_mm = results.trace_id_circumference_mm / (2 * Math.PI);
                something_calculated_in_this_pass = true;
            }

            if (results.trace_radius_id_mm !== null && results.pcb_stator_id_mm !== null && results.radial_gap_id_mm === null) {
                results.radial_gap_id_mm = results.trace_radius_id_mm - results.pcb_stator_id_mm / 2;
                something_calculated_in_this_pass = true;
            }

            if (results.radial_gap_od_mm === null) {
                results.radial_gap_od_mm = DEFAULT_TRACE_GAP_MM;
                something_calculated_in_this_pass = true;
            }

            if (results.trace_radius_id_mm !== null && results.non_magnet_area_mm === null) {
                results.non_magnet_area_mm = results.trace_radius_id_mm;
                something_calculated_in_this_pass = true;
            }

            if (results.pcb_stator_od_mm !== null && results.trace_radius_od_mm === null) {
                results.trace_radius_od_mm = results.pcb_stator_od_mm / 2 - DEFAULT_TRACE_GAP_MM;
                something_calculated_in_this_pass = true;
            }

            if (results.trace_radius_od_mm !== null && results.trace_od_circumference_mm === null) {
                results.trace_od_circumference_mm = results.trace_radius_od_mm * 2 * Math.PI;
                something_calculated_in_this_pass = true;
            }

            if (results.trace_od_circumference_mm !== null && results.number_of_lines !== null && results.number_of_lines > 0 && results.trace_thickness_od_mm === null) {
                results.trace_thickness_od_mm = results.trace_od_circumference_mm / results.number_of_lines - DEFAULT_TRACE_GAP_MM;
                something_calculated_in_this_pass = true;
            }

            if (results.trace_radius_od_mm !== null && results.trace_radius_id_mm !== null && results.trace_length_radial_mm === null) {
                results.trace_length_radial_mm = results.trace_radius_od_mm - results.trace_radius_id_mm;
                something_calculated_in_this_pass = true;
            }

            if (results.number_of_lines !== null && results.num_lines_per_phase === null) {
                results.num_lines_per_phase = results.number_of_lines / DEFAULT_NUM_PHASE;
                something_calculated_in_this_pass = true;
            }

            if (results.num_lines_per_phase !== null && results.num_lines_180 === null) {
                results.num_lines_180 = results.num_lines_per_phase / 2;
                something_calculated_in_this_pass = true;
            }

            if (results.num_lines_180 !== null && results.coil_per_phase_180 === null) {
                results.coil_per_phase_180 = results.num_lines_180 - 1;
                something_calculated_in_this_pass = true;
            }

            if (results.coil_per_phase_180 !== null && results.num_coils_per_phase === null) {
                results.num_coils_per_phase = results.coil_per_phase_180 * 2;
                something_calculated_in_this_pass = true;
            }

            if (results.num_coils_per_phase !== null && results.num_stator_coils === null) {
                results.num_stator_coils = DEFAULT_NUM_PHASE * results.num_coils_per_phase;
                something_calculated_in_this_pass = true;
            }

            if (results.num_stator_coils !== null && results.magnet_poles === null) {
                results.magnet_poles = results.num_stator_coils + 2;
                something_calculated_in_this_pass = true;
            }

            if (results.trace_length_radial_mm !== null && results.current_conducting_radial_mm === null) {
                results.current_conducting_radial_mm = results.trace_length_radial_mm - DEFAULT_TRACE_WIDTH_CURVED_LINE / 2;
                something_calculated_in_this_pass = true;
            }

            if (results.number_of_lines !== null && results.current_conducting_radial_mm !== null && results.total_conductor_length_m === null) {
                results.total_conductor_length_m = (results.current_conducting_radial_mm * results.number_of_lines) / 1000;
                something_calculated_in_this_pass = true;
            }

            if (results.total_conductor_length_m !== null && results.on_conductor_length_m === null) {
                results.on_conductor_length_m = (results.total_conductor_length_m / 3) * 2;
                something_calculated_in_this_pass = true;
            }

            if (results.non_magnet_area_mm === null && results.trace_radius_id_mm !== null) {
                results.non_magnet_area_mm = results.trace_radius_id_mm;
                something_calculated_in_this_pass = true;
            }

            if (results.non_magnet_area_mm !== null && results.current_conducting_radial_mm !== null && results.radius_od_mm === null) {
                results.radius_od_mm = results.non_magnet_area_mm + results.current_conducting_radial_mm;
                something_calculated_in_this_pass = true;
            }

            if (results.non_magnet_area_mm !== null && results.radius_od_mm !== null && results.avg_torque_radius_mm === null) {
                results.avg_torque_radius_mm = (results.non_magnet_area_mm + results.radius_od_mm) / 2;
                something_calculated_in_this_pass = true;
            }

            if (results.on_conductor_length_m !== null && results.num_pcb_in_series !== null && results.conductor_length_2phase_m === null) {
                results.conductor_length_2phase_m = results.on_conductor_length_m * results.num_pcb_in_series;
                something_calculated_in_this_pass = true;
            }

            if (results.num_pcb_in_series !== null && results.total_conductor_length_m !== null && results.total_pcb === null) {
                results.total_pcb = results.num_pcb_in_series * results.total_conductor_length_m;
                something_calculated_in_this_pass = true;
            }

            if (results.num_pcb_in_series !== null && results.layer_parallel !== null && results.stack_up_height_mm === null) {
                results.stack_up_height_mm =
                    results.num_pcb_in_series * results.layer_parallel * DEFAULT_PCB_THICKNESS_MM +
                    (results.layer_parallel * results.num_pcb_in_series + 1) * DEFAULT_PM_ROTOR_THICKNESS_MM +
                    results.layer_parallel * results.num_pcb_in_series * DEFAULT_AIR_GAP_MM;
                something_calculated_in_this_pass = true;
            }

            if (results.trace_length_radial_mm !== null && results.trace_length_radial_mm > 0 && results.trace_width_id_mm !== null && results.trace_thickness_od_mm !== null && results.average_trace_width_mm === null) {
                results.average_trace_width_mm =
                    (((results.trace_width_id_mm + results.trace_thickness_od_mm) * results.trace_length_radial_mm) / 2 +
                        DEFAULT_TRACE_GAP_MM * DEFAULT_TRACE_GAP_MM) /
                    (results.trace_length_radial_mm + DEFAULT_TRACE_GAP_MM);
                something_calculated_in_this_pass = true;
            }

            if (results.layer_parallel !== null && results.required_copper_thickness_mm === null) {
                results.required_copper_thickness_mm = DEFAULT_ONE_PCB_OZ_FT2 * results.layer_parallel;
                something_calculated_in_this_pass = true;
            }
        }

        // 3. Force Calculation (depends on current, conductor length, magnet strength)
        if (results.force_n === null && results.current_a !== null && results.conductor_length_2phase_m !== null && DEFAULT_MAGNET_STRENGTH_T !== null) {
            results.force_n = results.current_a * results.conductor_length_2phase_m * DEFAULT_MAGNET_STRENGTH_T;
            something_calculated_in_this_pass = true;
        }

        // 4. Torque Calculation (can be derived from force and radius, or power and RPM)
        if (results.torque_nm === null && results.force_n !== null && results.avg_torque_radius_mm !== null && results.avg_torque_radius_mm > 0) {
            results.torque_nm = results.force_n * (results.avg_torque_radius_mm / 1000);
            something_calculated_in_this_pass = true;
        }

        // 5. Efficiency Calculation (can be derived from power in/out, or electrical/mechanical losses)
        // This is a complex one, try to calculate it if not provided
        if (results.efficiency_percent === null) {
            let calculated_eff = null;
            // Method 1: From Power In and Power Out
            if (results.power_out_kw !== null && results.power_in_kw !== null && results.power_in_kw > 0) {
                calculated_eff = (results.power_out_kw / results.power_in_kw) * 100;
            }
            // Method 2: From Electrical parameters (simplified loss model)
            else if (results.voltage_v !== null && results.current_a !== null && results.conductor_length_2phase_m !== null && results.trace_width_id_mm !== null && results.layer_parallel !== null) {
                const Pin_kw = (results.voltage_v * results.current_a) / 1000;
                const Rw = calculate_winding_resistance(results);
                const Pcu_kw = (results.current_a * results.current_a * Rw) / 1000;
                const Pcore_kw = 0.05 * Pin_kw; // Estimate core loss as 5% of input power
                const Pmech_kw = 0.03 * Pin_kw; // Estimate mechanical loss as 3% of input power

                if (Pin_kw > Pcu_kw + Pcore_kw + Pmech_kw) {
                    const Pout_kw_derived = Pin_kw - Pcu_kw - Pcore_kw - Pmech_kw;
                    if (Pout_kw_derived > 0) {
                        calculated_eff = (Pout_kw_derived / Pin_kw) * 100;
                        if (results.power_out_kw === null) results.power_out_kw = Pout_kw_derived; // Update power out if derived
                    }
                }
            }

            if (calculated_eff !== null && calculated_eff >= 0 && calculated_eff <= 100) {
                results.efficiency_percent = calculated_eff;
                something_calculated_in_this_pass = true;
            }
        }

        // 6. Weight Calculation
        if (results.weight_g === null && results.total_pcb !== null && pcb_params !== null && pcb_params.weight_factor !== null) {
            results.weight_g = results.total_pcb * pcb_params.weight_factor;
            something_calculated_in_this_pass = true;
        }

        // 7. Power Density Calculation
        if (results.power_density_kw_kg === null && results.power_out_kw !== null && results.weight_g !== null && results.weight_g > 0) {
            results.power_density_kw_kg = results.power_out_kw / (results.weight_g / 1000);
            something_calculated_in_this_pass = true;
        }

        // 8. kV Rating Calculation
        if (results.kv_rating === null && results.rpm !== null && results.voltage_v !== null && results.voltage_v > 0) {
            results.kv_rating = results.rpm / results.voltage_v;
            something_calculated_in_this_pass = true;
        }

        // 9. Estimated Cost Calculation
        if (results.cost_inr === null && results.total_pcb !== null && pcb_params !== null && results.number_of_lines !== null) {
            const estimated_num_magnets = results.number_of_lines + 2; // Simplified estimation
            results.cost_inr =
                results.total_pcb * pcb_params.cost_factor_pcb +
                estimated_num_magnets * pcb_params.cost_factor_magnets +
                pcb_params.miscellaneous_cost;
            something_calculated_in_this_pass = true;
        }

        // If no new values were calculated in this pass, stop iterating
        if (!something_calculated_in_this_pass) {
            break;
        }
    }

    // Update results display
    document.getElementById('powerIn').textContent = fmt(results.power_in_kw, ' kW');
    document.getElementById('currentResult').textContent = fmt(results.current_a, ' A');
    document.getElementById('voltageResult').textContent = fmt(results.voltage_v, ' V');
    document.getElementById('efficiencyResult').textContent = fmt(results.efficiency_percent, '%');
    document.getElementById('powerOutResult').textContent = fmt(results.power_out_kw, ' kW');
    document.getElementById('torqueResult').textContent = fmt(results.torque_nm, ' Nm');
    document.getElementById('rpmResult').textContent = fmt(results.rpm, '');
    document.getElementById('forceResult').textContent = fmt(results.force_n, ' N');
    document.getElementById('pcbODResult').textContent = fmt(results.pcb_stator_od_mm, ' mm');
    document.getElementById('stackHeight').textContent = fmt(results.stack_up_height_mm, ' mm');
    document.getElementById('weightResult').textContent = fmt(results.weight_g, ' g');
    // document.getElementById('magnetsResult').textContent = fmt(results.magnet_poles, '');
    document.getElementById('powerDensity').textContent = fmt(results.power_density_kw_kg, ' kW/kg');
    document.getElementById('kvRating').textContent = fmt(results.kv_rating, ' RPM/V');
    // document.getElementById('conductorLength').textContent = fmt(results.conductor_length_2phase_m, ' m');
    document.getElementById('costResult').textContent = fmt(results.cost_inr, ' ₹');

    // Update highlight value
    const powerDensity = results.power_density_kw_kg;
    if (powerDensity !== null && !isNaN(powerDensity)) {
        document.getElementById('highlightValue').textContent = fmt(powerDensity, ' kW/kg');
        const highlightDiv = document.querySelector('.result-highlight');
        if (powerDensity > 10) {
            highlightDiv.innerHTML = `
                <div>Power Density</div>
                <div class="value">${fmt(powerDensity, ' kW/kg')}</div>
                <div>Excellent for aerospace applications</div>
            `;
            highlightDiv.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
        } else if (powerDensity > 5) {
            highlightDiv.innerHTML = `
                <div>Power Density</div>
                <div class="value">${fmt(powerDensity, ' kW/kg')}</div>
                <div>Good for aerospace applications</div>
            `;
            highlightDiv.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
        } else {
            highlightDiv.innerHTML = `
                <div>Power Density</div>
                <div class="value">${fmt(powerDensity, ' kW/kg')}</div>
                <div>Adequate for aerospace applications</div>
            `;
            highlightDiv.style.background = 'linear-gradient(135deg, #e67e22, #d35400)';
        }
    } else {
        document.getElementById('highlightValue').textContent = 'N/A';
        const highlightDiv = document.querySelector('.result-highlight');
        highlightDiv.innerHTML = `
            <div><h1>Contact Us</h1></div>
            
            <div>Need help with the PCM Motor Calculator?</div>
            <div>📧 Email: bibhuti@airbuddy.in</div>
            <div>📞 Phone: +917079142368</div>
        `;
        highlightDiv.style.background = 'linear-gradient(135deg, #2cf92c, #45b705)'; // Default color
    }

    // Update unit colors for active inputs
    document.querySelectorAll('.unit').forEach(unit => {
        unit.style.color = '#777';
        unit.style.fontWeight = 'normal';
    });

    document.querySelectorAll('input:focus').forEach(input => {
        const unit = input.nextElementSibling;
        if (unit && unit.classList.contains('unit')) {
            unit.style.color = '#3498db';
            unit.style.fontWeight = 'bold';
        }
    });
}