"""
Main entry point for the NX Crate Expression Generator.
Refactored modular architecture with separate UI, logic, and generation modules.
"""
import tkinter as tk
from ui_module import create_ui
from main_orchestrator import generate_crate_expressions

def main():
    """Main application entry point."""
    def generation_callback(inputs, output_filename):
        """Callback function for UI to generate expressions."""
        return generate_crate_expressions(inputs, output_filename)
    
    # Create and run the UI
    root = create_ui(generation_callback)
    root.mainloop()

if __name__ == "__main__":
    main()
