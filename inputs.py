from config import PCB_OD_PARAMETERS



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
        user_input = input(f"{prompt} (Options: {options_str}): ").strip()
        if user_input == "":
            return None # empty input
        try:
            od = int(user_input)
            if od in options:
                return od
            else:
                print(f"Invalid option. Please choose from {options_str}.")
        except ValueError:
            print("Invalid input. Please enter a number from the options or leave it blank.")


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
    # inputs["power_in_kw"] = get_input_float("Enter Power (kW): ")

    # Efficiency & Dimensions Inputs
    inputs["efficiency_percent"] = get_Efficiency_percent_input("Enter Efficiency (%): ")
    inputs["pcb_stator_od_mm"] = get_pcb_stator_od_input("Select PCB Stator OD (mm)", list(PCB_OD_PARAMETERS.keys()))

    return inputs 
