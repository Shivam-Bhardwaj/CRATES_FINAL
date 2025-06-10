def calculate_front_panel_components(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float
) -> dict:
    """
    Calculates the dimensions for the front panel components:
    plywood sheathing, top/bottom horizontal cleats, and left/right vertical cleats.

    Args:
        front_panel_assembly_width: Overall width of the front panel assembly.
        front_panel_assembly_height: Overall height of the front panel assembly.
        panel_sheathing_thickness: Thickness of the plywood/sheathing.
        cleat_material_thickness: Thickness of the cleat lumber.
        cleat_material_member_width: Actual face width of the cleat lumber (e.g., 3.5" for a 1x4 or 2x4).

    Returns:
        A dictionary containing the dimensions of the front panel components.
    """

    # 1. Plywood Board (Sheathing)
    plywood_width = front_panel_assembly_width
    plywood_height = front_panel_assembly_height
    plywood_thickness = panel_sheathing_thickness

    # 2. Top & Bottom Horizontal Cleats
    # These run the full width of the panel assembly.
    horizontal_cleat_length = front_panel_assembly_width
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness

    # 3. Left & Right Vertical Cleats
    # These fit between the Top and Bottom Horizontal Cleats.
    # Their length is the panel assembly height minus the width of the two horizontal cleats.
    vertical_cleat_length = front_panel_assembly_height - (2 * cleat_material_member_width)
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness
    
    # Ensure cleat lengths are not negative if panel is too small for cleats
    if vertical_cleat_length < 0:
        vertical_cleat_length = 0 # Or handle as an error/warning if preferred

    components = {
        'plywood': {
            'width': plywood_width,
            'height': plywood_height,
            'thickness': plywood_thickness
        },
        'horizontal_cleats': { # Top and Bottom
            'length': horizontal_cleat_length,
            'material_thickness': cleat_material_thickness, # Dimension perpendicular to sheathing
            'material_member_width': cleat_material_member_width, # Dimension on the face of sheathing
            'count': 2
        },
        'vertical_cleats': { # Left and Right
            'length': vertical_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2
        }
        # Mid cleats will be added later
    }
    return components

if __name__ == '__main__':
    # Example usage for testing
    test_fp_width = 48.0  # inches
    test_fp_height = 60.0 # inches
    test_sheathing_thick = 0.75 # inches
    test_cleat_thick = 1.5 # inches
    test_cleat_member_width = 3.5 # inches

    front_panel_data = calculate_front_panel_components(
        test_fp_width, 
        test_fp_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print("Front Panel Components Data:")
    import json
    print(json.dumps(front_panel_data, indent=4))

    # Test case where vertical cleats might be problematic
    test_fp_height_small = 5.0
    front_panel_data_small = calculate_front_panel_components(
        test_fp_width,
        test_fp_height_small,
        test_sheathing_thick,
        test_cleat_thick,
        test_cleat_member_width
    )
    print("\nFront Panel Components Data (Small Height):")
    print(json.dumps(front_panel_data_small, indent=4))