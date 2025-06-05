import datetime
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- Default Constants (can be overridden by GUI inputs where applicable) ---
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = { # Description: Actual Width
    "1x6 (5.5 in)": 5.5,
    "1x8 (7.25 in)": 7.25,
    "1x10 (9.25 in)": 9.25,
    "1x12 (11.25 in)": 11.25
}
DEFAULT_MIN_RIP_LUMBER_WIDTH = 2.5
DEFAULT_MAX_ALLOWABLE_INTER_FB_GAP = 0.25
MAX_NX_FLOORBOARD_INSTANCES = 20 # Max number of floorboard instances for NX

def generate_crate_expressions_logic( # Renamed from generate_skid_expressions_logic
    # Skid Inputs
    product_weight_lbs: float,
    product_length_in: float,
    product_width_in: float,
    clearance_each_side_in: float,
    # General Crate Inputs (new for floorboard end gaps)
    panel_thickness_in: float,
    cleat_thickness_in: float,
    # Floorboard Inputs (new)
    floorboard_actual_thickness_in: float,
    selected_std_lumber_widths: list[float], 
    max_allowable_inter_fb_gap_in: float,
    min_rip_lumber_width_in: float,
    # Output
    output_filename: str
) -> tuple[bool, str]:
    """
    Core logic to generate NX expressions for skids and advanced floorboard layout.
    """
    try:
        # --- Input Validations ---
        if product_weight_lbs < 0: return False, "Product weight cannot be negative."
        if panel_thickness_in <=0: return False, "Panel thickness must be positive."
        if cleat_thickness_in <=0: return False, "Cleat thickness must be positive."
        if floorboard_actual_thickness_in <=0: return False, "Floorboard thickness must be positive."
        if not selected_std_lumber_widths: return False, "At least one standard lumber width must be selected for floorboards."
        if max_allowable_inter_fb_gap_in < 0: return False, "Max inter-board gap cannot be negative."
        if min_rip_lumber_width_in <= 0: return False, "Min rip lumber width must be positive."
        
        # === SKID CALCULATIONS (EXISTING LOGIC - UNCHANGED) ===
        skid_actual_height_in: float
        skid_actual_width_in: float
        lumber_callout: str
        max_skid_spacing_rule_in: float

        if product_weight_lbs < 500:
            skid_actual_height_in = 3.5 
            skid_actual_width_in = 2.5  
            lumber_callout = "3x4 (oriented for 3.5 H)"
            max_skid_spacing_rule_in = 30.0
        elif 500 <= product_weight_lbs <= 4500:
            skid_actual_height_in = 3.5  
            skid_actual_width_in = 3.5   
            lumber_callout = "4x4"
            max_skid_spacing_rule_in = 30.0
        elif 4500 < product_weight_lbs <= 20000:
            skid_actual_height_in = 3.5  
            skid_actual_width_in = 5.5   
            lumber_callout = "4x6"
            max_skid_spacing_rule_in = 24.0
        else: 
            print(f"Warning: Product weight {product_weight_lbs} lbs is outside the 0-20000 lbs range. Using 4x6 specs.")
            skid_actual_height_in = 3.5
            skid_actual_width_in = 5.5
            lumber_callout = "4x6 (defaulted due to weight)"
            max_skid_spacing_rule_in = 24.0

        skid_model_length_in = product_length_in + (2 * clearance_each_side_in)
        crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in)
        crate_overall_length_od_in = skid_model_length_in

        calc_skid_count: int
        calc_skid_pitch_in: float
        calc_first_skid_pos_x_in: float

        if crate_overall_width_od_in <= skid_actual_width_in:
            calc_skid_count = 1
            calc_skid_pitch_in = 0.0
            calc_first_skid_pos_x_in = 0.0
        else:
            num_skids_float = (crate_overall_width_od_in - skid_actual_width_in) / max_skid_spacing_rule_in
            calc_skid_count = math.ceil(num_skids_float) + 1
            if calc_skid_count < 2:
                 calc_skid_count = 2
            if calc_skid_count <= 1:
                calc_skid_pitch_in = 0.0 
            else:
                calc_skid_pitch_in = (crate_overall_width_od_in - skid_actual_width_in) / (calc_skid_count - 1)
            total_centerline_span = (calc_skid_count - 1) * calc_skid_pitch_in
            calc_first_skid_pos_x_in = -total_centerline_span / 2.0
        x_master_skid_origin_offset_in = calc_first_skid_pos_x_in - (skid_actual_width_in / 2.0)
        # === END OF SKID CALCULATIONS ===

        # === ADVANCED FLOORBOARD CALCULATIONS (NEW LOGIC) ===
        fb_actual_length_in = crate_overall_width_od_in # Length of each floorboard (spans across skids)
        fb_actual_thickness_in = floorboard_actual_thickness_in
        
        cap_end_gap_each_side = panel_thickness_in + cleat_thickness_in
        fb_usable_coverage_y_in = skid_model_length_in - (2 * cap_end_gap_each_side) # Y-span floorboards must cover
        fb_start_y_offset_abs = cap_end_gap_each_side # Y-Position of the first floorboard's leading edge

        # Sort selected lumber widths from largest to smallest for the placement strategy
        sorted_selected_std_lumber_widths = sorted(selected_std_lumber_widths, reverse=True)

        floorboards_data = [] # List to store dicts: {'width': float, 'y_pos': float}
        current_y_pos = fb_start_y_offset_abs
        remaining_coverage_y = fb_usable_coverage_y_in

        # Iteratively place floorboards
        while remaining_coverage_y > min_rip_lumber_width_in - 0.001: # Loop while there's significant space
            placed_board_this_iteration = False
            # Try to place largest available standard lumber from the selected list
            for std_width in sorted_selected_std_lumber_widths:
                if std_width <= remaining_coverage_y + 0.001: # Check if standard board fits
                    floorboards_data.append({'width': std_width, 'y_pos': current_y_pos})
                    current_y_pos += std_width
                    remaining_coverage_y -= std_width
                    placed_board_this_iteration = True
                    # Add gap if there's more space to cover significantly
                    if remaining_coverage_y > min_rip_lumber_width_in - 0.001:
                        # Determine gap: it shouldn't make remaining space smaller than min_rip_width, unless remaining is already very small
                        potential_gap_before_next_board = remaining_coverage_y - min_rip_lumber_width_in
                        gap_to_add = min(max_allowable_inter_fb_gap_in, potential_gap_before_next_board if potential_gap_before_next_board > 0 else 0)
                        
                        # Only add gap if it's positive and makes sense
                        if gap_to_add > 0.001 and \
                           (remaining_coverage_y - gap_to_add >= min_rip_lumber_width_in - 0.001 or remaining_coverage_y - gap_to_add < 0.001): # if remaining after gap is still ok or very small
                             current_y_pos += gap_to_add
                             remaining_coverage_y -= gap_to_add
                        elif remaining_coverage_y < min_rip_lumber_width_in and remaining_coverage_y > 0.001 and max_allowable_inter_fb_gap_in > 0.001 : # if remaining is small, try to fill with gap
                            gap_to_add = min(max_allowable_inter_fb_gap_in, remaining_coverage_y)
                            current_y_pos += gap_to_add
                            remaining_coverage_y -= gap_to_add
                    break # Placed a std board, move to next position
            
            if placed_board_this_iteration:
                continue

            # If no standard board fit, try to place a custom rip board
            if remaining_coverage_y >= min_rip_lumber_width_in - 0.001:
                # Rip width cannot be wider than the widest selected standard lumber (or min_rip if no std selected, though validated earlier)
                max_std_width_available = max(sorted_selected_std_lumber_widths) if sorted_selected_std_lumber_widths else min_rip_lumber_width_in
                
                rip_width = max(min_rip_lumber_width_in, remaining_coverage_y) # Ensure it's at least min rip
                rip_width = min(rip_width, max_std_width_available) # Constrain to max available std width
                
                floorboards_data.append({'width': rip_width, 'y_pos': current_y_pos})
                current_y_pos += rip_width # No gap after the final custom board
                remaining_coverage_y -= rip_width
                placed_board_this_iteration = True

            if not placed_board_this_iteration: 
                # This should ideally not be reached if remaining_coverage_y is substantial
                # It means no standard or rip board could be placed.
                break 
        
        final_floor_gap_debug = remaining_coverage_y # This should be very small or zero
        # === END OF FLOORBOARD CALCULATIONS ===

        # --- Prepare expressions file content ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expressions_content = [
            f"// NX Expressions for Crate Design - Skids & Floorboards",
            f"// Generated by Python script at: {timestamp}\n",
            
            f"// =======================================================",
            f"// 1. USER INPUTS & CRATE CONSTANTS",
            f"// =======================================================",
            f"[lbm]product_weight = {product_weight_lbs:.3f}",
            f"[Inch]product_length_input = {product_length_in:.3f}",
            f"[Inch]product_width_input = {product_width_in:.3f}",
            f"[Inch]clearance_side_input = {clearance_each_side_in:.3f}",
            f"[Inch]INPUT_Panel_Thickness = {panel_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Thickness = {cleat_thickness_in:.3f}",
            f"[Inch]INPUT_Floorboard_Actual_Thickness = {floorboard_actual_thickness_in:.3f}",
            f"[Inch]INPUT_Max_Allowable_Inter_FB_Gap = {max_allowable_inter_fb_gap_in:.3f}",
            f"[Inch]INPUT_Min_Rip_Lumber_Width = {min_rip_lumber_width_in:.3f}",
            f"// Selected Standard Lumber Widths (Actual, Inches): {', '.join(map(str, sorted_selected_std_lumber_widths))}\n",

            f"// =======================================================",
            f"// 2. CALCULATED CRATE OUTER & USABLE DIMENSIONS",
            f"// =======================================================",
            f"[Inch]crate_overall_width_OD = {crate_overall_width_od_in:.3f}",
            f"[Inch]crate_overall_length_OD = {crate_overall_length_od_in:.3f}",
            f"[Inch]CALC_FB_Cap_End_Gap_Each_Side = {cap_end_gap_each_side:.3f}",
            f"[Inch]CALC_FB_Usable_Coverage_Y = {fb_usable_coverage_y_in:.3f}",
            f"[Inch]CALC_FB_Start_Y_Offset_Abs = {fb_start_y_offset_abs:.3f}\n",
            
            f"// =======================================================",
            f"// 3. SKID COMPONENT & LAYOUT PARAMETERS",
            f"// =======================================================",
            f"// Skid Lumber Callout: {lumber_callout}",
            f"[Inch]Skid_Actual_Height = {skid_actual_height_in:.3f}",
            f"[Inch]Skid_Actual_Width = {skid_actual_width_in:.3f}",
            f"[Inch]Skid_Actual_Length = {skid_model_length_in:.3f}",
            f"[Inch]RULE_Max_Skid_Spacing_Applied = {max_skid_spacing_rule_in:.3f}",
            f"CALC_Skid_Count = {calc_skid_count}",
            f"[Inch]CALC_Skid_Pitch = {calc_skid_pitch_in:.4f}",
            f"[Inch]CALC_First_Skid_Pos_X = {calc_first_skid_pos_x_in:.4f}", # For reference
            f"[Inch]X_Master_Skid_Origin_Offset = {x_master_skid_origin_offset_in:.4f}\n",

            f"// =======================================================",
            f"// 4. FLOORBOARD PARAMETERS (for N-Instance Suppression Strategy)",
            f"// =======================================================",
            f"[Inch]FB_Board_Actual_Length = {fb_actual_length_in:.3f} // Length of all floorboards (across skids)",
            f"[Inch]FB_Board_Actual_Thickness = {fb_actual_thickness_in:.3f} // Thickness of all floorboards",
            f"[Inch]DEBUG_FB_Final_Unused_Gap = {final_floor_gap_debug:.4f}\n"
        ]

        # Add expressions for each potential floorboard instance
        for i in range(MAX_NX_FLOORBOARD_INSTANCES):
            instance_num = i + 1
            if i < len(floorboards_data):
                board = floorboards_data[i]
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 0 // Use this board")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = {board['width']:.4f}")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = {board['y_pos']:.4f} // Leading Edge Y")
            else: # Instances not used by the current calculation
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 1 // Suppress this board")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = 0.0001") # Nominal small value for suppressed
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = 0.0000")
            expressions_content.append("") # Add a blank line for readability

        expressions_content.append(f"// End of AutoCrate Wizard Expressions")

        # Write to the output file
        with open(output_filename, "w") as f:
            for line in expressions_content:
                f.write(line + "\n")
        return True, f"Successfully generated expressions file: {output_filename}"

    except ValueError as ve: # Catch specific conversion errors
        return False, f"Input Error: {ve}. Please enter valid numbers."
    except Exception as e:
        # It's good to log the full error for debugging
        import traceback
        print(f"An unexpected error occurred in logic: {e}\n{traceback.format_exc()}")
        return False, f"An unexpected error occurred: {e}"


class CrateApp:
    def __init__(self, master):
        self.master = master
        master.title("NX Crate Expression Generator (Skids & Floor)")
        master.geometry("520x700") # Adjusted height for new fields

        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("TLabel", padding=3, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TEntry", padding=3, font=('Helvetica', 10))
        style.configure("TCheckbutton", padding=3, font=('Helvetica', 10))
        style.configure("TLabelframe.Label", font=('Helvetica', 10, 'bold')) # For LabelFrame titles
        master.configure(bg='#e1e1e1')

        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1); master.rowconfigure(0, weight=1)

        # --- Skid Inputs Section (Existing) ---
        skid_frame = ttk.LabelFrame(main_frame, text="Skid Parameters", padding="10")
        skid_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        skid_frame.columnconfigure(1, weight=1) 
        ttk.Label(skid_frame, text="Product Weight (lbs):").grid(row=0, column=0, sticky="w", pady=2)
        self.weight_entry = ttk.Entry(skid_frame, width=25); self.weight_entry.grid(row=0, column=1, sticky="ew", pady=2); self.weight_entry.insert(0, "300.0")
        ttk.Label(skid_frame, text="Product Length (in):").grid(row=1, column=0, sticky="w", pady=2)
        self.length_entry = ttk.Entry(skid_frame, width=25); self.length_entry.grid(row=1, column=1, sticky="ew", pady=2); self.length_entry.insert(0, "100.0")
        ttk.Label(skid_frame, text="Product Width (in):").grid(row=2, column=0, sticky="w", pady=2)
        self.width_entry = ttk.Entry(skid_frame, width=25); self.width_entry.grid(row=2, column=1, sticky="ew", pady=2); self.width_entry.insert(0, "40.0")
        ttk.Label(skid_frame, text="Clearance per Side (in):").grid(row=3, column=0, sticky="w", pady=2)
        self.clearance_entry = ttk.Entry(skid_frame, width=25); self.clearance_entry.grid(row=3, column=1, sticky="ew", pady=2); self.clearance_entry.insert(0, "2.5")

        # --- General Crate Inputs Section (New) ---
        general_frame = ttk.LabelFrame(main_frame, text="General Crate Parameters", padding="10")
        general_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        general_frame.columnconfigure(1, weight=1)
        ttk.Label(general_frame, text="Panel Thickness (in):").grid(row=0, column=0, sticky="w", pady=2)
        self.panel_thick_entry = ttk.Entry(general_frame, width=25); self.panel_thick_entry.grid(row=0, column=1, sticky="ew", pady=2); self.panel_thick_entry.insert(0, "0.25")
        ttk.Label(general_frame, text="Cleat Thickness (in):").grid(row=1, column=0, sticky="w", pady=2)
        self.cleat_thick_entry = ttk.Entry(general_frame, width=25); self.cleat_thick_entry.grid(row=1, column=1, sticky="ew", pady=2); self.cleat_thick_entry.insert(0, "0.75")
        
        # --- Floorboard Inputs Section (New & Modified) ---
        floor_frame = ttk.LabelFrame(main_frame, text="Floorboard Parameters", padding="10")
        floor_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        floor_frame.columnconfigure(1, weight=1) 
        floor_frame.columnconfigure(0, weight=0) 

        ttk.Label(floor_frame, text="Floorboard Actual Thickness (in):").grid(row=0, column=0, sticky="w", pady=2)
        self.fb_thickness_entry = ttk.Entry(floor_frame, width=25); self.fb_thickness_entry.grid(row=0, column=1, sticky="ew", pady=2); self.fb_thickness_entry.insert(0, "1.5") # Assuming 2x lumber for floor
        
        ttk.Label(floor_frame, text="Max Inter-Board Gap (in):").grid(row=1, column=0, sticky="w", pady=2)
        self.fb_max_gap_entry = ttk.Entry(floor_frame, width=25); self.fb_max_gap_entry.grid(row=1, column=1, sticky="ew", pady=2); self.fb_max_gap_entry.insert(0, str(DEFAULT_MAX_ALLOWABLE_INTER_FB_GAP))

        ttk.Label(floor_frame, text="Min Custom Rip Width (in):").grid(row=2, column=0, sticky="w", pady=2)
        self.fb_min_rip_entry = ttk.Entry(floor_frame, width=25); self.fb_min_rip_entry.grid(row=2, column=1, sticky="ew", pady=2); self.fb_min_rip_entry.insert(0, str(DEFAULT_MIN_RIP_LUMBER_WIDTH))

        # Available Lumber Selection (New)
        lumber_select_frame = ttk.LabelFrame(floor_frame, text="Available Standard Lumber (Actual Widths)", padding="5")
        lumber_select_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.lumber_vars = {} # To store BooleanVar for each checkbox
        col_count = 0
        max_cols = 2 # Number of columns for checkboxes
        for i, (desc, width_val) in enumerate(DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS.items()):
            var = tk.BooleanVar(value=True) # Default to selected
            cb = ttk.Checkbutton(lumber_select_frame, text=desc, variable=var)
            # Place checkboxes in a grid within their frame
            cb.grid(row=i // max_cols, column=i % max_cols, sticky="w", padx=5, pady=2)
            self.lumber_vars[width_val] = var # Store by actual width value (key)
            lumber_select_frame.columnconfigure(i % max_cols, weight=1) # Allow columns to expand

        # --- Generate Button ---
        self.generate_button = ttk.Button(main_frame, text="Generate Expressions File", command=self.generate_file)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=15) # Adjusted row
        
        main_frame.columnconfigure(0, weight=1) # Ensure main_frame's column expands

    def generate_file(self):
        try:
            # Retrieve values from Entry widgets
            weight = float(self.weight_entry.get())
            length = float(self.length_entry.get())
            width = float(self.width_entry.get())
            clearance = float(self.clearance_entry.get())
            panel_thick = float(self.panel_thick_entry.get())
            cleat_thick = float(self.cleat_thick_entry.get())
            fb_thickness = float(self.fb_thickness_entry.get())
            fb_max_gap = float(self.fb_max_gap_entry.get())
            fb_min_rip = float(self.fb_min_rip_entry.get())

            # Retrieve selected lumber widths
            selected_lumber_actual_widths = []
            for width_val, var in self.lumber_vars.items():
                if var.get(): # If the checkbox is checked
                    selected_lumber_actual_widths.append(width_val)
            
            if not selected_lumber_actual_widths: # Validation
                messagebox.showerror("Input Error", "Please select at least one available standard lumber type.")
                return

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for all numeric fields.")
            return

        # Ask user for save location
        output_filename = filedialog.asksaveasfilename(
            defaultextension=".exp",
            filetypes=[("Expression Files", "*.exp"), ("All Files", "*.*")],
            title="Save NX Expression File As...",
            initialfile="CrateExpressions_Full.exp" # Suggest a filename
        )
        if not output_filename: # User cancelled
            return

        # Call the logic function with all collected parameters
        success, message = generate_crate_expressions_logic(
            product_weight_lbs=weight,
            product_length_in=length,
            product_width_in=width,
            clearance_each_side_in=clearance,
            panel_thickness_in=panel_thick,
            cleat_thickness_in=cleat_thick,
            floorboard_actual_thickness_in=fb_thickness,
            selected_std_lumber_widths=selected_lumber_actual_widths,
            max_allowable_inter_fb_gap_in=fb_max_gap,
            min_rip_lumber_width_in=fb_min_rip,
            output_filename=output_filename
        )

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = CrateApp(root)
    root.mainloop()
