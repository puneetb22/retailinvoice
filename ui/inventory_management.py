"""
Inventory Management UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
from decimal import Decimal, InvalidOperation
import re
import random
from assets.styles import COLORS, FONTS, STYLES
from utils.helpers import make_button_keyboard_navigable

class InventoryManagementFrame(tk.Frame):
    """Inventory management with stock tracking, alerts and batch management"""

    def __init__(self, parent, controller, active_tab=None):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        self.active_tab = active_tab

        # Header with title
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Inventory Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure notebook style
        style = ttk.Style()
        style.configure("TNotebook", background=COLORS["bg_primary"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background=COLORS["bg_secondary"], 
                       foreground=COLORS["text_primary"],
                       padding=[10, 5],
                       font=FONTS["regular"])
        style.map("TNotebook.Tab", 
                 background=[("selected", COLORS["primary"])],
                 foreground=[("selected", COLORS["primary_light"])])

        # Create tabs
        self.products_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.inventory_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.batches_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.stock_entry_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])  # New tab
        self.alerts_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.categories_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.vendors_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.hsn_codes_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])

        self.notebook.add(self.products_tab, text="Products")
        self.notebook.add(self.inventory_tab, text="Stock Levels")
        self.notebook.add(self.batches_tab, text="Batch Management")
        self.notebook.add(self.stock_entry_tab, text="Stock Entry")  # Add new tab
        self.notebook.add(self.alerts_tab, text="Alerts & Expiry")
        self.notebook.add(self.categories_tab, text="Categories")
        self.notebook.add(self.vendors_tab, text="Vendors")
        self.notebook.add(self.hsn_codes_tab, text="HSN Codes")

        # Import utils
        from utils.helpers import make_button_keyboard_navigable
        
        # Setup tabs
        self.setup_products_tab()
        self.setup_inventory_tab()
        self.setup_batches_tab()
        self.setup_stock_entry_tab()  # Setup new tab
        self.setup_alerts_tab()
        self.setup_categories_tab()
        self.setup_vendors_tab()
        self.setup_hsn_codes_tab()
        
        # Set active tab if specified
        if self.active_tab == "products":
            self.notebook.select(0)  # Products is the first tab
        elif self.active_tab == "stock_entry":
            self.notebook.select(3)  # Stock Entry is the fourth tab

    def setup_products_tab(self):
        """Setup the products tab with product management functionality"""
        # Keyboard navigation variables
        self.current_focus = None  # Current focus area: 'products', 'buttons', 'search'
        self.selected_product_item = -1
        
        # Container
        container = tk.Frame(self.products_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Product Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Search frame
        search_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10, padx=20)
        search_frame.pack(side=tk.TOP, fill=tk.X)
        
        search_label = tk.Label(search_frame, 
                              text="Search:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace("w", lambda name, index, mode: self.search_products())
        
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.product_search_var,
                              font=FONTS["regular"],
                              width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Add product button
        add_btn = tk.Button(search_frame,
                          text="Add New Product",
                          font=FONTS["regular"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=5,
                          cursor="hand2",
                          highlightthickness=3,  # Added for focus visibility
                          highlightcolor=COLORS["primary"],  # Set focus color
                          highlightbackground=COLORS["bg_secondary"],  # Set inactive color
                          command=self.add_product)
        add_btn.pack(side=tk.RIGHT)
        
        # Make button keyboard-navigable with Enter key
        make_button_keyboard_navigable(add_btn)
        
        # Products treeview
        tree_frame = tk.Frame(container)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        self.product_tree = ttk.Treeview(tree_frame, 
                                      columns=("ID", "Code", "Name", "Vendor", "HSN", 
                                              "Wholesale", "Retail", "Tax", "Category",
                                              "Manufacturer", "Unit"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.product_tree.yview)
        
        # Define columns
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Code", text="Product Code")
        self.product_tree.heading("Name", text="Product Name")
        self.product_tree.heading("Vendor", text="Vendor")
        self.product_tree.heading("HSN", text="HSN Code")
        self.product_tree.heading("Wholesale", text="Wholesale Price")
        self.product_tree.heading("Retail", text="Retail Price")
        self.product_tree.heading("Tax", text="Tax %")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.heading("Manufacturer", text="Manufacturer")
        self.product_tree.heading("Unit", text="Unit")
        
        # Set column widths
        self.product_tree.column("ID", width=50)
        self.product_tree.column("Code", width=100)
        self.product_tree.column("Name", width=200)
        self.product_tree.column("Vendor", width=150)
        self.product_tree.column("HSN", width=100)
        self.product_tree.column("Wholesale", width=120)
        self.product_tree.column("Retail", width=120)
        self.product_tree.column("Tax", width=80)
        self.product_tree.column("Category", width=100)
        
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        
        # Binding for double-click to edit
        self.product_tree.bind("<Double-1>", self.edit_product)
        # Bind Enter key to edit product
        self.product_tree.bind("<Return>", self.edit_product)
        
        # Right-click menu for additional options
        self.context_menu = tk.Menu(container, tearoff=0, bg=COLORS["bg_white"], font=FONTS["small"])
        self.context_menu.add_command(label="Edit Product", command=self.edit_product)
        self.context_menu.add_command(label="Delete Product", command=self.delete_product)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Stock", command=self.add_stock)
        
        # Bind right-click on treeview
        self.product_tree.bind("<Button-3>", self.show_context_menu)
        
        # Information panel at the bottom
        info_frame = tk.Frame(container, bg=COLORS["bg_secondary"], pady=5)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)
        
        # Add a help icon
        help_icon = "ⓘ"  # Unicode information symbol
        help_label = tk.Label(info_frame,
                             text=help_icon,
                             font=("Arial", 16, "bold"),
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["primary"])
        help_label.pack(side=tk.LEFT, padx=5)
        
        # Info text
        info_text = "Double-click or press Enter on a product to edit it. Right-click for more options."
        info_label = tk.Label(info_frame, 
                             text=info_text,
                             font=FONTS["small_italic"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             justify=tk.LEFT)
        info_label.pack(side=tk.LEFT, padx=5)
        
        # Load products initially
        self.load_products()
        
    def setup_inventory_tab(self):
        """Setup the inventory tab with stock levels"""
        # Main container
        container = tk.Frame(self.inventory_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True)

        # Header with title and description
        header_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Current Stock Levels",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Search and action area with improved layout
        action_area = tk.Frame(container, bg=COLORS["bg_secondary"], pady=10, padx=10)
        action_area.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Search area - place search components inline for better space usage
        search_frame = tk.Frame(action_area, bg=COLORS["bg_secondary"])
        search_frame.pack(fill=tk.X, pady=5)

        search_label = tk.Label(search_frame, 
                               text="Search Product:",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_secondary"],
                               fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=5)

        self.inventory_search_var = tk.StringVar()
        self.inventory_search_var.trace("w", lambda name, index, mode: self.search_inventory())

        search_entry = tk.Entry(search_frame, 
                               textvariable=self.inventory_search_var,
                               font=FONTS["regular"],
                               width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Action buttons in a row
        button_frame = tk.Frame(search_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(side=tk.RIGHT, padx=5)

        # Refresh button
        refresh_btn = tk.Button(button_frame,
                              text="Refresh",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.load_inventory)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Add sorting options
        sort_frame = tk.Frame(action_area, bg=COLORS["bg_secondary"])
        sort_frame.pack(fill=tk.X, pady=5)

        sort_label = tk.Label(sort_frame,
                             text="Sort by:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"])
        sort_label.pack(side=tk.LEFT, padx=5)

        self.sort_options = ["Product Name", "Quantity (High to Low)", "Category"]
        self.sort_var = tk.StringVar(value=self.sort_options[0])
        sort_dropdown = ttk.Combobox(sort_frame,
                                    textvariable=self.sort_var,
                                    values=self.sort_options,
                                    width=20,
                                    state="readonly")
        sort_dropdown.pack(side=tk.LEFT, padx=5)
        sort_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_inventory())

        # Inventory treeview with improved visibility
        tree_container = tk.Frame(container, bg=COLORS["bg_primary"])
        tree_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Add a border to make the treeview stand out
        tree_frame = tk.Frame(tree_container, bd=1, relief=tk.RIDGE)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add both vertical and horizontal scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure treeview styles
        style = ttk.Style()
        style.configure("Treeview", 
                        background=COLORS["bg_white"],
                        foreground=COLORS["text_primary"],
                        rowheight=25,
                        fieldbackground=COLORS["bg_white"],
                        font=FONTS["regular"])
        style.configure("Treeview.Heading", 
                        font=FONTS["regular_bold"],
                        background=COLORS["bg_secondary"],
                        foreground=COLORS["text_primary"])

        # Create treeview with both scrollbars and increased height
        self.inventory_tree = ttk.Treeview(tree_frame, 
                                         columns=("ID", "Product", "Total Qty", "Category", "Wholesale", "Retail"),
                                         show="headings",
                                         yscrollcommand=y_scrollbar.set,
                                         xscrollcommand=x_scrollbar.set,
                                         height=20)  # Increase visible rows

        # Configure scrollbars
        y_scrollbar.config(command=self.inventory_tree.yview)
        x_scrollbar.config(command=self.inventory_tree.xview)

        # Define columns
        self.inventory_tree.heading("ID", text="Product ID")
        self.inventory_tree.heading("Product", text="Product Name")
        self.inventory_tree.heading("Total Qty", text="Total Quantity")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Wholesale", text="Wholesale Price")
        self.inventory_tree.heading("Retail", text="Retail Price")

        # Set column widths
        self.inventory_tree.column("ID", width=80, minwidth=60)
        self.inventory_tree.column("Product", width=250, minwidth=150)
        self.inventory_tree.column("Total Qty", width=100, minwidth=80)
        self.inventory_tree.column("Category", width=150, minwidth=100)
        self.inventory_tree.column("Wholesale", width=120, minwidth=100)
        self.inventory_tree.column("Retail", width=120, minwidth=100)

        self.inventory_tree.pack(fill=tk.BOTH, expand=True)

        # Color code low stock items
        self.inventory_tree.tag_configure("low_stock", background=COLORS["warning_light"])
        self.inventory_tree.tag_configure("out_of_stock", background=COLORS["danger_light"])

        # Binding for double-click to view batches
        self.inventory_tree.bind("<Double-1>", self.view_product_batches)
        # Bind Enter key directly to the treeview
        self.inventory_tree.bind("<Return>", self.view_product_batches)

        # Information and help panel at the bottom
        info_frame = tk.Frame(container, bg=COLORS["bg_secondary"], pady=5)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Add a help icon
        help_icon = "ⓘ"  # Unicode information symbol
        help_label = tk.Label(info_frame,
                             text=help_icon,
                             font=("Arial", 16, "bold"),
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["primary"])
        help_label.pack(side=tk.LEFT, padx=5)

        # Info text
        info_text = "Double-click or press Enter on a product to view its batch details. Items in yellow have low stock."
        info_label = tk.Label(info_frame, 
                             text=info_text,
                             font=FONTS["small_italic"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             justify=tk.LEFT)
        info_label.pack(side=tk.LEFT, padx=5)

    def setup_batches_tab(self):
        """Setup the batches tab with batch details"""
        # Header
        header_frame = tk.Frame(self.batches_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Batch Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Search and filter frame
        filter_frame = tk.Frame(self.batches_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        filter_frame.pack(side=tk.TOP, fill=tk.X)

        # Product dropdown
        product_label = tk.Label(filter_frame, 
                                text="Filter by Product:",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"])
        product_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.batch_product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(filter_frame, 
                                           textvariable=self.batch_product_var,
                                           font=FONTS["regular"],
                                           width=30,
                                           state="readonly")
        self.product_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.product_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_batches())

        # Show all button
        show_all_btn = tk.Button(filter_frame,
                               text="Show All Batches",
                               font=FONTS["regular"],
                               bg=COLORS["secondary"],
                               fg=COLORS["text_white"],
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=lambda: self.load_batches(show_all=True))
        show_all_btn.grid(row=0, column=2, padx=10, pady=5)

        # Batch treeview
        tree_frame = tk.Frame(self.batches_tab)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview
        self.batch_tree = ttk.Treeview(tree_frame, 
                                     columns=("ID", "Product", "Batch", "Qty", "MFG Date", 
                                            "Expiry", "Purchase Date"),
                                     show="headings",
                                     yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.batch_tree.yview)

        # Define columns
        self.batch_tree.heading("ID", text="ID")
        self.batch_tree.heading("Product", text="Product Name")
        self.batch_tree.heading("Batch", text="Batch Number")
        self.batch_tree.heading("Qty", text="Quantity")
        self.batch_tree.heading("MFG Date", text="MFG Date")
        self.batch_tree.heading("Expiry", text="Expiry Date")
        self.batch_tree.heading("Purchase Date", text="Purchase Date")

        # Set column widths
        self.batch_tree.column("ID", width=50)
        self.batch_tree.column("Product", width=250)
        self.batch_tree.column("Batch", width=100)
        self.batch_tree.column("Qty", width=80)
        self.batch_tree.column("MFG Date", width=100)
        self.batch_tree.column("Expiry", width=100)
        self.batch_tree.column("Purchase Date", width=100)
        self.batch_tree.column("Cost Price", width=100)
        self.batch_tree.column("Selling Price", width=100)

        self.batch_tree.pack(fill=tk.BOTH, expand=True)

        # Action buttons frame
        button_frame = tk.Frame(self.batches_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Edit batch button
        edit_btn = tk.Button(button_frame,
                           text="Edit Batch",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=self.edit_batch)
        edit_btn.pack(side=tk.RIGHT, padx=5)

        # Delete batch button
        delete_btn = tk.Button(button_frame,
                             text="Delete Batch",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_batch)
        delete_btn.pack(side=tk.RIGHT, padx=5)

    def setup_alerts_tab(self):
        """Setup the alerts tab with expiry and low stock alerts"""
        # Header
        header_frame = tk.Frame(self.alerts_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Inventory Alerts",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Filter frame
        filter_frame = tk.Frame(self.alerts_tab, bg=COLORS["bg_primary"], pady=10, padx=20)
        filter_frame.pack(side=tk.TOP, fill=tk.X)

        # Alert type selection
        alert_label = tk.Label(filter_frame, 
                              text="Alert Type:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        alert_label.pack(side=tk.LEFT, padx=(0, 10))

        self.alert_type_var = tk.StringVar(value="All Alerts")
        alert_options = ["All Alerts", "Low Stock", "Expiring Soon", "Expired"]

        for i, option in enumerate(alert_options):
            rb = tk.Radiobutton(filter_frame,
                              text=option,
                              variable=self.alert_type_var,
                              value=option,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.load_alerts)
            rb.pack(side=tk.LEFT, padx=10)

        # Alerts treeview
        tree_frame = tk.Frame(self.alerts_tab)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview
        self.alerts_tree = ttk.Treeview(tree_frame, 
                                      columns=("Type", "Product", "Current Qty", "Batch", 
                                             "Expiry", "Status"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.alerts_tree.yview)

        # Define columns
        self.alerts_tree.heading("Type", text="Alert Type")
        self.alerts_tree.heading("Product", text="Product Name")
        self.alerts_tree.heading("Current Qty", text="Current Qty")
        self.alerts_tree.heading("Batch", text="Batch Number")
        self.alerts_tree.heading("Expiry", text="Expiry Date")
        self.alerts_tree.heading("Status", text="Status")

        # Set column widths
        self.alerts_tree.column("Type", width=100)
        self.alerts_tree.column("Product", width=250)
        self.alerts_tree.column("Current Qty", width=100)
        self.alerts_tree.column("Batch", width=100)
        self.alerts_tree.column("Expiry", width=100)
        self.alerts_tree.column("Status", width=120)

        self.alerts_tree.pack(fill=tk.BOTH, expand=True)

        # Tag configurations for color coding
        self.alerts_tree.tag_configure("expired", background=COLORS["danger_light"])
        self.alerts_tree.tag_configure("expiring", background=COLORS["warning_light"])
        self.alerts_tree.tag_configure("low_stock", background=COLORS["info_light"])

    def load_inventory(self):
        """Load inventory data into the stock levels tab"""
        # Clear current items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get low stock threshold from settings
        low_stock_threshold = 10  # Default value
        threshold_setting = self.controller.db.fetchone("SELECT value FROM settings WHERE key = 'low_stock_threshold'")
        if threshold_setting and threshold_setting[0]:
            try:
                low_stock_threshold = int(threshold_setting[0])
            except (ValueError, TypeError):
                pass  # Use default if conversion fails
                
        # Base query to get inventory summary from batches table WITHOUT min_stock_level (not in schema)
        query = """
            SELECT p.id, p.name, COALESCE(SUM(b.quantity), 0) as total_qty, p.category, 
                   p.wholesale_price, p.selling_price
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id
            GROUP BY p.id
        """

        # Add sorting based on selected option
        sort_option = self.sort_var.get() if hasattr(self, 'sort_var') else "Product Name"

        if sort_option == "Quantity (High to Low)":
            query += " ORDER BY total_qty DESC, p.name"
        elif sort_option == "Category":
            query += " ORDER BY p.category, p.name"
        else:  # Default: Product Name
            query += " ORDER BY p.name"

        inventory = self.controller.db.fetchall(query)

        # Insert into treeview with color coding for stock levels
        for item in inventory:
            # Handle None for quantity
            quantity = item[2] if item[2] is not None else 0

            # Get minimum stock level (default to 10 if not set)
            min_stock = low_stock_threshold

            # Format the row
            row = (
                item[0],
                item[1],
                quantity,
                item[3] if item[3] else "",
                f"₹{item[4]:.2f}",
                f"₹{item[5]:.2f}"
            )

            # Determine tag based on stock level
            tag = ""
            if quantity <= 0:
                tag = "out_of_stock"
            elif quantity < min_stock:
                tag = "low_stock"

            # Insert into treeview with appropriate tag
            if tag:
                self.inventory_tree.insert("", "end", values=row, tags=(tag,))
            else:
                self.inventory_tree.insert("", "end", values=row)

    def search_inventory(self):
        """Search inventory based on search term"""
        search_term = self.inventory_search_var.get().strip().lower()

        # Clear current items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        if not search_term:
            # If search is empty, load all inventory
            self.load_inventory()
            return
            
        # Get low stock threshold from settings
        low_stock_threshold = 10  # Default value
        threshold_setting = self.controller.db.fetchone("SELECT value FROM settings WHERE key = 'low_stock_threshold'")
        if threshold_setting and threshold_setting[0]:
            try:
                low_stock_threshold = int(threshold_setting[0])
            except (ValueError, TypeError):
                pass  # Use default if conversion fails

        # Get filtered inventory without min_stock_level (not in schema) - using batches table
        query = """
            SELECT p.id, p.name, COALESCE(SUM(b.quantity), 0) as total_qty, p.category, 
                   p.wholesale_price, p.selling_price
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id
            WHERE LOWER(p.name) LIKE ? OR LOWER(p.product_code) LIKE ? OR LOWER(p.category) LIKE ?
            GROUP BY p.id
            ORDER BY p.name
        """
        search_pattern = f"%{search_term}%"
        inventory = self.controller.db.fetchall(query, (search_pattern, search_pattern, search_pattern))

        # Insert into treeview with color coding for stock levels
        for item in inventory:
            # Handle None for quantity
            quantity = item[2] if item[2] is not None else 0

            # Use the low_stock_threshold from settings
            min_stock = low_stock_threshold

            # Format the row
            row = (
                item[0],
                item[1],
                quantity,
                item[3] if item[3] else "",
                f"₹{item[4]:.2f}",
                f"₹{item[5]:.2f}"
            )

            # Determine tag based on stock level
            tag = ""
            if quantity <= 0:
                tag = "out_of_stock"
            elif quantity < min_stock:
                tag = "low_stock"

            # Insert into treeview with appropriate tag
            if tag:
                self.inventory_tree.insert("", "end", values=row, tags=(tag,))
            else:
                self.inventory_tree.insert("", "end", values=row)

    def load_product_dropdown(self):
        """Load products into the dropdown for batch filtering"""
        # Get products from database
        query = "SELECT id, name FROM products ORDER BY name"
        products = self.controller.db.fetchall(query)

        # Format for dropdown (ID: Name)
        product_list = [f"{product[0]}: {product[1]}" for product in products]

        # Update dropdown values
        self.product_dropdown["values"] = ["-- Select Product --"] + product_list
        self.product_dropdown.current(0)

    def load_batches(self, show_all=False):
        """Load batch data into the batches tab"""
        # Clear current items
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)

        # Query with error handling for selling_price column
        try:
            # Try to query with selling_price column
            query = """
                SELECT b.id, p.name, b.batch_number, b.quantity, 
                       b.manufacturing_date, b.expiry_date, b.purchase_date,
                       b.cost_price, COALESCE(b.selling_price, p.selling_price) as selling_price
                FROM batches b
                JOIN products p ON b.product_id = p.id
            """
            
            # Add filter if not showing all
            if not show_all and self.batch_product_var.get() and ":" in self.batch_product_var.get():
                product_id = self.batch_product_var.get().split(":")[0]
                query += f" WHERE b.product_id = {product_id}"

            query += " ORDER BY p.name, b.expiry_date"

            # Get batches from database
            batches = self.controller.db.fetchall(query)
            
            # Insert into treeview with price columns
            for batch in batches:
                # Format dates
                mfg_date = batch[4] if batch[4] else ""
                exp_date = batch[5] if batch[5] else ""
                purchase_date = batch[6] if batch[6] else ""
                cost_price = f"₹{batch[7]:.2f}" if batch[7] else "₹0.00"
                selling_price = f"₹{batch[8]:.2f}" if batch[8] else "₹0.00"

                row = (
                    batch[0],
                    batch[1],
                    batch[2] if batch[2] else "",
                    batch[3],
                    mfg_date,
                    exp_date,
                    purchase_date,
                    cost_price,
                    selling_price
                )

                self.batch_tree.insert("", "end", values=row)
                
        except Exception as e:
            print(f"Error loading batches with selling_price: {e}")
            # Fallback query without selling_price column
            query = """
                SELECT b.id, p.name, b.batch_number, b.quantity, 
                       b.manufacturing_date, b.expiry_date, b.purchase_date,
                       b.cost_price
                FROM batches b
                JOIN products p ON b.product_id = p.id
            """
            
            # Add filter if not showing all
            if not show_all and self.batch_product_var.get() and ":" in self.batch_product_var.get():
                product_id = self.batch_product_var.get().split(":")[0]
                query += f" WHERE b.product_id = {product_id}"

            query += " ORDER BY p.name, b.expiry_date"

            # Get batches from database
            batches = self.controller.db.fetchall(query)

            # Insert into treeview without selling price
            for batch in batches:
                # Format dates
                mfg_date = batch[4] if batch[4] else ""
                exp_date = batch[5] if batch[5] else ""
                purchase_date = batch[6] if batch[6] else ""
                cost_price = f"₹{batch[7]:.2f}" if len(batch) > 7 and batch[7] else "₹0.00"

                row = (
                    batch[0],
                    batch[1],
                    batch[2] if batch[2] else "",
                    batch[3],
                    mfg_date,
                    exp_date,
                    purchase_date,
                    cost_price,
                    "₹0.00"  # Default selling price
                )

                self.batch_tree.insert("", "end", values=row)

    def load_alerts(self):
        """Load alert data into the alerts tab"""
        # Clear current items
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)

        alert_type = self.alert_type_var.get()

        # Get low stock threshold from settings
        low_stock_threshold = int(self.controller.config.get('low_stock_threshold', 10))

        # Get current date for expiry comparisons
        today = datetime.date.today()
        thirty_days_later = today + datetime.timedelta(days=30)

        # Build query based on alert type
        if alert_type == "Low Stock" or alert_type == "All Alerts":
            # Low stock query
            query = """
                SELECT 'Low Stock' as alert_type, p.name, b.quantity, b.batch_number, 
                       b.expiry_date, 'Low Stock' as status
                FROM batches b
                JOIN products p ON b.product_id = p.id
                WHERE b.quantity <= ?
                ORDER BY b.quantity
            """

            # Get low stock items
            low_stock_items = self.controller.db.fetchall(query, (low_stock_threshold,))

            # Insert into treeview
            for item in low_stock_items:
                self.alerts_tree.insert("", "end", values=item, tags=("low_stock",))

        if alert_type == "Expiring Soon" or alert_type == "All Alerts":
            # Expiring soon query
            query = """
                SELECT 'Expiring Soon' as alert_type, p.name, b.quantity, b.batch_number, 
                       b.expiry_date, 'Expiring Soon' as status
                FROM batches b
                JOIN products p ON b.product_id = p.id
                WHERE b.expiry_date IS NOT NULL 
                AND b.expiry_date <= ? 
                AND b.expiry_date >= ?
                AND b.quantity > 0
                ORDER BY b.expiry_date
            """

            # Get expiring items
            expiring_items = self.controller.db.fetchall(query, 
                (thirty_days_later.isoformat(), today.isoformat()))

            # Insert into treeview
            for item in expiring_items:
                self.alerts_tree.insert("", "end", values=item, tags=("expiring",))

        if alert_type == "Expired" or alert_type == "All Alerts":
            # Expired query
            query = """
                SELECT 'Expired' as alert_type, p.name, b.quantity, b.batch_number, 
                       b.expiry_date, 'Expired' as status
                FROM batches b
                JOIN products p ON b.product_id = p.id
                WHERE b.expiry_date IS NOT NULL 
                AND b.expiry_date < ?
                AND b.quantity > 0
                ORDER BY b.expiry_date
            """

            # Get expired items
            expired_items = self.controller.db.fetchall(query, (today.isoformat(),))

            # Insert into treeview
            for item in expired_items:
                self.alerts_tree.insert("", "end", values=item, tags=("expired",))

    def view_product_batches(self, event=None):
        """View batches for selected product"""
        # Get selected product
        selection = self.inventory_tree.selection()
        if not selection:
            return

        # Get product ID and name
        product_id = self.inventory_tree.item(selection[0])["values"][0]
        product_name = self.inventory_tree.item(selection[0])["values"][1]

        # Switch to batches tab
        self.notebook.select(1)  # Select batches tab

        # Set filter and load batches
        product_entry = f"{product_id}: {product_name}"
        self.batch_product_var.set(product_entry)
        self.load_batches()

    def edit_batch(self):
        """Edit selected batch"""
        # Get selected batch
        selection = self.batch_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a batch to edit.")
            return

        # Get batch ID
        batch_id = self.batch_tree.item(selection[0])["values"][0]

        # Get batch data
        query = """
            SELECT b.*, p.name 
            FROM batches b
            JOIN products p ON b.product_id = p.id
            WHERE b.id = ?
        """
        batch = self.controller.db.fetchone(query, (batch_id,))

        if not batch:
            messagebox.showerror("Error", "Batch not found.")
            return

        # Column names for reference
        columns = [description[0] for description in self.controller.db.cursor.description]

        # Create edit batch dialog
        batch_dialog = tk.Toplevel(self)
        batch_dialog.title("Edit Batch")
        batch_dialog.geometry("500x400")
        batch_dialog.resizable(False, False)
        batch_dialog.configure(bg=COLORS["bg_primary"])
        batch_dialog.grab_set()  # Make window modal

        # Center the dialog
        batch_dialog.update_idletasks()
        width = batch_dialog.winfo_width()
        height = batch_dialog.winfo_height()
        x = (batch_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (batch_dialog.winfo_screenheight() // 2) - (height // 2)
        batch_dialog.geometry(f"+{x}+{y}")

        # Get product name (last column from join)
        product_name = batch[-1]

        # Create form
        title = tk.Label(batch_dialog, 
                        text=f"Edit Batch for: {product_name}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"],
                        wraplength=450)
        title.pack(pady=15)

        # Form frame
        form_frame = tk.Frame(batch_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Create form fields
        batch_label = tk.Label(form_frame, 
                              text="Batch Number:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        batch_label.grid(row=0, column=0, sticky="w", pady=8)

        batch_var = tk.StringVar()
        batch_idx = columns.index("batch_number")
        if batch[batch_idx]:
            batch_var.set(batch[batch_idx])

        batch_entry = tk.Entry(form_frame, 
                              textvariable=batch_var,
                              font=FONTS["regular"],
                              width=30)
        batch_entry.grid(row=0, column=1, sticky="w", pady=8, padx=10)

        # Quantity
        quantity_label = tk.Label(form_frame, 
                                text="Quantity:",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"])
        quantity_label.grid(row=1, column=0, sticky="w", pady=8)

        quantity_var = tk.StringVar()
        quantity_idx = columns.index("quantity")
        quantity_var.set(batch[quantity_idx])

        quantity_entry = tk.Entry(form_frame, 
                                textvariable=quantity_var,
                                font=FONTS["regular"],
                                width=30)
        quantity_entry.grid(row=1, column=1, sticky="w", pady=8, padx=10)

        # Manufacturing date
        mfg_label = tk.Label(form_frame, 
                            text="Manufacturing Date (YYYY-MM-DD):",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        mfg_label.grid(row=2, column=0, sticky="w", pady=8)

        mfg_var = tk.StringVar()
        mfg_idx = columns.index("manufacturing_date")
        if batch[mfg_idx]:
            mfg_var.set(batch[mfg_idx])

        mfg_entry = tk.Entry(form_frame, 
                            textvariable=mfg_var,
                            font=FONTS["regular"],
                            width=30)
        mfg_entry.grid(row=2, column=1, sticky="w", pady=8, padx=10)

        # Expiry date
        exp_label = tk.Label(form_frame, 
                            text="Expiry Date (YYYY-MM-DD):",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        exp_label.grid(row=3, column=0, sticky="w", pady=8)

        exp_var = tk.StringVar()
        exp_idx = columns.index("expiry_date")
        if batch[exp_idx]:
            exp_var.set(batch[exp_idx])

        exp_entry = tk.Entry(form_frame, 
                            textvariable=exp_var,
                            font=FONTS["regular"],
                            width=30)
        exp_entry.grid(row=3, column=1, sticky="w", pady=8, padx=10)

        # Buttons frame
        button_frame = tk.Frame(batch_dialog, bg=COLORS["bg_primary"], pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=batch_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)

        # Function to update batch
        def update_batch():
            # Validate required fields
            if not quantity_var.get().strip():
                messagebox.showerror("Error", "Quantity is required.")
                return

            # Validate quantity is a number
            try:
                quantity = int(quantity_var.get())
                if quantity < 0:
                    messagebox.showerror("Error", "Quantity cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number.")
                return

            # Validate dates if provided
            mfg_date = mfg_var.get().strip()
            exp_date = exp_var.get().strip()

            # Create batch data
            batch_data = {
                "batch_number": batch_var.get().strip(),
                "quantity": quantity
            }

            if mfg_date:
                try:
                    datetime.date.fromisoformat(mfg_date)
                    batch_data["manufacturing_date"] = mfg_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid manufacturing date format. Use YYYY-MM-DD.")
                    return

            if exp_date:
                try:
                    datetime.date.fromisoformat(exp_date)
                    batch_data["expiry_date"] = exp_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid expiry date format. Use YYYY-MM-DD.")
                    return

            # Get old quantity for transaction record
            old_quantity = batch[quantity_idx]

            # Update in database
            updated = self.controller.db.update("batches", batch_data, f"id = {batch_id}")

            if updated:
                # Add transaction record if quantity changed
                if old_quantity != quantity:
                    # Difference in quantity
                    qty_diff = quantity - old_quantity

                    if qty_diff != 0:
                        # Create transaction record
                        transaction_data = {
                            "product_id": batch[columns.index("product_id")],
                            "batch_number": batch_var.get().strip(),
                            "quantity": abs(qty_diff),
                            "transaction_type": "STOCK_IN" if qty_diff > 0 else "STOCK_OUT",
                            "reference_id": batch_id,
                            "notes": "Batch update"
                        }
                        self.controller.db.insert("inventory_transactions", transaction_data)

                messagebox.showinfo("Success", "Batch updated successfully!")
                batch_dialog.destroy()

                # Refresh data
                self.load_batches()
                self.load_inventory()
                self.load_alerts()
            else:
                messagebox.showerror("Error", "Failed to update batch.")

        # Save button
        save_btn = tk.Button(button_frame,
                           text="Update Batch",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=update_batch)
        save_btn.pack(side=tk.RIGHT, padx=5)

    def delete_batch(self):
        """Delete selected batch"""
        # Get selected batch
        selection = self.batch_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a batch to delete.")
            return

        # Get batch details
        batch_id = self.batch_tree.item(selection[0])["values"][0]
        product_name = self.batch_tree.item(selection[0])["values"][1]
        batch_number = self.batch_tree.item(selection[0])["values"][2]

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete batch {batch_number} of '{product_name}'?"):
            return

        # Delete from database
        deleted = self.controller.db.delete("batches", f"id = {batch_id}")

        if deleted:
            messagebox.showinfo("Success", "Batch deleted successfully!")
            # Refresh data
            self.load_batches()
            self.load_inventory()
            self.load_alerts()
        else:
            messagebox.showerror("Error", "Failed to delete batch.")

    def setup_categories_tab(self):
        """Setup the categories management tab"""
        # Header
        header_frame = tk.Frame(self.categories_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Product Categories",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Split frame into left (list) and right (form) sections
        main_frame = tk.Frame(self.categories_tab, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left side - Category list
        list_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Treeview for categories
        tree_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Categories treeview
        self.categories_tree = ttk.Treeview(tree_frame, 
                                         columns=("ID", "Name", "Description"),
                                         show="headings",
                                         yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.categories_tree.yview)

        # Define columns
        self.categories_tree.heading("ID", text="ID")
        self.categories_tree.heading("Name", text="Category Name")
        self.categories_tree.heading("Description", text="Description")

        # Set column widths
        self.categories_tree.column("ID", width=50)
        self.categories_tree.column("Name", width=150)
        self.categories_tree.column("Description", width=200)

        self.categories_tree.pack(fill=tk.BOTH, expand=True)

        # Right side - Category form
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Category form
        form_title = tk.Label(form_frame, 
                           text="Add/Edit Category",
                           font=FONTS["subheading"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Category name
        name_label = tk.Label(form_frame, 
                            text="Category Name:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        name_label.grid(row=1, column=0, sticky="w", pady=5)

        self.category_name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, 
                            textvariable=self.category_name_var,
                            font=FONTS["regular"],
                            width=30)
        name_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Description
        desc_label = tk.Label(form_frame, 
                            text="Description:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        desc_label.grid(row=2, column=0, sticky="w", pady=5)

        self.category_desc_var = tk.StringVar()
        desc_entry = tk.Entry(form_frame, 
                            textvariable=self.category_desc_var,
                            font=FONTS["regular"],
                            width=30)
        desc_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="w")

        # Save button
        self.category_save_btn = tk.Button(btn_frame,
                                       text="Save Category",
                                       font=FONTS["regular"],
                                       bg=COLORS["primary"],
                                       fg=COLORS["text_white"],
                                       padx=15,
                                       pady=5,
                                       cursor="hand2",
                                       command=self.save_category)
        self.category_save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # New button
        new_category_btn = tk.Button(btn_frame,
                                  text="New Category",
                                  font=FONTS["regular"],
                                  bg=COLORS["secondary"],
                                  fg=COLORS["text_white"],
                                  padx=15,
                                  pady=5,
                                  cursor="hand2",
                                  command=self.new_category)
        new_category_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        delete_category_btn = tk.Button(btn_frame,
                                     text="Delete Category",
                                     font=FONTS["regular"],
                                     bg=COLORS["danger"],
                                     fg=COLORS["text_white"],
                                     padx=15,
                                     pady=5,
                                     cursor="hand2",
                                     command=self.delete_category)
        delete_category_btn.pack(side=tk.LEFT)

        # Bind treeview selection
        self.categories_tree.bind("<<TreeviewSelect>>", self.on_category_select)

        # Status variable
        self.category_id_var = None
        self.category_mode = "add"  # 'add' or 'edit'

    def setup_vendors_tab(self):
        """Setup the vendors management tab"""
        # Header
        header_frame = tk.Frame(self.vendors_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Vendor Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Split frame into left (list) and right (form) sections
        main_frame = tk.Frame(self.vendors_tab, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left side - Vendor list
        list_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Treeview for vendors
        tree_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Vendors treeview
        self.vendors_tree = ttk.Treeview(tree_frame, 
                                      columns=("ID", "Name", "Contact", "Phone", "GSTIN"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.vendors_tree.yview)

        # Define columns
        self.vendors_tree.heading("ID", text="ID")
        self.vendors_tree.heading("Name", text="Vendor Name")
        self.vendors_tree.heading("Contact", text="Contact Person")
        self.vendors_tree.heading("Phone", text="Phone")
        self.vendors_tree.heading("GSTIN", text="GSTIN")

        # Set column widths
        self.vendors_tree.column("ID", width=50)
        self.vendors_tree.column("Name", width=150)
        self.vendors_tree.column("Contact", width=150)
        self.vendors_tree.column("Phone", width=120)
        self.vendors_tree.column("GSTIN", width=150)

        self.vendors_tree.pack(fill=tk.BOTH, expand=True)

        # Right side - Vendor form
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Vendor form
        form_title = tk.Label(form_frame, 
                           text="Add/Edit Vendor",
                           font=FONTS["subheading"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Vendor name
        name_label = tk.Label(form_frame, 
                            text="Vendor Name:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        name_label.grid(row=1, column=0, sticky="w", pady=5)

        self.vendor_name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, 
                            textvariable=self.vendor_name_var,
                            font=FONTS["regular"],
                            width=30)
        name_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Contact person
        contact_label = tk.Label(form_frame, 
                              text="Contact Person:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        contact_label.grid(row=2, column=0, sticky="w", pady=5)

        self.vendor_contact_var = tk.StringVar()
        contact_entry = tk.Entry(form_frame, 
                              textvariable=self.vendor_contact_var,
                              font=FONTS["regular"],
                              width=30)
        contact_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Phone
        phone_label = tk.Label(form_frame, 
                             text="Phone:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        phone_label.grid(row=3, column=0, sticky="w", pady=5)

        self.vendor_phone_var = tk.StringVar()
        phone_entry = tk.Entry(form_frame, 
                             textvariable=self.vendor_phone_var,
                             font=FONTS["regular"],
                             width=30)
        phone_entry.grid(row=3, column=1, sticky="w", pady=5)

        # Email
        email_label = tk.Label(form_frame, 
                             text="Email:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        email_label.grid(row=4, column=0, sticky="w", pady=5)

        self.vendor_email_var = tk.StringVar()
        email_entry = tk.Entry(form_frame, 
                             textvariable=self.vendor_email_var,
                             font=FONTS["regular"],
                             width=30)
        email_entry.grid(row=4, column=1, sticky="w", pady=5)

        # Address
        address_label = tk.Label(form_frame, 
                               text="Address:",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        address_label.grid(row=5, column=0, sticky="w", pady=5)

        self.vendor_address_var = tk.StringVar()
        address_entry = tk.Entry(form_frame, 
                               textvariable=self.vendor_address_var,
                               font=FONTS["regular"],
                               width=30)
        address_entry.grid(row=5, column=1, sticky="w", pady=5)

        # GSTIN
        gstin_label = tk.Label(form_frame, 
                             text="GSTIN:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        gstin_label.grid(row=6, column=0, sticky="w", pady=5)

        self.vendor_gstin_var = tk.StringVar()
        gstin_entry = tk.Entry(form_frame, 
                             textvariable=self.vendor_gstin_var,
                             font=FONTS["regular"],
                             width=30)
        gstin_entry.grid(row=6, column=1, sticky="w", pady=5)

        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="w")

        # Save button
        self.vendor_save_btn = tk.Button(btn_frame,
                                     text="Save Vendor",
                                     font=FONTS["regular"],
                                     bg=COLORS["primary"],
                                     fg=COLORS["text_white"],
                                     padx=15,
                                     pady=5,
                                     cursor="hand2",
                                     command=self.save_vendor)
        self.vendor_save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # New button
        new_vendor_btn = tk.Button(btn_frame,
                                text="New Vendor",
                                font=FONTS["regular"],
                                bg=COLORS["secondary"],
                                fg=COLORS["text_white"],
                                padx=15,
                                pady=5,
                                cursor="hand2",
                                command=self.new_vendor)
        new_vendor_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        delete_vendor_btn = tk.Button(btn_frame,
                                   text="Delete Vendor",
                                   font=FONTS["regular"],
                                   bg=COLORS["danger"],
                                   fg=COLORS["text_white"],
                                   padx=15,
                                   pady=5,
                                   cursor="hand2",
                                   command=self.delete_vendor)
        delete_vendor_btn.pack(side=tk.LEFT)

        # Bind treeview selection
        self.vendors_tree.bind("<<TreeviewSelect>>", self.on_vendor_select)

        # Status variable
        self.vendor_id_var = None
        self.vendor_mode = "add"  # 'add' or 'edit'

    def setup_hsn_codes_tab(self):
        """Setup the HSN codes management tab"""
        # Header
        header_frame = tk.Frame(self.hsn_codes_tab, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="HSN Codes Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Split frame into left (list) and right (form) sections
        main_frame = tk.Frame(self.hsn_codes_tab, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left side - HSN codes list
        list_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Search frame
        search_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"], pady=10)
        search_frame.pack(side=tk.TOP, fill=tk.X)

        search_label = tk.Label(search_frame, 
                              text="Search HSN Code:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.hsn_search_var = tk.StringVar()
        self.hsn_search_var.trace("w", lambda name, index, mode: self.search_hsn())

        search_entry = tk.Entry(search_frame, 
                              textvariable=self.hsn_search_var,
                              font=FONTS["regular"],
                              width=30)
        search_entry.pack(side=tk.LEFT)

        # Treeview for HSN codes
        tree_frame = tk.Frame(list_frame, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # HSN codes treeview
        self.hsn_tree = ttk.Treeview(tree_frame, 
                                   columns=("ID", "Code", "Description", "Tax Rate"),
                                   show="headings",
                                   yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.hsn_tree.yview)

        # Define columns
        self.hsn_tree.heading("ID", text="ID")
        self.hsn_tree.heading("Code", text="HSN Code")
        self.hsn_tree.heading("Description", text="Description")
        self.hsn_tree.heading("Tax Rate", text="Tax Rate (%)")

        # Set column widths
        self.hsn_tree.column("ID", width=50)
        self.hsn_tree.column("Code", width=100)
        self.hsn_tree.column("Description", width=250)
        self.hsn_tree.column("Tax Rate", width=100)

        self.hsn_tree.pack(fill=tk.BOTH, expand=True)

        # Right side - HSN code form
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], width=400)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # HSN code form
        form_title = tk.Label(form_frame, 
                           text="Add/Edit HSN Code",
                           font=FONTS["subheading"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # HSN code
        code_label = tk.Label(form_frame, 
                            text="HSN Code:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        code_label.grid(row=1, column=0, sticky="w", pady=5)

        self.hsn_code_var = tk.StringVar()
        code_entry = tk.Entry(form_frame, 
                            textvariable=self.hsn_code_var,
                            font=FONTS["regular"],
                            width=30)
        code_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Description
        desc_label = tk.Label(form_frame, 
                            text="Description:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        desc_label.grid(row=2, column=0, sticky="w", pady=5)

        self.hsn_desc_var = tk.StringVar()
        desc_entry = tk.Entry(form_frame, 
                            textvariable=self.hsn_desc_var,
                            font=FONTS["regular"],
                            width=30)
        desc_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Tax rate
        tax_label = tk.Label(form_frame, 
                           text="Tax Rate (%):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        tax_label.grid(row=3, column=0, sticky="w", pady=5)

        self.hsn_tax_var = tk.StringVar()
        tax_entry = tk.Entry(form_frame, 
                           textvariable=self.hsn_tax_var,
                           font=FONTS["regular"],
                           width=30)
        tax_entry.grid(row=3, column=1, sticky="w", pady=5)

        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=20)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="w")

        # Save button
        self.hsn_save_btn = tk.Button(btn_frame,
                                   text="Save HSN Code",
                                   font=FONTS["regular"],
                                   bg=COLORS["primary"],
                                   fg=COLORS["text_white"],
                                   padx=15,
                                   pady=5,
                                   cursor="hand2",
                                   command=self.save_hsn)
        self.hsn_save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # New button
        new_hsn_btn = tk.Button(btn_frame,
                              text="New HSN Code",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.new_hsn)
        new_hsn_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        delete_hsn_btn = tk.Button(btn_frame,
                                 text="Delete HSN Code",
                                 font=FONTS["regular"],
                                 bg=COLORS["danger"],
                                 fg=COLORS["text_white"],
                                 padx=15,
                                 pady=5,
                                 cursor="hand2",
                                 command=self.delete_hsn)
        delete_hsn_btn.pack(side=tk.LEFT)

        # Bind treeview selection
        self.hsn_tree.bind("<<TreeviewSelect>>", self.on_hsn_select)

        # Status variable
        self.hsn_id_var = None
        self.hsn_mode = "add"  # 'add' or 'edit'

    def setup_stock_entry_tab(self):
        """Setup the stock entry tab for adding new stock with improved UI and batch management"""
        # Create header
        header_frame = tk.Frame(self.stock_entry_tab, bg=COLORS["primary"])
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        header_label = tk.Label(header_frame, 
                              text="Stock Entry - Batch Management",
                              font=FONTS["heading"],
                              bg=COLORS["primary"],
                              fg=COLORS["text_white"])
        header_label.pack(pady=10)
        
        # Create main container
        main_container = tk.Frame(self.stock_entry_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left side - Entry form with modern layout
        form_container = tk.Frame(main_container, bg=COLORS["bg_primary"])
        form_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create labeled frame for the form
        form_labelframe = tk.LabelFrame(form_container, 
                                       text="Stock Entry Form",
                                       font=FONTS["regular_bold"],
                                       bg=COLORS["bg_primary"],
                                       fg=COLORS["text_primary"],
                                       padx=20,
                                       pady=15)
        form_labelframe.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create grid container inside the labeled frame
        grid_frame = tk.Frame(form_labelframe, bg=COLORS["bg_primary"])
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns
        grid_frame.columnconfigure(0, weight=0, minsize=150)  # Labels column
        grid_frame.columnconfigure(1, weight=1, minsize=300)  # Inputs column
        
        row = 0
        
        # Product selection
        tk.Label(grid_frame, 
                text="Select Product:",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                anchor="w").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        
        self.stock_product_var = tk.StringVar()
        self.stock_product_dropdown = ttk.Combobox(grid_frame, 
                                                 textvariable=self.stock_product_var,
                                                 font=FONTS["regular"],
                                                 width=40,
                                                 state="readonly")
        self.stock_product_dropdown.grid(row=row, column=1, sticky="ew", pady=8)
        self.stock_product_dropdown.bind("<<ComboboxSelected>>", self.on_stock_product_select)
        row += 1
        
        # Existing batches info section
        tk.Label(grid_frame, 
                text="Existing Batches:",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                anchor="w").grid(row=row, column=0, sticky="nw", padx=(0, 10), pady=8)
        
        self.existing_batches_frame = tk.Frame(grid_frame, 
                                             bg=COLORS["bg_secondary"], 
                                             relief=tk.RIDGE, 
                                             bd=1)
        self.existing_batches_frame.grid(row=row, column=1, sticky="ew", pady=8)
        
        existing_label = tk.Label(self.existing_batches_frame, 
                                text="Select product to view existing batches",
                                font=FONTS["small"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_secondary"])
        existing_label.pack(padx=10, pady=5)
        row += 1
        
        # Batch mode selection
        tk.Label(grid_frame, 
                text="Batch Mode:",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                anchor="w").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        
        batch_mode_frame = tk.Frame(grid_frame, bg=COLORS["bg_primary"])
        batch_mode_frame.grid(row=row, column=1, sticky="ew", pady=8)
        
        self.batch_mode_var = tk.StringVar(value="existing")
        
        existing_radio = tk.Radiobutton(batch_mode_frame,
                                      text="Add to Existing Batch",
                                      variable=self.batch_mode_var,
                                      value="existing",
                                      font=FONTS["regular"],
                                      bg=COLORS["bg_primary"],
                                      fg=COLORS["text_primary"],
                                      selectcolor=COLORS["bg_primary"],
                                      command=self.on_batch_mode_change)
        existing_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        new_radio = tk.Radiobutton(batch_mode_frame,
                                 text="Create New Batch",
                                 variable=self.batch_mode_var,
                                 value="new",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"],
                                 selectcolor=COLORS["bg_primary"],
                                 command=self.on_batch_mode_change)
        new_radio.pack(side=tk.LEFT)
        row += 1
        
        # Existing batch selection
        self.existing_batch_label = tk.Label(grid_frame, 
                                           text="Select Batch:",
                                           font=FONTS["regular"],
                                           bg=COLORS["bg_primary"],
                                           fg=COLORS["text_primary"],
                                           anchor="w")
        self.existing_batch_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        
        self.existing_batch_var = tk.StringVar()
        self.existing_batch_dropdown = ttk.Combobox(grid_frame, 
                                                   textvariable=self.existing_batch_var,
                                                   font=FONTS["regular"],
                                                   width=40,
                                                   state="readonly")
        self.existing_batch_dropdown.grid(row=row, column=1, sticky="ew", pady=8)
        self.existing_batch_dropdown.bind("<<ComboboxSelected>>", self.on_existing_batch_select)
        row += 1
        
        # New batch fields (initially hidden)
        self.new_batch_fields = []
        
        # Batch number
        batch_number_label = tk.Label(grid_frame, 
                                    text="Batch Number:",
                                    font=FONTS["regular"],
                                    bg=COLORS["bg_primary"],
                                    fg=COLORS["text_primary"],
                                    anchor="w")
        batch_number_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        self.new_batch_fields.append(batch_number_label)
        
        self.batch_number_var = tk.StringVar()
        batch_number_entry = tk.Entry(grid_frame, 
                                    textvariable=self.batch_number_var,
                                    font=FONTS["regular"],
                                    width=42)
        batch_number_entry.grid(row=row, column=1, sticky="ew", pady=8)
        self.new_batch_fields.append(batch_number_entry)
        row += 1
        
        # Manufacturing date
        mfg_label = tk.Label(grid_frame, 
                           text="Manufacturing Date:",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"],
                           anchor="w")
        mfg_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        self.new_batch_fields.append(mfg_label)
        
        self.mfg_date_var = tk.StringVar()
        self.mfg_date_var.set(datetime.datetime.now().strftime("%Y-%m-%d"))
        mfg_entry = tk.Entry(grid_frame, 
                           textvariable=self.mfg_date_var,
                           font=FONTS["regular"],
                           width=42)
        mfg_entry.grid(row=row, column=1, sticky="ew", pady=8)
        self.new_batch_fields.append(mfg_entry)
        row += 1
        
        # Expiry date
        expiry_label = tk.Label(grid_frame, 
                              text="Expiry Date:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              anchor="w")
        expiry_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        self.new_batch_fields.append(expiry_label)
        
        self.expiry_date_var = tk.StringVar()
        expiry_entry = tk.Entry(grid_frame, 
                              textvariable=self.expiry_date_var,
                              font=FONTS["regular"],
                              width=42)
        expiry_entry.grid(row=row, column=1, sticky="ew", pady=8)
        self.new_batch_fields.append(expiry_entry)
        row += 1
        
        # Wholesale price
        wholesale_label = tk.Label(grid_frame, 
                                 text="Wholesale Price:",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"],
                                 anchor="w")
        wholesale_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        self.new_batch_fields.append(wholesale_label)
        
        self.wholesale_price_var = tk.StringVar()
        wholesale_entry = tk.Entry(grid_frame, 
                                 textvariable=self.wholesale_price_var,
                                 font=FONTS["regular"],
                                 width=42)
        wholesale_entry.grid(row=row, column=1, sticky="ew", pady=8)
        self.new_batch_fields.append(wholesale_entry)
        row += 1
        
        # Selling price
        selling_label = tk.Label(grid_frame, 
                               text="Selling Price:",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"],
                               anchor="w")
        selling_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        self.new_batch_fields.append(selling_label)
        
        self.selling_price_var = tk.StringVar()
        selling_entry = tk.Entry(grid_frame, 
                               textvariable=self.selling_price_var,
                               font=FONTS["regular"],
                               width=42)
        selling_entry.grid(row=row, column=1, sticky="ew", pady=8)
        self.new_batch_fields.append(selling_entry)
        row += 1
        
        # Quantity (always visible)
        tk.Label(grid_frame, 
                text="Quantity to Add:",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                anchor="w").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=12)
        
        self.quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(grid_frame, 
                                textvariable=self.quantity_var,
                                font=FONTS["regular"],
                                width=42)
        quantity_entry.grid(row=row, column=1, sticky="ew", pady=12)
        row += 1
        
        # Buttons frame
        button_frame = tk.Frame(form_labelframe, bg=COLORS["bg_primary"])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Right-aligned buttons
        button_container = tk.Frame(button_frame, bg=COLORS["bg_primary"])
        button_container.pack(side=tk.RIGHT)
        
        # Clear button
        clear_btn = tk.Button(button_container,
                            text="Clear Form",
                            font=FONTS["regular"],
                            bg=COLORS["secondary"],
                            fg=COLORS["text_white"],
                            padx=20,
                            pady=8,
                            cursor="hand2",
                            command=self.clear_stock_entry_form)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        save_btn = tk.Button(button_container,
                           text="Save Stock Entry",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=8,
                           cursor="hand2",
                           command=self.save_stock_entry)
        save_btn.pack(side=tk.LEFT)
        
        # Right side - Recent entries
        entries_container = tk.Frame(main_container, bg=COLORS["bg_primary"])
        entries_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Recent entries labeled frame
        entries_labelframe = tk.LabelFrame(entries_container, 
                                         text="Recent Stock Entries",
                                         font=FONTS["regular_bold"],
                                         bg=COLORS["bg_primary"],
                                         fg=COLORS["text_primary"],
                                         padx=10,
                                         pady=10)
        entries_labelframe.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview for recent entries
        tree_frame = tk.Frame(entries_labelframe, bg=COLORS["bg_primary"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview
        self.stock_entries_tree = ttk.Treeview(tree_frame, 
                                             columns=("Date", "Product", "Batch", "Qty", "MFG Date", "Expiry", "W.Price", "S.Price"),
                                             show="headings",
                                             yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.stock_entries_tree.yview)

        # Define columns
        self.stock_entries_tree.heading("Date", text="Entry Date")
        self.stock_entries_tree.heading("Product", text="Product Name")
        self.stock_entries_tree.heading("Batch", text="Batch Number")
        self.stock_entries_tree.heading("Qty", text="Quantity")
        self.stock_entries_tree.heading("MFG Date", text="MFG Date")
        self.stock_entries_tree.heading("Expiry", text="Expiry Date")
        self.stock_entries_tree.heading("W.Price", text="Wholesale Price")
        self.stock_entries_tree.heading("S.Price", text="Selling Price")

        # Set column widths
        self.stock_entries_tree.column("Date", width=100)
        self.stock_entries_tree.column("Product", width=150)
        self.stock_entries_tree.column("Batch", width=100)
        self.stock_entries_tree.column("Qty", width=60)
        self.stock_entries_tree.column("MFG Date", width=80)
        self.stock_entries_tree.column("Expiry", width=80)
        self.stock_entries_tree.column("W.Price", width=80)
        self.stock_entries_tree.column("S.Price", width=80)

        self.stock_entries_tree.pack(fill=tk.BOTH, expand=True)

        # Initialize variables
        self.stock_product_ids = {}
        self.existing_batches_data = {}
        
        # Load initial data
        self.load_products_for_stock_entry()
        self.load_stock_entries()
        
        # Set initial mode
        self.on_batch_mode_change()

    def load_products_for_stock_entry(self):
        """Load products into the stock entry dropdown - only product names"""
        try:
            # Get products from database using proper query
            query = """
                SELECT id, name, wholesale_price, selling_price
                FROM products 
                ORDER BY name
            """
            products = self.controller.db.fetchall(query)
            
            if not products:
                print("No products found in database")
                return
            
            # Format for display: Just product names
            product_names = [p[1] for p in products]
            self.stock_product_dropdown['values'] = product_names
            
            # Store product details for reference
            self.stock_product_ids = {
                p[1]: {
                    'id': p[0],
                    'name': p[1],
                    'wholesale_price': p[2],
                    'selling_price': p[3]
                } for p in products
            }
            
        except Exception as e:
            print(f"Error loading products: {str(e)}")

    def on_stock_product_select(self, event=None):
        """Handle product selection in stock entry form"""
        selected = self.stock_product_var.get()
        if not selected or selected not in self.stock_product_ids:
            return
            
        try:
            product_details = self.stock_product_ids[selected]
            product_id = product_details['id']
            
            # Load existing batches for this product
            self.load_existing_batches(product_id)
            
            # Set default prices for new batch
            self.wholesale_price_var.set(f"{product_details['wholesale_price']:.2f}")
            self.selling_price_var.set(f"{product_details['selling_price']:.2f}")
            
            # Generate a default batch number for new batch
            if not self.batch_number_var.get():
                date_str = datetime.datetime.now().strftime("%Y%m%d")
                random_suffix = random.randint(100, 999)
                # Use product name abbreviation for batch code
                name_abbrev = ''.join([c for c in selected.upper() if c.isalpha()])[:4]
                self.batch_number_var.set(f"{name_abbrev}-{date_str}-{random_suffix}")
            
        except Exception as e:
            print(f"Error handling product selection: {str(e)}")

    def load_existing_batches(self, product_id):
        """Load existing batches for the selected product"""
        try:
            # Clear previous batches display
            for widget in self.existing_batches_frame.winfo_children():
                widget.destroy()
            
            # Get existing batches with proper error handling for missing selling_price column
            try:
                query = """
                    SELECT id, batch_number, quantity, manufacturing_date, expiry_date, 
                           cost_price, COALESCE(selling_price, 0) as selling_price
                    FROM batches 
                    WHERE product_id = ? AND quantity > 0
                    ORDER BY expiry_date ASC, manufacturing_date ASC
                """
                batches = self.controller.db.fetchall(query, (product_id,))
            except Exception as db_error:
                # Fallback query without selling_price if column doesn't exist
                print(f"Database error: {db_error}")
                query = """
                    SELECT id, batch_number, quantity, manufacturing_date, expiry_date, 
                           cost_price, 0 as selling_price
                    FROM batches 
                    WHERE product_id = ? AND quantity > 0
                    ORDER BY expiry_date ASC, manufacturing_date ASC
                """
                batches = self.controller.db.fetchall(query, (product_id,))
            
            self.existing_batches_data = {}
            batch_options = []
            
            if batches:
                # Add header
                header_label = tk.Label(self.existing_batches_frame,
                                      text="Available Batches:",
                                      font=FONTS["small_bold"],
                                      bg=COLORS["bg_secondary"],
                                      fg=COLORS["text_primary"],
                                      anchor="w")
                header_label.pack(fill=tk.X, padx=5, pady=2)
                
                for batch in batches:
                    batch_id, batch_number, quantity, mfg_date, exp_date, cost_price, selling_price = batch
                    
                    # Handle missing selling_price by using cost_price
                    if selling_price == 0 or selling_price is None:
                        selling_price = cost_price
                    
                    # Format display string
                    exp_str = f" (Exp: {exp_date})" if exp_date else " (No Expiry)"
                    display_str = f"{batch_number}{exp_str} - Qty: {quantity} - ₹{selling_price:.2f}"
                    batch_options.append(display_str)
                    
                    # Store batch data
                    self.existing_batches_data[display_str] = {
                        'id': batch_id,
                        'batch_number': batch_number,
                        'quantity': quantity,
                        'manufacturing_date': mfg_date,
                        'expiry_date': exp_date,
                        'cost_price': cost_price,
                        'selling_price': selling_price
                    }
                    
                    # Add batch info label
                    batch_info = tk.Label(self.existing_batches_frame,
                                        text=f"• {display_str}",
                                        font=FONTS["small"],
                                        bg=COLORS["bg_secondary"],
                                        fg=COLORS["text_primary"],
                                        anchor="w")
                    batch_info.pack(fill=tk.X, padx=10, pady=1)
            else:
                no_batch_label = tk.Label(self.existing_batches_frame,
                                        text="No existing batches found",
                                        font=FONTS["small"],
                                        bg=COLORS["bg_secondary"],
                                        fg=COLORS["text_secondary"],
                                        anchor="w")
                no_batch_label.pack(fill=tk.X, padx=10, pady=5)
            
            # Update existing batch dropdown
            self.existing_batch_dropdown['values'] = batch_options
            if batch_options:
                self.existing_batch_var.set(batch_options[0])
                self.on_existing_batch_select()
            else:
                self.existing_batch_var.set("")
                
        except Exception as e:
            print(f"Error loading existing batches: {str(e)}")
            # Show error in the UI
            error_label = tk.Label(self.existing_batches_frame,
                                 text=f"Error loading batches: {str(e)}",
                                 font=FONTS["small"],
                                 bg=COLORS["bg_secondary"],
                                 fg=COLORS["danger"],
                                 anchor="w")
            error_label.pack(fill=tk.X, padx=10, pady=5)

    def on_existing_batch_select(self, event=None):
        """Handle selection of existing batch"""
        selected = self.existing_batch_var.get()
        if not selected or selected not in self.existing_batches_data:
            return
        
        # No additional action needed for existing batch selection
        # The data is already loaded and will be used when saving

    def on_batch_mode_change(self):
        """Handle batch mode change between existing and new"""
        mode = self.batch_mode_var.get()
        
        if mode == "existing":
            # Show existing batch selection, hide new batch fields
            self.existing_batch_label.grid()
            self.existing_batch_dropdown.grid()
            # Hide new batch fields
            for field in self.new_batch_fields:
                field.grid_remove()
        else:
            # Show new batch fields, hide existing batch selection
            self.existing_batch_label.grid_remove()
            self.existing_batch_dropdown.grid_remove()
            # Show new batch fields
            for field in self.new_batch_fields:
                field.grid()

    def check_batch_duplicate(self, product_id, batch_number, mfg_date, exp_date, cost_price):
        """Check if a batch with similar details already exists"""
        query = """
            SELECT id, batch_number, manufacturing_date, expiry_date, cost_price
            FROM batches 
            WHERE product_id = ? AND (
                (batch_number = ?) OR
                (manufacturing_date = ? AND expiry_date = ? AND ABS(cost_price - ?) < 0.01)
            )
        """
        existing = self.controller.db.fetchall(query, (product_id, batch_number, mfg_date, exp_date, cost_price))
        return existing

    def save_stock_entry(self):
        """Save a new stock entry with proper batch management"""
        try:
            # Validate required fields
            if not self.stock_product_var.get():
                messagebox.showerror("Error", "Please select a product")
                return
                
            if not self.quantity_var.get():
                messagebox.showerror("Error", "Please enter quantity")
                return
                
            # Get product details
            selected_product = self.stock_product_var.get()
            if selected_product not in self.stock_product_ids:
                messagebox.showerror("Error", "Invalid product selection")
                return
                
            product_id = self.stock_product_ids[selected_product]['id']
            
            # Parse and validate quantity
            try:
                quantity = int(self.quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {str(e)}")
                return
            
            batch_mode = self.batch_mode_var.get()
            
            # Begin transaction
            self.controller.db.begin()
            
            try:
                if batch_mode == "existing":
                    # Add to existing batch
                    selected_batch = self.existing_batch_var.get()
                    if not selected_batch or selected_batch not in self.existing_batches_data:
                        messagebox.showerror("Error", "Please select an existing batch")
                        return
                    
                    batch_data = self.existing_batches_data[selected_batch]
                    batch_id = batch_data['id']
                    
                    # Update existing batch quantity
                    new_quantity = batch_data['quantity'] + quantity
                    self.controller.db.execute(
                        "UPDATE batches SET quantity = ? WHERE id = ?",
                        (new_quantity, batch_id)
                    )
                    
                    # Log the transaction
                    log_data = {
                        "batch_id": batch_id,
                        "product_id": product_id,
                        "transaction_type": "STOCK_IN",
                        "quantity_change": quantity,
                        "quantity_before": batch_data['quantity'],
                        "quantity_after": new_quantity,
                        "reference_type": "MANUAL_ENTRY",
                        "notes": f"Added {quantity} units to existing batch {batch_data['batch_number']}"
                    }
                    self.controller.db.insert("stock_log", log_data)
                    
                else:
                    # Create new batch
                    if not self.batch_number_var.get():
                        messagebox.showerror("Error", "Please enter batch number for new batch")
                        return
                    
                    # Validate new batch fields
                    try:
                        mfg_date = self.mfg_date_var.get() if self.mfg_date_var.get() else None
                        if mfg_date:
                            datetime.datetime.strptime(mfg_date, "%Y-%m-%d").date()
                            
                        expiry_date = self.expiry_date_var.get() if self.expiry_date_var.get() else None
                        if expiry_date:
                            datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
                    except ValueError:
                        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                        return
                    
                    try:
                        wholesale_price = float(self.wholesale_price_var.get()) if self.wholesale_price_var.get() else 0.0
                        selling_price = float(self.selling_price_var.get()) if self.selling_price_var.get() else 0.0
                        if wholesale_price < 0 or selling_price < 0:
                            raise ValueError("Prices cannot be negative")
                    except ValueError as e:
                        messagebox.showerror("Error", f"Invalid price: {str(e)}")
                        return
                    
                    batch_number = self.batch_number_var.get()
                    
                    # Check for duplicate batches
                    duplicates = self.check_batch_duplicate(product_id, batch_number, mfg_date, expiry_date, wholesale_price)
                    if duplicates:
                        duplicate_info = "\n".join([f"• Batch {d[1]} (MFG: {d[2]}, EXP: {d[3]}, Cost: ₹{d[4]:.2f})" for d in duplicates])
                        if not messagebox.askyesno("Duplicate Batch Detected", 
                                                 f"Similar batch(es) already exist:\n\n{duplicate_info}\n\nDo you want to continue creating a new batch?"):
                            return
                    
                    # Create new batch
                    batch_data = {
                        "product_id": product_id,
                        "batch_number": batch_number,
                        "quantity": quantity,
                        "manufacturing_date": mfg_date,
                        "expiry_date": expiry_date,
                        "purchase_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "cost_price": wholesale_price,
                        "selling_price": selling_price
                    }
                    
                    batch_id = self.controller.db.insert("batches", batch_data)
                    
                    if not batch_id:
                        raise Exception("Failed to create new batch")
                    
                    # Log the transaction
                    log_data = {
                        "batch_id": batch_id,
                        "product_id": product_id,
                        "transaction_type": "STOCK_IN",
                        "quantity_change": quantity,
                        "quantity_before": 0,
                        "quantity_after": quantity,
                        "reference_type": "MANUAL_ENTRY",
                        "notes": f"Created new batch {batch_number} with {quantity} units"
                    }
                    self.controller.db.insert("stock_log", log_data)
                
                # Commit transaction
                self.controller.db.commit()
                
                # Refresh displays
                self.load_stock_entries()
                if hasattr(self, 'stock_product_var') and self.stock_product_var.get():
                    self.on_stock_product_select()  # Refresh existing batches display
                
                # Clear form
                self.clear_stock_entry_form()
                
                messagebox.showinfo("Success", "Stock entry saved successfully")
                
            except Exception as e:
                # Rollback on error
                self.controller.db.rollback()
                raise e
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save stock entry: {str(e)}")

    def clear_stock_entry_form(self):
        """Clear all fields in the stock entry form"""
        self.stock_product_var.set('')
        self.existing_batch_var.set('')
        self.batch_number_var.set('')
        self.quantity_var.set('')
        self.mfg_date_var.set(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.expiry_date_var.set('')
        self.wholesale_price_var.set('')
        self.selling_price_var.set('')
        self.batch_mode_var.set("existing")
        self.on_batch_mode_change()
        
        # Clear existing batches display
        for widget in self.existing_batches_frame.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget('text') != "Existing Batches for Selected Product:":
                widget.destroy()

    def load_stock_entries(self):
        """Load recent stock entries into the treeview"""
        try:
            # Clear existing items
            for item in self.stock_entries_tree.get_children():
                self.stock_entries_tree.delete(item)

            entries = self.controller.db.fetchall("""
                SELECT 
                    b.created_at,
                    p.name,
                    b.batch_number,
                    b.quantity,
                    b.manufacturing_date,
                    b.expiry_date,
                    b.cost_price,
                    COALESCE(b.selling_price, p.selling_price) as selling_price
                FROM batches b
                JOIN products p ON b.product_id = p.id
                ORDER BY b.created_at DESC
                LIMIT 100
            """)

            for entry in entries:
                # Format dates
                created_at = datetime.datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                mfg_date = datetime.datetime.strptime(entry[4], "%Y-%m-%d").strftime("%d/%m/%Y") if entry[4] else ""
                expiry_date = datetime.datetime.strptime(entry[5], "%Y-%m-%d").strftime("%d/%m/%Y") if entry[5] else ""

                # Format prices
                wholesale_price = f"₹{entry[6]:.2f}" if entry[6] else ""
                selling_price = f"₹{entry[7]:.2f}" if entry[7] else ""

                self.stock_entries_tree.insert("", "end", values=(
                    created_at,
                    entry[1],  # Product name
                    entry[2],  # Batch number
                    entry[3],  # Quantity
                    mfg_date,
                    expiry_date,
                    wholesale_price,
                    selling_price
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock entries: {str(e)}")

    def on_show(self):
        """Called when frame is shown"""
        # Load data for all tabs
        self.load_products()  # Load products first
        self.load_inventory()
        self.load_product_dropdown()  # Load products for batch filtering
        self.load_batches(show_all=True)
        self.load_alerts()
        self.load_categories()
        self.load_vendors()
        self.load_hsn_codes()
        self.load_stock_entries()  # Load stock entries
        self.load_products_for_stock_entry()  # Load products for stock entry

    # Category management functions
    def load_categories(self):
        """Load categories from database"""
        # Clear existing data
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)

        # Get categories from database
        categories = self.controller.db.fetchall("SELECT * FROM categories ORDER BY name")

        # Insert into treeview
        for category in categories:
            self.categories_tree.insert("", "end", values=(category[0], category[1], category[2]))

    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.categories_tree.selection()
        if not selection:
            return

        # Get category details
        category_id = self.categories_tree.item(selection[0])["values"][0]
        category = self.controller.db.fetchone(f"SELECT * FROM categories WHERE id = {category_id}")

        if category:
            # Fill form fields
            self.category_name_var.set(category[1])
            self.category_desc_var.set(category[2])

            # Set status
            self.category_id_var = category_id
            self.category_mode = "edit"
            self.category_save_btn.config(text="Update Category")

    def new_category(self):
        """Reset form for new category"""
        # Clear form fields
        self.category_name_var.set("")
        self.category_desc_var.set("")

        # Set status
        self.category_id_var = None
        self.category_mode = "add"
        self.category_save_btn.config(text="Save Category")

    def save_category(self):
        """Save or update category"""
        # Get form data
        name = self.category_name_var.get().strip()
        description = self.category_desc_var.get().strip()

        # Validate
        if not name:
            messagebox.showerror("Error", "Category name is required.")
            return

        try:
            if self.category_mode == "add":
                # Check if category already exists
                existing = self.controller.db.fetchone(f"SELECT id FROM categories WHERE name = ?", (name,))
                if existing:
                    messagebox.showerror("Error", f"Category '{name}' already exists.")
                    return

                # Insert new category
                data = {
                    "name": name,
                    "description": description
                }

                inserted = self.controller.db.insert("categories", data)
                if inserted:
                    messagebox.showinfo("Success", "Category added successfully!")
                    self.load_categories()
                    self.new_category()
                else:
                    messagebox.showerror("Error", "Failed to add category.")
            else:
                # Update existing category
                data = {
                    "name": name,
                    "description": description
                }

                updated = self.controller.db.update("categories", data, f"id = {self.category_id_var}")
                if updated:
                    messagebox.showinfo("Success", "Category updated successfully!")
                    self.load_categories()
                    self.new_category()
                else:
                    messagebox.showerror("Error", "Failed to update category.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_category(self):
        """Delete selected category"""
        if not self.category_id_var:
            messagebox.showinfo("Info", "Please select a category to delete.")
            return

        # Check if category is used in products
        products = self.controller.db.fetchall(f"SELECT id FROM products WHERE category = ?", 
                                             (self.category_name_var.get(),))

        if products:
            messagebox.showerror("Error", "Cannot delete category as it is used by products.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete category '{self.category_name_var.get()}'?"):
            return

        # Delete from database
        deleted = self.controller.db.delete("categories", f"id = {self.category_id_var}")

        if deleted:
            messagebox.showinfo("Success", "Category deleted successfully!")
            self.load_categories()
            self.new_category()
        else:
            messagebox.showerror("Error", "Failed to delete category.")

    # Vendor management functions
    def load_vendors(self):
        """Load vendors from database"""
        # Clear existing data
        for item in self.vendors_tree.get_children():
            self.vendors_tree.delete(item)

        # Get vendors from database
        vendors = self.controller.db.fetchall("SELECT * FROM vendors ORDER BY name")

        # Insert into treeview
        for vendor in vendors:
            self.vendors_tree.insert("", "end", values=(vendor[0], vendor[1], vendor[2], vendor[3], vendor[6]))

    def on_vendor_select(self, event):
        """Handle vendor selection"""
        selection = self.vendors_tree.selection()
        if not selection:
            return

        # Get vendor details
        vendor_id = self.vendors_tree.item(selection[0])["values"][0]
        vendor = self.controller.db.fetchone(f"SELECT * FROM vendors WHERE id = {vendor_id}")

        if vendor:
            # Fill form fields
            self.vendor_name_var.set(vendor[1])
            self.vendor_contact_var.set(vendor[2] or "")
            self.vendor_phone_var.set(vendor[3] or "")
            self.vendor_email_var.set(vendor[4] or "")
            self.vendor_address_var.set(vendor[5] or "")
            self.vendor_gstin_var.set(vendor[6] or "")

            # Set status
            self.vendor_id_var = vendor_id
            self.vendor_mode = "edit"
            self.vendor_save_btn.config(text="Update Vendor")

    def new_vendor(self):
        """Reset form for new vendor"""
        # Clear form fields
        self.vendor_name_var.set("")
        self.vendor_contact_var.set("")
        self.vendor_phone_var.set("")
        self.vendor_email_var.set("")
        self.vendor_address_var.set("")
        self.vendor_gstin_var.set("")

        # Set status
        self.vendor_id_var = None
        self.vendor_mode = "add"
        self.vendor_save_btn.config(text="Save Vendor")

    def save_vendor(self):
        """Save or update vendor"""
        # Get form data
        name = self.vendor_name_var.get().strip()
        contact = self.vendor_contact_var.get().strip()
        phone = self.vendor_phone_var.get().strip()
        email = self.vendor_email_var.get().strip()
        address = self.vendor_address_var.get().strip()
        gstin = self.vendor_gstin_var.get().strip()

        # Validate
        if not name:
            messagebox.showerror("Error", "Vendor name is required.")
            return

        try:
            if self.vendor_mode == "add":
                # Check if vendor already exists
                existing = self.controller.db.fetchone(f"SELECT id FROM vendors WHERE name = ?", (name,))
                if existing:
                    messagebox.showerror("Error", f"Vendor '{name}' already exists.")
                    return

                # Insert new vendor
                data = {
                    "name": name,
                    "contact_person": contact,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "gstin": gstin
                }

                inserted = self.controller.db.insert("vendors", data)
                if inserted:
                    messagebox.showinfo("Success", "Vendor added successfully!")
                    self.load_vendors()
                    self.new_vendor()
                else:
                    messagebox.showerror("Error", "Failed to add vendor.")
            else:
                # Update existing vendor
                data = {
                    "name": name,
                    "contact_person": contact,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "gstin": gstin
                }

                updated = self.controller.db.update("vendors", data, f"id = {self.vendor_id_var}")
                if updated:
                    messagebox.showinfo("Success", "Vendor updated successfully!")
                    self.load_vendors()
                    self.new_vendor()
                else:
                    messagebox.showerror("Error", "Failed to update vendor.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_vendor(self):
        """Delete selected vendor"""
        if not self.vendor_id_var:
            messagebox.showinfo("Info", "Please select a vendor to delete.")
            return

        # Check if vendor is used in products
        products = self.controller.db.fetchall(f"SELECT id FROM products WHERE vendor = ?", 
                                             (self.vendor_name_var.get(),))

        if products:
            messagebox.showerror("Error", "Cannot delete vendor as it is used by products.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete vendor '{self.vendor_name_var.get()}'?"):
            return

        # Delete from database
        deleted = self.controller.db.delete("vendors", f"id = {self.vendor_id_var}")

        if deleted:
            messagebox.showinfo("Success", "Vendor deleted successfully!")
            self.load_vendors()
            self.new_vendor()
        else:
            messagebox.showerror("Error", "Failed to delete vendor.")

    # HSN code management functions
    def load_hsn_codes(self):
        """Load HSN codes from database"""
        # Clear existing data
        for item in self.hsn_tree.get_children():
            self.hsn_tree.delete(item)

        # Get HSN codes from database
        hsn_codes = self.controller.db.fetchall("SELECT * FROM hsn_codes ORDER BY code")

        # Insert into treeview
        for hsn in hsn_codes:
            self.hsn_tree.insert("", "end", values=(hsn[0], hsn[1], hsn[2], hsn[3]))

    def search_hsn(self):
        """Search HSN codes"""
        search_term = self.hsn_search_var.get().strip()

        # Clear treeview
        for item in self.hsn_tree.get_children():
            self.hsn_tree.delete(item)

        if not search_term:
            self.load_hsn_codes()
            return

        # Search in database
        hsn_codes = self.controller.db.fetchall(
            "SELECT * FROM hsn_codes WHERE code LIKE ? OR description LIKE ? ORDER BY code",
            (f"%{search_term}%", f"%{search_term}%")
        )

        # Insert into treeview
        for hsn in hsn_codes:
            self.hsn_tree.insert("", "end", values=(hsn[0], hsn[1], hsn[2], hsn[3]))

    def on_hsn_select(self, event):
        """Handle HSN code selection"""
        selection = self.hsn_tree.selection()
        if not selection:
            return

        # Get HSN code details
        hsn_id = self.hsn_tree.item(selection[0])["values"][0]
        hsn = self.controller.db.fetchone(f"SELECT * FROM hsn_codes WHERE id = {hsn_id}")

        if hsn:
            # Fill form fields
            self.hsn_code_var.set(hsn[1])
            self.hsn_desc_var.set(hsn[2])
            self.hsn_tax_var.set(hsn[3])

            # Set status
            self.hsn_id_var = hsn_id
            self.hsn_mode = "edit"
            self.hsn_save_btn.config(text="Update HSN Code")

    def new_hsn(self):
        """Reset form for new HSN code"""
        # Clear form fields
        self.hsn_code_var.set("")
        self.hsn_desc_var.set("")
        self.hsn_tax_var.set("")

        # Set status
        self.hsn_id_var = None
        self.hsn_mode = "add"
        self.hsn_save_btn.config(text="Save HSN Code")

    def save_hsn(self):
        """Save or update HSN code"""
        # Get form data
        code = self.hsn_code_var.get().strip()
        description = self.hsn_desc_var.get().strip()
        tax_rate = self.hsn_tax_var.get().strip()

        # Validate
        if not code:
            messagebox.showerror("Error", "HSN code is required.")
            return

        try:
            # Validate tax rate
            if tax_rate:
                tax_rate = float(tax_rate)
            else:
                tax_rate = 0.0

            if self.hsn_mode == "add":
                # Check if HSN code already exists
                existing = self.controller.db.fetchone(f"SELECT id FROM hsn_codes WHERE code = ?", (code,))
                if existing:
                    messagebox.showerror("Error", f"HSN code '{code}' already exists.")
                    return

                # Insert new HSN code
                data = {
                    "code": code,
                    "description": description,
                    "tax_rate": tax_rate
                }

                inserted = self.controller.db.insert("hsn_codes", data)
                if inserted:
                    messagebox.showinfo("Success", "HSN code added successfully!")
                    self.load_hsn_codes()
                    self.new_hsn()
                else:
                    messagebox.showerror("Error", "Failed to add HSN code.")
            else:
                # Update existing HSN code
                data = {
                    "code": code,
                    "description": description,
                    "tax_rate": tax_rate
                }

                updated = self.controller.db.update("hsn_codes", data, f"id = {self.hsn_id_var}")
                if updated:
                    messagebox.showinfo("Success", "HSN code updated successfully!")
                    self.load_hsn_codes()
                    self.new_hsn()
                else:
                    messagebox.showerror("Error", "Failed to update HSN code.")
        except ValueError:
            messagebox.showerror("Error", "Tax rate must be a number.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_hsn(self):
        """Delete selected HSN code"""
        if not self.hsn_id_var:
            messagebox.showinfo("Info", "Please select an HSN code to delete.")
            return

        # Check if HSN code is used in products
        products = self.controller.db.fetchall(f"SELECT id FROM products WHERE hsn_code = ?", 
                                             (self.hsn_code_var.get(),))

        if products:
            messagebox.showerror("Error", "Cannot delete HSN code as it is used by products.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete HSN code '{self.hsn_code_var.get()}'?"):
            return

        # Delete from database
        deleted = self.controller.db.delete("hsn_codes", f"id = {self.hsn_id_var}")

        if deleted:
            messagebox.showinfo("Success", "HSN code deleted successfully!")
            self.load_hsn_codes()
            self.new_hsn()
        else:
            messagebox.showerror("Error", "Failed to delete HSN code.")

    # Product Management Methods
    def load_products(self):
        """Load products from database into treeview"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get all products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category,
                   manufacturer, unit
            FROM products
            ORDER BY name
        """
        products = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for product in products:
            self.product_tree.insert("", "end", values=product)
    
    def search_products(self):
        """Search products based on search term"""
        search_term = self.product_search_var.get().lower()
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        if not search_term:
            # If search is empty, load all products
            self.load_products()
            return
        
        # Get filtered products
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category,
                   manufacturer, unit
            FROM products
            WHERE LOWER(name) LIKE ? OR 
                  LOWER(product_code) LIKE ? OR
                  LOWER(vendor) LIKE ? OR
                  LOWER(manufacturer) LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        products = self.controller.db.fetchall(query, (search_pattern, search_pattern, search_pattern))
        
        # Insert into treeview
        for product in products:
            self.product_tree.insert("", "end", values=product)
    
    def show_context_menu(self, event):
        """Show context menu for product treeview"""
        # Select row under mouse
        item = self.product_tree.identify_row(event.y)
        if item:
            self.product_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def add_product(self):
        """Add a new product"""
        product_dialog = tk.Toplevel(self)
        product_dialog.title("Add New Product")
        product_dialog.geometry("600x650")  # Larger size to fit all fields
        product_dialog.resizable(True, True)  # Allow resizing
        product_dialog.configure(bg=COLORS["bg_primary"])
        product_dialog.transient(self)  # Set to be on top of the parent window
        product_dialog.grab_set()  # Modal
        
        # Make dialog appear centered
        self._set_dialog_transient(product_dialog)
        
        # Create a scrollable frame to hold all fields
        main_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add a canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get categories, vendors and HSN codes
        categories = self.get_categories()
        vendors = self.get_vendors()
        hsn_codes = self.get_hsn_codes()
        
        # Title for first section
        section1_title = tk.Label(scrollable_frame, 
                                text="Product Details",
                                font=FONTS["subheading"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"],
                                padx=10,
                                pady=5,
                                width=50)
        section1_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Create unit options list
        unit_options = ["Kilogram (kg)", "Gram (g)", "Quintal (100 kg)", "Metric Tonne (MT)", 
                        "Litre (L)", "Millilitre (ml)", "Piece (pc)", "Packet", "Bag", 
                        "Box", "Bottle", "Sachet", "Dozen"]
        
        # Create form fields
        fields = [
            {"name": "product_code", "label": "Product Code:", "required": False, "type": "entry", "readonly": False},
            {"name": "name", "label": "Product Name:", "required": True, "type": "entry"},
            {"name": "manufacturer", "label": "Manufacturer Name:", "required": False, "type": "entry"},
            {"name": "vendor", "label": "Vendor:", "required": False, "type": "combobox", "values": vendors},
            {"name": "hsn_code", "label": "HSN Code:", "required": False, "type": "combobox", "values": hsn_codes},
            {"name": "category", "label": "Category:", "required": False, "type": "combobox", "values": categories},
            {"name": "unit", "label": "Unit:", "required": False, "type": "combobox", "values": unit_options},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True, "type": "entry"},
            {"name": "selling_price", "label": "Selling Price:", "required": True, "type": "entry"},
            {"name": "tax_percentage", "label": "Tax Percentage:", "required": False, "type": "entry"}
        ]
        
        # Inventory fields (now in the same form)
        # Title for second section
        section2_title = tk.Label(scrollable_frame, 
                                text="Initial Stock Information",
                                font=FONTS["subheading"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"],
                                padx=10,
                                pady=5)
        section2_title.grid(row=len(fields)+1, column=0, columnspan=2, sticky="ew", pady=(20, 10))
        
        inventory_fields = [
            {"name": "initial_stock", "label": "Initial Stock Quantity:", "required": False, "type": "entry"},
            {"name": "batch_number", "label": "Batch Number:", "required": False, "type": "entry"},
            {"name": "manufacturing_date", "label": "Manufacturing Date (YYYY-MM-DD):", "required": False, "type": "entry"},
            {"name": "expiry_date", "label": "Expiry Date (YYYY-MM-DD):", "required": False, "type": "entry"}
        ]
        
        # Variables to store entry values
        entry_vars = {}
        entries = {}
        
        # Create labels and entries for product details
        row_index = 1  # Start after section title
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(scrollable_frame, 
                          text=field["label"],
                          font=FONTS["regular"],
                          bg=COLORS["bg_primary"],
                          fg=COLORS["text_primary"])
            label.grid(row=row_index, column=0, sticky="w", pady=8, padx=10)
            
            # Entry or combobox
            if field["type"] == "entry":
                entry_vars[field["name"]] = tk.StringVar()
                entry = tk.Entry(scrollable_frame, 
                               textvariable=entry_vars[field["name"]],
                               font=FONTS["regular"],
                               width=30)
                
                # Set readonly if specified
                if field.get("readonly", False):
                    entry.config(state="readonly")
                    
                entry.grid(row=row_index, column=1, pady=8, padx=10, sticky="w")
                entries[field["name"]] = entry
                
            elif field["type"] == "combobox":
                entry_vars[field["name"]] = tk.StringVar()
                combobox = ttk.Combobox(scrollable_frame,
                                       textvariable=entry_vars[field["name"]],
                                       values=field["values"],
                                       font=FONTS["regular"],
                                       width=28)
                combobox.grid(row=row_index, column=1, pady=8, padx=10, sticky="w")
                entries[field["name"]] = combobox
                
                # Bind selection events for special handling in certain comboboxes
                if field["name"] in ["category", "vendor", "hsn_code"]:
                    combobox.bind("<<ComboboxSelected>>", 
                                 lambda e, name=field["name"]: self.handle_combobox_selection(e, name, entry_vars, entries))
            
            row_index += 1
        
        # Create labels and entries for inventory fields
        row_index = len(fields) + 2  # Continue after section title
        for i, field in enumerate(inventory_fields):
            # Label
            label = tk.Label(scrollable_frame, 
                          text=field["label"],
                          font=FONTS["regular"],
                          bg=COLORS["bg_primary"],
                          fg=COLORS["text_primary"])
            label.grid(row=row_index, column=0, sticky="w", pady=8, padx=10)
            
            # Entry
            entry_vars[field["name"]] = tk.StringVar()
            entry = tk.Entry(scrollable_frame, 
                           textvariable=entry_vars[field["name"]],
                           font=FONTS["regular"],
                           width=30)
            
            # Set default value for initial_stock
            if field["name"] == "initial_stock":
                entry_vars[field["name"]].set("0")  # Default to 0
                
            entry.grid(row=row_index, column=1, pady=8, padx=10, sticky="w")
            entries[field["name"]] = entry
            
            row_index += 1
        
        # Buttons frame
        button_frame = tk.Frame(scrollable_frame, bg=COLORS["bg_primary"], pady=20)
        button_frame.grid(row=row_index, column=0, columnspan=2, sticky="ew")
        
        # Add hint text about product code field
        product_code_hint = "Leave blank to auto-generate from category, or enter custom code"
        entries["product_code"].insert(0, product_code_hint)
        entries["product_code"].config(fg="gray")
        
        def on_product_code_focus_in(event):
            if entries["product_code"].get() == product_code_hint:
                entries["product_code"].delete(0, tk.END)
                entries["product_code"].config(fg=COLORS["text_primary"])
                
        def on_product_code_focus_out(event):
            if not entries["product_code"].get():
                entries["product_code"].insert(0, product_code_hint)
                entries["product_code"].config(fg="gray")
                
        # Bind focus events to handle hint text
        entries["product_code"].bind("<FocusIn>", on_product_code_focus_in)
        entries["product_code"].bind("<FocusOut>", on_product_code_focus_out)
        
        # Default tax percentage to 5%
        entry_vars["tax_percentage"].set("5.0")
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             highlightthickness=3,  # Added for focus visibility
                             highlightcolor=COLORS["primary"],  # Set focus color
                             highlightbackground=COLORS["bg_secondary"],  # Set inactive color
                             command=lambda: product_dialog.destroy())
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Make button keyboard-navigable
        make_button_keyboard_navigable(cancel_btn)
        
        # Function to save product
        def save_product():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Validation Error", f"{field['label']} is required.")
                    return
                
            # Validate numeric fields
            try:
                if entry_vars["wholesale_price"].get():
                    wholesale_price = Decimal(entry_vars["wholesale_price"].get())
                else:
                    wholesale_price = Decimal('0.00')
                    
                if entry_vars["selling_price"].get():
                    selling_price = Decimal(entry_vars["selling_price"].get())
                else:
                    selling_price = Decimal('0.00')
                    
                if entry_vars["tax_percentage"].get():
                    tax_percentage = Decimal(entry_vars["tax_percentage"].get())
                else:
                    tax_percentage = Decimal('0.00')
                    
                # Get value from initial_stock field, ensuring white space and hint text are handled
                initial_stock_value = entry_vars["initial_stock"].get().strip()
                print(f"Initial stock value from entry: '{initial_stock_value}'")
                
                # Check if the value is not empty
                if initial_stock_value:
                    try:
                        initial_stock = int(initial_stock_value)
                        print(f"Successfully converted initial_stock to int: {initial_stock}")
                    except ValueError:
                        messagebox.showerror("Validation Error", "Initial Stock must be a whole number.")
                        return
                else:
                    initial_stock = 0
                    print("No initial stock value, defaulting to 0")
                    
            except (ValueError, InvalidOperation):
                messagebox.showerror("Validation Error", "Price and tax fields must be valid numbers.")
                return
                
            # Construct product data
            product_data = {
                "name": entry_vars["name"].get(),
                "manufacturer": entry_vars["manufacturer"].get(),
                "vendor": entry_vars["vendor"].get(),
                "hsn_code": entry_vars["hsn_code"].get(),
                "category": entry_vars["category"].get(),
                "unit": entry_vars["unit"].get(),
                "wholesale_price": float(wholesale_price),  # Convert to float for database
                "selling_price": float(selling_price),
                "tax_percentage": float(tax_percentage)
            }
            
            # Handle product code - check if it's not the hint text
            product_code_hint = "Leave blank to auto-generate from category, or enter custom code"
            custom_code = entry_vars["product_code"].get()
            if custom_code and custom_code != product_code_hint:
                # Use the custom code provided by user
                product_data["product_code"] = custom_code
                print(f"Using user-provided product code: {custom_code}")
            else:
                # Auto-generate product code based on category (first 4 letters)
                category = product_data.get("category", "")
                prefix = ""
                if category:
                    # Extract alphabetic characters only for clean prefix
                    alpha_only = ''.join(c for c in category if c.isalpha()).upper()
                    
                    # Take exactly the first 4 letters
                    if len(alpha_only) >= 4:
                        prefix = alpha_only[:4]
                    else:
                        # If category has less than 4 letters, pad with 'X'
                        prefix = alpha_only.ljust(4, 'X')
                    
                    # Debug output
                    print(f"Using category '{category}' to generate prefix '{prefix}'")
                else:
                    # Default prefix if no category
                    prefix = "PROD"
                
                # Get the highest product number for this category
                query = """
                    SELECT product_code 
                    FROM products 
                    WHERE product_code LIKE ? 
                    ORDER BY LENGTH(product_code) DESC, product_code DESC 
                    LIMIT 1
                """
                result = self.controller.db.fetchone(query, (f"{prefix}%",))
                
                if result and result[0]:
                    # Extract the numeric part from the last code
                    try:
                        # Find all digits at the end of the string
                        import re
                        numeric_part = re.search(r'\d+$', result[0])
                        if numeric_part:
                            last_num = int(numeric_part.group())
                            next_num = last_num + 1
                        else:
                            next_num = 1
                    except (ValueError, IndexError):
                        next_num = 1
                else:
                    next_num = 1
                    
                # Generate code in format: SEED001, PESTI001, etc.
                product_data["product_code"] = f"{prefix}{str(next_num).zfill(3)}"
                
                # Log the generated code for debugging
                print(f"Auto-generated product code: {product_data['product_code']}")
            
            # Inventory data
            batch_number = entry_vars["batch_number"].get()
            manufacturing_date = entry_vars["manufacturing_date"].get() or None
            expiry_date = entry_vars["expiry_date"].get() or None
            
            try:
                # Begin transaction
                self.controller.db.begin()
                
                # Insert product
                print(f"Inserting product data: {product_data}")
                product_id = self.controller.db.insert("products", product_data)
                
                # Add initial stock if specified
                print(f"Checking initial stock: {initial_stock}")
                if initial_stock > 0:
                    # Use batches table instead of inventory for consistent display in UI
                    batch_data = {
                        "product_id": product_id,
                        "quantity": initial_stock,
                        "batch_number": batch_number,
                        "manufacturing_date": manufacturing_date,
                        "expiry_date": expiry_date,
                        "purchase_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "cost_price": float(wholesale_price) if wholesale_price else 0.0  # Use wholesale price as cost price
                    }
                    print(f"Adding batch data: {batch_data}")
                    try:
                        batch_id = self.controller.db.insert("batches", batch_data)
                        print(f"Successfully added batch with ID: {batch_id}")
                        
                        # Also add to inventory table for backward compatibility
                        inventory_data = {
                            "product_id": product_id,
                            "quantity": initial_stock,
                            "batch_number": batch_number,
                            "manufacturing_date": manufacturing_date,
                            "expiry_date": expiry_date,
                            "purchase_date": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                        inventory_id = self.controller.db.insert("inventory", inventory_data)
                        print(f"Also added to inventory table with ID: {inventory_id}")
                    except Exception as e:
                        print(f"Error adding stock: {e}")
                        raise e
                else:
                    print("No initial stock to add")
                
                # Commit transaction
                self.controller.db.commit()
                
                # Close dialog
                product_dialog.destroy()
                messagebox.showinfo("Success", "Product added successfully.")
                
                # Refresh product list
                self.load_products()  # Refresh product list
                
            except Exception as e:
                # Roll back in case of errors
                self.controller.db.rollback()
                error_details = str(e)
                print(f"Error adding product: {error_details}")
                messagebox.showerror("Error", f"Failed to add product: {error_details}")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Save Product",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           highlightthickness=3,  # Added for focus visibility
                           highlightcolor=COLORS["primary"],  # Set focus color
                           highlightbackground=COLORS["bg_secondary"],  # Set inactive color
                           command=lambda: save_product())
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Make button keyboard-navigable
        make_button_keyboard_navigable(save_btn)
        
        # Bind Enter key to save product
        def on_enter_key(event):
            save_product()
        
        product_dialog.bind('<Return>', on_enter_key)
    
    def edit_product(self, event=None):
        """Edit selected product"""
        # Get selected item
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return
            
        # Get product data
        product_id = self.product_tree.item(selected_item[0], "values")[0]
        
        # Get complete product data
        query = """
            SELECT id, product_code, name, vendor, hsn_code, 
                   wholesale_price, selling_price, tax_percentage, category,
                   manufacturer, unit
            FROM products
            WHERE id = ?
        """
        product = self.controller.db.fetchone(query, (product_id,))
        
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
            
        # Create edit dialog similar to add_product
        product_dialog = tk.Toplevel(self)
        product_dialog.title("Edit Product")
        product_dialog.geometry("600x550")
        product_dialog.resizable(True, True)
        product_dialog.configure(bg=COLORS["bg_primary"])
        product_dialog.transient(self)
        product_dialog.grab_set()
        
        # Make dialog appear centered
        self._set_dialog_transient(product_dialog)
        
        # Create a frame to hold all fields
        main_frame = tk.Frame(product_dialog, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Get categories, vendors and HSN codes
        categories = self.get_categories()
        vendors = self.get_vendors()
        hsn_codes = self.get_hsn_codes()
        
        # Title
        title = tk.Label(main_frame, 
                        text="Edit Product Details",
                        font=FONTS["subheading"],
                        bg=COLORS["bg_secondary"],
                        fg=COLORS["text_primary"],
                        padx=10,
                        pady=5,
                        width=50)
        title.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        
        # Create a frame for the form fields
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create unit options list
        unit_options = ["Kilogram (kg)", "Gram (g)", "Quintal (100 kg)", "Metric Tonne (MT)", 
                        "Litre (L)", "Millilitre (ml)", "Piece (pc)", "Packet", "Bag", 
                        "Box", "Bottle", "Sachet", "Dozen"]
                        
        # Create form fields
        fields = [
            {"name": "id", "label": "Product ID:", "required": False, "type": "entry", "readonly": True},
            {"name": "product_code", "label": "Product Code:", "required": False, "type": "entry", "readonly": False},
            {"name": "name", "label": "Product Name:", "required": True, "type": "entry"},
            {"name": "manufacturer", "label": "Manufacturer Name:", "required": False, "type": "entry"},
            {"name": "vendor", "label": "Vendor:", "required": False, "type": "combobox", "values": vendors},
            {"name": "hsn_code", "label": "HSN Code:", "required": False, "type": "combobox", "values": hsn_codes},
            {"name": "category", "label": "Category:", "required": False, "type": "combobox", "values": categories},
            {"name": "unit", "label": "Unit:", "required": False, "type": "combobox", "values": unit_options},
            {"name": "wholesale_price", "label": "Wholesale Price:", "required": True, "type": "entry"},
            {"name": "selling_price", "label": "Selling Price:", "required": True, "type": "entry"},
            {"name": "tax_percentage", "label": "Tax Percentage:", "required": False, "type": "entry"}
        ]
        
        # Variables to store entry values
        entry_vars = {}
        entries = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                          text=field["label"],
                          font=FONTS["regular"],
                          bg=COLORS["bg_primary"],
                          fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=8, padx=10)
            
            # Entry or combobox
            if field["type"] == "entry":
                entry_vars[field["name"]] = tk.StringVar()
                entry = tk.Entry(form_frame, 
                               textvariable=entry_vars[field["name"]],
                               font=FONTS["regular"],
                               width=30)
                
                # Set readonly if specified
                if field.get("readonly", False):
                    entry.config(state="readonly")
                    
                entry.grid(row=i, column=1, pady=8, padx=10, sticky="w")
                entries[field["name"]] = entry
                
                # Set initial value from product data
                if field["name"] == "id":
                    entry_vars[field["name"]].set(product[0])  # ID
                elif field["name"] == "product_code":
                    entry_vars[field["name"]].set(product[1])  # Product Code
                elif field["name"] == "name":
                    entry_vars[field["name"]].set(product[2])  # Name
                elif field["name"] == "wholesale_price":
                    entry_vars[field["name"]].set(product[5])  # Wholesale Price
                elif field["name"] == "selling_price":
                    entry_vars[field["name"]].set(product[6])  # Selling Price
                elif field["name"] == "tax_percentage":
                    entry_vars[field["name"]].set(product[7])  # Tax Percentage
                elif field["name"] == "manufacturer":
                    entry_vars[field["name"]].set(product[9] or "")  # Manufacturer
                elif field["name"] == "unit":
                    entry_vars[field["name"]].set(product[10] or "")  # Unit
                
            elif field["type"] == "combobox":
                entry_vars[field["name"]] = tk.StringVar()
                combobox = ttk.Combobox(form_frame,
                                       textvariable=entry_vars[field["name"]],
                                       values=field["values"],
                                       font=FONTS["regular"],
                                       width=28)
                combobox.grid(row=i, column=1, pady=8, padx=10, sticky="w")
                entries[field["name"]] = combobox
                
                # Set initial value from product data
                if field["name"] == "vendor":
                    entry_vars[field["name"]].set(product[3] or "")  # Vendor
                elif field["name"] == "hsn_code":
                    entry_vars[field["name"]].set(product[4] or "")  # HSN Code
                elif field["name"] == "category":
                    entry_vars[field["name"]].set(product[8] or "")  # Category
                elif field["name"] == "unit":
                    entry_vars[field["name"]].set(product[10] or "")  # Unit
                
                # Bind selection events for special handling in certain comboboxes
                if field["name"] in ["category", "vendor", "hsn_code"]:
                    combobox.bind("<<ComboboxSelected>>", 
                                 lambda e, name=field["name"]: self.handle_combobox_selection(e, name, entry_vars, entries))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], pady=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=lambda: product_dialog.destroy())
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Make button keyboard-navigable
        make_button_keyboard_navigable(cancel_btn)
        
        # Function to save product
        def save_product():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Validation Error", f"{field['label']} is required.")
                    return
                
            # Validate numeric fields
            try:
                wholesale_price = Decimal(entry_vars["wholesale_price"].get())
                selling_price = Decimal(entry_vars["selling_price"].get())
                
                if entry_vars["tax_percentage"].get():
                    tax_percentage = Decimal(entry_vars["tax_percentage"].get())
                else:
                    tax_percentage = Decimal('0.00')
                    
            except (ValueError, InvalidOperation):
                messagebox.showerror("Validation Error", "Price and tax fields must be valid numbers.")
                return
                
            # Construct product data
            product_data = {
                "name": entry_vars["name"].get(),
                "manufacturer": entry_vars["manufacturer"].get(),
                "vendor": entry_vars["vendor"].get(),
                "hsn_code": entry_vars["hsn_code"].get(),
                "category": entry_vars["category"].get(),
                "unit": entry_vars["unit"].get(),
                "wholesale_price": float(wholesale_price),  # Convert to float for database
                "selling_price": float(selling_price),
                "tax_percentage": float(tax_percentage)
            }
            
            # Handle product code
            custom_code = entry_vars["product_code"].get().strip()
            if custom_code:
                product_data["product_code"] = custom_code
                # Debug output
                print(f"Updating product with user-provided code: {custom_code}")
            else:
                # Keep existing code if nothing provided
                query = """SELECT product_code FROM products WHERE id = ?"""
                existing_code = self.controller.db.fetchone(query, (product_id,))[0]
                product_data["product_code"] = existing_code
                print(f"Keeping existing product code: {existing_code}")
            
            try:
                # Update product
                product_id = entry_vars["id"].get()
                self.controller.db.update("products", product_data, f"id = {product_id}")
                
                # Close dialog
                product_dialog.destroy()
                messagebox.showinfo("Success", "Product updated successfully.")
                
                # Refresh product list
                self.load_products()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Save Changes",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=lambda: save_product())
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Make button keyboard-navigable
        make_button_keyboard_navigable(save_btn)
        
        # Bind Enter key to save product
        def on_enter_key(event):
            save_product()
        
        product_dialog.bind('<Return>', on_enter_key)
    
    def handle_combobox_selection(self, event, field_name, entry_vars, entries):
        """Handle selection in category or vendor combobox"""
        combobox = event.widget
        selected_value = combobox.get()
        
        # Additional logic can be added here in the future if needed
        
    def delete_product(self):
        """Delete selected product"""
        # Get selected item
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
            
        # Get product data
        product_id = self.product_tree.item(selected_item[0], "values")[0]
        product_name = self.product_tree.item(selected_item[0], "values")[2]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                     f"Are you sure you want to delete {product_name}?\n\n"
                                     f"This will also remove all inventory items for this product.")
        if not confirm:
            return
            
        try:
            # Begin transaction
            self.controller.db.begin()
            
            # Delete inventory items for this product
            self.controller.db.delete("inventory", f"product_id = {product_id}")
            
            # Delete product
            self.controller.db.delete("products", f"id = {product_id}")
            
            # Commit transaction
            self.controller.db.commit()
            
            messagebox.showinfo("Success", f"{product_name} has been deleted.")
            
            # Refresh product list
            self.load_products()
            
        except Exception as e:
            # Roll back in case of errors
            self.controller.db.rollback()
            messagebox.showerror("Error", f"Failed to delete product: {e}")
    
    def add_stock(self):
        """Add stock to selected product"""
        # Get selected item
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a product to add stock.")
            return
            
        # Get product data
        product_id = self.product_tree.item(selected_item[0], "values")[0]
        product_name = self.product_tree.item(selected_item[0], "values")[2]
        
        # Create dialog
        stock_dialog = tk.Toplevel(self)
        stock_dialog.title("Add Stock")
        stock_dialog.geometry("500x350")
        stock_dialog.resizable(False, False)
        stock_dialog.configure(bg=COLORS["bg_primary"])
        stock_dialog.transient(self)
        stock_dialog.grab_set()
        
        # Make dialog appear centered
        self._set_dialog_transient(stock_dialog)
        
        # Create a frame for the form
        main_frame = tk.Frame(stock_dialog, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, 
                        text=f"Add Stock for {product_name}",
                        font=FONTS["subheading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        fields = [
            {"name": "quantity", "label": "Quantity:", "required": True},
            {"name": "batch_number", "label": "Batch Number:", "required": False},
            {"name": "manufacturing_date", "label": "Manufacturing Date (YYYY-MM-DD):", "required": False},
            {"name": "expiry_date", "label": "Expiry Date (YYYY-MM-DD):", "required": False},
            {"name": "purchase_price", "label": "Purchase Price per Unit:", "required": False}
        ]
        
        # Variables to store entry values
        entry_vars = {}
        
        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                          text=field["label"],
                          font=FONTS["regular"],
                          bg=COLORS["bg_primary"],
                          fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=8, padx=10)
            
            # Entry
            entry_vars[field["name"]] = tk.StringVar()
            entry = tk.Entry(form_frame, 
                           textvariable=entry_vars[field["name"]],
                           font=FONTS["regular"],
                           width=25)
            entry.grid(row=i, column=1, pady=8, padx=10, sticky="w")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"], pady=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=lambda: stock_dialog.destroy())
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Function to save stock
        def save_stock():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Validation Error", f"{field['label']} is required.")
                    return
            
            # Validate quantity
            try:
                quantity = int(entry_vars["quantity"].get())
                if quantity <= 0:
                    messagebox.showerror("Validation Error", "Quantity must be greater than zero.")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity must be a whole number.")
                return
                
            # Validate purchase price if provided
            purchase_price = None
            if entry_vars["purchase_price"].get():
                try:
                    purchase_price = float(entry_vars["purchase_price"].get())
                except ValueError:
                    messagebox.showerror("Validation Error", "Purchase price must be a valid number.")
                    return
            
            # Get other values
            batch_number = entry_vars["batch_number"].get()
            manufacturing_date = entry_vars["manufacturing_date"].get() or None
            expiry_date = entry_vars["expiry_date"].get() or None
            
            # Construct inventory data
            inventory_data = {
                "product_id": product_id,
                "quantity": quantity,
                "batch_number": batch_number,
                "manufacturing_date": manufacturing_date,
                "expiry_date": expiry_date,
                "purchase_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "purchase_price": purchase_price
            }
            
            try:
                # Begin transaction
                self.controller.db.begin()
                
                # Insert into batches table first (this is what the UI uses to display inventory)
                batch_data = {
                    "product_id": product_id,
                    "quantity": quantity,
                    "batch_number": batch_number,
                    "manufacturing_date": manufacturing_date,
                    "expiry_date": expiry_date,
                    "purchase_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "cost_price": purchase_price if purchase_price is not None else 0.0
                }
                print(f"Adding batch data: {batch_data}")
                batch_id = self.controller.db.insert("batches", batch_data)
                print(f"Successfully added batch with ID: {batch_id}")
                
                # Also add to inventory table for backward compatibility
                print(f"Adding inventory data: {inventory_data}")
                inventory_id = self.controller.db.insert("inventory", inventory_data)
                print(f"Successfully added inventory with ID: {inventory_id}")
                
                # Commit transaction
                self.controller.db.commit()
                
                # Close dialog
                stock_dialog.destroy()
                messagebox.showinfo("Success", f"Stock added successfully for {product_name}.")
                
                # Refresh inventory
                self.load_inventory()
                self.load_batches(show_all=True)
                
            except Exception as e:
                # Rollback in case of error
                self.controller.db.rollback()
                print(f"Error adding stock: {e}")
                messagebox.showerror("Error", f"Failed to add stock: {e}")
        
        # Save button
        save_btn = tk.Button(button_frame,
                           text="Add Stock",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=save_stock)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def _set_dialog_transient(self, dialog):
        """Helper method to set dialog transient property correctly"""
        dialog.withdraw()  # Hide the window initially
        dialog.update_idletasks()  # Update "requested size" from geometry manager
        
        # Calculate position x, y for the window to be centered on parent
        x = self.winfo_rootx() + (self.winfo_width() / 2) - (dialog.winfo_width() / 2)
        y = self.winfo_rooty() + (self.winfo_height() / 2) - (dialog.winfo_height() / 2)
        
        # Set the position
        dialog.geometry(f"+{int(x)}+{int(y)}")
        dialog.deiconify()  # Show the window
        
    # Helper functions for product management
    def get_categories(self):
        """Get list of category names"""
        query = "SELECT name FROM categories ORDER BY name"
        result = self.controller.db.fetchall(query)
        return [cat[0] for cat in result] if result else []
        
    def get_vendors(self):
        """Get list of vendor names"""
        query = "SELECT name FROM vendors ORDER BY name"
        result = self.controller.db.fetchall(query)
        return [vendor[0] for vendor in result] if result else []
        
    def get_hsn_codes(self):
        """Get list of HSN codes with descriptions"""
        query = "SELECT code FROM hsn_codes ORDER BY code"
        result = self.controller.db.fetchall(query)
        return [code[0] for code in result] if result else []