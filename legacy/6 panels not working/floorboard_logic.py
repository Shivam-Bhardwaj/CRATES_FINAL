"""
Floorboard calculation logic for crate design.
Handles floorboard layout, gap calculations, and lumber optimization.
"""
import math
from typing import List, Dict, Tuple, NamedTuple

class FloorboardData(NamedTuple):
    """Container for individual floorboard data."""
    width: float
    y_pos: float

class FloorboardParameters(NamedTuple):
    """Container for floorboard calculation results."""
    actual_length_in: float
    actual_thickness_in: float
    actual_middle_gap: float
    center_custom_board_width: float
    initial_start_y_offset_abs: float
    floorboards_data: List[FloorboardData]

def calculate_floorboard_parameters(
    crate_overall_width_od_in: float,
    skid_model_length_in: float,
    panel_thickness_in: float,
    cleat_thickness_in: float,
    floorboard_actual_thickness_in: float,
    selected_std_lumber_widths: List[float],
    max_allowable_middle_gap_in: float,
    min_custom_lumber_width_in: float,
    force_small_custom_board_bool: bool,
    min_forceable_custom_board_width: float = 0.25
) -> FloorboardParameters:
    """
    Calculate floorboard layout and parameters.
    
    Args:
        crate_overall_width_od_in: Overall crate width
        skid_model_length_in: Skid length
        panel_thickness_in: Panel thickness
        cleat_thickness_in: Cleat thickness
        floorboard_actual_thickness_in: Floorboard thickness
        selected_std_lumber_widths: Available standard lumber widths
        max_allowable_middle_gap_in: Maximum allowable gap in middle
        min_custom_lumber_width_in: Minimum custom lumber width
        force_small_custom_board_bool: Force small custom boards
        min_forceable_custom_board_width: Minimum forceable custom board width
        
    Returns:
        FloorboardParameters: All calculated floorboard parameters
    """
    # Basic floorboard parameters
    fb_actual_length_in = crate_overall_width_od_in
    fb_actual_thickness_in = floorboard_actual_thickness_in
    
    # Calculate usable coverage area
    cap_end_gap_each_side = panel_thickness_in + cleat_thickness_in
    fb_usable_coverage_y_in = skid_model_length_in - (2 * cap_end_gap_each_side)
    fb_initial_start_y_offset_abs = cap_end_gap_each_side
    
    # Sort available lumber widths (largest first)
    sorted_std_lumber_widths_available = sorted(selected_std_lumber_widths, reverse=True)
    
    # Fill with standard lumber pieces
    all_lumber_pieces = []
    y_covered_by_lumber = 0.0
    y_remaining_for_lumber = fb_usable_coverage_y_in
    
    while True:
        best_fit_std = 0
        for std_w in sorted_std_lumber_widths_available:
            if std_w <= y_remaining_for_lumber + 0.001:
                best_fit_std = std_w
                break
                
        if best_fit_std > 0:
            all_lumber_pieces.append(best_fit_std)
            y_covered_by_lumber += best_fit_std
            y_remaining_for_lumber -= best_fit_std
        else:
            break
    
    # Handle remaining gap with custom board or gap
    center_custom_board_width = 0.0
    actual_middle_gap = 0.0
    
    if (force_small_custom_board_bool and 
        min_forceable_custom_board_width - 0.001 <= y_remaining_for_lumber < min_custom_lumber_width_in + 0.001):
        # Force small custom board
        center_custom_board_width = y_remaining_for_lumber
        all_lumber_pieces.append(center_custom_board_width)
        y_covered_by_lumber += center_custom_board_width
        actual_middle_gap = 0.0
    elif y_remaining_for_lumber >= min_custom_lumber_width_in - 0.001:
        # Use regular custom board
        center_custom_board_width = y_remaining_for_lumber
        all_lumber_pieces.append(center_custom_board_width)
        y_covered_by_lumber += center_custom_board_width
        actual_middle_gap = 0.0
    elif 0.001 < y_remaining_for_lumber <= max_allowable_middle_gap_in + 0.001:
        # Leave as gap
        actual_middle_gap = y_remaining_for_lumber
    
    # Recalculate gap if custom board was added
    if center_custom_board_width > 0.001:
        actual_middle_gap = fb_usable_coverage_y_in - y_covered_by_lumber
        if not (0.001 < actual_middle_gap <= max_allowable_middle_gap_in + 0.001):
            actual_middle_gap = 0.0
    
    # Create floorboard layout data
    floorboards_data = []
    current_y_pos = fb_initial_start_y_offset_abs
    num_lumber_pieces_for_layout = len(all_lumber_pieces)
    
    # Determine where to insert the gap (middle of the layout)
    gap_insertion_index = (math.ceil(num_lumber_pieces_for_layout / 2.0) - 1 
                          if actual_middle_gap > 0.001 else -1)
    
    for i, board_w_val in enumerate(all_lumber_pieces):
        floorboards_data.append(FloorboardData(width=board_w_val, y_pos=current_y_pos))
        current_y_pos += board_w_val
        
        # Insert gap after the middle board if needed
        if (i == gap_insertion_index and 
            actual_middle_gap > 0.001 and 
            center_custom_board_width <= 0.001):
            current_y_pos += actual_middle_gap
    
    return FloorboardParameters(
        actual_length_in=fb_actual_length_in,
        actual_thickness_in=fb_actual_thickness_in,
        actual_middle_gap=actual_middle_gap,
        center_custom_board_width=center_custom_board_width,
        initial_start_y_offset_abs=fb_initial_start_y_offset_abs,
        floorboards_data=floorboards_data
    )
