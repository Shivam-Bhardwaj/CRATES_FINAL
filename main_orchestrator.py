"""
Main orchestrator module for the NX Crate Expression Generator.
Coordinates the skid, floorboard, panel logic modules and NX generator.
"""
from typing import Dict, Tuple, List

from skid_logic import calculate_skid_parameters
from floorboard_logic import calculate_floorboard_parameters
from panel_logic import calculate_panel_parameters
from nx_generator import generate_nx_expressions_file

# Constants
MIN_FORCEABLE_CUSTOM_BOARD_WIDTH = 0.25

def validate_inputs(inputs: Dict) -> Tuple[bool, str]:
    """
    Validate all user inputs before processing.
    
    Args:
        inputs: Dictionary of user inputs
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Extract inputs for validation
        product_weight_lbs = inputs['product_weight_lbs']
        product_length_in = inputs['product_length_in']
        product_width_in = inputs['product_width_in']
        clearance_each_side_in = inputs['clearance_each_side_in']
        panel_thickness_in = inputs['panel_thickness_in']
        cleat_thickness_in = inputs['cleat_thickness_in']
        product_actual_height_in = inputs['product_actual_height_in']
        clearance_above_product_in = inputs['clearance_above_product_in']
        ground_clearance_in = inputs['ground_clearance_in']
        floorboard_actual_thickness_in = inputs['floorboard_actual_thickness_in']
        selected_std_lumber_widths = inputs['selected_std_lumber_widths']
        max_allowable_middle_gap_in = inputs['max_allowable_middle_gap_in']
        min_custom_lumber_width_in = inputs['min_custom_lumber_width_in']
        force_small_custom_board_bool = inputs['force_small_custom_board_bool']
        
        # Validate inputs
        if product_weight_lbs < 0:
            return False, "Product weight must be non-negative."
        if product_length_in <= 0:
            return False, "Product length must be positive."
        if product_width_in <= 0:
            return False, "Product width must be positive."
        if clearance_each_side_in < 0:
            return False, "Clearance cannot be negative."
        if panel_thickness_in <= 0:
            return False, "Panel sheathing thickness must be positive."
        if cleat_thickness_in < 0:
            return False, "Cleat thickness cannot be negative (can be 0)."
        if product_actual_height_in <= 0:
            return False, "Product actual height must be positive."
        if clearance_above_product_in < 0:
            return False, "Clearance above product cannot be negative."
        if ground_clearance_in < 0:
            return False, "Ground clearance cannot be negative."
        if floorboard_actual_thickness_in <= 0:
            return False, "Floorboard thickness must be positive."
        if not selected_std_lumber_widths:
            return False, "No standard lumber selected for floorboards."
        if max_allowable_middle_gap_in < 0:
            return False, "Max middle gap cannot be negative."
        if min_custom_lumber_width_in <= 0:
            return False, "Min custom lumber width must be positive."
        if (min_custom_lumber_width_in < MIN_FORCEABLE_CUSTOM_BOARD_WIDTH and 
            force_small_custom_board_bool):
            return False, f"Min custom board width generally cannot be less than {MIN_FORCEABLE_CUSTOM_BOARD_WIDTH} inches."
        
        return True, ""
        
    except KeyError as e:
        return False, f"Missing required input: {e}"
    except Exception as e:
        return False, f"Input validation error: {e}"

def generate_crate_expressions(inputs: Dict, output_filename: str) -> Tuple[bool, str]:
    """
    Main orchestrator function that coordinates all calculation modules.
    
    Args:
        inputs: Dictionary containing all user inputs
        output_filename: Path where to save the NX expressions file
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Validate inputs
        is_valid, error_msg = validate_inputs(inputs)
        if not is_valid:
            return False, error_msg
        
        # Extract inputs
        product_weight_lbs = inputs['product_weight_lbs']
        product_length_in = inputs['product_length_in']
        product_width_in = inputs['product_width_in']
        clearance_each_side_in = inputs['clearance_each_side_in']
        allow_3x4_skids_bool = inputs['allow_3x4_skids_bool']
        panel_thickness_in = inputs['panel_thickness_in']
        cleat_thickness_in = inputs['cleat_thickness_in']
        product_actual_height_in = inputs['product_actual_height_in']
        clearance_above_product_in = inputs['clearance_above_product_in']
        ground_clearance_in = inputs['ground_clearance_in']
        floorboard_actual_thickness_in = inputs['floorboard_actual_thickness_in']
        selected_std_lumber_widths = inputs['selected_std_lumber_widths']
        max_allowable_middle_gap_in = inputs['max_allowable_middle_gap_in']
        min_custom_lumber_width_in = inputs['min_custom_lumber_width_in']
        force_small_custom_board_bool = inputs['force_small_custom_board_bool']
        
        # === STEP 1: Calculate Skid Parameters ===
        skid_params = calculate_skid_parameters(
            product_weight_lbs=product_weight_lbs,
            product_length_in=product_length_in,
            product_width_in=product_width_in,
            clearance_each_side_in=clearance_each_side_in,
            allow_3x4_skids_bool=allow_3x4_skids_bool
        )
        
        # Calculate overall crate dimensions (needed for other modules)
        crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in)
        crate_overall_length_od_in = skid_params.model_length_in
        
        # === STEP 2: Calculate Floorboard Parameters ===
        floorboard_params = calculate_floorboard_parameters(
            crate_overall_width_od_in=crate_overall_width_od_in,
            skid_model_length_in=skid_params.model_length_in,
            panel_thickness_in=panel_thickness_in,
            cleat_thickness_in=cleat_thickness_in,
            floorboard_actual_thickness_in=floorboard_actual_thickness_in,
            selected_std_lumber_widths=selected_std_lumber_widths,
            max_allowable_middle_gap_in=max_allowable_middle_gap_in,
            min_custom_lumber_width_in=min_custom_lumber_width_in,
            force_small_custom_board_bool=force_small_custom_board_bool,
            min_forceable_custom_board_width=MIN_FORCEABLE_CUSTOM_BOARD_WIDTH
        )
        
        # === STEP 3: Calculate Panel Parameters ===
        panel_params = calculate_panel_parameters(
            crate_overall_width_od_in=crate_overall_width_od_in,
            crate_overall_length_od_in=crate_overall_length_od_in,
            panel_thickness_in=panel_thickness_in,
            cleat_thickness_in=cleat_thickness_in,
            product_actual_height_in=product_actual_height_in,
            clearance_above_product_in=clearance_above_product_in,
            floorboard_actual_thickness_in=floorboard_actual_thickness_in,
            skid_actual_height_in=skid_params.actual_height_in,
            ground_clearance_in=ground_clearance_in
        )
        
        # === STEP 4: Generate NX Expressions File ===
        success = generate_nx_expressions_file(
            # Input parameters
            product_weight_lbs=product_weight_lbs,
            product_length_in=product_length_in,
            product_width_in=product_width_in,
            clearance_each_side_in=clearance_each_side_in,
            allow_3x4_skids_bool=allow_3x4_skids_bool,
            panel_thickness_in=panel_thickness_in,
            cleat_thickness_in=cleat_thickness_in,
            product_actual_height_in=product_actual_height_in,
            clearance_above_product_in=clearance_above_product_in,
            ground_clearance_in=ground_clearance_in,
            floorboard_actual_thickness_in=floorboard_actual_thickness_in,
            selected_std_lumber_widths=selected_std_lumber_widths,
            max_allowable_middle_gap_in=max_allowable_middle_gap_in,
            min_custom_lumber_width_in=min_custom_lumber_width_in,
            force_small_custom_board_bool=force_small_custom_board_bool,
            # Calculated parameters
            skid_params=skid_params,
            floorboard_params=floorboard_params,
            panel_params=panel_params,
            crate_overall_width_od_in=crate_overall_width_od_in,
            crate_overall_length_od_in=crate_overall_length_od_in,
            output_filename=output_filename
        )
        
        if success:
            return True, f"Successfully generated: {output_filename}"
        else:
            return False, "Failed to generate NX expressions file"
            
    except Exception as e:
        import traceback
        print(f"Error in generate_crate_expressions: {e}\n{traceback.format_exc()}")
        return False, f"Error: {e}"
