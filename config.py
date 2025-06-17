import math 

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
        "num_pcb_in_series": 7,
        "layer_parallel": 6,
        "cost_factor_pcb": 130,
        "cost_factor_magnets": 130,
        "miscellaneous_cost": 1000,
        "weight_factor": (8 + 10) # weight calculation
    },
    150: {
        "pcb_stator_id_mm": 100,
        "trace_width_id_mm": 5.3,
        "num_pcb_in_series": 5,
        "layer_parallel": 10,
        "cost_factor_pcb": 200,
        "cost_factor_magnets": 200,
        "miscellaneous_cost": 1500,
        "weight_factor": (11 + 12) # weight calculation
    }
}
