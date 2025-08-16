def external(current, rise):
    k = 0.048
    b = 0.44
    c = 0.725
    return (current / (k * (rise ** b))) ** (1 / c)

def internal(current, rise):
    k = 0.024
    b = 0.44
    c = 0.725
    return (current / (k * (rise ** b))) ** (1 / c)

def mil_to_mm(mil):
    return mil * 0.0254

def mil_to_um(mil):
    return mil * 25.4

def calc_trace_width(
    Current, Thickness, Rise, Ambient, Trace,
    ThicknessUnit, RiseUnit, AmbientUnit, TraceUnit,
    InternalWidthUnit="mil", ExternalWidthUnit="mil"
):
    # Convert Thickness to cm
    if ThicknessUnit == "oz/ft²":
        Thickness *= 0.0035  # oz to mm, then to cm
    elif ThicknessUnit == "mil":
        Thickness *= 2.54e-3  # mil to cm
    elif ThicknessUnit == "mm":
        Thickness *= 0.1  # mm to cm
    elif ThicknessUnit == "µm":
        Thickness *= 1e-4  # µm to cm

    # Convert Temperature Rise to °C
    if RiseUnit == "°F":
        Rise = (Rise * 5) / 9

    # Convert Ambient Temperature to °C
    if AmbientUnit == "°F":
        Ambient = (Ambient - 32) * 5 / 9

    # Convert Trace Length to cm
    if TraceUnit == "in":
        Trace /= 0.393701
    elif TraceUnit == "ft":
        Trace /= 0.032808
    elif TraceUnit == "mil":
        Trace /= 393.7008
    elif TraceUnit == "mm":
        Trace /= 10
    elif TraceUnit == "µm":
        Trace /= 10000
    elif TraceUnit == "m":
        Trace /= 0.01
    elif TraceUnit == "cm":
        pass  # already in cm

    # Internal Layer Calculation
    Ai = internal(Current, Rise)
    Ai = Ai * 2.54 * 2.54 / 1e6  # Convert mil² to m²
    InternalWidth = Ai / Thickness  # in m

    InternalWidth_mil = InternalWidth / 2.54e-3
    InternalWidth_mm = mil_to_mm(InternalWidth_mil)
    InternalWidth_um = mil_to_um(InternalWidth_mil)

    # Resistance Calculation (using copper resistivity 1.7e-6 ohm-cm)
    InternalResistance = ((1.7e-6) * Trace / Ai) * (1 + 3.9e-3 * ((Ambient + Rise) - 25))
    InternalVoltage = InternalResistance * Current
    InternalPower = Current * Current * InternalResistance

    # External Layer Calculation
    Ae = external(Current, Rise)
    Ae = Ae * 2.54 * 2.54 / 1e6  # Convert mil² to m²
    ExternalWidth = Ae / Thickness  # in m

    ExternalWidth_mil = ExternalWidth / 2.54e-3
    ExternalWidth_mm = mil_to_mm(ExternalWidth_mil)
    ExternalWidth_um = mil_to_um(ExternalWidth_mil)

    ExternalResistance = ((1.7e-6) * Trace / Ae) * (1 + 3.9e-3 * ((Ambient + Rise) - 25))
    ExternalVoltage = ExternalResistance * Current
    ExternalPower = Current * Current * ExternalResistance

    return {
        "InternalWidth": InternalWidth,
        "InternalWidth_mil": InternalWidth_mil,
        "InternalWidth_mm": InternalWidth_mm,
        "InternalWidth_um": InternalWidth_um,
        "ExternalWidth": ExternalWidth,
        "ExternalWidth_mil": ExternalWidth_mil,
        "ExternalWidth_mm": ExternalWidth_mm,
        "ExternalWidth_um": ExternalWidth_um,
        "InternalResistance": InternalResistance,
        "ExternalResistance": ExternalResistance,
        "InternalVoltage": InternalVoltage,
        "ExternalVoltage": ExternalVoltage,
        "InternalPower": InternalPower,
        "ExternalPower": ExternalPower,
    }

# === Main Execution ===

if __name__ == "__main__":
    # Get User Inputs
    current = float(input("Enter Current (A): "))

    ambient_value = float(input("Enter Ambient Temperature value: "))
    print("Enter Ambient Temperature unit:")
    print("1. °C")
    print("2. °F")
    ambient_unit_choice = int(input())
    ambient_unit = "°C" if ambient_unit_choice == 1 else "°F"

    thickness_value = float(input("Enter Thickness value: "))
    print("Enter Thickness unit:")
    print("1. oz/ft² (oz)")
    print("2. mil")
    print("3. mm")
    print("4. µm")
    thickness_unit_choice = int(input())
    thickness_unit_map = {
        1: "oz/ft²",
        2: "mil",
        3: "mm",
        4: "µm"
    }
    thickness_unit = thickness_unit_map[thickness_unit_choice]

    trace_value = float(input("Enter Trace Length value: "))
    print("Enter Trace Length unit:")
    trace_unit_options = ["in", "ft", "mil", "mm", "µm", "cm", "m"]
    for i, unit in enumerate(trace_unit_options, 1):
        print(f"{i}. {unit}")
    trace_unit_choice = int(input())
    trace_unit = trace_unit_options[trace_unit_choice - 1]

    rise_value = float(input("Enter Temperature Rise value: "))
    print("Enter Temperature Rise unit:")
    print("1. °C")
    print("2. °F")
    rise_unit_choice = int(input())
    rise_unit = "°C" if rise_unit_choice == 1 else "°F"

    # Calculate and Output Results
    result = calc_trace_width(
        current, thickness_value, rise_value, ambient_value, trace_value,
        thickness_unit, rise_unit, ambient_unit, trace_unit
    )

    print("\n*Internal Layers:")
    print(f"Required Trace Width:")
    print(f"{result['InternalWidth_mil']:.10f} mil / {result['InternalWidth_mm']:.10f} mm / {result['InternalWidth_um']:.10f} µm")
    print(f"Resistance Ω: {result['InternalResistance']:.10f}")
    print(f"Voltage Drop V: {result['InternalVoltage']:.10f}")
    print(f"Power Loss W: {result['InternalPower']:.10f}")

    print("\n*External Layers in Air:")
    print(f"Required Trace Width:")
    print(f"{result['ExternalWidth_mil']:.10f} mil / {result['ExternalWidth_mm']:.10f} mm / {result['ExternalWidth_um']:.10f} µm")
    print(f"Resistance Ω: {result['ExternalResistance']:.10f}")
    print(f"Voltage Drop V: {result['ExternalVoltage']:.10f}")
    print(f"Power Loss W: {result['ExternalPower']:.10f}")
    