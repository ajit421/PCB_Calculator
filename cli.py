from inputs import collect_inputs
# from calculations import calculate_results
from utils import fmt
from motor_calculator import calculate_results

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
