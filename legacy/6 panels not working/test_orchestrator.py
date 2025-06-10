import logging
from main_orchestrator import generate_crate_expressions

# --- Setup Logging (copied from main.py) ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('autocrate_app.log', mode='w')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# --- End Logging Setup ---

def run_test():
    logger.info("Starting test_orchestrator.py run...")

    sample_inputs = {
        'product_weight_lbs': 300.0,
        'product_length_in': 100.0,
        'product_width_in': 40.0,
        'clearance_each_side_in': 2.5,
        'allow_3x4_skids_bool': True,
        'panel_thickness_in': 0.25,
        'cleat_thickness_in': 0.75,
        'product_actual_height_in': 50.0,
        'clearance_above_product_in': 2.0,
        'ground_clearance_in': 1.0,
        'cleat_actual_width_in': 3.5,
        'floorboard_actual_thickness_in': 1.5,
        'selected_std_lumber_widths': [5.5, 7.25, 9.25, 11.25],
        'max_allowable_middle_gap_in': 0.25,
        'min_custom_lumber_width_in': 2.5,
        'force_small_custom_board_bool': True,
        'skid_material_nominal_width_in': 3.5, # Added based on previous errors
        'skid_material_nominal_thickness_in': 1.5, # Added
        'skid_spacing_in': 24.0, # Added
        'max_inter_cleat_spacing_in': 24.0, # Added
        'num_skids_override': None # Added (optional)
    }
    logger.debug(f"Using sample_inputs: {sample_inputs}")

    output_filename = "H:/Shared drives/DV Shared/_ Projects/_2025/AMAT/AutoCrate/Test_Crate_Output.exp"
    
    try:
        success, message = generate_crate_expressions(sample_inputs, output_filename)
        
        if success:
            logger.info(f"Test successful: {message}")
            print(f"Test successful: {message}")
        else:
            logger.error(f"Test failed: {message}")
            print(f"Test failed: {message}")
            
    except Exception as e:
        logger.critical(f"Unhandled exception during test run: {e}", exc_info=True)
        print(f"Unhandled exception during test run: {e}")

if __name__ == "__main__":
    run_test()
