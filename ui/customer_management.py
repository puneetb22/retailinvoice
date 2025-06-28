"""
Customer Management UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES

class CustomerManagementFrame(tk.Frame):
    """Customer management frame for adding, editing, and viewing customers"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller

        # Keyboard navigation variables
        self.current_focus = None  # Current focus area: 'customers', 'search', 'buttons'
        self.selected_customer_item = -1

        # Bind keyboard events
        self.bind("<Key>", self.handle_key_event)

        # Create layout
        self.create_layout()

        # Load customers
        self.load_customers()

    def create_layout(self):
        """Create the customer management layout"""
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Customer Management",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)

        # Search frame
        search_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10, padx=20)
        search_frame.pack(side=tk.TOP, fill=tk.X)

        search_label = tk.Label(search_frame, 
                               text="Search:",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_customers())

        search_entry = tk.Entry(search_frame, 
                               textvariable=self.search_var,
                               font=FONTS["regular"],
                               width=30)
        search_entry.pack(side=tk.LEFT)

        # Add customer button using theme properties
        add_btn = tk.Button(search_frame,
                          text="Add New Customer",
                          font=FONTS["regular"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          activebackground=COLORS["primary_light"],
                          activeforeground=COLORS["text_white"],
                          padx=15,
                          pady=5,
                          cursor="hand2",
                          command=self.add_customer)
        add_btn.pack(side=tk.RIGHT)

        # Customers treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

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

        # Create treeview
        self.customer_tree = ttk.Treeview(tree_frame, 
                                        columns=("ID", "Name", "Phone", "Address", "Credit", "Created", "Updated"),
                                        show="headings",
                                        yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=self.customer_tree.yview)

        # Define columns
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Customer Name")
        self.customer_tree.heading("Phone", text="Phone Number")
        self.customer_tree.heading("Address", text="Address")
        self.customer_tree.heading("Credit", text="Credit Limit")
        self.customer_tree.heading("Created", text="Created Date")
        self.customer_tree.heading("Updated", text="Updated Date")

        # Set column widths
        self.customer_tree.column("ID", width=50)
        self.customer_tree.column("Name", width=200)
        self.customer_tree.column("Phone", width=120)
        self.customer_tree.column("Address", width=250)
        self.customer_tree.column("Credit", width=100)
        self.customer_tree.column("Created", width=120)
        self.customer_tree.column("Updated", width=120)

        self.customer_tree.pack(fill=tk.BOTH, expand=True)

        # Binding for double-click to edit
        self.customer_tree.bind("<Double-1>", self.edit_customer)

        # Right-click menu for additional options
        self.context_menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_white"], font=FONTS["small"])
        self.context_menu.add_command(label="Edit Customer", command=self.edit_customer)
        self.context_menu.add_command(label="Delete Customer", command=self.delete_customer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Purchase History", command=self.view_history)

        # Bind right-click to show menu
        self.customer_tree.bind("<Button-3>", self.show_context_menu)

        # Action buttons frame
        button_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10, padx=20)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Delete customer button using theme properties
        delete_btn = tk.Button(button_frame,
                             text="Delete Customer",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             activebackground=COLORS["danger"],
                             activeforeground=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_customer)
        delete_btn.pack(side=tk.RIGHT, padx=5)

        # Edit customer button using theme properties
        edit_btn = tk.Button(button_frame,
                           text="Edit Customer",
                           font=FONTS["regular"],
                           bg=COLORS["secondary"],
                           fg=COLORS["text_white"],
                           activebackground=COLORS["secondary_dark"],
                           activeforeground=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=self.edit_customer)
        edit_btn.pack(side=tk.RIGHT, padx=5)

        # View history button using theme properties
        history_btn = tk.Button(button_frame,
                              text="View Purchase History",
                              font=FONTS["regular"],
                              bg=COLORS["primary"],
                              fg=COLORS["text_white"],
                              activebackground=COLORS["primary_light"],
                              activeforeground=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.view_history)
        history_btn.pack(side=tk.RIGHT, padx=5)

    def load_customers(self):
        """Load customers from database into treeview"""
        # Clear current items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        # Get customers from database
        query = """
            SELECT id, name, phone, address, credit_limit, created_at, updated_at
            FROM customers
            ORDER BY name
        """
        customers = self.controller.db.fetchall(query)

        # Insert into treeview
        for customer in customers:
            # Format dates
            created_date = self._format_date(customer[5]) if customer[5] else ""
            updated_date = self._format_date(customer[6]) if customer[6] else ""

            # Format credit limit
            credit_limit = f"₹{customer[4]:.2f}" if customer[4] else "₹0.00"

            self.customer_tree.insert("", "end", values=(
                customer[0],
                customer[1],
                customer[2] if customer[2] else "",
                customer[3] if customer[3] else "",
                credit_limit,
                created_date,
                updated_date
            ))

    def search_customers(self):
        """Search customers based on search term"""
        search_term = self.search_var.get().strip().lower()

        # Clear current items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        if not search_term:
            # If search is empty, load all customers
            self.load_customers()
            return

        # Get filtered customers
        query = """
            SELECT id, name, phone, address, credit_limit, created_at, updated_at
            FROM customers
            WHERE LOWER(name) LIKE ? OR 
                  LOWER(phone) LIKE ? OR
                  LOWER(address) LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        customers = self.controller.db.fetchall(query, (search_pattern, search_pattern, search_pattern))

        # Insert into treeview
        for customer in customers:
            # Format dates
            created_date = self._format_date(customer[5]) if customer[5] else ""
            updated_date = self._format_date(customer[6]) if customer[6] else ""

            # Format credit limit
            credit_limit = f"₹{customer[4]:.2f}" if customer[4] else "₹0.00"

            self.customer_tree.insert("", "end", values=(
                customer[0],
                customer[1],
                customer[2] if customer[2] else "",
                customer[3] if customer[3] else "",
                credit_limit,
                created_date,
                updated_date
            ))

    def add_customer(self):
        """Open dialog to add a new customer"""
        # Create customer dialog
        dialog = tk.Toplevel(self)
        dialog.title("Add New Customer")
        dialog.geometry("600x450")
        dialog.resizable(True, True)  # Allow resizing
        dialog.configure(bg=COLORS["bg_primary"])
        dialog.grab_set()  # Make window modal

        # Bind ESC key to close dialog
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        dialog.focus_set()  # Set focus to enable ESC key

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")

        # Create form
        title = tk.Label(dialog, 
                        text="Add New Customer",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)

        # Form frame
        form_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Create form fields
        fields = [
            {"name": "name", "label": "Customer Name:", "required": True},
            {"name": "phone", "label": "Phone Number:", "required": False},
            {"name": "address", "label": "Address:", "required": False},
            {"name": "credit_limit", "label": "Credit Limit (₹):", "required": False}
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
            label.grid(row=i, column=0, sticky="w", pady=8)

            # Entry
            var = tk.StringVar()
            entry_vars[field["name"]] = var

            # Default credit limit to 0
            if field["name"] == "credit_limit":
                var.set("0")

            entry = tk.Entry(form_frame, 
                            textvariable=var,
                            font=FONTS["regular"],
                            width=40)
            entry.grid(row=i, column=1, sticky="w", pady=8, padx=10)

            # Add asterisk for required fields
            if field["required"]:
                required = tk.Label(form_frame, 
                                  text="*",
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["danger"])
                required.grid(row=i, column=2, sticky="w")

        # Buttons frame
        button_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Cancel button using theme properties
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             activebackground=COLORS["bg_primary"],
                             activeforeground=COLORS["text_primary"],
                             padx=20,
                             pady=5,
                             cursor="hand2",
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)

        # Function to save customer
        def save_customer():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Error", f"{field['label']} is required.")
                    return

            # Validate credit limit is a number
            try:
                credit_limit = float(entry_vars["credit_limit"].get().strip() or 0)
                if credit_limit < 0:
                    messagebox.showerror("Error", "Credit limit cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Credit limit must be a number.")
                return

            # Create customer data
            customer_data = {
                "name": entry_vars["name"].get().strip(),
                "phone": entry_vars["phone"].get().strip(),
                "address": entry_vars["address"].get().strip(),
                "credit_limit": credit_limit,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Insert into database
            customer_id = self.controller.db.insert("customers", customer_data)

            if customer_id:
                messagebox.showinfo("Success", "Customer added successfully!")
                dialog.destroy()
                self.load_customers()  # Refresh customer list
            else:
                messagebox.showerror("Error", "Failed to add customer.")

        # Save button using theme properties
        save_btn = tk.Button(button_frame,
                           text="Save Customer",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           activebackground=COLORS["primary_light"],
                           activeforeground=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=save_customer)
        save_btn.pack(side=tk.RIGHT, padx=5)

    def edit_customer(self, event=None):
        """Open dialog to edit selected customer"""
        # Get selected item
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to edit.")
            return

        # Get customer ID
        customer_id = self.customer_tree.item(selection[0])["values"][0]

        # Get customer data
        query = """
            SELECT * FROM customers WHERE id = ?
        """
        customer = self.controller.db.fetchone(query, (customer_id,))

        if not customer:
            messagebox.showerror("Error", "Customer not found.")
            return

        # Create customer dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Customer")
        dialog.geometry("600x450")
        dialog.resizable(True, True)  # Allow resizing
        dialog.configure(bg=COLORS["bg_primary"])
        dialog.grab_set()  # Make window modal

        # Bind ESC key to close dialog
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        dialog.focus_set()  # Set focus to enable ESC key

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")

        # Create form
        title = tk.Label(dialog, 
                        text="Edit Customer",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=15)

        # Form frame
        form_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Column names for reference
        columns = [description[0] for description in self.controller.db.cursor.description]

        # Create form fields
        fields = [
            {"name": "name", "label": "Customer Name:", "required": True},
            {"name": "phone", "label": "Phone Number:", "required": False},
            {"name": "address", "label": "Address:", "required": False},
            {"name": "credit_limit", "label": "Credit Limit (₹):", "required": False}
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
            label.grid(row=i, column=0, sticky="w", pady=8)

            # Entry
            var = tk.StringVar()
            entry_vars[field["name"]] = var

            # Set value from customer data
            index = columns.index(field["name"])
            if customer[index] is not None:
                var.set(customer[index])

            entry = tk.Entry(form_frame, 
                            textvariable=var,
                            font=FONTS["regular"],
                            width=40)
            entry.grid(row=i, column=1, sticky="w", pady=8, padx=10)

            # Add asterisk for required fields
            if field["required"]:
                required = tk.Label(form_frame, 
                                  text="*",
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["danger"])
                required.grid(row=i, column=2, sticky="w")

        # Buttons frame
        button_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], pady=15)
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
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20)

        # Function to update customer
        def update_customer():
            # Validate required fields
            for field in fields:
                if field["required"] and not entry_vars[field["name"]].get().strip():
                    messagebox.showerror("Error", f"{field['label']} is required.")
                    return

            # Validate credit limit is a number
            try:
                credit_limit = float(entry_vars["credit_limit"].get().strip() or 0)
                if credit_limit < 0:
                    messagebox.showerror("Error", "Credit limit cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Credit limit must be a number.")
                return

            # Create customer data
            customer_data = {
                "name": entry_vars["name"].get().strip(),
                "phone": entry_vars["phone"].get().strip(),
                "address": entry_vars["address"].get().strip(),
                "credit_limit": credit_limit,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Update in database
            updated = self.controller.db.update("customers", customer_data, f"id = {customer_id}")

            if updated:
                messagebox.showinfo("Success", "Customer updated successfully!")
                dialog.destroy()
                self.load_customers()  # Refresh customer list
            else:
                messagebox.showerror("Error", "Failed to update customer.")

        # Save button
        save_btn = tk.Button(button_frame,
                           text="Update Customer",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=20,
                           pady=5,
                           cursor="hand2",
                           command=update_customer)
        save_btn.pack(side=tk.RIGHT, padx=5)

    def delete_customer(self):
        """Delete selected customer"""
        # Get selected item
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to delete.")
            return

        # Get customer ID
        customer_id = self.customer_tree.item(selection[0])["values"][0]
        customer_name = self.customer_tree.item(selection[0])["values"][1]

        # Don't allow deleting Walk-in Customer
        if customer_id == 1:
            messagebox.showwarning("Warning", "Cannot delete the default Walk-in Customer.")
            return

        # Check if customer has invoices
        query = """
            SELECT COUNT(*) FROM invoices WHERE customer_id = ?
        """
        invoice_count = self.controller.db.fetchone(query, (customer_id,))[0]

        if invoice_count > 0:
            messagebox.showwarning("Cannot Delete", 
                                 f"Customer '{customer_name}' has {invoice_count} invoices associated with them.\n\n"
                                 f"Please delete the invoices first or reassign them to another customer.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete customer '{customer_name}'?"):
            return

        # Delete from database
        deleted = self.controller.db.delete("customers", f"id = {customer_id}")

        if deleted:
            messagebox.showinfo("Success", "Customer deleted successfully!")
            self.load_customers()  # Refresh customer list
        else:
            messagebox.showerror("Error", "Failed to delete customer.")

    def view_history(self):
        """View purchase history for selected customer"""
        # Get selected item
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to view purchase history.")
            return

        # Get customer ID
        customer_id = self.customer_tree.item(selection[0])["values"][0]
        customer_name = self.customer_tree.item(selection[0])["values"][1]

        # Create dialog
        history_dialog = tk.Toplevel(self)
        history_dialog.title(f"Purchase History - {customer_name}")
        history_dialog.geometry("800x500")
        history_dialog.configure(bg=COLORS["bg_primary"])
        history_dialog.grab_set()  # Make window modal

        # Bind ESC key to close dialog
        history_dialog.bind("<Escape>", lambda e: history_dialog.destroy())
        history_dialog.focus_set()  # Set focus to enable ESC key

        # Center the dialog
        history_dialog.update_idletasks()
        width = history_dialog.winfo_width()
        height = history_dialog.winfo_height()
        x = (history_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (history_dialog.winfo_screenheight() // 2) - (height // 2)
        history_dialog.geometry(f"+{x}+{y}")

        # Create header
        title = tk.Label(history_dialog, 
                        text=f"Purchase History for {customer_name}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=10)

        # Add stats frame
        stats_frame = tk.Frame(history_dialog, bg=COLORS["bg_primary"], padx=20, pady=10)
        stats_frame.pack(fill=tk.X)

        # Get purchase statistics
        query = """
            SELECT 
                COUNT(*) as total_invoices, 
                SUM(total_amount) as total_spent,
                SUM(CASE WHEN payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID') 
                     THEN credit_amount ELSE 0 END) as total_credit
            FROM invoices
            WHERE customer_id = ?
        """
        stats = self.controller.db.fetchone(query, (customer_id,))

        # Stats labels
        total_invoices = stats[0] if stats[0] else 0
        total_spent = stats[1] if stats[1] else 0
        total_credit = stats[2] if stats[2] else 0

        # Format stats
        tk.Label(stats_frame, 
                text=f"Total Invoices: {total_invoices}",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"]).grid(row=0, column=0, padx=20)

        tk.Label(stats_frame, 
                text=f"Total Amount: ₹{total_spent:.2f}",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"]).grid(row=0, column=1, padx=20)

        # Credit balance with conditional color formatting
        credit_label = tk.Label(stats_frame, 
                text=f"Outstanding Amount: ₹{total_credit:.2f}",
                font=FONTS["regular_bold"],
                bg=COLORS["bg_primary"],
                fg=COLORS["danger"] if total_credit > 0 else COLORS["text_primary"])
        credit_label.grid(row=0, column=2, padx=20)

        # Create notebook for tabs
        notebook = ttk.Notebook(history_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        invoices_tab = tk.Frame(notebook, bg=COLORS["bg_primary"])
        payment_history_tab = tk.Frame(notebook, bg=COLORS["bg_primary"])

        notebook.add(invoices_tab, text="All Invoices")
        notebook.add(payment_history_tab, text="Payment History")

        # Setup invoices tab
        self._setup_invoices_tab(invoices_tab, customer_id)

        # Setup payment history tab
        self._setup_payment_history_tab(payment_history_tab, customer_id)

        # Buttons frame
        button_frame = tk.Frame(history_dialog, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

        # Close button
        close_btn = tk.Button(button_frame,
                            text="Close",
                            font=FONTS["regular"],
                            bg=COLORS["secondary"],
                            fg=COLORS["text_white"],
                            padx=20,
                            pady=5,
                            cursor="hand2",
                            command=history_dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10)

    def _setup_invoices_tab(self, parent, customer_id):
        """Setup the invoices tab in purchase history"""
        # Create frame with scrollbar
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview
        invoices_tree = ttk.Treeview(tree_frame, 
                                   columns=("ID", "Invoice", "Date", "Total", "Status", "Method"),
                                   show="headings",
                                   yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=invoices_tree.yview)

        # Define columns
        invoices_tree.heading("ID", text="ID")
        invoices_tree.heading("Invoice", text="Invoice Number")
        invoices_tree.heading("Date", text="Date")
        invoices_tree.heading("Total", text="Total Amount")
        invoices_tree.heading("Status", text="Payment Status")
        invoices_tree.heading("Method", text="Payment Method")

        # Set column widths
        invoices_tree.column("ID", width=50)
        invoices_tree.column("Invoice", width=150)
        invoices_tree.column("Date", width=150)
        invoices_tree.column("Total", width=100)
        invoices_tree.column("Status", width=100)
        invoices_tree.column("Method", width=100)

        invoices_tree.pack(fill=tk.BOTH, expand=True)

        # Get invoices data
        query = """
            SELECT id, invoice_number, invoice_date, total_amount, payment_status, payment_method
            FROM invoices
            WHERE customer_id = ?
            ORDER BY invoice_date DESC
        """
        invoices = self.controller.db.fetchall(query, (customer_id,))

        # Insert into treeview
        if not invoices:
             # Display a message when no invoices are found
            no_invoices_label = tk.Label(tree_frame,
                                          text="No invoices found for this customer.",
                                          font=FONTS["regular"],
                                          bg=COLORS["bg_primary"],
                                          fg=COLORS["text_secondary"])
            no_invoices_label.pack(pady=20, padx=20)
        else:
            for invoice in invoices:
                # Format date
                invoice_date = self._format_date(invoice[2]) if invoice[2] else ""

                # Format total
                total = f"₹{invoice[3]:.2f}" if invoice[3] else "₹0.00"

                # Set row tags for credit sales
                tags = ("credit",) if invoice[4] == "CREDIT" else ()

                invoices_tree.insert("", "end", values=(
                    invoice[0],
                    invoice[1],
                    invoice_date,
                    total,
                    invoice[4],
                    invoice[5]
                ), tags=tags)

        # Configure tag for credit sales
        invoices_tree.tag_configure("credit", background=COLORS["danger_light"])

    def _setup_credit_tab(self, parent, customer_id):
        """Setup the credit tab in purchase history with improved management capabilities"""
        # Get customer details for credit limit
        query = """
            SELECT credit_limit FROM customers WHERE id = ?
        """
        customer_credit_limit = self.controller.db.fetchone(```python
query, (customer_id,))[0] or 0

        # Get total outstanding credit
        query = """
            SELECT SUM(credit_amount) FROM invoices 
            WHERE customer_id = ? AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID'))
        """
        total_outstanding = self.controller.db.fetchone(query, (customer_id,))[0] or 0

        # Create summary frame at top
        summary_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=15, pady=15)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create three columns for credit stats
        # 1. Credit Limit
        limit_frame = tk.Frame(summary_frame, bg=COLORS["bg_secondary"])
        limit_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        limit_label = tk.Label(limit_frame, 
                            text="Credit Limit",
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_secondary"],
                            fg=COLORS["text_primary"])
        limit_label.pack(anchor="w")

        limit_value = tk.Label(limit_frame, 
                            text=f"₹{customer_credit_limit:.2f}",
                            font=FONTS["heading_small"],
                            bg=COLORS["bg_secondary"],
                            fg=COLORS["primary"])
        limit_value.pack(anchor="w")

        # 2. Outstanding Credit
        outstanding_frame = tk.Frame(summary_frame, bg=COLORS["bg_secondary"])
        outstanding_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        outstanding_label = tk.Label(outstanding_frame, 
                                  text="Outstanding Credit",
                                  font=FONTS["regular_bold"],
                                  bg=COLORS["bg_secondary"],
                                  fg=COLORS["text_primary"])
        outstanding_label.pack(anchor="w")

        outstanding_value = tk.Label(outstanding_frame, 
                                   text=f"₹{total_outstanding:.2f}",
                                   font=FONTS["heading_small"],
                                   bg=COLORS["bg_secondary"],
                                   fg=COLORS["danger"] if total_outstanding > 0 else COLORS["success"])
        outstanding_value.pack(anchor="w")

        # 3. Available Credit
        available_credit = max(0, customer_credit_limit - total_outstanding)
        available_frame = tk.Frame(summary_frame, bg=COLORS["bg_secondary"])
        available_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        available_label = tk.Label(available_frame, 
                                text="Available Credit",
                                font=FONTS["regular_bold"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["text_primary"])
        available_label.pack(anchor="w")

        available_value = tk.Label(available_frame, 
                                text=f"₹{available_credit:.2f}",
                                font=FONTS["heading_small"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["success"])
        available_value.pack(anchor="w")

        # Add a progress bar for credit usage
        progress_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=10)
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Only show progress if there's a credit limit
        if customer_credit_limit > 0:
            usage_percent = min(100, (total_outstanding / customer_credit_limit) * 100)
            progress_text = tk.Label(progress_frame, 
                                  text=f"Credit Usage: {usage_percent:.1f}%",
                                  font=FONTS["regular_small"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["text_primary"])
            progress_text.pack(anchor="w", pady=(0, 5))

            # Progress bar background
            progress_bg = tk.Frame(progress_frame, bg=COLORS["bg_secondary"], height=15, width=300)
            progress_bg.pack(fill=tk.X, pady=(0, 10))

            # Determine color based on usage
            if usage_percent < 50:
                bar_color = COLORS["success"]
            elif usage_percent < 80:
                bar_color = COLORS["warning"]
            else:
                bar_color = COLORS["danger"]

            # Progress bar fill
            bar_width = int((usage_percent / 100) * 300)
            progress_fill = tk.Frame(progress_bg, bg=bar_color, height=15, width=bar_width)
            progress_fill.place(x=0, y=0, width=bar_width, height=15)

        # Create transaction history with tabs
        history_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        history_notebook = ttk.Notebook(history_frame)
        history_notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for different views
        all_credits_tab = tk.Frame(history_notebook, bg=COLORS["bg_primary"])
        active_credits_tab = tk.Frame(history_notebook, bg=COLORS["bg_primary"])
        payment_history_tab = tk.Frame(history_notebook, bg=COLORS["bg_primary"])

        history_notebook.add(active_credits_tab, text="Active Credits")
        history_notebook.add(all_credits_tab, text="All Credit Transactions")
        history_notebook.add(payment_history_tab, text="Payment History")

        # Setup Active Credits tab
        # Create frame with scrollbar
        active_tree_frame = tk.Frame(active_credits_tab)
        active_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        active_scrollbar = ttk.Scrollbar(active_tree_frame)
        active_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create improved treeview with additional info
        credit_tree = ttk.Treeview(active_tree_frame, 
                                 columns=("ID", "Invoice", "Date", "Total", "Amount", "Days", "Status"),
                                 show="headings",
                                 yscrollcommand=active_scrollbar.set)

        # Configure scrollbar
        active_scrollbar.config(command=credit_tree.yview)

        # Define columns
        credit_tree.heading("ID", text="ID")
        credit_tree.heading("Invoice", text="Invoice Number")
        credit_tree.heading("Date", text="Date")
        credit_tree.heading("Total", text="Invoice Total")
        credit_tree.heading("Amount", text="Outstanding")
        credit_tree.heading("Days", text="Days Outstanding")
        credit_tree.heading("Status", text="Status")

        # Set column widths
        credit_tree.column("ID", width=40)
        credit_tree.column("Invoice", width=120)
        credit_tree.column("Date", width=120)
        credit_tree.column("Total", width=100)
        credit_tree.column("Amount", width=100)
        credit_tree.column("Days", width=70)
        credit_tree.column("Status", width=80)

        credit_tree.pack(fill=tk.BOTH, expand=True)

        # Get active credit invoices with outstanding amounts
        query = """
            SELECT id, invoice_number, invoice_date, total_amount, credit_amount, payment_status
            FROM invoices
            WHERE customer_id = ? 
            AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID')) 
            AND credit_amount > 0
            ORDER BY invoice_date DESC
        """
        active_credits = self.controller.db.fetchall(query, (customer_id,))

        # Calculate and configure tags for aging
        today = datetime.date.today()

        # Insert into treeview
        for invoice in active_credits:
            # Format date
            invoice_date = self._format_date(invoice[2]) if invoice[2] else ""

            # Calculate days outstanding
            try:
                invoice_date_obj = datetime.datetime.strptime(invoice[2].split()[0], "%Y-%m-%d").date()
                days_outstanding = (today - invoice_date_obj).days
            except (ValueError, AttributeError):
                days_outstanding = 0

            # Format amounts
            total = f"₹{invoice[3]:.2f}" if invoice[3] else "₹0.00"
            amount = f"₹{invoice[4]:.2f}" if invoice[4] else "₹0.00"

            # Determine row tag based on aging
            if days_outstanding <= 30:
                tag = "current"
            elif days_outstanding <= 60:
                tag = "overdue30"
            elif days_outstanding <= 90:
                tag = "overdue60"
            else:
                tag = "overdue90"

            credit_tree.insert("", "end", values=(
                invoice[0],
                invoice[1],
                invoice_date,
                total,
                amount,
                days_outstanding,
                invoice[5]
            ), tags=(tag,))

        # Configure tags for highlighting aging periods
        credit_tree.tag_configure("current", background="#f0f8ff")
        credit_tree.tag_configure("overdue30", background="#fffacd")
        credit_tree.tag_configure("overdue60", background="#ffa07a")
        credit_tree.tag_configure("overdue90", background="#ffb6c1")

        # Setup All Credits tab - similar to original but with all credit transactions
        self._setup_all_credits_tab(all_credits_tab, customer_id)

        # Setup Payment History tab
        self._setup_payment_history_tab(payment_history_tab, customer_id)

        # Add legend for aging periods
        legend_frame = tk.Frame(parent, bg=COLORS["bg_primary"], padx=15, pady=10)
        legend_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(0, 5))

        tk.Label(legend_frame, text="Legend:", font=FONTS["regular_small"], 
               bg=COLORS["bg_primary"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(0, 10))

        # Create color swatches
        legend_items = [
            {"color": "#f0f8ff", "text": "Current"},
            {"color": "#fffacd", "text": "30+ Days"},
            {"color": "#ffa07a", "text": "60+ Days"},
            {"color": "#ffb6c1", "text": "90+ Days"}
        ]

        for item in legend_items:
            swatch = tk.Frame(legend_frame, bg=item["color"], width=15, height=15)
            swatch.pack(side=tk.LEFT, padx=(10, 5))
            tk.Label(legend_frame, text=item["text"], 
                   font=FONTS["regular_small"], bg=COLORS["bg_primary"], 
                   fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(0, 10))

        # Add payment button frame
        if active_credits:
            # Payment frame
            payment_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=10)
            payment_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

            # Add a payment button
            pay_btn = tk.Button(payment_frame,
                              text="Record Payment",
                              font=FONTS["regular"],
                              bg=COLORS["success"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=8,
                              cursor="hand2",
                              relief=tk.FLAT,
                              command=lambda: self._record_payment(customer_id, credit_tree))
            pay_btn.pack(side=tk.RIGHT, padx=5)

            # Add a set credit limit button
            adjust_limit_btn = tk.Button(payment_frame,
                                      text="Adjust Credit Limit",
                                      font=FONTS["regular"],
                                      bg=COLORS["primary"],
                                      fg=COLORS["text_white"],
                                      padx=15, 
                                      pady=8,
                                      cursor="hand2",
                                      relief=tk.FLAT,
                                      command=lambda: self._adjust_credit_limit(customer_id))
            adjust_limit_btn.pack(side=tk.RIGHT, padx=15)

    def _setup_all_credits_tab(self, parent, customer_id):
        """Setup the all credits tab to show historical credit transactions"""
        # Create frame with scrollbar
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview
        all_credits_tree = ttk.Treeview(tree_frame, 
                                  columns=("ID", "Invoice", "Date", "Total", "Credit", "Status"),
                                  show="headings",
                                  yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=all_credits_tree.yview)

        # Define columns
        all_credits_tree.heading("ID", text="ID")
        all_credits_tree.heading("Invoice", text="Invoice Number")
        all_credits_tree.heading("Date", text="Date")
        all_credits_tree.heading("Total", text="Invoice Total")
        all_credits_tree.heading("Credit", text="Credit Amount")
        all_credits_tree.heading("Status", text="Status")

        # Set column widths
        all_credits_tree.column("ID", width=40)
        all_credits_tree.column("Invoice", width=120)
        all_credits_tree.column("Date", width=120)
        all_credits_tree.column("Total", width=100)
        all_credits_tree.column("Credit", width=100)
        all_credits_tree.column("Status", width=80)

        all_credits_tree.pack(fill=tk.BOTH, expand=True)

        # Get all credit invoices (including paid ones)
        try:
            # First try with payments table (for future implementation)
            query = """
                SELECT id, invoice_number, invoice_date, total_amount, 
                       CASE 
                           WHEN payment_status = 'PAID' THEN 0
                           ELSE credit_amount 
                       END as credit_amount,
                       payment_status
                FROM invoices
                WHERE customer_id = ? AND 
                      (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID') OR 
                       (payment_status = 'PAID' AND (
                           SELECT COUNT(*) FROM payments 
                           WHERE invoice_id = invoices.id AND payment_type = 'credit'
                       ) > 0))
                ORDER BY invoice_date DESC
            """
            credit_invoices = self.controller.db.fetchall(query, (customer_id,))
        except:
            # Fallback query without payments table
            query = """
                SELECT id, invoice_number, invoice_date, total_amount, 
                       CASE 
                           WHEN payment_status = 'PAID' THEN 0
                           ELSE credit_amount 
                       END as credit_amount,
                       payment_status
                FROM invoices
                WHERE customer_id = ? AND 
                      (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID', 'PAID'))
                ORDER BY invoice_date DESC
            """
            credit_invoices = self.controller.db.fetchall(query, (customer_id,))

        # Insert into treeview
        for invoice in credit_invoices:
            # Format date
            invoice_date = self._format_date(invoice[2]) if invoice[2] else ""

            # Format amounts
            total = f"₹{invoice[3]:.2f}" if invoice[3] is not None else "₹0.00"
            credit = f"₹{invoice[4]:.2f}" if invoice[4] is not None else "₹0.00"

            # Determine tag based on payment status
            tag = invoice[5].lower() if invoice[5] else ""

            all_credits_tree.insert("", "end", values=(
                invoice[0],
                invoice[1],
                invoice_date,
                total,
                credit,
                invoice[5]
            ), tags=(tag,))

        # Configure tags for status highlighting
        all_credits_tree.tag_configure("credit", background="#ffb6c1")     # Light red
        all_credits_tree.tag_configure("partial", background="#fffacd")     # Light yellow
        all_credits_tree.tag_configure("partially_paid", background="#fffacd")  # Light yellow (same as partial)
        all_credits_tree.tag_configure("paid", background="#e0f7e0")         # Light green

    def _setup_payment_history_tab(self, parent, customer_id):
        """Setup the payment history tab to show all payments made"""
        # Create frame with scrollbar
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview with updated columns including depositor
        payments_tree = ttk.Treeview(tree_frame, 
                                  columns=("ID", "Date", "Invoice", "Amount", "Method", "Reference", "Depositor", "Notes"),
                                  show="headings",
                                  yscrollcommand=scrollbar.set)

        # Configure scrollbar
        scrollbar.config(command=payments_tree.yview)

        # Define columns with added depositor column
        payments_tree.heading("ID", text="ID")
        payments_tree.heading("Date", text="Payment Date")
        payments_tree.heading("Invoice", text="Invoice Number")
        payments_tree.heading("Amount", text="Amount Paid")
        payments_tree.heading("Method", text="Payment Method")
        payments_tree.heading("Reference", text="Reference")
        payments_tree.heading("Depositor", text="Depositor")
        payments_tree.heading("Notes", text="Notes")

        # Set column widths
        payments_tree.column("ID", width=40)
        payments_tree.column("Date", width=120)
        payments_tree.column("Invoice", width=120)
        payments_tree.column("Amount", width=100)
        payments_tree.column("Method", width=100)
        payments_tree.column("Reference", width=100)
        payments_tree.column("Depositor", width=120)
        payments_tree.column("Notes", width=150)

        payments_tree.pack(fill=tk.BOTH, expand=True)

        # Check if customer_payments table exists and create it if it doesn't
        try:
            table_check = self.controller.db.fetchone(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='customer_payments'"
            )

            if not table_check:
                # Create customer_payments table if it doesn't exist
                self.controller.db.execute("""
                    CREATE TABLE IF NOT EXISTS customer_payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER,
                        invoice_id INTEGER,
                        amount REAL,
                        payment_method TEXT,
                        reference_number TEXT,
                        depositor_name TEXT,
                        payment_date TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers (id),
                        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                    )
                """)
                self.controller.db.commit()

                # Display message for new payment system
                message_frame = tk.Frame(parent, bg=COLORS["bg_primary"], padx=20, pady=20)
                message_frame.pack(fill=tk.BOTH, expand=True)

                message = tk.Label(message_frame, 
                                text="Payment tracking system has been activated. No payment history available yet.",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_secondary"],
                                wraplength=500,
                                justify=tk.CENTER)
                message.pack(pady=50)
                return
        except Exception as e:
            print(f"Error checking/creating customer_payments table: {str(e)}")

        # Get payment history from customer_payments table
        # Initialize payments list as empty to avoid "possibly unbound" warning
        payments = []

        try:
            # Use the proper schema with dedicated depositor_name column
            query = """
                SELECT 
                    cp.id, 
                    cp.payment_date, 
                    inv.invoice_number,
                    cp.amount, 
                    cp.payment_method, 
                    cp.reference_number,
                    cp.notes,
                    cp.created_at,
                    cp.depositor_name
                FROM customer_payments cp
                LEFT JOIN invoices inv ON cp.invoice_id = inv.id
                WHERE cp.customer_id = ?
                ORDER BY cp.payment_date DESC, cp.created_at DESC
            """
            payments = self.controller.db.fetchall(query, (customer_id,))

            # Insert into treeview
            total_paid = 0
            for payment in payments:
                # Format date
                payment_date = self._format_date(payment[1]) if payment[1] else ""

                # Calculate total paid
                payment_amount = payment[3] if payment[3] is not None else 0
                total_paid += payment_amount

                # Format amount
                amount = f"₹{payment_amount:.2f}" if payment_amount > 0 else "₹0.00"

                # Get reference number
                reference = payment[5] or ""

                # Extract depositor info and strip whitespace
                depositor = payment[8].strip() if payment[8] else ""

                # Extract general notes (excluding depositor info if it's there)
                notes = payment[6] or ""
                if "Depositor:" in notes:
                    notes = notes.split("Depositor:")[0].strip()

                # Add to treeview
                payments_tree.insert("", "end", values=(
                    payment[0],
                    payment_date,
                    payment[2] or "Unknown",  # Invoice number
                    amount,
                    payment[4] or "",  # Payment method
                    reference,
                    depositor,
                    notes
                ))

            # Add a summary row at the bottom showing total payments
            if len(payments) > 0:
                # Add a separator
                payments_tree.insert("", "end", values=("", "", "", "", "", "", "", ""), tags=("separator",))

                # Add total row
                payments_tree.insert("", "end", values=(
                    "",
                    "",
                    "TOTAL",
                    f"₹{total_paid:.2f}",
                    "",
                    "",
                    "",
                    f"Total Paid Amount"
                ), tags=("total",))

                # Configure tags for the total row
                payments_tree.tag_configure("separator", background="#f0f0f0")
                payments_tree.tag_configure("total", background="#e6f7ff")

            # Fall back to search in customer_transactions if no payments found
            if not payments or len(payments) == 0:
                print("No payments found in customer_payments table, checking customer_transactions")
                # Try to find payment history in customer_transactions for backward compatibility
                ct_query = """
                    SELECT 
                        ct.id, 
                        ct.transaction_date, 
                        i.invoice_number,
                        ct.amount, 
                        CASE 
                            WHEN ct.notes LIKE '%via CASH%' THEN 'CASH'
                            WHEN ct.notes LIKE '%via UPI%' THEN 'UPI'
                            WHEN ct.notes LIKE '%via CHEQUE%' THEN 'CHEQUE'
                            ELSE ''
                        END as payment_method,
                        '' as reference_number,
                        ct.notes,
                        ct.created_at,
                        CASE
                            WHEN ct.notes LIKE '%by %' 
                            THEN SUBSTR(ct.notes, INSTR(ct.notes, 'by ') + 3)
                            ELSE ''
                        END as depositor
                    FROM customer_transactions ct
                    LEFT JOIN invoices i ON ct.reference_id = i.id
                    WHERE ct.customer_id = ? AND ct.transaction_type = 'CREDIT_PAYMENT'
                    ORDER BY ct.transaction_date DESC, ct.created_at DESC
                """
                trans_payments = self.controller.db.fetchall(ct_query, (customer_id,))

                # Insert into treeview
                trans_total_paid = 0
                for payment in trans_payments:
                    # Format date
                    payment_date = self._format_date(payment[1]) if payment[1] else ""

                    # Calculate total paid
                    payment_amount = payment[3] if payment[3] is not None else 0
                    trans_total_paid += payment_amount

                    # Format amount
                    amount = f"₹{payment_amount:.2f}" if payment_amount > 0 else "₹0.00"

                    # Extract depositor info from notes if present and strip whitespace
                    depositor = payment[8].strip() if payment[8] else ""

                    # Add to treeview
                    payments_tree.insert("", "end", values=(
                        payment[0],
                        payment_date,
                        payment[2] or "Unknown",  # Invoice number
                        amount,
                        payment[4] or "",  # Payment method
                        payment[5] or "",  # Reference
                        depositor,
                        payment[6] or ""   # Notes
                    ))

                # Add a summary row at the bottom showing total payments from transactions
                if len(trans_payments) > 0:
                    # Add a separator if not already added
                    if len(payments) == 0:  # No previous payments
                        payments_tree.insert("", "end", values=("", "", "", "", "", "", "", ""), tags=("separator",))

                    # Add total row
                    payments_tree.insert("", "end", values=(
                        "",
                        "",
                        "TOTAL",
                        f"₹{trans_total_paid:.2f}",
                        "",
                        "",
                        "",
                        f"Total Paid Amount"
                    ), tags=("total",))

                    # Configure tags for the total row if not already configured
                    payments_tree.tag_configure("separator", background="#f0f0f0")
                    payments_tree.tag_configure("total", background="#e6f7ff")

                # Update payments list with transaction records
                payments.extend(trans_payments)

        except Exception as e:
            # If the query fails, show an empty tree
            print(f"Error fetching payment history: {str(e)}")
            import traceback
            traceback.print_exc()

        # Check if there are any payments displayed
        if not payments or len(payments) == 0:
            # Display a message when no payments are found
            message_frame = tk.Frame(parent, bg=COLORS["bg_primary"], padx=20, pady=20)
            message_frame.pack(fill=tk.BOTH, expand=True)

            message = tk.Label(message_frame, 
                             text="No payment records found for this customer.",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_secondary"],
                             wraplength=500,
                             justify=tk.CENTER)
            message.pack(pady=50)

            # Add explanation for developers
            explanation = tk.Label(message_frame,
                                text="Payment records will appear here when payments are collected via Sales History > Collect Payment.",
                                font=FONTS["regular_small"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_secondary"],
                                wraplength=500,
                                justify=tk.CENTER)
            explanation.pack(pady=10)

        # Add informational note
        note_frame = tk.Frame(parent, bg=COLORS["bg_primary"], padx=10, pady=5)
        note_frame.pack(fill=tk.X, side=tk.BOTTOM)

        note_text = ("This tab shows all payment collections for credit sales and split payments. " 
                    "Payments are listed chronologically with the most recent at the top.")
        note_label = tk.Label(note_frame, 
                            text=note_text,
                            font=FONTS["regular_small"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_secondary"],
                            wraplength=500,
                            justify=tk.LEFT)
        note_label.pack(anchor="w")

    def _adjust_credit_limit(self, customer_id):
        """Allow adjusting the credit limit for a customer"""
        # Get current customer info
        query = """
            SELECT name, credit_limit FROM customers WHERE id = ?
        """
        customer = self.controller.db.fetchone(query, (customer_id,))

        if not customer:
            messagebox.showerror("Error", "Customer not found.")
            return

        customer_name = customer[0]
        current_limit = customer[1] or 0

        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Adjust Credit Limit - {customer_name}")
        dialog.geometry("450x250")
        dialog.configure(bg=COLORS["bg_primary"])
        dialog.grab_set()  # Make window modal

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")

        # Title
        title = tk.Label(dialog, 
                       text=f"Adjust Credit Limit for {customer_name}",
                       font=FONTS["heading"],
                       bg=COLORS["bg_primary"],
                       fg=COLORS["text_primary"],
                       wraplength=400)
        title.pack(pady=15)

        # Create form
        form_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Current limit
        current_label = tk.Label(form_frame, 
                               text=f"Current Credit Limit: ₹{current_limit:.2f}",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["primary"])
        current_label.pack(anchor="w", pady=5)

        # New limit
        limit_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        limit_frame.pack(fill=tk.X, pady=10)

        limit_label = tk.Label(limit_frame, 
                             text="New Credit Limit (₹):",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        limit_label.pack(side=tk.LEFT)

        limit_var = tk.StringVar(value=str(current_limit))
        limit_entry = tk.Entry(limit_frame, 
                             textvariable=limit_var,
                             font=FONTS["regular"],
                             width=15)
        limit_entry.pack(side=tk.LEFT, padx=10)

        # Notes
        notes_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        notes_frame.pack(fill=tk.X, pady=5)

        notes_label = tk.Label(notes_frame, 
                             text="Reason for Change:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        notes_label.pack(anchor="w")

        notes_var = tk.StringVar()
        notes_entry = tk.Entry(notes_frame, 
                             textvariable=notes_var,
                             font=FONTS["regular"],
                             width=40)
        notes_entry.pack(fill=tk.X, pady=5)

        # Buttons
        button_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20)

        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Save function
        def save_limit():
            try:
                # Validate new limit
                new_limit = float(limit_var.get())
                if new_limit < 0:
                    messagebox.showerror("Error", "Credit limit cannot be negative.")
                    return

                # Get total outstanding credit
                query = """
                    SELECT SUM(credit_amount) FROM invoices 
                    WHERE customer_id = ? AND (payment_status IN ('CREDIT', 'PARTIALLY_PAID', 'PARTIAL', 'UNPAID'))
                """
                total_outstanding = self.controller.db.fetchone(query, (customer_id,))[0] or 0

                # If reducing credit limit below outstanding amount, warn user
                if new_limit < total_outstanding:
                    confirm = messagebox.askyesno(
                        "Warning", 
                        f"The new credit limit (₹{new_limit:.2f}) is less than the current outstanding credit " 
                        f"(₹{total_outstanding:.2f}).\n\nThis may prevent further credit sales until " 
                        f"the outstanding amount is reduced.\n\nDo you want to continue?"
                    )
                    if not confirm:
                        return

                # Update customer data
                customer_data = {
                    "credit_limit": new_limit,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Log the change in notes if provided
                notes = notes_var.get().strip()
                if notes:
                    # In a real implementation, this would go to a change log table
                    print(f"Credit limit change for customer {customer_id}: " 
                          f"₹{current_limit:.2f} -> ₹{new_limit:.2f}. Reason: {notes}")

                # Update in database
                updated = self.controller.db.update("customers", customer_data, f"id = {customer_id}")

                if updated:
                    messagebox.showinfo("Success", 
                                      f"Credit limit updated from ₹{current_limit:.2f} to ₹{new_limit:.2f}.")
                    dialog.destroy()

                    # Refresh the view
                    self.view_history()
                else:
                    messagebox.showerror("Error", "Failed to update credit limit.")

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid credit limit.")

        # Save button
        save_btn = tk.Button(button_frame,
                           text="Update Credit Limit",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=save_limit)
        save_btn.pack(side=tk.RIGHT, padx=5)

    def _record_payment(self, customer_id, credit_tree):
        """Record payment for credit sale"""
        # Get selected invoice
        selection = credit_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select an invoice to record payment.")
            return

        # Get invoice details
        invoice_id = credit_tree.item(selection[0])["values"][0]
        invoice_number = credit_tree.item(selection[0])["values"][1]
        amount = credit_tree.item(selection[0])["values"][4]  # Updated to match new column structure

        # Parse amount
        credit_amount = float(amount.replace("₹", ""))

        # Create payment dialog
        payment_dialog = tk.Toplevel(self)
        payment_dialog.title("Record Payment")
        payment_dialog.geometry("450x350")
        payment_dialog.resizable(True, True)  # Allow resizing
        payment_dialog.configure(bg=COLORS["bg_primary"])
        payment_dialog.grab_set()

        # Center the dialog
        payment_dialog.update_idletasks()
        width = payment_dialog.winfo_width()
        height = payment_dialog.winfo_height()
        x = (payment_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (payment_dialog.winfo_screenheight() // 2) - (height // 2)
        payment_dialog.geometry(f"+{x}+{y}")

        # Create form
        title = tk.Label(payment_dialog, 
                        text=f"Record Payment for Invoice #{invoice_number}",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"],
                        wraplength=420)
        title.pack(pady=10)

        # Form frame
        form_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Amount due with highlighted box
        due_frame = tk.Frame(form_frame, bg=COLORS["danger_light"], padx=10, pady=10, 
                           bd=1, relief=tk.SOLID)
        due_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        due_label = tk.Label(due_frame, 
                           text=f"Amount Due:",
                           font=FONTS["regular_bold"],
                           bg=COLORS["danger_light"],
                           fg=COLORS["text_primary"])
        due_label.pack(side=tk.LEFT)

        due_amount = tk.Label(due_frame, 
                            text=f"{amount}",
                            font=FONTS["heading_small"],
                            bg=COLORS["danger_light"],
                            fg=COLORS["danger"])
        due_amount.pack(side=tk.RIGHT, padx=10)

        # Payment date
        date_label = tk.Label(form_frame, 
                            text="Payment Date:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        date_label.grid(row=1, column=0, sticky="w", pady=8)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        date_var = tk.StringVar(value=today)
        date_entry = tk.Entry(form_frame, 
                            textvariable=date_var,
                            font=FONTS["regular"],
                            width=15)
        date_entry.grid(row=1, column=1, sticky="w", pady=8, padx=5)

        # Payment method
        method_label = tk.Label(form_frame, 
                              text="Payment Method:",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        method_label.grid(row=2, column=0, sticky="w", pady=8)

        method_var = tk.StringVar(value="Cash")
        methods = ["Cash", "UPI", "Bank Transfer", "Check"]

        method_combo = ttk.Combobox(form_frame, 
                                  textvariable=method_var, 
                                  values=methods,
                                  font=FONTS["regular"],
                                  width=15,
                                  state="readonly")
        method_combo.grid(row=2, column=1, sticky="w", pady=8, padx=5)

        # Reference number (for UPI/bank/check)
        ref_label = tk.Label(form_frame, 
                           text="Reference Number:",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        ref_label.grid(row=3, column=0, sticky="w", pady=8)

        ref_var = tk.StringVar()
        ref_entry = tk.Entry(form_frame, 
                           textvariable=ref_var,
                           font=FONTS["regular"],
                           width=20)
        ref_entry.grid(row=3, column=1, sticky="w", pady=8, padx=5)

        # Payment amount
        amount_label = tk.Label(form_frame, 
                              text="Payment Amount:",
                              font=FONTS["regular_bold"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        amount_label.grid(row=4, column=0, sticky="w", pady=8)

        amount_var = tk.StringVar(value=str(credit_amount))
        amount_entry = tk.Entry(form_frame, 
                              textvariable=amount_var,
                              font=FONTS["regular_bold"],
                              width=15)
        amount_entry.grid(row=4, column=1, sticky="w", pady=8, padx=5)

        # Depositor Name (new field)
        depositor_label = tk.Label(form_frame, 
                                 text="Depositor Name:",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        depositor_label.grid(row=5, column=0, sticky="w", pady=8)

        depositor_var = tk.StringVar()
        depositor_entry = tk.Entry(form_frame, 
                                 textvariable=depositor_var,
                                 font=FONTS["regular"],
                                 width=20)
        depositor_entry.grid(row=5, column=1, sticky="w", pady=8, padx=5)

        # Notes
        notes_label = tk.Label(form_frame, 
                             text="Notes:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        notes_label.grid(row=6, column=0, sticky="w", pady=8)

        notes_var = tk.StringVar()
        notes_entry = tk.Entry(form_frame, 
                             textvariable=notes_var,
                             font=FONTS["regular"],
                             width=30)
        notes_entry.grid(row=6, column=1, sticky="w", pady=8, padx=5)

        # Buttons frame
        button_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=FONTS["regular"],
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             relief=tk.FLAT,
                             command=payment_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Function to save payment
        def save_payment():
            try:
                # Validate payment amount
                payment_amount = float(amount_var.get())
                if payment_amount <= 0:
                    messagebox.showerror("Error", "Payment amount must be greater than zero.")
                    return

                if payment_amount > credit_amount:
                    messagebox.showerror("Error", "Payment amount cannot exceed the amount due.")
                    return

                # Update invoice status
                if payment_amount == credit_amount:
                    # Fully paid
                    payment_status = "PAID"
                    new_credit_amount = 0
                else:
                    # Partially paid - use PARTIALLY_PAID for consistency with sales_history.py
                    payment_status = "PARTIALLY_PAID"
                    new_credit_amount = credit_amount - payment_amount

                # Get payment method
                payment_method = method_var.get()

                # Update cash/upi amount based on payment method
                cash_amount = payment_amount if payment_method == "Cash" else 0
                upi_amount = payment_amount if payment_method == "UPI" else 0
                bank_amount = payment_amount if payment_method == "Bank Transfer" else 0

                # Create notes with reference number and depositor name if provided
                notes = notes_var.get().strip()
                ref_number = ref_var.get().strip()
                depositor_name = depositor_var.get().strip()

                # Add reference number to notes if provided
                if ref_number:
                    if notes:
                        notes += f" | Ref: {ref_number}"
                    else:
                        notes = f"Ref: {ref_number}"

                # Add depositor name to notes if provided
                if depositor_name:
                    if notes:
                        notes += f" | Depositor: {depositor_name}"
                    else:
                        notes = f"Depositor: {depositor_name}"

                # Update invoice data
                invoice_data = {
                    "payment_status": payment_status,
                    "credit_amount": new_credit_amount,
                    "cash_amount": cash_amount if payment_method == "Cash" else None,
                    "upi_amount": upi_amount if payment_method == "UPI" else None,
                    "bank_amount": bank_amount if payment_method == "Bank Transfer" else None,
                    "payment_method": payment_method,
                    "payment_reference": ref_number if ref_number else None,
                    "payment_date": date_var.get().strip(),
                    "notes": notes,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Start a transaction
                self.controller.db.begin()
                try:
                    # Update invoice table
                    updated = self.controller.db.update("invoices", invoice_data, f"id = {invoice_id}")

                    # Check if customer_payments table exists
                    table_check = self.controller.db.fetchone(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='customer_payments'"
                    )

                    if not table_check:
                        # Create customer_payments table if it doesn't exist
                        self.controller.db.execute("""
                            CREATE TABLE IF NOT EXISTS customer_payments (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                customer_id INTEGER,
                                invoice_id INTEGER,
                                amount REAL,
                                payment_method TEXT,
                                reference_number TEXT,
                                payment_date TEXT,
                                notes TEXT,
                                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (customer_id) REFERENCES customers (id),
                                FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                            )
                        """)

                    # Record payment in customer_payments table
                    payment_data = {
                        "customer_id": customer_id,
                        "invoice_id": invoice_id,
                        "amount": payment_amount,
                        "payment_method": payment_method,
                        "reference_number": ref_number,
                        "payment_date": date_var.get().strip(),
                        "notes": notes,
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    payment_id = self.controller.db.insert("customer_payments", payment_data)

                    # Commit transaction
                    self.controller.db.commit()

                    if updated and payment_id:
                        messagebox.showinfo("Success", f"Payment of ₹{payment_amount:.2f} recorded successfully!")
                        payment_dialog.destroy()

                        # Refresh the view
                        self.view_history()
                    else:
                        messagebox.showerror("Error", "Failed to record payment.")

                except Exception as e:
                    # Rollback on error
                    self.controller.db.rollback()
                    print(f"Error saving payment: {str(e)}")
                    messagebox.showerror("Error", f"Failed to record payment: {str(e)}")

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid payment amount.")

        # Save button
        save_btn = tk.Button(button_frame,
                           text="Record Payment",
                           font=FONTS["regular"],
                           bg=COLORS["success"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           relief=tk.FLAT,
                           command=save_payment)
        save_btn.pack(side=tk.RIGHT, padx=10)

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.customer_tree.identify_row(event.y)
        if iid:
            # Select the item
            self.customer_tree.selection_set(iid)
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)

    def _format_date(self, date_str):
        """Format date string for display"""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return date_obj.strftime("%d %b %Y, %I:%M %p")
        except (ValueError, TypeError):
            try:
                # Try parsing just the date part
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj.strftime("%d %b %Y")
            except (ValueError, TypeError):
                return date_str

    def handle_key_event(self, event):
        """Handle keyboard events for customer management navigation"""
        # Focus management
        if event.keysym == "Tab":
            # Switch between customer list and search
            if self.current_focus is None or self.current_focus == "customers":
                self.current_focus = "search"
                self.search_var.set("")
                for widget in self.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Entry):
                                child.focus_set()
                                return "break"
            else:
                self.current_focus = "customers"
                self.selected_customer_item = 0 if self.customer_tree.get_children() else -1
                if self.selected_customer_item >= 0:
                    self.customer_tree.selection_set(self.customer_tree.get_children()[self.selected_customer_item])
                    self.customer_tree.focus_set()
                return "break"

        # Navigation within customer list
        if self.current_focus == "customers":
            customer_items = self.customer_tree.get_children()
            if not customer_items:
                return

            if event.keysym == "Down":
                # Move to next customer
                self.selected_customer_item = min(self.selected_customer_item + 1, len(customer_items) - 1)
                self.customer_tree.selection_set(customer_items[self.selected_customer_item])
                self.customer_tree.see(customer_items[self.selected_customer_item])
            elif event.keysym == "Up":
                # Move to previous customer
                self.selected_customer_item = max(self.selected_customer_item - 1, 0)
                self.customer_tree.selection_set(customer_items[self.selected_customer_item])
                self.customer_tree.see(customer_items[self.selected_customer_item])
            elif event.keysym == "Return" or event.keysym == "space":
                # Edit selected customer
                self.edit_customer()
            elif event.keysym == "Delete":
                # Delete selected customer
                self.delete_customer()

        # Global keyboard shortcuts
        if event.keysym == "n" and event.state & 0x4:  # Ctrl+N
            # Add new customer
            self.add_customer()
        elif event.keysym == "e" and event.state & 0x4:  # Ctrl+E
            # Edit selected customer
            selected = self.customer_tree.selection()
            if selected:
                self.edit_customer()
        elif event.keysym == "d" and event.state & 0x4:  # Ctrl+D
            # Delete selected customer
            selected = self.customer_tree.selection()
            if selected:
                self.delete_customer()
        elif event.keysym == "h" and event.state & 0x4:  # Ctrl+H
            # View purchase history
            selected = self.customer_tree.selection()
            if selected:
                self.view_history()
        elif event.keysym == "f" and event.state & 0x4:  # Ctrl+F
            # Focus on search
            self.current_focus = "search"
            self.search_var.set("")
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Entry):
                            child.focus_set()
                            return "break"

    def on_show(self):
        """Called when frame is shown"""
        # Refresh customer list
        self.load_customers()

        # Set initial focus
        self.current_focus = "customers"
        self.focus_set()

        # Select first customer if available
        if self.customer_tree.get_children():
            self.selected_customer_item = 0
            self.customer_tree.selection_set(self.customer_tree.get_children()[0])
            self.customer_tree.focus_set()