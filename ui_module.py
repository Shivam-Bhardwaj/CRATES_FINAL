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
        master.title("NX Crate Expression Generator - Modern Interface")
        master.geometry("700x900")
        master.minsize(650, 800)
        
        # Configure styling
        self._setup_styles()
        
        # Create scrollable main frame
        self._create_scrollable_frame(master)
          # Create UI sections with modern layout
        self._create_header()
        self._create_product_specs_section()
        self._create_construction_specs_section()
        self._create_lumber_selection_section()
        self._create_action_section()
        
        # Configure responsive layout
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
    
    def _setup_styles(self):
        """Configure modern ttk styles for the UI."""
        style = ttk.Style()
        
        # Use a simple, reliable theme
        style.theme_use('clam')   # Consistent cross-platform theme
        
        # Define color scheme with better contrast
        colors = {
            'primary': '#2E86AB',      # Professional blue
            'secondary': '#A23B72',    # Accent purple
            'success': '#2E8B57',      # Success green
            'light_gray': '#F8F9FA',   # Light background
            'medium_gray': '#6C757D',  # Medium text
            'dark_gray': '#343A40',    # Dark text
            'white': '#FFFFFF',
            'entry_bg': '#FFFFFF',     # Entry background
            'button_bg': '#E9ECEF'     # Button background
        }
        
        # Configure label styles with dark text
        style.configure("Title.TLabel", 
                       font=('Segoe UI', 16, 'bold'), 
                       foreground=colors['primary'],
                       background=colors['light_gray'])
        
        style.configure("Heading.TLabel", 
                       font=('Segoe UI', 11, 'bold'), 
                       foreground=colors['dark_gray'],
                       background=colors['light_gray'])
        
        style.configure("Modern.TLabel", 
                       font=('Segoe UI', 9), 
                       foreground=colors['dark_gray'],  # Changed from medium_gray to dark_gray for better visibility
                       background=colors['light_gray'])
        
        # Configure entry styles
        style.configure("Modern.TEntry", 
                       font=('Segoe UI', 9),
                       fieldbackground=colors['entry_bg'],
                       foreground=colors['dark_gray'],
                       relief="solid",
                       borderwidth=1,
                       insertcolor=colors['dark_gray'])
        
        # Configure button styles
        style.configure("Modern.TButton", 
                       font=('Segoe UI', 10, 'bold'),
                       relief="raised",
                       borderwidth=1,
                       focuscolor='none')
        
        style.map("Modern.TButton",
                 background=[('active', colors['primary']),
                            ('!active', colors['button_bg'])],
                 foreground=[('active', colors['white']),
                            ('!active', colors['dark_gray'])])
        
        style.configure("Generate.TButton", 
                       font=('Segoe UI', 12, 'bold'),
                       relief="raised",
                       borderwidth=2,
                       focuscolor='none')
        
        style.map("Generate.TButton",
                 background=[('active', colors['success']),
                            ('!active', colors['primary'])],
                 foreground=[('active', colors['white']),
                            ('!active', colors['white'])])
        
        # Configure checkbox styles
        style.configure("Modern.TCheckbutton", 
                       font=('Segoe UI', 9),
                       foreground=colors['dark_gray'],
                       background=colors['light_gray'],
                       focuscolor='none')
        
        # Configure labelframe styles
        style.configure("Modern.TLabelframe", 
                       relief="solid",
                       borderwidth=1,
                       background=colors['light_gray'])
        
        style.configure("Modern.TLabelframe.Label", 
                       font=('Segoe UI', 10, 'bold'),
                       foreground=colors['primary'],
                       background=colors['light_gray'])
        
        # Configure main window background
        self.master.configure(bg=colors['light_gray'])
    
    def _create_scrollable_frame(self, master):
        """Create a scrollable frame for the UI content."""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(master, bg='#F8F9FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
          # Create main frame with padding
        self.main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        self.main_frame.pack(fill="both", expand=True)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _create_header(self):
        """Create the header section."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 30))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🏗️ NX Crate Expression Generator", 
                               style="Title.TLabel")
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                  text="Modern Interface • Parametric Design • Automated Calculations",
                                  style="Modern.TLabel")
        subtitle_label.pack(pady=(5, 0))
    
    def _create_product_specs_section(self):
        """Create the product specifications section."""
        specs_frame = ttk.LabelFrame(self.main_frame, 
                                    text="📦 Product Specifications", 
                                    style="Modern.TLabelframe",
                                    padding="15")
        specs_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        specs_frame.columnconfigure(1, weight=1)
        specs_frame.columnconfigure(3, weight=1)
        
        # Product dimensions in a 2x3 grid
        dimensions = [
            ("Weight (lbs):", "300.0", 0, 0),
            ("Length (in):", "100.0", 0, 2),
            ("Width (in):", "40.0", 1, 0),
            ("Height (in):", "50.0", 1, 2),
            ("Clearance per Side (in):", "2.5", 2, 0),
            ("Clearance Above (in):", "2.0", 2, 2)
        ]
        
        self.entries = {}
        for label_text, default_val, row, col in dimensions:
            # Label
            label = ttk.Label(specs_frame, text=label_text, style="Modern.TLabel")
            label.grid(row=row, column=col, sticky="w", padx=(0, 10), pady=5)
            
            # Entry
            entry = ttk.Entry(specs_frame, style="Modern.TEntry", width=15)
            entry.insert(0, default_val)
            entry.grid(row=row, column=col+1, sticky="ew", padx=(0, 20), pady=5)
            
            # Store entry reference
            entry_key = label_text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(":", "")
            self.entries[entry_key] = entry
    
    def _create_construction_specs_section(self):
        """Create the construction specifications section."""
        construction_frame = ttk.LabelFrame(self.main_frame, 
                                           text="🔧 Construction Specifications", 
                                           style="Modern.TLabelframe",
                                           padding="15")
        construction_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        construction_frame.columnconfigure(1, weight=1)
        construction_frame.columnconfigure(3, weight=1)
        
        # Construction parameters in 2x3 grid
        construction_params = [
            ("Panel Thickness (in):", "0.25", 0, 0),
            ("Cleat Thickness (in):", "0.75", 0, 2),
            ("Floorboard Thickness (in):", "1.5", 1, 0),
            ("Ground Clearance (in):", "1.0", 1, 2),
            ("Max Middle Gap (in):", "0.25", 2, 0),
            ("Min Custom Width (in):", "2.5", 2, 2)
        ]
        
        for label_text, default_val, row, col in construction_params:
            # Label
            label = ttk.Label(construction_frame, text=label_text, style="Modern.TLabel")
            label.grid(row=row, column=col, sticky="w", padx=(0, 10), pady=5)
            
            # Entry
            entry = ttk.Entry(construction_frame, style="Modern.TEntry", width=15)
            entry.insert(0, default_val)
            entry.grid(row=row, column=col+1, sticky="ew", padx=(0, 20), pady=5)
            
            # Store entry reference
            entry_key = label_text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(":", "")
            self.entries[entry_key] = entry
        
        # Options checkboxes
        options_frame = ttk.Frame(construction_frame)
        options_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(15, 0))
        
        self.allow_3x4_skids_var = tk.BooleanVar(value=True)
        allow_3x4_cb = ttk.Checkbutton(options_frame, 
                                      text="Allow 3x4 Skids (for loads < 500 lbs)", 
                                      variable=self.allow_3x4_skids_var,
                                      style="Modern.TCheckbutton")
        allow_3x4_cb.pack(anchor="w", pady=2)
        
        self.force_small_custom_var = tk.BooleanVar(value=False)
        force_custom_cb = ttk.Checkbutton(options_frame,
                                         text=f"Force small custom board for tiny gaps (0.25\" - 2.5\")",
                                         variable=self.force_small_custom_var,
                                         style="Modern.TCheckbutton")
        force_custom_cb.pack(anchor="w", pady=2)
    
    def _create_lumber_selection_section(self):
        """Create the lumber selection section."""
        lumber_frame = ttk.LabelFrame(self.main_frame, 
                                     text="🪵 Lumber Selection", 
                                     style="Modern.TLabelframe",
                                     padding="15")
        lumber_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(lumber_frame, 
                              text="Select available standard lumber widths (actual dimensions):",
                              style="Modern.TLabel")
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Lumber checkboxes in a grid
        lumber_grid = ttk.Frame(lumber_frame)
        lumber_grid.pack(fill="x")
        
        self.lumber_vars = {}
        lumber_options = [
            ("2×6 (5.5 in)", 5.5),
            ("2×8 (7.25 in)", 7.25),
            ("2×10 (9.25 in)", 9.25),
            ("2×12 (11.25 in)", 11.25)
        ]
        
        for i, (desc, width_val) in enumerate(lumber_options):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(lumber_grid, 
                               text=desc, 
                               variable=var,
                               style="Modern.TCheckbutton")
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 40), pady=5)
            self.lumber_vars[width_val] = var
            lumber_grid.columnconfigure(i % 2, weight=1)
    
    def _create_action_section(self):
        """Create the action buttons section."""
        action_frame = ttk.Frame(self.main_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        # Generate button
        self.generate_button = ttk.Button(action_frame, 
                                         text="🚀 Generate NX Expressions File", 
                                         command=self.generate_file,
                                         style="Generate.TButton")
        self.generate_button.pack(ipadx=20, ipady=10)
        
        # Status label
        self.status_label = ttk.Label(action_frame, 
                                     text="Ready to generate expressions",                                     style="Modern.TLabel")
        self.status_label.pack(pady=(10, 0))
    
    def _create_skid_section(self, parent):
        """Create the skid parameters section."""
        # This method is deprecated - functionality moved to _create_product_specs_section
        pass
    
    def _create_general_section(self, parent):
        """Create the general crate & panel parameters section."""
        # This method is deprecated - functionality moved to _create_construction_specs_section
        pass
    
    def _create_floorboard_section(self, parent):
        """Create the floorboard parameters section."""        # This method is deprecated - functionality moved to _create_construction_specs_section and _create_lumber_selection_section
        pass
    
    def _create_generate_button(self, parent):
        """Create the generate button."""
        # This method is deprecated - functionality moved to _create_action_section
        pass
    
    def get_user_inputs(self) -> Tuple[bool, Dict]:
        """
        Extract and validate user inputs from the UI.
        
        Returns:
            Tuple[bool, Dict]: (success, inputs_dict or error_message)
        """
        try:
            # Extract numeric inputs from entries dictionary
            weight = float(self.entries['weight_lbs'].get())
            length = float(self.entries['length_in'].get())
            width = float(self.entries['width_in'].get())
            height = float(self.entries['height_in'].get())
            clearance = float(self.entries['clearance_per_side_in'].get())
            clear_above_prod = float(self.entries['clearance_above_in'].get())
            
            panel_thick = float(self.entries['panel_thickness_in'].get())
            cleat_thick = float(self.entries['cleat_thickness_in'].get())
            fb_thickness = float(self.entries['floorboard_thickness_in'].get())
            ground_clear = float(self.entries['ground_clearance_in'].get())
            fb_max_gap = float(self.entries['max_middle_gap_in'].get())
            fb_min_custom = float(self.entries['min_custom_width_in'].get())
            
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
                'product_actual_height_in': height,
                'clearance_above_product_in': clear_above_prod,
                'ground_clearance_in': ground_clear,
                'floorboard_actual_thickness_in': fb_thickness,
                'selected_std_lumber_widths': selected_lumber,
                'max_allowable_middle_gap_in': fb_max_gap,
                'min_custom_lumber_width_in': fb_min_custom,
                'force_small_custom_board_bool': force_small_custom
            }
            
            return True, inputs
            
        except ValueError as e:            return False, f"Invalid number entered: {e}"
        except KeyError as e:
            return False, f"Missing input field: {e}"
    
    def generate_file(self):
        """Handle the generate file button click."""
        # Update status
        self.status_label.config(text="Validating inputs...")
        self.master.update()
        
        # Get user inputs
        success, inputs = self.get_user_inputs()
        if not success:
            self.status_label.config(text="Input validation failed")
            messagebox.showerror("Input Error", inputs)
            return
        
        # Get output filename
        self.status_label.config(text="Selecting output file...")
        self.master.update()
        
        output_filename = filedialog.asksaveasfilename(
            defaultextension=".exp",
            initialfile="Crate_Final_With_Panels.exp",
            filetypes=[("NX Expression files", "*.exp"), ("All files", "*.*")]
        )
        if not output_filename:
            self.status_label.config(text="File selection cancelled")
            return
        
        # Call the generation callback
        try:
            self.status_label.config(text="Generating expressions file...")
            self.master.update()
            
            success, message = self.generation_callback(inputs, output_filename)
            if success:
                self.status_label.config(text="✅ File generated successfully!")
                messagebox.showinfo("Success", message)
            else:
                self.status_label.config(text="❌ Generation failed")
                messagebox.showerror("Error", message)
        except Exception as e:
            self.status_label.config(text="❌ Unexpected error occurred")
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
