import math

# Constants - Updated with correct IPC-2221 factors
MIL_PER_OZ = 1.378 # 1 oz/ft² = 1.378 mil (standard for copper)
RESISTIVITY_25C = 1.724e-8  # Copper resistivity at 25°C (Ω·m)
TEMP_COEFFICIENT = 0.00393  # Temperature coefficient for copper (per °C)

# Precomputed thickness conversion factors - Corrected
FACTOR_MIL = 1 / MIL_PER_OZ  # mil to oz/ft²
FACTOR_MM = 1000 / (25.4 * MIL_PER_OZ)  # mm to oz/ft²
FACTOR_UM = 1 / (25.4 * MIL_PER_OZ)  # µm to oz/ft²

# Correct IPC-2221 constants
IPC2221_CONSTANTS = {
    "internal": {"k": 0.024, "b": 0.44, "c": 0.725},
    "external": {"k": 0.048, "b": 0.44, "c": 0.725}
}

# Convert Fahrenheit to Celsius
def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9

# Convert thickness to oz/ft²
def convert_thickness_to_oz(value, unit):
    # Convert thickness to oz/ft² using correct IPC-2221 conversion factors
    if unit == 1:  # oz/ft²
        return value
    elif unit == 2:  # mil
        return value * FACTOR_MIL
    elif unit == 3:  # mm
        return value * FACTOR_MM
    elif unit == 4:  # µm
        return value * FACTOR_UM
    else:
        raise ValueError("Invalid thickness unit selected.")

# Convert length to meters
def convert_length_to_meters(value, unit):
    # Conversion factors to meters
    conversions = {
        1: 0.0254,      # in -> m
        2: 0.3048,      # ft -> m
        3: 0.0000254,   # mil -> m
        4: 0.001,       # mm -> m
        5: 0.000001,    # µm -> m
        6: 0.01,        # cm -> m
        7: 1.0          # m -> m
    }
    return value * conversions[unit]

# Convert mil to mm
def mil_to_mm(mil):
    return mil * 0.0254

# Convert mil to µm
def mil_to_um(mil):
    return mil * 25.4

# Convert mm to mil
def mm_to_mil(mm):
    return mm / 0.0254

# Convert µm to mil
def um_to_mil(um):
    return um / 25.4

# Convert mil to square mm
def mil2_to_mm2(mil2):
    return mil2 * (0.0254 ** 2)

# Calculate trace width
def calculate_trace_width(current, temp_rise, thickness_oz, layer_type):
    # Get correct IPC-2221 constants
    constants = IPC2221_CONSTANTS[layer_type]
    k = constants["k"]
    b = constants["b"]
    c = constants["c"]
    
    # Calculate cross-sectional area (mil²) - CORRECTED FORMULA
    # Area = [I / (k * ΔT^b)]^(1/c)
    area_mil2 = (current / (k * (temp_rise ** b))) ** (1 / c)
    
    # Convert thickness to mil
    thickness_mil = thickness_oz * MIL_PER_OZ
    
    # Calculate width in mil (W = A / t)
    width_mil = area_mil2 / thickness_mil
    
    return area_mil2, width_mil

# Calculate resistance
def calculate_resistance(length_m, width_mil, thickness_oz, operating_temp):
    # Adjust resistivity for operating temperature
    rho = RESISTIVITY_25C * (1 + TEMP_COEFFICIENT * (operating_temp - 25))
    
    # Convert dimensions to meters
    width_m = width_mil * 0.0000254  # mil to meters
    thickness_m = thickness_oz * MIL_PER_OZ * 0.0000254  # oz to mil to meters
    
    # Calculate cross-sectional area in m²
    area_m2 = width_m * thickness_m
    
    # Calculate resistance
    resistance = rho * length_m / area_m2
    
    return resistance

# Get user input
def get_user_input():
    print("=== PCB Trace Width Calculator ===\n")
    
    current = float(input("Enter Current (A): "))
    
    # Ambient temperature handling
    print("\nAmbient Temperature:")
    print("1. °C")
    print("2. °F")
    temp_unit = int(input("Select unit: "))
    ambient_temp = float(input("Enter Ambient Temperature: "))
    
    if temp_unit == 2:
        ambient_temp = fahrenheit_to_celsius(ambient_temp)
    elif temp_unit != 1:
        raise ValueError("Invalid unit selected for ambient temperature.")
    
    # Thickness input
    print("\nThickness:")
    print("1. oz/ft² (oz)")
    print("2. mil")
    print("3. mm")
    print("4. µm")
    thickness_unit = int(input("Select unit: "))
    thickness_value = float(input("Enter Thickness value: "))
    thickness_oz = convert_thickness_to_oz(thickness_value, thickness_unit)
    
    # Trace length input
    print("\nTrace Length:")
    print("1. in")
    print("2. ft")
    print("3. mil")
    print("4. mm")
    print("5. µm")
    print("6. cm")
    print("7. m")
    length_unit = int(input("Select unit: "))
    length_value = float(input("Enter Trace Length value: "))
    length_m = convert_length_to_meters(length_value, length_unit)
    
    # Temperature rise handling - CRITICAL FIX: Delta conversion
    print("\nTemperature Rise:")
    print("1. °C")
    print("2. °F")
    temp_rise_unit = int(input("Select unit: "))
    temp_rise = float(input("Enter Temperature Rise value: "))

    # Delta temperature conversion (F to C)
    if temp_rise_unit == 2:
        temp_rise = temp_rise * 5/9  # Δ°F to Δ°C conversion
    elif temp_rise_unit != 1:
        raise ValueError("Invalid unit selected for temperature rise.")
    
    return current, ambient_temp, thickness_oz, length_m, temp_rise

# Display results
def display_results(current, ambient_temp, thickness_oz, length_m, temp_rise):
    # Calculate operating temperature
    operating_temp = ambient_temp + temp_rise
    
    print("\n" + "="*60)
    print("CALCULATION RESULTS")
    print("="*60)
    print(f"Operating Temperature: {operating_temp:.10f} °C")
    
    for layer_type in ["internal", "external"]:
        print(f"\n{layer_type.upper()} LAYERS:")
        print("-" * 40)
        
        # Calculate trace width
        area_mil2, width_mil = calculate_trace_width( current, temp_rise, thickness_oz, layer_type)
        
        # Calculate resistance with operating temperature
        resistance = calculate_resistance(length_m, width_mil, thickness_oz, operating_temp)
        
        # Calculate derived values
        voltage_drop = current * resistance
        power_loss = current * voltage_drop
        
        # Display results
        print(f"Required Trace Width:")
        print(f"{width_mil:.10f} mil / {mil_to_mm(width_mil):.10f} mm / {mil_to_um(width_mil):.10f} µm")

        area_mm2 = mil2_to_mm2(area_mil2)
        print(f"\nCross-sectional Area: {area_mil2:.10f} mil² / {area_mm2:.10f} mm²")
        print(f"Resistance: {resistance:.10f} Ω")
        print(f"Voltage Drop: {voltage_drop:.10f} V")
        print(f"Power Loss: {power_loss:.10f} W")

# Main function
def main():
    try:
        # Get user input
        current, ambient_temp, thickness_oz, length_m, temp_rise = get_user_input()
        
        # Calculate and display results
        display_results(current, ambient_temp, thickness_oz, length_m, temp_rise)

       
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except KeyboardInterrupt:
        print("\nCalculation cancelled.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the program
if __name__ == "__main__":
    main()
