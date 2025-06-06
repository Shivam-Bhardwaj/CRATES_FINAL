"""
LEGACY SUPPORT: This file now uses the new modular architecture while maintaining 
the original interface for backward compatibility.

The logic has been refactored into separate modules:
- skid_logic.py: Skid calculations
- floorboard_logic.py: Floorboard layout and gap calculations  
- panel_logic.py: Panel sizing and bounding box calculations
- nx_generator.py: NX expressions file generation
- ui_module.py: User interface components
- main_orchestrator.py: Coordinates all logic modules
"""
import datetime
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import the new modular components
from main_orchestrator import generate_crate_expressions

# --- Default Constants (maintained for compatibility) ---
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = { 
    "2x6 (5.5 in)": 5.5, "2x8 (7.25 in)": 7.25,
    "2x10 (9.25 in)": 9.25, "2x12 (11.25 in)": 11.25
}
DEFAULT_MIN_CUSTOM_LUMBER_WIDTH = 2.5
DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP = 0.25
MIN_FORCEABLE_CUSTOM_BOARD_WIDTH = 0.25 
MAX_NX_FLOORBOARD_INSTANCES = 20

def generate_crate_expressions_logic(
    # Skid Inputs
    product_weight_lbs: float, product_length_in: float, product_width_in: float,
    clearance_each_side_in: float, allow_3x4_skids_bool: bool,
    # General Crate & Panel Inputs
    panel_thickness_in: float, cleat_thickness_in: float,
    product_actual_height_in: float, 
    clearance_above_product_in: float,
    ground_clearance_in: float,
    # Floorboard Inputs
    floorboard_actual_thickness_in: float, selected_std_lumber_widths: list[float], 
    max_allowable_middle_gap_in: float, min_custom_lumber_width_in: float,
    force_small_custom_board_bool: bool, 
    # Output
    output_filename: str
) -> tuple[bool, str]:
    """
    LEGACY WRAPPER: Maintains original interface while using new modular architecture.
    
    This function now serves as a compatibility wrapper around the new modular system.
    The actual logic is now distributed across separate modules for better maintainability.
    """
    try:
        # Package inputs for the new modular system
        inputs = {
            'product_weight_lbs': product_weight_lbs,
            'product_length_in': product_length_in,
            'product_width_in': product_width_in,
            'clearance_each_side_in': clearance_each_side_in,
            'allow_3x4_skids_bool': allow_3x4_skids_bool,
            'panel_thickness_in': panel_thickness_in,
            'cleat_thickness_in': cleat_thickness_in,
            'product_actual_height_in': product_actual_height_in,
            'clearance_above_product_in': clearance_above_product_in,
            'ground_clearance_in': ground_clearance_in,
            'floorboard_actual_thickness_in': floorboard_actual_thickness_in,
            'selected_std_lumber_widths': selected_std_lumber_widths,
            'max_allowable_middle_gap_in': max_allowable_middle_gap_in,
            'min_custom_lumber_width_in': min_custom_lumber_width_in,
            'force_small_custom_board_bool': force_small_custom_board_bool
        }
        
        # Use the new modular orchestrator
        return generate_crate_expressions(inputs, output_filename)
        
    except Exception as e:
        import traceback
        print(f"Error in legacy wrapper: {e}\n{traceback.format_exc()}")
        return False, f"Error: {e}"

class CrateApp: 
    """
    LEGACY UI CLASS: Maintained for backward compatibility.
    
    For new development, use the modular UI in ui_module.py.
    This class now provides a thin wrapper around the new modular system.
    """
    def __init__(self, master):
        # Import and use the new modular UI
        from ui_module import CrateGeneratorUI
        from main_orchestrator import generate_crate_expressions
        
        def generation_callback(inputs, output_filename):
            return generate_crate_expressions(inputs, output_filename)
        
        # Create the new UI instance
        self.ui = CrateGeneratorUI(master, generation_callback)
        
        # Update window title to indicate legacy mode
        master.title("NX Crate Exporter (Legacy Interface - Uses Modular Backend)")

if __name__ == "__main__":
    root = tk.Tk()
    app = CrateApp(root)
    root.mainloop()
