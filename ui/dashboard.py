"""
Main dashboard for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES

# Import UI modules (will be loaded when needed)
# DEPRECATED: import ui.product_management as product_management 
# The above import is no longer used - inventory_management.py now handles all product functionality
import ui.sales as sales
import ui.sales_history as sales_history
import ui.customer_management as customer_management
import ui.reports as reports
import ui.inventory_management as inventory_management
import ui.settings as settings
import ui.backup as backup
import ui.cloud_sync as cloud_sync
import ui.accounting as accounting

class Dashboard(tk.Frame):
    """Main dashboard containing the navigation and content frames"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller

        # Dictionary to store frames
        self.frames = {}

        # Navigation variables
        self.nav_buttons = []
        self.current_nav_index = 0

        # Create layout
        self.create_layout()

        # Bind keyboard events
        self.bind("<Key>", self.handle_key_event)
        self.focus_set()  # Set focus to this frame

        # Load initial frame
        self.load_module("sales")

    def create_layout(self):
        """Create the main dashboard layout"""
        # Top header
        self.header_frame = tk.Frame(self, bg=COLORS["primary"], height=60)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Shop name
        shop_name = self.controller.config.get('shop_name', 'Agritech Products Shop')
        shop_label = tk.Label(self.header_frame, 
                             text=shop_name,
                             font=FONTS["heading_light"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"])
        shop_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Removed keyboard shortcuts button (moved to settings)

        # Current date and time
        self.datetime_label = tk.Label(self.header_frame,
                                      text=self.get_current_datetime(),
                                      font=FONTS["regular_light"],
                                      bg=COLORS["primary"],
                                      fg=COLORS["text_white"])
        self.datetime_label.pack(side=tk.RIGHT, padx=15, pady=15)
        self.update_datetime()

        # Side navigation
        self.nav_frame = tk.Frame(self, bg=COLORS["bg_secondary"], width=220)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.nav_frame.pack_propagate(False)

        # Create navigation items
        self.create_nav_items()

        # Main content area
        self.content_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Footer removed as requested

    def create_nav_items(self):
        """Create navigation buttons in the sidebar"""
        # Nav title
        nav_title = tk.Label(self.nav_frame, 
                            text="MENU",
                            font=FONTS["nav_title"],
                            bg=COLORS["bg_secondary"],
                            fg=COLORS["text_primary"])
        nav_title.pack(side=tk.TOP, pady=(20, 15), padx=10, anchor="w")

        # Nav items with icons
        nav_items = [
            {"name": "sales", "text": "Sales & Checkout", "icon": "🛒 "},
            {"name": "sales_history", "text": "Sales History", "icon": "📜 "},
            {"name": "inventory", "text": "Inventory", "icon": "📦 "},  # Changed to product icon for clarity
            {"name": "customers", "text": "Customers", "icon": "👥 "},
            {"name": "reports", "text": "Reports", "icon": "📊 "},
            {"name": "accounting", "text": "Accounting", "icon": "📒 "},
            {"name": "settings", "text": "Settings", "icon": "⚙️ "},
            {"name": "backup", "text": "Backup & Restore", "icon": "💾 "},
            {"name": "cloud_sync", "text": "Cloud Sync", "icon": "☁️ "}
        ]

        # Track selected button for styling
        self.selected_nav = None

        # Create buttons
        for item in nav_items:
            # Create a frame for each button to ensure consistent layout
            btn_frame = tk.Frame(self.nav_frame, bg=COLORS["bg_secondary"])
            btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)

            # Create the button with fixed width icon space
            # Determine if this is the initially selected button (sales)
            is_initial_selection = (item["name"] == "sales")

            # Set font based on whether this is the initial selection
            button_font = (FONTS["nav_item"][0], FONTS["nav_item"][1], "bold") if is_initial_selection else FONTS["nav_item"]

            # Set background and foreground colors based on selection - using a darker color for selected text
            bg_color = COLORS["primary"] if is_initial_selection else COLORS["bg_secondary"]
            # Changed from text_white to text_white_highlight to improve visibility
            fg_color = "#ffeb3b" if is_initial_selection else COLORS["text_primary"]  # Using a yellow color for selected items

            btn = tk.Button(btn_frame,
                          text=f"{item['icon']}{item['text']}",
                          font=button_font,
                          bg=bg_color,
                          fg=fg_color,
                          bd=0,
                          padx=10,
                          pady=8,
                          anchor="w",
                          width=25,
                          relief=tk.FLAT,
                          activebackground=COLORS["primary_light"],
                          activeforeground=COLORS["text_white"],
                          cursor="hand2",
                          justify=tk.LEFT,
                          highlightthickness=3,  # Increased highlight thickness for better visibility
                          highlightcolor=COLORS["primary"],  # Set focus color
                          highlightbackground=COLORS["bg_secondary"],  # Set inactive color
                          command=lambda i=item["name"]: self.load_module(i))
            btn.pack(side=tk.TOP, padx=0, pady=3, fill=tk.X)

            # Bind Enter key to button
            btn.bind("<Return>", lambda event, i=item["name"]: self.load_module(i))

            # Store button in the nav_buttons list for keyboard navigation
            # Use a dictionary to store module name with the button
            btn_data = {"button": btn, "module_name": item["name"]}
            self.nav_buttons.append(btn_data)

            # Store reference to button
            setattr(self, f"btn_{item['name']}", btn)

        # Add exit button at bottom
        exit_btn = tk.Button(self.nav_frame,
                           text="🚪 Exit Application",
                           font=FONTS["nav_item"],
                           bg=COLORS["bg_secondary"],
                           fg=COLORS["danger"],
                           bd=0,
                           padx=10,
                           pady=10,
                           anchor="w",
                           width=25,
                           relief=tk.FLAT,
                           activebackground=COLORS["danger"],
                           activeforeground=COLORS["text_white"],
                           cursor="hand2",
                           highlightthickness=3,  # Increased highlight thickness for better visibility
                           highlightcolor=COLORS["danger"],  # Set focus color (red for exit)
                           highlightbackground=COLORS["bg_secondary"],  # Set inactive color
                           command=self.controller.exit_application)
        exit_btn.pack(side=tk.BOTTOM, padx=0, pady=20, fill=tk.X)

        # Bind Enter key to exit button
        exit_btn.bind("<Return>", lambda event: self.controller.exit_application())

    def load_module(self, module_name):
        """Load the specified module into the content frame"""
        # Update nav button styles
        self.update_nav_selection(module_name)

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Load appropriate module frame based on selection
        frame = None
        if module_name == "products":
            # Redirect products to the inventory management with products tab active
            frame = inventory_management.InventoryManagementFrame(self.content_frame, self.controller, active_tab="products")
        elif module_name == "sales":
            frame = sales.SalesFrame(self.content_frame, self.controller)
        elif module_name == "sales_history":
            frame = sales_history.SalesHistoryFrame(self.content_frame, self.controller)
        elif module_name == "customers":
            frame = customer_management.CustomerManagementFrame(self.content_frame, self.controller)
        elif module_name == "reports":
            frame = reports.ReportsFrame(self.content_frame, self.controller)
        elif module_name == "inventory":
            frame = inventory_management.InventoryManagementFrame(self.content_frame, self.controller)
        elif module_name == "settings":
            frame = settings.SettingsFrame(self.content_frame, self.controller)
        elif module_name == "backup":
            frame = backup.BackupFrame(self.content_frame, self.controller)
        elif module_name == "cloud_sync":
            frame = cloud_sync.CloudSyncFrame(self.content_frame, self.controller)
        elif module_name == "accounting":
            frame = accounting.AccountingFrame(self.content_frame, self.controller)

        # Pack the frame if it was created
        if frame:
            frame.pack(fill=tk.BOTH, expand=True)

            # Store reference
            self.frames[module_name] = frame

            # Call on_show if method exists
            if hasattr(frame, 'on_show'):
                frame.on_show()

    def update_nav_selection(self, selected):
        """Update the styling of navigation buttons"""
        # Reset all buttons to normal state
        normal_font = FONTS["nav_item"]
        for item in ["sales", "sales_history", "inventory", "customers", "reports", "accounting", "settings", "backup", "cloud_sync"]:
            if hasattr(self, f"btn_{item}"):
                btn = getattr(self, f"btn_{item}")
                btn.config(
                    bg=COLORS["bg_secondary"], 
                    fg=COLORS["text_primary"],
                    font=normal_font
                )

        # Highlight selected button with bold font and different color
        if hasattr(self, f"btn_{selected}"):
            # Create a bold version of the nav_item font for the active section
            active_font = (FONTS["nav_item"][0], FONTS["nav_item"][1], "bold")

            btn = getattr(self, f"btn_{selected}")
            btn.config(
                bg=COLORS["primary"], 
                fg="#ffeb3b",  # Using yellow color for selected items to improve visibility
                font=active_font
            )

    def get_current_datetime(self):
        """Get formatted current date and time"""
        now = datetime.datetime.now()
        return now.strftime("%d %b %Y, %I:%M:%S %p")

    def update_datetime(self):
        """Update the datetime display"""
        self.datetime_label.config(text=self.get_current_datetime())
        # Update every second
        self.after(1000, self.update_datetime)

    def on_show(self):
        """Called when dashboard is shown"""
        # Check for low stock and expired items
        self.check_alerts()

    def handle_key_event(self, event):
        """Handle keyboard events for navigation"""
        # Only process if we have buttons in the list
        if not self.nav_buttons:
            return

        # Get current active module name
        current_module = None
        for i, btn_data in enumerate(self.nav_buttons):
            btn = btn_data["button"]
            if btn.cget("bg") == COLORS["primary"]:
                current_module = btn_data["module_name"]
                self.current_nav_index = i
                break

        if event.keysym == "Down" or event.keysym == "Right":
            # Move to the next menu item
            self.current_nav_index = (self.current_nav_index + 1) % len(self.nav_buttons)
            module_name = self.nav_buttons[self.current_nav_index]["module_name"]
            self.load_module(module_name)

        elif event.keysym == "Up" or event.keysym == "Left":
            # Move to the previous menu item
            self.current_nav_index = (self.current_nav_index - 1) % len(self.nav_buttons)
            module_name = self.nav_buttons[self.current_nav_index]["module_name"]
            self.load_module(module_name)

        elif event.keysym == "Return" or event.keysym == "space":
            # Activate currently selected menu item
            if self.current_nav_index < len(self.nav_buttons):
                module_name = self.nav_buttons[self.current_nav_index]["module_name"]
                self.load_module(module_name)

        elif event.keysym == "Escape":
            # Show confirmation dialog for exit
            if messagebox.askyesno("Exit Confirmation", "Are you sure you want to exit?"):
                self.controller.exit_application()

        # Pass the event to the active module if it has a handle_key_event method
        if self.current_nav_index < len(self.nav_buttons):
            current_module = self.nav_buttons[self.current_nav_index]["module_name"]
            if current_module in self.frames and hasattr(self.frames[current_module], 'handle_key_event'):
                self.frames[current_module].handle_key_event(event)

    def check_alerts(self):
        """Check for system alerts like low stock, expired items"""
        # Query for alerts
        # This is a simplistic implementation - would be expanded in real app

        low_stock_threshold = int(self.controller.config.get('low_stock_threshold', 10))

        # Check for low stock items
        query = """
            SELECT COUNT(*) FROM inventory
            JOIN products ON inventory.product_id = products.id
            WHERE inventory.quantity <= ?
        """
        low_stock_count = self.controller.db.fetchone(query, (low_stock_threshold,))[0]

        # Check for expiring items (items expiring in 30 days)
        today = datetime.date.today()
        thirty_days_later = today + datetime.timedelta(days=30)

        query = """
            SELECT COUNT(*) FROM inventory
            WHERE expiry_date IS NOT NULL 
            AND expiry_date <= ? 
            AND expiry_date >= ?
        """
        expiring_count = self.controller.db.fetchone(query, (thirty_days_later.isoformat(), today.isoformat()))[0]

        # Show alert if needed
        if low_stock_count > 0 or expiring_count > 0:
            alert_msg = "System Alerts:\n"
            if low_stock_count > 0:
                alert_msg += f"• {low_stock_count} products with low stock\n"
            if expiring_count > 0:
                alert_msg += f"• {expiring_count} products expiring soon\n"

            messagebox.showwarning("Inventory Alerts", alert_msg)
    
    def show_frame(self, module_name):
        """Function to load frame based on the module name."""
        self.load_module(module_name)