#!/usr/bin/env python3
"""
Agritech Point of Sale System - Main Application Entry
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, PhotoImage

print("Starting POS application...")

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_handler import DBHandler
from ui.login import AutoLoginFrame
from ui.dashboard import Dashboard
from utils.config import load_config, save_config
from assets.styles import COLORS, FONTS, STYLES, set_theme

class POSApplication(tk.Tk):
    """Main application class for the POS system"""

    def __init__(self):
        super().__init__()

        # Initialize database
        self.db = DBHandler()
        if not self.db.is_initialized:
            messagebox.showerror("Database Error", 
                                 "Failed to initialize database. Please check permissions and disk space.")
            self.destroy()
            sys.exit(1)

        # Load configuration
        self.config = load_config()

        # Apply theme early based on configuration
        theme_mode = self.config.get('app_theme', 'light')
        theme_type = self.config.get('theme_type', 'default')
        set_theme(theme_mode, theme_type)

        # Initialize default user (shopkeeper)
        self.current_user = {
            "id": 1,
            "name": "Shopkeeper",
            "role": "admin"
        }

        # Setup main window
        self.title(f"{self.config.get('shop_name', 'Agritech')} - Point of Sale")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Set icon
        try:
            # We'll use a placeholder icon if available
            self.iconphoto(True, PhotoImage(file="assets/logo.png"))
        except:
            pass

        # Dictionary to hold all frames
        self.frames = {}

        # Initialize UI
        self.setup_ui()

        # Bind global function key shortcuts for menu navigation
        self.bind_all("<F1>", lambda event: self.navigate_to_menu("sales"))
        self.bind_all("<F2>", lambda event: self.navigate_to_menu("sales_history"))
        self.bind_all("<F3>", lambda event: self.navigate_to_menu("inventory"))
        self.bind_all("<F4>", lambda event: self.navigate_to_menu("customers"))
        self.bind_all("<F5>", lambda event: self.navigate_to_menu("reports"))
        self.bind_all("<F6>", lambda event: self.navigate_to_menu("accounting"))

        # Skip login and go directly to dashboard (temporary)
        self.show_frame("dashboard")

    def setup_ui(self):
        """Setup the main UI container and frames"""
        # Main container for all frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize login frame to fill the entire window
        login_frame = AutoLoginFrame(container, self)
        self.frames["login"] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")

        # Create dashboard (will be shown after auto-login)
        dashboard = Dashboard(container, self)
        self.frames["dashboard"] = dashboard
        dashboard.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_name):
        """Raise the specified frame to the top"""
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            # Call on_show method if exists (for refreshing data)
            if hasattr(frame, 'on_show'):
                frame.on_show()

    def navigate_to_menu(self, module_name):
        """Navigate to a specific menu module from anywhere in the app"""
        # First ensure we're on the dashboard frame
        self.show_frame("dashboard")

        # Then load the specific module in the dashboard
        dashboard = self.frames.get("dashboard")
        if dashboard and hasattr(dashboard, 'load_module'):
            dashboard.load_module(module_name)

    def show_dashboard(self):
        """Show the main dashboard"""
        self.show_frame("dashboard")

    def exit_application(self):
        """Safely exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            # Save any pending configuration changes
            save_config(self.config)
            # Close database connection
            self.db.close()
            # Destroy the tkinter root
            self.destroy()

    def create_backup(self):
        """Trigger a database backup"""
        from utils.backup import create_backup
        success = create_backup(self.db)
        if success:
            messagebox.showinfo("Backup", "Backup created successfully!")
        else:
            messagebox.showerror("Backup Error", "Failed to create backup. Please check permissions.")

    def show_keyboard_shortcuts(self):
        """Display keyboard shortcuts help"""
        shortcuts_window = tk.Toplevel(self)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("600x500")
        shortcuts_window.resizable(False, False)
        shortcuts_window.configure(bg=COLORS["bg_primary"])

        # Create content
        tk.Label(shortcuts_window, 
               text="Keyboard Shortcuts",
               font=FONTS["heading"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(pady=15)

        # Create scrollable frame
        canvas = tk.Canvas(shortcuts_window, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(shortcuts_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Navigation shortcuts
        self.add_shortcut_section(scrollable_frame, "Navigation", [
            ("↑/↓", "Navigate between items in lists"),
            ("Tab", "Switch focus between different areas"),
            ("Left/Right", "Navigate between menu items"),
            ("Esc", "Exit the application (with confirmation)")
        ])

        # Dashboard shortcuts
        self.add_shortcut_section(scrollable_frame, "Dashboard", [
            ("F1", "Open Sales & CheckOut"),
            ("F2", "Open Sales History"),
            ("F3", "Open Inventory"),
            ("F4", "Open Customers"),
            ("F5", "Open Reports"),
            ("F6", "Open Accounting"),
            ("Arrow Keys", "Navigate between menu items"),
            ("Enter", "Select menu item")
        ])

        # Sales shortcuts
        self.add_shortcut_section(scrollable_frame, "Sales Screen", [
            ("Ctrl+C", "Change customer"),
            ("Ctrl+P", "Process cash payment"),
            ("Ctrl+U", "Process UPI payment"),
            ("Ctrl+S", "Process split payment"),
            ("Ctrl+X", "Cancel sale"),
            ("Ctrl+Z", "Suspend sale"),
            ("Ctrl+F", "Focus on search field"),
            ("Enter", "Add selected product / Edit cart item"),
            ("Delete", "Remove item from cart")
        ])

        # Products shortcuts
        self.add_shortcut_section(scrollable_frame, "Product Management", [
            ("Ctrl+N", "Add new product"),
            ("Ctrl+E", "Edit selected product"),
            ("Ctrl+D", "Delete selected product"),
            ("Ctrl+S", "Add stock to product"),
            ("Ctrl+F", "Focus on search field"),
            ("Enter", "Edit selected product"),
            ("Delete", "Delete selected product")
        ])

        # Customer shortcuts
        self.add_shortcut_section(scrollable_frame, "Customer Management", [
            ("Ctrl+N", "Add new customer"),
            ("Ctrl+E", "Edit selected customer"),
            ("Ctrl+D", "Delete selected customer"),
            ("Ctrl+H", "View purchase history"),
            ("Ctrl+F", "Focus on search field"),
            ("Enter", "Edit selected customer"),
            ("Delete", "Delete selected customer")
        ])

        # Button at bottom
        button_frame = tk.Frame(shortcuts_window, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        close_btn = tk.Button(button_frame,
                           text="Close",
                           font=FONTS["regular"],
                           bg=COLORS["secondary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           command=shortcuts_window.destroy)
        close_btn.pack(padx=20, pady=10)

        # Center the window
        shortcuts_window.update_idletasks()
        width = shortcuts_window.winfo_width()
        height = shortcuts_window.winfo_height()
        x = (shortcuts_window.winfo_screenwidth() // 2) - (width // 2)
        y = (shortcuts_window.winfo_screenheight() // 2) - (height // 2)
        shortcuts_window.geometry(f"+{x}+{y}")

    def add_shortcut_section(self, parent, title, shortcuts):
        """Add a section of shortcuts to the help window"""
        # Section title
        section_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=5)
        section_frame.pack(fill=tk.X, pady=5)

        section_title = tk.Label(section_frame,
                               text=title,
                               font=FONTS["subheading"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=5)
        section_title.pack(fill=tk.X)

        # Shortcuts
        for shortcut, description in shortcuts:
            shortcut_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
            shortcut_frame.pack(fill=tk.X, padx=10)

            shortcut_key = tk.Label(shortcut_frame,
                                  text=shortcut,
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["text_primary"],
                                  width=15,
                                  anchor="w")
            shortcut_key.pack(side=tk.LEFT, padx=10, pady=3)

            shortcut_desc = tk.Label(shortcut_frame,
                                   text=description,
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   anchor="w")
            shortcut_desc.pack(side=tk.LEFT, padx=10, pady=3, fill=tk.X, expand=True)

if __name__ == "__main__":
    app = POSApplication()
    # Set window to start centered
    window_width = app.winfo_width()
    window_height = app.winfo_height()
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    app.geometry(f"+{x}+{y}")
    app.mainloop()