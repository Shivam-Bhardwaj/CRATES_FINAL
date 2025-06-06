"""
NX Expressions file generator for crate design.
Generates parametric expressions for use in Siemens NX CAD system.
"""
import datetime
from typing import List

from skid_logic import SkidParameters
from floorboard_logic import FloorboardParameters
from panel_logic import PanelParameters

# Constants
MAX_NX_FLOORBOARD_INSTANCES = 20

def generate_nx_expressions_file(
    # Input parameters
    product_weight_lbs: float,
    product_length_in: float,
    product_width_in: float,
    clearance_each_side_in: float,
    allow_3x4_skids_bool: bool,
    panel_thickness_in: float,
    cleat_thickness_in: float,
    product_actual_height_in: float,
    clearance_above_product_in: float,
    ground_clearance_in: float,
    floorboard_actual_thickness_in: float,
    selected_std_lumber_widths: List[float],
    max_allowable_middle_gap_in: float,
    min_custom_lumber_width_in: float,
    force_small_custom_board_bool: bool,
    # Calculated parameters
    skid_params: SkidParameters,
    floorboard_params: FloorboardParameters,
    panel_params: PanelParameters,
    crate_overall_width_od_in: float,
    crate_overall_length_od_in: float,
    output_filename: str
) -> bool:
    """
    Generate NX expressions file with all calculated parameters.
    
    Args:
        Input parameters and calculated results from logic modules
        output_filename: Path to save the expressions file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare expressions file content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expressions_content = [
            f"// NX Expressions - Skids, Floorboards & Panels (Sandwich Logic Corrected)",
            f"// Generated: {timestamp}\n",
            
            f"// --- USER INPUTS & CRATE CONSTANTS ---",
            f"[lbm]product_weight = {product_weight_lbs:.3f}",
            f"[Inch]product_length_input = {product_length_in:.3f}",
            f"[Inch]product_width_input = {product_width_in:.3f}",
            f"[Inch]clearance_side_input = {clearance_each_side_in:.3f}",
            f"BOOL_Allow_3x4_Skids_Input = {1 if allow_3x4_skids_bool else 0}",
            f"[Inch]INPUT_Panel_Thickness = {panel_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Thickness = {cleat_thickness_in:.3f}",
            f"[Inch]INPUT_Product_Actual_Height = {product_actual_height_in:.3f}",
            f"[Inch]INPUT_Clearance_Above_Product = {clearance_above_product_in:.3f}",
            f"[Inch]INPUT_Ground_Clearance_End_Panels = {ground_clearance_in:.3f}",
            f"BOOL_Force_Small_Custom_Floorboard = {1 if force_small_custom_board_bool else 0}",
            f"[Inch]INPUT_Floorboard_Actual_Thickness = {floorboard_actual_thickness_in:.3f}",
            f"[Inch]INPUT_Max_Allowable_Middle_Gap = {max_allowable_middle_gap_in:.3f}",
            f"[Inch]INPUT_Min_Custom_Lumber_Width = {min_custom_lumber_width_in:.3f}\n",
            
            f"// --- CALCULATED CRATE DIMENSIONS ---",
            f"[Inch]crate_overall_width_OD = {crate_overall_width_od_in:.3f}",
            f"[Inch]crate_overall_length_OD = {crate_overall_length_od_in:.3f}\n",
            
            f"// --- SKID PARAMETERS ---",
            f"// Skid Lumber Callout: {skid_params.lumber_callout}",
            f"[Inch]Skid_Actual_Height = {skid_params.actual_height_in:.3f}",
            f"[Inch]Skid_Actual_Width = {skid_params.actual_width_in:.3f}",
            f"[Inch]Skid_Actual_Length = {skid_params.model_length_in:.3f}",
            f"CALC_Skid_Count = {skid_params.count}",
            f"[Inch]CALC_Skid_Pitch = {skid_params.pitch_in:.4f}",
            f"[Inch]CALC_First_Skid_Pos_X = {skid_params.first_pos_x_in:.4f}",
            f"[Inch]X_Master_Skid_Origin_Offset = {skid_params.master_origin_offset_in:.4f}\n",
            
            f"// --- FLOORBOARD PARAMETERS ---",
            f"[Inch]FB_Board_Actual_Length = {floorboard_params.actual_length_in:.3f}",
            f"[Inch]FB_Board_Actual_Thickness = {floorboard_params.actual_thickness_in:.3f}",
            f"[Inch]CALC_FB_Actual_Middle_Gap = {floorboard_params.actual_middle_gap:.4f}",
            f"[Inch]CALC_FB_Center_Custom_Board_Width = {floorboard_params.center_custom_board_width if floorboard_params.center_custom_board_width > 0.001 else 0.0:.4f}",
            f"[Inch]CALC_FB_Start_Y_Offset_Abs = {floorboard_params.initial_start_y_offset_abs:.3f}\n",
            f"// Floorboard Instance Data"
        ]
        
        # Add floorboard instances
        for i in range(MAX_NX_FLOORBOARD_INSTANCES):
            instance_num = i + 1
            if i < len(floorboard_params.floorboards_data):
                board = floorboard_params.floorboards_data[i]
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = {board.width:.4f}")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = {board.y_pos:.4f}")
            else:
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 1")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = 0.0001")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = 0.0000")
        
        # Add panel parameters
        expressions_content.extend([
            f"\n// --- PANEL BOUNDING BOX PARAMETERS ---",
            f"[Inch]PANEL_Front_Calc_Width = {panel_params.front_calc_width:.3f}",
            f"[Inch]PANEL_Front_Calc_Height = {panel_params.front_calc_height:.3f}",
            f"[Inch]PANEL_Front_Calc_Depth = {panel_params.front_calc_depth:.3f}\n",
            f"[Inch]PANEL_Back_Calc_Width = {panel_params.back_calc_width:.3f}",
            f"[Inch]PANEL_Back_Calc_Height = {panel_params.back_calc_height:.3f}",
            f"[Inch]PANEL_Back_Calc_Depth = {panel_params.back_calc_depth:.3f}\n",
            f"[Inch]PANEL_End_Calc_Length = {panel_params.end_calc_length:.3f} // For Left & Right End Panels",
            f"[Inch]PANEL_End_Calc_Height = {panel_params.end_calc_height:.3f} // For Left & Right End Panels",
            f"[Inch]PANEL_End_Calc_Depth = {panel_params.end_calc_depth:.3f} // For Left & Right End Panels\n",
            f"[Inch]PANEL_Top_Calc_Width = {panel_params.top_calc_width:.3f}",
            f"[Inch]PANEL_Top_Calc_Length = {panel_params.top_calc_length:.3f}",
            f"[Inch]PANEL_Top_Calc_Depth = {panel_params.top_calc_depth:.3f}\n",
            f"// End of Expressions"
        ])
        
        # Write to file
        with open(output_filename, "w") as f:
            for line in expressions_content:
                f.write(line + "\n")
                
        return True
        
    except Exception as e:
        print(f"Error generating NX expressions file: {e}")
        return False
