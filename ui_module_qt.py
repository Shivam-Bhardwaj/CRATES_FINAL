"""
Modern UI for NX Crate Expression Generator using PyQt6.
This replaces the Tkinter UI for a crisp, high-DPI, professional look.
"""
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QCheckBox, QPushButton, QLabel, QScrollArea, QHBoxLayout, QFileDialog,
    QGridLayout, QDialog, QTextEdit, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

# Default Constants (match backend)
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = [
    ("2x6 (5.5 in)", 5.5), ("2x8 (7.25 in)", 7.25),
    ("2x10 (9.25 in)", 9.25), ("2x12 (11.25 in)", 11.25)
]

class CrateGeneratorUI(QMainWindow):
    def __init__(self, generation_callback):
        super().__init__()
        self.generation_callback = generation_callback
        self.setWindowTitle("NX Crate Expression Generator")
        self.setMinimumSize(850, 540)
        self.setMaximumSize(1200, 700)

        # --- Main Widget and Layout ---
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(24, 24, 24, 16)

        # --- General Crate & Panel Parameters ---
        general_group = QGroupBox("General Crate & Panel Parameters")
        general_grid = QGridLayout()
        general_grid.setHorizontalSpacing(24)
        general_grid.setVerticalSpacing(18)
        general_group.setLayout(general_grid)
        general_fields = [
            ("Product Actual Height (in):", "50.0", "product_actual_height", "Actual product height in inches"),
            ("Clearance Above Product (in):", "2.0", "clearance_above_product", "Clearance above product in inches"),
            ("Ground Clearance (End Panels, in):", "1.0", "ground_clearance", "Ground clearance for end panels in inches"),
            ("Cleat Actual Width (in):", "3.5", "cleat_actual_width", "Cleat actual width in inches"),
        ]
        for i, (label, default, attr, placeholder) in enumerate(general_fields):
            le = QLineEdit(default)
            le.setMinimumWidth(180)
            le.setMaximumWidth(300)
            le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            le.setAlignment(Qt.AlignmentFlag.AlignRight)
            le.setPlaceholderText(placeholder)
            general_grid.addWidget(QLabel(label), i, 0)
            general_grid.addWidget(le, i, 1)
            setattr(self, attr, le)
        main_layout.insertWidget(0, general_group)

        # --- Product Specifications ONLY ---
        prod_group = QGroupBox("\U0001F4E6  Product Specifications")
        prod_grid = QGridLayout()
        prod_grid.setHorizontalSpacing(24)
        prod_grid.setVerticalSpacing(18)
        prod_group.setLayout(prod_grid)
        prod_fields = [
            ("Weight (lbs):", "300.0", "weight", "Enter product weight in pounds"),
            ("Length (in):", "100.0", "length", "Enter product length in inches"),
            ("Width (in):", "40.0", "width", "Enter product width in inches"),
            ("Height (in):", "50.0", "height", "Enter product height in inches"),
            ("Clearance per Side (in):", "2.5", "clearance", "Side clearance in inches"),
            ("Clearance Above (in):", "2.0", "clear_above", "Top clearance in inches"),
        ]
        for i, (label, default, attr, placeholder) in enumerate(prod_fields):
            le = QLineEdit(default)
            le.setMinimumWidth(180)
            le.setMaximumWidth(300)
            le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            le.setAlignment(Qt.AlignmentFlag.AlignRight)
            le.setPlaceholderText(placeholder)
            prod_grid.addWidget(QLabel(label), i//2, (i%2)*2)
            prod_grid.addWidget(le, i//2, (i%2)*2+1)
            setattr(self, attr, le)
        main_layout.addWidget(prod_group)

        # --- Construction Specifications ---
        constr_group = QGroupBox("\U0001F528  Construction Specifications")
        constr_grid = QGridLayout()
        constr_grid.setHorizontalSpacing(24)
        constr_grid.setVerticalSpacing(18)
        constr_group.setLayout(constr_grid)
        constr_fields = [
            ("Panel Thickness (in):", "0.25", "panel_thick", "Panel sheathing thickness"),
            ("Cleat Thickness (in):", "0.75", "cleat_thick", "Cleat thickness"),
            ("Floorboard Thickness (in):", "1.5", "fb_thick", "Floorboard thickness"),
            ("Ground Clearance (in):", "1.0", "ground_clear", "Ground clearance at ends"),
            ("Max Middle Gap (in):", "0.25", "max_gap", "Maximum allowable floor gap"),
            ("Min Custom Width (in):", "2.5", "min_custom", "Minimum custom board width"),
        ]
        for i, (label, default, attr, placeholder) in enumerate(constr_fields):
            le = QLineEdit(default)
            le.setMinimumWidth(180)
            le.setMaximumWidth(300)
            le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            le.setAlignment(Qt.AlignmentFlag.AlignRight)
            le.setPlaceholderText(placeholder)
            constr_grid.addWidget(QLabel(label), i//3, (i%3)*2)
            constr_grid.addWidget(le, i//3, (i%3)*2+1)
            setattr(self, attr, le)
        # Checkboxes below grid, full width
        self.allow_3x4 = QCheckBox("Allow 3x4 Skids (for loads < 500 lbs)")
        self.allow_3x4.setChecked(True)
        self.force_small_custom = QCheckBox("Force small custom board for tiny gaps (0.25\" - 2.5\")")
        self.force_small_custom.setChecked(True)
        self.force_small_custom.setEnabled(True)
        constr_grid.addWidget(self.allow_3x4, 2, 0, 1, 6)
        constr_grid.addWidget(self.force_small_custom, 3, 0, 1, 6)
        main_layout.addWidget(constr_group)

        # --- Lumber Selection ---
        lumber_group = QGroupBox("\U0001FA93  Lumber Selection")
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(18)
        self.lumber_checks = []
        for i, (desc, width) in enumerate(DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS):
            cb = QCheckBox(desc)
            cb.setChecked(True)
            self.lumber_checks.append((cb, width))
            row, col = divmod(i, 2)
            grid.addWidget(cb, row, col)
        lumber_group.setLayout(grid)
        main_layout.addWidget(lumber_group)

        # --- Generate Button ---
        self.generate_btn = QPushButton("🚀 Generate NX Expressions File")
        self.generate_btn.setMinimumHeight(40)
        main_layout.addWidget(self.generate_btn)
        main_layout.setAlignment(self.generate_btn, Qt.AlignmentFlag.AlignHCenter)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready to generate expressions")
        self.setStatusBar(self.status_bar)

        # Connect button
        self.generate_btn.clicked.connect(self.generate_file)

    def get_user_inputs(self):
        try:
            # General Crate & Panel Parameters
            product_actual_height = float(self.product_actual_height.text())
            clearance_above_product = float(self.clearance_above_product.text())
            ground_clearance = float(self.ground_clearance.text())
            cleat_actual_width = float(self.cleat_actual_width.text())

            # --- Product Specifications ONLY ---
            weight = float(self.weight.text())
            length = float(self.length.text())
            width = float(self.width.text())
            height = float(self.height.text())
            clearance = float(self.clearance.text())
            clear_above = float(self.clear_above.text())
            panel_thick = float(self.panel_thick.text())
            cleat_thick = float(self.cleat_thick.text())
            fb_thick = float(self.fb_thick.text())
            ground_clear = float(self.ground_clear.text())
            max_gap = float(self.max_gap.text())
            min_custom = float(self.min_custom.text())
            allow_3x4 = self.allow_3x4.isChecked()
            force_small_custom = self.force_small_custom.isChecked()
            selected_lumber = [w for cb, w in self.lumber_checks if cb.isChecked()]
            if not selected_lumber:
                return False, "Please select at least one standard lumber size."
            inputs = {
                'product_weight_lbs': weight,
                'product_length_in': length,
                'product_width_in': width,
                'clearance_each_side_in': clearance,
                'allow_3x4_skids_bool': allow_3x4,
                'panel_thickness_in': panel_thick,
                'cleat_thickness_in': cleat_thick,
                'product_actual_height_in': product_actual_height,
                'clearance_above_product_in': clearance_above_product,
                'ground_clearance_in': ground_clearance,
                'cleat_actual_width_in': cleat_actual_width,
                'floorboard_actual_thickness_in': fb_thick,
                'selected_std_lumber_widths': selected_lumber,
                'max_allowable_middle_gap_in': max_gap,
                'min_custom_lumber_width_in': min_custom,
                'force_small_custom_board_bool': force_small_custom
            }
            return True, inputs
        except ValueError as e:
            return False, f"Invalid number entered: {e}"

    def generate_file(self):
        self.status_bar.showMessage("Validating inputs...")
        QApplication.processEvents()
        success, inputs = self.get_user_inputs()
        if not success:
            self.status_bar.showMessage("Input validation failed")
            self.show_message("Input Error", inputs, error=True)
            return
        self.status_bar.showMessage("Selecting output file...")
        QApplication.processEvents()
        filename, _ = QFileDialog.getSaveFileName(self, "Save NX Expressions File", "Crate_Final_With_Panels.exp", "NX Expression files (*.exp);;All files (*)")
        if not filename:
            self.status_bar.showMessage("File selection cancelled")
            return
        self.status_bar.showMessage("Generating expressions file...")
        QApplication.processEvents()
        try:
            success, message = self.generation_callback(inputs, filename)
            if success:
                self.status_bar.showMessage("✅ File generated successfully!")
                self.show_message("Success", message, error=False)
            else:
                self.status_bar.showMessage("❌ Generation failed")
                self.show_message("Generation Error", message, error=True)
        except Exception as e:
            self.status_bar.showMessage("❌ Unexpected error occurred")
            self.show_message("Unexpected Error", str(e), error=True)

    def show_message(self, title, msg, error=False):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        layout = QVBoxLayout(dlg)
        label = QLabel(msg)
        if error:
            label.setStyleSheet("color: #b00020; font-weight: bold;")
        else:
            label.setStyleSheet("color: #006400; font-weight: bold;")
        layout.addWidget(label)
        dlg.setLayout(layout)
        dlg.resize(420, 100)
        dlg.exec()

def create_ui(generation_callback):
    app = QApplication.instance() or QApplication(sys.argv)
    window = CrateGeneratorUI(generation_callback)
    window.show()
    return app, window
