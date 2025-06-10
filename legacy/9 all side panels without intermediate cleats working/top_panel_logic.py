def calculate_top_panel_components(
    top_panel_assembly_width: float,  # This corresponds to the overall width of the top panel (like front_panel_calc_width)
    top_panel_assembly_length: float, # This corresponds to the overall length of the top panel (like crate_overall_length_od_in)
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float
) -> dict:
    """
    Calculates the dimensions for the top panel components:
    plywood sheathing, primary cleats (along length), and secondary cleats (along width).

    Args:
        top_panel_assembly_width: Overall width of the top panel assembly.
        top_panel_assembly_length: Overall length of the top panel assembly.
        panel_sheathing_thickness: Thickness of the plywood/sheathing.
        cleat_material_thickness: Thickness of the cleat lumber.
        cleat_material_member_width: Actual face width of the cleat lumber.

    Returns:
        A dictionary containing the dimensions of the top panel components.
    """

    # 1. Plywood Board (Sheathing)
    plywood_width = top_panel_assembly_width
    plywood_length = top_panel_assembly_length # The main dimension of the plywood sheet
    plywood_thickness = panel_sheathing_thickness

    # 2. Primary Cleats (e.g., running along the length of the crate)
    # These run the full length of the panel assembly.
    primary_cleat_length = top_panel_assembly_length
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness

    # 3. Secondary Cleats (e.g., running across the width, between primary cleats)
    # These fit between the Primary Cleats.
    # Their length is the panel assembly width minus the width of the two primary cleats.
    secondary_cleat_length = top_panel_assembly_width - (2 * cleat_material_member_width)
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness
    
    # Ensure cleat lengths are not negative
    if secondary_cleat_length < 0:
        secondary_cleat_length = 0

    components = {
        'plywood': {
            'width': plywood_width,    # Dimension across the crate
            'length': plywood_length,  # Dimension along the crate length
            'thickness': plywood_thickness
        },
        'primary_cleats': { # e.g., 2 cleats running along the length of the top panel
            'length': primary_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2 # Assuming one on each long edge
        },
        'secondary_cleats': { # e.g., 2 cleats running across the width, between primary cleats
            'length': secondary_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2 # Assuming one on each short edge, fitting between primary
        }
        # More complex internal cleating (e.g., mid-span supports) could be added later
    }
    return components

if __name__ == '__main__':
    # Example usage for testing
    test_tp_width = 48.0  # inches (like front_panel_calc_width)
    test_tp_length = 100.0 # inches (like crate_overall_length_od_in)
    test_sheathing_thick = 0.75 # inches
    test_cleat_thick = 1.5 # inches
    test_cleat_member_width = 3.5 # inches

    top_panel_data = calculate_top_panel_components(
        test_tp_width, 
        test_tp_length, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print("Top Panel Components Data:")
    import json
    print(json.dumps(top_panel_data, indent=4))

    # Test case where secondary cleats might be problematic
    test_tp_width_small = 5.0
    top_panel_data_small = calculate_top_panel_components(
        test_tp_width_small,
        test_tp_length,
        test_sheathing_thick,
        test_cleat_thick,
        test_cleat_member_width
    )
    print("\nTop Panel Components Data (Small Width):")
    print(json.dumps(top_panel_data_small, indent=4))