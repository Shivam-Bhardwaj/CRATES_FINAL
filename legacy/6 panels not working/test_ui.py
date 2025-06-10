#!/usr/bin/env python3
"""
Quick test script to demonstrate the modernized UI.
This will open the UI window briefly to show the updated interface.
"""
import tkinter as tk
import threading
import time
from ui_module import create_ui
from main_orchestrator import generate_crate_expressions

def generation_callback(inputs, output_filename):
    """Test callback for the UI."""
    return generate_crate_expressions(inputs, output_filename)

def test_ui():
    """Create and briefly display the modernized UI."""
    print("Creating modernized UI...")
    
    # Create the UI
    root = create_ui(generation_callback)
    
    # Schedule the window to close after a few seconds for demo
    def close_after_delay():
        time.sleep(5)  # Show for 5 seconds
        root.quit()
        root.destroy()
    
    # Start the close timer in a separate thread
    timer_thread = threading.Thread(target=close_after_delay, daemon=True)
    timer_thread.start()
    
    print("UI window should be open now - will close automatically in 5 seconds...")
    print("Key improvements:")
    print("✅ Modern organized sections: Product Specs, Construction Specs, Lumber Selection")
    print("✅ Better color scheme with proper contrast (dark text on light background)")
    print("✅ Professional styling with consistent fonts and spacing")
    print("✅ Responsive layout with proper padding and alignment")
    print("✅ Status updates during file generation")
    print("✅ Scrollable interface for better usability")
    
    try:
        root.mainloop()
    except tk.TclError:
        pass  # Window was closed
    
    print("UI demonstration complete!")

if __name__ == "__main__":
    test_ui()
