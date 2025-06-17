import math
from config import DEFAULT_TRACE_GAP_MM, DEFAULT_AIR_GAP_MM
from config import DEFAULT_PCB_THICKNESS_MM, DEFAULT_PM_ROTOR_THICKNESS_MM

def calculate_mechanical_results(results):
    # id_circumference_mm = pcb_stator_id_mm *pi
    results["id_circumference_mm"] = results["pcb_stator_id_mm"] * math.pi

    # Trace radius ID is Pcb stator ID / 2
    results["trace_radius_id_mm"] = results["pcb_stator_id_mm"] / 2

    # non magnet area is trace radius ID
    results["non_magnet_area_mm"] = results["trace_radius_id_mm"]

    # Calculate `total pcb`= num_pcb_in_series * layer_parallel
    results["total_pcb"] = results["num_pcb_in_series"] * results["layer_parallel"]

    # Trace radius OD = (Trace OD/2) - DEFAULT_TRACE_GAP_MM
    results["trace_radius_od_mm"] = ("pcb_od_mm" / 2) - DEFAULT_TRACE_GAP_MM
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

    return results
