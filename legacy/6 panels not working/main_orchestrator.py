# FILE: main_orchestrator.py
"""
Main orchestrator module for the NX Crate Expression Generator.
Coordinates the skid, floorboard, panel logic modules and NX generator.
"""
from typing import Dict, Tuple, List

from skid_logic import calculate_skid_parameters
from floorboard_logic import calculate_floorboard_parameters, FloorboardParameters # Added FloorboardParameters import
from panel_logic import calculate_panel_parameters, PanelParameters # Added PanelParameters import
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
        # --- ADDED VALIDATION ---
        cleat_actual_width_in = inputs['cleat_actual_width_in']
        product_actual_height_in = inputs['product_actual_height_in']
        clearance_above_product_in = inputs['clearance_above_product_in']
        ground_clearance_in = inputs['ground_clearance_in']
        floorboard_actual_thickness_in = inputs['floorboard_actual_thickness_in']
        selected_std_lumber_widths = inputs['selected_std_lumber_widths']
        max_allowable_middle_gap_in = inputs['max_allowable_middle_gap_in']
        min_custom_lumber_width_in = inputs['min_custom_lumber_width_in']
        force_small_custom_board_bool = inputs['force_small_custom_board_bool']
        # --- ADDED for skid and cleat validation ---
        skid_material_nominal_width_in = inputs['skid_material_nominal_width_in']
        skid_material_nominal_thickness_in = inputs['skid_material_nominal_thickness_in']
        skid_spacing_in = inputs['skid_spacing_in']
        # num_skids_override is optional, so not validated here for presence
        max_inter_cleat_spacing_in = inputs['max_inter_cleat_spacing_in']
        
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
        # --- ADDED VALIDATION ---
        if cleat_actual_width_in <= 0:
            return False, "Cleat actual width must be positive."
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
        # --- ADDED validation for new inputs ---
        if skid_material_nominal_width_in <= 0:
            return False, "Skid material nominal width must be positive."
        if skid_material_nominal_thickness_in <= 0:
            return False, "Skid material nominal thickness must be positive."
        if skid_spacing_in < 0: # Can be 0 if only one skid, but not negative
            return False, "Skid spacing cannot be negative."
        if max_inter_cleat_spacing_in <= 0:
            return False, "Max inter cleat spacing must be positive."
        
        return True, ""
        
    except KeyError as e:
        return False, f"Missing required input: {e}"
    except Exception as e:
        return False, f"Input validation error: {e}"

def calculate_side_vertical_cleat_length(inputs: dict) -> float:
    """
    Calculate the length of the side (end) panel vertical cleat based on product and crate inputs.
    Formula:
        length = skid_height + floorboard_thickness + product_height + top_clearance - ground_clearance
    """
    return (
        inputs["skid_height_in"]
        + inputs["floorboard_actual_thickness_in"]
        + inputs["product_actual_height_in"]
        + inputs["clearance_above_product_in"]
        - inputs["ground_clearance_in"]
    )

def calculate_front_back_top_bottom_cleat_length(inputs: dict) -> float:
    """
    Calculate the length of the front/back panel top/bottom cleat.
    Formula:
        length = product_width + 2 * side_clearance + 2 * (side panel thickness + cleat_thickness)
    """
    return (
        inputs["product_actual_width_in"]
        + 2 * inputs["side_clearance_in"]
        + 2 * (inputs["panel_thickness_in"] + inputs["cleat_thickness_in"])
    )

def calculate_side_horizontal_cleat_length(inputs: dict) -> float:
    """
    Calculate the length of the side (end) panel horizontal cleat.
    Formula:
        length = product_length_along_skids + 2 * side_clearance - 2 * cleat_actual_width
    """
    return (
        inputs["product_actual_length_in"]
        + 2 * inputs["side_clearance_in"]
        - 2 * inputs["cleat_actual_width_in"]
    )

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
        cleat_actual_width_in = inputs['cleat_actual_width_in']
        product_actual_height_in = inputs['product_actual_height_in']
        clearance_above_product_in = inputs['clearance_above_product_in']
        ground_clearance_in = inputs['ground_clearance_in']
        floorboard_actual_thickness_in = inputs['floorboard_actual_thickness_in']
        selected_std_lumber_widths = inputs['selected_std_lumber_widths']
        max_allowable_middle_gap_in = inputs['max_allowable_middle_gap_in']
        min_custom_lumber_width_in = inputs['min_custom_lumber_width_in']
        force_small_custom_board_bool = inputs['force_small_custom_board_bool']
        skid_material_nominal_width_in = inputs['skid_material_nominal_width_in']
        skid_material_nominal_thickness_in = inputs['skid_material_nominal_thickness_in']
        skid_spacing_in = inputs['skid_spacing_in']
        num_skids_override = inputs.get('num_skids_override') # Optional
        max_inter_cleat_spacing_in = inputs['max_inter_cleat_spacing_in']
        
        # --- Calculate derived dimensions ---
        # Skid parameters
        skid_params = calculate_skid_parameters(
            product_weight_lbs,
            product_length_in,
            product_width_in,
            clearance_each_side_in,
            allow_3x4_skids_bool
            # Removed skid_material_nominal_width_in, skid_material_nominal_thickness_in, skid_spacing_in, num_skids_override
            # as they are not direct inputs to calculate_skid_parameters based on previous corrections.
            # calculate_skid_parameters seems to only need the first 5 arguments.
        )

        # Crate internal dimensions (plywood to plywood)
        crate_internal_width = product_width_in + (2 * clearance_each_side_in)
        crate_internal_length = product_length_in + (2 * clearance_each_side_in)

        # Floorboard parameters
        floorboard_params = calculate_floorboard_parameters(
            crate_overall_width_od_in=crate_internal_width, # Corrected argument name
            skid_model_length_in=skid_params.model_length_in, # Added missing argument
            panel_thickness_in=panel_thickness_in, # Added missing argument
            cleat_thickness_in=cleat_thickness_in, # Added missing argument
            floorboard_actual_thickness_in=floorboard_actual_thickness_in,
            selected_std_lumber_widths=selected_std_lumber_widths,
            max_allowable_middle_gap_in=max_allowable_middle_gap_in,
            min_custom_lumber_width_in=min_custom_lumber_width_in,
            force_small_custom_board_bool=force_small_custom_board_bool
            # min_forceable_custom_board_width is optional with a default
        )
        
        # Panel parameters
        enclosed_vertical_space_height = (
            # floorboard_actual_thickness_in + # This was an error, floorboard is part of the height calculation for side panels, not general enclosed space from skids
            product_actual_height_in +
            clearance_above_product_in
        )

        front_back_panel_plywood_height = enclosed_vertical_space_height # Sits on floorboards

        side_panel_plywood_height = (
            skid_params.actual_height_in +
            floorboard_actual_thickness_in +
            product_actual_height_in +
            clearance_above_product_in -
            ground_clearance_in
        )
        side_panel_plywood_height = max(0, side_panel_plywood_height)

        panel_assembly_thickness = panel_thickness_in + cleat_thickness_in

        panel_params = PanelParameters(
            assembly_overall_thickness=panel_assembly_thickness,
            front_calc_width=crate_internal_width,
            front_calc_height=front_back_panel_plywood_height,
            front_calc_depth=panel_assembly_thickness,
            back_calc_width=crate_internal_width,
            back_calc_height=front_back_panel_plywood_height,
            back_calc_depth=panel_assembly_thickness,
            end_calc_length=crate_internal_length, # Side panel "length" is along crate length
            end_calc_height=side_panel_plywood_height,
            end_calc_depth=panel_assembly_thickness,
            top_calc_length=crate_internal_length,
            top_calc_width=crate_internal_width,
            top_calc_depth=panel_assembly_thickness
        )

        # Overall Crate Dimensions (Outer Dimensions)
        # Front/Back panels are full width of crate_internal_width + their assembly thickness on each side (length direction)
        # Side panels are "sandwiched", so they determine the overall width.
        crate_overall_length_od_in = crate_internal_length + (2 * panel_assembly_thickness)
        crate_overall_width_od_in = crate_internal_width + (2 * panel_assembly_thickness)
        
        # The specific cleat length calculations (fb_top_bot_cleat_len, etc.) are removed from here.
        # nx_generator.py calculates the required cleat lengths for its expressions internally.

        # Generate NX expressions file
        success = generate_nx_expressions_file(
            product_weight_lbs=product_weight_lbs,
            product_length_in=product_length_in,
            product_width_in=product_width_in,
            clearance_each_side_in=clearance_each_side_in,
            allow_3x4_skids_bool=allow_3x4_skids_bool,
            panel_thickness_in=panel_thickness_in,
            cleat_thickness_in=cleat_thickness_in,
            cleat_actual_width_in=cleat_actual_width_in,
            product_actual_height_in=product_actual_height_in,
            clearance_above_product_in=clearance_above_product_in,
            ground_clearance_in=ground_clearance_in,
            floorboard_actual_thickness_in=floorboard_actual_thickness_in,
            selected_std_lumber_widths=selected_std_lumber_widths,
            max_allowable_middle_gap_in=max_allowable_middle_gap_in,
            min_custom_lumber_width_in=min_custom_lumber_width_in,
            force_small_custom_board_bool=force_small_custom_board_bool,
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
        print(f"Error in generate_crate_expressions: {e}\\n{traceback.format_exc()}")
        return False, f"Error: {e}"

# Remove the now-unused cleat calculation helper functions if they were solely for the old inputs_for_nx
# For example, if calculate_side_vertical_cleat_length, 
# calculate_front_back_top_bottom_cleat_length, 
# and calculate_side_horizontal_cleat_length are no longer used elsewhere, they can be removed.
# However, looking at their definitions, they seem generic and might be useful later,
# or were intended for a different purpose than populating inputs_for_nx.
# For now, I will leave them, as the primary goal is to fix the TypeError.
# The specific cleat length calculations that were done just before creating `inputs_for_nx`
# (i.e., fb_top_bot_cleat_len, side_vert_cleat_len, side_horiz_cleat_len variables)
# are effectively superseded by nx_generator.py's internal logic or direct use of panel_params.
