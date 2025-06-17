import math
from config import DEFAULT_MAGNET_STRENGTH_T


def calculate_electrical_results(results, something_calculated_in_this_pass=False):

    # NEW: Calculate Power Out from Torque and RPM
    if results["power_out_kw"] is None:
        if results["torque_nm"] is not None and results["rpm"] is not None:
            omega = 2 * math.pi * results["rpm"] / 60  # rad/s
            results["power_out_kw"] = (results["torque_nm"] * omega) / 1000
            something_calculated_in_this_pass = True

    # NEW: Calculate RPM from Power Out and Torque
    if results["rpm"] is None:
        if results["power_out_kw"] is not None and results["torque_nm"] is not None and results["torque_nm"] != 0:
            results["rpm"] = (results["power_out_kw"] * 9548.8) / results["torque_nm"]
            something_calculated_in_this_pass = True

    # NEW: Calculate Voltage from Power In and Current
    if results["voltage_v"] is None:
        if results["power_in_kw"] is not None and results["current_a"] is not None and results["current_a"] != 0:
            results["voltage_v"] = (results["power_in_kw"] * 1000) / results["current_a"]
            something_calculated_in_this_pass = True





    # ----------------------- Electrical Input Calculations -----------------------

    # Calculate Power In (kW)

    if results["power_in_kw"] is None:
        if results["current_a"] is not None and results["voltage_v"] is not None:
            results["power_in_kw"] = (results["current_a"] * results["voltage_v"]) / 1000 # powerIn = (current * voltage) / 1000
            something_calculated_in_this_pass = True

        elif results["power_out_kw"] is not None and results["efficiency_percent"] is not None and results["efficiency_percent"] > 0:
            results["power_in_kw"] = (results["power_out_kw"] / results["efficiency_percent"]) * 100 # powerIn = (powerOut / efficiency) * 100

            something_calculated_in_this_pass = True

    # Calculate Current (A)
    if results["current_a"] is None:
        if results["power_in_kw"] is not None and results["voltage_v"] is not None and results["voltage_v"] > 0:
            results["current_a"] = (results["power_in_kw"] * 1000) / results["voltage_v"] # current = (powerIn * 1000) / voltage
            something_calculated_in_this_pass = True
            
        elif results["force_n"] is not None and results["conductor_length_2phase_m"] is not None and DEFAULT_MAGNET_STRENGTH_T is not None and  \
            results["conductor_length_2phase_m"] is not None and results["conductor_length_2phase_m"] > 0 and \
                (results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T) != 0:

            results["current_a"] = results["force_n"] / (results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T) # current = force / (conductor Length * magnet Strength)
            something_calculated_in_this_pass = True


    # Calculate Voltage (V)
    if results["voltage_v"] is None:
        if results["power_in_kw"] is not None and results["current_a"] is not None and results["current_a"] > 0:
            results["voltage_v"] = (results["power_in_kw"] * 1000) / results["current_a"] # voltage = (powerIn * 1000) / current
            something_calculated_in_this_pass = True

        elif results["rpm"] is not None and results.get("kv_rating") is not None and results["kv_rating"] > 0:
            results["voltage_v"] = results["rpm"] / results["kv_rating"] # voltage = rpm / KV rating

            something_calculated_in_this_pass = True

    return results, something_calculated_in_this_pass
