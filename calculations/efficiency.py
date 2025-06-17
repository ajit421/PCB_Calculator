import math
from config import DEFAULT_MAGNET_STRENGTH_T, DEFAULT_ONE_PCB_OZ_FT2
# from motor_calculator import calculate_winding_resistance




def calculate_winding_resistance(results):
    """Calculate winding resistance from PCB trace geometry"""
    required_keys = [
        "conductor_length_2phase_m", 
        "trace_width_id_mm", 
        "layer_parallel"
    ]
    
    if not all(key in results for key in required_keys):
        return 0.2  # Default estimate
    
    try:
        # Copper properties
        resistivity = 1.68e-8  # Ω·m (copper)
        copper_thickness = DEFAULT_ONE_PCB_OZ_FT2 * 34.8e-6  # Convert oz/ft² to meters
        
        # Calculate cross-sectional area (m²)
        trace_width_m = results["trace_width_id_mm"] * 1e-3
        cross_section = trace_width_m * copper_thickness
        
        # Calculate total resistance
        total_resistance = (resistivity * results["conductor_length_2phase_m"]) / cross_section
        
        # Account for parallel layers
        parallel_resistance = total_resistance / results["layer_parallel"]
        
        return max(parallel_resistance, 0.001)  # Ensure non-zero value
    except Exception as e:
        results.setdefault("status_messages", []).append(f"Error in winding resistance calculation: {e}")
        # Fallback to default on any error
        return 0.2


def calculate_efficiency(results):
    """
    Calculate motor efficiency using one of three methods:
    1. Direct power ratio (power_out / power_in)
    2. Electrical method (voltage and current with losses)
    3. Force method (force and conductor length with losses)
    Returns True if efficiency was calculated, False otherwise.
    """
    # Only calculate if efficiency isn't already set
    if results.get("efficiency_percent") is not None:
        return False
        
    # Method 1: Using Power Out and Power In
    if results.get("power_out_kw") is not None and results.get("power_in_kw") is not None:
        if results["power_in_kw"] > 0:
            eff = (results["power_out_kw"] / results["power_in_kw"]) * 100
            if 0 < eff <= 100:
                results["efficiency_percent"] = eff
                return True
            else:
                if eff > 100:
                    results.setdefault("status_messages", []).append( "Warning: Efficiency >100% (Power Ratio Method) - check input values")
                else:
                    results.setdefault("status_messages", []).append( "Warning: Efficiency ≤0% (Power Ratio Method) - check input values")
    
    # Method 2: Using Voltage and Current (with losses)
    if results.get("voltage_v") is not None and results.get("current_a") is not None:
        # Calculate input power in kW
        Pin_kw = (results["voltage_v"] * results["current_a"]) / 1000 # power_in_kw = voltage * current / 1000
        
        # Calculate winding resistance
        Rw = calculate_winding_resistance(results)
        I0 = 0.3  # No-load current (A)
        
        # Calculate losses in kW
        Pcu_kw = (results["current_a"] ** 2) * Rw / 1000 # pcu_kw = (current_a ** 2) * Rw / 1000
        # Core loss (assumed 5% of input power)
        Pcore_kw = results["voltage_v"] * I0 / 1000 # pcore_kw = voltage * I0 / 1000
        # Mechanical loss (assumed 3% of input power)
        Pmech_kw = 0.03 * Pin_kw

        if Pin_kw > (Pcu_kw + Pcore_kw + Pmech_kw):
            Pout_kw = Pin_kw - Pcu_kw - Pcore_kw - Pmech_kw
            eff = (Pout_kw / Pin_kw) * 100
            
            if 0 < eff <= 100:
                results["power_out_kw"] = Pout_kw
                results["efficiency_percent"] = eff
                return True
            elif eff > 100:
                results.setdefault("status_messages", []).append("Warning: Efficiency >100% (Electrical Method) - check loss model")
            else:
                results.setdefault("status_messages", []).append("Warning: Efficiency ≤0% (Electrical Method) - losses too high")
    
    # Method 3: Force-Based with Losses
    if (results.get("force_n") is not None and 
        results.get("conductor_length_2phase_m") is not None and 
        DEFAULT_MAGNET_STRENGTH_T is not None and
        results.get("rpm") is not None and
        results.get("avg_torque_radius_mm") is not None):
        
        try:
            # Calculate current from Lorentz force
            I = results["force_n"] / (results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T)
            
            # Calculate winding resistance
            Rw = calculate_winding_resistance(results)
            
            # Convert to SI units
            radius_m = results["avg_torque_radius_mm"] / 1000
            angular_velocity = results["rpm"] * (2 * math.pi) / 60
            
            # Calculate electromagnetic power
            em_power_kw = results["force_n"] * angular_velocity * radius_m / 1000
            
            # Estimate losses
            I0 = 0.3  # No-load current (A)
            Pcu_kw = (I ** 2) * Rw / 1000
            Pcore_kw = 0.05 * em_power_kw  # Core loss (5% of EM power)
            Pmech_kw = 0.03 * em_power_kw  # Mechanical loss (3% of EM power)
            
            # Calculate output power and efficiency
            if em_power_kw > (Pcu_kw + Pcore_kw + Pmech_kw):
                Pout_kw = em_power_kw - Pcore_kw - Pmech_kw
                Pin_kw = em_power_kw + Pcu_kw
                eff = (Pout_kw / Pin_kw) * 100
                
                if 0 < eff <= 100:
                    results["power_out_kw"] = Pout_kw
                    results["efficiency_percent"] = eff
                    results["current_a"] = I
                    return True
        except ZeroDivisionError:
            results.setdefault("status_messages", []).append("Error in force-based efficiency: Division by zero")
    
    # If all methods fail
    results.setdefault("status_messages", []).append("Efficiency could not be calculated - insufficient data")
    return False



# # In your calculate_results() function, replace the existing efficiency code with:

# # Calculate efficiency using best available method
# if not something_calculated_in_this_pass:
#     if calculate_efficiency(results):
#         something_calculated_in_this_pass = True

# # Add efficiency validation
# if results.get("efficiency_percent") is not None:
#     eff = results["efficiency_percent"]
#     if eff > 100:
#         results.setdefault("status_messages", []).append("Warning: Efficiency exceeds 100% -> check input values")
#     elif eff <= 0:
#         results.setdefault("status_messages", []).append("Warning: Efficiency is 0 or negative -> check input values")

#         something_calculated_in_this_pass = True

