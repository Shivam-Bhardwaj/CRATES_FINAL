import datetime
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from front_panel_logic import calculate_front_panel_components
from back_panel_logic import calculate_back_panel_components
from end_panel_logic import calculate_end_panel_components
from top_panel_logic import calculate_top_panel_components # Import for top panel

# --- Default Constants ---
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = { 
    "2x6 (5.5 in)": 5.5, "2x8 (7.25 in)": 7.25,
    "2x10 (9.25 in)": 9.25, "2x12 (11.25 in)": 11.25
}
DEFAULT_MIN_CUSTOM_LUMBER_WIDTH = 2.5
DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP = 0.25
MIN_FORCEABLE_CUSTOM_BOARD_WIDTH = 0.25 
MAX_NX_FLOORBOARD_INSTANCES = 20
DEFAULT_CLEAT_MEMBER_WIDTH = 3.5 # Added default for cleat member width

def generate_crate_expressions_logic(
    # Skid Inputs
    product_weight_lbs: float, product_length_in: float, product_width_in: float,
    clearance_each_side_in: float, allow_3x4_skids_bool: bool,
    # General Crate & Panel Inputs
    panel_thickness_in: float, cleat_thickness_in: float, cleat_member_actual_width_in: float, # Added cleat_member_actual_width_in
    product_actual_height_in: float, 
    clearance_above_product_in: float,
    ground_clearance_in: float,
    # Floorboard Inputs
    floorboard_actual_thickness_in: float, selected_std_lumber_widths: list[float], 
    max_allowable_middle_gap_in: float, min_custom_lumber_width_in: float,
    force_small_custom_board_bool: bool, 
    # Output
    output_filename: str
) -> tuple[bool, str]:
    try:
        # --- Input Validations ---
        if product_weight_lbs < 0: return False, "Product weight invalid."
        if product_length_in <=0: return False, "Product length must be positive."
        if product_width_in <=0: return False, "Product width must be positive."
        if clearance_each_side_in < 0: return False, "Clearance cannot be negative."
        if panel_thickness_in <=0: return False, "Panel sheathing thickness must be positive."
        if cleat_thickness_in <0: return False, "Cleat thickness cannot be negative (can be 0)."
        if cleat_member_actual_width_in <=0: return False, "Cleat member actual width must be positive." # Added validation
        if product_actual_height_in <=0: return False, "Product actual height must be positive."
        if clearance_above_product_in <0: return False, "Clearance above product cannot be negative."
        if ground_clearance_in <0: return False, "Ground clearance cannot be negative."
        if floorboard_actual_thickness_in <=0: return False, "Floorboard thickness must be positive."
        if not selected_std_lumber_widths: return False, "No standard lumber selected for floorboards."
        if max_allowable_middle_gap_in < 0: return False, "Max middle gap cannot be negative."
        if min_custom_lumber_width_in <= 0: return False, "Min custom lumber width must be positive."
        if min_custom_lumber_width_in < MIN_FORCEABLE_CUSTOM_BOARD_WIDTH and force_small_custom_board_bool:
             if min_custom_lumber_width_in < MIN_FORCEABLE_CUSTOM_BOARD_WIDTH:
                return False, f"Min custom board width generally cannot be less than {MIN_FORCEABLE_CUSTOM_BOARD_WIDTH} inches."

        # === SKID CALCULATIONS ===
        skid_actual_height_in: float; skid_actual_width_in: float; lumber_callout: str; max_skid_spacing_rule_in: float
        use_3x4_for_light_load = allow_3x4_skids_bool and product_weight_lbs < 500
        if use_3x4_for_light_load:
            skid_actual_height_in = 3.5; skid_actual_width_in = 2.5; lumber_callout = "3x4 (oriented for 3.5 H)"; max_skid_spacing_rule_in = 30.0
        elif product_weight_lbs < 4500:
            skid_actual_height_in = 3.5; skid_actual_width_in = 3.5; lumber_callout = "4x4"; max_skid_spacing_rule_in = 30.0
        elif 4500 <= product_weight_lbs <= 20000:
            skid_actual_height_in = 3.5; skid_actual_width_in = 5.5; lumber_callout = "4x6"; max_skid_spacing_rule_in = 24.0
        else:
            skid_actual_height_in = 3.5; skid_actual_width_in = 5.5; lumber_callout = "4x6 (defaulted)"; max_skid_spacing_rule_in = 24.0
        
        skid_model_length_in = product_length_in + (2 * clearance_each_side_in)
        crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in) 
        crate_overall_length_od_in = skid_model_length_in 
        
        calc_skid_count: int; calc_skid_pitch_in: float; calc_first_skid_pos_x_in: float
        if crate_overall_width_od_in <= skid_actual_width_in + 0.0001: 
            calc_skid_count = 1; calc_skid_pitch_in = 0.0; calc_first_skid_pos_x_in = 0.0
        else:
            num_skids_float = (crate_overall_width_od_in - skid_actual_width_in) / max_skid_spacing_rule_in
            calc_skid_count = math.ceil(num_skids_float) + 1
            if calc_skid_count < 2: calc_skid_count = 2
            if calc_skid_count > 1 :
                calc_skid_pitch_in = (crate_overall_width_od_in - skid_actual_width_in) / (calc_skid_count - 1)
            else:
                calc_skid_pitch_in = 0.0
            total_centerline_span = (calc_skid_count - 1) * calc_skid_pitch_in
            calc_first_skid_pos_x_in = -total_centerline_span / 2.0 
        x_master_skid_origin_offset_in = calc_first_skid_pos_x_in - (skid_actual_width_in / 2.0)
        
        # === FLOORBOARD CALCULATIONS ===
        fb_actual_length_in = crate_overall_width_od_in 
        fb_actual_thickness_in = floorboard_actual_thickness_in
        cap_end_gap_each_side = panel_thickness_in + cleat_thickness_in
        fb_usable_coverage_y_in = skid_model_length_in - (2 * cap_end_gap_each_side) 
        fb_initial_start_y_offset_abs = cap_end_gap_each_side 
        sorted_std_lumber_widths_available = sorted(selected_std_lumber_widths, reverse=True)
        all_lumber_pieces = []; y_covered_by_lumber = 0.0; y_remaining_for_lumber = fb_usable_coverage_y_in
        while True:
            best_fit_std = 0
            for std_w in sorted_std_lumber_widths_available:
                if std_w <= y_remaining_for_lumber + 0.001: best_fit_std = std_w; break
            if best_fit_std > 0:
                all_lumber_pieces.append(best_fit_std); y_covered_by_lumber += best_fit_std; y_remaining_for_lumber -= best_fit_std
            else: break 
        center_custom_board_width = 0.0; actual_middle_gap = 0.0
        if force_small_custom_board_bool and MIN_FORCEABLE_CUSTOM_BOARD_WIDTH - 0.001 <= y_remaining_for_lumber < min_custom_lumber_width_in + 0.001 :
            center_custom_board_width = y_remaining_for_lumber; all_lumber_pieces.append(center_custom_board_width); y_covered_by_lumber += center_custom_board_width; actual_middle_gap = 0.0
        elif y_remaining_for_lumber >= min_custom_lumber_width_in - 0.001:
            center_custom_board_width = y_remaining_for_lumber; all_lumber_pieces.append(center_custom_board_width); y_covered_by_lumber += center_custom_board_width; actual_middle_gap = 0.0
        elif 0.001 < y_remaining_for_lumber <= max_allowable_middle_gap_in + 0.001: actual_middle_gap = y_remaining_for_lumber
        if center_custom_board_width > 0.001:
            actual_middle_gap = fb_usable_coverage_y_in - y_covered_by_lumber 
            if not (0.001 < actual_middle_gap <= max_allowable_middle_gap_in + 0.001): actual_middle_gap = 0.0
        floorboards_data = []; current_y_pos = fb_initial_start_y_offset_abs; num_lumber_pieces_for_layout = len(all_lumber_pieces)
        gap_insertion_index = math.ceil(num_lumber_pieces_for_layout / 2.0) - 1 if actual_middle_gap > 0.001 else -1
        for i, board_w_val in enumerate(all_lumber_pieces):
            floorboards_data.append({'width': board_w_val, 'y_pos': current_y_pos}); current_y_pos += board_w_val
            if i == gap_insertion_index and actual_middle_gap > 0.001 and center_custom_board_width <= 0.001: current_y_pos += actual_middle_gap
        
        # === PANEL BOUNDING BOX CALCULATIONS (Corrected Assembly Logic) ===
        panel_assembly_overall_thickness = panel_thickness_in + cleat_thickness_in 
        
        # Front/Back panels have a depth/thickness
        front_panel_calc_depth = panel_assembly_overall_thickness
        back_panel_calc_depth = panel_assembly_overall_thickness
        
        # End Panels are sandwiched between Front and Back
        end_panel_calc_length = crate_overall_length_od_in - front_panel_calc_depth - back_panel_calc_depth
        end_panel_calc_height_base = floorboard_actual_thickness_in + product_actual_height_in + clearance_above_product_in
        end_panel_calc_height = end_panel_calc_height_base + (skid_actual_height_in - ground_clearance_in)
        end_panel_calc_depth = panel_assembly_overall_thickness
        
        # Front/Back panel width covers the end panels
        front_panel_calc_width = crate_overall_width_od_in + (2 * end_panel_calc_depth)
        front_panel_calc_height = end_panel_calc_height_base 
        
        # Back Panel Assy (Same as Front for now, component details can be separated later if different)
        back_panel_calc_width = front_panel_calc_width
        back_panel_calc_height = front_panel_calc_height
        
        # Top Panel Assy (covers all vertical panels)
        top_panel_calc_width = front_panel_calc_width 
        top_panel_calc_length = crate_overall_length_od_in
        top_panel_calc_depth = panel_assembly_overall_thickness

        # === DETAILED PANEL COMPONENT CALCULATIONS ===
        # --- Front Panel Components ---
        front_panel_components_data = calculate_front_panel_components(
            front_panel_assembly_width=front_panel_calc_width,
            front_panel_assembly_height=front_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )

        # --- Back Panel Components ---
        back_panel_components_data = calculate_back_panel_components( 
            back_panel_assembly_width=back_panel_calc_width,
            back_panel_assembly_height=back_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )

        # --- End Panel Components (for Left & Right, assumed identical) ---
        # Overall dimensions for end panels are already calculated:
        # end_panel_calc_length (this is the "face width" of the end panel)
        # end_panel_calc_height
        # Material properties are the same.
        end_panel_components_data = calculate_end_panel_components(
            end_panel_assembly_face_width=end_panel_calc_length,
            end_panel_assembly_height=end_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )

        # --- Top Panel Components ---
        # Overall dimensions for top panel are already calculated:
        # top_panel_calc_width, top_panel_calc_length
        # Material properties are the same.
        top_panel_components_data = calculate_top_panel_components(
            top_panel_assembly_width=top_panel_calc_width,
            top_panel_assembly_length=top_panel_calc_length,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )

        # --- Prepare expressions file content ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expressions_content = [
            f"// NX Expressions - Skids, Floorboards & Detailed Panels", # Updated title
            f"// Generated: {timestamp}\n",
            f"// --- USER INPUTS & CRATE CONSTANTS ---",
            f"[lbm]product_weight = {product_weight_lbs:.3f}",
            f"[Inch]product_length_input = {product_length_in:.3f}",
            f"[Inch]product_width_input = {product_width_in:.3f}", 
            f"[Inch]clearance_side_input = {clearance_each_side_in:.3f}", 
            f"BOOL_Allow_3x4_Skids_Input = {1 if allow_3x4_skids_bool else 0}",
            f"[Inch]INPUT_Panel_Thickness = {panel_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Thickness = {cleat_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Member_Actual_Width = {cleat_member_actual_width_in:.3f}", # Added input echo
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
            f"// Skid Lumber Callout: {lumber_callout}",
            f"[Inch]Skid_Actual_Height = {skid_actual_height_in:.3f}",
            f"[Inch]Skid_Actual_Width = {skid_actual_width_in:.3f}",
            f"[Inch]Skid_Actual_Length = {skid_model_length_in:.3f}",
            f"CALC_Skid_Count = {calc_skid_count}",
            f"[Inch]CALC_Skid_Pitch = {calc_skid_pitch_in:.4f}", 
            f"[Inch]X_Master_Skid_Origin_Offset = {x_master_skid_origin_offset_in:.4f}\n",
            
            f"// --- FLOORBOARD PARAMETERS ---",
            f"[Inch]FB_Board_Actual_Length = {fb_actual_length_in:.3f}", 
            f"[Inch]FB_Board_Actual_Thickness = {fb_actual_thickness_in:.3f}",
            f"[Inch]CALC_FB_Actual_Middle_Gap = {actual_middle_gap:.4f}", 
            f"[Inch]CALC_FB_Center_Custom_Board_Width = {center_custom_board_width if center_custom_board_width > 0.001 else 0.0:.4f}",
            f"[Inch]CALC_FB_Start_Y_Offset_Abs = {fb_initial_start_y_offset_abs:.3f}\n",
            f"// Floorboard Instance Data"
        ]
        for i in range(MAX_NX_FLOORBOARD_INSTANCES):
            instance_num = i + 1
            if i < len(floorboards_data):
                board = floorboards_data[i]
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = {board['width']:.4f}")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = {board['y_pos']:.4f}")
            else:
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 1")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = 0.0001")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = 0.0000")
            
        expressions_content.extend([
            f"\n// --- OVERALL PANEL ASSEMBLY DIMENSIONS (Informational) ---",
            f"[Inch]PANEL_Front_Assy_Overall_Width = {front_panel_calc_width:.3f}",
            f"[Inch]PANEL_Front_Assy_Overall_Height = {front_panel_calc_height:.3f}",
            f"[Inch]PANEL_Front_Assy_Overall_Depth = {front_panel_calc_depth:.3f}\n",
            
            f"[Inch]PANEL_Back_Assy_Overall_Width = {back_panel_calc_width:.3f}", # Assuming same as front for now
            f"[Inch]PANEL_Back_Assy_Overall_Height = {back_panel_calc_height:.3f}",
            f"[Inch]PANEL_Back_Assy_Overall_Depth = {back_panel_calc_depth:.3f}\n",

            f"[Inch]PANEL_End_Assy_Overall_Length_Face = {end_panel_calc_length:.3f} // For Left & Right End Panels",
            f"[Inch]PANEL_End_Assy_Overall_Height = {end_panel_calc_height:.3f}",
            f"[Inch]PANEL_End_Assy_Overall_Depth_Thickness = {end_panel_calc_depth:.3f}\n",

            f"[Inch]PANEL_Top_Assy_Overall_Width = {top_panel_calc_width:.3f}",
            f"[Inch]PANEL_Top_Assy_Overall_Length = {top_panel_calc_length:.3f}",
            f"[Inch]PANEL_Top_Assy_Overall_Depth_Thickness = {top_panel_calc_depth:.3f}\n",

            f"// --- FRONT PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]FP_Plywood_Width = {front_panel_components_data['plywood']['width']:.3f}",
            f"[Inch]FP_Plywood_Height = {front_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]FP_Plywood_Thickness = {front_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Horizontal Cleats (Top & Bottom)",
            f"[Inch]FP_Horizontal_Cleat_Length = {front_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]FP_Horizontal_Cleat_Material_Thickness = {front_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]FP_Horizontal_Cleat_Material_Member_Width = {front_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"FP_Horizontal_Cleat_Count = {front_panel_components_data['horizontal_cleats']['count']}\n",

            f"// Vertical Cleats (Left & Right)",
            f"[Inch]FP_Vertical_Cleat_Length = {front_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]FP_Vertical_Cleat_Material_Thickness = {front_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]FP_Vertical_Cleat_Material_Member_Width = {front_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"FP_Vertical_Cleat_Count = {front_panel_components_data['vertical_cleats']['count']}\n",
            
            f"// --- BACK PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]BP_Plywood_Width = {back_panel_components_data['plywood']['width']:.3f}",
            f"[Inch]BP_Plywood_Height = {back_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]BP_Plywood_Thickness = {back_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Horizontal Cleats (Top & Bottom)",
            f"[Inch]BP_Horizontal_Cleat_Length = {back_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]BP_Horizontal_Cleat_Material_Thickness = {back_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]BP_Horizontal_Cleat_Material_Member_Width = {back_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"BP_Horizontal_Cleat_Count = {back_panel_components_data['horizontal_cleats']['count']}\n",

            f"// Vertical Cleats (Left & Right)",
            f"[Inch]BP_Vertical_Cleat_Length = {back_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]BP_Vertical_Cleat_Material_Thickness = {back_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]BP_Vertical_Cleat_Material_Member_Width = {back_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"BP_Vertical_Cleat_Count = {back_panel_components_data['vertical_cleats']['count']}\n",

            f"// --- END PANEL COMPONENT DETAILS (for Left & Right panels) ---",
            f"// Plywood Sheathing",
            f"[Inch]EP_Plywood_Face_Width = {end_panel_components_data['plywood']['width']:.3f}",
            f"[Inch]EP_Plywood_Height = {end_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]EP_Plywood_Thickness = {end_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Vertical Cleats (Left & Right - run full height)",
            f"[Inch]EP_Vertical_Cleat_Length = {end_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]EP_Vertical_Cleat_Material_Thickness = {end_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]EP_Vertical_Cleat_Material_Member_Width = {end_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"EP_Vertical_Cleat_Count = {end_panel_components_data['vertical_cleats']['count']}\n",

            f"// Horizontal Cleats (Top & Bottom - fit between vertical cleats)",
            f"[Inch]EP_Horizontal_Cleat_Length = {end_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]EP_Horizontal_Cleat_Material_Thickness = {end_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]EP_Horizontal_Cleat_Material_Member_Width = {end_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"EP_Horizontal_Cleat_Count = {end_panel_components_data['horizontal_cleats']['count']}\n",

            f"// --- TOP PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]TP_Plywood_Width = {top_panel_components_data['plywood']['width']:.3f}", # Across crate width
            f"[Inch]TP_Plywood_Length = {top_panel_components_data['plywood']['length']:.3f}", # Along crate length
            f"[Inch]TP_Plywood_Thickness = {top_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Primary Cleats (e.g., along length)",
            f"[Inch]TP_Primary_Cleat_Length = {top_panel_components_data['primary_cleats']['length']:.3f}",
            f"[Inch]TP_Primary_Cleat_Material_Thickness = {top_panel_components_data['primary_cleats']['material_thickness']:.3f}",
            f"[Inch]TP_Primary_Cleat_Material_Member_Width = {top_panel_components_data['primary_cleats']['material_member_width']:.3f}",
            f"TP_Primary_Cleat_Count = {top_panel_components_data['primary_cleats']['count']}\n",

            f"// Secondary Cleats (e.g., across width, between primary)",
            f"[Inch]TP_Secondary_Cleat_Length = {top_panel_components_data['secondary_cleats']['length']:.3f}",
            f"[Inch]TP_Secondary_Cleat_Material_Thickness = {top_panel_components_data['secondary_cleats']['material_thickness']:.3f}",
            f"[Inch]TP_Secondary_Cleat_Material_Member_Width = {top_panel_components_data['secondary_cleats']['material_member_width']:.3f}",
            f"TP_Secondary_Cleat_Count = {top_panel_components_data['secondary_cleats']['count']}\n"
        ])
            
        expressions_content.append(f"// End of Expressions")

        with open(output_filename, "w") as f:
            for line in expressions_content: f.write(line + "\n")
        return True, f"Successfully generated: {output_filename}"
    except Exception as e:
        import traceback
        print(f"Error in logic: {e}\n{traceback.format_exc()}")
        return False, f"Error: {e}"

class CrateApp: 
    def __init__(self, master):
        self.master = master; master.title("NX Crate Exporter (Corrected Sandwich Logic)") 
        master.geometry("550x880") 
        style = ttk.Style(); style.theme_use('clam') 
        style.configure("TLabel", padding=3, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TEntry", padding=3, font=('Helvetica', 10))
        style.configure("TCheckbutton", padding=3, font=('Helvetica', 10))
        style.configure("TLabelframe.Label", font=('Helvetica', 10, 'bold'))
        master.configure(bg='#e1e1e1')

        main_frame = ttk.Frame(master, padding="10"); main_frame.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1); master.rowconfigure(0, weight=1)

        skid_frame = ttk.LabelFrame(main_frame, text="Skid Parameters", padding="10")
        skid_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew"); skid_frame.columnconfigure(1, weight=1)
        ttk.Label(skid_frame, text="Product Weight (lbs):").grid(row=0, column=0, sticky="w", pady=2); self.weight_entry = ttk.Entry(skid_frame, width=25); self.weight_entry.grid(row=0, column=1, sticky="ew", pady=2); self.weight_entry.insert(0,"300.0")
        ttk.Label(skid_frame, text="Product Length (in):").grid(row=1, column=0, sticky="w", pady=2); self.length_entry = ttk.Entry(skid_frame, width=25); self.length_entry.grid(row=1, column=1, sticky="ew", pady=2); self.length_entry.insert(0,"100.0")
        ttk.Label(skid_frame, text="Product Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.width_entry = ttk.Entry(skid_frame, width=25); self.width_entry.grid(row=2, column=1, sticky="ew", pady=2); self.width_entry.insert(0,"40.0")
        ttk.Label(skid_frame, text="Clearance per Side (in):").grid(row=3, column=0, sticky="w", pady=2); self.clearance_entry = ttk.Entry(skid_frame, width=25); self.clearance_entry.grid(row=3, column=1, sticky="ew", pady=2); self.clearance_entry.insert(0,"2.5")
        self.allow_3x4_skids_var = tk.BooleanVar(value=True) 
        self.allow_3x4_skids_cb = ttk.Checkbutton(skid_frame, text="Allow 3x4 Skids (for loads < 500 lbs)", variable=self.allow_3x4_skids_var)
        self.allow_3x4_skids_cb.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)

        general_frame = ttk.LabelFrame(main_frame, text="General Crate & Panel Parameters", padding="10") 
        general_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew"); general_frame.columnconfigure(1, weight=1)
        ttk.Label(general_frame, text="Panel Sheathing Thickness (in):").grid(row=0, column=0, sticky="w", pady=2); self.panel_thick_entry = ttk.Entry(general_frame, width=25); self.panel_thick_entry.grid(row=0, column=1, sticky="ew", pady=2); self.panel_thick_entry.insert(0,"0.25")
        ttk.Label(general_frame, text="Cleat Thickness (in):").grid(row=1, column=0, sticky="w", pady=2); self.cleat_thick_entry = ttk.Entry(general_frame, width=25); self.cleat_thick_entry.grid(row=1, column=1, sticky="ew", pady=2); self.cleat_thick_entry.insert(0,"0.75")
        ttk.Label(general_frame, text="Cleat Member Actual Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.cleat_member_width_entry = ttk.Entry(general_frame, width=25); self.cleat_member_width_entry.grid(row=2, column=1, sticky="ew", pady=2); self.cleat_member_width_entry.insert(0, str(DEFAULT_CLEAT_MEMBER_WIDTH)) # New GUI Entry
        ttk.Label(general_frame, text="Product Actual Height (in):").grid(row=3, column=0, sticky="w", pady=2); self.product_actual_height_entry = ttk.Entry(general_frame, width=25); self.product_actual_height_entry.grid(row=3, column=1, sticky="ew", pady=2); self.product_actual_height_entry.insert(0,"50.0")
        ttk.Label(general_frame, text="Clearance Above Product (in):").grid(row=4, column=0, sticky="w", pady=2); self.clearance_above_product_entry = ttk.Entry(general_frame, width=25); self.clearance_above_product_entry.grid(row=4, column=1, sticky="ew", pady=2); self.clearance_above_product_entry.insert(0,"2.0")
        ttk.Label(general_frame, text="Ground Clearance (End Panels, in):").grid(row=5, column=0, sticky="w", pady=2); self.ground_clearance_entry = ttk.Entry(general_frame, width=25); self.ground_clearance_entry.grid(row=5, column=1, sticky="ew", pady=2); self.ground_clearance_entry.insert(0,"1.0")
        
        floor_frame = ttk.LabelFrame(main_frame, text="Floorboard Parameters", padding="10")
        floor_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew"); floor_frame.columnconfigure(1, weight=1); floor_frame.columnconfigure(0, weight=0) 
        ttk.Label(floor_frame, text="Floorboard Actual Thickness (in):").grid(row=0, column=0, sticky="w", pady=2); self.fb_thickness_entry = ttk.Entry(floor_frame, width=25); self.fb_thickness_entry.grid(row=0, column=1, sticky="ew", pady=2); self.fb_thickness_entry.insert(0,"1.5")
        ttk.Label(floor_frame, text="Max Allowable Middle Gap (in):").grid(row=1, column=0, sticky="w", pady=2); self.fb_max_gap_entry = ttk.Entry(floor_frame, width=25); self.fb_max_gap_entry.grid(row=1, column=1, sticky="ew", pady=2); self.fb_max_gap_entry.insert(0, str(DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP))
        ttk.Label(floor_frame, text="Min Custom Board Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.fb_min_custom_entry = ttk.Entry(floor_frame, width=25); self.fb_min_custom_entry.grid(row=2, column=1, sticky="ew", pady=2); self.fb_min_custom_entry.insert(0, str(DEFAULT_MIN_CUSTOM_LUMBER_WIDTH))
        self.force_small_custom_var = tk.BooleanVar(value=False) 
        self.force_small_custom_cb = ttk.Checkbutton(floor_frame, text=f"Force small custom board for tiny gap ({MIN_FORCEABLE_CUSTOM_BOARD_WIDTH}\" - {DEFAULT_MIN_CUSTOM_LUMBER_WIDTH}\")", variable=self.force_small_custom_var)
        self.force_small_custom_cb.grid(row=3, column=0, columnspan=2, sticky="w", pady=4)
        lumber_select_frame = ttk.LabelFrame(floor_frame, text="Available Standard Lumber (Actual Widths)", padding="5")
        lumber_select_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew") 
        self.lumber_vars = {}
        max_cols = 2 
        for i, (desc, width_val) in enumerate(DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS.items()): 
            var = tk.BooleanVar(value=True); cb = ttk.Checkbutton(lumber_select_frame, text=desc, variable=var)
            cb.grid(row=i // max_cols, column=i % max_cols, sticky="w", padx=5, pady=2); self.lumber_vars[width_val] = var
            lumber_select_frame.columnconfigure(i % max_cols, weight=1)

        self.generate_button = ttk.Button(main_frame, text="Generate Expressions File", command=self.generate_file)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=20) 
        main_frame.columnconfigure(0, weight=1)

    def generate_file(self): 
        try:
            weight = float(self.weight_entry.get()); length = float(self.length_entry.get()); width = float(self.width_entry.get())   
            clearance = float(self.clearance_entry.get()); allow_3x4 = self.allow_3x4_skids_var.get() 
            panel_thick = float(self.panel_thick_entry.get()); cleat_thick = float(self.cleat_thick_entry.get())
            cleat_member_w = float(self.cleat_member_width_entry.get()) # Get new input
            prod_actual_height = float(self.product_actual_height_entry.get()); clear_above_prod = float(self.clearance_above_product_entry.get())
            ground_clear = float(self.ground_clearance_entry.get())
            fb_thickness = float(self.fb_thickness_entry.get()); fb_max_gap = float(self.fb_max_gap_entry.get())
            fb_min_custom = float(self.fb_min_custom_entry.get()); force_small_custom = self.force_small_custom_var.get()
            selected_lumber = [w for w, v in self.lumber_vars.items() if v.get()]
            if not selected_lumber: messagebox.showerror("Input Error", "Select lumber."); return
        except ValueError: messagebox.showerror("Error", "Invalid number."); return
        
        output_filename = filedialog.asksaveasfilename(defaultextension=".exp", initialfile="Crate_Final_With_Panels.exp")
        if not output_filename: return

        success, message = generate_crate_expressions_logic(
            product_weight_lbs=weight, product_length_in=length, product_width_in=width, 
            clearance_each_side_in=clearance, allow_3x4_skids_bool=allow_3x4, 
            panel_thickness_in=panel_thick, cleat_thickness_in=cleat_thick, 
            cleat_member_actual_width_in=cleat_member_w, # Pass new input
            product_actual_height_in=prod_actual_height, clearance_above_product_in=clear_above_prod,
            ground_clearance_in=ground_clear,
            floorboard_actual_thickness_in=fb_thickness, selected_std_lumber_widths=selected_lumber, 
            max_allowable_middle_gap_in=fb_max_gap, 
            min_custom_lumber_width_in=fb_min_custom,
            force_small_custom_board_bool=force_small_custom,
            output_filename=output_filename)
        if success: messagebox.showinfo("Success", message)
        else: messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk(); app = CrateApp(root); root.mainloop()
