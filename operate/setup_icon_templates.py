import os
import pyautogui
import time
import tkinter as tk
from tkinter import simpledialog, messagebox


def setup_icon_templates():
    """
    Simplified helper script to set up icon templates for visual target finding.
    Uses simple coordinate input rather than visual selection.
    """
    # Create templates directory if it doesn't exist
    template_dir = "icon_templates"
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        print(f"Created directory: {template_dir}")

    # Create a simple GUI for capturing templates
    root = tk.Tk()
    root.title("Icon Template Capture Tool")
    root.geometry("400x200")

    # Function to capture icon at cursor position
    def capture_at_cursor():
        icon_name = simpledialog.askstring("Icon Name", "Enter name for this icon/folder:", parent=root)
        if not icon_name:
            return

        # Give user time to position cursor
        messagebox.showinfo("Capture Icon",
                            "Position your mouse cursor over the center of the icon you want to capture, then click OK.")

        # Get cursor position
        time.sleep(0.5)  # Small delay after dialog closes
        x, y = pyautogui.position()

        # Capture region around cursor (100x100 pixels)
        region_size = 50  # pixels in each direction from center
        region = (x - region_size, y - region_size, region_size * 2, region_size * 2)

        try:
            # Capture the region
            screenshot = pyautogui.screenshot(region=region)

            # Save the template
            filename = f"{icon_name.replace(' ', '_').lower()}.png"
            filepath = os.path.join(template_dir, filename)
            screenshot.save(filepath)

            messagebox.showinfo("Success", f"Saved template as {filename}")
            print(f"Saved template as {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture: {str(e)}")
            print(f"Error: {e}")

    # Function to capture custom region
    def capture_custom_region():
        icon_name = simpledialog.askstring("Icon Name", "Enter name for this icon/folder:", parent=root)
        if not icon_name:
            return

        # Ask for region coordinates
        try:
            x = simpledialog.askinteger("X Coordinate", "Enter X coordinate (left edge):", parent=root)
            if x is None: return

            y = simpledialog.askinteger("Y Coordinate", "Enter Y coordinate (top edge):", parent=root)
            if y is None: return

            width = simpledialog.askinteger("Width", "Enter width in pixels:", parent=root, minvalue=10, maxvalue=500)
            if width is None: return

            height = simpledialog.askinteger("Height", "Enter height in pixels:", parent=root, minvalue=10,
                                             maxvalue=500)
            if height is None: return

            # Capture the specified region
            region = (x, y, width, height)
            screenshot = pyautogui.screenshot(region=region)

            # Save the template
            filename = f"{icon_name.replace(' ', '_').lower()}.png"
            filepath = os.path.join(template_dir, filename)
            screenshot.save(filepath)

            messagebox.showinfo("Success", f"Saved template as {filename}")
            print(f"Saved template as {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture: {str(e)}")
            print(f"Error: {e}")

    # Create and place buttons
    label = tk.Label(root, text="Icon Template Capture Tool", font=("Arial", 14))
    label.pack(pady=10)

    instructions = tk.Label(root, text="Choose a capture method:")
    instructions.pack(pady=5)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    cursor_btn = tk.Button(button_frame, text="Capture at Cursor", command=capture_at_cursor, width=20)
    cursor_btn.grid(row=0, column=0, padx=10, pady=5)

    region_btn = tk.Button(button_frame, text="Specify Region Manually", command=capture_custom_region, width=20)
    region_btn.grid(row=0, column=1, padx=10, pady=5)

    close_btn = tk.Button(root, text="Close", command=root.destroy, width=10)
    close_btn.pack(pady=10)

    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    setup_icon_templates()