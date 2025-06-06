"""
User Interface module for the NX Crate Expression Generator.
Provides a Tkinter-based GUI for user input and file generation.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Tuple, List

# Default Constants
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = { 
    "2x6 (5.5 in)": 5.5, "2x8 (7.25 in)": 7.25,
    "2x10 (9.25 in)": 9.25, "2x12 (11.25 in)": 11.25
}
DEFAULT_MIN_CUSTOM_LUMBER_WIDTH = 2.5
DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP = 0.25
MIN_FORCEABLE_CUSTOM_BOARD_WIDTH = 0.25

class CrateGeneratorUI:
    """Main UI class for the Crate Expression Generator."""
    
    def __init__(self, master, generation_callback):
        """
        Initialize the UI.
        
        Args:
            master: Tkinter root window
            generation_callback: Function to call when generating expressions
        """
        self.master = master
        self.generation_callback = generation_callback
        
        # Configure main window
        master.title("NX Crate Exporter (Modular Architecture)")
        master.geometry("550x880")
        
        # Configure styling
        self._setup_styles()
        
        # Create main frame
        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        
        # Create UI sections
        self._create_skid_section(main_frame)
        self._create_general_section(main_frame)
        self._create_floorboard_section(main_frame)
        self._create_generate_button(main_frame)
        
        # Configure main frame grid
        main_frame.columnconfigure(0, weight=1)
    
    def _setup_styles(self):
        """Configure ttk styles for the UI."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", padding=3, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TEntry", padding=3, font=('Helvetica', 10))
        style.configure("TCheckbutton", padding=3, font=('Helvetica', 10))
        style.configure("TLabelframe.Label", font=('Helvetica', 10, 'bold'))
        self.master.configure(bg='#e1e1e1')
    
    def _create_skid_section(self, parent):
        """Create the skid parameters section."""
        skid_frame = ttk.LabelFrame(parent, text="Skid Parameters", padding="10")
        skid_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        skid_frame.columnconfigure(1, weight=1)
        
        # Product weight
        ttk.Label(skid_frame, text="Product Weight (lbs):").grid(
            row=0, column=0, sticky="w", pady=2)
        self.weight_entry = ttk.Entry(skid_frame, width=25)
        self.weight_entry.grid(row=0, column=1, sticky="ew", pady=2)
        self.weight_entry.insert(0, "300.0")
        
        # Product length
        ttk.Label(skid_frame, text="Product Length (in):").grid(
            row=1, column=0, sticky="w", pady=2)
        self.length_entry = ttk.Entry(skid_frame, width=25)
        self.length_entry.grid(row=1, column=1, sticky="ew", pady=2)
        self.length_entry.insert(0, "100.0")
        
        # Product width
        ttk.Label(skid_frame, text="Product Width (in):").grid(
            row=2, column=0, sticky="w", pady=2)
        self.width_entry = ttk.Entry(skid_frame, width=25)
        self.width_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.width_entry.insert(0, "40.0")
        
        # Clearance per side
        ttk.Label(skid_frame, text="Clearance per Side (in):").grid(
            row=3, column=0, sticky="w", pady=2)
        self.clearance_entry = ttk.Entry(skid_frame, width=25)
        self.clearance_entry.grid(row=3, column=1, sticky="ew", pady=2)
        self.clearance_entry.insert(0, "2.5")
        
        # Allow 3x4 skids checkbox
        self.allow_3x4_skids_var = tk.BooleanVar(value=True)
        self.allow_3x4_skids_cb = ttk.Checkbutton(
            skid_frame, 
            text="Allow 3x4 Skids (for loads < 500 lbs)", 
            variable=self.allow_3x4_skids_var
        )
        self.allow_3x4_skids_cb.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)
    
    def _create_general_section(self, parent):
        """Create the general crate & panel parameters section."""
        general_frame = ttk.LabelFrame(parent, text="General Crate & Panel Parameters", padding="10")
        general_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        general_frame.columnconfigure(1, weight=1)
        
        # Panel sheathing thickness
        ttk.Label(general_frame, text="Panel Sheathing Thickness (in):").grid(
            row=0, column=0, sticky="w", pady=2)
        self.panel_thick_entry = ttk.Entry(general_frame, width=25)
        self.panel_thick_entry.grid(row=0, column=1, sticky="ew", pady=2)
        self.panel_thick_entry.insert(0, "0.25")
        
        # Cleat thickness
        ttk.Label(general_frame, text="Cleat Thickness (in):").grid(
            row=1, column=0, sticky="w", pady=2)
        self.cleat_thick_entry = ttk.Entry(general_frame, width=25)
        self.cleat_thick_entry.grid(row=1, column=1, sticky="ew", pady=2)   
        self.cleat_thick_entry.insert(0, "0.75")
        
        # Product actual height
        ttk.Label(general_frame, text="Product Actual Height (in):").grid(
            row=2, column=0, sticky="w", pady=2)
        self.product_actual_height_entry = ttk.Entry(general_frame, width=25)
        self.product_actual_height_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.product_actual_height_entry.insert(0, "50.0")
        
        # Clearance above product
        ttk.Label(general_frame, text="Clearance Above Product (in):").grid(
            row=3, column=0, sticky="w", pady=2)
        self.clearance_above_product_entry = ttk.Entry(general_frame, width=25)
        self.clearance_above_product_entry.grid(row=3, column=1, sticky="ew", pady=2)
        self.clearance_above_product_entry.insert(0, "2.0")
        
        # Ground clearance
        ttk.Label(general_frame, text="Ground Clearance (End Panels, in):").grid(
            row=4, column=0, sticky="w", pady=2)
        self.ground_clearance_entry = ttk.Entry(general_frame, width=25)
        self.ground_clearance_entry.grid(row=4, column=1, sticky="ew", pady=2)
        self.ground_clearance_entry.insert(0, "1.0")
    
    def _create_floorboard_section(self, parent):
        """Create the floorboard parameters section."""
        floor_frame = ttk.LabelFrame(parent, text="Floorboard Parameters", padding="10")
        floor_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        floor_frame.columnconfigure(1, weight=1)
        floor_frame.columnconfigure(0, weight=0)
        
        # Floorboard actual thickness
        ttk.Label(floor_frame, text="Floorboard Actual Thickness (in):").grid(
            row=0, column=0, sticky="w", pady=2)
        self.fb_thickness_entry = ttk.Entry(floor_frame, width=25)
        self.fb_thickness_entry.grid(row=0, column=1, sticky="ew", pady=2)
        self.fb_thickness_entry.insert(0, "1.5")
        
        # Max allowable middle gap
        ttk.Label(floor_frame, text="Max Allowable Middle Gap (in):").grid(
            row=1, column=0, sticky="w", pady=2)
        self.fb_max_gap_entry = ttk.Entry(floor_frame, width=25)
        self.fb_max_gap_entry.grid(row=1, column=1, sticky="ew", pady=2)
        self.fb_max_gap_entry.insert(0, str(DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP))
        
        # Min custom board width
        ttk.Label(floor_frame, text="Min Custom Board Width (in):").grid(
            row=2, column=0, sticky="w", pady=2)
        self.fb_min_custom_entry = ttk.Entry(floor_frame, width=25)
        self.fb_min_custom_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.fb_min_custom_entry.insert(0, str(DEFAULT_MIN_CUSTOM_LUMBER_WIDTH))
        
        # Force small custom board checkbox
        self.force_small_custom_var = tk.BooleanVar(value=False)
        self.force_small_custom_cb = ttk.Checkbutton(
            floor_frame,
            text=f"Force small custom board for tiny gap ({MIN_FORCEABLE_CUSTOM_BOARD_WIDTH}\" - {DEFAULT_MIN_CUSTOM_LUMBER_WIDTH}\")",
            variable=self.force_small_custom_var
        )
        self.force_small_custom_cb.grid(row=3, column=0, columnspan=2, sticky="w", pady=4)
        
        # Lumber selection frame
        lumber_select_frame = ttk.LabelFrame(floor_frame, text="Available Standard Lumber (Actual Widths)", padding="5")
        lumber_select_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.lumber_vars = {}
        max_cols = 2
        for i, (desc, width_val) in enumerate(DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS.items()):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(lumber_select_frame, text=desc, variable=var)
            cb.grid(row=i // max_cols, column=i % max_cols, sticky="w", padx=5, pady=2)
            self.lumber_vars[width_val] = var
            lumber_select_frame.columnconfigure(i % max_cols, weight=1)
    
    def _create_generate_button(self, parent):
        """Create the generate button."""
        self.generate_button = ttk.Button(
            parent, 
            text="Generate Expressions File", 
            command=self.generate_file
        )
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=20)
    
    def get_user_inputs(self) -> Tuple[bool, Dict]:
        """
        Extract and validate user inputs from the UI.
        
        Returns:
            Tuple[bool, Dict]: (success, inputs_dict or error_message)
        """
        try:
            # Extract numeric inputs
            weight = float(self.weight_entry.get())
            length = float(self.length_entry.get())
            width = float(self.width_entry.get())
            clearance = float(self.clearance_entry.get())
            panel_thick = float(self.panel_thick_entry.get())
            cleat_thick = float(self.cleat_thick_entry.get())
            prod_actual_height = float(self.product_actual_height_entry.get())
            clear_above_prod = float(self.clearance_above_product_entry.get())
            ground_clear = float(self.ground_clearance_entry.get())
            fb_thickness = float(self.fb_thickness_entry.get())
            fb_max_gap = float(self.fb_max_gap_entry.get())
            fb_min_custom = float(self.fb_min_custom_entry.get())
            
            # Extract boolean inputs
            allow_3x4 = self.allow_3x4_skids_var.get()
            force_small_custom = self.force_small_custom_var.get()
            
            # Extract lumber selection
            selected_lumber = [w for w, v in self.lumber_vars.items() if v.get()]
            if not selected_lumber:
                return False, "Please select at least one standard lumber size."
            
            # Package inputs
            inputs = {
                'product_weight_lbs': weight,
                'product_length_in': length,
                'product_width_in': width,
                'clearance_each_side_in': clearance,
                'allow_3x4_skids_bool': allow_3x4,
                'panel_thickness_in': panel_thick,
                'cleat_thickness_in': cleat_thick,
                'product_actual_height_in': prod_actual_height,
                'clearance_above_product_in': clear_above_prod,
                'ground_clearance_in': ground_clear,
                'floorboard_actual_thickness_in': fb_thickness,
                'selected_std_lumber_widths': selected_lumber,
                'max_allowable_middle_gap_in': fb_max_gap,
                'min_custom_lumber_width_in': fb_min_custom,
                'force_small_custom_board_bool': force_small_custom
            }
            
            return True, inputs
            
        except ValueError as e:
            return False, f"Invalid number entered: {e}"
    
    def generate_file(self):
        """Handle the generate file button click."""
        # Get user inputs
        success, inputs = self.get_user_inputs()
        if not success:
            messagebox.showerror("Input Error", inputs)
            return
        
        # Get output filename
        output_filename = filedialog.asksaveasfilename(
            defaultextension=".exp",
            initialfile="Crate_Final_With_Panels.exp",
            filetypes=[("NX Expression files", "*.exp"), ("All files", "*.*")]
        )
        if not output_filename:
            return
        
        # Call the generation callback
        try:
            success, message = self.generation_callback(inputs, output_filename)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

def create_ui(generation_callback) -> tk.Tk:
    """
    Create and return the main UI window.
    
    Args:
        generation_callback: Function to call when generating expressions
        
    Returns:
        tk.Tk: The root window
    """
    root = tk.Tk()
    app = CrateGeneratorUI(root, generation_callback)
    return root
