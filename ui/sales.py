"""
Sales UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import re
import os
import decimal
from decimal import Decimal, InvalidOperation
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import calendar
import locale
import json

from assets.styles import COLORS, FONTS, STYLES
from utils.helpers import format_currency, parse_currency
from utils.pdf_invoice_generator import generate_invoice

class SalesFrame(tk.Frame):
    """Sales frame for processing transactions"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Store cart items
        self.cart_items = []
        self.next_item_id = 1
        
        # Track temporarily reserved inventory from cart
        self.reserved_inventory = {}
        
        # Current customer
        self.current_customer = {
            "id": 1,  # Default to Walk-in Customer
            "name": "Walk-in Customer",
            "phone": "",
            "address": ""
        }
        
        # Create layout
        self.create_layout()
        
        # We now use the database for suspended bills
        # self.suspended_bills is kept for backward compatibility but not used
        
        # Keyboard navigation variables
        self.current_focus = None  # Current focus area: 'cart', 'products', 'buttons'
        self.selected_cart_item = -1
        self.selected_product_item = -1
        
        # Bind keyboard events
        self.bind("<Key>", self.handle_key_event)
        self.focus_set()
    
    def _set_dialog_transient(self, dialog):
        """Helper method to set dialog transient property correctly"""
        # Get the top-level window for this frame
        root = self.winfo_toplevel()
        dialog.transient(root)
        # Center dialog on parent
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def create_layout(self):
        """Create the sales layout"""
        # Main container with two frames side by side
        main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Cart (55% width)
        self.left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"])
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Product search and customer info (45% width)
        self.right_panel = tk.Frame(main_container, bg=COLORS["bg_secondary"], width=500)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Make sure the right panel maintains width
        self.right_panel.grid_propagate(False)  # For grid layout
        self.right_panel.pack_propagate(False)  # For pack layout
        
        # Setup left panel (cart)
        self.setup_cart_panel(self.left_panel)
        
        # Setup right panel (product search)
        self.setup_product_panel(self.right_panel)
        
        # Add keyboard shortcuts info
        shortcut_frame = tk.Frame(self.right_panel, bg=COLORS["bg_secondary"], padx=10, pady=5)
        shortcut_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        shortcut_label = tk.Label(
            shortcut_frame,
            text="Keyboard Shortcuts: Tab: Cycle focus | Ctrl+Shift+P: Products | Ctrl+Shift+C: Cart | Ctrl+D: Add Customer | Enter: Add/Edit",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT
        )
        shortcut_label.pack(anchor="w")
        
    def load_customers_for_dropdown(self):
        """Load customer list for dropdown"""
        db = self.controller.db
        query = """
            SELECT id, name, phone FROM customers
            ORDER BY name
            LIMIT 100
        """
        customers = db.fetchall(query)
        
        # Format customer list for combobox
        customer_list = ["Walk-in Customer"]
        self.customer_data = {0: {"id": 1, "name": "Walk-in Customer", "phone": ""}}
        
        for customer in customers:
            display_text = f"{customer[1]} ({customer[2] if customer[2] else 'No phone'})"
            customer_list.append(display_text)
            self.customer_data[len(customer_list)-1] = {"id": customer[0], "name": customer[1], "phone": customer[2] or ""}
        
        # Store full customer list for reference
        self.full_customer_list = customer_list.copy()
        
        # Update combobox values - don't show all initially, just Walk-in
        # This is to avoid overwhelming dropdown and focus user on search
        self.customer_combo['values'] = ["Walk-in Customer"]
    
    def filter_customers(self, event):
        """Filter customers based on input in combobox with real-time filtering"""
        try:
            # Store cursor position
            cursor_pos = self.customer_combo.index(tk.INSERT)
            search_term = self.customer_var.get().strip().lower()
            
            # Skip filtering if the search term is empty or the placeholder
            if not search_term or search_term == "search customer":
                # Reset to default options when empty
                self.customer_combo['values'] = ["Walk-in Customer"]
                self.customer_data = {0: {"id": 1, "name": "Walk-in Customer", "phone": ""}}
                return
                
            # Get all customers matching the search term
            db = self.controller.db
            query = """
                SELECT id, name, phone FROM customers
                WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ?
                ORDER BY name
                LIMIT 50
            """
            
            # Use % for wildcard search
            search_pattern = f"%{search_term}%"
            customers = db.fetchall(query, (search_pattern, search_pattern))
            
            # Format customer list for combobox
            customer_list = ["Walk-in Customer"]
            self.customer_data = {0: {"id": 1, "name": "Walk-in Customer", "phone": ""}}
            
            # Add matching customers
            for customer in customers:
                display_text = f"{customer[1]} ({customer[2] if customer[2] else 'No phone'})"
                customer_list.append(display_text)
                self.customer_data[len(customer_list)-1] = {"id": customer[0], "name": customer[1], "phone": customer[2] or ""}
            
            # If no customers found (only Walk-in Customer), add "Add New Customer" option
            if len(customer_list) == 1:
                customer_list.append("+ Add New Customer (Ctrl+D)")
                self.customer_data[len(customer_list)-1] = {"id": "new", "name": "Add New Customer", "phone": ""}
            
            # Update combobox values
            current_text = self.customer_var.get()
            self.customer_combo['values'] = customer_list
            
            # Preserve the typed text and cursor position
            if current_text != "Search Customer":
                # Temporarily disable the trace to avoid recursive calls
                self.customer_var.trace_remove("write", self.trace_id)
                self.customer_var.set(current_text)
                # Re-enable the trace
                self.trace_id = self.customer_var.trace_add("write", lambda *args: self.schedule_filter())
                
                # Restore cursor position after a brief delay
                self.customer_combo.after_idle(lambda: self.customer_combo.icursor(cursor_pos))
                    
        except Exception as e:
            # Log any errors but don't crash the application
            print(f"Error in filter_customers: {str(e)}")
    
    def schedule_filter(self):
        """Schedule filtering with a small delay to avoid rapid calls"""
        # Cancel any pending filter calls
        if hasattr(self, 'filter_after_id'):
            self.after_cancel(self.filter_after_id)
        
        # Schedule new filter call with a small delay
        self.filter_after_id = self.after(100, self.delayed_filter)
    
    def delayed_filter(self):
        """Delayed filter function to prevent excessive database calls"""
        # Create a dummy event object for the filter function
        class DummyEvent:
            def __init__(self):
                self.keysym = None
        
        self.filter_customers(DummyEvent())
    
    def on_customer_selected(self, event):
        """Handle customer selection from dropdown"""
        selection = self.customer_combo.current()
        
        if selection >= 0 and selection in self.customer_data:
            customer_info = self.customer_data[selection]
            
            # Check if "Add New Customer" was selected
            if customer_info["id"] == "new":
                self.open_add_customer_dialog()
                return
            
            # Update current customer
            self.current_customer = {
                "id": customer_info["id"],
                "name": customer_info["name"],
                "phone": customer_info["phone"]
            }
            
            # Update customer label in cart panel
            self.customer_label.config(text=customer_info["name"])
    
    def set_walkin_customer(self):
        """Set customer to Walk-in Customer"""
        # Update combobox
        self.customer_var.set("Walk-in Customer")
        self.customer_combo.current(0)
        
        # Update current customer
        self.current_customer = {
            "id": 1,
            "name": "Walk-in Customer",
            "phone": ""
        }
        
        # Update customer label in cart panel
        self.customer_label.config(text="Walk-in Customer")
        
    def setup_customer_search_panel(self, parent):
        """Setup the customer search panel with dropdown and buttons"""
        # Get parent background color for consistent styling
        parent_bg = parent.cget("bg")
        
        # Clean container frame with minimal styling
        container = tk.Frame(parent, bg=parent_bg)
        container.pack(fill=tk.X, pady=5)
        
        # Customer label with clean styling
        customer_label = tk.Label(container, 
                                text="Customer:",
                                font=FONTS["regular_bold"],
                                bg=parent_bg,
                                fg=COLORS["text_primary"])
        customer_label.pack(side=tk.LEFT, padx=(5, 10))
        
        # Customer search variable
        self.customer_var = tk.StringVar()
        
        # Create autocomplete combobox with placeholder
        self.customer_combo = ttk.Combobox(container, 
                                         textvariable=self.customer_var,
                                         font=FONTS["regular"],
                                         width=30)
        self.customer_combo.pack(side=tk.LEFT, padx=5)
        
        # Set placeholder
        self.customer_combo.set("Search Customer")
        
        # Configure placeholder behavior
        def on_combo_focusin(event):
            if self.customer_var.get() == "Search Customer":
                self.customer_var.set("")
                
        def on_combo_focusout(event):
            if not self.customer_var.get().strip():
                self.customer_var.set("Search Customer")
        
        # Bind events for dropdown with placeholder behavior
        self.customer_combo.bind("<FocusIn>", on_combo_focusin)
        self.customer_combo.bind("<FocusOut>", on_combo_focusout)
        self.customer_combo.bind("<KeyRelease>", self.on_customer_key_release)
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_selected)
        self.customer_combo.bind("<Return>", self.on_customer_enter)
        
        # Set up trace for real-time filtering
        self.trace_id = self.customer_var.trace_add("write", lambda *args: self.schedule_filter())
        
        # Load initial customer list
        self.load_customers_for_dropdown()
    
    def on_customer_key_release(self, event):
        """Handle key release events in customer combobox"""
        # Handle specific keys without triggering filter
        if event.keysym in ('Return', 'KP_Enter', 'Tab', 'Escape', 'Up', 'Down'):
            return
        
        # For other keys, the trace will handle filtering
        pass
    
    def on_customer_enter(self, event):
        """Handle Enter key in customer combobox"""
        current_selection = self.customer_combo.current()
        
        # If a valid selection is made
        if current_selection >= 0 and current_selection in self.customer_data:
            customer_info = self.customer_data[current_selection]
            
            # Check if "Add New Customer" was selected
            if customer_info["id"] == "new":
                self.open_add_customer_dialog()
                return "break"
            
            # Otherwise, select the customer
            self.on_customer_selected(event)
            return "break"
        
        # If no selection but text exists, try to find matching customer
        search_text = self.customer_var.get().strip()
        if search_text and search_text.lower() != "search customer":
            # Look for exact match or close match
            for idx, customer_info in self.customer_data.items():
                if customer_info["name"].lower().startswith(search_text.lower()):
                    self.customer_combo.current(idx)
                    self.on_customer_selected(event)
                    return "break"
            
            # No match found, offer to add new customer
            if messagebox.askyesno("Customer Not Found", 
                                 f"Customer '{search_text}' not found.\n\nWould you like to add this as a new customer?"):
                self.open_add_customer_dialog(default_name=search_text)
                return "break"
    
    def open_add_customer_dialog(self, default_name=""):
        """Open the add customer dialog with optional default name"""
        # Reset customer combobox to avoid conflicts
        self.customer_var.set("Search Customer")
        
        # Call the existing change_customer method with add_new=True
        self.change_customer(add_new=True, default_name=default_name)
        
        # Walk-in customer button with clean styling
        walkin_btn = tk.Button(container,
                             text="Walk-in",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=10,
                             pady=3,
                             cursor="hand2",
                             command=self.set_walkin_customer)
        walkin_btn.pack(side=tk.LEFT, padx=5)
        
        # New customer button with clean styling
        new_btn = tk.Button(container,
                          text="+ New",
                          font=FONTS["regular"],
                          bg=COLORS["secondary"],
                          fg=COLORS["text_white"],
                          padx=10,
                          pady=3,
                          cursor="hand2",
                          command=lambda: self.change_customer(add_new=True))
        new_btn.pack(side=tk.LEFT, padx=5)
        
        # Directory button with clean styling
        dir_btn = tk.Button(container,
                          text="📁",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=8,
                          pady=3,
                          cursor="hand2",
                          command=self.change_customer)
        dir_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_cart_panel(self, parent):
        """Setup the cart panel with item list and totals"""
        # Clean customer info frame without excessive styling
        customer_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], pady=5, padx=5)
        customer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Setup customer search panel with dropdown and buttons
        self.setup_customer_search_panel(customer_frame)
        
        # Hidden customer label (still needed for some functions)
        self.customer_label = tk.Label(self, 
                                     text="Walk-in Customer", 
                                     font=FONTS["regular"])
        self.customer_label.pack_forget()
        
        # Create a frame for cart label and date picker
        cart_header_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        cart_header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Cart label
        cart_label = tk.Label(cart_header_frame, 
                             text="Cart Items",
                             font=FONTS["subheading"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        cart_label.pack(side=tk.LEFT)
        
        # Invoice date label and picker
        date_frame = tk.Frame(cart_header_frame, bg=COLORS["bg_primary"])
        date_frame.pack(side=tk.RIGHT)
        
        date_label = tk.Label(date_frame,
                             text="Invoice Date:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        date_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create date entry with calendar button
        self.invoice_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%d/%m/%Y"))
        self.invoice_date_obj = datetime.datetime.now()  # Store the actual date object
        date_entry = ttk.Entry(date_frame,
                             textvariable=self.invoice_date_var,
                             width=12,
                             font=FONTS["regular"],
                             style='primary.TEntry')
        date_entry.pack(side=tk.LEFT)
        
        def show_calendar():
            # Parse current date from DD/MM/YYYY format
            try:
                current_date = datetime.datetime.strptime(self.invoice_date_var.get(), "%d/%m/%Y").date()
            except ValueError:
                current_date = datetime.datetime.now().date()
                
            dialog = DatePickerDialog(
                parent=self,
                title="Select Invoice Date",
                firstweekday=6,  # Sunday first
                startdate=current_date,
                bootstyle="primary"
            )
            if hasattr(dialog, 'date_selected'):
                # Store both the string and datetime object
                self.invoice_date_var.set(dialog.date_selected.strftime("%d/%m/%Y"))
                self.invoice_date_obj = datetime.datetime.combine(dialog.date_selected, datetime.datetime.now().time())
        
        # Add calendar button
        cal_button = ttk.Button(date_frame,
                              text="📅",
                              style='primary.TButton',
                              width=3,
                              command=show_calendar)
        cal_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Cart treeview frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        
        # Create treeview for cart items
        self.cart_tree = ttk.Treeview(tree_frame, 
                                    columns=("product", "price", "qty", "discount", "total"),
                                    show="headings",
                                    yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.cart_tree.yview)
        
        # Define columns
        self.cart_tree.heading("product", text="Product")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("discount", text="Disc %")
        self.cart_tree.heading("total", text="Total")
        
        # Set column widths
        self.cart_tree.column("product", width=250)
        self.cart_tree.column("price", width=100)
        self.cart_tree.column("qty", width=70)
        self.cart_tree.column("discount", width=70)
        self.cart_tree.column("total", width=120)
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to edit item
        self.cart_tree.bind("<Double-1>", self.edit_cart_item)
        # Bind right-click for context menu
        self.cart_tree.bind("<Button-3>", self.show_cart_context_menu)
        
        # Totals and payment frame
        totals_frame = tk.Frame(parent, bg=COLORS["bg_white"], padx=10, pady=10)
        totals_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Subtotal
        tk.Label(totals_frame, 
               text="Subtotal:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", pady=5)
               
        self.subtotal_label = tk.Label(totals_frame, 
                                     text="₹0.00",
                                     font=FONTS["regular"],
                                     bg=COLORS["bg_white"],
                                     fg=COLORS["text_primary"])
        self.subtotal_label.grid(row=0, column=1, sticky="e", pady=5)
        
        # Discount
        tk.Label(totals_frame, 
               text="Discount:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", pady=5)
        
        discount_frame = tk.Frame(totals_frame, bg=COLORS["bg_white"])
        discount_frame.grid(row=1, column=1, sticky="e", pady=5)
        
        self.discount_var = tk.StringVar(value="0.00")
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=self.discount_var,
                                font=FONTS["regular"],
                                width=8)
        discount_entry.pack(side=tk.LEFT)
        
        self.discount_type_var = tk.StringVar(value="amount")
        discount_type = ttk.Combobox(discount_frame, 
                                   textvariable=self.discount_type_var,
                                   values=["amount", "%"],
                                   width=5,
                                   state="readonly")
        discount_type.pack(side=tk.LEFT, padx=(5, 0))
        
        # Label to show calculated discount amount
        self.discount_amount_label = tk.Label(totals_frame, 
                                           text="- ₹0.00",
                                           font=FONTS["regular"],
                                           bg=COLORS["bg_white"],
                                           fg=COLORS["danger"])
        # Not displaying this label directly in the grid, but keeping it for update_totals()
        
        # Bind discount changes
        self.discount_var.trace_add("write", lambda *args: self.update_totals())
        self.discount_type_var.trace_add("write", lambda *args: self.update_totals())
        
        # CGST (9%)
        tk.Label(totals_frame, 
               text="CGST (9%):",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", pady=3)
               
        self.cgst_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        self.cgst_label.grid(row=2, column=1, sticky="e", pady=3)
        
        # SGST (9%)
        tk.Label(totals_frame, 
               text="SGST (9%):",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=3, column=0, sticky="w", pady=3)
               
        self.sgst_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        self.sgst_label.grid(row=3, column=1, sticky="e", pady=3)
        
        # Total Tax (for compatibility)
        self.tax_label = tk.Label(totals_frame, 
                                text="₹0.00",
                                font=FONTS["regular"],
                                bg=COLORS["bg_white"],
                                fg=COLORS["text_primary"])
        # Not showing this label but keeping it for code compatibility
        
        # Total
        tk.Label(totals_frame, 
               text="TOTAL:",
               font=FONTS["heading"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=4, column=0, sticky="w", pady=10)
               
        self.total_label = tk.Label(totals_frame, 
                                  text="₹0.00",
                                  font=FONTS["heading"],
                                  bg=COLORS["bg_white"],
                                  fg=COLORS["primary"])
        self.total_label.grid(row=4, column=1, sticky="e", pady=10)
        
        # Make totals_frame columns expandable
        totals_frame.columnconfigure(0, weight=1)
        totals_frame.columnconfigure(1, weight=1)
        
        # Payment buttons frame
        payment_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=10)
        payment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cancel button
        cancel_btn = tk.Button(payment_frame,
                             text="CANCEL",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=10,
                             cursor="hand2",
                             command=self.cancel_sale)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Suspend button - for saving a sale for later
        suspend_btn = tk.Button(payment_frame,
                              text="SUSPEND",
                              font=FONTS["regular_bold"],
                              bg=COLORS["warning"],
                              fg=COLORS["text_primary"],
                              padx=15,
                              pady=10,
                              cursor="hand2",
                              command=self.suspend_sale)
        suspend_btn.pack(side=tk.LEFT, padx=5)
        
        # Suspended bills button
        suspended_btn = tk.Button(payment_frame,
                                text="SUSPENDED",
                                font=FONTS["regular_bold"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"],
                                padx=15,
                                pady=10,
                                cursor="hand2",
                                command=self.show_suspended_bills)
        suspended_btn.pack(side=tk.LEFT, padx=5)
        
        # Right-aligned payment buttons
        payment_btns_frame = tk.Frame(payment_frame, bg=COLORS["bg_primary"])
        payment_btns_frame.pack(side=tk.RIGHT)
        
        # Cash payment button
        cash_btn = tk.Button(payment_btns_frame,
                           text="CASH",
                           font=FONTS["regular_bold"],
                           bg=COLORS["success"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=10,
                           cursor="hand2",
                           command=lambda: self.process_payment("CASH"))
        cash_btn.pack(side=tk.LEFT, padx=5)
        
        # UPI payment button
        upi_btn = tk.Button(payment_btns_frame,
                          text="UPI",
                          font=FONTS["regular_bold"],
                          bg=COLORS["secondary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=10,
                          cursor="hand2",
                          command=lambda: self.process_payment("UPI"))
        upi_btn.pack(side=tk.LEFT, padx=5)
        
        # Credit payment button
        credit_btn = tk.Button(payment_btns_frame,
                             text="CREDIT",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=10,
                             cursor="hand2",
                             command=lambda: self.process_payment("CREDIT"))
        credit_btn.pack(side=tk.LEFT, padx=5)
        
        # Split payment button
        split_btn = tk.Button(payment_btns_frame,
                            text="SPLIT",
                            font=FONTS["regular_bold"],
                            bg=COLORS["info"],
                            fg=COLORS["text_white"],
                            padx=15,
                            pady=10,
                            cursor="hand2",
                            command=lambda: self.process_payment("SPLIT"))
        split_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_product_panel(self, parent):
        """Setup the product search panel"""
        # Product search section
        search_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=5)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search label and entry in the same row for compact layout
        search_label = tk.Label(search_frame, 
                              text="Search Products:",
                              font=FONTS["regular_bold"],
                              bg=COLORS["bg_secondary"],
                              fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, pady=5)
        
        # Search input with autocommit
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.search_var,
                              font=FONTS["regular"],
                              width=25)
        search_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0), pady=5)
        
        # Bind search input changes to search_products method
        self.search_var.trace_add("write", lambda *args: self.search_products())
        
        # Product list section - give it more vertical space
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Product list label
        products_label = tk.Label(list_frame, 
                                text="Products List",
                                font=FONTS["subheading"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"])
        products_label.pack(anchor="w", padx=5, pady=(5, 5))
        
        # Products treeview frame - make it taller
        products_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        products_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add both vertical and horizontal scrollbars
        scrollbar_y = ttk.Scrollbar(products_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(products_frame, orient='horizontal')
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Products treeview with both scrollbars
        self.products_tree = ttk.Treeview(products_frame, 
                                        columns=("id", "name", "price", "stock"),
                                        show="headings",
                                        yscrollcommand=scrollbar_y.set,
                                        xscrollcommand=scrollbar_x.set,
                                        height=15)  # Increase visible rows
        
        # Configure scrollbars
        scrollbar_y.config(command=self.products_tree.yview)
        scrollbar_x.config(command=self.products_tree.xview)
        
        # Define columns
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Product Name")
        self.products_tree.heading("price", text="Price")
        self.products_tree.heading("stock", text="Stock")
        
        # Set column widths - make product name wider
        self.products_tree.column("id", width=50, minwidth=50)
        self.products_tree.column("name", width=250, minwidth=150)
        self.products_tree.column("price", width=80, minwidth=80)
        self.products_tree.column("stock", width=60, minwidth=60)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to add to cart
        self.products_tree.bind("<Double-1>", self.add_to_cart)
        # Bind Enter key directly to the treeview
        self.products_tree.bind("<Return>", self.add_to_cart)
        
        # Load products initially
        self.load_products()
        
        # Action buttons frame - more compact layout
        action_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=5)
        action_frame.pack(fill=tk.X, pady=5)
        
        # Button frame with two buttons side by side
        button_frame = tk.Frame(action_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X)
        
        # Add to cart button
        add_to_cart_btn = tk.Button(button_frame,
                                  text="Add to Cart",
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["primary"],
                                  fg=COLORS["text_white"],
                                  padx=10,
                                  pady=5,
                                  cursor="hand2",
                                  command=lambda: self.add_to_cart(None))
        add_to_cart_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Quick add button
        quick_add_btn = tk.Button(button_frame,
                                text="Quick Add",
                                font=FONTS["regular"],
                                bg=COLORS["secondary"],
                                fg=COLORS["text_white"],
                                padx=10,
                                pady=5,
                                cursor="hand2",
                                command=self.quick_add_item)
        quick_add_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def get_hsn_codes(self):
        """Get list of HSN codes with descriptions"""
        query = "SELECT code, description FROM hsn_codes ORDER BY code"
        results = self.controller.db.fetchall(query)
        
        hsn_codes = []
        for hsn in results:
            # Format as "CODE: DESCRIPTION" for better readability in dropdown
            if hsn[0]:
                hsn_code_text = f"{hsn[0]}"
                if hsn[1]:
                    hsn_code_text += f": {hsn[1]}"
                hsn_codes.append(hsn_code_text)
                
        return hsn_codes
    
    def load_products(self):
        """Load products from database into treeview"""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        # Get products from database
        db = self.controller.db
        products = db.fetchall("""
            SELECT p.id, p.name, p.selling_price, COALESCE(SUM(b.quantity), 0) as stock
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id AND (b.expiry_date > date('now') OR b.expiry_date IS NULL)
            GROUP BY p.id, p.name, p.selling_price
            ORDER BY p.name
        """)
        
        # Insert products into treeview, subtracting reserved quantities
        for product in products:
            product_id, name, price, stock = product
            
            # Subtract reserved quantity if this product is in cart
            reserved_qty = self.reserved_inventory.get(product_id, 0)
            available_stock = max(0, stock - reserved_qty)
            
            # Format price with Rupee symbol
            formatted_price = format_currency(price)
            
            # Insert into treeview with adjusted stock
            self.products_tree.insert("", "end", values=(product_id, name, formatted_price, available_stock))
            
            # Debug log for visibility
            if reserved_qty > 0:
                print(f"DEBUG: Product {product_id} '{name}' has {stock} in inventory, {reserved_qty} reserved, {available_stock} available")
    
    def search_products(self):
        """Search products based on search term"""
        search_term = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        # If search term is empty, load all products
        if not search_term:
            self.load_products()
            return
            
        # Get products from database that match search term
        db = self.controller.db
        products = db.fetchall("""
            SELECT p.id, p.name, p.selling_price, COALESCE(SUM(b.quantity), 0) as stock
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id AND (b.expiry_date > date('now') OR b.expiry_date IS NULL)
            WHERE p.name LIKE ? OR p.product_code LIKE ? OR p.description LIKE ?
            GROUP BY p.id, p.name, p.selling_price
            ORDER BY p.name
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        # Insert matching products into treeview, accounting for reserved inventory
        for product in products:
            product_id, name, price, stock = product
            
            # Subtract reserved quantity if this product is in cart
            reserved_qty = self.reserved_inventory.get(product_id, 0)
            available_stock = max(0, stock - reserved_qty)
            
            # Format price with Rupee symbol
            formatted_price = format_currency(price)
            
            # Insert into treeview with adjusted stock
            self.products_tree.insert("", "end", values=(product_id, name, formatted_price, available_stock))
    
    def add_to_cart(self, event=None):
        """Add selected product to cart with batch selection"""
        # Get selected product
        if event:  # Triggered by double-click
            selected_item = self.products_tree.selection()
            if not selected_item:
                return
            item = selected_item[0]
        else:  # Triggered by button
            selected_items = self.products_tree.selection()
            if not selected_items:
                messagebox.showinfo("Select Product", "Please select a product first!")
                return
            item = selected_items[0]
            
        # Get product details
        product_values = self.products_tree.item(item, "values")
        product_id = product_values[0]
        product_name = product_values[1]
        product_price = parse_currency(product_values[2])
        available_stock = int(product_values[3])
        
        # Get additional product details and batches from database
        db = self.controller.db
        product_details = db.fetchone("""
            SELECT p.hsn_code, p.tax_percentage
            FROM products p
            WHERE p.id = ?
        """, (product_id,))
        
        # Set default values if not found
        if product_details:
            hsn_code = product_details[0] or ""
            tax_percentage = product_details[1] or 18  # Default 18% GST if not set
        else:
            hsn_code = ""
            tax_percentage = 18  # Default 18% GST
            
        # Get batches separately for better handling
        batch_query = """
            SELECT b.id, b.batch_number, b.quantity, b.expiry_date, 
                   COALESCE(b.selling_price, p.selling_price) as selling_price,
                   b.manufacturing_date
            FROM batches b
            JOIN products p ON b.product_id = p.id
            WHERE b.product_id = ? 
            AND b.quantity > 0
            AND (b.expiry_date > date('now') OR b.expiry_date IS NULL)
            ORDER BY 
                CASE WHEN b.expiry_date IS NULL THEN 1 ELSE 0 END,
                b.expiry_date ASC,
                b.manufacturing_date ASC
        """
        
        batch_rows = db.fetchall(batch_query, (product_id,))
        
        # Parse batch information
        batches = []
        for batch_row in batch_rows:
            try:
                batches.append({
                    'id': batch_row[0],
                    'number': batch_row[1] or f"BATCH-{batch_row[0]}",
                    'quantity': batch_row[2],
                    'expiry': batch_row[3],
                    'selling_price': float(batch_row[4]) if batch_row[4] else product_price,
                    'manufacturing_date': batch_row[5]
                })
            except (ValueError, IndexError, TypeError) as e:
                print(f"Error parsing batch data: {e}")
                continue
        
        # Check stock
        if available_stock <= 0:
            messagebox.showwarning("Out of Stock", 
                                  f"{product_name} is out of stock!")
            return
            
        # Create a variable to track if item was added to cart
        item_added = [False]
        temporary_reservation = 0
            
        # Ask for quantity and discount
        dialog = tk.Toplevel(self)
        dialog.title("Add to Cart")
        dialog.geometry("400x350")  # Made taller to accommodate batch dropdown
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        tk.Label(content_frame, 
               text=product_name,
               font=FONTS["subheading"]).pack(pady=(0, 10))
        
        # Get real-time available quantity from database (accounting for any current reservations)
        db_stock = db.fetchone("""
            SELECT COALESCE(SUM(b.quantity), 0) as stock
            FROM products p
            LEFT JOIN batches b ON p.id = b.product_id AND (b.expiry_date > date('now') OR b.expiry_date IS NULL)
            WHERE p.id = ?
            GROUP BY p.id
        """, (product_id,))
        
        actual_stock = db_stock[0] if db_stock else 0
        reserved_qty = self.reserved_inventory.get(product_id, 0)
        real_available_stock = max(0, actual_stock - reserved_qty)
        
        # Update the label to show the real-time available stock
        stock_label = tk.Label(content_frame, 
               text=f"Price: {product_values[2]} | Available: {real_available_stock}",
               font=FONTS["regular"])
        stock_label.pack(pady=(0, 20))
        
        # If item is truly out of stock, show warning and close dialog
        if real_available_stock <= 0:
            dialog.after(100, lambda: [
                messagebox.showwarning("Out of Stock", f"{product_name} is out of stock!"),
                dialog.destroy()
            ])
            return
        
        # Price variable that will be updated based on batch selection
        current_price = [product_price]  # Use list for reference
        
        # Batch selection (show for any product with batches)
        selected_batch = [None]  # Use list to store selected batch for access in nested functions
        batch_frame = None
        
        # Always show batch selection if batches exist
        if len(batches) > 0:
            batch_frame = tk.Frame(content_frame)
            batch_frame.pack(fill=tk.X, pady=10)
            
            # Add a separator line for better visual separation
            separator = tk.Frame(batch_frame, height=2, bg=COLORS["bg_secondary"])
            separator.pack(fill=tk.X, pady=(0, 10))
            
            batch_label = tk.Label(batch_frame, 
                   text="Select Batch:",
                   font=FONTS["regular_bold"])
            batch_label.pack(anchor="w", pady=(0, 5))
            
            # Create batch options with expiry dates and prices
            batch_options = []
            for batch in batches:
                expiry_str = f" (Exp: {batch['expiry']})" if batch['expiry'] else " (No Expiry)"
                price_str = f" - ₹{batch['selling_price']:.2f}"
                batch_options.append(f"{batch['number']}{expiry_str}{price_str} - {batch['quantity']} units")
            
            batch_var = tk.StringVar(value=batch_options[0] if batch_options else "")
            batch_combo = ttk.Combobox(batch_frame,
                                     textvariable=batch_var,
                                     values=batch_options,
                                     font=FONTS["regular"],
                                     width=50,
                                     state="readonly")
            batch_combo.pack(fill=tk.X, pady=5)
            
            # Show batch count for clarity
            batch_count_label = tk.Label(batch_frame,
                                       text=f"Available batches: {len(batches)}",
                                       font=FONTS["small"],
                                       fg=COLORS["text_secondary"])
            batch_count_label.pack(anchor="w", pady=(5, 0))
            
            # Store selected batch info and update price
            def on_batch_select(event=None):
                selected = batch_var.get()
                for i, batch in enumerate(batches):
                    expiry_str = f" (Exp: {batch['expiry']})" if batch['expiry'] else " (No Expiry)"
                    price_str = f" - ₹{batch['selling_price']:.2f}"
                    if selected.startswith(f"{batch['number']}{expiry_str}{price_str}"):
                        selected_batch[0] = batch
                        current_price[0] = batch['selling_price']
                        # Update the price and stock display for this specific batch
                        stock_label.config(text=f"Price: ₹{batch['selling_price']:.2f} | Available: {batch['quantity']} units")
                        break
            
            batch_combo.bind("<<ComboboxSelected>>", on_batch_select)
            
            # Set initial batch selection
            if batch_options:
                selected_batch[0] = batches[0]
                current_price[0] = batches[0]['selling_price']
                # Update initial display with first batch info
                stock_label.config(text=f"Price: ₹{batches[0]['selling_price']:.2f} | Available: {batches[0]['quantity']} units")
                
            # If only one batch, show it but make it clear it's auto-selected
            if len(batches) == 1:
                batch_combo.config(state="disabled")
                # Add a note for single batch
                note_label = tk.Label(batch_frame, 
                                    text="(Only one batch available - auto-selected)",
                                    font=FONTS["small"],
                                    fg=COLORS["text_secondary"])
                note_label.pack(anchor="w", pady=(0, 5))
        else:
            # Show message when no batches are available
            no_batch_frame = tk.Frame(content_frame)
            no_batch_frame.pack(fill=tk.X, pady=10)
            
            separator = tk.Frame(no_batch_frame, height=2, bg=COLORS["bg_secondary"])
            separator.pack(fill=tk.X, pady=(0, 10))
            
            no_batch_label = tk.Label(no_batch_frame, 
                                    text="⚠️ No batches available for this product",
                                    font=FONTS["regular"],
                                    fg=COLORS["danger"])
            no_batch_label.pack(anchor="w")
        
        # Quantity
        qty_frame = tk.Frame(content_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qty_frame, 
               text="Quantity:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        qty_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=10)
        qty_entry.grid(row=0, column=1, sticky="w")
        qty_entry.select_range(0, tk.END)  # Select all text
        
        # Item discount
        discount_frame = tk.Frame(content_frame)
        discount_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(discount_frame, 
               text="Discount (%):",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        discount_var = tk.StringVar(value="0")
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=0, column=1, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def on_dialog_close():
            """Handle dialog close and cleanup any temporary reservation"""
            if not item_added[0]:
                print(f"DEBUG: Dialog canceled, no items added")
                if temporary_reservation > 0:
                    # Clean up any temporary reservation
                    print(f"DEBUG: Cleaning up temporary reservation of {temporary_reservation} units for product {product_id}")
                    if product_id in self.reserved_inventory:
                        self.reserved_inventory[product_id] -= temporary_reservation
                        if self.reserved_inventory[product_id] <= 0:
                            del self.reserved_inventory[product_id]
            
            # Refresh product list to show updated stock
            self.load_products()
            dialog.destroy()
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=on_dialog_close)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def add_item():
            try:
                quantity = int(qty_var.get())
                discount = float(discount_var.get())
                
                # Validate quantity
                if quantity <= 0:
                    messagebox.showwarning("Invalid Quantity", 
                                         "Quantity must be greater than zero!")
                    return
                
                # Check batch-specific stock if batch selection exists
                if len(batches) > 0:
                    if not selected_batch[0]:
                        messagebox.showwarning("No Batch Selected", "Please select a batch!")
                        return
                    
                    if quantity > selected_batch[0]['quantity']:
                        messagebox.showwarning("Insufficient Stock", 
                                             f"Only {selected_batch[0]['quantity']} units available in batch {selected_batch[0]['number']}!")
                        return
                else:
                    # No batches available - this shouldn't happen if we have proper batch management
                    messagebox.showwarning("No Stock Available", 
                                         f"No batches available for {product_name}. Please add stock first.")
                    return
                
                # Validate discount
                if discount < 0 or discount > 100:
                    messagebox.showwarning("Invalid Discount", 
                                         "Discount must be between 0 and 100!")
                    return
                
                # Use batch-specific price if available
                item_price = current_price[0] if selected_batch[0] else product_price
                
                # Calculate total - use Decimal for consistent math with money values
                discount_factor = Decimal('1') - (Decimal(str(discount)) / Decimal('100'))
                total = Decimal(str(item_price)) * Decimal(str(quantity)) * discount_factor
                
                # Check if product already exists in cart
                existing_item = None
                for item in self.cart_items:
                    if item["product_id"] == product_id and item.get("batch_id") == (selected_batch[0]['id'] if selected_batch[0] else None):
                        existing_item = item
                        break
                
                if existing_item:
                    # Update existing item quantity and total
                    new_quantity = existing_item["quantity"] + quantity
                    new_total = Decimal(str(item_price)) * Decimal(str(new_quantity)) * discount_factor
                    existing_item["quantity"] = new_quantity
                    existing_item["total"] = new_total
                    existing_item["price"] = item_price  # Update price to batch price
                    
                    # Update batch information if this item has a specific batch
                    if selected_batch[0]:
                        existing_item.update({
                            "batch_id": selected_batch[0]['id'],
                            "batch_number": selected_batch[0]['number'],
                            "expiry_date": selected_batch[0]['expiry']
                        })
                    
                    print(f"DEBUG: Updated existing cart item. New quantity: {new_quantity}, batch_id: {existing_item.get('batch_id', 'None')}")
                    
                    # Update reserved inventory
                    if product_id not in self.reserved_inventory:
                        self.reserved_inventory[product_id] = quantity
                    else:
                        self.reserved_inventory[product_id] += quantity
                else:
                    # Add as new item to cart
                    cart_item = {
                        "id": self.next_item_id,
                        "product_id": product_id,
                        "name": product_name,
                        "price": item_price,  # Use batch-specific price
                        "quantity": quantity,
                        "discount": discount,
                        "total": total,
                        "hsn_code": hsn_code,
                        "tax_percentage": tax_percentage
                    }
                    
                    # Add batch information if available
                    if selected_batch[0]:
                        cart_item.update({
                            "batch_id": selected_batch[0]['id'],
                            "batch_number": selected_batch[0]['number'],
                            "expiry_date": selected_batch[0]['expiry']
                        })
                        print(f"DEBUG: Added cart item with batch_id: {selected_batch[0]['id']} for product {product_id}")
                    
                    self.cart_items.append(cart_item)
                    
                    # Increment next item ID
                    self.next_item_id += 1
                    print(f"DEBUG: Added new cart item with ID: {self.next_item_id-1}")
                    
                    # Track this inventory as reserved
                    if product_id not in self.reserved_inventory:
                        self.reserved_inventory[product_id] = quantity
                    else:
                        self.reserved_inventory[product_id] += quantity
                
                print(f"DEBUG: Reserved {quantity} units of product {product_id}, total reserved: {self.reserved_inventory[product_id]}")
                
                # Mark that the item was successfully added
                item_added[0] = True
                
                # Update cart display
                self.update_cart()
                
                # Refresh product list to display updated stock
                self.load_products()
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning("Invalid Input", 
                                     "Please enter valid numbers for quantity and discount!")
        
        add_btn = tk.Button(button_frame,
                          text="Add to Cart",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=20,
                          pady=5,
                          command=add_item)
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to quantity entry
        qty_entry.focus_set()
        
        # Bind Enter key to add_item function
        dialog.bind("<Return>", lambda event: add_item())
        
        # Handle dialog close event (e.g. if user clicks X button)
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # Refresh product list after dialog closes
        self.load_products()
    
    def quick_add_item(self):
        """Add an item without barcode/product lookup"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Quick Add Item")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Add Custom Item",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Product name
        name_frame = tk.Frame(content_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(name_frame, 
               text="Name:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, 
                            textvariable=name_var,
                            font=FONTS["regular"],
                            width=30)
        name_entry.grid(row=0, column=1, sticky="w")
        
        # Price
        price_frame = tk.Frame(content_frame)
        price_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(price_frame, 
               text="Price:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        price_var = tk.StringVar()
        price_entry = tk.Entry(price_frame, 
                             textvariable=price_var,
                             font=FONTS["regular"],
                             width=15)
        price_entry.grid(row=0, column=1, sticky="w")
        
        # Quantity
        qty_frame = tk.Frame(content_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qty_frame, 
               text="Quantity:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        qty_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=10)
        qty_entry.grid(row=0, column=1, sticky="w")
        
        # Tax rate (GST)
        tax_frame = tk.Frame(content_frame)
        tax_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(tax_frame, 
               text="GST Rate:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        tax_var = tk.StringVar(value="18")
        tax_combo = ttk.Combobox(tax_frame, 
                               textvariable=tax_var,
                               values=["0", "5", "12", "18", "28"],
                               font=FONTS["regular"],
                               width=10,
                               state="readonly")
        tax_combo.grid(row=0, column=1, sticky="w")
        
        # Item discount
        discount_frame = tk.Frame(content_frame)
        discount_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(discount_frame, 
               text="Discount (%):",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        discount_var = tk.StringVar(value="0")
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=0, column=1, sticky="w")
        
        # Add HSN/SAC code field with dropdown
        hsn_frame = tk.Frame(content_frame)
        hsn_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(hsn_frame, 
               text="HSN/SAC Code:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        hsn_var = tk.StringVar()
        hsn_combo = ttk.Combobox(hsn_frame, 
                               textvariable=hsn_var,
                               values=self.get_hsn_codes(),
                               font=FONTS["regular"],
                               width=25)
        hsn_combo.grid(row=0, column=1, sticky="w")
        
        # Allow user to type in the combobox
        hsn_combo.configure(state="normal")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def add_item():
            try:
                # Get values
                name = name_var.get().strip()
                price = float(price_var.get())
                quantity = int(qty_var.get())
                discount = float(discount_var.get())
                hsn_code = hsn_var.get().strip()
                
                # Validate
                if not name:
                    messagebox.showwarning("Missing Name", 
                                         "Please enter a product name!")
                    return
                
                if price <= 0:
                    messagebox.showwarning("Invalid Price", 
                                         "Price must be greater than zero!")
                    return
                
                if quantity <= 0:
                    messagebox.showwarning("Invalid Quantity", 
                                         "Quantity must be greater than zero!")
                    return
                
                if discount < 0 or discount > 100:
                    messagebox.showwarning("Invalid Discount", 
                                         "Discount must be between 0 and 100!")
                    return
                
                # Calculate total - use Decimal for consistent math with money values
                discount_factor = Decimal('1') - (Decimal(str(discount)) / Decimal('100'))
                total = Decimal(str(price)) * Decimal(str(quantity)) * discount_factor
                
                # Add to cart
                self.cart_items.append({
                    "id": self.next_item_id,
                    "product_id": None,  # None for custom items
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "discount": discount,
                    "total": total,
                    "hsn_code": hsn_code,
                    "tax_percentage": float(tax_var.get())
                })
                
                # Increment next item ID
                self.next_item_id += 1
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning("Invalid Input", 
                                     "Please enter valid numbers for price, quantity, and discount!")
        
        add_btn = tk.Button(button_frame,
                          text="Add to Cart",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=20,
                          pady=5,
                          command=add_item)
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to name entry
        name_entry.focus_set()
        
        # Bind Enter key to move between fields
        name_entry.bind("<Return>", lambda event: price_entry.focus_set())
        price_entry.bind("<Return>", lambda event: qty_entry.focus_set())
        qty_entry.bind("<Return>", lambda event: tax_combo.focus_set())
        tax_combo.bind("<Return>", lambda event: discount_entry.focus_set())
        discount_entry.bind("<Return>", lambda event: hsn_combo.focus_set())
        hsn_combo.bind("<Return>", lambda event: add_item())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def update_cart(self):
        """Update the cart treeview display"""
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        # Add updated items
        for item in self.cart_items:
            # Format values for display
            product_name = item["name"]
            price = format_currency(item["price"])
            quantity = str(item["quantity"])
            discount = f"{item.get('discount', 0)}%" if item.get('discount', 0) > 0 else "0%"
            total = format_currency(item["total"])
            
            # Insert into treeview with correct column mapping
            self.cart_tree.insert("", "end", values=(
                product_name,  # product column
                price,         # price column
                quantity,      # qty column
                discount,      # discount column
                total          # total column
            ))
            
        # Update totals after cart display is updated
        self.update_totals()
    
    def update_totals(self):
        """Calculate and update cart totals with correct GST handling for inclusive pricing"""
        # Initialize totals
        subtotal = Decimal('0')
        taxable_value = Decimal('0')
        total_tax = Decimal('0')
        total_cgst = Decimal('0')
        total_sgst = Decimal('0')
        
        # First calculate item-level totals and taxes
        for item in self.cart_items:
            # Get item details with proper decimal handling
            inclusive_price = Decimal(str(item["price"]))
            quantity = Decimal(str(item["quantity"]))
            item_discount_pct = Decimal(str(item.get("discount", 0))) / Decimal('100')
            gst_rate = Decimal(str(item.get("tax_percentage", 18))) / Decimal('100')
            
            # Calculate item total before discount (inclusive of GST)
            item_total = inclusive_price * quantity
            
            # Apply item-level discount
            item_discount_amount = item_total * item_discount_pct
            item_discounted_total = item_total - item_discount_amount
            
            # Calculate taxable value from discounted total (inclusive price)
            # Formula: taxable_value = total_price / (1 + gst_rate)
            item_taxable_value = item_discounted_total / (Decimal('1') + gst_rate)
            
            # Calculate GST amount (difference between total and taxable value)
            item_tax = item_discounted_total - item_taxable_value
            
            # Split GST into CGST and SGST (50-50)
            item_cgst = item_tax / Decimal('2')
            item_sgst = item_tax / Decimal('2')
            
            # Update item totals
            item["total"] = item_discounted_total
            item["taxable_value"] = item_taxable_value
            item["tax_amount"] = item_tax
            item["cgst_amount"] = item_cgst
            item["sgst_amount"] = item_sgst
            
            # Add to running totals
            subtotal += item_discounted_total
            taxable_value += item_taxable_value
            total_tax += item_tax
            total_cgst += item_cgst
            total_sgst += item_sgst
        
        # Apply bill-level discount if any
        try:
            bill_discount_value = Decimal(str(self.discount_var.get() or '0'))
            bill_discount_type = self.discount_type_var.get()
            
            if bill_discount_type == "amount":
                # Fixed amount discount
                bill_discount_amount = bill_discount_value
            else:
                # Percentage discount
                bill_discount_amount = subtotal * bill_discount_value / Decimal('100')
            
            # Ensure discount doesn't exceed subtotal
            if bill_discount_amount > subtotal:
                bill_discount_amount = subtotal
                
            # Calculate discount ratio to apply proportionally
            if subtotal > Decimal('0'):
                discount_ratio = Decimal('1') - (bill_discount_amount / subtotal)
            else:
                discount_ratio = Decimal('1')
                
            # Apply bill discount proportionally to all components
            final_subtotal = subtotal * discount_ratio
            final_taxable_value = taxable_value * discount_ratio
            final_tax = total_tax * discount_ratio
            final_cgst = total_cgst * discount_ratio
            final_sgst = total_sgst * discount_ratio
            
        except (ValueError, InvalidOperation):
            # Invalid discount value, treat as zero
            bill_discount_amount = Decimal('0')
            final_subtotal = subtotal
            final_taxable_value = taxable_value
            final_tax = total_tax
            final_cgst = total_cgst
            final_sgst = total_sgst
        
        # Calculate final total
        total = final_subtotal
        
        # Calculate rounded total (to nearest whole number)
        total_rounded = round(total)
        rounding_adjustment = total_rounded - total
        
        # Store values for payment processing and invoice generation
        self.original_total = total
        self.rounded_total = total_rounded
        self.rounding_adjustment = rounding_adjustment
        self.taxable_value = final_taxable_value
        self.cgst_amount = final_cgst
        self.sgst_amount = final_sgst
        self.total_tax = final_tax
        
        # Update labels
        self.subtotal_label.config(text=format_currency(subtotal))
        if bill_discount_amount > Decimal('0'):
            self.discount_amount_label.config(text=f"- {format_currency(bill_discount_amount)}")
        else:
            self.discount_amount_label.config(text="")
            
        # Update tax labels
        self.cgst_label.config(text=format_currency(final_cgst))
        self.sgst_label.config(text=format_currency(final_sgst))
        self.tax_label.config(text=format_currency(final_tax))
        
        # Show both original and rounded totals when there's a difference
        if abs(rounding_adjustment) > Decimal('0.01'):
            self.total_label.config(text=f"{format_currency(total)}\nRounded: {format_currency(total_rounded)}")
        else:
            self.total_label.config(text=format_currency(total))
    
    def edit_cart_item(self, event=None):
        """Edit selected cart item"""
        # Get selected item
        selected_items = self.cart_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        
        # Get the product name from the first column to find the cart item
        selected_values = self.cart_tree.item(selected_item, "values")
        if not selected_values:
            return
            
        product_name = selected_values[0]  # First column is product name
        
        # Find the corresponding cart item by product name
        # If multiple items with same product name, get the first one (should be improved in future)
        cart_item = None
        for item in self.cart_items:
            if item["name"] == product_name:
                cart_item = item
                break
                
        if not cart_item:
            return
            
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Cart Item")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        tk.Label(content_frame, 
               text=cart_item["name"],
               font=FONTS["subheading"]).pack(pady=(0, 10))
        
        tk.Label(content_frame, 
               text=f"Price: {format_currency(cart_item['price'])}",
               font=FONTS["regular"]).pack(pady=(0, 20))
        
        # Quantity
        qty_frame = tk.Frame(content_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qty_frame, 
               text="Quantity:",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        qty_var = tk.StringVar(value=str(cart_item["quantity"]))
        qty_entry = tk.Entry(qty_frame, 
                           textvariable=qty_var,
                           font=FONTS["regular"],
                           width=10)
        qty_entry.grid(row=0, column=1, sticky="w")
        qty_entry.select_range(0, tk.END)  # Select all text
        
        # Item discount
        discount_frame = tk.Frame(content_frame)
        discount_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(discount_frame, 
               text="Discount (%):",
               font=FONTS["regular_bold"],
               width=12,
               anchor="w").grid(row=0, column=0, sticky="w")
        
        discount_var = tk.StringVar(value=str(cart_item["discount"]))
        discount_entry = tk.Entry(discount_frame, 
                                textvariable=discount_var,
                                font=FONTS["regular"],
                                width=10)
        discount_entry.grid(row=0, column=1, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def remove_item():
            # Ask for confirmation
            if messagebox.askyesno("Remove Item", 
                                 f"Are you sure you want to remove {cart_item['name']} from the cart?"):
                # Remove from cart
                self.cart_items = [item for item in self.cart_items if item["id"] != cart_item_id]
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
        
        remove_btn = tk.Button(button_frame,
                             text="Remove Item",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             command=remove_item)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        def update_item():
            try:
                quantity = int(qty_var.get())
                discount = float(discount_var.get())
                
                # Validate quantity
                if quantity <= 0:
                    messagebox.showwarning("Invalid Quantity", 
                                         "Quantity must be greater than zero!")
                    return
                
                # Check stock if this is a database product
                if cart_item["product_id"]:
                    db = self.controller.db
                    available_stock = db.fetchone("""
                        SELECT COALESCE(SUM(b.quantity), 0) as stock
                        FROM products p
                        LEFT JOIN batches b ON p.id = b.product_id AND b.expiry_date > date('now')
                        WHERE p.id = ?
                        GROUP BY p.id
                    """, (cart_item["product_id"],))
                    
                    if available_stock and quantity > available_stock[0]:
                        messagebox.showwarning("Insufficient Stock", 
                                             f"Only {available_stock[0]} units available!")
                        return
                
                # Validate discount
                if discount < 0 or discount > 100:
                    messagebox.showwarning("Invalid Discount", 
                                         "Discount must be between 0 and 100!")
                    return
                
                # Calculate total - use Decimal for consistent math with money values
                discount_factor = Decimal('1') - (Decimal(str(discount)) / Decimal('100'))
                total = Decimal(str(cart_item["price"])) * Decimal(str(quantity)) * discount_factor
                
                # Update cart item
                for item in self.cart_items:
                    if item["id"] == cart_item_id:
                        item["quantity"] = quantity
                        item["discount"] = discount
                        item["total"] = total
                        # Preserve HSN code and tax rate which were already set
                        break
                
                # Update cart display
                self.update_cart()
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning("Invalid Input", 
                                     "Please enter valid numbers for quantity and discount!")
        
        update_btn = tk.Button(button_frame,
                             text="Update",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=20,
                             pady=5,
                             command=update_item)
        update_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to quantity entry
        qty_entry.focus_set()
        
        # Bind Enter key to update_item function
        dialog.bind("<Return>", lambda event: update_item())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def show_cart_context_menu(self, event):
        """Show context menu for cart treeview"""
        # Get clicked item
        item = self.cart_tree.identify_row(event.y)
        if not item:
            return
            
        # Select the item
        self.cart_tree.selection_set(item)
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Edit Item", 
                               command=self.edit_cart_item)
        context_menu.add_command(label="Remove Item", 
                               command=self.remove_selected_item)
        
        # Show context menu
        context_menu.post(event.x_root, event.y_root)
    
    def remove_selected_item(self):
        """Remove selected item from cart"""
        # Get selected item
        selected_items = self.cart_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        
        # Get the product name from the first column to find the cart item
        selected_values = self.cart_tree.item(selected_item, "values")
        if not selected_values:
            return
            
        product_name = selected_values[0]  # First column is product name
        
        # Find the corresponding cart item by product name
        cart_item = None
        for item in self.cart_items:
            if item["name"] == product_name:
                cart_item = item
                break
                
        if not cart_item:
            return
            
        # Ask for confirmation
        if messagebox.askyesno("Remove Item", 
                             f"Are you sure you want to remove {cart_item['name']} from the cart?"):
            # Release reserved inventory for this item
            product_id = cart_item.get("product_id")
            if product_id and product_id in self.reserved_inventory:
                # Get the quantity being removed
                quantity = cart_item["quantity"]
                # Subtract from reserved inventory
                self.reserved_inventory[product_id] -= quantity
                
                # Remove from reserved_inventory if zero
                if self.reserved_inventory[product_id] <= 0:
                    del self.reserved_inventory[product_id]
                    
                print(f"DEBUG: Released {quantity} units of product {product_id} from reservation")
            
            # Remove from cart
            self.cart_items = [item for item in self.cart_items if item["id"] != cart_item_id]
            
            # Update cart display
            self.update_cart()
            
            # Refresh product list to display updated stock
            self.load_products()
    
    def change_customer(self, add_new=False, default_name=""):
        """Change the customer for this sale"""
        # Get current customer
        current_customer_id = self.current_customer["id"]
        
        # If adding new customer
        if add_new:
            # Create dialog
            dialog = tk.Toplevel(self)
            dialog.title("Add New Customer")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()
            
            # Set dialog position
            self._set_dialog_transient(dialog)
            
            # Create frame for content
            content_frame = tk.Frame(dialog, padx=20, pady=20)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            tk.Label(content_frame, 
                   text="Add New Customer",
                   font=FONTS["subheading"]).pack(pady=(0, 20))
            
            # Customer details
            # Name
            name_frame = tk.Frame(content_frame)
            name_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(name_frame, 
                   text="Name:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            name_var = tk.StringVar(value=default_name)
            name_entry = tk.Entry(name_frame, 
                                textvariable=name_var,
                                font=FONTS["regular"],
                                width=30)
            name_entry.grid(row=0, column=1, sticky="w")
            
            # Phone
            phone_frame = tk.Frame(content_frame)
            phone_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(phone_frame, 
                   text="Phone:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            phone_var = tk.StringVar()
            phone_entry = tk.Entry(phone_frame, 
                                 textvariable=phone_var,
                                 font=FONTS["regular"],
                                 width=20)
            phone_entry.grid(row=0, column=1, sticky="w")
            
            # Email
            email_frame = tk.Frame(content_frame)
            email_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(email_frame, 
                   text="Email:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            email_var = tk.StringVar()
            email_entry = tk.Entry(email_frame, 
                                 textvariable=email_var,
                                 font=FONTS["regular"],
                                 width=30)
            email_entry.grid(row=0, column=1, sticky="w")
            
            # Address
            address_frame = tk.Frame(content_frame)
            address_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(address_frame, 
                   text="Address:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            address_var = tk.StringVar()
            address_entry = tk.Entry(address_frame, 
                                   textvariable=address_var,
                                   font=FONTS["regular"],
                                   width=30)
            address_entry.grid(row=0, column=1, sticky="w")
            
            # Village
            village_frame = tk.Frame(content_frame)
            village_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(village_frame, 
                   text="Village:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            village_var = tk.StringVar()
            village_entry = tk.Entry(village_frame, 
                                   textvariable=village_var,
                                   font=FONTS["regular"],
                                   width=20)
            village_entry.grid(row=0, column=1, sticky="w")
            
            # Tax information
            tax_frame = tk.Frame(content_frame)
            tax_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(tax_frame, 
                   text="GSTIN:",
                   font=FONTS["regular_bold"],
                   width=15,
                   anchor="w").grid(row=0, column=0, sticky="w")
            
            gstin_var = tk.StringVar()
            gstin_entry = tk.Entry(tax_frame, 
                                 textvariable=gstin_var,
                                 font=FONTS["regular"],
                                 width=20)
            gstin_entry.grid(row=0, column=1, sticky="w")
            
            # Buttons
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            cancel_btn = tk.Button(button_frame,
                                 text="Cancel",
                                 font=FONTS["regular"],
                                 padx=20,
                                 pady=5,
                                 command=dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            def add_customer():
                # Get values
                name = name_var.get().strip()
                phone = phone_var.get().strip()
                email = email_var.get().strip()
                address = address_var.get().strip()
                village = village_var.get().strip()
                gstin = gstin_var.get().strip()
                
                # Validate
                if not name:
                    messagebox.showwarning("Missing Name", 
                                         "Please enter customer name!")
                    return
                
                # Create customer
                db = self.controller.db
                try:
                    db.begin()
                    
                    # Insert customer
                    customer_id = db.insert("customers", {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "village": village,
                        "gstin": gstin,
                        "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    db.commit()
                    
                    # Update current customer
                    self.current_customer = {
                        "id": customer_id,
                        "name": name,
                        "phone": phone,
                        "address": address,
                        "village": village,
                        "gstin": gstin
                    }
                    
                    # Update customer label
                    self.customer_label.config(text=name)
                    
                    # Close dialog
                    dialog.destroy()
                    
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"Failed to create customer: {str(e)}")
            
            save_btn = tk.Button(button_frame,
                               text="Save Customer",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=add_customer)
            save_btn.pack(side=tk.RIGHT, padx=5)
            
            # Set focus to name entry
            name_entry.focus_set()
            
            # Bind Enter key to move between fields
            name_entry.bind("<Return>", lambda event: phone_entry.focus_set())
            phone_entry.bind("<Return>", lambda event: email_entry.focus_set())
            email_entry.bind("<Return>", lambda event: address_entry.focus_set())
            address_entry.bind("<Return>", lambda event: village_entry.focus_set())
            village_entry.bind("<Return>", lambda event: gstin_entry.focus_set())
            gstin_entry.bind("<Return>", lambda event: add_customer())
            
            # Wait for dialog to close
            dialog.wait_window()
            
        else:
            # Create dialog
            dialog = tk.Toplevel(self)
            dialog.title("Select Customer")
            dialog.geometry("800x500")
            dialog.resizable(True, True)
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()
            
            # Set dialog position
            self._set_dialog_transient(dialog)
            
            # Create frame for content
            content_frame = tk.Frame(dialog, padx=20, pady=20)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = tk.Frame(content_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(header_frame, 
                   text="Select Customer",
                   font=FONTS["subheading"]).pack(side=tk.LEFT)
            
            # Search frame
            search_frame = tk.Frame(content_frame)
            search_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(search_frame, 
                   text="Search:",
                   font=FONTS["regular_bold"]).pack(side=tk.LEFT, padx=(0, 10))
            
            search_var = tk.StringVar()
            search_entry = tk.Entry(search_frame, 
                                  textvariable=search_var,
                                  font=FONTS["regular"],
                                  width=30)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Customer treeview
            tree_frame = tk.Frame(content_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Treeview
            columns = ("id", "name", "phone", "village", "address")
            customer_tree = ttk.Treeview(tree_frame, 
                                       columns=columns,
                                       show="headings",
                                       yscrollcommand=scrollbar.set)
            
            # Configure scrollbar
            scrollbar.config(command=customer_tree.yview)
            
            # Configure columns
            customer_tree.heading("id", text="ID")
            customer_tree.heading("name", text="Name")
            customer_tree.heading("phone", text="Phone")
            customer_tree.heading("village", text="Village")
            customer_tree.heading("address", text="Address")
            
            customer_tree.column("id", width=50)
            customer_tree.column("name", width=200)
            customer_tree.column("phone", width=120)
            customer_tree.column("village", width=120)
            customer_tree.column("address", width=250)
            
            customer_tree.pack(fill=tk.BOTH, expand=True)
            
            # Load customers
            def load_customers(search_term=None):
                # Clear treeview
                for item in customer_tree.get_children():
                    customer_tree.delete(item)
                
                # Get customers from database
                db = self.controller.db
                
                if search_term:
                    customers = db.fetchall("""
                        SELECT id, name, phone, village, address
                        FROM customers
                        WHERE name LIKE ? OR phone LIKE ? OR village LIKE ?
                        ORDER BY name
                    """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
                else:
                    customers = db.fetchall("""
                        SELECT id, name, phone, village, address
                        FROM customers
                        ORDER BY name
                    """)
                
                # Insert walk-in customer
                customer_tree.insert("", "end", values=(1, "Walk-in Customer", "", "", ""))
                
                # Insert customers
                for customer in customers:
                    # Skip walk-in customer if it's in the database
                    if customer[0] == 1:
                        continue
                    customer_tree.insert("", "end", values=customer)
                
                # Select current customer
                if current_customer_id == 1:
                    # Select walk-in customer
                    customer_tree.selection_set(customer_tree.get_children()[0])
                else:
                    # Find current customer
                    for item in customer_tree.get_children():
                        if customer_tree.item(item, "values")[0] == current_customer_id:
                            customer_tree.selection_set(item)
                            customer_tree.see(item)
                            break
            
            # Initial load
            load_customers()
            
            # Bind search
            def on_search(*args):
                search_term = search_var.get().strip()
                load_customers(search_term if search_term else None)
            
            search_var.trace_add("write", on_search)
            
            # Buttons
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            cancel_btn = tk.Button(button_frame,
                                 text="Cancel",
                                 font=FONTS["regular"],
                                 padx=20,
                                 pady=5,
                                 command=dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            def select_customer():
                # Get selected item
                selected_items = customer_tree.selection()
                if not selected_items:
                    messagebox.showinfo("Select Customer", "Please select a customer!")
                    return
                selected_item = selected_items[0]
                
                # Get customer details
                customer_values = customer_tree.item(selected_item, "values")
                customer_id = int(customer_values[0])
                
                # If walk-in customer
                if customer_id == 1:
                    self.current_customer = {
                        "id": 1,
                        "name": "Walk-in Customer",
                        "phone": "",
                        "address": "",
                        "village": "",
                        "gstin": ""
                    }
                else:
                    # Get complete customer details from database
                    db = self.controller.db
                    customer = db.fetchone("""
                        SELECT id, name, phone, address, village, gstin
                        FROM customers
                        WHERE id = ?
                    """, (customer_id,))
                    
                    self.current_customer = {
                        "id": customer[0],
                        "name": customer[1],
                        "phone": customer[2],
                        "address": customer[3],
                        "village": customer[4],
                        "gstin": customer[5]
                    }
                
                # Update customer label
                self.customer_label.config(text=self.current_customer["name"])
                
                # Close dialog
                dialog.destroy()
            
            select_btn = tk.Button(button_frame,
                                 text="Select Customer",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["primary"],
                                 fg=COLORS["text_white"],
                                 padx=20,
                                 pady=5,
                                 command=select_customer)
            select_btn.pack(side=tk.RIGHT, padx=5)
            
            # Add button for new customer
            add_btn = tk.Button(button_frame,
                              text="Add New Customer",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              padx=20,
                              pady=5,
                              command=lambda: [dialog.destroy(), self.change_customer(add_new=True)])
            add_btn.pack(side=tk.RIGHT, padx=5)
            
            # Double-click to select
            customer_tree.bind("<Double-1>", lambda event: select_customer())
            
            # Set focus to search entry
            search_entry.focus_set()
            
            # Bind Enter key in search entry
            search_entry.bind("<Return>", lambda event: customer_tree.focus_set())
            
            # Bind Enter key on treeview
            customer_tree.bind("<Return>", lambda event: select_customer())
            
            # Wait for dialog to close
            dialog.wait_window()
    
    def cancel_sale(self):
        """Cancel the current sale"""
        if not self.cart_items:
            return
            
        # Ask for confirmation
        if messagebox.askyesno("Cancel Sale", 
                             "Are you sure you want to cancel this sale? All items will be removed."):
            # Log inventory being released
            if self.reserved_inventory:
                print(f"DEBUG: Releasing all reserved inventory: {self.reserved_inventory}")
                
            # Clear reserved inventory
            self.reserved_inventory = {}
            
            # Clear cart
            self.cart_items = []
            
            # Reset to walk-in customer
            self.current_customer = {
                "id": 1,
                "name": "Walk-in Customer",
                "phone": "",
                "address": ""
            }
            self.customer_label.config(text="Walk-in Customer")
            
            # Reset discount
            self.discount_var.set("0.00")
            self.discount_type_var.set("amount")
            
            # Update cart display
            self.update_cart()
            
            # Reset item ID counter
            self.next_item_id = 1
            
            # Refresh product list to display updated stock
            self.load_products()
    
    def suspend_sale(self):
        """Suspend the current sale for later retrieval"""
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "No items in cart to suspend!")
            return
            
        # Create dialog for suspension notes
        dialog = tk.Toplevel(self)
        dialog.title("Suspend Sale")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Suspend Current Sale",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Notes
        tk.Label(content_frame, 
               text="Notes (optional):",
               font=FONTS["regular_bold"],
               anchor="w").pack(anchor="w")
        
        notes_var = tk.StringVar()
        notes_entry = tk.Entry(content_frame, 
                             textvariable=notes_var,
                             font=FONTS["regular"],
                             width=40)
        notes_entry.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def suspend():
            # Get suspension notes
            notes = notes_var.get().strip()
            
            # Store bill data as a string (serialized)
            import json
            
            # We need to convert Decimal to float for JSON serialization
            cart_items_serializable = []
            for item in self.cart_items:
                serializable_item = {}
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        serializable_item[key] = float(value)
                    else:
                        serializable_item[key] = value
                cart_items_serializable.append(serializable_item)
            
            bill_data = json.dumps({
                "items": cart_items_serializable,
                "next_item_id": self.next_item_id
            })
            
            # Save to database
            db = self.controller.db
            db.insert("suspended_bills", {
                "customer_id": self.current_customer["id"],
                "bill_data": bill_data,
                "discount": float(self.discount_var.get() or 0),
                "discount_type": self.discount_type_var.get(),
                "notes": notes,
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Reset sale
            self.cancel_sale()
            
            # Close dialog
            dialog.destroy()
            
            # Show confirmation
            messagebox.showinfo("Sale Suspended", 
                              "The sale has been suspended and can be retrieved later.")
        
        suspend_btn = tk.Button(button_frame,
                              text="Suspend Sale",
                              font=FONTS["regular_bold"],
                              bg=COLORS["warning"],
                              fg=COLORS["text_primary"],
                              padx=20,
                              pady=5,
                              command=suspend)
        suspend_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to notes entry
        notes_entry.focus_set()
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: suspend())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def show_suspended_bills(self):
        """Show suspended bills and allow retrieval"""
        # Get suspended bills from database
        db = self.controller.db
        query = """
            SELECT sb.id, c.name as customer_name, c.id as customer_id, 
                   sb.bill_data, sb.discount, sb.discount_type, sb.notes, sb.timestamp
            FROM suspended_bills sb
            JOIN customers c ON sb.customer_id = c.id
            ORDER BY sb.timestamp DESC
        """
        suspended_bills_db = db.fetchall(query)
        
        if not suspended_bills_db:
            messagebox.showinfo("No Suspended Bills", 
                              "There are no suspended bills to retrieve.")
            return
            
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Suspended Bills")
        dialog.geometry("800x500")
        dialog.resizable(True, True)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Suspended Bills",
               font=FONTS["subheading"]).pack(anchor="w", pady=(0, 20))
        
        # Bills treeview
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("id", "customer", "items", "total", "timestamp", "notes")
        bills_tree = ttk.Treeview(tree_frame, 
                                columns=columns,
                                show="headings",
                                yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=bills_tree.yview)
        
        # Configure columns
        bills_tree.heading("id", text="#")
        bills_tree.heading("customer", text="Customer")
        bills_tree.heading("items", text="Items")
        bills_tree.heading("total", text="Total")
        bills_tree.heading("timestamp", text="Suspended At")
        bills_tree.heading("notes", text="Notes")
        
        bills_tree.column("id", width=50)
        bills_tree.column("customer", width=150)
        bills_tree.column("items", width=80)
        bills_tree.column("total", width=100)
        bills_tree.column("timestamp", width=150)
        bills_tree.column("notes", width=200)
        
        bills_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load suspended bills from database
        import json
        
        # Store bill rows for later reference
        self.suspended_bill_rows = {}
        
        for i, bill in enumerate(suspended_bills_db):
            # Extract bill data
            bill_id = bill[0]
            customer_name = bill[1]
            customer_id = bill[2]
            bill_data_json = bill[3]
            discount_value = bill[4]
            discount_type = bill[5]
            notes = bill[6]
            timestamp = bill[7]
            
            # Parse bill data
            try:
                bill_data = json.loads(bill_data_json)
                items = bill_data.get("items", [])
                
                # Calculate total
                total = sum(item.get("total", 0) for item in items)
                
                # Apply bill-level discount
                try:
                    if discount_type == "amount":
                        # Fixed amount discount
                        discount_amount = discount_value
                    else:
                        # Percentage discount
                        discount_amount = total * discount_value / 100
                        
                    # Ensure discount doesn't exceed total
                    discount_amount = min(discount_amount, total)
                    
                    # Calculate final total after discount
                    final_total = total - discount_amount
                    
                except (ValueError, TypeError):
                    # Invalid discount value, treat as zero
                    final_total = total
                
                # Format total
                formatted_total = format_currency(final_total)
                
                # Format timestamp - handle both string and datetime
                if isinstance(timestamp, str):
                    formatted_timestamp = timestamp
                else:
                    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
                
                # Insert into treeview with bill_id as tag
                item_id = bills_tree.insert("", "end", tags=(bill_id,), values=(
                    bill_id,  # Use actual database ID instead of row number
                    customer_name,
                    len(items),
                    formatted_total,
                    formatted_timestamp,
                    notes or ""
                ))
                
                # Store reference to this bill
                self.suspended_bill_rows[item_id] = {
                    "db_id": bill_id,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "bill_data": bill_data,
                    "discount": discount_value,
                    "discount_type": discount_type,
                    "notes": notes
                }
                
            except json.JSONDecodeError:
                # Skip invalid data
                print(f"Error parsing bill data for bill ID {bill_id}")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        close_btn = tk.Button(button_frame,
                            text="Close",
                            font=FONTS["regular"],
                            padx=20,
                            pady=5,
                            command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        def retrieve_bill():
            # Get selected item
            selected_items = bills_tree.selection()
            if not selected_items:
                messagebox.showinfo("Select Bill", "Please select a suspended bill to retrieve!")
                return
            selected_item = selected_items[0]
            
            # Get bill data from our stored references
            if selected_item not in self.suspended_bill_rows:
                messagebox.showerror("Error", "Could not find bill data.")
                return
                
            bill_data = self.suspended_bill_rows[selected_item]
            
            # Check if current cart has items
            if self.cart_items:
                if not messagebox.askyesno("Replace Cart", 
                                         "This will replace the current cart items. Continue?"):
                    return
            
            # Load customer data
            db = self.controller.db
            customer_query = "SELECT * FROM customers WHERE id = ?"
            customer_result = db.fetchone(customer_query, (bill_data["customer_id"],))
            
            if customer_result:
                customer = {
                    "id": customer_result[0],
                    "name": customer_result[1],
                    "phone": customer_result[2],
                    "email": customer_result[3],
                    "address": customer_result[4],
                    "village": customer_result[5],
                    "gstin": customer_result[6],
                    "credit_limit": customer_result[7]
                }
            else:
                # Fallback to Walk-in customer if original customer was deleted
                default_customer = db.fetchone("SELECT * FROM customers WHERE name = 'Walk-in Customer'")
                if not default_customer:
                    # If no Walk-in customer, create a basic customer record
                    customer = {
                        "id": 1,
                        "name": "Walk-in Customer",
                        "phone": "",
                        "email": "",
                        "address": "",
                        "village": "",
                        "gstin": "",
                        "credit_limit": 0
                    }
                else:
                    customer = {
                        "id": default_customer[0],
                        "name": default_customer[1],
                        "phone": default_customer[2],
                        "email": default_customer[3],
                        "address": default_customer[4],
                        "village": default_customer[5],
                        "gstin": default_customer[6],
                        "credit_limit": default_customer[7]
                    }
            
            # Restore customer
            self.current_customer = customer
            self.customer_label.config(text=customer["name"])
            
            # Restore items - convert float prices back to Decimal for consistency
            cart_items = []
            for item in bill_data["bill_data"]["items"]:
                # Create a new dict with Decimal values for amounts
                decimal_item = {}
                for key, value in item.items():
                    if key in ["price", "total", "discount_amount"]:
                        decimal_item[key] = Decimal(str(value))
                    else:
                        decimal_item[key] = value
                cart_items.append(decimal_item)
                
            self.cart_items = cart_items
            
            # Reset item ID counter to ensure unique IDs
            if "next_item_id" in bill_data["bill_data"]:
                self.next_item_id = bill_data["bill_data"]["next_item_id"]
            elif self.cart_items:
                # Fallback: use max ID + 1
                self.next_item_id = max(item.get("id", 0) for item in self.cart_items) + 1
            else:
                self.next_item_id = 1
            
            # Restore discount
            self.discount_var.set(bill_data["discount"])
            self.discount_type_var.set(bill_data["discount_type"])
            
            # Update cart display
            self.update_cart()
            
            # Remove from suspended bills database
            db.delete("suspended_bills", f"id = {bill_data['db_id']}")
            
            # Close dialog
            dialog.destroy()
            
            # Show confirmation
            messagebox.showinfo("Bill Retrieved", 
                              "The suspended bill has been retrieved successfully.")
        
        retrieve_btn = tk.Button(button_frame,
                               text="Retrieve Bill",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=retrieve_bill)
        retrieve_btn.pack(side=tk.RIGHT, padx=5)
        
        def delete_bill():
            # Get selected item
            selected_items = bills_tree.selection()
            if not selected_items:
                messagebox.showinfo("Select Bill", "Please select a suspended bill to delete!")
                return
            selected_item = selected_items[0]
            
            # Get bill data from our stored references
            if selected_item not in self.suspended_bill_rows:
                messagebox.showerror("Error", "Could not find bill data.")
                return
                
            bill_data = self.suspended_bill_rows[selected_item]
            
            # Confirm deletion
            if messagebox.askyesno("Delete Bill", 
                                 "Are you sure you want to delete this suspended bill?"):
                # Remove from suspended bills database
                db = self.controller.db
                db.delete("suspended_bills", f"id = {bill_data['db_id']}")
                
                # Close dialog and re-open (refresh)
                dialog.destroy()
                self.show_suspended_bills()
        
        delete_btn = tk.Button(button_frame,
                             text="Delete Bill",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=20,
                             pady=5,
                             command=delete_bill)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Double-click to retrieve
        bills_tree.bind("<Double-1>", lambda event: retrieve_bill())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def process_payment(self, payment_type):
        """Process payment for the current sale"""
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "No items in cart to process payment!")
            return
            
        # Calculate totals
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Convert to Decimal for consistent types and precision
        subtotal = Decimal(str(subtotal))
        
        # Apply any additional discount
        try:
            discount_value = Decimal(str(self.discount_var.get()))
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                # Fixed amount discount
                discount_amount = discount_value
            else:
                # Percentage discount
                discount_amount = subtotal * discount_value / Decimal('100')
                
            # Ensure discount doesn't exceed subtotal
            discount_amount = min(discount_amount, subtotal)
            
            # Calculate final subtotal after discount
            final_subtotal = subtotal - discount_amount
            
        except (ValueError, InvalidOperation):
            # Invalid discount value, treat as zero
            discount_amount = Decimal('0')
            final_subtotal = subtotal
        
        # Calculate tax based on individual item tax rates
        tax_amount = Decimal('0')
        
        # First calculate proportion of each item after cart-level discount
        if final_subtotal > Decimal('0'):
            discount_ratio = Decimal('1') - (discount_amount / subtotal) if subtotal > Decimal('0') else Decimal('1')
            
            # Calculate tax for each item based on its individual tax rate
            for item in self.cart_items:
                # Get item's tax rate (default to 5% if not specified)
                item_tax_rate = Decimal(str(item.get("tax_percentage", 5))) / Decimal('100')
                
                # Calculate item's post-discount amount
                item_discounted_total = item["total"] * discount_ratio
                
                # Calculate and add tax
                item_tax = item_discounted_total * item_tax_rate
                tax_amount += item_tax
        
        # Calculate total
        total = final_subtotal + tax_amount
        
        # Use rounded total if available (from update_totals method)
        if hasattr(self, 'rounded_total'):
            original_total = total
            total = self.rounded_total
            print(f"Using rounded total for payment: {original_total} -> {total} (adjustment: {total - original_total})")
        
        # Check payment type and process accordingly
        if payment_type == "CASH":
            # Process cash payment
            self._process_cash_payment(total)
        elif payment_type == "UPI":
            # Process UPI payment
            self._process_upi_payment(total)
        elif payment_type == "CREDIT":
            # Process credit payment
            self._process_credit_payment(total)
        elif payment_type == "SPLIT":
            # Process split payment
            self._process_split_payment(total)
    
    def _process_cash_payment(self, total):
        """Process cash payment"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Cash Payment")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Cash Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (9%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (9%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Received amount
        tk.Label(content_frame, 
               text="Amount Received:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        received_var = tk.StringVar(value=str(total))
        received_entry = tk.Entry(content_frame, 
                                textvariable=received_var,
                                font=FONTS["heading"],
                                width=15)
        received_entry.pack(anchor="w", pady=(0, 20))
        received_entry.select_range(0, tk.END)  # Select all text
        
        # Change
        tk.Label(content_frame, 
               text="Change:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        change_label = tk.Label(content_frame, 
                              text="₹0.00",
                              font=FONTS["heading"],
                              fg=COLORS["secondary"])
        change_label.pack(anchor="w", pady=(0, 20))
        
        # Calculate change on input
        def calculate_change(*args):
            try:
                received = Decimal(str(received_var.get()))
                change = received - total
                change_label.config(text=format_currency(change))
            except (ValueError, InvalidOperation):
                change_label.config(text="₹0.00")
        
        received_var.trace_add("write", calculate_change)
        
        # Calculate initial change
        calculate_change()
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            try:
                received = Decimal(str(received_var.get()))
                if received < total:
                    messagebox.showwarning("Insufficient Payment", 
                                         "Amount received is less than total amount!")
                    return
                
                # Proceed with completing the sale
                dialog.destroy()
                # Use a reference object to pass data between methods
                payment_data = {
                    "payment_type": "CASH",
                    "amount": total,
                    "received": received,
                    "change": received - total,
                    "reference": None
                }
                self._complete_sale(payment_data)
                
            except ValueError:
                messagebox.showwarning("Invalid Amount", 
                                     "Please enter a valid amount!")
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["success"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to received amount entry
        received_entry.focus_set()
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _process_upi_payment(self, total):
        """Process UPI payment"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("UPI Payment")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="UPI Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (9%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (9%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Transaction reference
        tk.Label(content_frame, 
               text="UPI Transaction Reference:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        reference_var = tk.StringVar()
        reference_entry = tk.Entry(content_frame, 
                                 textvariable=reference_var,
                                 font=FONTS["regular"],
                                 width=30)
        reference_entry.pack(anchor="w", pady=(0, 5))
        
        # Hint for UPI reference
        hint_label = tk.Label(content_frame, 
                           text="Enter the last 6 digits of the UPI transaction ID",
                           font=FONTS["small"],
                           fg=COLORS["text_secondary"])
        hint_label.pack(anchor="w", pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            reference = reference_var.get().strip()
            if not reference:
                messagebox.showwarning("Missing Reference", 
                                     "Please enter the UPI transaction reference!")
                return
            
            # Validate reference format (simple check for 6 digits)
            if not (reference.isdigit() and 4 <= len(reference) <= 10):
                messagebox.showwarning("Invalid Reference", 
                                     "Please enter a valid UPI reference (4-10 digits)!")
                return
            
            # Proceed with completing the sale
            dialog.destroy()
            # Use a reference object to pass data between methods
            payment_data = {
                "payment_type": "UPI",
                "amount": total,
                "received": total,  # Exact amount for UPI
                "change": Decimal('0'),
                "reference": reference
            }
            self._complete_sale(payment_data)
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["success"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to reference entry
        reference_entry.focus_set()
        
        # Bind Enter key
        dialog.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _process_credit_payment(self, total):
        """Process credit payment"""
        # Check if customer is walk-in
        if self.current_customer["id"] == 1:
            messagebox.showwarning("Cannot Extend Credit", 
                                 "Credit sales require a registered customer. " +
                                 "Please change the customer before proceeding with credit payment.")
            return
            
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Credit Payment")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Credit Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Customer info
        tk.Label(content_frame, 
               text="Customer:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        customer_label = tk.Label(content_frame, 
                                text=self.current_customer["name"],
                                font=FONTS["regular"])
        customer_label.pack(anchor="w", pady=(0, 10))
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (9%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (9%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Get customer's current credit balance
        db = self.controller.db
        credit_balance = db.fetchone("""
            SELECT COALESCE(SUM(
                CASE 
                    WHEN transaction_type = 'CREDIT_SALE' THEN amount 
                    WHEN transaction_type = 'CREDIT_PAYMENT' THEN -amount 
                    ELSE 0 
                END
            ), 0) as balance
            FROM customer_transactions
            WHERE customer_id = ?
        """, (self.current_customer["id"],))
        
        current_balance = credit_balance[0] if credit_balance else 0
        new_balance = current_balance + total
        
        # Show credit balance
        tk.Label(content_frame, 
               text="Current Credit Balance:",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        balance_label = tk.Label(content_frame, 
                               text=format_currency(current_balance),
                               font=FONTS["regular"])
        balance_label.pack(anchor="w", pady=(0, 10))
        
        tk.Label(content_frame, 
               text="New Credit Balance (after this sale):",
               font=FONTS["regular_bold"]).pack(anchor="w")
        
        new_balance_label = tk.Label(content_frame, 
                                   text=format_currency(new_balance),
                                   font=FONTS["regular"],
                                   fg=COLORS["danger"])
        new_balance_label.pack(anchor="w", pady=(0, 15))
        
        # Payment Method - Add options for payment method tracking
        tk.Label(content_frame, 
               text="Payment Method (for record):",
               font=FONTS["regular_bold"]).pack(anchor="w")
               
        payment_method_var = tk.StringVar(value="CREDIT")
        payment_methods = ["CREDIT", "CASH", "UPI", "CHEQUE", "BANK", "OTHER"]
        payment_method_frame = tk.Frame(content_frame)
        payment_method_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Create radio buttons for payment methods
        for i, method in enumerate(payment_methods):
            rb = tk.Radiobutton(
                payment_method_frame,
                text=method,
                variable=payment_method_var,
                value=method,
                font=FONTS["regular"]
            )
            row = i // 3
            col = i % 3
            rb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
        
        # Reference number for certain payment methods
        reference_frame = tk.Frame(content_frame)
        reference_frame.pack(fill=tk.X, pady=(0, 15))
        
        reference_label = tk.Label(reference_frame, 
                                text="Reference Number (for UPI/Cheque/Bank):",
                                font=FONTS["regular"])
        reference_label.pack(anchor="w")
        
        reference_var = tk.StringVar()
        reference_entry = tk.Entry(reference_frame, 
                                textvariable=reference_var,
                                font=FONTS["regular"],
                                width=30)
        reference_entry.pack(anchor="w", pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            # Get payment method and reference
            payment_method = payment_method_var.get()
            reference = None
            
            # Validate reference for UPI/CHEQUE/BANK
            if payment_method in ["UPI", "CHEQUE", "BANK"]:
                reference = reference_var.get().strip()
                if not reference:
                    messagebox.showwarning("Missing Reference", 
                                        "Please enter a reference number for UPI/Cheque/Bank payment records.")
                    return
            
            # Confirm credit sale
            if messagebox.askyesno("Confirm Credit Sale", 
                                f"Extend credit of {format_currency(total)} to {self.current_customer['name']}?"):
                # Proceed with completing the sale
                dialog.destroy()
                # Use a reference object to pass data between methods
                payment_data = {
                    "payment_type": "CREDIT",
                    "credit_payment_method": payment_method,  # Added for tracking
                    "amount": total,
                    "received": Decimal('0'),  # No immediate payment
                    "change": Decimal('0'),
                    "reference": reference
                }
                self._complete_sale(payment_data)
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Credit Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Show/hide reference field based on payment method
        def toggle_reference_field(*args):
            method = payment_method_var.get()
            if method in ["UPI", "CHEQUE", "BANK"]:
                reference_frame.pack(fill=tk.X, pady=(0, 15))
            else:
                reference_frame.pack_forget()
        
        # Bind payment method change
        payment_method_var.trace_add("write", toggle_reference_field)
        # Initial state
        toggle_reference_field()
        
        # Bind Enter key to complete button
        dialog.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _process_split_payment(self, total):
        """Process split payment (cash + UPI + credit)"""
        # Check if customer is walk-in (for credit option)
        allow_credit = self.current_customer["id"] != 1
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Split Payment")
        dialog.geometry("600x700")  # Increased size for credit option
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Set dialog position
        self._set_dialog_transient(dialog)
        
        # Create frame for content with scrolling capabilities
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create content inside scrollable frame
        content_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(content_frame, 
               text="Split Payment",
               font=FONTS["subheading"]).pack(pady=(0, 20))
        
        # Customer info (if not walk-in)
        if allow_credit:
            customer_frame = tk.Frame(content_frame, bg=COLORS["bg_secondary"], padx=10, pady=10)
            customer_frame.pack(fill=tk.X, pady=(0, 20))
            
            tk.Label(customer_frame, 
                   text=f"Customer: {self.current_customer['name']}",
                   font=FONTS["regular_bold"],
                   bg=COLORS["bg_secondary"]).pack(anchor="w")
        
        # Create a frame for tax breakdown
        breakdown_frame = tk.Frame(content_frame)
        breakdown_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subtotal row
        tk.Label(breakdown_frame, 
               text="Subtotal:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        # Calculate subtotal by removing GST from total
        subtotal = sum(item["total"] for item in self.cart_items)
        tk.Label(breakdown_frame, 
               text=format_currency(subtotal),
               font=FONTS["regular"]).grid(row=0, column=1, sticky="e", pady=2)
               
        # CGST row
        tk.Label(breakdown_frame, 
               text="CGST (9%):",
               font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.cgst_amount),
               font=FONTS["regular"]).grid(row=1, column=1, sticky="e", pady=2)
               
        # SGST row
        tk.Label(breakdown_frame, 
               text="SGST (9%):",
               font=FONTS["regular"]).grid(row=2, column=0, sticky="w", pady=2)
               
        tk.Label(breakdown_frame, 
               text=format_currency(self.sgst_amount),
               font=FONTS["regular"]).grid(row=2, column=1, sticky="e", pady=2)
        
        # Total amount row
        tk.Label(breakdown_frame, 
               text="Total Amount:",
               font=FONTS["regular_bold"]).grid(row=3, column=0, sticky="w", pady=5)
        
        total_label = tk.Label(breakdown_frame, 
                             text=format_currency(total),
                             font=FONTS["heading"],
                             fg=COLORS["primary"])
        total_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # Configure columns
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.columnconfigure(1, weight=1)
        
        # Payment method selection section
        method_frame = tk.LabelFrame(content_frame, text="Payment Split", padx=10, pady=10)
        method_frame.pack(fill=tk.X, pady=(10, 20))
        
        # Credit amount (only if customer is not walk-in)
        credit_var = tk.StringVar(value="0.00")
        credit_enabled = tk.BooleanVar(value=False)
        credit_entry = None  # Initialize to None for safety
        
        if allow_credit:
            credit_frame = tk.Frame(method_frame)
            credit_frame.pack(fill=tk.X, pady=5)
            
            # Credit checkbox
            credit_check = tk.Checkbutton(
                credit_frame,
                text="Include Credit",
                font=FONTS["regular"],
                variable=credit_enabled
            )
            credit_check.grid(row=0, column=0, sticky="w")
            
            # Credit amount entry
            tk.Label(credit_frame, 
                   text="Credit Amount:",
                   font=FONTS["regular"]).grid(row=1, column=0, sticky="w", pady=2)
            
            credit_entry = tk.Entry(credit_frame, 
                                 textvariable=credit_var,
                                 font=FONTS["regular"],
                                 width=15,
                                 state=tk.DISABLED)
            credit_entry.grid(row=1, column=1, sticky="w", pady=2)
            
            # Bind the checkbox command after credit_entry is defined
            credit_check.config(
                command=lambda: credit_entry.config(state=tk.NORMAL if credit_enabled.get() else tk.DISABLED)
            )
        
        # Cash amount
        cash_frame = tk.Frame(method_frame)
        cash_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cash_frame, 
               text="Cash Amount:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        cash_var = tk.StringVar(value="0.00")
        cash_entry = tk.Entry(cash_frame, 
                            textvariable=cash_var,
                            font=FONTS["regular"],
                            width=15)
        cash_entry.grid(row=0, column=1, sticky="w", pady=2)
        
        # UPI amount
        upi_frame = tk.Frame(method_frame)
        upi_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(upi_frame, 
               text="UPI Amount:",
               font=FONTS["regular"]).grid(row=0, column=0, sticky="w", pady=2)
        
        upi_var = tk.StringVar(value=str(total))
        upi_entry = tk.Entry(upi_frame, 
                           textvariable=upi_var,
                           font=FONTS["regular"],
                           width=15)
        upi_entry.grid(row=0, column=1, sticky="w", pady=2)
        
        remaining_label = tk.Label(method_frame, 
                                 text=f"Remaining: {format_currency(Decimal('0'))}",
                                 font=FONTS["regular_bold"],
                                 fg=COLORS["success"])
        remaining_label.pack(anchor="e", pady=(10, 0))
        
        # Update remaining amount when any amount changes
        def update_remaining(*args):
            try:
                cash_amount = Decimal(str(cash_var.get() or '0'))
                upi_amount = Decimal(str(upi_var.get() or '0'))
                credit_amount = Decimal(str(credit_var.get() or '0')) if allow_credit and credit_enabled.get() else Decimal('0')
                
                total_entered = cash_amount + upi_amount + credit_amount
                remaining = total - total_entered
                
                if abs(remaining) < Decimal('0.01'):  # Close enough to zero
                    remaining = Decimal('0')
                    remaining_label.config(text=f"Remaining: {format_currency(remaining)}", fg=COLORS["success"])
                elif remaining < Decimal('0'):  # Overpayment
                    remaining_label.config(text=f"Overpayment: {format_currency(abs(remaining))}", fg=COLORS["danger"])
                else:  # Underpayment
                    remaining_label.config(text=f"Remaining: {format_currency(remaining)}", fg=COLORS["warning"])
                    
            except (ValueError, InvalidOperation):
                remaining_label.config(text=f"Remaining: {format_currency(total)}", fg=COLORS["warning"])
        
        # Add trace to all amount variables
        cash_var.trace_add("write", update_remaining)
        upi_var.trace_add("write", update_remaining)
        if allow_credit:
            credit_var.trace_add("write", update_remaining)
            credit_enabled.trace_add("write", update_remaining)
            
        # Update initial state
        update_remaining()
        
        # UPI reference section
        reference_frame = tk.LabelFrame(content_frame, text="UPI Transaction Details", padx=10, pady=10)
        reference_frame.pack(fill=tk.X, pady=(0, 20))
        
        reference_var = tk.StringVar()
        reference_entry = tk.Entry(reference_frame, 
                                 textvariable=reference_var,
                                 font=FONTS["regular"],
                                 width=30)
        reference_entry.pack(anchor="w", pady=5)
        
        # Hint for UPI reference
        hint_label = tk.Label(reference_frame, 
                           text="Enter the last 6 digits of the UPI transaction ID",
                           font=FONTS["small"],
                           fg=COLORS["text_secondary"])
        hint_label.pack(anchor="w")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             padx=20,
                             pady=5,
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        def complete_sale():
            try:
                # Get all payment amounts
                cash_amount = Decimal(str(cash_var.get() or '0'))
                upi_amount = Decimal(str(upi_var.get() or '0'))
                credit_amount = Decimal(str(credit_var.get() or '0')) if allow_credit and credit_enabled.get() else Decimal('0')
                
                # Validate amounts
                if cash_amount < Decimal('0') or upi_amount < Decimal('0') or credit_amount < Decimal('0'):
                    messagebox.showwarning("Invalid Amounts", "Payment amounts cannot be negative!")
                    return
                
                # Calculate total payments
                total_payment = cash_amount + upi_amount + credit_amount
                
                # Validate total
                if abs(total_payment - total) > Decimal('0.01'):  # Allow small rounding error
                    messagebox.showwarning("Payment Mismatch", 
                                         f"Total payment ({format_currency(total_payment)}) does not match sale total ({format_currency(total)})!")
                    return
                
                # Validate credit amount
                if credit_amount > Decimal('0') and self.current_customer["id"] == 1:
                    messagebox.showwarning("Invalid Credit", "Credit cannot be extended to Walk-in customer!")
                    return
                
                # Validate UPI reference if UPI amount is used
                reference = ""
                if upi_amount > Decimal('0.01'):  # More than 0.01 is considered UPI payment
                    reference = reference_var.get().strip()
                    if not reference:
                        messagebox.showwarning("Missing Reference", "Please enter the UPI transaction reference!")
                        return
                    
                    # Validate reference format (simple check for 6 digits)
                    if not (reference.isdigit() and 4 <= len(reference) <= 10):
                        messagebox.showwarning("Invalid Reference", "Please enter a valid UPI reference (4-10 digits)!")
                        return
                
                # Proceed with completing the sale
                dialog.destroy()
                
                # Use a reference object to pass data between methods
                payment_data = {
                    "payment_type": "SPLIT",
                    "amount": total,
                    "cash_amount": cash_amount,
                    "upi_amount": upi_amount,
                    "credit_amount": credit_amount,
                    "received": cash_amount + upi_amount,  # Total received (excluding credit)
                    "change": Decimal('0'),  # No change in split payment
                    "reference": reference
                }
                self._complete_sale(payment_data)
                
            except (ValueError, InvalidOperation):
                messagebox.showwarning("Invalid Amount", "Please enter valid payment amounts!")
        
        complete_btn = tk.Button(button_frame,
                               text="Complete Sale",
                               font=FONTS["regular_bold"],
                               bg=COLORS["success"],
                               fg=COLORS["text_white"],
                               padx=20,
                               pady=5,
                               command=complete_sale)
        complete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set focus to cash entry
        cash_entry.focus_set()
        
        # Bind Enter key to move between fields
        fields = [cash_entry, upi_entry, reference_entry]
        if allow_credit and credit_entry is not None:
            fields.insert(2, credit_entry)  # Insert before reference_entry
            
        for i, field in enumerate(fields):
            if i < len(fields) - 1:
                next_field = fields[i+1]
                field.bind("<Return>", lambda event, nf=next_field: nf.focus_set())
            else:
                field.bind("<Return>", lambda event: complete_sale())
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _complete_sale(self, payment_data):
        """Complete the sale and save to database"""
        # Calculate totals
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # Convert to Decimal for consistent types and precision
        subtotal = Decimal(str(subtotal))
        
        # Apply any additional discount
        try:
            discount_value = Decimal(str(self.discount_var.get()))
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                # Fixed amount discount
                discount_amount = discount_value
            else:
                # Percentage discount
                discount_amount = subtotal * discount_value / Decimal('100')
                
            # Ensure discount doesn't exceed subtotal
            discount_amount = min(discount_amount, subtotal)
            
        except (ValueError, InvalidOperation):
            # Invalid discount value, treat as zero
            discount_amount = Decimal('0')
        
        # Calculate final subtotal after discount
        final_subtotal = subtotal - discount_amount
        
        # Calculate tax based on individual item tax rates
        tax_amount = Decimal('0')
        taxable_value = Decimal('0')
        
        # First calculate proportion of each item after cart-level discount
        if final_subtotal > Decimal('0'):
            discount_ratio = Decimal('1') - (discount_amount / subtotal) if subtotal > Decimal('0') else Decimal('1')
            
            # Calculate tax for each item based on its individual tax rate
            for item in self.cart_items:
                # Get item's tax rate (default to 18% if not specified)
                item_tax_percentage = Decimal(str(item.get("tax_percentage", 18)))
                item_tax_rate = item_tax_percentage / Decimal('100')
                
                # Calculate item's post-discount amount
                item_discounted_total = item["total"] * discount_ratio
                
                # Calculate taxable value (excluding tax)
                item_taxable_value = item_discounted_total / (Decimal('1') + item_tax_rate)
                
                # Calculate tax amount
                item_tax = item_discounted_total - item_taxable_value
                
                # Add to totals
                tax_amount += item_tax
                taxable_value += item_taxable_value
        
        # Store CGST and SGST separately (split evenly)
        cgst_amount = tax_amount / Decimal('2')
        sgst_amount = tax_amount / Decimal('2')
        
        # Round to nearest whole number (requested feature)
        final_subtotal_rounded = round(final_subtotal)
        
        # Calculate the rounding adjustment
        rounding_adjustment = final_subtotal_rounded - final_subtotal
        
        # Store the original and rounded values for display
        print(f"Original total: {final_subtotal}, Rounded total: {final_subtotal_rounded}, Adjustment: {rounding_adjustment}")
        
        # Store sale in database
        db = self.controller.db
        try:
            # Begin transaction
            db.begin()
            
            # Use the selected invoice date if available, otherwise use current time
            sale_date = self.invoice_date_obj if hasattr(self, 'invoice_date_obj') else datetime.datetime.now()
            formatted_sale_date = sale_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Get financial year for invoice number prefix (Indian Financial Year starts in April)
            if sale_date.month >= 4:  # After April 1
                fy_start = sale_date.year
                fy_end = sale_date.year + 1
            else:
                fy_start = sale_date.year - 1
                fy_end = sale_date.year
            
            # Format as YY-YY (e.g., 24-25)
            fy_prefix = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
            
            # Get store name for invoice number prefix
            store_name = "AGT"  # Default prefix
            store_info = db.fetchone("SELECT value FROM settings WHERE key = 'invoice_prefix'")
            if store_info and store_info[0] and store_info[0].strip():
                store_name = store_info[0].strip()
            
            # Get next invoice number
            invoice_prefix = f"{fy_prefix}/{store_name}-"
            
            # Get last invoice number
            last_invoice = db.fetchone("""
                SELECT invoice_number FROM sales
                WHERE invoice_number LIKE ?
                ORDER BY id DESC LIMIT 1
            """, (f"{fy_prefix}/%",))
            
            # Calculate next number
            last_num = 0
            if last_invoice:
                try:
                    last_part = last_invoice[0].split('-')[-1]
                    last_num = int(last_part)
                except (ValueError, IndexError, TypeError) as e:
                    print(f"Error parsing invoice number: {e}")
            
            # Next invoice number
            invoice_num = last_num + 1
            invoice_number = f"{fy_prefix}/{store_name}-{invoice_num:03d}"
            
            # Get current user ID
            user_id = self.controller.current_user.get("id", 1)
            
            # Convert all Decimal values to float for SQLite compatibility
            sale_id = db.insert("sales", {
                "customer_id": self.current_customer["id"],
                "invoice_number": invoice_number,
                "subtotal": float(subtotal),
                "discount": float(discount_amount),
                "tax": float(tax_amount),  # Total GST (18%)
                "cgst": float(cgst_amount),  # 9% CGST
                "sgst": float(sgst_amount),  # 9% SGST
                "total": float(payment_data["amount"]),
                "payment_type": payment_data["payment_type"],
                "payment_reference": payment_data.get("reference"),
                "sale_date": formatted_sale_date,  # Use the formatted sale date
                "user_id": user_id
            })
            
            # Get payment details from payment_data
            cash_amount = float(payment_data.get("cash_amount", 0))
            upi_amount = float(payment_data.get("upi_amount", 0))
            credit_amount = float(payment_data.get("credit_amount", 0))
            upi_reference = payment_data.get("reference", "")
            credit_payment_method = None
            credit_reference = None
            
            # Insert into invoices table with the same date
            invoice_id = db.insert("invoices", {
                "invoice_number": invoice_number,
                "customer_id": self.current_customer["id"],
                "subtotal": float(subtotal),
                "discount_amount": float(discount_amount),
                "tax_amount": float(tax_amount),
                "total_amount": float(payment_data["amount"]),
                "payment_method": payment_data["payment_type"],
                "payment_status": "PAID" if payment_data["payment_type"] != "CREDIT" and 
                                          not (payment_data["payment_type"] == "SPLIT" and credit_amount > 0) 
                                   else "PARTIALLY_PAID" if payment_data["payment_type"] == "SPLIT" and credit_amount > 0 
                                   else "UNPAID",
                "cash_amount": cash_amount,
                "upi_amount": upi_amount,
                "upi_reference": upi_reference,
                "credit_amount": credit_amount,
                "credit_payment_method": credit_payment_method,
                "credit_reference": credit_reference,
                "invoice_date": formatted_sale_date  # Use the same formatted sale date
            })
            
            # Store split payment details if applicable
            if payment_data["payment_type"] == "SPLIT":
                # Check if payment_splits table has credit_amount column
                try:
                    cols = db.fetchall("PRAGMA table_info(payment_splits)")
                    col_names = [col[1] for col in cols]
                    
                    if "credit_amount" not in col_names:
                        db.execute("ALTER TABLE payment_splits ADD COLUMN credit_amount REAL DEFAULT 0")
                except Exception as e:
                    print(f"Warning: Could not check/add columns to payment_splits: {e}")
                
                db.insert("payment_splits", {
                    "sale_id": sale_id,
                    "cash_amount": float(payment_data.get("cash_amount", 0)),
                    "upi_amount": float(payment_data.get("upi_amount", 0)),
                    "credit_amount": float(payment_data.get("credit_amount", 0)),
                    "upi_reference": payment_data.get("reference", "")
                })
                
            # Also insert into invoices table for compatibility with sales_history view
            # Handle different payment types safely
            cash_amount = 0
            upi_amount = 0
            upi_reference = ""
            credit_amount = 0
            credit_payment_method = ""
            credit_reference = ""
            
            # Set appropriate values based on payment type
            if payment_data["payment_type"] == "CASH":
                cash_amount = float(payment_data["received"])
            elif payment_data["payment_type"] == "UPI":
                upi_amount = float(payment_data["received"])
                upi_reference = payment_data.get("reference", "")
            elif payment_data["payment_type"] == "SPLIT":
                cash_amount = float(payment_data.get("cash_amount", 0))
                upi_amount = float(payment_data.get("upi_amount", 0))
                credit_amount = float(payment_data.get("credit_amount", 0))
                upi_reference = payment_data.get("reference", "")
            elif payment_data["payment_type"] == "CREDIT":
                credit_amount = float(payment_data["amount"])
                # Store the payment method selected for this credit sale
                credit_payment_method = payment_data.get("credit_payment_method", "CREDIT")
                credit_reference = payment_data.get("reference", "")
            
            # Add necessary columns to invoices table if not present
            # This ensures backward compatibility
            try:
                # Check if credit_payment_method column exists
                cols = db.fetchall("PRAGMA table_info(invoices)")
                col_names = [col[1] for col in cols]
                
                # Add column for credit payment method if not exists
                if "credit_payment_method" not in col_names:
                    db.execute("ALTER TABLE invoices ADD COLUMN credit_payment_method TEXT")
                
                # Add column for credit reference if not exists
                if "credit_reference" not in col_names:
                    db.execute("ALTER TABLE invoices ADD COLUMN credit_reference TEXT")
            except Exception as e:
                print(f"Warning: Could not check/add columns: {e}")
            
            # Store sale items
            for item in self.cart_items:
                # Use the actual price from cart item (batch-specific price)
                actual_price = item["price"]  # This contains the batch-specific price
                
                # Calculate item tax with proper Decimal handling
                tax_rate = item.get("tax_percentage", 18)  # Default 18% if not specified
                price = Decimal(str(item["price"]))
                quantity = Decimal(str(item["quantity"]))
                discount = Decimal(str(item["discount"]))
                tax_rate_decimal = Decimal(str(tax_rate))
                
                # Calculate discounted price
                discounted_amount = price * quantity * (Decimal('1') - discount / Decimal('100'))
                
                # Calculate tax amount (split between CGST and SGST)
                tax_amount = discounted_amount * (tax_rate_decimal / Decimal('100'))
                
                # Insert sale item - convert any Decimal values to float for SQLite
                # Debug output to verify HSN code and batch info
                hsn_code = item.get("hsn_code", "")
                batch_number = item.get("batch_number", "")
                expiry_date = item.get("expiry_date", "")
                actual_price = float(item["price"])  # This should be the batch-specific price
                print(f"Item: {item['name']}, HSN code: '{hsn_code}', Batch: '{batch_number}', Expiry: '{expiry_date}', Rate: {actual_price}")
                
                sale_item_id = db.insert("sale_items", {
                    "sale_id": sale_id,
                    "product_id": item["product_id"],
                    "product_name": item["name"],
                    "hsn_code": hsn_code,
                    "batch_number": batch_number,
                    "expiry_date": expiry_date,
                    "quantity": float(item["quantity"]),
                    "price": actual_price,  # Use the actual batch-specific price from cart item
                    "discount_percent": float(item["discount"]),
                    "tax_rate": float(tax_rate),  # Use tax_rate column name that exists in schema
                    "tax_amount": float(tax_amount),
                    "total": float(item["total"])
                })
                
                # Add to invoice_items table for compatibility with sales_history view
                # Check if hsn_code column exists in invoice_items before inserting
                try:
                    cols = db.fetchall("PRAGMA table_info(invoice_items)")
                    col_names = [col[1] for col in cols]
                    
                    invoice_item_data = {
                        "invoice_id": invoice_id,
                        "product_id": item["product_id"] or 0,  # Use 0 if product_id is None
                        "batch_number": batch_number,  # Pass the actual batch number
                        "quantity": float(item["quantity"]),
                        "price_per_unit": float(item["price"]),  # Use actual batch-specific price
                        "discount_percentage": float(item["discount"]),
                        "tax_percentage": float(tax_rate),
                        "total_price": float(item["total"])
                    }
                    
                    # Only add hsn_code if the column exists
                    if "hsn_code" in col_names:
                        invoice_item_data["hsn_code"] = hsn_code
                    
                    db.insert("invoice_items", invoice_item_data)
                    
                except Exception as e:
                    print(f"Insert error: {e}")
                    # Try without hsn_code
                    db.insert("invoice_items", {
                        "invoice_id": invoice_id,
                        "product_id": item["product_id"] or 0,
                        "batch_number": batch_number,  # Pass the actual batch number
                        "quantity": float(item["quantity"]),
                        "price_per_unit": float(item["price"]),  # Use actual batch-specific price
                        "discount_percentage": float(item["discount"]),
                        "tax_percentage": float(tax_rate),
                        "total_price": float(item["total"])
                    })
                
                # Update inventory for database products
                if item["product_id"]:
                    batch_id = item.get("batch_id")
                    quantity = item["quantity"]
                    
                    if batch_id:
                        # Specific batch was selected - deduct from that batch only
                        print(f"DEBUG: Deducting {quantity} units from specific batch {batch_id} for product {item['product_id']}")
                        
                        # Get current batch quantity
                        batch_info = db.fetchone("""
                            SELECT quantity FROM batches WHERE id = ?
                        """, (batch_id,))
                        
                        if batch_info and batch_info[0] >= quantity:
                            # Update batch quantity
                            db.execute("""
                                UPDATE batches
                                SET quantity = quantity - ?
                                WHERE id = ?
                            """, (quantity, batch_id))
                            
                            # Record inventory movement
                            try:
                                db.insert("inventory_movements", {
                                    "product_id": item["product_id"],
                                    "batch_id": batch_id,
                                    "quantity": -quantity,
                                    "movement_type": "SALE",
                                    "reference_id": sale_item_id,
                                    "movement_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                            except Exception as e:
                                print(f"Warning: Could not record inventory movement: {e}")
                            
                            print(f"DEBUG: Successfully deducted {quantity} units from batch {batch_id}")
                        else:
                            available = batch_info[0] if batch_info else 0
                            print(f"WARNING: Insufficient stock in batch {batch_id}. Available: {available}, Required: {quantity}")
                    else:
                        # No specific batch - use FEFO logic as fallback
                        print(f"DEBUG: No specific batch selected, using FEFO logic for product {item['product_id']}")
                        
                        # Get batches for this product, starting with oldest expiry
                        try:
                            batches = db.fetchall("""
                                SELECT id, quantity
                                FROM batches
                                WHERE product_id = ? AND quantity > 0 
                                AND (expiry_date > date('now') OR expiry_date IS NULL)
                                ORDER BY CASE WHEN expiry_date IS NULL THEN 1 ELSE 0 END, expiry_date ASC
                            """, (item["product_id"],))
                        except Exception as e:
                            print(f"Error getting batches: {e}")
                            continue
                        
                        # Handle empty batch results
                        if not batches:
                            print(f"Warning: No batches found for product {item['product_id']} - {item['name']}")
                            continue
                        
                        remaining_qty = quantity
                        for batch_row in batches:
                            # Handle potential tuple index errors
                            if len(batch_row) < 2:
                                print(f"Warning: Invalid batch data for product {item['product_id']}: {batch_row}")
                                continue
                                
                            batch_id, batch_qty = batch_row
                            if remaining_qty <= 0:
                                break
                            
                            # How much to take from this batch
                            batch_deduction = min(remaining_qty, batch_qty)
                            
                            # Update batch quantity
                            db.execute("""
                                UPDATE batches
                                SET quantity = quantity - ?
                                WHERE id = ?
                            """, (batch_deduction, batch_id))
                            
                            # Record inventory movement
                            try:
                                db.insert("inventory_movements", {
                                    "product_id": item["product_id"],
                                    "batch_id": batch_id,
                                    "quantity": -batch_deduction,
                                    "movement_type": "SALE",
                                    "reference_id": sale_item_id,
                                    "movement_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                            except Exception as e:
                                print(f"Warning: Could not record inventory movement: {e}")
                            
                            remaining_qty -= batch_deduction
                            
                        if remaining_qty > 0:
                            print(f"WARNING: Could not deduct full quantity. Remaining: {remaining_qty}")
            
            # If credit sale or split with credit, record the transaction
            if payment_data["payment_type"] == "CREDIT" or (payment_data["payment_type"] == "SPLIT" and credit_amount > 0):
                # Get the correct amount for the transaction
                transaction_amount = payment_data["amount"] if payment_data["payment_type"] == "CREDIT" else credit_amount
                
                db.insert("customer_transactions", {
                    "customer_id": self.current_customer["id"],
                    "amount": float(transaction_amount),  # Convert Decimal to float for SQLite
                    "transaction_type": "CREDIT_SALE",
                    "reference_id": sale_id,
                    "transaction_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "notes": f"Credit sale - Invoice #{invoice_number}"
                })
            
            db.commit()
            
            # Show success message
            messagebox.showinfo("Sale Complete", 
                              f"Sale completed successfully!\nInvoice #: {invoice_number}")
            
            # Generate and print invoice
            self._generate_invoice(sale_id, invoice_number)
            
            # Reset cart
            self.cart_items = []
            
            # Reset to walk-in customer
            self.current_customer = {
                "id": 1,
                "name": "Walk-in Customer",
                "phone": "",
                "address": ""
            }
            self.customer_label.config(text="Walk-in Customer")
            
            # Reset discount
            self.discount_var.set("0.00")
            self.discount_type_var.set("amount")
            
            # Log inventory being cleared after successful sale
            if self.reserved_inventory:
                print(f"DEBUG: Clearing reserved inventory after successful sale: {self.reserved_inventory}")
                
            # Clear reserved inventory
            self.reserved_inventory = {}
            
            # Update cart display
            self.update_cart()
            
            # Reload products to reflect updated inventory
            self.load_products()
            
            # Reset item ID counter
            self.next_item_id = 1
            
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
            # Log the error for debugging
            print(f"Sale error: {str(e)}")
    
    def _generate_invoice(self, sale_id, invoice_number):
        """Generate invoice for completed sale"""
        db = self.controller.db
        
        try:
            # Get sale details
            sale = db.fetchone("""
                SELECT s.*, c.name as customer_name, c.phone as customer_phone,
                       c.address as customer_address, c.village as customer_village,
                       c.gstin as customer_gstin
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                WHERE s.id = ?
            """, (sale_id,))
            
            if not sale:
                messagebox.showerror("Error", "Could not find sale details for invoice generation!")
                return
            
            # Get sale items with HSN code
            items = db.fetchall("""
                SELECT si.*, 
                       CASE WHEN si.hsn_code IS NOT NULL AND si.hsn_code != '' 
                            THEN si.hsn_code 
                            ELSE p.hsn_code 
                       END as resolved_hsn_code,
                       p.manufacturer, 
                       p.unit,
                       p.batch_no,
                       p.expiry_date,
                       b.batch_number as batch_from_batch,
                       b.company_name,
                       b.expiry_date as batch_expiry
                FROM sale_items si
                LEFT JOIN products p ON si.product_id = p.id
                LEFT JOIN (
                    SELECT * FROM batches 
                    WHERE quantity > 0
                    ORDER BY expiry_date ASC
                ) b ON si.product_id = b.product_id
                WHERE si.sale_id = ?
                GROUP BY si.id
            """, (sale_id,))
            
            # Get store info
            store_info = {}
            settings = db.fetchall("SELECT key, value FROM settings WHERE key IN ('store_name', 'store_address', 'store_phone', 'store_gstin', 'store_email')")
            for key, value in settings:
                store_info[key] = value
            
            # Format the date properly - use the sale date from the database
            try:
                sale_date = datetime.datetime.strptime(sale[9], '%Y-%m-%d %H:%M:%S')
                formatted_date = sale_date.strftime('%d/%m/%Y')
                formatted_time = sale_date.strftime('%I:%M %p')
            except (ValueError, IndexError) as e:
                print(f"Error parsing sale date: {e}")
                # Fallback to current time if there's a parsing error
                current_datetime = datetime.datetime.now()
                formatted_date = current_datetime.strftime('%d/%m/%Y')
                formatted_time = current_datetime.strftime('%I:%M %p')
            
            invoice_data = {
                "invoice_number": invoice_number,
                "date": formatted_date,
                "time": formatted_time,
                "store_info": {
                    "name": store_info.get("store_name", "Agritech Store"),
                    "address": store_info.get("store_address", "Address Not Set"),
                    "phone": store_info.get("store_phone", "Phone Not Set"),
                    "gstin": store_info.get("store_gstin", "GSTIN Not Set"),
                    "email": store_info.get("store_email", "Email Not Set")
                },
                "customer": {
                    "name": sale[13],  # customer_name
                    "phone": sale[14],  # customer_phone
                    "address": sale[15],  # customer_address
                    "village": sale[16],  # customer_village
                    "gstin": sale[17]   # customer_gstin
                },
                "items": [],
                "payment": {
                    "subtotal": sale[3],  # subtotal
                    "discount": sale[4],  # discount
                    "cgst": sale[11],     # cgst
                    "sgst": sale[12],     # sgst
                    "total": sale[6],     # total
                    "method": str(sale[7]) if sale[7] is not None else "Cash",    # payment_type
                    "reference": sale[8]  # payment_reference
                }
            }
            
            # Get invoice directory
            invoices_dir = os.path.join(".", "invoices")
            os.makedirs(invoices_dir, exist_ok=True)
            
            # Generate PDF filename using invoice number (no timestamp)
            file_name = f"invoice_{invoice_number.replace('/', '-')}.pdf"
            save_path = os.path.join(invoices_dir, file_name)
            
            # Generate the invoice
            from utils.pdf_invoice_generator import generate_invoice
            generate_invoice(invoice_data, save_path)
            
            # Update the invoice record with the file path
            db.execute("""
                UPDATE invoices 
                SET file_path = ? 
                WHERE invoice_number = ?
            """, (save_path, invoice_number))
            
            db.commit()
            
            # Open the generated invoice
            if os.path.exists(save_path):
                os.startfile(save_path)
            else:
                messagebox.showwarning("Warning", "Invoice was generated but could not be opened automatically.")
                
        except Exception as e:
            db.rollback()
            print(f"Error generating invoice: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")
    
    def handle_key_event(self, event):
        """Handle keyboard events for navigation"""
        key = event.keysym
        ctrl = event.state & 0x4  # Control key
        shift = event.state & 0x1  # Shift key
        
        # Get the widget that currently has focus
        focused_widget = self.focus_get()
        
        # Ctrl+D to add new customer (global shortcut)
        if ctrl and key.lower() == "d":
            self.open_add_customer_dialog()
            return "break"
        
        # Tab key to cycle focus
        if key == "Tab":
            if not self.current_focus:
                self.current_focus = "products"
            elif self.current_focus == "products":
                self.current_focus = "cart"
            elif self.current_focus == "cart":
                self.current_focus = "buttons"
            else:
                self.current_focus = "products"
            
            self._update_focus()
            return "break"  # Prevent default tab behavior
        
        # Ctrl+Shift+P to focus products
        elif ctrl and shift and key.lower() == "p":
            self.current_focus = "products"
            self._update_focus()
            return "break"
        
        # Ctrl+Shift+C to focus cart
        elif ctrl and shift and key.lower() == "c":
            self.current_focus = "cart"
            self._update_focus()
            return "break"
        
        # Ctrl+Shift+B to focus buttons
        elif ctrl and shift and key.lower() == "b":
            self.current_focus = "buttons"
            self._update_focus()
            return "break"
        
        # Enter key to select or edit
        elif key == "Return":
            # Check if we're in the products or cart treeview
            if focused_widget == self.products_tree:
                # The Enter key is now directly bound to the treeview via self.products_tree.bind("<Return>", self.add_to_cart)
                # so we don't need to handle it here, but keep as backup
                self.add_to_cart(None)
                return "break"
            elif focused_widget == self.cart_tree:
                self.edit_cart_item()
                return "break"
            elif self.current_focus == "products":
                self.add_to_cart(None)
            elif self.current_focus == "cart":
                self.edit_cart_item()
        
        # Escape key to clear search
        elif key == "Escape":
            if self.current_focus == "products" or focused_widget == self.products_tree:
                self.search_var.set("")
                self.load_products()
    
    def _update_focus(self):
        """Update the focus based on current_focus"""
        if self.current_focus == "products":
            # Focus products treeview
            self.products_tree.focus_set()
            
            # Select first item if none selected
            if not self.products_tree.selection():
                items = self.products_tree.get_children()
                if items:
                    self.products_tree.selection_set(items[0])
                    self.products_tree.focus(items[0])
        
        elif self.current_focus == "cart":
            # Focus cart treeview
            self.cart_tree.focus_set()
            
            # Select first item if none selected
            if not self.cart_tree.selection():
                items = self.cart_tree.get_children()
                if items:
                    self.cart_tree.selection_set(items[0])
                    self.cart_tree.focus(items[0])
        
        elif self.current_focus == "buttons":
            # For now, just focus the search entry
            # In a future enhancement, we could make the payment buttons focusable
            self.search_var.set("")
            search_entry = self.winfo_children()[0].winfo_children()[0].winfo_children()[0]
            search_entry.focus_set()
    
    def on_show(self):
        """Called when frame is shown"""
        # Reset reserved inventory
        if hasattr(self, 'reserved_inventory') and self.reserved_inventory:
            print(f"DEBUG: Resetting reserved inventory on frame show: {self.reserved_inventory}")
            self.reserved_inventory = {}
            
        # Reset the view
        self.load_products()
        
        # Set initial focus to products treeview
        self.current_focus = "products"
        self._update_focus()

    def generate_invoice(self):
        """Generate invoice for current sale using pre-calculated totals"""
        try:
            # Get current date and time
            current_date = datetime.datetime.now()
            formatted_date = current_date.strftime("%d-%m-%Y")
            formatted_time = current_date.strftime("%H:%M")
            
            # Get customer details
            customer_name = self.current_customer.get("name", "Walk-in Customer")
            customer_phone = self.current_customer.get("phone", "")
            customer_email = self.current_customer.get("email", "")
            
            # Prepare items list with pre-calculated values
            items = []
            for item in self.cart_items:
                items.append({
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'discount': float(item.get('discount', 0)),
                    'total': float(item['total']),
                    'taxable_value': float(item['taxable_value']),
                    'tax_amount': float(item['tax_amount']),
                    'cgst_amount': float(item['cgst_amount']),
                    'sgst_amount': float(item['sgst_amount']),
                    'hsn_code': item.get('hsn_code', ''),
                    'unit': item.get('unit', 'pcs')
                })
            
            # Get the selected date for invoice number and financial year
            sale_date = self.invoice_date_obj if hasattr(self, 'invoice_date_obj') else datetime.datetime.now()
            
            # Calculate financial year based on selected date
            if sale_date.month >= 4:  # After April 1
                fy_start = sale_date.year
                fy_end = sale_date.year + 1
            else:
                fy_start = sale_date.year - 1
                fy_end = sale_date.year
            
            # Format as YY-YY (e.g., 24-25)
            fy_prefix = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
            
            # Get store name for invoice number prefix
            store_name = "AGT"  # Default prefix
            store_info = self.controller.db.fetchone("SELECT value FROM settings WHERE key = 'invoice_prefix'")
            if store_info and store_info[0] and store_info[0].strip():
                store_name = store_info[0].strip()
            
            # Get next invoice number
            invoice_prefix = f"{fy_prefix}/{store_name}-"
            
            # Get last invoice number
            last_invoice = self.controller.db.fetchone("""
                SELECT invoice_number FROM sales
                WHERE invoice_number LIKE ?
                ORDER BY id DESC LIMIT 1
            """, (f"{fy_prefix}/%",))
            
            # Calculate next number
            last_num = 0
            if last_invoice:
                try:
                    last_part = last_invoice[0].split('-')[-1]
                    last_num = int(last_part)
                except (ValueError, IndexError, TypeError) as e:
                    print(f"Error parsing invoice number: {e}")
            
            # Next invoice number
            invoice_num = last_num + 1
            invoice_number = f"{fy_prefix}/{store_name}-{invoice_num:03d}"
            
            # Create invoice data dictionary using pre-calculated totals
            invoice_data = {
                'invoice_number': invoice_number,
                'date': formatted_date,
                'time': formatted_time,
                'customer': {
                    'name': customer_name,
                    'phone': customer_phone,
                    'email': customer_email
                },
                'items': items,
                'payment': {
                    'subtotal': float(self.original_total),  # Use pre-calculated total
                    'discount': float(self.discount_amount) if hasattr(self, 'discount_amount') else 0.0,
                    'taxable_value': float(self.taxable_value),  # Use pre-calculated taxable value
                    'cgst': float(self.cgst_amount),  # Use pre-calculated CGST
                    'sgst': float(self.sgst_amount),  # Use pre-calculated SGST
                    'total': float(self.rounded_total),  # Use pre-calculated rounded total
                    'method': 'Cash',  # Default payment method
                    'status': 'PAID'
                }
            }
            
            # Generate PDF with invoice number in filename
            pdf_filename = f"invoice_{invoice_number.replace('/', '-')}.pdf"
            save_path = os.path.join("data", "invoices", pdf_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Generate the invoice using the invoice generator
            from utils.pdf_invoice_generator import generate_invoice
            generate_invoice(invoice_data, save_path)
            
            # Save to sales history with pre-calculated values
            self.save_to_sales_history(
                invoice_number=invoice_number,
                date=formatted_date,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                items=items,
                subtotal=float(self.original_total),
                tax_amount=float(self.total_tax),
                total=float(self.rounded_total)
            )
            
            # Clear cart after successful generation
            self.clear_cart()
            messagebox.showinfo("Success", "Invoice generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")
            print(f"Invoice generation error: {str(e)}")  # Log the error for debugging

    def save_to_sales_history(self, invoice_number, date, customer_name, customer_phone, customer_email, items, subtotal, tax_amount, total):
        """Save sale to history"""
        try:
            # Create sales history directory if it doesn't exist
            os.makedirs('data/sales_history', exist_ok=True)
            
            # Create history entry
            history_entry = {
                'invoice_number': invoice_number,
                'date': date,  # Store the formatted date
                'customer': {
                    'name': customer_name,
                    'phone': customer_phone,
                    'email': customer_email
                },
                'items': items,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'total': total
            }
            
            # Save to JSON file
            history_file = f'data/sales_history/{invoice_number}.json'
            with open(history_file, 'w') as f:
                json.dump(history_entry, f, indent=4)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sales history: {str(e)}")

class DatePickerDialog:
    def __init__(self, parent=None, title="Select Date", firstweekday=6, startdate=None, bootstyle="primary"):
        # Safe locale setup
        try:
            locale.setlocale(locale.LC_TIME, "")
        except locale.Error:
            pass

        self.parent = parent
        self.root = ttk.Toplevel(
            title=title,
            transient=self.parent,
            resizable=(False, False),
            topmost=True,
            minsize=(226, 1)
        )
        self.firstweekday = firstweekday
        self.startdate = startdate or datetime.datetime.now().date()
        self.bootstyle = bootstyle

        self.date_selected = self.startdate
        self.date = startdate or self.date_selected
        self.calendar = calendar.Calendar(firstweekday=firstweekday)

        self.titlevar = ttk.StringVar()
        self.datevar = ttk.IntVar()

        self._setup_calendar()
        self.root.grab_set()
        self.root.wait_window()

    def _setup_calendar(self):
        # Create the widget containers
        self.frm_calendar = ttk.Frame(master=self.root, padding=0, borderwidth=0, relief=FLAT)
        self.frm_calendar.pack(fill=BOTH, expand=YES)
        self.frm_title = ttk.Frame(self.frm_calendar, padding=(3, 3))
        self.frm_title.pack(fill=X)
        self.frm_header = ttk.Frame(self.frm_calendar, bootstyle=SECONDARY)
        self.frm_header.pack(fill=X)

        # Create visual components
        self._draw_titlebar()
        self._draw_calendar()

        # Center the window
        self.root.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.root.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

    def _update_widget_bootstyle(self):
        self.frm_title.configure(bootstyle=self.bootstyle)
        self.title.configure(bootstyle=f"{self.bootstyle}-inverse")
        self.prev_period.configure(style=f"Chevron.{self.bootstyle}.TButton")
        self.next_period.configure(style=f"Chevron.{self.bootstyle}.TButton")

    def _draw_calendar(self):
        self._update_widget_bootstyle()
        self._set_title()
        self._current_month_days()
        self.frm_dates = ttk.Frame(self.frm_calendar)
        self.frm_dates.pack(fill=BOTH, expand=YES)

        for row, weekday_list in enumerate(self.monthdays):
            for col, day in enumerate(weekday_list):
                self.frm_dates.columnconfigure(col, weight=1)
                if day == 0:
                    ttk.Label(
                        master=self.frm_dates,
                        text=self.monthdates[row][col].day,
                        anchor=CENTER,
                        padding=5,
                        bootstyle=SECONDARY
                    ).grid(row=row, column=col, sticky=NSEW)
                else:
                    if all([
                        day == self.date_selected.day,
                        self.date.month == self.date_selected.month,
                        self.date.year == self.date_selected.year
                    ]):
                        day_style = "secondary-toolbutton"
                    else:
                        day_style = f"{self.bootstyle}-calendar"

                    def selected(x=row, y=col):
                        self._on_date_selected(x, y)

                    btn = ttk.Radiobutton(
                        master=self.frm_dates,
                        variable=self.datevar,
                        value=day,
                        text=day,
                        bootstyle=day_style,
                        padding=5,
                        command=selected
                    )
                    btn.grid(row=row, column=col, sticky=NSEW)

    def _draw_titlebar(self):
        self.prev_period = ttk.Button(
            master=self.frm_title,
            text="«",
            command=self.on_prev_month,
            style=f"Chevron.{self.bootstyle}.TButton"
        )
        self.prev_period.pack(side=LEFT)

        self.title = ttk.Label(
            master=self.frm_title,
            textvariable=self.titlevar,
            anchor=CENTER,
            font=FONTS["regular_bold"]
        )
        self.title.pack(side=LEFT, fill=X, expand=YES)

        self.next_period = ttk.Button(
            master=self.frm_title,
            text="»",
            command=self.on_next_month,
            style=f"Chevron.{self.bootstyle}.TButton"
        )
        self.next_period.pack(side=LEFT)

        # Bind year navigation
        self.prev_period.bind("<Button-3>", self.on_prev_year, "+")
        self.next_period.bind("<Button-3>", self.on_next_year, "+")
        self.title.bind("<Button-1>", self.on_reset_date)

        # Create weekday headers
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        header = weekdays[self.firstweekday:] + weekdays[:self.firstweekday]
        for col in header:
            ttk.Label(
                master=self.frm_header,
                text=col,
                anchor=CENTER,
                padding=5,
                bootstyle=(SECONDARY, INVERSE)
            ).pack(side=LEFT, fill=X, expand=YES)

    def _set_title(self):
        _titledate = f'{self.date.strftime("%B %Y")}'
        self.titlevar.set(value=_titledate.capitalize())

    def _current_month_days(self):
        self.monthdays = self.calendar.monthdayscalendar(
            year=self.date.year, month=self.date.month
        )
        self.monthdates = self.calendar.monthdatescalendar(
            year=self.date.year, month=self.date.month
        )

    def _on_date_selected(self, row, col):
        self.date_selected = self.monthdates[row][col]
        self.root.destroy()

    def _selection_callback(func):
        def inner(self, *args):
            func(self, *args)
            self.frm_dates.destroy()
            self._draw_calendar()
        return inner

    @_selection_callback
    def on_next_month(self):
        year, month = self._nextmonth(self.date.year, self.date.month)
        self.date = datetime.datetime(year=year, month=month, day=1).date()

    @_selection_callback
    def on_next_year(self, *_):
        year = self.date.year + 1
        month = self.date.month
        self.date = datetime.datetime(year=year, month=month, day=1).date()

    @_selection_callback
    def on_prev_month(self):
        year, month = self._prevmonth(self.date.year, self.date.month)
        self.date = datetime.datetime(year=year, month=month, day=1).date()

    @_selection_callback
    def on_prev_year(self, *_):
        year = self.date.year - 1
        month = self.date.month
        self.date = datetime.datetime(year=year, month=month, day=1).date()

    @_selection_callback
    def on_reset_date(self, *_):
        self.date = self.startdate

    @staticmethod
    def _nextmonth(year, month):
        if month == 12:
            return year + 1, 1
        else:
            return year, month + 1

    @staticmethod
    def _prevmonth(year, month):
        if month == 1:
            return year - 1, 12
        else:
            return year, month - 1