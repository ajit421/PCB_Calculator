import math
import inputs


def calculate_cost_and_weight(results, pcb_params):


    # Calculate Overall Size (mm)
    if results["size_mm"] is None and results["pcb_stator_od_mm"] is not None and results["stack_up_height_mm"] is not None:
        results["size_mm"] = results["pcb_stator_od_mm"] + results["stack_up_height_mm"] + 5
        something_calculated_in_this_pass = True

    # If size_mm is still None, it means we cannot calculate size without PCB OD or stack height
    elif results["size_mm"] is None:
        results["status_messages"].append("Overall size could not be calculated due to missing PCB Stator OD or stack height.")

    # Calculate Weight (g)
    if results["weight_g"] is None and results["total_pcb"] is not None and pcb_params is not None:
        results["weight_g"] = results["total_pcb"] * pcb_params["weight_factor"] # weight(gm) = (total pcb * (factor))
        something_calculated_in_this_pass = True

    # Calculate Power Density (kW/kg)
    if results["power_density_kw_kg"] is None:
        if results["power_out_kw"] is not None and results["weight_g"] is not None and results["weight_g"] > 0:

            results["power_density_kw_kg"] = results["power_out_kw"] / (results["weight_g"] / 1000) # power density = powerOut / (weight/1000)
            something_calculated_in_this_pass = True
            
        # If Power Out and Power Density are given 
        elif results["power_out_kw"] is not None and inputs.get("power_density_kw_kg") is not None and inputs["power_density_kw_kg"] > 0:
            if results["weight_g"] is None: # Only calculate if weight is not already known
                results["weight_g"] = (results["power_out_kw"] / inputs["power_density_kw_kg"]) * 1000 # weight = (powerOut / power density) * 1000

            results["power_density_kw_kg"] = inputs["power_density_kw_kg"] # Set power density from input as it was used to derive weight
            something_calculated_in_this_pass = True

    # Calculate kV Rating
    if results["kv_rating"] is None:
        if results["rpm"] is not None and results["voltage_v"] is not None and results["voltage_v"] > 0:
            results["kv_rating"] = results["rpm"] / results["voltage_v"] # KV rating = rpm / voltage 
            something_calculated_in_this_pass = True

        elif results["rpm"] is not None and inputs.get("voltage_v") is not None and inputs["voltage_v"] > 0:
            # If voltage was provided as an input, use it to calculate kV rating
            results["kv_rating"] = results["rpm"] / inputs["voltage_v"] # KV rating = rpm / voltage
            something_calculated_in_this_pass = True

    # Calculate Estimated Cost (₹)
    if results["cost_inr"] is None and results["total_pcb"] is not None and pcb_params is not None:
        # 'no of magnets' is not directly calculable from the given inputs and formulas
        # For demonstration, we'll estimate 'no of magnets' based on 'number of lines'
        # This is an "estimation not directly derived from provided sources"and may require independent verification

        estimated_num_magnets = None
        if results["number_of_lines"] is not None:
            estimated_num_magnets = results["number_of_lines"] * 2  # For 3-phase motor
            if estimated_num_magnets <= 0:
                estimated_num_magnets = 1 # non-zero

        if estimated_num_magnets is not None:
            results["cost_inr"] = (results["total_pcb"] * pcb_params["cost_factor_pcb"]) + \
                                    (estimated_num_magnets * pcb_params["cost_factor_magnets"]) + \
                                    pcb_params["miscellaneous_cost"] # cost = (total pcb * cost factor) + (no of magnets * cost factor magnets) + miscellaneous cost
            something_calculated_in_this_pass = True

        else:
            results["status_messages"].append("Cost estimation requires 'number of lines' (to infer number of magnets), which could not be determined.")

    return results, something_calculated_in_this_pass


