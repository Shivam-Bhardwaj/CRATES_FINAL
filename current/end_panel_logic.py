def calculate_end_panel_components(
    end_panel_assembly_face_width: float, # This is the "length" or main face dimension of the end panel
    end_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float
) -> dict:
    """
    Calculates the dimensions for the end panel components:
    plywood sheathing, full-height vertical cleats, and in-between horizontal cleats.

    Args:
        end_panel_assembly_face_width: Overall width of the end panel's main face.
        end_panel_assembly_height: Overall height of the end panel assembly.
        panel_sheathing_thickness: Thickness of the plywood/sheathing.
        cleat_material_thickness: Thickness of the cleat lumber.
        cleat_material_member_width: Actual face width of the cleat lumber.

    Returns:
        A dictionary containing the dimensions of the end panel components.
    """

    # 1. Plywood Board (Sheathing)
    plywood_width = end_panel_assembly_face_width
    plywood_height = end_panel_assembly_height
    plywood_thickness = panel_sheathing_thickness

    # 2. Vertical Cleats (Left & Right)
    # These run the full height of the panel assembly.
    vertical_cleat_length = end_panel_assembly_height
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness

    # 3. Horizontal Cleats (Top & Bottom)
    # These fit between the Left and Right Vertical Cleats.
    # Their length is the panel assembly face width minus the width of the two vertical cleats.
    horizontal_cleat_length = end_panel_assembly_face_width - (2 * cleat_material_member_width)
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness
    
    # Ensure cleat lengths are not negative if panel is too small for cleats
    if horizontal_cleat_length < 0:
        horizontal_cleat_length = 0 # Or handle as an error/warning

    components = {
        'plywood': {
            'width': plywood_width, # Corresponds to end_panel_assembly_face_width
            'height': plywood_height,
            'thickness': plywood_thickness
        },
        'vertical_cleats': { # Left and Right, run full height
            'length': vertical_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2
        },
        'horizontal_cleats': { # Top and Bottom, fit between vertical cleats
            'length': horizontal_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2
        }
    }
    return components

if __name__ == '__main__':
    # Example usage for testing
    test_ep_face_width = 30.0  # inches
    test_ep_height = 60.0 # inches
    test_sheathing_thick = 0.75 # inches
    test_cleat_thick = 1.5 # inches
    test_cleat_member_width = 3.5 # inches

    end_panel_data = calculate_end_panel_components(
        test_ep_face_width, 
        test_ep_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print("End Panel Components Data:")
    import json
    print(json.dumps(end_panel_data, indent=4))

    # Test case where horizontal cleats might be problematic
    test_ep_face_width_small = 5.0
    end_panel_data_small = calculate_end_panel_components(
        test_ep_face_width_small,
        test_ep_height,
        test_sheathing_thick,
        test_cleat_thick,
        test_cleat_member_width
    )
    print("\nEnd Panel Components Data (Small Face Width):")
    print(json.dumps(end_panel_data_small, indent=4))