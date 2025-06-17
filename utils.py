

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
