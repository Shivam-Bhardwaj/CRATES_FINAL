import datetime
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- Default Constants ---
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = { 
    "2x6 (5.5 in)": 5.5,
    "2x8 (7.25 in)": 7.25,
    "2x10 (9.25 in)": 9.25,
    "2x12 (11.25 in)": 11.25
}
DEFAULT_MIN_CUSTOM_LUMBER_WIDTH = 2.5
DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP = 0.25
MAX_NX_FLOORBOARD_INSTANCES = 20

def generate_crate_expressions_logic( # Renamed from generate_skid_expressions_logic
    # Skid Inputs
    product_weight_lbs: float,
    product_length_in: float,
    product_width_in: float,
    clearance_each_side_in: float,
    allow_3x4_skids_bool: bool,
    # General Crate Inputs (for floorboard end gaps)
    panel_thickness_in: float,
    cleat_thickness_in: float,
    # Floorboard Inputs
    floorboard_actual_thickness_in: float,
    selected_std_lumber_widths: list[float], 
    max_allowable_middle_gap_in: float,
    min_custom_lumber_width_in: float,
    # Output
    output_filename: str
) -> tuple[bool, str]:
    """
    Core logic to generate NX expressions for skids and advanced floorboard layout.
    """
    try:
        # --- Input Validations ---
        if product_weight_lbs < 0: return False, "Product weight cannot be negative."
        if product_length_in <=0: return False, "Product length must be positive."
        if product_width_in <=0: return False, "Product width must be positive."
        if clearance_each_side_in < 0: return False, "Clearance cannot be negative."
        if panel_thickness_in <=0: return False, "Panel thickness must be positive."
        if cleat_thickness_in <=0: return False, "Cleat thickness must be positive."
        if floorboard_actual_thickness_in <=0: return False, "Floorboard thickness must be positive."
        if not selected_std_lumber_widths: return False, "At least one standard lumber width must be selected for floorboards."
        if max_allowable_middle_gap_in < 0: return False, "Max middle gap cannot be negative."
        if min_custom_lumber_width_in <= 0: return False, "Min custom lumber width must be positive."
        
        # === SKID CALCULATIONS (UNCHANGED FROM PREVIOUS WORKING VERSION) ===
        skid_actual_height_in: float; skid_actual_width_in: float; lumber_callout: str; max_skid_spacing_rule_in: float
        use_3x4_for_light_load = allow_3x4_skids_bool and product_weight_lbs < 500
        if use_3x4_for_light_load:
            skid_actual_height_in = 3.5; skid_actual_width_in = 2.5
            lumber_callout = "3x4 (oriented for 3.5 H)"; max_skid_spacing_rule_in = 30.0
        elif product_weight_lbs < 4500:
            skid_actual_height_in = 3.5; skid_actual_width_in = 3.5
            lumber_callout = "4x4"; max_skid_spacing_rule_in = 30.0
        elif 4500 <= product_weight_lbs <= 20000:
            skid_actual_height_in = 3.5; skid_actual_width_in = 5.5
            lumber_callout = "4x6"; max_skid_spacing_rule_in = 24.0
        else:
            skid_actual_height_in = 3.5; skid_actual_width_in = 5.5
            lumber_callout = "4x6 (defaulted due to weight)"; max_skid_spacing_rule_in = 24.0
        
        skid_model_length_in = product_length_in + (2 * clearance_each_side_in)
        crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in)
        crate_overall_length_od_in = skid_model_length_in
        calc_skid_count: int; calc_skid_pitch_in: float; calc_first_skid_pos_x_in: float
        if crate_overall_width_od_in <= skid_actual_width_in:
            calc_skid_count = 1; calc_skid_pitch_in = 0.0; calc_first_skid_pos_x_in = 0.0
        else:
            num_skids_float = (crate_overall_width_od_in - skid_actual_width_in) / max_skid_spacing_rule_in
            calc_skid_count = math.ceil(num_skids_float) + 1
            if calc_skid_count < 2: calc_skid_count = 2
            if calc_skid_count <= 1: calc_skid_pitch_in = 0.0
            else: calc_skid_pitch_in = (crate_overall_width_od_in - skid_actual_width_in) / (calc_skid_count - 1)
            total_centerline_span = (calc_skid_count - 1) * calc_skid_pitch_in
            calc_first_skid_pos_x_in = -total_centerline_span / 2.0
        x_master_skid_origin_offset_in = calc_first_skid_pos_x_in - (skid_actual_width_in / 2.0)
        # === END OF SKID CALCULATIONS ===

        # === FLOORBOARD CALCULATIONS (RE-INTEGRATED MIDDLE GAP LOGIC) ===
        fb_actual_length_in = crate_overall_width_od_in 
        fb_actual_thickness_in = floorboard_actual_thickness_in
        cap_end_gap_each_side = panel_thickness_in + cleat_thickness_in
        fb_usable_coverage_y_in = skid_model_length_in - (2 * cap_end_gap_each_side) 
        fb_initial_start_y_offset_abs = cap_end_gap_each_side 
        sorted_selected_std_lumber_widths = sorted(selected_std_lumber_widths, reverse=True)
        temp_boards_list = []; current_filled_width = 0.0; space_left_to_fill = fb_usable_coverage_y_in
        while True: 
            board_found_this_pass = False
            for std_width in sorted_selected_std_lumber_widths:
                if std_width <= space_left_to_fill + 0.001: 
                    temp_boards_list.append(std_width); current_filled_width += std_width
                    space_left_to_fill -= std_width; board_found_this_pass = True; break
            if not board_found_this_pass: break
        custom_board_width = 0.0 
        if space_left_to_fill >= min_custom_lumber_width_in - 0.001:
            custom_board_width = space_left_to_fill
            temp_boards_list.append(custom_board_width); current_filled_width += custom_board_width
        total_lumber_width_placed = current_filled_width
        actual_middle_gap = fb_usable_coverage_y_in - total_lumber_width_placed
        if not (0.001 < actual_middle_gap <= max_allowable_middle_gap_in): actual_middle_gap = 0.0
        floorboards_data = []; current_y_pos = fb_initial_start_y_offset_abs; num_boards_total = len(temp_boards_list); gap_placed = False
        boards_in_first_group = math.ceil(num_boards_total / 2.0) if actual_middle_gap > 0.001 and num_boards_total > 1 else num_boards_total
        for i, board_w in enumerate(temp_boards_list):
            floorboards_data.append({'width': board_w, 'y_pos': current_y_pos})
            current_y_pos += board_w
            if actual_middle_gap > 0.001 and (i + 1) == boards_in_first_group and (i + 1) < num_boards_total:
                current_y_pos += actual_middle_gap; gap_placed = True
        final_floor_gap_debug_val = fb_usable_coverage_y_in - (sum(b['width'] for b in floorboards_data) + (actual_middle_gap if gap_placed else 0))
        # === END OF FLOORBOARD CALCULATIONS ===

        # --- Prepare expressions file content ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expressions_content = [
            f"// NX Expressions - Skids & Floorboards (Dimensions for BOM)",
            f"// Generated: {timestamp}\n",
            f"// --- USER INPUTS & CRATE CONSTANTS ---",
            f"[lbm]product_weight = {product_weight_lbs:.3f}",
            f"[Inch]product_length_input = {product_length_in:.3f}",
            f"[Inch]product_width_input = {product_width_in:.3f}", 
            f"[Inch]clearance_side_input = {clearance_each_side_in:.3f}", 
            f"BOOL_Allow_3x4_Skids_Input = {1 if allow_3x4_skids_bool else 0}", # For reference
            f"[Inch]INPUT_Panel_Thickness = {panel_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Thickness = {cleat_thickness_in:.3f}",
            f"[Inch]INPUT_Floorboard_Actual_Thickness = {floorboard_actual_thickness_in:.3f}",
            f"[Inch]INPUT_Max_Allowable_Middle_Gap = {max_allowable_middle_gap_in:.3f}",
            f"[Inch]INPUT_Min_Custom_Lumber_Width = {min_custom_lumber_width_in:.3f}\n",
            f"// --- CALCULATED CRATE DIMENSIONS ---",
            f"[Inch]crate_overall_width_OD = {crate_overall_width_od_in:.3f}",
            f"[Inch]crate_overall_length_OD = {crate_overall_length_od_in:.3f}",
            f"[Inch]CALC_FB_Cap_End_Gap_Each_Side = {cap_end_gap_each_side:.3f}", # For reference
            f"[Inch]CALC_FB_Usable_Coverage_Y = {fb_usable_coverage_y_in:.3f}",   # For reference
            f"[Inch]CALC_FB_Start_Y_Offset_Abs = {fb_initial_start_y_offset_abs:.3f}\n",
            f"// --- SKID PARAMETERS ---",
            f"// Skid Lumber Callout: {lumber_callout}",
            f"[Inch]Skid_Actual_Height = {skid_actual_height_in:.3f}",
            f"[Inch]Skid_Actual_Width = {skid_actual_width_in:.3f}",
            f"[Inch]Skid_Actual_Length = {skid_model_length_in:.3f}",
            f"[Inch]RULE_Max_Skid_Spacing_Applied = {max_skid_spacing_rule_in:.3f}", # For reference
            f"CALC_Skid_Count = {calc_skid_count}",
            f"[Inch]CALC_Skid_Pitch = {calc_skid_pitch_in:.4f}",
            f"[Inch]CALC_First_Skid_Pos_X = {calc_first_skid_pos_x_in:.4f}", # For reference
            f"[Inch]X_Master_Skid_Origin_Offset = {x_master_skid_origin_offset_in:.4f}\n",
            
            f"// --- FLOORBOARD PARAMETERS ---",
            f"[Inch]FB_Board_Actual_Length = {fb_actual_length_in:.3f}",
            f"[Inch]FB_Board_Actual_Thickness = {fb_actual_thickness_in:.3f}",
            f"[Inch]CALC_FB_Actual_Middle_Gap = {actual_middle_gap:.4f}",
            f"[Inch]DEBUG_FB_Final_Unused_Space = {final_floor_gap_debug_val:.4f}\n"
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
            expressions_content.append("")
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
        self.master = master; master.title("NX Crate Exporter (Skids & Floor - Dimensions for BOM)") 
        master.geometry("550x750") 
        style = ttk.Style(); style.theme_use('clam') 
        style.configure("TLabel", padding=3, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TEntry", padding=3, font=('Helvetica', 10))
        style.configure("TCheckbutton", padding=3, font=('Helvetica', 10))
        style.configure("TLabelframe.Label", font=('Helvetica', 10, 'bold'))
        master.configure(bg='#e1e1e1')

        main_frame = ttk.Frame(master, padding="10"); main_frame.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1); master.rowconfigure(0, weight=1)

        # --- Skid Parameters Frame ---
        skid_frame = ttk.LabelFrame(main_frame, text="Skid Parameters", padding="10")
        skid_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew"); skid_frame.columnconfigure(1, weight=1)
        
        ttk.Label(skid_frame, text="Product Weight (lbs):").grid(row=0, column=0, sticky="w", pady=2)
        self.weight_entry = ttk.Entry(skid_frame, width=25); self.weight_entry.grid(row=0, column=1, sticky="ew", pady=2); self.weight_entry.insert(0,"300.0")
        
        ttk.Label(skid_frame, text="Product Length (in):").grid(row=1, column=0, sticky="w", pady=2)
        self.length_entry = ttk.Entry(skid_frame, width=25); self.length_entry.grid(row=1, column=1, sticky="ew", pady=2); self.length_entry.insert(0,"100.0")
        
        ttk.Label(skid_frame, text="Product Width (in):").grid(row=2, column=0, sticky="w", pady=2)
        self.width_entry = ttk.Entry(skid_frame, width=25); self.width_entry.grid(row=2, column=1, sticky="ew", pady=2); self.width_entry.insert(0,"40.0")
        
        ttk.Label(skid_frame, text="Clearance per Side (in):").grid(row=3, column=0, sticky="w", pady=2)
        self.clearance_entry = ttk.Entry(skid_frame, width=25); self.clearance_entry.grid(row=3, column=1, sticky="ew", pady=2); self.clearance_entry.insert(0,"2.5")

        self.allow_3x4_skids_var = tk.BooleanVar(value=True) 
        self.allow_3x4_skids_cb = ttk.Checkbutton(skid_frame, text="Allow 3x4 Skids (for loads < 500 lbs)", variable=self.allow_3x4_skids_var)
        self.allow_3x4_skids_cb.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)

        # --- General Crate Parameters Frame ---
        general_frame = ttk.LabelFrame(main_frame, text="General Crate Parameters", padding="10")
        general_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew"); general_frame.columnconfigure(1, weight=1)
        ttk.Label(general_frame, text="Panel Thickness (in):").grid(row=0, column=0, sticky="w", pady=2); self.panel_thick_entry = ttk.Entry(general_frame, width=25); self.panel_thick_entry.grid(row=0, column=1, sticky="ew", pady=2); self.panel_thick_entry.insert(0,"0.25")
        ttk.Label(general_frame, text="Cleat Thickness (in):").grid(row=1, column=0, sticky="w", pady=2); self.cleat_thick_entry = ttk.Entry(general_frame, width=25); self.cleat_thick_entry.grid(row=1, column=1, sticky="ew", pady=2); self.cleat_thick_entry.insert(0,"0.75")
        
        # --- Floorboard Parameters Frame ---
        floor_frame = ttk.LabelFrame(main_frame, text="Floorboard Parameters", padding="10")
        floor_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew"); floor_frame.columnconfigure(1, weight=1); floor_frame.columnconfigure(0, weight=0) 
        ttk.Label(floor_frame, text="Floorboard Actual Thickness (in):").grid(row=0, column=0, sticky="w", pady=2); self.fb_thickness_entry = ttk.Entry(floor_frame, width=25); self.fb_thickness_entry.grid(row=0, column=1, sticky="ew", pady=2); self.fb_thickness_entry.insert(0,"1.5")
        ttk.Label(floor_frame, text="Max Allowable Middle Gap (in):").grid(row=1, column=0, sticky="w", pady=2); self.fb_max_gap_entry = ttk.Entry(floor_frame, width=25); self.fb_max_gap_entry.grid(row=1, column=1, sticky="ew", pady=2); self.fb_max_gap_entry.insert(0, str(DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP))
        ttk.Label(floor_frame, text="Min Custom Board Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.fb_min_custom_entry = ttk.Entry(floor_frame, width=25); self.fb_min_custom_entry.grid(row=2, column=1, sticky="ew", pady=2); self.fb_min_custom_entry.insert(0, str(DEFAULT_MIN_CUSTOM_LUMBER_WIDTH))

        lumber_select_frame = ttk.LabelFrame(floor_frame, text="Available Standard Lumber (Actual Widths)", padding="5")
        lumber_select_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        self.lumber_vars = {}
        max_cols = 2 
        for i, (desc, width_val) in enumerate(DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS.items()): 
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(lumber_select_frame, text=desc, variable=var)
            cb.grid(row=i // max_cols, column=i % max_cols, sticky="w", padx=5, pady=2); self.lumber_vars[width_val] = var
            lumber_select_frame.columnconfigure(i % max_cols, weight=1)

        self.generate_button = ttk.Button(main_frame, text="Generate Expressions File", command=self.generate_file)
        self.generate_button.grid(row=4, column=0, columnspan=2, pady=20) 
        main_frame.columnconfigure(0, weight=1)

    def generate_file(self):
        try:
            weight = float(self.weight_entry.get())
            length = float(self.length_entry.get())
            width = float(self.width_entry.get())   
            clearance = float(self.clearance_entry.get()) 
            allow_3x4 = self.allow_3x4_skids_var.get() 
            panel_thick = float(self.panel_thick_entry.get())
            cleat_thick = float(self.cleat_thick_entry.get())
            fb_thickness = float(self.fb_thickness_entry.get())
            fb_max_gap = float(self.fb_max_gap_entry.get())
            fb_min_custom = float(self.fb_min_custom_entry.get())
            selected_lumber = [w for w, v in self.lumber_vars.items() if v.get()]
            if not selected_lumber: messagebox.showerror("Input Error", "Select lumber."); return
        except ValueError: messagebox.showerror("Error", "Invalid number."); return
        
        output_filename = filedialog.asksaveasfilename(defaultextension=".exp", initialfile="Crate_SkidsAndFloor.exp")
        if not output_filename: return

        success, message = generate_crate_expressions_logic(
            product_weight_lbs=weight, product_length_in=length, product_width_in=width, 
            clearance_each_side_in=clearance, 
            allow_3x4_skids_bool=allow_3x4, 
            panel_thickness_in=panel_thick, 
            cleat_thickness_in=cleat_thick, floorboard_actual_thickness_in=fb_thickness, 
            selected_std_lumber_widths=selected_lumber, 
            max_allowable_middle_gap_in=fb_max_gap, 
            min_custom_lumber_width_in=fb_min_custom,
            output_filename=output_filename)
        if success: messagebox.showinfo("Success", message)
        else: messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk(); app = CrateApp(root); root.mainloop()
