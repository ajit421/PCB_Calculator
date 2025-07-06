import math


# ------------------------- Constants and Configuration Data -------------------------

# Default physical constants
DEFAULT_AIR_GAP_MM = 0.1 # Air gap
DEFAULT_NUM_PHASE = 3 # Number of phases
DEFAULT_PCB_THICKNESS_MM = 1.6 # PCB thickness
DEFAULT_PM_ROTOR_THICKNESS_MM = 3.0 # PM rotor thickness
DEFAULT_PM_ROTOR_AXIAL_HIGHT_MM = 3.0 # PM rotor axial height
DEFAULT_ONE_PCB_OZ_FT2 = 40 # Copper weight per layer
DEFAULT_MAGNET_STRENGTH_T = 0.5 # Magnet Strength
DEFAULT_CELL_UNIT_CHARGE_V = 2 # Cell unit charge

DEFAULT_TRACE_GAP_MM = 0.5 # Trace gap (Constant across all ODs)
DEFAULT_TRACE_WIDTH_CURVED_LINE = 0.5 # Trace width for curved lines
DEFAULT_REMANENCE_TESLA = 1.47 # Remanence Tesla
DEFAULT_PARALLEL_STACKING_CONSTANT = 1.5 # Parallel stacking constant

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
        "pcb_stator_od_mm": 50,
        "weight_factor": (5 + 7) # weight calculation = 12
    },
    80: {
        "pcb_stator_id_mm": 40,
        "trace_width_id_mm": 2.5,
        "num_pcb_in_series": 9,
        "layer_parallel": 4,
        "cost_factor_pcb": 100,
        "cost_factor_magnets": 100,
        "miscellaneous_cost": 800,
        "pcb_stator_od_mm": 80,
        "weight_factor": ( 7 + 9 ) # weight calculation = 16
    },
    100: {
        "pcb_stator_id_mm": 49,
        "trace_width_id_mm": 4.9,
        "num_pcb_in_series": 7,
        "layer_parallel": 6,
        "cost_factor_pcb": 130,
        "cost_factor_magnets": 130,
        "miscellaneous_cost": 1000,
        "pcb_stator_od_mm": 100,
        "weight_factor": (8 + 10) # weight calculation = 18
    },
    150: {
        "pcb_stator_id_mm": 100,
        "trace_width_id_mm": 5.3,
        "num_pcb_in_series": 5,
        "layer_parallel": 10,
        "cost_factor_pcb": 200,
        "cost_factor_magnets": 200,
        "miscellaneous_cost": 1500,
        "pcb_stator_od_mm": 150,
        "weight_factor": (11 + 12) # weight calculation = 23
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
        parallel_resistance = total_resistance / results["layer_parallel"]  # num_pcb_in_series is used to scale resistance

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

    # new method
    # calculate efficiency = (( power_in_kw * 1000)- Total Losses)/ (power_in_kw * 1000)*100,2
    if results["power_in_kw"] is not None and results["total_losses_kw"] is not None:
        results["efficiency_percent"] = round(((results['power_in_kw'] * 1000) - results['total_losses_kw']) / (results['power_in_kw'] * 1000) * 100, 2)
        return True
        
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
        "power_in_kw": inputs.get("power_in_kw"),
        "efficiency_percent": inputs.get("efficiency_percent"),
        "pcb_stator_od_mm": inputs.get("pcb_stator_od_mm"),
        "num_cell_series" : inputs.get("num_cell_series"),
        
        "force_n": None,
        "size_mm": None,
        "weight_g": None,
        "power_density_kw_kg": None,
        "kv_rating": None,
        "cost_inr": None,
        "conductor_length_2phase_m": None,
        "total_pcb": None,  # Total PCB length in meters
        "num_coils_per_phase": None,  
        "pcb_stator_id_mm": None,  
        "trace_width_id_mm": None, 
        "number_of_lines": None,
        "num_lines_per_phase": None, 
        "num_lines_180": None,
        "coil_per_phase_180": None,
        "trace_length_radial_mm": None,
        "trace_radius_id_mm": None, 
        "trace_radius_od_mm": None, 
        "trace_od_circumference_mm": None,  
        "current_conducting_radial_mm": None,
        "trace_id_circumference_mm": None,  
        "trace_width_od_mm": None,
        "trace_thickness_id_mm": None,
        "id_circumference_mm": None,
        "non_magnet_area_mm": None,
        "trace_thickness_od_mm": None,
        "num_stator_coils": None,
        "magnet_poles": None,
        "average_trace_width_mm": None,
        "total_conductor_length_m": None,
        "on_conductor_length_m": None,
        "required_copper_thickness_mm": None,
        "radius_od_mm": None,
        "stack_up_height_mm": None,

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

        # STATOR ID CIRCUMFERENCE = PCB STATOR ID * DEFAULT_TRACE_GAP_MM * PI
        results["stator_id_circumference_mm"] = results["pcb_stator_id_mm"] * DEFAULT_TRACE_GAP_MM * math.pi

        # STATOR ID CIRCUMFERENCE = PCB STATOR ID * DEFAULT_TRACE_GAP_MM * PI
        results["stator_id_circumference_mm"] = results["pcb_stator_id_mm"] * DEFAULT_TRACE_GAP_MM * math.pi



        # number of lines = 

        if results["id_circumference_mm"] is not None and results["trace_width_id_mm"] is not None:

            # Step 1: Calculate division
            temp = results["id_circumference_mm"] / (results["trace_width_id_mm"] + DEFAULT_AIR_GAP_MM)

            # Step 2: CEILING to nearest multiple of 6
            significance = 6
            ceiling_result = significance * math.ceil(temp / significance)

            # Step 3: CLEAN - removes non-printable chars (mostly not needed for numbers in Python)
            results["number_of_lines"] = int(ceiling_result) # Mimics CLEAN behavior on strings


        # Trace ID circumference = number of lines * ( DEFAULT_TRACE_GAP_MM + trace_width_id_mm )
        if results["trace_width_id_mm"] is not None and results["pcb_stator_id_mm"] is not None:
            results["trace_id_circumference_mm"] = ((results["number_of_lines"]) * (DEFAULT_TRACE_GAP_MM + results["trace_width_id_mm"]))

        # Trace radius ID = ( Trace ID circumference / 2*pi )
        results["trace_radius_id_mm"] = results["trace_id_circumference_mm"] / (2 * math.pi)

        # radial gap id = ( trace radius ID - ( pcb stator id / 2 ) )
        results["radial_gap_id_mm"] = results["trace_radius_id_mm"] - ( results["pcb_stator_id_mm"] / 2)

        # radial gap OD = DEFAULT_TRACE_GAP_MM
        results["radial_gap_od_mm"] = DEFAULT_TRACE_GAP_MM

        # non magnet area = trace radius ID
        results["non_magnet_area_mm"] = results["trace_radius_id_mm"]

        
        # Trace radius OD = (pcb_stator_od_mm / 2 ) - DEFAULT_TRACE_GAP_MM
        results["trace_radius_od_mm"] = (results["pcb_stator_od_mm"] / 2 ) - DEFAULT_TRACE_GAP_MM

        # Trace OD circumference = trace radius OD * 2 * pi
        results["trace_od_circumference_mm"] = results["trace_radius_od_mm"] * 2 * math.pi
        
        # trace thickness OD = (trace OD circumference / number of lines ) - DEFAULT_TRACE_GAP_MM
        results["trace_thickness_od_mm"] = (results["trace_od_circumference_mm"] / results["number_of_lines"]) - DEFAULT_TRACE_GAP_MM

        # trace width OD = (trace OD circumference / number of lines ) - DEFAULT_TRACE_GAP_MM
        results["trace_width_od_mm"] = (results["trace_od_circumference_mm"] / results["number_of_lines"]) - DEFAULT_TRACE_GAP_MM

        # Trace length radial = (Trace radius OD - Trace radius ID)
        results["trace_length_radial_mm"] = results["trace_radius_od_mm"] - results["trace_radius_id_mm"]

        # number of line per phase = number_of_lines / DEFAULT_NUM_PHASE
        if results["number_of_lines"] is not None:
            results["num_lines_per_phase"] = results["number_of_lines"] / DEFAULT_NUM_PHASE

        # number of lines 180 = number of lines per phase / 2
        if results["num_lines_per_phase"] is not None:
            results["num_lines_180"] = results["num_lines_per_phase"] / 2        

        # coil per phase 180 = number of line per phase 180 - 1
        results["coil_per_phase_180"] = (results["num_lines_180"] - 1)

        # Coil per phase = Coil per phase 180 * 2
        results["num_coils_per_phase"] = results["coil_per_phase_180"] * 2

        # Number of stator coils = number of phases * per phase coils
        results["num_stator_coils"] = DEFAULT_NUM_PHASE * results["num_coils_per_phase"]

        # magnet poles = stator coils + 2
        results["magnet_poles"] = results["num_stator_coils"] + 2

        # Current conducting radial length = Trace length radial - (  DEFAULT_TRACE_WIDTH_CURVED_LINE / 2)
        if results["trace_length_radial_mm"] is not None:
            results["current_conducting_radial_mm"] = results["trace_length_radial_mm"] - (DEFAULT_TRACE_WIDTH_CURVED_LINE / 2)
        
        # corrected conductor length calculation
        if results["number_of_lines"] is not None:
            results["total_conductor_length_m"] = (results["current_conducting_radial_mm"] * results["number_of_lines"] ) /1000
        
        # on conductor length = total conductor length / 3
        if results["total_conductor_length_m"] is not None:
            results["on_conductor_length_m"] = (results["total_conductor_length_m"] / 3) * 2

        # 5. Set non-magnet area (must come after trace_radius_id_mm calculation)
        results["non_magnet_area_mm"] = results.get("trace_radius_id_mm", 0)
    
        # radius OD = non magnet area + currentConductingRadial
        if results["non_magnet_area_mm"] is not None and results["current_conducting_radial_mm"] is not None:
            results["radius_od_mm"] = results["non_magnet_area_mm"] + results["current_conducting_radial_mm"]

        # avg torque radius = (current conducting radial /2) + non magnet area
        results["avg_torque_radius_mm"] = (results["current_conducting_radial_mm"] / 2) + results["non_magnet_area_mm"]
        
        
        # conductor length(2 phase switch ON) = onConductorLength * number of pcb in series
        if results["on_conductor_length_m"] is not None and results["num_pcb_in_series"] is not None:
            results["conductor_length_2phase_m"] = results["on_conductor_length_m"] * results["num_pcb_in_series"]


        # All 3 phase = num_pcb_in_series * total_conductor_length_m
        results["total_pcb"] = results["num_pcb_in_series"] * results["total_conductor_length_m"]

        # height_mm = DEFAULT_PM_ROTOR_AXIAL_HIGHT_MM
        results["height_mm"] = DEFAULT_PM_ROTOR_AXIAL_HIGHT_MM

        # width_OD_mm = (trace_od_circumference_mm / magnet_poles) - (DEFAULT_TRACE_GAP_MM)
        results["width_OD_mm"] = (results["trace_od_circumference_mm"] / results["magnet_poles"]) - DEFAULT_TRACE_GAP_MM

        # width_ID_mm = (trace_id_circumference_mm / magnet_poles) - (DEFAULT_TRACE_GAP_MM)
        results["width_ID_mm"] = (results["trace_id_circumference_mm"] / results["magnet_poles"]) - DEFAULT_TRACE_GAP_MM

        # length_L_ID_to_OD_mm = trace_length_radial_mm
        results["length_L_ID_to_OD_mm"] = results["trace_length_radial_mm"]

        # surface_magnetic_value_tesla = (DEFAULT_REMANENCE_TESLA / math.pi) *  math.atan((2* height_mm * math.sqrt( (width_OD_mm ^2 + (( width_ID_mm + length_L_ID_to_OD_mm) / 2)^2+4* height_mm^2))/(width_OD_mm*((width_ID_mm + length_L_ID_to_OD_mm)/2)))* DEFAULT_PARALLEL_STACKING_CONSTANT
        results["surface_magnetic_value_tesla"] = (DEFAULT_REMANENCE_TESLA / math.pi) *  math.atan((2* results["height_mm"] * math.sqrt(results["width_OD_mm"] **2 + (( results["width_ID_mm"] + results["length_L_ID_to_OD_mm"]) / 2)**2+4* results["height_mm"]**2))/(results["width_OD_mm"]*((results["width_ID_mm"] + results["length_L_ID_to_OD_mm"])/2)))* DEFAULT_PARALLEL_STACKING_CONSTANT



        # Stack up height = ( number of pcb in series * layer in parallel connection * pcb board thickness) + ((( layer in parallel connection * number of pac in series  ) + 1 ) * pcb rotor thickness ) + (layer in parallel connection * number of pcb in series * DEFAULT_AIR_GAP_MM)
        if results["num_pcb_in_series"] is not None and results["layer_parallel"] is not None:
            results["stack_up_height_mm"] = (results["num_pcb_in_series"] * results["layer_parallel"] * DEFAULT_PCB_THICKNESS_MM) + \
                                            (((results["layer_parallel"] * results["num_pcb_in_series"]) + 1) * DEFAULT_PM_ROTOR_THICKNESS_MM) + \
                                            (results["layer_parallel"] * results["num_pcb_in_series"] * DEFAULT_AIR_GAP_MM)

        # Calculate the average trace width = (((trace width ID + trace width OD) / 2 * trace thickness OD) + (DEFAULT_TRACE_GAP_MM * DEFAULT_TRACE_GAP_MM )) / (trace length radial + DEFAULT_TRACE_GAP_MM )
        if results["trace_length_radial_mm"] > 0:
            results["average_trace_width_mm"] = (((results["trace_width_id_mm"] + results["trace_thickness_od_mm"]) / 2 * results["trace_length_radial_mm"]) + (DEFAULT_TRACE_GAP_MM * DEFAULT_TRACE_GAP_MM)) / (results["trace_length_radial_mm"] + DEFAULT_TRACE_GAP_MM)

        # Required Copper Thickness = DEFAULT_ONE_PCB_OZ_FT2 * layer_parallel
        if results["layer_parallel"] is not None:
            results["required_copper_thickness_mm"] = DEFAULT_ONE_PCB_OZ_FT2 * results["layer_parallel"]



        
        

    # Iterative calculation loop for primary outputs 
    # This loop attempts to calculate values multiple times as new dependencies might become available
    # Power → Voltage → Current → Force... not possible to calculate in one loop

    max_iterations = 7 # A fixed number of iterations
    for _ in range(max_iterations):


        something_calculated_in_this_pass = False





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


            # This block does not check if `total_losses_kw` is already set
        if (results.get("current_a") is not None and 
            results.get("voltage_v") is not None and 
            results.get("power_out_kw") is not None):
            
            Rw = calculate_winding_resistance(results)
            Pcu_kw = (results["current_a"] ** 2) * Rw / 1000
            Pcore_kw = results["voltage_v"] * 0.3 / 1000
            Pmech_kw = 0.03 * results["power_out_kw"]
            results["total_losses_kw"] = Pcu_kw + Pcore_kw + Pmech_kw
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

       


        # ----------------------- Electrical Input Calculations -----------------------

        # Calculate Voltage (V)
        if not results.get("voltage_v") and results.get("num_cell_series") is not None:
            # If voltage is not provided, calculate it from number of cells in series
            results["voltage_v"] = results["num_cell_series"] * DEFAULT_CELL_UNIT_CHARGE_V
            something_calculated_in_this_pass = True

        elif results["voltage_v"] is None:
            # If voltage is still not known, check if current and power are available
            if results["current_a"] is not None and results["power_in_kw"] is not None and results["current_a"] > 0:
                results["voltage_v"] = (results["power_in_kw"] * 1000) / results["current_a"] # voltage = (powerIn * 1000) / current
                something_calculated_in_this_pass = True

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
                
            elif results["force_n"] is not None and results["conductor_length_2phase_m"] is not None and DEFAULT_MAGNET_STRENGTH_T is not None and results["conductor_length_2phase_m"] > 0:

                results["current_a"] = results["force_n"] / (results["conductor_length_2phase_m"] * DEFAULT_MAGNET_STRENGTH_T) # current = force / (conductor Length * magnet Strength)
                something_calculated_in_this_pass = True



                

        # ----------------------- Mechanical Output Calculations -----------------------


        # Calculate Force (N)
        if results["force_n"] is None:
            if results["current_a"] is not None and results["conductor_length_2phase_m"] is not None and results["surface_magnetic_value_tesla"] is not None:

                results["force_n"] = results["current_a"] * results["conductor_length_2phase_m"] * results["surface_magnetic_value_tesla"]  # force = current * conductor Length * surface_magnetic_value_tesla 
                
                something_calculated_in_this_pass = True

           

        # Calculate Torque (Nm)
        if results["torque_nm"] is None:
            if results["avg_torque_radius_mm"] is not None and results["force_n"] is not None:
                results["torque_nm"] = (results["avg_torque_radius_mm"] / 1000) * results["force_n"] # torque = (avg torque radius / 1000) * force 
                something_calculated_in_this_pass = True

            elif results["power_out_kw"] is not None and results["rpm"] is not None and results["rpm"] > 0:
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
            # pcb diameter = pcb_stator_od_mm 
            results["pcb_diameter_mm"] = results["pcb_stator_od_mm"]
            something_calculated_in_this_pass = True

            # pcb height = stack_up_height_mm + 10
            results["pcb_height_mm"] = results["stack_up_height_mm"] + 10
            something_calculated_in_this_pass = True

        
        # Calculate Weight (g)
        if results["weight_g"] is None and results["total_pcb"] is not None and pcb_params is not None:
            results["weight_g"] = results["total_pcb"] * pcb_params["weight_factor"] # weight(gm) = (total pcb * (factor))
            something_calculated_in_this_pass = True

        # Calculate Power Density (kW/kg)
        if results["power_density_kw_kg"] is None:
            if results["power_out_kw"] is not None and results["weight_g"] is not None and results["weight_g"] > 0:

                results["power_density_kw_kg"] = results["power_out_kw"] / (results["weight_g"] / 1000) # power density = powerOut / (weight/1000)
                something_calculated_in_this_pass = True
                
            # # If Power Out and Power Density are given 
            # elif results["power_out_kw"] is not None and inputs.get("power_density_kw_kg") is not None and inputs["power_density_kw_kg"] > 0:
            #     if results["weight_g"] is None: # Only calculate if weight is not already known
            #         results["weight_g"] = (results["power_out_kw"] / inputs["power_density_kw_kg"]) * 1000 # weight = (powerOut / power density) * 1000

            #     results["power_density_kw_kg"] = inputs["power_density_kw_kg"] # Set power density from input as it was used to derive weight
            #     something_calculated_in_this_pass = True

        # Calculate kV Rating
        if results["kv_rating"] is None:
            if results["rpm"] is not None and results["voltage_v"] is not None and results["voltage_v"] > 0:
                results["kv_rating"] = results["rpm"] / results["voltage_v"] # KV rating = rpm / voltage 
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
                      "size_mm", "weight_g", "power_density_kw_kg", "kv_rating", "cost_inr", "efficiency_percent", "conductor_length_2phase_m",
                      "total_pcb", "num_cell_series", "pcb_stator_od_mm", "status_messages"]

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
    print_result("PCB Diameter (mm)", "pcb_diameter_mm")
    print_result("PCB Height (mm)", "pcb_height_mm")
    # print_result("Overall Size (mm)", "size_mm")

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
