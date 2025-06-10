"""
Panel calculation logic for crate design.
Handles panel sizing and bounding box calculations for sandwich assembly.
"""
from typing import NamedTuple

class PanelParameters(NamedTuple):
    """Container for all panel calculation results."""
    assembly_overall_thickness: float
    # Front panel
    front_calc_width: float
    front_calc_height: float
    front_calc_depth: float
    # Back panel  
    back_calc_width: float
    back_calc_height: float
    back_calc_depth: float
    # End panels
    end_calc_length: float
    end_calc_height: float
    end_calc_depth: float
    # Top panel
    top_calc_width: float
    top_calc_length: float
    top_calc_depth: float

def calculate_panel_parameters(
    crate_overall_width_od_in: float,
    crate_overall_length_od_in: float,
    panel_thickness_in: float,
    cleat_thickness_in: float,
    product_actual_height_in: float,
    clearance_above_product_in: float,
    floorboard_actual_thickness_in: float,
    skid_actual_height_in: float,
    ground_clearance_in: float
) -> PanelParameters:
    """
    Calculate panel dimensions for sandwich assembly construction.
    
    Args:
        crate_overall_width_od_in: Overall crate width
        crate_overall_length_od_in: Overall crate length
        panel_thickness_in: Panel sheathing thickness
        cleat_thickness_in: Cleat thickness
        product_actual_height_in: Product height
        clearance_above_product_in: Clearance above product
        floorboard_actual_thickness_in: Floorboard thickness
        skid_actual_height_in: Skid height
        ground_clearance_in: Ground clearance for end panels
        
    Returns:
        PanelParameters: All calculated panel parameters
    """
    # Panel assembly thickness (sheathing + cleat)
    panel_assembly_overall_thickness = panel_thickness_in + cleat_thickness_in
    
    # All panels have the same depth (thickness)
    front_panel_calc_depth = panel_assembly_overall_thickness
    back_panel_calc_depth = panel_assembly_overall_thickness
    end_panel_calc_depth = panel_assembly_overall_thickness
    
    # Panel heights
    # Front/Back panels go all the way to ground (include ground clearance)
    front_panel_calc_height = (product_actual_height_in + 
                              clearance_above_product_in + 
                              floorboard_actual_thickness_in + 
                              skid_actual_height_in + 
                              ground_clearance_in + 
                              panel_assembly_overall_thickness)
    back_panel_calc_height = front_panel_calc_height
    
    # End panels sit on skids, don't extend to ground
    # Formula: front_panel_height - ground_clearance + skid_height
    end_panel_calc_height = front_panel_calc_height - ground_clearance_in + skid_actual_height_in
    
    # Panel lengths/widths for sandwich assembly
    # End panels are sandwiched BETWEEN Front and Back panels
    end_panel_calc_length = crate_overall_length_od_in - front_panel_calc_depth - back_panel_calc_depth
    
    # Front/Back panel width COVERS the end panels
    front_panel_calc_width = crate_overall_width_od_in + (2 * end_panel_calc_depth)
    back_panel_calc_width = front_panel_calc_width
    
    # Top panel COVERS all vertical panels
    top_panel_calc_width = front_panel_calc_width
    top_panel_calc_length = crate_overall_length_od_in
    top_panel_calc_depth = panel_assembly_overall_thickness
    
    return PanelParameters(
        assembly_overall_thickness=panel_assembly_overall_thickness,
        front_calc_width=front_panel_calc_width,
        front_calc_height=front_panel_calc_height,
        front_calc_depth=front_panel_calc_depth,
        back_calc_width=back_panel_calc_width,
        back_calc_height=back_panel_calc_height,
        back_calc_depth=back_panel_calc_depth,
        end_calc_length=end_panel_calc_length,
        end_calc_height=end_panel_calc_height,
        end_calc_depth=end_panel_calc_depth,
        top_calc_width=top_panel_calc_width,
        top_calc_length=top_panel_calc_length,
        top_calc_depth=top_panel_calc_depth
    )
