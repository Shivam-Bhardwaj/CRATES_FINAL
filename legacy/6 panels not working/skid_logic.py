"""
Skid calculation logic for crate design.
Handles skid sizing, count, and positioning calculations.
"""
import math
from typing import Tuple, NamedTuple

class SkidParameters(NamedTuple):
    """Container for skid calculation results."""
    actual_height_in: float
    actual_width_in: float
    lumber_callout: str
    max_spacing_rule_in: float
    model_length_in: float
    count: int
    pitch_in: float
    first_pos_x_in: float
    master_origin_offset_in: float

def calculate_skid_parameters(
    product_weight_lbs: float,
    product_length_in: float, 
    product_width_in: float,
    clearance_each_side_in: float,
    allow_3x4_skids_bool: bool
) -> SkidParameters:
    """
    Calculate all skid parameters based on product specifications.
    
    Args:
        product_weight_lbs: Weight of the product
        product_length_in: Length of the product
        product_width_in: Width of the product  
        clearance_each_side_in: Clearance on each side
        allow_3x4_skids_bool: Whether to allow 3x4 skids for light loads
        
    Returns:
        SkidParameters: All calculated skid parameters
    """
    # Determine skid lumber size based on weight
    use_3x4_for_light_load = allow_3x4_skids_bool and product_weight_lbs < 500
    
    if use_3x4_for_light_load:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 2.5  # Rotated 3x4
        lumber_callout = "3x4 (oriented for 3.5 H)"
        max_skid_spacing_rule_in = 30.0
    elif product_weight_lbs < 4500:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 3.5  # 4x4
        lumber_callout = "4x4"
        max_skid_spacing_rule_in = 30.0
    elif 4500 <= product_weight_lbs <= 20000:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 5.5  # 4x6
        lumber_callout = "4x6"
        max_skid_spacing_rule_in = 24.0
    else:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 5.5  # 4x6 default
        lumber_callout = "4x6 (defaulted)"
        max_skid_spacing_rule_in = 24.0
    
    # Calculate crate dimensions
    skid_model_length_in = product_length_in + (2 * clearance_each_side_in)
    crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in)
    
    # Calculate skid count and positioning
    if crate_overall_width_od_in <= skid_actual_width_in + 0.0001:
        # Single skid case
        calc_skid_count = 1
        calc_skid_pitch_in = 0.0
        calc_first_skid_pos_x_in = 0.0
    else:
        # Multiple skids case
        num_skids_float = (crate_overall_width_od_in - skid_actual_width_in) / max_skid_spacing_rule_in
        calc_skid_count = math.ceil(num_skids_float) + 1
        
        if calc_skid_count < 2:
            calc_skid_count = 2
            
        if calc_skid_count > 1:
            calc_skid_pitch_in = (crate_overall_width_od_in - skid_actual_width_in) / (calc_skid_count - 1)
        else:
            calc_skid_pitch_in = 0.0
            
        # Center skids symmetrically about X=0
        total_centerline_span = (calc_skid_count - 1) * calc_skid_pitch_in
        calc_first_skid_pos_x_in = -total_centerline_span / 2.0
    
    # Calculate master origin offset
    x_master_skid_origin_offset_in = calc_first_skid_pos_x_in - (skid_actual_width_in / 2.0)
    
    return SkidParameters(
        actual_height_in=skid_actual_height_in,
        actual_width_in=skid_actual_width_in,
        lumber_callout=lumber_callout,
        max_spacing_rule_in=max_skid_spacing_rule_in,
        model_length_in=skid_model_length_in,
        count=calc_skid_count,
        pitch_in=calc_skid_pitch_in,
        first_pos_x_in=calc_first_skid_pos_x_in,
        master_origin_offset_in=x_master_skid_origin_offset_in
    )
