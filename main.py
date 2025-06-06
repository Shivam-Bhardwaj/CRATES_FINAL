"""
Main entry point for the NX Crate Expression Generator.
Refactored modular architecture with separate UI, logic, and generation modules.
"""
import tkinter as tk
from main_orchestrator import generate_crate_expressions

try:
    from ui_module_qt import create_ui  # Use PyQt6 UI if available
except ImportError:
    from ui_module import create_ui      # Fallback to Tkinter UI

def main():
    """Main application entry point."""
    def generation_callback(inputs, output_filename):
        """Callback function for UI to generate expressions."""
        return generate_crate_expressions(inputs, output_filename)
    
    # Create and run the UI
    result = create_ui(generation_callback)
    # PyQt6 returns (QApplication, window), Tkinter returns Tk
    if isinstance(result, tuple) and hasattr(result[0], "exec"):
        app, window = result
        app.exec()
    else:
        result.mainloop()

if __name__ == "__main__":
    main()
