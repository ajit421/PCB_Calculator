import math

# for block magnet
def block_magnet(remanence_tesla, height_mm, length_mm, width_OD_mm, width_ID_mm ):

    average_width = (width_OD_mm + width_ID_mm) / 2
    #
    if average_width == 0 or length_mm == 0:
        return "Error: Division by zero in block_magnet calculation."

    sqrt_inner_term = length_mm**2 + average_width**2 + 4*height_mm**2
    numerator = 2* height_mm * math.sqrt(sqrt_inner_term)
    denominator = length_mm * average_width

    # Check for division by zero
    if denominator == 0:
        return "Error: Division by zero in block_magnet calculation."
    
    arctan_argument = numerator / denominator
    magnetic_field = (remanence_tesla / math.pi) * math.atan(arctan_argument) 
    return magnetic_field


# for ring magnet
def ring_magnet(remanence_tesla, hight_mm, OD_mm, ID_mm):
    # unit conversion
    hight_m = hight_mm / 1000  # convert mm to m
    OD_m = OD_mm / 1000        # convert mm to m
    ID_m = ID_mm / 1000        # convert mm to m

    r_outer_m = OD_m / 2
    r_inner_m = ID_m / 2
    
    if (r_outer_m **2 + hight_m**2) == 0 or (r_inner_m **2 + hight_m**2) == 0:
        return "Error: Division by zero in ring_magnet calculation."

    outer_term = hight_m / math.sqrt(r_outer_m**2 + hight_m**2)
    inner_term = hight_m / math.sqrt(r_inner_m**2 + hight_m**2)
    magnetic_field = (remanence_tesla / 2) * (outer_term - inner_term) 
    return magnetic_field




# for cylinder magnet

def cylinder_magnet(remanence_tesla, height_mm, diameter_mm):
    height_m = height_mm / 1000  # convert mm to m
    diameter_m = diameter_mm / 1000  # convert mm to m
    radius_m = diameter_m / 2

    if (radius_m **2 + height_m**2) == 0:
        return "Error: Division by zero in cylinder_magnet calculation."

    magnetic_field = (remanence_tesla / 2) * (height_m / math.sqrt(radius_m**2 + height_m**2))
    return magnetic_field



########################
# user interface functions
########################


# check if input is a float
def get_float_input(input_text):
    #Continuously prompts the user for a valid float input.
    while True:
        try:
            return float(input(input_text))
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

# Run Block Magnet Calculator
def run_block_calculator():
    """Gets user input and runs the block magnet calculation."""
    print("\n--- Block Magnet Calculator ---")
    remanence_tesla = get_float_input("Enter Remanence (Br) in Tesla: ")
    height_mm = get_float_input("Enter Height (H) in mm: ")
    length_mm = get_float_input("Enter Length (L) in mm: ")
    width_OD_mm = get_float_input("Enter First Width (W1_OD) in mm: ")
    width_ID_mm = get_float_input("Enter Second Width (W2_ID) in mm: ")

    result = block_magnet(remanence_tesla, height_mm, length_mm, width_OD_mm, width_ID_mm)
    print(f"Magnetic Field Strength: {result:.6f} T")

# Run Ring Magnet Calculator
def run_ring_calculator():
    # Gets user input and runs the ring magnet calculation.
    print("\n--- Ring Magnet Calculator ---")
    remanence_tesla = get_float_input("Enter Remanence (Br) in Tesla: ")
    height_mm = get_float_input("Enter Height (H) in mm: ")
    OD_mm = get_float_input("Enter Outer Diameter (OD) in mm: ")
    ID_mm = get_float_input("Enter Inner Diameter (ID) in mm: ")

    result = ring_magnet(remanence_tesla, height_mm, OD_mm, ID_mm)
    print(f"Magnetic Field Strength: {result:.6f} T")


# Run Cylinder Magnet Calculator
def run_cylinder_calculator():
    # Gets user input and runs the cylinder magnet calculation.
    print("\n--- Cylinder Magnet Calculator ---")
    remanence_tesla = get_float_input("Enter Remanence (Br) in Tesla: ")
    height_mm = get_float_input("Enter Height (H) in mm: ")
    diameter_mm = get_float_input("Enter Diameter (D) in mm: ")

    result = cylinder_magnet(remanence_tesla, height_mm, diameter_mm)
    print(f"Magnetic Field Strength: {result:.6f} T")


# Print Result Function
def print_result(result):
    # Prints the calculation result in a formatted way
    print("-" * 25)
    if isinstance(result, str):
        print(f"Error: {result}")
    else:
        print(f"Calculated Magnetic Field: {result:.6f} T")
    print("-" * 25)


# Main Function
def main():
    # Main function to run the interactive calculator
    while True:
        print("\n===== Magnet Calculator Menu =====")
        print("1. Calculate for Block Magnet")
        print("2. Calculate for Ring Magnet")
        print("3. Calculate for Cylinder Magnet")

        
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            run_block_calculator()
        elif choice == '2':
            run_ring_calculator()
        elif choice == '3':
            run_cylinder_calculator()
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")


if __name__ == "__main__":
    main()

# This code provides a command-line interface for calculating the magnetic field strength of different types of magnets.
# It includes functions for block, ring, and cylinder magnets, along with user input handling and error checking.
# The user can select the type of magnet and input the required parameters to get the magnetic field strength.
# The results are printed in a formatted way, and the program runs in a loop until the user decides to exit.
# The code is designed to be user-friendly and robust against invalid inputs.
