"""
Sales History UI for POS system
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import subprocess
import calendar
import locale
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Import global styles and formatting utils
from assets.styles import COLORS, FONTS
from utils.helpers import format_currency, parse_date, format_date

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

class SalesHistoryFrame(tk.Frame):
    """Sales history frame for viewing and reprinting invoices"""
    
    def __init__(self, parent, controller):
        """Initialize the sales history frame"""
        super().__init__(parent, bg=COLORS["bg_primary"])
        self.current_invoice_id = None
        self.controller = controller
        self.selected_date = datetime.date.today()
        
        # Initialize date variables
        self.date_var = tk.StringVar(value=self.selected_date.strftime("%d/%m/%Y"))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create widgets for sales history display"""
        # Main container with minimal padding to maximize screen usage 
        main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header frame at top
        header_frame = tk.Frame(main_container, bg=COLORS["bg_primary"], padx=10, pady=5)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Title on left of header
        title_label = tk.Label(
            header_frame,
            text="Daily Sales History",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Date filter controls on right
        date_frame = tk.Frame(header_frame, bg=COLORS["bg_primary"])
        date_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            date_frame,
            text="Select Date:",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Create date entry with calendar button
        date_entry = ttk.Entry(date_frame,
                             textvariable=self.date_var,
                             width=12,
                             font=FONTS["regular"],
                             style='primary.TEntry')
        date_entry.pack(side=tk.LEFT)
        
        def show_calendar():
            # Parse current date from DD/MM/YYYY format
            try:
                current_date = datetime.datetime.strptime(self.date_var.get(), "%d/%m/%Y").date()
            except ValueError:
                current_date = datetime.datetime.now().date()
                
            dialog = DatePickerDialog(
                parent=self,
                title="Select Date",
                firstweekday=6,  # Sunday first
                startdate=current_date,
                bootstyle="primary"
            )
            if hasattr(dialog, 'date_selected'):
                self.date_var.set(dialog.date_selected.strftime("%d/%m/%Y"))
                self.selected_date = dialog.date_selected
                self.load_sales()
        
        # Add calendar button
        cal_button = ttk.Button(date_frame,
                              text="📅",
                              style='primary.TButton',
            width=3,
                              command=show_calendar)
        cal_button.pack(side=tk.LEFT, padx=(5, 10))
        
        # Today button
        today_btn = ttk.Button(
            date_frame,
            text="Today",
            style='secondary.TButton',
            command=self.select_today
        )
        today_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        view_button = ttk.Button(
            date_frame,
            text="View Sales",
            style='primary.TButton',
            command=self.load_sales
        )
        view_button.pack(side=tk.LEFT)
        
        # Create content frame for main content area
        content_frame = tk.Frame(main_container, bg=COLORS["bg_primary"], padx=5, pady=0)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel (invoices list) - 55% width
        left_frame = tk.Frame(content_frame, bg=COLORS["bg_primary"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=0)
        
        # Create right panel (invoice details) - 45% width  
        right_frame = tk.Frame(content_frame, bg=COLORS["bg_primary"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=0)
        
        # Make the frames match the proportions in sales.py
        left_frame.config(width=550)  # 55% width
        right_frame.config(width=450) # 45% width
        
        # Setup two panels - left for invoices list, right for details
        self.setup_sales_list(left_frame)
        self.setup_details_panel(right_frame)
    
    def setup_sales_list(self, parent):
        """Setup the sales/invoices list panel"""
        # Create the list frame with proper padding
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Prevent the frame from changing its size based on children
        parent.pack_propagate(False)
        
        # Title for list
        tk.Label(
            list_frame,
            text="Invoices",
            font=FONTS["subheading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        
        # Stats for the selected day
        self.stats_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.total_sales_label = tk.Label(
            self.stats_frame,
            text="Total Sales: ₹0.00",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.total_sales_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.invoice_count_label = tk.Label(
            self.stats_frame,
            text="Invoices: 0",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.invoice_count_label.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="Search:",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["regular"]
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.search_invoices)
        
        # Tree and scrollbar container
        tree_container = tk.Frame(list_frame, bg=COLORS["bg_secondary"])
        tree_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Treeview for sales list
        columns = ("invoice_number", "customer", "amount", "payment", "time")
        self.sales_tree = ttk.Treeview(
            tree_container, 
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview"
        )
        
        # Define headings with more descriptive names
        self.sales_tree.heading("invoice_number", text="Invoice #")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("amount", text="Amount")
        self.sales_tree.heading("payment", text="Payment")
        self.sales_tree.heading("time", text="Time")
        
        # Calculate optimal column widths based on available space
        # We'll set proportions that add up to 100% of available width
        self.sales_tree.column("invoice_number", width=120, anchor="w", minwidth=80, stretch=True)
        self.sales_tree.column("customer", width=170, anchor="w", minwidth=100, stretch=True)
        self.sales_tree.column("amount", width=100, anchor="e", minwidth=80, stretch=True)
        self.sales_tree.column("payment", width=100, anchor="center", minwidth=80, stretch=True)
        self.sales_tree.column("time", width=80, anchor="center", minwidth=60, stretch=True)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.sales_tree.xview)
        self.sales_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Place treeview with pack layout to match sales.py
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.sales_tree.bind("<<TreeviewSelect>>", self.on_invoice_select)
        self.sales_tree.bind("<Double-1>", self.view_invoice)
        
        # Bind right-click context menu
        self.sales_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_details_panel(self, parent):
        """Setup the invoice details panel"""
        # Create the details frame with proper padding
        details_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=10, pady=10)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Prevent the frame from changing its size based on children
        parent.pack_propagate(False)
        
        # Title for details
        title_label = tk.Label(
            details_frame,
            text="Invoice Details",
            font=FONTS["subheading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(side=tk.TOP, anchor="w", pady=(0, 15))
        
        # Customer and invoice info container
        info_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        info_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))
        
        # Customer info - left side
        customer_frame = tk.Frame(info_frame, bg=COLORS["bg_secondary"])
        customer_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor="nw")
        
        tk.Label(
            customer_frame,
            text="Customer Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w")
        
        self.customer_name_label = tk.Label(
            customer_frame,
            text="Name: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.customer_name_label.pack(anchor="w", pady=(5, 0))
        
        self.customer_phone_label = tk.Label(
            customer_frame,
            text="Phone: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.customer_phone_label.pack(anchor="w")
        
        self.customer_address_label = tk.Label(
            customer_frame,
            text="Address: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.customer_address_label.pack(anchor="w")
        
        # Invoice info - right side
        invoice_frame = tk.Frame(info_frame, bg=COLORS["bg_secondary"])
        invoice_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True, anchor="ne")
        
        tk.Label(
            invoice_frame,
            text="Invoice Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w")
        
        self.invoice_number_label = tk.Label(
            invoice_frame,
            text="No.: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.invoice_number_label.pack(anchor="w", pady=(5, 0))
        
        self.invoice_date_label = tk.Label(
            invoice_frame,
            text="Date: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.invoice_date_label.pack(anchor="w")
        
        self.invoice_amount_label = tk.Label(
            invoice_frame,
            text="Amount: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor="w", 
            justify="left"
        )
        self.invoice_amount_label.pack(anchor="w")
        
        # Invoice items section
        items_label_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        items_label_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        tk.Label(
            items_label_frame,
            text="Items",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, anchor="w")
        
        # Create a container for items that expands to fill available space
        items_container = tk.Frame(details_frame, bg=COLORS["bg_secondary"], 
                                  highlightbackground=COLORS["border"], 
                                  highlightthickness=1)
        items_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Set minimum height for items container
        items_container.configure(height=300)
        items_container.pack_propagate(False)  # Prevent shrinking below minimum size
        
        # Create frame for treeview and scrollbars that fills the entire container
        tree_frame = tk.Frame(items_container, bg=COLORS["bg_secondary"])
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=2)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview for invoice items
        columns = ("item", "hsn", "qty", "price", "discount", "amount")
        self.items_tree = ttk.Treeview(
            tree_frame, 
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Connect scrollbars to treeview
        v_scrollbar.config(command=self.items_tree.yview)
        h_scrollbar.config(command=self.items_tree.xview)
        
        # Define headings
        self.items_tree.heading("item", text="Item")
        self.items_tree.heading("hsn", text="HSN")
        self.items_tree.heading("qty", text="Qty")
        self.items_tree.heading("price", text="Price")
        self.items_tree.heading("discount", text="Disc %")
        self.items_tree.heading("amount", text="Amount")
        
        # Define columns with improved alignment and proportions - using stretch=True to fill available space
        self.items_tree.column("item", width=180, anchor="w", minwidth=100, stretch=True)  # Wider for item names, left aligned
        self.items_tree.column("hsn", width=80, anchor="center", minwidth=60, stretch=True)  # Center HSN codes
        self.items_tree.column("qty", width=60, anchor="center", minwidth=40, stretch=True)  # Center quantities
        self.items_tree.column("price", width=100, anchor="e", minwidth=80, stretch=True)  # Right align prices
        self.items_tree.column("discount", width=80, anchor="center", minwidth=60, stretch=True)  # Center discounts
        self.items_tree.column("amount", width=100, anchor="e", minwidth=80, stretch=True)  # Right align amounts
        
        # Place treeview
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Payment info section
        payment_label_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        payment_label_frame.pack(side=tk.TOP, fill=tk.X, pady=(15, 5))
        
        tk.Label(
            payment_label_frame,
            text="Payment Information",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT, anchor="w")
        
        # Payment details container
        payment_container = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        payment_container.pack(side=tk.TOP, fill=tk.X)
        
        # Payment info in two columns
        payment_columns = tk.Frame(payment_container, bg=COLORS["bg_secondary"])
        payment_columns.pack(side=tk.TOP, fill=tk.X)
        
        # Left side payment info
        payment_left = tk.Frame(payment_columns, bg=COLORS["bg_secondary"])
        payment_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.payment_method_label = tk.Label(
            payment_left,
            text="Method: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_method_label.pack(anchor="w")
        
        # Right side payment info
        payment_right = tk.Frame(payment_columns, bg=COLORS["bg_secondary"])
        payment_right.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.payment_status_label = tk.Label(
            payment_right,
            text="Status: -",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_status_label.pack(anchor="w")
        
        # Additional payment details below
        payment_details = tk.Frame(payment_container, bg=COLORS["bg_secondary"])
        payment_details.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        self.payment_details_label = tk.Label(
            payment_details,
            text="",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.payment_details_label.pack(anchor="w")
        
        # Buttons frame at the bottom
        buttons_frame = tk.Frame(details_frame, bg=COLORS["bg_secondary"])
        buttons_frame.pack(side=tk.TOP, fill=tk.X, pady=(15, 0))
        
        self.view_btn = tk.Button(
            buttons_frame,
            text="View Invoice",
            font=FONTS["regular_bold"],
            bg=COLORS["primary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.view_invoice
        )
        self.view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.print_btn = tk.Button(
            buttons_frame,
            text="Print Invoice",
            font=FONTS["regular_bold"],
            bg=COLORS["secondary"],
            fg=COLORS["text_white"],
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.print_invoice
        )
        self.print_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add collect payment button for credit invoices
        self.collect_payment_btn = tk.Button(
            buttons_frame,
            text="Collect Payment",
            font=FONTS["regular_bold"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.collect_payment
        )
        self.collect_payment_btn.pack(side=tk.LEFT)
    
    def select_today(self):
        """Set date to today"""
        today = datetime.date.today()
        self.date_var.set(today.strftime("%d/%m/%Y"))
        self.selected_date = today
        self.load_sales()
    
    def load_sales(self):
        """Load sales for the selected date"""
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Reset details
        self.clear_details()
        
        # Format date for SQL query
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        # Query to get invoices for the selected date
        query = """
            SELECT i.id, i.invoice_number, c.name as customer_name, 
                   i.total_amount, i.payment_method, i.payment_status,
                   i.invoice_date, i.file_path
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE DATE(i.invoice_date) = ?
            ORDER BY i.invoice_date DESC
        """
        
        invoices = self.controller.db.fetchall(query, (date_str,))
        
        if not invoices:
            self.update_stats(0, 0)
            messagebox.showinfo("No Invoices", f"No invoices found for {self.selected_date.strftime('%d-%m-%Y')}.")
            return
        
        # Calculate total sales
        total_sales = sum(invoice[3] for invoice in invoices)
        invoice_count = len(invoices)
        
        # Update stats
        self.update_stats(total_sales, invoice_count)
        
        # Add invoices to treeview
        for invoice in invoices:
            # Parse invoice date for display
            invoice_time = datetime.datetime.strptime(invoice[6], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            
            self.sales_tree.insert(
                "",
                "end",
                values=(
                    invoice[1],                      # Invoice number
                    invoice[2] or "Walk-in Customer", # Customer name
                    format_currency(invoice[3]),     # Total amount
                    invoice[4],                      # Payment method
                    invoice_time                     # Time
                ),
                tags=(str(invoice[0]),)  # Store invoice ID as tag for selection
            )
    
    def search_invoices(self, event=None):
        """Search invoices based on search term"""
        search_term = self.search_var.get().lower()
        
        # If search term is empty, reload all invoices
        if not search_term:
            self.load_sales()
            return
        
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Format date for SQL query
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        # Query to get invoices for the selected date matching search term
        query = """
            SELECT i.id, i.invoice_number, c.name as customer_name, 
                   i.total_amount, i.payment_method, i.payment_status,
                   i.invoice_date, i.file_path
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE DATE(i.invoice_date) = ?
              AND (i.invoice_number LIKE ? OR c.name LIKE ? OR i.payment_method LIKE ?)
            ORDER BY i.invoice_date DESC
        """
        
        search_pattern = f"%{search_term}%"
        invoices = self.controller.db.fetchall(
            query, 
            (date_str, search_pattern, search_pattern, search_pattern)
        )
        
        if not invoices:
            # No results found
            self.update_stats(0, 0)
            return
        
        # Calculate total sales for filtered results
        total_sales = sum(invoice[3] for invoice in invoices)
        invoice_count = len(invoices)
        
        # Update stats for filtered results
        self.update_stats(total_sales, invoice_count)
        
        # Add invoices to treeview
        for invoice in invoices:
            # Parse invoice date for display
            invoice_time = datetime.datetime.strptime(invoice[6], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            
            self.sales_tree.insert(
                "",
                "end",
                values=(
                    invoice[1],                      # Invoice number
                    invoice[2] or "Walk-in Customer", # Customer name
                    format_currency(invoice[3]),     # Total amount
                    invoice[4],                      # Payment method
                    invoice_time                     # Time
                ),
                tags=(str(invoice[0]),)  # Store invoice ID as tag for selection
            )
    
    def update_stats(self, total_sales, invoice_count):
        """Update stats display"""
        self.total_sales_label.config(text=f"Total Sales: {format_currency(total_sales)}")
        self.invoice_count_label.config(text=f"Invoices: {invoice_count}")
    
    def on_invoice_select(self, event=None):
        """Handle invoice selection in treeview"""
        selection = self.sales_tree.selection()
        if not selection:
            self.clear_details()
            return
        
        # Get invoice ID from tag with better error handling
        try:
            # Dump ALL item details to see exactly what we're working with
            all_item_details = self.sales_tree.item(selection[0])
            print(f"DEBUG: ALL selected item details: {all_item_details}")
            
            item_tags = self.sales_tree.item(selection[0], "tags")
            print(f"DEBUG: Selected item tags: {item_tags}")
            
            # Also print the item values to see what invoice number we're looking at
            item_values = self.sales_tree.item(selection[0], "values")
            print(f"DEBUG: Selected item values: {item_values}")
            
            if not item_tags:
                print("DEBUG: No tags found on selected item")
                # Try to recover - use the row directly 
                row_id = selection[0]
                try:
                    # See if the row's ID can be parsed as an invoice ID
                    if row_id.startswith("I"):
                        potential_id = int(row_id[1:]) # Skip the "I" prefix
                        print(f"DEBUG: Recovered potential ID from row_id: {potential_id}")
                        invoice_id = potential_id
                    else:
                        raise ValueError("Row ID not in expected format")
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Couldn't extract ID from row: {e}")
                    self.clear_details()
                    messagebox.showerror("Error", "This invoice record is missing its ID tag. Please try another invoice.")
                    return
            else:
                try:    
                    invoice_id = int(item_tags[0])
                except (IndexError, ValueError, TypeError) as e:
                    print(f"DEBUG: Error extracting invoice ID from tags: {e}")
                    self.clear_details()
                    messagebox.showerror("Error", "Could not determine invoice ID from selection.")
                    return
                
            print(f"DEBUG: Processing selection for invoice ID: {invoice_id}")
            self.current_invoice_id = invoice_id
            
            # Check if invoice exists in either invoices or sales table
            check_query = """
                SELECT 
                    (SELECT COUNT(*) FROM invoices WHERE id = ?) as invoice_count,
                    (SELECT COUNT(*) FROM sales WHERE id = ?) as sale_count
            """
            check_result = self.controller.db.fetchone(check_query, (invoice_id, invoice_id))
            
            if not check_result:
                print(f"DEBUG: Failed to check if invoice ID {invoice_id} exists")
                self.clear_details()
                return
                
            invoice_exists = check_result[0] > 0
            sale_exists = check_result[1] > 0
            
            print(f"DEBUG: Invoice ID {invoice_id} exists in invoices: {invoice_exists}, in sales: {sale_exists}")
            
            # Determine which table to query based on existence
            if invoice_exists:
                # Query from invoices table
                query = """
                    SELECT 
                        i.id, i.invoice_number, i.customer_id, i.subtotal, 
                        i.discount_amount, i.tax_amount, i.total_amount, 
                        i.payment_method, i.payment_status, i.cash_amount, 
                        i.upi_amount, i.upi_reference, i.credit_amount, 
                        i.invoice_date, i.file_path,
                        c.name, c.phone, c.address
                    FROM invoices i
                    LEFT JOIN customers c ON i.customer_id = c.id
                    WHERE i.id = ?
                """
            elif sale_exists:
                # Query from sales table 
                query = """
                    SELECT 
                        s.id, s.invoice_number, s.customer_id, s.subtotal, 
                        s.discount_amount, s.tax_amount, s.total, 
                        s.payment_method, s.status, s.cash_amount, 
                        s.upi_amount, s.upi_reference, s.credit_amount, 
                        s.created_at, NULL as file_path,
                        c.name, c.phone, c.address
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    WHERE s.id = ?
                """
            else:
                print(f"DEBUG: Invoice {invoice_id} not found in either table")
                self.clear_details()
                messagebox.showinfo("Not Found", f"Invoice #{invoice_id} could not be found in the database.")
                return
            
            # Fetch the record
            invoice = self.controller.db.fetchone(query, (invoice_id,))
            
            if not invoice:
                print(f"DEBUG: Query returned no results for ID: {invoice_id}")
                self.clear_details()
                return
            
            # Debug output to see what we're working with
            print(f"DEBUG: Found invoice: {invoice}")
            
            # Update UI with comprehensive error handling
            try:
                # Update customer info - safely handle missing data
                customer_name = invoice[15] if len(invoice) > 15 and invoice[15] else 'Walk-in Customer'
                customer_phone = invoice[16] if len(invoice) > 16 and invoice[16] else '-'
                customer_address = invoice[17] if len(invoice) > 17 and invoice[17] else '-'
                
                self.customer_name_label.config(text=f"Name: {customer_name}")
                self.customer_phone_label.config(text=f"Phone: {customer_phone}")
                self.customer_address_label.config(text=f"Address: {customer_address}")
                
                # Update invoice info
                invoice_number = invoice[1] if len(invoice) > 1 and invoice[1] else '-'
                self.invoice_number_label.config(text=f"No.: {invoice_number}")
                
                # Handle date formatting with comprehensive error handling
                try:
                    invoice_date = invoice[13] if len(invoice) > 13 else None
                    if invoice_date:
                        try:
                            formatted_date = format_date(invoice_date)
                        except:
                            # If format_date fails, try parsing first
                            formatted_date = format_date(parse_date(invoice_date))
                    else:
                        formatted_date = format_date(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                except Exception as e:
                    print(f"DEBUG: Error formatting date: {e}, using current date")
                    formatted_date = format_date(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                self.invoice_date_label.config(text=f"Date: {formatted_date}")
                
                # Total amount could be in different columns based on the table
                total_index = 6
                total = 0
                if len(invoice) > total_index:
                    try:
                        total = float(invoice[total_index]) if invoice[total_index] is not None else 0
                    except (ValueError, TypeError):
                        print(f"DEBUG: Error converting total to float: {invoice[total_index]}")
                
                self.invoice_amount_label.config(text=f"Amount: {format_currency(total)}")
                
                # Update payment info
                payment_method = invoice[7] if len(invoice) > 7 and invoice[7] else '-'
                payment_status = invoice[8] if len(invoice) > 8 and invoice[8] else 'PAID'
                
                self.payment_method_label.config(text=f"Method: {payment_method}")
                self.payment_status_label.config(text=f"Status: {payment_status}")
                
                # Enable collect payment button for credit invoices with "UNPAID" or "PARTIALLY_PAID" status
                if payment_method and payment_status:
                    # Get credit amount with safe access
                    credit_amount = 0
                    try:
                        if invoice[12] is not None:
                            credit_amount = float(invoice[12])
                    except (ValueError, TypeError):
                        print(f"DEBUG: Error converting credit amount to float: {invoice[12]}")
                    
                    # Enable button for:
                    # 1. CREDIT payment method with UNPAID or PARTIALLY_PAID status
                    # 2. SPLIT payment method with remaining credit amount > 0
                    # 3. Any invoice with PARTIAL or PARTIALLY_PAID status (handle different naming conventions)
                    enable_button = False
                    
                    # Handle CREDIT payment method
                    if payment_method.upper() == "CREDIT" and (
                        payment_status.upper() in ["UNPAID", "PARTIALLY_PAID", "PARTIAL"]):
                        enable_button = True
                        
                    # Handle SPLIT payment method with remaining credit
                    elif payment_method.upper() == "SPLIT" and credit_amount > 0:
                        enable_button = True
                    
                    # Also enable for any payment method with a partial payment status
                    elif payment_status.upper() in ["PARTIALLY_PAID", "PARTIAL"]:
                        enable_button = True
                    
                    if enable_button:
                        self.collect_payment_btn.config(state=tk.NORMAL)
                    else:
                        self.collect_payment_btn.config(state=tk.DISABLED)
                else:
                    self.collect_payment_btn.config(state=tk.DISABLED)
                
                # Modified to only show pending amount instead of full payment breakdown
                payment_details = ""
                try:
                    if payment_method and payment_method.upper() in ["SPLIT", "CREDIT"]:
                        # Only show pending amount for SPLIT or CREDIT payments
                        credit = invoice[12] if len(invoice) > 12 and invoice[12] is not None else 0
                        upi_ref = invoice[11] if len(invoice) > 11 and invoice[11] else ""
                        
                        # For UNPAID or PARTIALLY_PAID, show outstanding amount
                        if payment_status and payment_status.upper() in ["UNPAID", "PARTIALLY_PAID", "PARTIAL"]:
                            payment_details = f"Outstanding Amount: {format_currency(credit)}"
                            
                            # Removed UPI reference display as per requirement
                        elif payment_status and payment_status.upper() == "PAID":
                            # For fully paid credits
                            if payment_method.upper() == "CREDIT":
                                payment_details = "Fully Paid"
                            elif payment_method.upper() == "SPLIT":
                                # For split payments that are fully paid
                                payment_details = "Fully Paid"
                                # Removed UPI reference display as per requirement
                    elif payment_method and payment_method.upper() == "UPI":
                        # No need to show UPI reference in sales history
                        payment_details = "Paid via UPI"
                except Exception as e:
                    print(f"DEBUG: Error creating payment details: {e}")
                
                self.payment_details_label.config(text=payment_details)
                
                # Show payment history for credit or split payments
                if payment_status and (payment_status.upper() in ["PARTIALLY_PAID", "PARTIAL", "PAID"] and 
                                       (payment_method.upper() == "CREDIT" or 
                                        (payment_method.upper() == "SPLIT" and invoice[12] is not None and float(invoice[12]) > 0))):
                    payment_history = self.get_payment_history(invoice_id)
                    if payment_history and payment_history != "No payment records found.":
                        if payment_details:
                            payment_details += "\n\n" + payment_history
                        else:
                            payment_details = payment_history
                        self.payment_details_label.config(text=payment_details)
                
                # Handle buttons for view/print
                if invoice_exists and len(invoice) > 14:
                    file_path = invoice[14]  # file_path is at index 14 from invoices table
                    if file_path and os.path.exists(file_path):
                        print(f"DEBUG: Invoice file exists at: {file_path}")
                        self.view_btn.config(state=tk.NORMAL)
                        self.print_btn.config(state=tk.NORMAL)
                    else:
                        # Try with relative path
                        file_name = os.path.basename(file_path) if file_path else ""
                        rel_path = os.path.join(".", "invoices", file_name) if file_name else ""
                        
                        if rel_path and os.path.exists(rel_path):
                            print(f"DEBUG: Invoice file exists at relative path: {rel_path}")
                            self.view_btn.config(state=tk.NORMAL)
                            self.print_btn.config(state=tk.NORMAL)
                        else:
                            print(f"DEBUG: Invoice file not found at: {file_path} or {rel_path}")
                            self.view_btn.config(state=tk.DISABLED)
                            self.print_btn.config(state=tk.DISABLED)
                else:
                    # No file for sales or missing data
                    self.view_btn.config(state=tk.DISABLED)
                    self.print_btn.config(state=tk.DISABLED)
                
            except Exception as e:
                print(f"DEBUG: Error updating UI with invoice details: {e}")
                import traceback
                traceback.print_exc()
            
            # Load invoice items with the ID
            self.load_invoice_items(invoice_id)
            
        except Exception as e:
            print(f"DEBUG: Unhandled error in on_invoice_select: {e}")
            import traceback
            traceback.print_exc()
            self.clear_details()
    
    def load_invoice_items(self, invoice_id):
        """Load items for the selected invoice"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        print(f"DEBUG: Loading items for invoice ID: {invoice_id}")
        
        # First check if this is a valid invoice ID
        query_check = "SELECT COUNT(*) FROM invoices WHERE id = ?"
        result_check = self.controller.db.fetchone(query_check, (invoice_id,))
        has_invoice = result_check and result_check[0] > 0
        
        # Check if there's a corresponding sale ID
        query_check_sale = "SELECT COUNT(*) FROM sales WHERE id = ?"
        result_check_sale = self.controller.db.fetchone(query_check_sale, (invoice_id,))
        has_sale = result_check_sale and result_check_sale[0] > 0
        
        print(f"DEBUG: Invoice ID {invoice_id} exists in invoices table: {has_invoice}")
        print(f"DEBUG: Invoice ID {invoice_id} exists in sales table: {has_sale}")
        
        # Get the table schema to understand what columns are available
        try:
            print("DEBUG: Checking table schema for invoice_items")
            schema_query = "PRAGMA table_info(invoice_items)"
            schema = self.controller.db.fetchall(schema_query)
            print(f"DEBUG: invoice_items schema: {[col[1] for col in schema]}")
        except Exception as e:
            print(f"DEBUG: Error checking schema: {e}")
        
        # Search for invoice items with more rigorous error handling
        items = []
        
        # Try the invoice_items table if we have an invoice record
        if has_invoice:
            try:
                # Use a dynamic approach that checks column names first
                schema_query = "PRAGMA table_info(invoice_items)"
                schema = self.controller.db.fetchall(schema_query)
                column_names = [col[1] for col in schema]
                
                # Determine price column
                price_column = None
                for price_name in ['unit_price', 'price_per_unit', 'price']:
                    if price_name in column_names:
                        price_column = price_name
                        break
                
                # Default to 'unit_price' if we can't determine
                if not price_column:
                    price_column = 'unit_price'
                    print(f"DEBUG: Could not determine price column, using {price_column}")
                else:
                    print(f"DEBUG: Using {price_column} for price")
                
                # Build a more resilient query based on available columns
                # Check if hsn_code column exists in invoice_items
                has_hsn_in_invoice_items = 'hsn_code' in column_names
                
                query = f"""
                    SELECT 
                        COALESCE(p.name, 'Item ' || ii.product_id) as product_name,
                        {('COALESCE(ii.hsn_code, p.hsn_code, ' + "'-')" if has_hsn_in_invoice_items else 'COALESCE(p.hsn_code, ' + "'-')")} as hsn_code,
                        COALESCE(ii.quantity, 0) as quantity,
                        COALESCE(ii.{price_column}, 0) as price,
                        COALESCE(ii.discount_percentage, 0) as discount,
                        COALESCE(ii.total_price, 0) as total
                    FROM invoice_items ii
                    LEFT JOIN products p ON ii.product_id = p.id
                    WHERE ii.invoice_id = ?
                """
                items = self.controller.db.fetchall(query, (invoice_id,))
                if items:
                    print(f"DEBUG: Found {len(items)} items in invoice_items table")
                    # Print first item for debugging
                    if len(items) > 0:
                        print(f"DEBUG: First item data: {items[0]}")
            except Exception as e:
                print(f"DEBUG: Error querying invoice_items: {e}")
                import traceback
                traceback.print_exc()
        
        # If no items found or no invoice, try the sale_items table
        if not items and has_sale:
            try:
                # Check schema of sale_items too
                schema_query = "PRAGMA table_info(sale_items)"
                schema = self.controller.db.fetchall(schema_query)
                column_names = [col[1] for col in schema]
                print(f"DEBUG: sale_items schema: {column_names}")
                
                # Determine discount column
                discount_column = 'discount_percentage'
                if 'discount_percentage' in column_names:
                    discount_column = 'discount_percentage'
                elif 'discount_percent' in column_names:
                    discount_column = 'discount_percent'
                
                query = f"""
                    SELECT 
                        COALESCE(si.product_name, 'Item ' || si.product_id) as product_name,
                        COALESCE(si.hsn_code, '-') as hsn_code,
                        COALESCE(si.quantity, 0) as quantity,
                        COALESCE(si.price, 0) as price,
                        COALESCE(si.{discount_column}, 0) as discount,
                        COALESCE(si.total, ROUND(COALESCE(si.quantity, 0) * COALESCE(si.price, 0) * (1 - COALESCE(si.{discount_column}, 0)/100), 2)) as total
                    FROM sale_items si
                    WHERE si.sale_id = ?
                """
                items = self.controller.db.fetchall(query, (invoice_id,))
                if items:
                    print(f"DEBUG: Found {len(items)} items in sale_items table")
                    # Print first item for debugging
                    if len(items) > 0:
                        print(f"DEBUG: First sale item data: {items[0]}")
            except Exception as e:
                print(f"DEBUG: Error querying sale_items: {e}")
                import traceback
                traceback.print_exc()
        
        # Check relationship between invoices and sales to try alternative approach
        if not items and has_invoice:
            try:
                print("DEBUG: Trying to find related sale for this invoice")
                # Try to find associated sale ID via invoice number
                query = """
                    SELECT s.id 
                    FROM sales s
                    JOIN invoices i ON s.invoice_number = i.invoice_number
                    WHERE i.id = ?
                """
                related_sale = self.controller.db.fetchone(query, (invoice_id,))
                
                if related_sale:
                    sale_id = related_sale[0]
                    print(f"DEBUG: Found related sale ID {sale_id} for invoice {invoice_id}")
                    
                    # Now query sale_items using this sale ID
                    # First check the schema to use the correct column names
                    schema_query = "PRAGMA table_info(sale_items)"
                    schema = self.controller.db.fetchall(schema_query)
                    column_names = [col[1] for col in schema]
                    print(f"DEBUG: sale_items schema for related sale: {column_names}")
                    
                    # Determine discount column name
                    discount_column = 'discount_percent'
                    if 'discount_percentage' in column_names:
                        discount_column = 'discount_percentage'
                    elif 'discount_percent' in column_names:
                        discount_column = 'discount_percent'
                    
                    print(f"DEBUG: Using discount column: {discount_column}")
                    
                    query = f"""
                        SELECT 
                            COALESCE(si.product_name, 'Item ' || si.product_id) as product_name,
                            COALESCE(si.hsn_code, '-') as hsn_code,
                            COALESCE(si.quantity, 0) as quantity,
                            COALESCE(si.price, 0) as price,
                            COALESCE(si.{discount_column}, 0) as discount,
                            COALESCE(si.total, ROUND(COALESCE(si.quantity, 0) * COALESCE(si.price, 0) * (1 - COALESCE(si.{discount_column}, 0)/100), 2)) as total
                        FROM sale_items si
                        WHERE si.sale_id = ?
                    """
                    items = self.controller.db.fetchall(query, (sale_id,))
                    if items:
                        print(f"DEBUG: Found {len(items)} items in sale_items table via related sale")
            except Exception as e:
                print(f"DEBUG: Error finding related sale: {e}")
        
        # If still no items found, try a raw approach to get any data
        if not items:
            print(f"DEBUG: No items found in either table for ID {invoice_id}")
            try:
                # Get a raw dump of any invoice_items for this invoice_id
                raw_query = "SELECT * FROM invoice_items WHERE invoice_id = ?"
                raw_items = self.controller.db.fetchall(raw_query, (invoice_id,))
                
                if raw_items and len(raw_items) > 0:
                    print(f"DEBUG: Found {len(raw_items)} raw invoice_items")
                    # Print the raw data to understand structure
                    for i, raw_item in enumerate(raw_items):
                        print(f"DEBUG: Raw item {i+1}: {raw_item}")
                        
                        # Try to create proper display values
                        try:
                            product_id = raw_item[2] if len(raw_item) > 2 and raw_item[2] is not None else "Unknown"
                            # Try to get product name from products table
                            product_query = "SELECT name FROM products WHERE id = ?"
                            product_result = self.controller.db.fetchone(product_query, (product_id,))
                            product_name = product_result[0] if product_result else f"Product #{product_id}"
                            
                            # Find quantity, price and total based on column position
                            quantity = raw_item[4] if len(raw_item) > 4 and raw_item[4] is not None else 0
                            price = 0
                            for j in range(3, len(raw_item)):
                                if isinstance(raw_item[j], (int, float)) and raw_item[j] > 0 and raw_item[j] < 10000:
                                    # This is likely the price value
                                    price = raw_item[j]
                                    break
                            
                            # Total is likely one of the higher values
                            total = 0
                            for j in range(3, len(raw_item)):
                                if isinstance(raw_item[j], (int, float)) and raw_item[j] > price:
                                    # This is likely the total value
                                    total = raw_item[j]
                                    break
                            
                            # Create a display item
                            self.items_tree.insert(
                                "",
                                "end",
                                values=(
                                    product_name,
                                    "-",
                                    quantity,
                                    format_currency(price),
                                    "0",
                                    format_currency(total)
                                )
                            )
                        except Exception as e:
                            print(f"DEBUG: Error processing raw item: {e}")
                    
                    # If we processed items, return
                    if self.items_tree.get_children():
                        print("DEBUG: Successfully added items from raw data")
                        return
            except Exception as e:
                print(f"DEBUG: Error in raw query: {e}")
                import traceback
                traceback.print_exc()
            
            # If still nothing, add a placeholder item for better user experience
            self.items_tree.insert(
                "",
                "end",
                values=(
                    "No items found for this invoice",
                    "-",
                    "0",
                    "₹0.00",
                    "0",
                    "₹0.00"
                )
            )
            return
        
        # Add the items to the treeview
        for i, item in enumerate(items, 1):
            try:
                # Extract data with comprehensive error handling
                product_name = item[0] if item[0] and len(item) > 0 else "Unknown Product"
                hsn_code = item[1] if len(item) > 1 and item[1] else "-"
                
                try:
                    quantity = int(item[2]) if len(item) > 2 and item[2] is not None else 0
                except (ValueError, TypeError):
                    quantity = 0
                
                try:
                    price = float(item[3]) if len(item) > 3 and item[3] is not None else 0.0
                except (ValueError, TypeError):
                    price = 0.0
                
                try:
                    discount = float(item[4]) if len(item) > 4 and item[4] is not None else 0.0
                except (ValueError, TypeError):
                    discount = 0.0
                
                try:
                    total = float(item[5]) if len(item) > 5 and item[5] is not None else 0.0
                except (ValueError, TypeError):
                    total = 0.0
                
                # Create a unique ID for this row
                row_id = f"item_{invoice_id}_{i}"
                
                # Insert data into treeview
                self.items_tree.insert(
                    "",
                    "end",
                    iid=row_id,
                    values=(
                        product_name,
                        hsn_code,
                        quantity,
                        format_currency(price),
                        discount,
                        format_currency(total)
                    )
                )
                
                print(f"DEBUG: Added item {row_id}: {product_name}, {hsn_code}, {quantity}, {price}, {discount}, {total}")
            except Exception as e:
                print(f"DEBUG: Error adding item to treeview: {e}")
                import traceback
                traceback.print_exc()
        
        # Add a success message if items were added
        if self.items_tree.get_children():
            print(f"DEBUG: Successfully added {len(self.items_tree.get_children())} items to treeview")
        else:
            print("DEBUG: No items were added to the treeview despite finding data")
            # Add a placeholder item so the user sees something
            self.items_tree.insert(
                "",
                "end",
                values=(
                    "Items could not be displayed properly",
                    "-",
                    "0",
                    "₹0.00",
                    "0",
                    "₹0.00"
                )
            )
    
    def collect_payment(self):
        """Collect payment for a credit invoice"""
        if not self.current_invoice_id:
            messagebox.showerror("Error", "No invoice selected.")
            return
            
        # Get invoice details
        query = """
            SELECT 
                i.id, i.invoice_number, i.customer_id, i.total_amount, 
                i.payment_method, i.payment_status, i.credit_amount,
                c.name as customer_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
        """
        invoice = self.controller.db.fetchone(query, (self.current_invoice_id,))
        
        if not invoice:
            messagebox.showerror("Error", "Invoice not found.")
            return
            
        # Extract invoice details
        invoice_id = invoice[0]
        invoice_number = invoice[1]
        customer_id = invoice[2]
        total_amount = invoice[3]
        payment_method = invoice[4]
        payment_status = invoice[5]
        credit_amount = invoice[6] or 0
        customer_name = invoice[7] or "Walk-in Customer"
        
        # Verify this is a credit or split invoice with pending amount
        if not payment_method or (payment_method.upper() != "CREDIT" and payment_method.upper() != "SPLIT"):
            messagebox.showerror("Error", "This operation is only allowed for credit or split payment invoices.")
            return
            
        # For SPLIT payments, verify there's an outstanding credit amount
        if payment_method.upper() == "SPLIT" and (credit_amount is None or credit_amount <= 0):
            messagebox.showerror("Error", "There's no pending credit amount to collect for this invoice.")
            return
            
        # Verify the payment status is UNPAID, PARTIALLY_PAID, or PARTIAL
        if not payment_status or (payment_status.upper() not in ["UNPAID", "PARTIALLY_PAID", "PARTIAL"]):
            messagebox.showerror("Error", "This invoice must have an unpaid or partially paid status to collect payment.")
            return
        
        # Create collect payment dialog
        payment_dialog = tk.Toplevel(self)
        payment_dialog.title("Collect Payment")
        payment_dialog.geometry("500x700")
        payment_dialog.resizable(False, False)
        payment_dialog.configure(bg=COLORS["bg_primary"])
        payment_dialog.grab_set()  # Make window modal
        
        # Center the dialog
        payment_dialog.update_idletasks()
        width = payment_dialog.winfo_width()
        height = payment_dialog.winfo_height()
        x = (payment_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (payment_dialog.winfo_screenheight() // 2) - (height // 2)
        payment_dialog.geometry(f"+{x}+{y}")
        
        # Create form
        title_label = tk.Label(
            payment_dialog, 
            text=f"Collect Payment for Invoice #{invoice_number}",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            wraplength=450
        )
        title_label.pack(pady=15)
        
        # Customer info
        info_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], padx=20)
        info_frame.pack(fill=tk.X)
        
        customer_label = tk.Label(
            info_frame,
            text=f"Customer: {customer_name}",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            anchor="w"
        )
        customer_label.pack(side=tk.TOP, anchor="w", pady=5)
        
        amount_label = tk.Label(
            info_frame,
            text=f"Outstanding Amount: {format_currency(credit_amount)}",
            font=FONTS["regular_bold"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            anchor="w"
        )
        amount_label.pack(side=tk.TOP, anchor="w", pady=5)
        
        # Form frame
        form_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Payment method
        payment_method_label = tk.Label(
            form_frame,
            text="Payment Method:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        payment_method_label.grid(row=0, column=0, sticky="w", pady=8)
        
        payment_method_var = tk.StringVar(value="CASH")
        payment_methods = ["CASH", "UPI", "CHEQUE"]
        
        payment_method_menu = ttk.Combobox(
            form_frame,
            textvariable=payment_method_var,
            values=payment_methods,
            state="readonly",
            font=FONTS["regular"],
            width=20
        )
        payment_method_menu.grid(row=0, column=1, sticky="w", pady=8, padx=10)
        
        # Payment reference (for UPI/Cheque)
        reference_label = tk.Label(
            form_frame,
            text="Reference Number:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        reference_label.grid(row=1, column=0, sticky="w", pady=8)
        
        reference_var = tk.StringVar()
        reference_entry = tk.Entry(
            form_frame,
            textvariable=reference_var,
            font=FONTS["regular"],
            width=25
        )
        reference_entry.grid(row=1, column=1, sticky="w", pady=8, padx=10)
        
        # Payment date
        date_label = tk.Label(
            form_frame,
            text="Payment Date:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        date_label.grid(row=2, column=0, sticky="w", pady=8)
        
        today = datetime.date.today()
        date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        date_entry = tk.Entry(
            form_frame,
            textvariable=date_var,
            font=FONTS["regular"],
            width=25
        )
        date_entry.grid(row=2, column=1, sticky="w", pady=8, padx=10)
        
        # Payment amount
        amount_label = tk.Label(
            form_frame,
            text="Payment Amount:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        amount_label.grid(row=3, column=0, sticky="w", pady=8)
        
        # Default to full payment
        amount_var = tk.StringVar(value=str(credit_amount))
        amount_entry = tk.Entry(
            form_frame,
            textvariable=amount_var,
            font=FONTS["regular"],
            width=25
        )
        amount_entry.grid(row=3, column=1, sticky="w", pady=8, padx=10)
        
        # Depositor name
        depositor_label = tk.Label(
            form_frame,
            text="Depositor Name:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        depositor_label.grid(row=4, column=0, sticky="w", pady=8)
        
        depositor_var = tk.StringVar()
        depositor_entry = tk.Entry(
            form_frame,
            textvariable=depositor_var,
            font=FONTS["regular"],
            width=25
        )
        depositor_entry.grid(row=4, column=1, sticky="w", pady=8, padx=10)
        
        # Notes
        notes_label = tk.Label(
            form_frame,
            text="Notes:",
            font=FONTS["regular"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        notes_label.grid(row=5, column=0, sticky="nw", pady=8)
        
        notes_entry = tk.Text(
            form_frame,
            font=FONTS["regular"],
            width=25,
            height=3
        )
        notes_entry.grid(row=5, column=1, sticky="w", pady=8, padx=10)
        
        # Buttons frame
        button_frame = tk.Frame(payment_dialog, bg=COLORS["bg_primary"], pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=FONTS["regular"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=20,
            pady=5,
            cursor="hand2",
            command=payment_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Function to process payment
        def process_payment():
            # Validate payment method
            if not payment_method_var.get():
                messagebox.showerror("Error", "Please select a payment method.")
                return
                
            # Validate reference number for UPI/CHEQUE
            if payment_method_var.get() in ["UPI", "CHEQUE"] and not reference_var.get().strip():
                messagebox.showerror("Error", "Reference number is required for UPI/Cheque payments.")
                return
                
            # Validate date
            try:
                payment_date = datetime.datetime.strptime(date_var.get(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                return
                
            # Validate payment amount
            try:
                payment_amount = float(amount_var.get())
                if payment_amount <= 0:
                    messagebox.showerror("Error", "Payment amount must be greater than zero.")
                    return
                if payment_amount > credit_amount:
                    messagebox.showerror("Error", f"Payment amount cannot exceed the outstanding amount of {format_currency(credit_amount)}.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid payment amount. Please enter a valid number.")
                return
                
            # Get depositor name
            depositor_name = depositor_var.get().strip()
            if not depositor_name:
                messagebox.showerror("Error", "Please enter the depositor name.")
                return
                
            # Get notes
            notes = notes_entry.get("1.0", tk.END).strip()
            
            # No need to add depositor to notes anymore since we have a dedicated field
            # We're keeping the notes clean - depositor name is stored in its own column
            
            # Update invoice status
            try:
                # Start a transaction
                self.controller.db.begin()
                
                # Calculate remaining amount after this payment
                remaining_amount = round(credit_amount - payment_amount, 2)
                
                # Determine new payment status based on remaining amount
                new_status = "PAID"
                if remaining_amount > 0:
                    # Use the same status naming convention that was already in the system
                    if payment_status.upper() == "PARTIAL":
                        new_status = "PARTIAL"
                    else:
                        new_status = "PARTIALLY_PAID"
                
                # 1. Update invoice status and credit_amount
                self.controller.db.execute(
                    "UPDATE invoices SET payment_status = ?, credit_amount = ? WHERE id = ?",
                    (new_status, remaining_amount, invoice_id)
                )
                
                # 2. Record the payment in the customer_payments table
                # Check if customer_payments table exists
                table_check = self.controller.db.fetchone(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='customer_payments'"
                )
                
                if not table_check:
                    # Create customer_payments table if it doesn't exist with depositor_name field
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
                
                # Insert payment record with depositor_name field
                self.controller.db.execute(
                    """
                    INSERT INTO customer_payments 
                    (customer_id, invoice_id, amount, payment_method, reference_number, depositor_name, payment_date, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        customer_id, 
                        invoice_id, 
                        payment_amount, 
                        payment_method_var.get(), 
                        reference_var.get(),
                        depositor_name,
                        payment_date.strftime("%Y-%m-%d"), 
                        notes
                    )
                )
                
                # 3. Add entry to customer_transactions table for accounting ledger
                # Insert transaction entry
                self.controller.db.execute(
                    """
                    INSERT INTO customer_transactions
                    (customer_id, amount, transaction_type, reference_id, transaction_date, notes) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        customer_id,
                        payment_amount,  # Amount of payment
                        "CREDIT_PAYMENT",  # Transaction type
                        invoice_id,  # Reference to invoice
                        payment_date.strftime("%Y-%m-%d %H:%M:%S"),
                        f"Payment for Invoice #{invoice_number} via {payment_method_var.get()} by {depositor_name}"
                    )
                )
                
                # Commit transaction
                self.controller.db.commit()
                
                # Generate success message based on payment type
                if new_status == "PAID":
                    success_msg = f"Full payment of {format_currency(payment_amount)} has been recorded. The invoice is now marked as PAID."
                else:
                    success_msg = f"Partial payment of {format_currency(payment_amount)} has been recorded. Remaining amount: {format_currency(remaining_amount)}"
                
                messagebox.showinfo("Payment Recorded", success_msg)
                
                # Close dialog
                payment_dialog.destroy()
                
                # Refresh sales list
                self.load_sales()
                
            except Exception as e:
                # Rollback transaction on error
                self.controller.db.rollback()
                print(f"ERROR: Failed to process payment: {e}")
                messagebox.showerror("Error", f"Failed to process payment: {e}")
        
        # Save button with improved visibility
        save_btn = tk.Button(
            button_frame,
            text="Record Payment",
            font=FONTS["heading"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            padx=20,
            pady=8,
            cursor="hand2",
            command=process_payment
        )
        save_btn.pack(side=tk.RIGHT, padx=20)
            
    def clear_details(self):
        """Clear all detail fields"""
        self.customer_name_label.config(text="Name: -")
        self.customer_phone_label.config(text="Phone: -")
        self.customer_address_label.config(text="Address: -")
        
        self.invoice_number_label.config(text="Number: -")
        self.invoice_date_label.config(text="Date: -")
        self.invoice_amount_label.config(text="Amount: -")
        
        self.payment_method_label.config(text="Method: -")
        self.payment_status_label.config(text="Status: -")
        self.payment_details_label.config(text="")
        
        self.view_btn.config(state=tk.DISABLED)
        self.print_btn.config(state=tk.DISABLED)
        self.collect_payment_btn.config(state=tk.DISABLED)
        
        # Clear items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
    
    def view_invoice(self, event=None):
        """View the selected invoice"""
        selection = self.sales_tree.selection()
        if not selection:
            return
        
        # Get invoice ID from tag
        try:
            invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
            print(f"DEBUG: Viewing invoice with ID: {invoice_id}")
        except (IndexError, ValueError) as e:
            print(f"DEBUG: Error getting invoice ID from selection: {e}")
            messagebox.showerror("Error", "Unable to determine invoice ID. Please try selecting the invoice again.")
            return
        
        # Query to get invoice file path
        query = "SELECT file_path FROM invoices WHERE id = ?"
        result = self.controller.db.fetchone(query, (invoice_id,))
        
        if not result or not result[0]:
            print(f"DEBUG: Invoice file path not found in database for ID: {invoice_id}")
            # Try to regenerate the invoice if the file is missing
            if self.attempt_invoice_regeneration(invoice_id):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if not result or not result[0]:
                    messagebox.showerror("Error", "Invoice PDF file could not be regenerated.")
                    return
            else:
                messagebox.showerror("Error", "Invoice PDF file not found and could not be regenerated.")
                return
        
        file_path = result[0]
        print(f"DEBUG: Original invoice file path: {file_path}")
        
        # Fix absolute paths to use relative paths
        if file_path and (file_path.startswith('C:') or file_path.startswith('/')):
            # Convert absolute path to relative path
            print(f"DEBUG: Converting absolute path to relative")
            file_name = os.path.basename(file_path)
            file_path = os.path.join(".", "invoices", file_name)
            
            # Update the database with the fixed path
            self.controller.db.execute(
                "UPDATE invoices SET file_path = ? WHERE id = ?",
                (file_path, invoice_id)
            )
            self.controller.db.commit()
            print(f"DEBUG: Updated to relative path: {file_path}")
        
        # Ensure invoices directory exists
        invoices_dir = os.path.join(".", "invoices")
        os.makedirs(invoices_dir, exist_ok=True)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"DEBUG: Invoice file does not exist at path: {file_path}")
            
            # Always use PDF format for invoice regeneration to match template exactly
            print(f"DEBUG: Regenerating as PDF to match template exactly")
            
            # Try regenerating the invoice
            regenerated = self.attempt_invoice_regeneration(invoice_id, "pdf")
            
            # If regeneration succeeded, get new path
            if regenerated:
                # Get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if result and result[0]:
                    file_path = result[0]
                    print(f"DEBUG: Regenerated invoice with new path: {file_path}")
                else:
                    messagebox.showerror("Error", "Invoice regenerated but path is missing.")
                    return
            else:
                messagebox.showerror("Error", 
                                  f"Invoice PDF file not found at the expected location:\n{file_path}\n"
                                  "And automatic regeneration failed.")
                return
            
            # Check again if file exists after regeneration
            if not os.path.isfile(file_path):
                messagebox.showerror("Error", 
                                  f"Invoice PDF file still not found after regeneration attempt:\n{file_path}")
                return
        
        try:
            print(f"DEBUG: Attempting to open file: {file_path}")
            # Use the viewer from pdf_invoice_generator
            from utils.pdf_invoice_generator import view_invoice
            if view_invoice(file_path):
                print("DEBUG: Invoice opened successfully")
            else:
                raise Exception("Failed to open invoice file with system viewer")
                
        except Exception as e:
            print(f"DEBUG: Error opening invoice: {e}")
            messagebox.showinfo(
                "File Location", 
                f"The invoice has been saved to:\n{os.path.abspath(file_path)}\n\n"
                "Please open this file to view the invoice."
            )
            
    def get_payment_history(self, invoice_id):
        """
        Payment history is now only shown in Customer Management module's View Purchase History tab
        This method is kept for backward compatibility but always returns None
        """
        # Per user request, payment history should only be shown in Customer Management module
        return None
    
    def attempt_invoice_regeneration(self, invoice_id, output_format="pdf"):
        """
        Attempt to regenerate an invoice file
        
        Args:
            invoice_id: The ID of the invoice to regenerate
            output_format: Always 'pdf' to match shop_bill.pdf template exactly
        """
        print(f"DEBUG: Attempting to regenerate invoice {invoice_id} as {output_format}")
        try:
            # First try to get invoice data from invoices table with detailed field selection
            query = """
                SELECT 
                    i.invoice_number, 
                    i.invoice_date, 
                    i.total_amount,
                    i.payment_method,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.address as customer_address,
                    c.village as customer_village,
                    c.gstin as customer_gstin
                FROM 
                    invoices i
                LEFT JOIN 
                    customers c ON i.customer_id = c.id
                WHERE 
                    i.id = ?
            """
            invoice_data = self.controller.db.fetchone(query, (invoice_id,))
            
            # If not found, try the sales table as a fallback
            using_sales_table = False
            if not invoice_data:
                print(f"DEBUG: Invoice data not found in invoices table for ID: {invoice_id}")
                print(f"DEBUG: Trying to find data in sales table instead")
                
                # More detailed query to get all needed sales data
                sales_query = """
                    SELECT 
                        s.invoice_number, 
                        s.sale_date, 
                        s.total,
                        s.payment_type,
                        c.name as customer_name,
                        c.phone as customer_phone,
                        c.address as customer_address,
                        c.village as customer_village,
                        c.gstin as customer_gstin
                    FROM 
                        sales s
                    LEFT JOIN 
                        customers c ON s.customer_id = c.id
                    WHERE 
                        s.id = ?
                """
                invoice_data = self.controller.db.fetchone(sales_query, (invoice_id,))
                using_sales_table = True
                
                if not invoice_data:
                    print(f"DEBUG: Invoice data not found in sales table either for ID: {invoice_id}")
                    return False
            
            # Check the schema of invoice_items and sale_items to build safe queries
            print("DEBUG: Checking table schemas for invoice items retrieval")
            ii_schema = self.controller.db.fetchall("PRAGMA table_info(invoice_items)")
            si_schema = self.controller.db.fetchall("PRAGMA table_info(sale_items)")
            
            ii_columns = [col[1] for col in ii_schema]
            si_columns = [col[1] for col in si_schema]
            
            print(f"DEBUG: invoice_items columns: {ii_columns}")
            print(f"DEBUG: sale_items columns: {si_columns}")
            
            # Get the invoice items - first try invoice_items table with detailed product info
            # Build query safely based on actual columns
            tax_amount_calc = ""
            if 'tax_amount' in ii_columns:
                tax_amount_calc = "ii.tax_amount as tax_amount"
            else:
                # Calculate tax amount if column doesn't exist
                tax_amount_calc = "(ii.total_price * ii.tax_percentage / 100) as tax_amount"
            
            items_query = f"""
                SELECT 
                    p.name as product_name,
                    p.hsn_code,
                    ii.quantity,
                    ii.price_per_unit as price,
                    ii.discount_percentage as discount,
                    ii.total_price as total,
                    ii.tax_percentage as tax_rate,
                    {tax_amount_calc}
                FROM 
                    invoice_items ii
                LEFT JOIN 
                    products p ON ii.product_id = p.id
                WHERE 
                    ii.invoice_id = ?
            """
            
            try:
                items = self.controller.db.fetchall(items_query, (invoice_id,))
                print(f"DEBUG: Found {len(items) if items else 0} items in invoice_items")
            except Exception as e:
                print(f"DEBUG: Error querying invoice_items: {e}")
                items = []
            
            # If no items found, try sale_items table
            if not items:
                print(f"DEBUG: No items found in invoice_items for ID: {invoice_id}")
                print(f"DEBUG: Trying sale_items table")
                
                # Determine correct discount column name
                discount_col = 'discount_percent'
                if 'discount_percentage' in si_columns:
                    discount_col = 'discount_percentage'
                
                tax_amount_field = ""
                if 'tax_amount' in si_columns:
                    tax_amount_field = "tax_amount"
                else:
                    # Calculate tax amount if column doesn't exist
                    tax_amount_field = "(price * tax_percentage / 100) as tax_amount"
                
                # Determine correct tax rate column
                tax_rate_col = 'tax_percentage'
                if tax_rate_col not in si_columns:
                    tax_rate_col = 'tax_percent'
                
                sale_items_query = f"""
                    SELECT 
                        product_name,
                        hsn_code,
                        quantity,
                        price,
                        {discount_col} as discount,
                        total,
                        {tax_rate_col} as tax_rate,
                        {tax_amount_field}
                    FROM 
                        sale_items
                    WHERE 
                        sale_id = ?
                """
                try:
                    items = self.controller.db.fetchall(sale_items_query, (invoice_id,))
                    print(f"DEBUG: Found {len(items) if items else 0} items in sale_items")
                except Exception as e:
                    print(f"DEBUG: Error querying sale_items: {e}")
                    items = []
            
            if not items:
                print(f"DEBUG: No items found for invoice ID: {invoice_id}")
                return False
                
            # Initialize default values first
            invoice_number = f"INV-{invoice_id}"
            invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            total_amount = 0.0
            payment_method = "CASH"
            customer = {
                "name": "Walk-in Customer",
                "phone": "",
                "address": "",
                "village": "",
                "gstin": ""
            }
            
            # Initialize payment status
            payment_status = "PAID"  # Default if not found
            
            # Try to extract values from invoice_data
            try:
                if invoice_data and len(invoice_data) > 0:
                    invoice_number = invoice_data[0] if invoice_data[0] else f"INV-{invoice_id}"
                    
                    if len(invoice_data) > 1:
                        invoice_date = invoice_data[1] if invoice_data[1] else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                    if len(invoice_data) > 2 and invoice_data[2] is not None:
                        total_amount = float(invoice_data[2])
                        
                    if len(invoice_data) > 3:
                        payment_method = invoice_data[3] if invoice_data[3] else "CASH"
                    
                    # Get payment status if available
                    if len(invoice_data) > 6 and invoice_data[6]:
                        payment_status = invoice_data[6]
                    
                    # More detailed customer information
                    if len(invoice_data) > 4:
                        customer = {
                            "name": invoice_data[4] or "Walk-in Customer",
                            "phone": invoice_data[5] if len(invoice_data) > 5 and invoice_data[5] else "",
                            "address": invoice_data[6] if len(invoice_data) > 6 and invoice_data[6] else "",
                            "village": invoice_data[7] if len(invoice_data) > 7 and invoice_data[7] else "",
                            "gstin": invoice_data[8] if len(invoice_data) > 8 and invoice_data[8] else ""
                        }
                
                print(f"DEBUG: Extracted invoice data - Number: {invoice_number}, Date: {invoice_date}, Total: {total_amount}")
                print(f"DEBUG: Customer: {customer['name']}, Phone: {customer['phone']}")
            except (IndexError, TypeError, ValueError) as e:
                print(f"DEBUG: Error extracting invoice details: {e}")
                # We already set default values above, so no need to handle missing values here
            
            # Format the items with better error handling
            formatted_items = []
            subtotal = 0.0
            tax_total = 0.0
            
            for item in items:
                try:
                    # Get values with default fallbacks
                    name = item[0] if item[0] else "Unknown Product"
                    hsn_code = item[1] if len(item) > 1 and item[1] else ""
                    quantity = float(item[2]) if len(item) > 2 and item[2] is not None else 0
                    price = float(item[3]) if len(item) > 3 and item[3] is not None else 0
                    discount = float(item[4]) if len(item) > 4 and item[4] is not None else 0
                    total = float(item[5]) if len(item) > 5 and item[5] is not None else 0
                    tax_rate = float(item[6]) if len(item) > 6 and item[6] is not None else 0
                    tax_amount = float(item[7]) if len(item) > 7 and item[7] is not None else 0
                    
                    # Build the item dictionary with all available information
                    item_dict = {
                        "name": name,
                        "hsn_code": hsn_code,
                        "quantity": quantity,
                        "price": price,
                        "discount": discount,
                        "total": total,
                        "tax_rate": tax_rate,
                        "tax_amount": tax_amount
                    }
                    
                    formatted_items.append(item_dict)
                    subtotal += (price * quantity)
                    tax_total += tax_amount
                    
                    print(f"DEBUG: Added invoice item: {name}, Qty: {quantity}, Price: {price}, Total: {total}")
                except (IndexError, TypeError, ValueError) as e:
                    print(f"DEBUG: Error processing invoice item: {e}, item data: {item}")
                    # Continue with other items
            
            # Safety check - if no items were processed successfully, return false
            if not formatted_items:
                print("DEBUG: No items could be processed successfully")
                return False
                
            # Import the specialized PDF invoice generator
            from utils.pdf_invoice_generator import generate_invoice
            
            # Get shop information from settings
            store_info = {}
            try:
                settings_query = "SELECT key, value FROM settings WHERE key IN ('store_name', 'store_address', 'store_phone', 'store_gstin', 'store_email', 'invoice_prefix')"
                settings = self.controller.db.fetchall(settings_query)
                
                for key, value in settings:
                    if key == 'invoice_prefix':
                        # Store invoice prefix separately
                        invoice_prefix = value
                    else:
                        # Convert settings key to store_info format (remove 'store_' prefix)
                        clean_key = key.replace('store_', '')
                        store_info[clean_key] = value
                
                print(f"DEBUG: Retrieved store info from settings: {store_info}")
            except Exception as e:
                print(f"DEBUG: Error retrieving store info from settings: {e}")
                # Set defaults if settings retrieval fails
                store_info = {
                    'name': 'Agritech Products Shop',
                    'address': 'Main Road, Maharashtra',
                    'phone': '+91 1234567890',
                    'gstin': '27AABCU9603R1ZX'
                }
            
            # Format invoice data as expected by the generator
            # Payment history is no longer shown on invoices per user request
            invoice_data_dict = {
                'invoice_number': invoice_number,
                'date': invoice_date,
                'customer_name': customer['name'],
                'customer_phone': customer['phone'],
                'customer_address': customer['address'],
                'customer_village': customer.get('village', ''),
                'customer_gstin': customer.get('gstin', ''),
                'items': formatted_items,
                'payment': {
                    'method': payment_method,
                    'subtotal': subtotal,
                    'tax_total': tax_total,
                    'total': total_amount,
                    'status': payment_status,  # Use actual payment status
                    'payment_history': None  # No payment history on invoices per user request
                },
                'store_info': store_info   # Add shop information
            }
            
            # Create invoices directory if it doesn't exist - use relative path
            invoices_dir = os.path.join('.', 'invoices')
            if not os.path.exists(invoices_dir):
                os.makedirs(invoices_dir)
                
            # Generate path for the new invoice file - using relative path
            # Clean the invoice number to make a valid filename
            safe_invoice_number = invoice_number.replace('/', '-').replace('\\', '-').replace(':', '-')
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Always use PDF format for exact template matching
            # Get invoice prefix from the number (format like "24-25/ABC-001")
            original_invoice_parts = invoice_number.split('/')
            if len(original_invoice_parts) > 1:
                # Extract prefix from original invoice number (e.g., "ABC" from "24-25/ABC-001")
                prefix_part = original_invoice_parts[1].split('-')[0]
            else:
                # Fallback to invoice prefix from settings
                settings_row = self.controller.db.fetchone("SELECT value FROM settings WHERE key = 'invoice_prefix'")
                prefix_part = settings_row[0] if settings_row and settings_row[0] else "INV"
                
            invoice_filename = f"{prefix_part}_{safe_invoice_number}_{timestamp}.pdf"
            file_path = os.path.join(invoices_dir, invoice_filename)
            
            # Debug output
            print(f"DEBUG: Creating regenerated invoice as {output_format} at: {os.path.abspath(file_path)}")
            print(f"DEBUG: Invoice data: {invoice_data_dict}")
            
            # Generate the new invoice file with exact template match
            success = generate_invoice(invoice_data_dict, file_path)
            
            if success and os.path.exists(file_path):
                print(f"DEBUG: Invoice file created successfully at: {file_path}")
                
                # Check if this invoice exists in the invoices table
                check_query = "SELECT id FROM invoices WHERE id = ?"
                invoice_exists = self.controller.db.fetchone(check_query, (invoice_id,))
                
                if invoice_exists:
                    # Update existing invoice record with the new file path
                    update_query = "UPDATE invoices SET file_path = ? WHERE id = ?"
                    self.controller.db.execute(update_query, (file_path, invoice_id))
                    print(f"DEBUG: Updated existing invoice record with new file path")
                elif using_sales_table:
                    # This was a sales record that doesn't have a corresponding invoices record
                    # Get the invoice details from the sales table
                    sales_details = self.controller.db.fetchone("""
                        SELECT invoice_number, customer_id, subtotal, discount, tax, total, payment_type
                        FROM sales WHERE id = ?
                    """, (invoice_id,))
                    
                    if sales_details:
                        # Create a new entry in the invoices table
                        try:
                            self.controller.db.execute("""
                                INSERT INTO invoices
                                (id, invoice_number, customer_id, subtotal, tax_amount, total_amount, 
                                 payment_method, payment_status, file_path, invoice_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, 'PAID', ?, CURRENT_TIMESTAMP)
                            """, (
                                invoice_id,  # Use the same ID as the sales record
                                sales_details[0],  # invoice_number
                                sales_details[1],  # customer_id
                                sales_details[2],  # subtotal
                                sales_details[4],  # tax
                                sales_details[5],  # total
                                sales_details[6],  # payment_type/method
                                file_path
                            ))
                            print(f"DEBUG: Created new invoice record in invoices table from sales record")
                        except Exception as e:
                            print(f"DEBUG: Error creating invoice record: {e}")
                            # Even if the database insert fails, we still generated the invoice file
                
                self.controller.db.commit()
                print(f"DEBUG: Invoice regeneration process completed successfully")
                return True
            else:
                print(f"DEBUG: Invoice regeneration failed - generate_invoice returned {success}")
                return False
                
        except Exception as e:
            print(f"DEBUG: Error regenerating invoice: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_invoice(self):
        """Print the selected invoice"""
        selection = self.sales_tree.selection()
        if not selection:
            return
        
        # Get invoice ID from tag
        try:
            invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
            print(f"DEBUG: Printing invoice with ID: {invoice_id}")
        except (IndexError, ValueError) as e:
            print(f"DEBUG: Error getting invoice ID from selection: {e}")
            messagebox.showerror("Error", "Unable to determine invoice ID. Please try selecting the invoice again.")
            return
        
        # Query to get invoice file path
        query = "SELECT file_path FROM invoices WHERE id = ?"
        result = self.controller.db.fetchone(query, (invoice_id,))
        
        if not result or not result[0]:
            print(f"DEBUG: Invoice file path not found in database for ID: {invoice_id}")
            # Always regenerate as PDF for printing
            if self.attempt_invoice_regeneration(invoice_id, "pdf"):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if not result or not result[0]:
                    messagebox.showerror("Error", "Invoice file could not be regenerated.")
                    return
            else:
                messagebox.showerror("Error", "Invoice file not found and could not be regenerated.")
                return
        
        file_path = result[0]
        print(f"DEBUG: Invoice file path: {file_path}")
        
        # Verify that invoice file exists, otherwise regenerate it
        if not file_path or not os.path.isfile(file_path):
            print(f"DEBUG: Invoice file not found, attempting to regenerate")
            if self.attempt_invoice_regeneration(invoice_id, "pdf"):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if result and result[0] and os.path.isfile(result[0]):
                    file_path = result[0]
                else:
                    messagebox.showinfo(
                        "Missing Invoice", 
                        "The invoice file could not be found or regenerated.\n"
                        "Please try again or contact support."
                    )
            else:
                messagebox.showinfo(
                    "Invoice Error", 
                    "The invoice file could not be regenerated.\n"
                    "Please try again or contact support."
                )
        
        # Check if file exists
        if not os.path.isfile(file_path):
            print(f"DEBUG: Invoice file does not exist at path: {file_path}")
            # Always regenerate as PDF for printing
            if self.attempt_invoice_regeneration(invoice_id, "pdf"):
                # If regeneration succeeded, get the new path
                result = self.controller.db.fetchone(query, (invoice_id,))
                if result and result[0] and os.path.isfile(result[0]):
                    file_path = result[0]
                else:
                    messagebox.showerror("Error", "Invoice file could not be regenerated.")
                    return
            else:
                messagebox.showerror("Error", "Invoice file not found and could not be regenerated.")
                return
        
        try:
            print(f"DEBUG: Attempting to print file: {file_path}")
            import platform
            
            # All invoice files should be PDF format now
            is_pdf = True
            file_type = "PDF"
            
            if platform.system() == 'Windows':
                # On Windows, open the file with the print operation or use default viewer
                messagebox.showinfo(
                    "Print Invoice", 
                    f"Please use the {file_type} viewer's print dialog to print the invoice.\n\n"
                    "The invoice will now open for printing."
                )
                # Use subprocess to open for printing - more compatible than startfile
                try:
                    # Try to use default print command for PDFs
                    subprocess.call(['rundll32.exe', 'shell32.dll,ShellExec_RunDLL', 'print', file_path])
                except Exception as print_err:
                    print(f"DEBUG: Error using direct print command: {print_err}")
                    # Fall back to just opening the file
                    subprocess.call(['start', '', file_path], shell=True)
                print("DEBUG: Print command sent to Windows")
            else:
                # On Unix-like systems
                print("DEBUG: Attempting to print on Unix-like system")
                try:
                    # Try using lpr for printing PDFs
                    subprocess.call(['lpr', file_path])
                    messagebox.showinfo("Print Invoice", "Invoice has been sent to the default printer.")
                except Exception as print_err:
                    print(f"DEBUG: Error printing with lpr: {print_err}")
                    # Fall back to opening the file
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', file_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', file_path])
                    messagebox.showinfo(
                        "Manual Printing Required", 
                        "Automated printing is not available.\n\n"
                        "The file has been opened. Please use the application's print function."
                    )
                print("DEBUG: Print command completed")
        except Exception as e:
            print(f"DEBUG: Error printing invoice: {e}")
            messagebox.showinfo(
                "Manual Printing Required", 
                "Automated printing is not available.\n\n"
                "Please open the file and print it manually."
            )
            self.view_invoice()
    
    def show_context_menu(self, event):
        """Show context menu for invoice list"""
        selection = self.sales_tree.selection()
        if not selection:
            return
        
        # Get invoice ID from tag
        try:
            invoice_id = int(self.sales_tree.item(selection[0], "tags")[0])
        except (IndexError, ValueError):
            return
        
        # Query to check if invoice has a file path
        query = "SELECT file_path FROM invoices WHERE id = ?"
        result = self.controller.db.fetchone(query, (invoice_id,))
        
        has_file = result and result[0] and os.path.isfile(result[0])
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Add menu items
        context_menu.add_command(label="View Details", command=self.on_invoice_select)
        
        # Always add view and print options, they will attempt regeneration if needed
        context_menu.add_command(label="View Invoice", command=self.view_invoice)
        context_menu.add_command(label="Print Invoice", command=self.print_invoice)
        
        # Add regenerate option
        context_menu.add_separator()
        context_menu.add_command(
            label="Regenerate Invoice", 
            command=lambda: self.regenerate_invoice_from_menu(invoice_id, "pdf")
        )
        
        # Display the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def regenerate_invoice_from_menu(self, invoice_id, output_format="pdf"):
        """
        Explicitly regenerate an invoice from the context menu
        
        Args:
            invoice_id: ID of the invoice to regenerate
            output_format: Always 'pdf' to match shop_bill.pdf template exactly
        """
        if self.attempt_invoice_regeneration(invoice_id, "pdf"):
            messagebox.showinfo(
                "Success", 
                "Invoice has been regenerated successfully.\n"
                "You can now view or access the invoice."
            )
            # Update the selection to refresh buttons
            self.on_invoice_select()
        else:
            messagebox.showerror(
                "Error", 
                "Failed to regenerate the invoice.\n"
                "Please check the application logs for more details."
            )
    
    def on_show(self):
        """Called when frame is shown"""
        # Load today's sales by default
        self.select_today()