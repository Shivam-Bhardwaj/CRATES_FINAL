"""
Main entry point for the NX Crate Expression Generator.
Refactored modular architecture with separate UI, logic, and generation modules.
"""
import tkinter as tk
import logging
import sys # For sys.exit
from main_orchestrator import generate_crate_expressions

try:
    from ui_module_qt import create_ui  # Use PyQt6 UI if available
except ImportError:
    from ui_module import create_ui      # Fallback to Tkinter UI

# --- Setup Logging ---
# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Create a file handler
file_handler = logging.FileHandler('autocrate_app.log', mode='w') # 'w' to overwrite, 'a' to append
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) # Log INFO and above to console

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# --- End Logging Setup ---

def main():
    """Main application entry point."""
    logger.info("Application started.")
    def generation_callback(inputs, output_filename):
        """Callback function for UI to generate expressions."""
        try:
            logger.info(f"Generation callback triggered for: {output_filename}")
            logger.debug(f"Inputs received: {inputs}")
            result = generate_crate_expressions(inputs, output_filename)
            logger.info(f"Expression generation successful: {result}")
            return result
        except Exception as e:
            logger.error(f"Error during expression generation: {e}", exc_info=True)
            # Depending on how the UI handles callback return values,
            # you might want to return an error message or raise the exception
            # For now, returning a string indicating failure.
            return f"Generation Error: {e}"
    
    try:
        # Create and run the UI
        logger.info("Creating UI...")
        result = create_ui(generation_callback)
        logger.info("UI created. Starting event loop.")
        # PyQt6 returns (QApplication, window), Tkinter returns Tk
        if isinstance(result, tuple) and hasattr(result[0], "exec"):
            app, window = result
            app.exec()
        else:
            result.mainloop()
        logger.info("UI event loop finished.")
    except ImportError as e:
        logger.critical(f"Failed to import a UI module: {e}", exc_info=True)
        # Optionally, show a simple Tkinter error if all UI fails
        root = tk.Tk()
        root.withdraw() # Hide the main window
        tk.messagebox.showerror("Startup Error", f"Failed to load UI components: {e}\nPlease ensure PyQt6 or Tkinter is installed.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unhandled error occurred in the main application: {e}", exc_info=True)
        # Optionally, show a simple Tkinter error
        try:
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showerror("Application Error", f"An unexpected error occurred: {e}\nCheck autocrate_app.log for details.")
        except Exception as tk_err:
            logger.error(f"Could not display Tkinter error dialog: {tk_err}")
        sys.exit(1)
    finally:
        logger.info("Application shutting down.")

if __name__ == "__main__":
    main()
