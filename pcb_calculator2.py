import math

from matplotlib.pylab import angle 

# ------------------------- Constants and Configuration Data -------------------------

# Default physical constants
DEFAULT_AIR_GAP_MM = 0.1 # Air gap
DEFAULT_NUM_PHASE = 3 # Number of phases
DEFAULT_PCB_THICKNESS_MM = 1.6 # PCB thickness
DEFAULT_PM_ROTOR_THICKNESS_MM = 3.0 # PM rotor thickness
DEFAULT_ONE_PCB_OZ_FT2 = 40 # Copper weight per layer
DEFAULT_MAGNET_STRENGTH_T = 0.5 # Magnet Strength
DEFAULT_CELL_UNIT_CHARGE_V = 4.2 # Cell unit charge
DEFAULT_TRACE_GAP_MM = 0.225 # Trace gap (Constant across all ODs)

# Predefined values based on PCB Stator Outer Diameter (OD)
PCB_OD_PARAMETERS = {
    50: {
        "pcb_stator_id_mm": 8,
        "trace_width_id_mm": 3,
        "num_pcb_in_series": 15,
        "layer_parallel": 2,
        "cost_factor_pcb": 80,
        "cost_factor_magnets": 80,
        "miscellaneous_cost": 500,
        "weight_factor": (5 + 7) # weight calculation
    },
    100: {
        "pcb_stator_id_mm": 49,
        "trace_width_id_mm": 4.9,
        "num_pcb_in_series": 5,
        "layer_parallel": 6,
        "cost_factor_pcb": 130,
        "cost_factor_magnets": 130,
        "miscellaneous_cost": 1000,
        "weight_factor": (8 + 10) # weight calculation
    },
    150: {
        "pcb_stator_id_mm": 100,
        "trace_width_id_mm": 5.3,
        "num_pcb_in_series": 7,
        "layer_parallel": 10,
        "cost_factor_pcb": 200,
        "cost_factor_magnets": 200,
        "miscellaneous_cost": 1500,
        "weight_factor": (11 + 12) # weight calculation
    }
}

# ----------------------------- Input Handling Functions ---------------------------------------

# Function to get float input from the user
def get_input_float(prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            return None # empty input

        try:
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a number or leave it blank.")

# Function to get Efficiency percent input from the user
# This function ensures the efficiency is between 0 and 100
def get_Efficiency_percent_input(prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            return None # empty input

        try:
            efficiency_percent = float(user_input)
            if 0 <= efficiency_percent <= 100:
                return efficiency_percent
            else:
                print("Efficiency should be between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a number or leave it blank.")

# Function to get PCB Stator OD input from the user
def get_pcb_stator_od_input(prompt, options):
    options_str = ", ".join(map(str, options))
    while True:
        user_input = input(f"{prompt} (Options: {options_str}, or enter any value): ").strip()
        if user_input == "":
            return None # empty input
        try:
            od = int(user_input)
            return od
        except ValueError:
            print(f"Invalid input. Please enter a number from the options or leave it blank.")
            
        #     if od in options:
        #         return od
        #     else:
        #         print(f"Invalid option. Please choose from {options_str}.")
        # except ValueError:
        #     print("Invalid input. Please enter a number from the options or leave it blank.")


# --------------------Step 1: Collect inputs from the user--------------------

def collect_inputs():
    print("\n--- AirBuddy Aerospace PCB Calculator Input ---")

    inputs = {} # store user inputs

    # Mechanical Output
    inputs["power_out_kw"] = get_input_float("Enter Power Out (kW): ")
    inputs["torque_nm"] = get_input_float("Enter Torque (Nm): ")
    inputs["rpm"] = get_input_float("Enter RPM: ")

    # Electrical Input
    inputs["current_a"] = get_input_float("Enter Current (A): ")
    inputs["voltage_v"] = get_input_float("Enter Voltage (V): ")
    inputs["num_cell_series"] = get_input_float("Enter Number of Cells in Series : ")

    # inputs["power_in_kw"] = get_input_float("Enter Power (kW): ")

    # Efficiency & Dimensions Inputs
    inputs["efficiency_percent"] = get_Efficiency_percent_input("Enter Efficiency (%): ")
    inputs["pcb_stator_od_mm"] = get_pcb_stator_od_input("Select PCB Stator OD (mm)", list(PCB_OD_PARAMETERS.keys()))
    return inputs

# ----------------------- Main Calculation Logic -----------------------
# calculate all possible outputs using available inputs
# It uses an interdependencies between formulas

# --------------------Step 2: Perform calculations based on the collected inputs--------------------


def calculate_winding_resistance(results):
    """Calculate winding resistance from PCB trace geometry"""
    required_keys = ["conductor_length_2phase_m", "trace_width_id_mm", "layer_parallel"]
    
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
        parallel_resistance = total_resistance / results["layer_parallel"] * results.get("num_pcb_in_series", 1)  # num_pcb_in_series is used to scale resistance
        
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
        "power_in_kw": None, # will be calculated later
        "efficiency_percent": inputs.get("efficiency_percent"),
        "pcb_stator_od_mm": inputs.get("pcb_stator_od_mm"),
        "num_cell_series" : inputs.get("num_cell_series"),
        
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
    pcb_params = None

    # pcb_params = PCB_OD_PARAMETERS.get(pcb_od_mm) 

    # find the closest predefined OD if custom value was entered
    if pcb_od_mm is not None:
        if pcb_od_mm not in PCB_OD_PARAMETERS:
            #Find closest standarad OD
            closest_od = min(PCB_OD_PARAMETERS.keys(), key=lambda x: abs(x - pcb_od_mm))
            pcb_params = PCB_OD_PARAMETERS[closest_od]

            # calculate difference percentage
            diff_pct = abs(closest_od - pcb_od_mm) / closest_od * 100

            if diff_pct > 20: # if more than 20% different
                results["status_messages"].append(f"warning: custom OD ({pcb_od_mm}mm) is {diff_pct:.0f}% different from nearest standard ({closest_od}mm)"
                                                  "results may be inaccurate")
            else:
                results["status_messages"].append(f"using parameters for closest standard OD: {closest_od}mm (your input: {pcb_od_mm}mm)")
        else:
            pcb_params = PCB_OD_PARAMETERS.get(pcb_od_mm)
    else:
        
        results["status_messages"].append("PCB Stator OD (Outer Diameter) was not provided. Dimensions, weight, power density, and cost cannot be fully calculated.")
    if pcb_params:
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


        # Trace radius OD = (Trace OD/2) - DEFAULT_TRACE_GAP_MM
        results["trace_radius_od_mm"] = (pcb_od_mm / 2) - DEFAULT_TRACE_GAP_MM
        results["trace_od_circumference_mm"] = 2 * math.pi * results["trace_radius_od_mm"]

        # Trace length radial = (Trace radius OD - Trace radius ID)
        results["trace_length_radial_mm"] = results["trace_radius_od_mm"] - results["trace_radius_id_mm"]

        # Calculate `total pcb`= num_pcb_in_series * layer_parallel
        results["total_pcb"] = results["num_pcb_in_series"] * results["layer_parallel"]


        # currentConductingRadial = trace Length radial - (traceWidth / 2)
        # Assuming traceWidth refers to trace_width_id_mm for this calculation

        # results["current_conducting_radial_mm"] = results["trace_length_radial_mm"] - (results["trace_width_id_mm"] / 2)
        # if results["current_conducting_radial_mm"] < 0: # positive
        #     results["current_conducting_radial_mm"] = 0
        #     results["status_messages"].append("Calculated current conducting radial length is negative")

        # Calculate `number of Lines`
        # Approximating spreadsheet functions CLEAN(CEILING(X), 6) as ceil then round to nearest multiple of 6

        # if (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM) > 0:
        #     temp_num_lines = results["id_circumference_mm"] / (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM)
        #     results["number_of_lines"] = math.ceil(temp_num_lines)
        #     results["number_of_lines"] = round(results["number_of_lines"] / 6) * 6 # nearest multiple of 6
        #     if results["number_of_lines"] == 0:
        #         results["number_of_lines"] = 6 # minimum value

        # if results["trace_width_id_mm"] > 0:
        #     results["current_conducting_radial_mm"] = ( results["trace_length_radial_mm"] - (results["trace_width_id_mm"] / 2) ) # currentConductingRadial = trace Length radial - (traceWidth / 2)
        #     if results["current_conducting_radial_mm"] < 0: # positive
        #         results["current_conducting_radial_mm"] = 0
        #         results["status_messages"].append("Calculated current conducting radial length is negative")
        # else:
        #     results["current_conducting_radial_mm"] = 0

       # Calculate `number of Lines`
        if results["trace_width_id_mm"] > 0:
            temp_num_lines = results["id_circumference_mm"] / (results["trace_width_id_mm"] + DEFAULT_TRACE_GAP_MM)
            temp_num_lines = math.ceil(temp_num_lines) # clean(CEILING(X), 6) equivalent
            results["number_of_lines"] = round(temp_num_lines / 6) * 6 # round to nearest multiple of 6
            if results["number_of_lines"] == 0: # minimum value
                results["number_of_lines"] = 6
        else:
            results["number_of_lines"] = 6 # default value if trace width is zero
            results["status_messages"].append("cannot determine number of lines due to zero trace width or gap. this affects several downstream calculations")

        # calculate trace width at OD
        if results["number_of_lines"] is not None and results["trace_od_circumference_mm"] is not None:
            results["trace_width_od_mm"] = (results["trace_od_circumference_mm"] / results["number_of_lines"]) - DEFAULT_TRACE_GAP_MM
            results["average_trace_width_mm"] = (results["trace_width_id_mm"] + results["trace_width_od_mm"]) / 2
        
        

        # corrected conductor length calculation
        if results["number_of_lines"] is not None:
            results["total_conductor_length_1pcb_m"] = (results["id_circumference_mm"] * results["number_of_lines"]) /1000
            results["on_conductor_length_m"] = (results["total_conductor_length_1pcb_m"] / 3) * 2
        else:
            results["total_conductor_length_1pcb_m"] = None
            results["on_conductor_length_m"] = None

        # conductor length(2 phase switch ON) = onConductorLength * number of pcb in series
        if results["on_conductor_length_m"] is not None and results["num_pcb_in_series"] is not None:
            results["conductor_length_2phase_m"] = results["on_conductor_length_m"] * results["num_pcb_in_series"]

        else:
            results["conductor_length_2phase_m"] = None

        # radius calculations
        if results["trace_length_radial_mm"] is not None and results["trace_radius_id_mm"] is not None:
            results["current_conducting_radial_mm"] = results["trace_length_radial_mm"] - (results["trace_width_id_mm"] / 2)

        if results["current_conducting_radial_mm"] < 0:
            results["current_conducting_radial_mm"] = 0
            results["status_messages"].append("Calculated current conducting radial length is negative")

        # radius OD = non magnet area + currentConductingRadial
        if results["non_magnet_area_mm"] is not None and results["current_conducting_radial_mm"] is not None:
            results["radius_od_mm"] = results["non_magnet_area_mm"] + results["current_conducting_radial_mm"]
            results["avg_torque_radius_mm"] = (results["non_magnet_area_mm"] + results["radius_od_mm"]) / 2 # avg torque radius = (non magnet area + radius OD) / 2
        else:
            results["radius_od_mm"] = None
            results["avg_torque_radius_mm"] = None

        # # avg torque radius = (non magnet area + radius OD) / 2
        # if results["non_magnet_area_mm"] is not None and results["radius_od_mm"] is not None:
        #     results["avg_torque_radius_mm"] = (results["non_magnet_area_mm"] + results["radius_od_mm"]) / 2

        # else:
        #     results["avg_torque_radius_mm"] = None

        # stack up height
        # if results["num_pcb_in_series"] is not None and results["layer_parallel"] is not None:
        #     results["stack_up_height_mm"] = (results["num_pcb_in_series"] * results["layer_parallel"] * DEFAULT_PCB_THICKNESS_MM) + \
        #                                      ((results["num_pcb_in_series"] * results["layer_parallel"] * DEFAULT_PM_ROTOR_THICKNESS_MM) + DEFAULT_PM_ROTOR_THICKNESS_MM) + \
        #                                      (DEFAULT_AIR_GAP_MM * results["num_pcb_in_series"] * results["layer_parallel"])
        

        if results["num_pcb_in_series"] is not None and results["layer_parallel"] is not None:
            num_pcb = results["num_pcb_in_series"] * results["layer_parallel"]
            results["stack_up_height_mm"] = (num_pcb * DEFAULT_PCB_THICKNESS_MM) + \
                                             ((num_pcb + 1) * DEFAULT_PM_ROTOR_THICKNESS_MM) + \
                                             (num_pcb * DEFAULT_AIR_GAP_MM)

        else:
            results["stack_up_height_mm"] = None

    # Overall Size 
    if results["stack_up_height_mm"] is not None and pcb_od_mm is not None:
        results["size_mm"] = pcb_od_mm + results["stack_up_height_mm"] + 5 # +5mm for covering
        # size_mm = pcb_od_mm + stack_up_height_mm + 5

    
    # if results["voltage_v"] <= 0:
    #         results["status_messages"].append("Voltage must be greater than 0.")
    
    # if results["current_a"] <= 0:
    #     results["status_messages"].append("Current must be greater than 0.")
    

    # Iterative calculation loop for primary outputs 
    # This loop attempts to calculate values multiple times as new dependencies might become available
    # Power → Voltage → Current → Force... not possible to calculate in one loop

    max_iterations = 5 # A fixed number of iterations
    for _ in range(max_iterations):


        something_calculated_in_this_pass = False



        '''       

        # calculate Efficiency
        # Efficiency = (power out / power in) * 100
        # Efficiency can be calculated in two ways:
        # 1. Using Power Out and Power In
        # 2. Using Voltage and Current (with losses considered)
        # 3. Using Force and Conductor Length (with losses considered)
        # 4. Using RPM and KV Rating (if available)
        # Efficiency without losses:

        
        # if results["efficiency_percent"] is None:
        #     if results["power_out_kw"] is not None and results["power_in_kw"] is not None and results["power_in_kw"] > 0:
        #         results["efficiency_percent"] = (results["power_out_kw"] / results["power_in_kw"]) * 100 # efficiency = (powerOut / powerIn) * 100
        #         something_calculated_in_this_pass = True

        # elif results["efficiency_percent"] > 100:
        #     results["status_messages"].append("Warning: Efficiency exceeds 100% -> likely incorrect input.")
        #     something_calculated_in_this_pass = True

        # elif results["efficiency_percent"] <= 0:
        #     results["status_messages"].append("Warning: Efficiency is 0 or negative -> likely incorrect input.")
        #     something_calculated_in_this_pass = True

        


        # # Efficiency with losses:
        # if results["efficiency_percent"] is None:
        #     if results["voltage_v"] is not None and results["current_a"] is not None:
        #         Pin = results["voltage_v"] * results["current_a"]

        #         # --- NEW: Estimated resistance and no-load current ---
        #         # Add these keys to user inputs or use default values
        #         Rw =  0.2  # ohms (default guess)
        #         I0 =  0.3       # A (default no-load current)

        #         Pc = (results["current_a"] ** 2) * Rw
        #         Pfl = results["voltage_v"] * I0

        #         eff = (Pin - Pc - Pfl) / Pin if Pin > 0 else None

        #         if eff is not None:
        #             results["efficiency_percent"] = eff * 100
        #             something_calculated_in_this_pass = True

        #     elif results["power_out_kw"] is not None and results["power_in_kw"] is not None and results["power_in_kw"] > 0:
        #         results["efficiency_percent"] = (results["power_out_kw"] / results["power_in_kw"]) * 100
        #         something_calculated_in_this_pass = True

        # elif results["efficiency_percent"] > 100:
        #     results["status_messages"].append("Warning: Efficiency exceeds 100% -> likely incorrect input.")
        #     something_calculated_in_this_pass = True

        # elif results["efficiency_percent"] <= 0:
        #     results["status_messages"].append("Warning: Efficiency is 0 or negative -> likely incorrect input.")
        #     something_calculated_in_this_pass = True
        



        # if results["force_n"] is not None and results["conductor_length_2phase_m"] is not None and DEFAULT_MAGNET_STRENGTH_T is not None:
        #     I = results["force_n"] / (results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T) # current = force / (conductor Length * magnet Strength)
        #     V = results.get("voltage_v", )
        #     if V is not None and V > 0:
        #         Pin = I * V 
        #         Rw = 0.2  # ohms (default guess)
        #         I0 = 0.3  # A (default no-load current)

        #         Pcu = I**2 * Rw
        #         Pcore = V * I0
        #         if Pin > 0:
        #             efficiency = (Pin - Pcu - Pcore) / Pin
        #             results["efficiency_percent"] = efficiency * 100
        #             something_calculated_in_this_pass = True
        '''





        # In your calculate_results() function, replace the existing efficiency code with:

        # Calculate efficiency using best available method
        if not something_calculated_in_this_pass:
            if calculate_efficiency(results):
                something_calculated_in_this_pass = True

        # Add efficiency validation
        if results.get("efficiency_percent") is not None:
            eff = results["efficiency_percent"]
            if eff > 100:
                results.setdefault("status_messages", []).append("Warning: Efficiency exceeds 100% -> check input values")
            elif eff <= 0:
                results.setdefault("status_messages", []).append("Warning: Efficiency is 0 or negative -> check input values")

                something_calculated_in_this_pass = True



        # voltage from cells in series
        if results["voltage_v"] is None and results.get("num_cell_series") is not None:
            results["voltage_v"] = results["num_cell_series"] * DEFAULT_CELL_UNIT_CHARGE_V
            something_calculated_in_this_pass = True



        # Calculate Power Out from Torque and RPM
        if results["power_out_kw"] is None:
            if results["torque_nm"] is not None and results["rpm"] is not None:
                omega = 2 * math.pi * results["rpm"] / 60  # rad/s
                results["power_out_kw"] = (results["torque_nm"] * omega) / 1000
                something_calculated_in_this_pass = True

        # Calculate RPM from Power Out and Torque
        if results["rpm"] is None:
            if results["power_out_kw"] is not None and results["torque_nm"] is not None and results["torque_nm"] != 0:
                results["rpm"] = (results["power_out_kw"] * 1000 * 60) / ( results["torque_nm"] * (2 * math.pi) )  # RPM = (powerOut * 1000 * 60) / (torque * 2 * pi)
                something_calculated_in_this_pass = True

        # Calculate Voltage from Power In and Current
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
                results["conductor_length_2phase_m"] > 0:

                results["current_a"] = results["force_n"] / (results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T) # current = force / (conductor Length * magnet Strength)
                something_calculated_in_this_pass = True



        # Calculate Voltage (V)

        # if results["voltage_v"] is None:
        #     if inputs.get("num_cell_series") is not None:
        #         results["voltage_v"] = inputs["num_cell_series"] * DEFAULT_CELL_UNIT_CHARGE_V
        #         something_calculated_in_this_pass = True



        # if results["voltage_v"] is None:
        #     if results["power_in_kw"] is not None and results["current_a"] is not None and results["current_a"] > 0:
        #         results["voltage_v"] = (results["power_in_kw"] * 1000) / results["current_a"] # voltage = (powerIn * 1000) / current
        #         something_calculated_in_this_pass = True

        #     elif results["rpm"] is not None and results.get("kv_rating") is not None and results["kv_rating"] > 0:
        #         results["voltage_v"] = results["rpm"] / results["kv_rating"] # voltage = rpm / KV rating
        #         something_calculated_in_this_pass = True

        #     elif results["num_cell_series"] is not None:
        #         results["voltage_v"] = results["num_cell_series"] * DEFAULT_CELL_UNIT_CHARGE_V
        #         something_calculated_in_this_pass = True


                

        # ----------------------- Mechanical Output Calculations -----------------------


        # Calculate Force (N)
        if results["force_n"] is None:
            if results["current_a"] is not None and results["conductor_length_2phase_m"] is not None and DEFAULT_MAGNET_STRENGTH_T is not None:

                results["force_n"] = results["current_a"] * results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T  # force = current * conductor Length * magnet Strength 
                
                something_calculated_in_this_pass = True

            elif (results["torque_nm"] is not None and results["avg_torque_radius_mm"] is not None and results["avg_torque_radius_mm"] > 0):
                results["force_n"] = results["torque_nm"] / (results["avg_torque_radius_mm"] / 1000) # force = torque / (avg torque radius / 1000)
                something_calculated_in_this_pass = True
            
            # If kv_rating in RPM/V is known:
            elif results.get("kv_rating") is not None and results["voltage_v"] is not None and results["voltage_v"] > 0:
                kV_rpm_per_V = results["kv_rating"]
                kT_Nm_per_A = 60 / (2*math.pi * kV_rpm_per_V)  # approximate relation in SI
                if results["current_a"] is not None:
                    results["force_n"] = kT_Nm_per_A * results["current_a"] / (results["avg_torque_radius_mm"] / 1000) # force = (kT * I) / (avg torque radius / 1000)
                    something_calculated_in_this_pass = True

        

        # Calculate Torque (Nm)
        if results["torque_nm"] is None:
            if results["avg_torque_radius_mm"] is not None and results["force_n"] is not None:
                results["torque_nm"] = (results["avg_torque_radius_mm"] / 1000) * results["force_n"] # torque = (avg torque radius / 1000) * force 
                something_calculated_in_this_pass = True

            elif results["power_out_kw"] is not None and results["rpm"] is not None and results["rpm"] > 0:
                # omega = 2 * math.pi * results["rpm"] / 60
                # if omega > 0:
                # results["torque_nm"] = (results["power_out_kw"] * 1000) / omega
                results["torque_nm"] = (results["power_out_kw"] * 1000 * 60) / (results["rpm"] * 2 * math.pi) # torque = (powerOut * 1000 * 60) / (rpm * 2 * Math.PI)
                something_calculated_in_this_pass = True

        # Calculate Power Out (kW)
        if results["power_out_kw"] is None:
            if results["efficiency_percent"] is not None and results["power_in_kw"] is not None:
                results["power_out_kw"] = (results["efficiency_percent"] / 100) * results["power_in_kw"] # powerOut = (efficiency / 100) * powerIn
                something_calculated_in_this_pass = True

            elif results["rpm"] is not None and results["torque_nm"] is not None:
                results["power_out_kw"] = (results["rpm"] * results["torque_nm"] * 2 * math.pi) / (1000 * 60) # powerOut = (rpm * torque * 2 * Math.PI) / (1000 * 60)

                something_calculated_in_this_pass = True

        # Calculate RPM
        if results["rpm"] is None:
            if results["power_out_kw"] is not None and results["torque_nm"] is not None and (results["torque_nm"] * 2 * math.pi) != 0:
                results["rpm"] = (results["power_out_kw"] * 1000 * 60) / (results["torque_nm"] * 2 * math.pi) # rpm = (powerOut * 1000) * 60) / (torque * 2 * Math.PI)
                something_calculated_in_this_pass = True

            elif results.get("kv_rating") is not None and results["voltage_v"] is not None:
                results["rpm"] = results["kv_rating"] * results["voltage_v"] # rpm = KV rating * voltage

                something_calculated_in_this_pass = True



        # -------------------- Additional Metrics Calculations --------------------


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
                estimated_num_magnets = results["number_of_lines"] + 2 # statorCoil + 2 (as per the formula: magnetPoles = statorCoil + 2
                if estimated_num_magnets <= 0:
                    estimated_num_magnets = 1 # non-zero

            if estimated_num_magnets is not None:
                results["cost_inr"] = (results["total_pcb"] * pcb_params["cost_factor_pcb"]) + \
                                      (estimated_num_magnets * pcb_params["cost_factor_magnets"]) + \
                                      pcb_params["miscellaneous_cost"] # cost = (total pcb * cost factor) + (no of magnets * cost factor magnets) + miscellaneous cost
                something_calculated_in_this_pass = True

            else:
                results["status_messages"].append("Cost estimation requires 'number of lines' (to infer number of magnets), which could not be determined.")


     
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



# ----------------------- Formatting Functions -----------------------
def fmt(value):
    """Formats a value for clean output display"""
    if value is None:
        return "N/A"
    if isinstance(value, int):
        return str(value)
    try:
        fvalue = float(value)
    except (TypeError, ValueError):
        return str(value)

    # Handle near-zero values
    if abs(fvalue) < 1e-10:
        return "0"

    # Handle near-integer values
    if abs(fvalue - round(fvalue)) < 1e-6:
        return str(int(round(fvalue)))

    # Format with up to 4 decimals, then trim trailing zeros
    s = f"{fvalue:.4f}".rstrip('0').rstrip('.')
    
    # Add leading zero for small decimals
    if s.startswith('.'):
        s = '0' + s
    elif s.startswith('-.'):
        s = '-0' + s[2:]
    
    return s # fmt


# --------------------Step 3: Display the results to the user--------------------
# ----------------------- Display Results Function -----------------------

def display_results(results):
    """
    Displays the calculated results with smart formatting.
    Only shows values that were successfully calculated.
    """
    print("\n--- AirBuddy Aerospace PCB Calculator Results ---")

    # Helper to safely format and print a value
    def print_result(label, key):
        formatted = fmt(results.get(key))
        print(f" {label}: {formatted}")

    # --------------------------
    # Mechanical Output Section
    # --------------------------
    print("\nMechanical Output:")
    print_result("Power Out (kW)", "power_out_kw")
    print_result("Torque (Nm)", "torque_nm")
    print_result("RPM", "rpm")
    print_result("Force (N)", "force_n")

    # --------------------------
    # Electrical Input Section
    # --------------------------
    print("\nElectrical Input:")
    print_result("Current (A)", "current_a")
    print_result("Voltage (V)", "voltage_v")
    print_result("Power In (kW)", "power_in_kw")
    print_result("Cells in Series", "num_cell_series")

    # --------------------------
    # Efficiency & Dimensions
    # --------------------------
    print("\nEfficiency & Dimensions:")
    print_result("Efficiency (%)", "efficiency_percent")
    print_result("PCB Stator OD (mm)", "pcb_stator_od_mm")

    # --------------------------
    # Calculated Dimensions
    # --------------------------
    print("\nCalculated Dimensions:")
    print_result("Overall Size (mm)", "size_mm")

    # --------------------------
    # Additional Metrics
    # --------------------------
    print("\nAdditional Metrics:")
    print_result("Weight (g)", "weight_g")
    print_result("Power Density (kW/kg)", "power_density_kw_kg")
    print_result("kV Rating", "kv_rating")
    print_result("Estimated Cost (₹)", "cost_inr")

    # --------------------------
    # Status Messages
    # --------------------------
    if results["status_messages"]:
        print("\n--- Important Notes / Warnings ---")
        for msg in results["status_messages"]:
            print(f"- {msg}")

    # --------------------------
    # Final Note
    # --------------------------
    print("\nNote: The 'number of magnets' used in cost calculation is estimated as number_of_lines + 2")
    print("      This aligns with the formula: magnetPoles = statorCoil + 2")



# ----------------------- Main Execution Block -----------------------


# This block runs when you execute the Python script
if __name__ == "__main__":
    print("Welcome to the AirBuddy Aerospace PCB Calculator!")

    # Step 1: Collect inputs from the user
    user_inputs = collect_inputs()

    # Step 2: Perform calculations based on the collected inputs
    calculated_results = calculate_results(user_inputs)

    # Step 3: Display the results to the user
    display_results(calculated_results)
