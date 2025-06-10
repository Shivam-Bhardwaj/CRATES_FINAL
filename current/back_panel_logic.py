from front_panel_logic import calculate_front_panel_components # Reuse the core calculation

def calculate_back_panel_components(
    back_panel_assembly_width: float,
    back_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float
) -> dict:
    """
    Calculates the dimensions for the back panel components.
    This currently uses the same logic as the front panel.

    Args:
        back_panel_assembly_width: Overall width of the back panel assembly.
        back_panel_assembly_height: Overall height of the back panel assembly.
        panel_sheathing_thickness: Thickness of the plywood/sheathing.
        cleat_material_thickness: Thickness of the cleat lumber.
        cleat_material_member_width: Actual face width of the cleat lumber.

    Returns:
        A dictionary containing the dimensions of the back panel components.
    """
    # The logic for calculating components is identical to the front panel
    return calculate_front_panel_components(
        front_panel_assembly_width=back_panel_assembly_width,
        front_panel_assembly_height=back_panel_assembly_height,
        panel_sheathing_thickness=panel_sheathing_thickness,
        cleat_material_thickness=cleat_material_thickness,
        cleat_material_member_width=cleat_material_member_width
    )

if __name__ == '__main__':
    # Example usage for testing
    test_bp_width = 50.0  # inches
    test_bp_height = 65.0 # inches
    test_sheathing_thick = 0.5 # inches
    test_cleat_thick = 0.75 # inches
    test_cleat_member_width = 3.5 # inches

    back_panel_data = calculate_back_panel_components(
        test_bp_width, 
        test_bp_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print("Back Panel Components Data:")
    import json
    print(json.dumps(back_panel_data, indent=4))