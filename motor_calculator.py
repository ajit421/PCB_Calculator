import math
from config import PCB_OD_PARAMETERS
from config import DEFAULT_TRACE_GAP_MM, DEFAULT_AIR_GAP_MM, DEFAULT_PCB_THICKNESS_MM, DEFAULT_PM_ROTOR_THICKNESS_MM
from inputs import collect_inputs
from utils import fmt
from calculations.efficiency import calculate_efficiency
from calculations.cost_weight import calculate_cost_and_weight
from calculations.mechanical import calculate_mechanical_results
from calculations.electrical import calculate_electrical_results


def calculate_results(inputs):
    """
    If a value cannot be calculated due to missing dependencies,
    it will remain None.
    """
    # Initialize results dictionary with input values and None for outputs that need calculation
    results = {

        "power_out_kw": inputs.get("power_out_kw"),
        "torque_nm": inputs.get("torque_nm"),
        "rpm": inputs.get("rpm"),
        "current_a": inputs.get("current_a"),
        "voltage_v": inputs.get("voltage_v"),
        "power_in_kw": inputs.get("power_in_kw"),
        "efficiency_percent": inputs.get("efficiency_percent"),
        "pcb_stator_od_mm": inputs.get("pcb_stator_od_mm"),
        
        "force_n": None,
        "size_mm": None,
        "weight_g": None,
        "power_density_kw_kg": None,
        "kv_rating": None,
        "cost_inr": None,
        "status_messages": [] # store messages success or failure
    }

    # Extract PCB Stator OD specific parameters if OD was provided
    pcb_od_mm = inputs.get("pcb_stator_od_mm")

    pcb_params = PCB_OD_PARAMETERS.get(pcb_od_mm) 

    if pcb_od_mm is None:
        results["status_messages"].append("PCB Stator OD (Outer Diameter) was not provided. Dimensions, weight, power density, and cost cannot be fully calculated.")
    else:
        # Assign predefined parameters based on selected OD
        results["pcb_stator_id_mm"] = pcb_params["pcb_stator_id_mm"]
        results["trace_width_id_mm"] = pcb_params["trace_width_id_mm"]
        results["num_pcb_in_series"] = pcb_params["num_pcb_in_series"]
        results["layer_parallel"] = pcb_params["layer_parallel"]

        results["cost_factor_pcb"] = pcb_params["cost_factor_pcb"]
        results["cost_factor_magnets"] = pcb_params["cost_factor_magnets"]
        results["miscellaneous_cost"] = pcb_params["miscellaneous_cost"]
        results["weight_factor"] = pcb_params["weight_factor"]


        # Calculate basic derived dimensions for the selected OD
        # formulas from 'formulas_rev.txt'

        # id_circumference_mm = pcb_stator_id_mm *pi
        results["id_circumference_mm"] = results["pcb_stator_id_mm"] * math.pi

        # Trace radius ID is Pcb stator ID / 2
        results["trace_radius_id_mm"] = results["pcb_stator_id_mm"] / 2

        # non magnet area is trace radius ID
        results["non_magnet_area_mm"] = results["trace_radius_id_mm"]

        # Calculate `total pcb`= num_pcb_in_series * layer_parallel
        results["total_pcb"] = results["num_pcb_in_series"] * results["layer_parallel"]

        # Trace radius OD = (Trace OD/2) - DEFAULT_TRACE_GAP_MM
        results["trace_radius_od_mm"] = (pcb_od_mm / 2) - DEFAULT_TRACE_GAP_MM
        results["trace_od_circumference_mm"] = 2 * math.pi * results["trace_radius_od_mm"]

        # Trace length radial = (Trace radius OD - Trace radius ID)
        results["trace_length_radial_mm"] = results["trace_radius_od_mm"] - results["trace_radius_id_mm"]

        # currentConductingRadial = trace Length radial - (traceWidth / 2)
        # Assuming traceWidth refers to trace_width_id_mm for this calculation
        results["current_conducting_radial_mm"] = results["trace_length_radial_mm"] - (results["trace_width_id_mm"] / 2)
        if results["current_conducting_radial_mm"] < 0: # positive
            results["current_conducting_radial_mm"] = 0
            results["status_messages"].append("Calculated current conducting radial length is negative")

        # Calculate `number of Lines`
        # Approximating spreadsheet functions CLEAN(CEILING(X), 6) as ceil then round to nearest multiple of 6

        # if (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM) > 0:
        #     temp_num_lines = results["id_circumference_mm"] / (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM)
        #     results["number_of_lines"] = math.ceil(temp_num_lines)
        #     results["number_of_lines"] = round(results["number_of_lines"] / 6) * 6 # nearest multiple of 6
        #     if results["number_of_lines"] == 0:
        #         results["number_of_lines"] = 6 # minimum value

        if (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM) > 0:
            temp_num_lines = results["id_circumference_mm"] / (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM)
            results["number_of_lines"] = math.ceil(temp_num_lines / 6) * 6 # nearest multiple of 6
            if results["number_of_lines"] == 0:
                results["number_of_lines"] = 6 # minimum value

        else: 
            results["number_of_lines"] = None
            results["status_messages"].append("Cannot determine number of lines due to zero trace width or gap. This affects several downstream calculations.")

        # totalConductorLength(1pcb) = (currentConductingRadial * number of Lines) / 1000
        if results["current_conducting_radial_mm"] is not None and results["number_of_lines"] is not None:
            results["total_conductor_length_1pcb_m"] = (results["current_conducting_radial_mm"] * results["number_of_lines"]) / 1000
        else:
            results["total_conductor_length_1pcb_m"] = None

        # onConductorLength = (totalConductorLength(1pcb) / 3) * 2
        if results["total_conductor_length_1pcb_m"] is not None:
            results["on_conductor_length_m"] = (results["total_conductor_length_1pcb_m"] / 3) * 2
        else:
            results["on_conductor_length_m"] = None

        # conductor length(2 phase switch ON) = onConductorLength * number of pcb in series
        if results["on_conductor_length_m"] is not None and results["num_pcb_in_series"] is not None:
            results["conductor_length_2phase_m"] = results["on_conductor_length_m"] * results["num_pcb_in_series"]

        else:
            results["conductor_length_2phase_m"] = None

        # radius OD = non magnet area + currentConductingRadial
        if results["non_magnet_area_mm"] is not None and results["current_conducting_radial_mm"] is not None:
            results["radius_od_mm"] = results["non_magnet_area_mm"] + results["current_conducting_radial_mm"]
        else:
            results["radius_od_mm"] = None

        # avg torque radius = (non magnet area + radius OD) / 2
        if results["non_magnet_area_mm"] is not None and results["radius_od_mm"] is not None:
            results["avg_torque_radius_mm"] = (results["non_magnet_area_mm"] + results["radius_od_mm"]) / 2

        else:
            results["avg_torque_radius_mm"] = None

        # stack up height
        if results["num_pcb_in_series"] is not None and results["layer_parallel"] is not None:
            results["stack_up_height_mm"] = (results["num_pcb_in_series"] * results["layer_parallel"] * DEFAULT_PCB_THICKNESS_MM) + \
                                             ((results["num_pcb_in_series"] * results["layer_parallel"] * DEFAULT_PM_ROTOR_THICKNESS_MM) + DEFAULT_PM_ROTOR_THICKNESS_MM) + \
                                             (DEFAULT_AIR_GAP_MM * results["num_pcb_in_series"] * results["layer_parallel"])
        else:
            results["stack_up_height_mm"] = None

    # Overall Size 
    if results["stack_up_height_mm"] is not None and pcb_od_mm is not None:
        results["size_mm"] = pcb_od_mm + results["stack_up_height_mm"] + 5 # +5mm for covering
        # size_mm = pcb_od_mm + stack_up_height_mm + 5
    else:
        results["size_mm"] = None
    
    # if results["voltage_v"] <= 0:
    #         results["status_messages"].append("Voltage must be greater than 0.")
    
    # if results["current_a"] <= 0:
    #     results["status_messages"].append("Current must be greater than 0.")
    

    # Iterative calculation loop for primary outputs 
    # This loop attempts to calculate values multiple times as new dependencies might become available
    # Power → Voltage → Current → Force... not possible to calculate in one loop

    max_iterations = 7 # A fixed number of iterations
    for _ in range(max_iterations):


        something_calculated_in_this_pass = False




        if calculate_efficiency(results):
            something_calculated_in_this_pass = True
        if calculate_mechanical_results(results):
            something_calculated_in_this_pass = True
        if calculate_electrical_results(results):
            something_calculated_in_this_pass = True
        if pcb_params and calculate_cost_and_weight(results, pcb_params):
            something_calculated_in_this_pass = True



        # If no new values were calculated in this pass, stop iterating
        if not something_calculated_in_this_pass:
            break

    # After all iterations, add status messages for any remaining uncalculated outputs
    final_outputs = ["power_out_kw", "torque_nm", "rpm", "force_n", "current_a", "voltage_v", "power_in_kw",
                      "size_mm", "weight_g", "power_density_kw_kg", "kv_rating", "cost_inr", "efficiency_percent"]

    for key in final_outputs:
        if results.get(key) is None:
            results["status_messages"].append(f"'{key.replace('_', ' ').title()}' could not be calculated due to insufficient input data or missing dependencies")
    return results




# # Overall Size 
# if results["stack_up_height_mm"] is not None and pcb_od_mm is not None:
#     results["size_mm"] = pcb_od_mm + results["stack_up_height_mm"] + 5 # +5mm for covering
#     # size_mm = pcb_od_mm + stack_up_height_mm + 5
# else:
#     results["size_mm"] = None
