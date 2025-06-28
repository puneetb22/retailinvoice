"""
Reports UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import pandas as pd
import os
import sys
import traceback

# Import matplotlib with error handling
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    matplotlib_available = True
except ImportError:
    matplotlib_available = False
    print("WARNING: Matplotlib not available. Charts will be disabled.")

from assets.styles import COLORS, FONTS, STYLES
from utils.export import export_to_excel

class ReportsFrame(tk.Frame):
    """Reports frame for viewing sales analytics and generating reports"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
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
        self.sales_summary_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.sales_by_product_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.payment_methods_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.tax_report_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.inventory_report_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        
        self.notebook.add(self.sales_summary_tab, text="Sales Summary")
        self.notebook.add(self.sales_by_product_tab, text="Sales by Product")
        self.notebook.add(self.payment_methods_tab, text="Payment Methods")
        self.notebook.add(self.tax_report_tab, text="Tax Report")
        self.notebook.add(self.inventory_report_tab, text="Inventory Report")
        
        # Setup tabs
        self.setup_sales_summary_tab()
        self.setup_sales_by_product_tab()
        self.setup_payment_methods_tab()
        self.setup_tax_report_tab()
        self.setup_inventory_report_tab()
    
    def setup_sales_summary_tab(self):
        """Setup the sales summary tab"""
        # Main container with two frames side by side
        main_container = tk.Frame(self.sales_summary_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)  # Don't shrink
        
        # Right panel - Charts and data
        right_panel = tk.Frame(main_container, bg=COLORS["bg_white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Setup left panel controls
        self.setup_sales_summary_controls(left_panel)
        
        # Setup right panel with charts container
        self.sales_summary_charts_frame = tk.Frame(right_panel, bg=COLORS["bg_white"])
        self.sales_summary_charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Load default data
        self.load_sales_summary()
    
    def setup_sales_summary_controls(self, parent):
        """Setup controls for sales summary tab"""
        # Title
        title = tk.Label(parent, 
                        text="Report Options",
                        font=FONTS["subheading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=(20, 10))
        
        # Date range frame
        date_frame = tk.LabelFrame(parent, 
                                 text="Date Range",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range options
        date_ranges = [
            "Today", 
            "Yesterday", 
            "This Week", 
            "Last Week", 
            "This Month", 
            "Last Month", 
            "This Year", 
            "Custom Range"
        ]
        
        # Create radio buttons for date ranges
        self.sales_date_range_var = tk.StringVar(value="This Month")
        
        for i, date_range in enumerate(date_ranges):
            rb = tk.Radiobutton(date_frame, 
                              text=date_range,
                              variable=self.sales_date_range_var,
                              value=date_range,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.toggle_custom_date_range)
            rb.pack(anchor="w", padx=10, pady=2)
        
        # Custom date range frame
        self.custom_date_frame = tk.Frame(parent, bg=COLORS["bg_primary"], padx=10)
        
        # Start date
        start_label = tk.Label(self.custom_date_frame, 
                             text="Start Date (YYYY-MM-DD):",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        start_label.pack(anchor="w", pady=(10, 5))
        
        self.start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(self.custom_date_frame, 
                                  textvariable=self.start_date_var,
                                  font=FONTS["regular"],
                                  width=15)
        start_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # End date
        end_label = tk.Label(self.custom_date_frame, 
                           text="End Date (YYYY-MM-DD):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        end_label.pack(anchor="w", pady=(0, 5))
        
        self.end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(self.custom_date_frame, 
                                textvariable=self.end_date_var,
                                font=FONTS["regular"],
                                width=15)
        end_date_entry.pack(fill=tk.X)
        
        # Initial state - hide custom date frame
        self.toggle_custom_date_range()
        
        # Generate report button using theme properties
        generate_btn = tk.Button(parent,
                               text="Generate Report",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               activebackground=COLORS["primary_light"],
                               activeforeground=COLORS["text_white"],
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.load_sales_summary)
        generate_btn.pack(padx=10, pady=15)
        
        # Export button using theme properties
        export_btn = tk.Button(parent,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             activebackground=COLORS["secondary_dark"],
                             activeforeground=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.export_sales_summary)
        export_btn.pack(padx=10, pady=5)
    
    def toggle_custom_date_range(self):
        """Show/hide custom date range inputs based on selection"""
        if self.sales_date_range_var.get() == "Custom Range":
            # Set default date range (last 30 days)
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            self.start_date_var.set(thirty_days_ago.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            
            # Show custom date frame
            self.custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            # Hide custom date frame
            self.custom_date_frame.pack_forget()
    
    def get_date_range(self):
        """Get start and end dates based on selected range"""
        date_range = self.sales_date_range_var.get()
        today = datetime.date.today()
        
        if date_range == "Today":
            return today, today
        
        elif date_range == "Yesterday":
            yesterday = today - datetime.timedelta(days=1)
            return yesterday, yesterday
        
        elif date_range == "This Week":
            start_of_week = today - datetime.timedelta(days=today.weekday())
            return start_of_week, today
        
        elif date_range == "Last Week":
            end_of_last_week = today - datetime.timedelta(days=today.weekday() + 1)
            start_of_last_week = end_of_last_week - datetime.timedelta(days=6)
            return start_of_last_week, end_of_last_week
        
        elif date_range == "This Month":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        
        elif date_range == "Last Month":
            end_of_last_month = today.replace(day=1) - datetime.timedelta(days=1)
            start_of_last_month = end_of_last_month.replace(day=1)
            return start_of_last_month, end_of_last_month
        
        elif date_range == "This Year":
            start_of_year = today.replace(month=1, day=1)
            return start_of_year, today
        
        elif date_range == "Custom Range":
            try:
                start_date = datetime.datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date()
                
                # Validate dates
                if start_date > end_date:
                    messagebox.showerror("Date Error", "Start date cannot be after end date.")
                    raise ValueError("Invalid date range")
                
                return start_date, end_date
                
            except ValueError as e:
                if "Invalid date range" not in str(e):
                    messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
                # Default to this month on error
                start_of_month = today.replace(day=1)
                return start_of_month, today
        
        # Default fallback
        return today - datetime.timedelta(days=30), today
    
    def load_sales_summary(self):
        """Load and display sales summary data"""
        # Get date range
        start_date, end_date = self.get_date_range()
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing charts
        for widget in self.sales_summary_charts_frame.winfo_children():
            widget.destroy()
        
        # Get sales data
        query = """
            SELECT 
                DATE(invoice_date) as sale_date,
                COUNT(*) as num_invoices,
                SUM(total_amount) as total_sales,
                SUM(discount_amount) as total_discount,
                SUM(tax_amount) as total_tax
            FROM invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
            GROUP BY DATE(invoice_date)
            ORDER BY sale_date
        """
        sales_data = self.controller.db.fetchall(query, (start_date_str, end_date_str))
        
        if not sales_data:
            # No data for selected range
            no_data_label = tk.Label(self.sales_summary_charts_frame,
                                   text="No sales data available for the selected date range.",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_white"],
                                   fg=COLORS["text_secondary"])
            no_data_label.pack(expand=True)
            return
        
        # Convert to pandas DataFrame for easier manipulation
        columns = ["Date", "Invoices", "Total Sales", "Discount", "Tax"]
        df = pd.DataFrame(sales_data, columns=columns)
        
        # Store for export
        self.sales_summary_df = df
        
        # Calculate summary metrics
        total_sales = df["Total Sales"].sum()
        total_invoices = df["Invoices"].sum()
        avg_sale = total_sales / total_invoices if total_invoices > 0 else 0
        total_discount = df["Discount"].sum()
        total_tax = df["Tax"].sum()
        
        # Create summary frame
        summary_frame = tk.Frame(self.sales_summary_charts_frame, bg=COLORS["bg_white"], padx=20, pady=10)
        summary_frame.pack(fill=tk.X)
        
        # Add summary labels
        metrics = [
            {"label": "Total Sales:", "value": f"₹{total_sales:.2f}"},
            {"label": "Invoices:", "value": str(int(total_invoices))},
            {"label": "Average Sale:", "value": f"₹{avg_sale:.2f}"},
            {"label": "Total Discount:", "value": f"₹{total_discount:.2f}"},
            {"label": "Total Tax:", "value": f"₹{total_tax:.2f}"}
        ]
        
        for i, metric in enumerate(metrics):
            tk.Label(summary_frame, 
                   text=metric["label"],
                   font=FONTS["regular_bold"],
                   bg=COLORS["bg_white"],
                   fg=COLORS["text_primary"]).grid(row=i//3, column=(i%3)*2, sticky="w", padx=10, pady=5)
            
            tk.Label(summary_frame, 
                   text=metric["value"],
                   font=FONTS["regular"],
                   bg=COLORS["bg_white"],
                   fg=COLORS["text_primary"]).grid(row=i//3, column=(i%3)*2+1, sticky="w", padx=10, pady=5)
        
        # Create charts
        charts_container = tk.Frame(self.sales_summary_charts_frame, bg=COLORS["bg_white"])
        charts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sales chart
        self.create_sales_chart(charts_container, df)
    
    def create_sales_chart(self, parent, df):
        """Create a sales chart using matplotlib"""
        try:
            # Check if matplotlib is available
            if not matplotlib_available:
                self.show_chart_alternative(parent, df)
                return
                
            # Check if dataframe is empty or has only one row
            if df.empty or len(df) < 2:
                self.show_chart_alternative(parent, df, message="Not enough data for chart visualization")
                return
                
            # Create figure
            fig = Figure(figsize=(10, 5), dpi=100)
            ax = fig.add_subplot(111)
            
            # Plot data
            ax.plot(df["Date"], df["Total Sales"], marker='o', linestyle='-', linewidth=2, color='#4e73df')
            
            # Set labels and title
            ax.set_xlabel('Date')
            ax.set_ylabel('Sales Amount (₹)')
            ax.set_title('Daily Sales')
            
            # Rotate x-axis labels for better readability
            fig.autofmt_xdate()
            
            # Tight layout
            fig.tight_layout()
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"ERROR creating sales chart: {e}")
            traceback.print_exc()
            self.show_chart_alternative(parent, df, message=f"Error creating chart: {str(e)}")
            
    def show_chart_alternative(self, parent, df, message="Chart visualization not available"):
        """Show alternative to matplotlib chart when it's not available"""
        # Create a frame for the alternative display
        alt_frame = tk.Frame(parent, bg=COLORS["bg_white"], bd=1, relief=tk.SUNKEN)
        alt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add message about chart unavailability
        tk.Label(
            alt_frame,
            text=message,
            font=FONTS["regular_bold"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_white"],
            pady=20
        ).pack()
        
        # If we have data, show it in a table format instead
        if not df.empty:
            # Create a table header
            header_frame = tk.Frame(alt_frame, bg=COLORS["bg_white"])
            header_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
            
            # Add column headers
            for i, col in enumerate(["Date", "Sales Amount (₹)"]):
                tk.Label(
                    header_frame,
                    text=col,
                    font=FONTS["regular_bold"],
                    fg=COLORS["text_primary"],
                    bg=COLORS["bg_secondary"],
                    width=25 if i == 0 else 15,
                    padx=10,
                    pady=5
                ).grid(row=0, column=i, sticky="ew")
            
            # Add data rows (show up to 10 rows to keep it manageable)
            data_frame = tk.Frame(alt_frame, bg=COLORS["bg_white"])
            data_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
            
            max_rows = min(10, len(df))
            for i in range(max_rows):
                # Alternate row colors for better readability
                bg_color = COLORS["bg_white"] if i % 2 == 0 else "#f8f9fc"
                
                tk.Label(
                    data_frame,
                    text=str(df["Date"].iloc[i]),
                    font=FONTS["regular"],
                    fg=COLORS["text_primary"],
                    bg=bg_color,
                    width=25,
                    padx=10,
                    pady=5,
                    anchor="w"
                ).grid(row=i, column=0, sticky="ew")
                
                tk.Label(
                    data_frame,
                    text=f"₹{df['Total Sales'].iloc[i]:.2f}",
                    font=FONTS["regular"],
                    fg=COLORS["text_primary"],
                    bg=bg_color,
                    width=15,
                    padx=10,
                    pady=5,
                    anchor="e"
                ).grid(row=i, column=1, sticky="ew")
            
            # If there are more rows than we're showing, add a note
            if len(df) > max_rows:
                tk.Label(
                    alt_frame,
                    text=f"Showing {max_rows} of {len(df)} rows. Use Export to Excel for complete data.",
                    font=FONTS["regular_italic"],
                    fg=COLORS["text_secondary"],
                    bg=COLORS["bg_white"],
                    pady=5
                ).pack()
    
    def export_sales_summary(self):
        """Export sales summary data to Excel"""
        if not hasattr(self, 'sales_summary_df') or self.sales_summary_df.empty:
            messagebox.showinfo("Export", "No data available to export.")
            return
        
        # Get date range for filename
        start_date, end_date = self.get_date_range()
        filename = f"Sales_Summary_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return  # User cancelled
        
        # Export the data
        try:
            # Create a writer and export the DataFrame
            export_to_excel(self.sales_summary_df, file_path, sheet_name="Sales Summary")
            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def setup_sales_by_product_tab(self):
        """Setup the sales by product tab"""
        # Main container with two frames side by side
        main_container = tk.Frame(self.sales_by_product_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)  # Don't shrink
        
        # Right panel - Data
        right_panel = tk.Frame(main_container, bg=COLORS["bg_white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Setup left panel controls
        # Reuse similar controls as sales summary
        self.setup_product_sales_controls(left_panel)
        
        # Setup right panel with data table
        self.product_sales_frame = tk.Frame(right_panel, bg=COLORS["bg_white"])
        self.product_sales_frame.pack(fill=tk.BOTH, expand=True)
        
        # Load default data
        self.load_sales_by_product()
    
    def setup_product_sales_controls(self, parent):
        """Setup controls for product sales tab"""
        # Title
        title = tk.Label(parent, 
                        text="Report Options",
                        font=FONTS["subheading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=(20, 10))
        
        # Date range frame
        date_frame = tk.LabelFrame(parent, 
                                 text="Date Range",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range options
        date_ranges = [
            "Today", 
            "This Week", 
            "This Month", 
            "Last Month", 
            "This Year", 
            "Custom Range"
        ]
        
        # Create radio buttons for date ranges
        self.product_date_range_var = tk.StringVar(value="This Month")
        
        for i, date_range in enumerate(date_ranges):
            rb = tk.Radiobutton(date_frame, 
                              text=date_range,
                              variable=self.product_date_range_var,
                              value=date_range,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.toggle_product_custom_date_range)
            rb.pack(anchor="w", padx=10, pady=2)
        
        # Custom date range frame
        self.product_custom_date_frame = tk.Frame(parent, bg=COLORS["bg_primary"], padx=10)
        
        # Start date
        start_label = tk.Label(self.product_custom_date_frame, 
                             text="Start Date (YYYY-MM-DD):",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        start_label.pack(anchor="w", pady=(10, 5))
        
        self.product_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(self.product_custom_date_frame, 
                                  textvariable=self.product_start_date_var,
                                  font=FONTS["regular"],
                                  width=15)
        start_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # End date
        end_label = tk.Label(self.product_custom_date_frame, 
                           text="End Date (YYYY-MM-DD):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        end_label.pack(anchor="w", pady=(0, 5))
        
        self.product_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(self.product_custom_date_frame, 
                                textvariable=self.product_end_date_var,
                                font=FONTS["regular"],
                                width=15)
        end_date_entry.pack(fill=tk.X)
        
        # Sort by frame
        sort_frame = tk.LabelFrame(parent, 
                                 text="Sort By",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        sort_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Sort options
        sort_options = [
            "Quantity (High to Low)", 
            "Amount (High to Low)", 
            "Product Name (A to Z)"
        ]
        
        # Create radio buttons for sort options
        self.sort_by_var = tk.StringVar(value="Amount (High to Low)")
        
        for i, option in enumerate(sort_options):
            rb = tk.Radiobutton(sort_frame, 
                              text=option,
                              variable=self.sort_by_var,
                              value=option,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"])
            rb.pack(anchor="w", padx=10, pady=2)
        
        # Initial state - hide custom date frame
        self.toggle_product_custom_date_range()
        
        # Generate report button
        generate_btn = tk.Button(parent,
                               text="Generate Report",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.load_sales_by_product)
        generate_btn.pack(padx=10, pady=15)
        
        # Export button
        export_btn = tk.Button(parent,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.export_product_sales)
        export_btn.pack(padx=10, pady=5)
    
    def toggle_product_custom_date_range(self):
        """Show/hide custom date range inputs for product sales"""
        if self.product_date_range_var.get() == "Custom Range":
            # Set default date range (last 30 days)
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            self.product_start_date_var.set(thirty_days_ago.strftime("%Y-%m-%d"))
            self.product_end_date_var.set(today.strftime("%Y-%m-%d"))
            
            # Show custom date frame
            self.product_custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            # Hide custom date frame
            self.product_custom_date_frame.pack_forget()
    
    def get_product_date_range(self):
        """Get start and end dates for product sales report"""
        date_range = self.product_date_range_var.get()
        today = datetime.date.today()
        
        if date_range == "Today":
            return today, today
        
        elif date_range == "This Week":
            start_of_week = today - datetime.timedelta(days=today.weekday())
            return start_of_week, today
        
        elif date_range == "This Month":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        
        elif date_range == "Last Month":
            end_of_last_month = today.replace(day=1) - datetime.timedelta(days=1)
            start_of_last_month = end_of_last_month.replace(day=1)
            return start_of_last_month, end_of_last_month
        
        elif date_range == "This Year":
            start_of_year = today.replace(month=1, day=1)
            return start_of_year, today
        
        elif date_range == "Custom Range":
            try:
                start_date = datetime.datetime.strptime(self.product_start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.product_end_date_var.get(), "%Y-%m-%d").date()
                
                # Validate dates
                if start_date > end_date:
                    messagebox.showerror("Date Error", "Start date cannot be after end date.")
                    raise ValueError("Invalid date range")
                
                return start_date, end_date
                
            except ValueError as e:
                if "Invalid date range" not in str(e):
                    messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
                # Default to this month on error
                start_of_month = today.replace(day=1)
                return start_of_month, today
        
        # Default fallback
        return today - datetime.timedelta(days=30), today
    
    def load_sales_by_product(self):
        """Load and display sales by product data"""
        # Get date range
        start_date, end_date = self.get_product_date_range()
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing content
        for widget in self.product_sales_frame.winfo_children():
            widget.destroy()
        
        # Get sorting option
        sort_option = self.sort_by_var.get()
        
        # Define sort field and direction
        sort_clause = ""
        if sort_option == "Quantity (High to Low)":
            sort_clause = "ORDER BY total_quantity DESC"
        elif sort_option == "Amount (High to Low)":
            sort_clause = "ORDER BY total_amount DESC"
        else:  # Product Name (A to Z)
            sort_clause = "ORDER BY product_name ASC"
        
        # Query for product sales
        query = f"""
            SELECT 
                p.id as product_id,
                p.name as product_name,
                p.category,
                SUM(ii.quantity) as total_quantity,
                SUM(ii.total_price) as total_amount,
                AVG(ii.price_per_unit) as avg_price
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            LEFT JOIN products p ON ii.product_id = p.id
            WHERE DATE(i.invoice_date) BETWEEN ? AND ?
            GROUP BY p.id, p.name, p.category
            {sort_clause}
        """
        
        product_sales = self.controller.db.fetchall(query, (start_date_str, end_date_str))
        
        if not product_sales:
            # No data for selected range
            no_data_label = tk.Label(self.product_sales_frame,
                                   text="No sales data available for the selected date range.",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_white"],
                                   fg=COLORS["text_secondary"])
            no_data_label.pack(expand=True)
            return
        
        # Convert to pandas DataFrame for easier manipulation
        columns = ["Product ID", "Product Name", "Category", "Quantity Sold", "Total Amount", "Average Price"]
        df = pd.DataFrame(product_sales, columns=columns)
        
        # Store for export
        self.product_sales_df = df
        
        # Create TreeView for product sales data
        tree_frame = tk.Frame(self.product_sales_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure treeview
        product_tree = ttk.Treeview(tree_frame, 
                                  columns=("Rank", "Product", "Category", "Qty", "Amount", "Avg Price"),
                                  show="headings",
                                  yscrollcommand=scrollbar.set)
        
        # Set scrollbar command
        scrollbar.config(command=product_tree.yview)
        
        # Define columns
        product_tree.heading("Rank", text="#")
        product_tree.heading("Product", text="Product Name")
        product_tree.heading("Category", text="Category")
        product_tree.heading("Qty", text="Qty Sold")
        product_tree.heading("Amount", text="Total Amount")
        product_tree.heading("Avg Price", text="Avg Price")
        
        # Set column widths
        product_tree.column("Rank", width=50, anchor="center")
        product_tree.column("Product", width=250)
        product_tree.column("Category", width=100)
        product_tree.column("Qty", width=100, anchor="e")
        product_tree.column("Amount", width=120, anchor="e")
        product_tree.column("Avg Price", width=120, anchor="e")
        
        product_tree.pack(fill=tk.BOTH, expand=True)
        
        # Insert data into tree
        for i, row in enumerate(product_sales, 1):
            product_id, name, category, quantity, amount, avg_price = row
            
            # Format display values
            if name is None:
                name = "Custom Item"
            
            if category is None:
                category = ""
                
            # Insert row
            product_tree.insert("", "end", values=(
                i,  # Rank
                name,
                category,
                int(quantity),
                f"₹{amount:.2f}",
                f"₹{avg_price:.2f}"
            ))
        
        # Add summary row at the top (bold)
        total_quantity = sum(row[3] for row in product_sales)
        total_amount = sum(row[4] for row in product_sales)
        
        product_tree.insert("", 0, values=(
            "",
            "TOTAL",
            "",
            int(total_quantity),
            f"₹{total_amount:.2f}",
            ""
        ), tags=('total',))
        
        # Configure tag for total row
        product_tree.tag_configure('total', font=FONTS["regular_bold"])
    
    def export_product_sales(self):
        """Export product sales data to Excel"""
        if not hasattr(self, 'product_sales_df') or self.product_sales_df.empty:
            messagebox.showinfo("Export", "No data available to export.")
            return
        
        # Get date range for filename
        start_date, end_date = self.get_product_date_range()
        filename = f"Product_Sales_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return  # User cancelled
        
        # Export the data
        try:
            # Create a writer and export the DataFrame
            export_to_excel(self.product_sales_df, file_path, sheet_name="Product Sales")
            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def setup_payment_methods_tab(self):
        """Setup the payment methods tab"""
        # Main container
        main_container = tk.Frame(self.payment_methods_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(main_container, 
                        text="Payment Methods Report",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=10)
        
        # Date range frame
        date_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        date_frame.pack(fill=tk.X, pady=10)
        
        # Start date
        tk.Label(date_frame, 
               text="Start Date:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, padx=5, pady=5)
        
        self.payment_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(date_frame, 
                                  textvariable=self.payment_start_date_var,
                                  font=FONTS["regular"],
                                  width=12)
        start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # End date
        tk.Label(date_frame, 
               text="End Date:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=2, padx=5, pady=5)
        
        self.payment_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(date_frame, 
                                textvariable=self.payment_end_date_var,
                                font=FONTS["regular"],
                                width=12)
        end_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Set default dates (current month)
        today = datetime.date.today()
        start_of_month = today.replace(day=1)
        self.payment_start_date_var.set(start_of_month.strftime("%Y-%m-%d"))
        self.payment_end_date_var.set(today.strftime("%Y-%m-%d"))
        
        # Generate button
        generate_btn = tk.Button(date_frame,
                               text="Generate Report",
                               font=FONTS["regular"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=2,
                               cursor="hand2",
                               command=self.load_payment_methods)
        generate_btn.grid(row=0, column=4, padx=15, pady=5)
        
        # Export button
        export_btn = tk.Button(date_frame,
                             text="Export",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=2,
                             cursor="hand2",
                             command=self.export_payment_methods)
        export_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Results frame
        self.payment_results_frame = tk.Frame(main_container, bg=COLORS["bg_white"])
        self.payment_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Load initial data
        self.load_payment_methods()
    
    def load_payment_methods(self):
        """Load and display payment methods data"""
        try:
            # Parse dates
            start_date = datetime.datetime.strptime(self.payment_start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(self.payment_end_date_var.get(), "%Y-%m-%d").date()
            
            # Validate dates
            if start_date > end_date:
                messagebox.showerror("Date Error", "Start date cannot be after end date.")
                return
                
        except ValueError:
            messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
            return
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing content
        for widget in self.payment_results_frame.winfo_children():
            widget.destroy()
        
        # Query for payment method summary
        query = """
            SELECT 
                payment_method,
                COUNT(*) as num_invoices,
                SUM(total_amount) as total_amount
            FROM invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """
        
        payment_data = self.controller.db.fetchall(query, (start_date_str, end_date_str))
        
        if not payment_data:
            # No data for selected range
            no_data_label = tk.Label(self.payment_results_frame,
                                   text="No payment data available for the selected date range.",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_white"],
                                   fg=COLORS["text_secondary"])
            no_data_label.pack(expand=True)
            return
        
        # Convert to pandas DataFrame
        columns = ["Payment Method", "Number of Invoices", "Total Amount"]
        self.payment_df = pd.DataFrame(payment_data, columns=columns)
        
        # Calculate cash/upi/credit breakdown
        query_breakdown = """
            SELECT 
                SUM(cash_amount) as total_cash,
                SUM(upi_amount) as total_upi,
                SUM(credit_amount) as total_credit
            FROM invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
        """
        
        breakdown_data = self.controller.db.fetchone(query_breakdown, (start_date_str, end_date_str))
        
        # Create two-column layout
        results_container = tk.Frame(self.payment_results_frame, bg=COLORS["bg_white"])
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Table
        table_frame = tk.Frame(results_container, bg=COLORS["bg_white"])
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right column - Chart
        chart_frame = tk.Frame(results_container, bg=COLORS["bg_white"])
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add payment method table
        self.create_payment_table(table_frame, payment_data)
        
        # Add payment breakdown section
        self.create_payment_breakdown(table_frame, breakdown_data)
        
        # Add chart
        self.create_payment_chart(chart_frame, payment_data)
    
    def create_payment_table(self, parent, payment_data):
        """Create payment methods table"""
        # Table frame
        treeview_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        treeview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview
        payment_tree = ttk.Treeview(treeview_frame, 
                                  columns=("Method", "Invoices", "Amount", "Percentage"),
                                  show="headings",
                                  height=len(payment_data) + 1)
        
        # Define columns
        payment_tree.heading("Method", text="Payment Method")
        payment_tree.heading("Invoices", text="# Invoices")
        payment_tree.heading("Amount", text="Total Amount")
        payment_tree.heading("Percentage", text="% of Total")
        
        # Set column widths
        payment_tree.column("Method", width=150)
        payment_tree.column("Invoices", width=100, anchor="e")
        payment_tree.column("Amount", width=150, anchor="e")
        payment_tree.column("Percentage", width=100, anchor="e")
        
        payment_tree.pack(fill=tk.BOTH, expand=True)
        
        # Calculate total
        total_amount = sum(row[2] for row in payment_data)
        total_invoices = sum(row[1] for row in payment_data)
        
        # Insert data
        for row in payment_data:
            method, invoices, amount = row
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            
            payment_tree.insert("", "end", values=(
                method,
                invoices,
                f"₹{amount:.2f}",
                f"{percentage:.1f}%"
            ))
        
        # Add total row
        payment_tree.insert("", "end", values=(
            "TOTAL",
            total_invoices,
            f"₹{total_amount:.2f}",
            "100.0%"
        ), tags=('total',))
        
        # Configure tag for total row
        payment_tree.tag_configure('total', font=FONTS["regular_bold"])
    
    def create_payment_breakdown(self, parent, breakdown_data):
        """Create payment breakdown section"""
        if not breakdown_data:
            return
            
        total_cash, total_upi, total_credit = breakdown_data
        
        # Ensure none is treated as zero
        total_cash = total_cash if total_cash is not None else 0
        total_upi = total_upi if total_upi is not None else 0
        total_credit = total_credit if total_credit is not None else 0
        
        # Frame for breakdown
        breakdown_frame = tk.LabelFrame(parent, 
                                      text="Payment Breakdown",
                                      font=FONTS["regular_bold"],
                                      bg=COLORS["bg_white"],
                                      fg=COLORS["text_primary"])
        breakdown_frame.pack(fill=tk.X, pady=10)
        
        # Create grid for breakdown
        tk.Label(breakdown_frame, 
               text="Cash Payments:",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        tk.Label(breakdown_frame, 
               text=f"₹{total_cash:.2f}",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=0, column=1, sticky="e", padx=10, pady=5)
        
        tk.Label(breakdown_frame, 
               text="UPI Payments:",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        tk.Label(breakdown_frame, 
               text=f"₹{total_upi:.2f}",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=1, column=1, sticky="e", padx=10, pady=5)
        
        tk.Label(breakdown_frame, 
               text="Credit Sales:",
               font=FONTS["regular"],
               bg=COLORS["bg_white"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        tk.Label(breakdown_frame, 
               text=f"₹{total_credit:.2f}",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_white"],
               fg=COLORS["danger"]).grid(row=2, column=1, sticky="e", padx=10, pady=5)
    
    def create_payment_chart(self, parent, payment_data):
        """Create payment methods chart"""
        # Extract data
        methods = [row[0] for row in payment_data]
        amounts = [row[2] for row in payment_data]
        
        # Create figure
        fig = Figure(figsize=(6, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Plot pie chart
        wedges, texts, autotexts = ax.pie(
            amounts, 
            labels=methods, 
            autopct='%1.1f%%',
            startangle=90,
            shadow=False,
            colors=['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
        )
        
        # Customize chart
        ax.set_title('Payment Methods Distribution')
        
        # Make labels and percentages more readable
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_weight('bold')
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Tight layout
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_payment_methods(self):
        """Export payment methods data to Excel"""
        if not hasattr(self, 'payment_df') or self.payment_df.empty:
            messagebox.showinfo("Export", "No data available to export.")
            return
        
        # Format dates for filename
        try:
            start_date = datetime.datetime.strptime(self.payment_start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(self.payment_end_date_var.get(), "%Y-%m-%d").date()
            filename = f"Payment_Methods_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
        except:
            filename = "Payment_Methods_Report.xlsx"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return  # User cancelled
        
        # Export the data
        try:
            # Create a writer and export the DataFrame
            export_to_excel(self.payment_df, file_path, sheet_name="Payment Methods")
            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def setup_tax_report_tab(self):
        """Setup the tax report tab"""
        # Main container
        main_container = tk.Frame(self.tax_report_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(main_container, 
                        text="Tax Report",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=10)
        
        # Date range frame
        date_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        date_frame.pack(fill=tk.X, pady=10)
        
        # Start date
        tk.Label(date_frame, 
               text="Start Date:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, padx=5, pady=5)
        
        self.tax_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(date_frame, 
                                  textvariable=self.tax_start_date_var,
                                  font=FONTS["regular"],
                                  width=12)
        start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # End date
        tk.Label(date_frame, 
               text="End Date:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=2, padx=5, pady=5)
        
        self.tax_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(date_frame, 
                                textvariable=self.tax_end_date_var,
                                font=FONTS["regular"],
                                width=12)
        end_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Set default dates (current month)
        today = datetime.date.today()
        start_of_month = today.replace(day=1)
        self.tax_start_date_var.set(start_of_month.strftime("%Y-%m-%d"))
        self.tax_end_date_var.set(today.strftime("%Y-%m-%d"))
        
        # Generate button
        generate_btn = tk.Button(date_frame,
                               text="Generate Report",
                               font=FONTS["regular"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=2,
                               cursor="hand2",
                               command=self.load_tax_report)
        generate_btn.grid(row=0, column=4, padx=15, pady=5)
        
        # Export button
        export_btn = tk.Button(date_frame,
                             text="Export",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=2,
                             cursor="hand2",
                             command=self.export_tax_report)
        export_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Results frame
        self.tax_results_frame = tk.Frame(main_container, bg=COLORS["bg_white"])
        self.tax_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Load initial data
        self.load_tax_report()
    
    def load_tax_report(self):
        """Load and display tax report data with CGST/SGST breakup"""
        try:
            # Parse dates
            start_date = datetime.datetime.strptime(self.tax_start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(self.tax_end_date_var.get(), "%Y-%m-%d").date()
            
            # Validate dates
            if start_date > end_date:
                messagebox.showerror("Date Error", "Start date cannot be after end date.")
                return
                
        except ValueError:
            messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
            return
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing content
        for widget in self.tax_results_frame.winfo_children():
            widget.destroy()
        
        # Query for tax data by tax percentage with HSN/SAC code and detailed info
        query = """
            SELECT 
                ii.tax_percentage,
                p.hsn_code as hsn_code,
                SUM(ii.quantity) as quantity,
                SUM(ii.total_price) as taxable_amount,
                SUM(ii.total_price * (ii.tax_percentage / 100) / 2) as cgst_amount,
                SUM(ii.total_price * (ii.tax_percentage / 100) / 2) as sgst_amount,
                SUM(ii.total_price * (ii.tax_percentage / 100)) as total_tax
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            JOIN products p ON ii.product_id = p.id
            WHERE DATE(i.invoice_date) BETWEEN ? AND ?
            GROUP BY ii.tax_percentage, p.hsn_code
            ORDER BY ii.tax_percentage, p.hsn_code
        """
        
        try:
            tax_data = self.controller.db.fetchall(query, (start_date_str, end_date_str))
        except Exception as e:
            # If HSN code column doesn't exist in products table, use simpler query
            print(f"HSN code query failed: {e}")
            query = """
                SELECT 
                    ii.tax_percentage,
                    '' as hsn_code,
                    SUM(ii.quantity) as quantity,
                    SUM(ii.total_price) as taxable_amount,
                    SUM(ii.total_price * (ii.tax_percentage / 100) / 2) as cgst_amount,
                    SUM(ii.total_price * (ii.tax_percentage / 100) / 2) as sgst_amount,
                    SUM(ii.total_price * (ii.tax_percentage / 100)) as total_tax
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.id
                WHERE DATE(i.invoice_date) BETWEEN ? AND ?
                GROUP BY ii.tax_percentage
                ORDER BY ii.tax_percentage
            """
            tax_data = self.controller.db.fetchall(query, (start_date_str, end_date_str))
        
        if not tax_data:
            # No data for selected range
            no_data_label = tk.Label(self.tax_results_frame,
                                   text="No tax data available for the selected date range.",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_white"],
                                   fg=COLORS["text_secondary"])
            no_data_label.pack(expand=True)
            return
        
        # Convert to pandas DataFrame
        columns = ["Tax Percentage", "HSN/SAC", "Quantity", "Taxable Amount", "CGST Amount", "SGST Amount", "Total Tax"]
        self.tax_df = pd.DataFrame(tax_data, columns=columns)
        
        # Create tax report table
        treeview_frame = tk.Frame(self.tax_results_frame, bg=COLORS["bg_white"])
        treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbars to the treeview
        tree_scroll_y = ttk.Scrollbar(treeview_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = ttk.Scrollbar(treeview_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Create treeview with all columns
        tax_tree = ttk.Treeview(treeview_frame, 
                              columns=("Tax", "HSN", "Quantity", "Taxable", "CGST", "SGST", "Total Tax"),
                              show="headings",
                              yscrollcommand=tree_scroll_y.set,
                              xscrollcommand=tree_scroll_x.set)
        
        # Configure scrollbars
        tree_scroll_y.config(command=tax_tree.yview)
        tree_scroll_x.config(command=tax_tree.xview)
        
        # Define columns
        tax_tree.heading("Tax", text="Tax %")
        tax_tree.heading("HSN", text="HSN/SAC")
        tax_tree.heading("Quantity", text="Quantity")
        tax_tree.heading("Taxable", text="Taxable Amount")
        tax_tree.heading("CGST", text="CGST Amount")
        tax_tree.heading("SGST", text="SGST Amount")
        tax_tree.heading("Total Tax", text="Total Tax")
        
        # Set column widths
        tax_tree.column("Tax", width=60, anchor="e")
        tax_tree.column("HSN", width=100, anchor="e")
        tax_tree.column("Quantity", width=70, anchor="e")
        tax_tree.column("Taxable", width=120, anchor="e")
        tax_tree.column("CGST", width=100, anchor="e")
        tax_tree.column("SGST", width=100, anchor="e")
        tax_tree.column("Total Tax", width=100, anchor="e")
        
        tax_tree.pack(fill=tk.BOTH, expand=True)
        
        # Calculate totals
        total_items = sum(row[2] for row in tax_data)
        total_taxable = sum(row[3] for row in tax_data)
        total_cgst = sum(row[4] for row in tax_data)
        total_sgst = sum(row[5] for row in tax_data)
        total_tax = sum(row[6] for row in tax_data)
        
        # Insert data
        for row in tax_data:
            tax_percent, hsn_code, quantity, taxable_amount, cgst_amount, sgst_amount, total_tax_amount = row
            
            tax_tree.insert("", "end", values=(
                f"{tax_percent:.1f}%",
                hsn_code if hsn_code else "-",
                f"{int(quantity)}",
                f"₹{taxable_amount:.2f}",
                f"₹{cgst_amount:.2f}",
                f"₹{sgst_amount:.2f}",
                f"₹{total_tax_amount:.2f}"
            ))
        
        # Add total row
        tax_tree.insert("", "end", values=(
            "TOTAL",
            "",
            total_items,
            f"₹{total_taxable:.2f}",
            f"₹{total_cgst:.2f}",
            f"₹{total_sgst:.2f}",
            f"₹{total_tax:.2f}"
        ), tags=('total',))
        
        # Configure tag for total row
        tax_tree.tag_configure('total', font=FONTS["regular_bold"])
        
        # Add summary section
        summary_frame = tk.LabelFrame(self.tax_results_frame, 
                                     text="GST Summary",
                                     font=FONTS["regular_bold"],
                                     bg=COLORS["bg_white"],
                                     fg=COLORS["text_primary"])
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Calculate some metrics for summary
        invoice_count_query = """
            SELECT COUNT(*) FROM invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
        """
        invoice_count = self.controller.db.fetchone(invoice_count_query, (start_date_str, end_date_str))[0]
        
        # Summary info with CGST/SGST breakdown
        summary_info = [
            {"label": "Total Invoices:", "value": str(invoice_count)},
            {"label": "Total Sales (incl. tax):", "value": f"₹{(total_taxable + total_tax):.2f}"},
            {"label": "Taxable Amount:", "value": f"₹{total_taxable:.2f}"},
            {"label": "CGST Collected:", "value": f"₹{total_cgst:.2f}"},
            {"label": "SGST Collected:", "value": f"₹{total_sgst:.2f}"},
            {"label": "Total Tax Collected:", "value": f"₹{total_tax:.2f}"}
        ]
        
        # Create summary grid with two columns
        col_count = 2  # Number of columns
        row_count = (len(summary_info) + col_count - 1) // col_count  # Calculate rows needed
        
        for i, info in enumerate(summary_info):
            row = i // col_count
            col = (i % col_count) * 2  # Multiply by 2 for label and value columns
            
            tk.Label(summary_frame, 
                   text=info["label"],
                   font=FONTS["regular_bold"],
                   bg=COLORS["bg_white"],
                   fg=COLORS["text_primary"]).grid(row=row, column=col, sticky="w", padx=20, pady=5)
            
            tk.Label(summary_frame, 
                   text=info["value"],
                   font=FONTS["regular"],
                   bg=COLORS["bg_white"],
                   fg=COLORS["text_primary"]).grid(row=row, column=col+1, sticky="e", padx=20, pady=5)
    
    def export_tax_report(self):
        """Export tax report data to Excel with GSTR-1 compatible format"""
        if not hasattr(self, 'tax_df') or self.tax_df.empty:
            messagebox.showinfo("Export", "No data available to export.")
            return
        
        # Format dates for filename
        try:
            start_date = datetime.datetime.strptime(self.tax_start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(self.tax_end_date_var.get(), "%Y-%m-%d").date()
            filename = f"GST_Report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
        except:
            filename = "GST_Report.xlsx"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return  # User cancelled
        
        # Export the data
        try:
            # Get additional metadata
            shop_name = "Agritech POS"  # Default value
            shop_gstin = ""  # Default empty
            
            # Try to get actual shop details from settings
            try:
                shop_query = "SELECT value FROM settings WHERE key = ?"
                shop_name_result = self.controller.db.fetchone(shop_query, ("shop_name",))
                if shop_name_result and shop_name_result[0]:
                    shop_name = shop_name_result[0]
                
                shop_gstin_result = self.controller.db.fetchone(shop_query, ("shop_gstin",))
                if shop_gstin_result and shop_gstin_result[0]:
                    shop_gstin = shop_gstin_result[0]
            except Exception as e:
                print(f"Error fetching shop details: {e}")
            
            # Create a copy of the dataframe 
            export_df = self.tax_df.copy()
            
            # Add report metadata at the top of the sheet
            metadata = pd.DataFrame({
                "Report Type": ["GST Tax Report"],
                "Business Name": [shop_name],
                "GSTIN": [shop_gstin],
                "Period": [f"{start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"],
                "Generated Date": [datetime.datetime.now().strftime("%d-%m-%Y %H:%M")]
            })
            
            # Calculate summary data
            total_taxable = export_df["Taxable Amount"].sum()
            total_cgst = export_df["CGST Amount"].sum()
            total_sgst = export_df["SGST Amount"].sum()
            total_tax = export_df["Total Tax"].sum()
            
            # Create summary DataFrame
            summary_df = pd.DataFrame({
                "Summary": ["Total Taxable Value", "Total CGST", "Total SGST", "Total Tax"],
                "Amount": [
                    f"₹{total_taxable:.2f}",
                    f"₹{total_cgst:.2f}",
                    f"₹{total_sgst:.2f}",
                    f"₹{total_tax:.2f}"
                ]
            })
            
            # Format currency columns in the main dataframe
            for col in ["Taxable Amount", "CGST Amount", "SGST Amount", "Total Tax"]:
                export_df[col] = export_df[col].apply(lambda x: f"₹{x:.2f}" if pd.notnull(x) else "")
            
            # Export to Excel with multiple sections
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                # Write metadata at the top
                metadata.to_excel(writer, sheet_name="GST Report", index=False, startrow=0)
                
                # Write the main data below metadata
                export_df.to_excel(writer, sheet_name="GST Report", index=False, startrow=len(metadata) + 2)
                
                # Write summary at the bottom
                summary_df.to_excel(writer, sheet_name="GST Report", index=False, 
                                   startrow=len(metadata) + len(export_df) + 4)
                
                # Get workbook and worksheet objects for formatting
                workbook = writer.book
                worksheet = writer.sheets["GST Report"]
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D9EAD3',
                    'border': 1
                })
                
                data_format = workbook.add_format({
                    'border': 1
                })
                
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14
                })
                
                summary_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#FCE4D6',
                    'border': 1
                })
                
                # Apply formats to the headers and data
                for col_num, value in enumerate(metadata.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                data_start_row = len(metadata) + 2
                for col_num, value in enumerate(export_df.columns.values):
                    worksheet.write(data_start_row, col_num, value, header_format)
                
                summary_start_row = len(metadata) + len(export_df) + 4
                for col_num, value in enumerate(summary_df.columns.values):
                    worksheet.write(summary_start_row, col_num, value, summary_format)
                
                # Add title above metadata
                worksheet.merge_range('A1:E1', 'GST Tax Report', title_format)
                
                # Set column widths
                worksheet.set_column('A:A', 15)  # Tax percentage
                worksheet.set_column('B:B', 15)  # HSN/SAC
                worksheet.set_column('C:C', 10)  # Quantity
                worksheet.set_column('D:D', 20)  # Taxable Amount
                worksheet.set_column('E:E', 15)  # CGST
                worksheet.set_column('F:F', 15)  # SGST
                worksheet.set_column('G:G', 15)  # Total Tax
            
            messagebox.showinfo("Export Successful", f"GST Report exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            print(f"Export error details: {traceback.format_exc()}")
    
    def setup_inventory_report_tab(self):
        """Setup the inventory report tab"""
        # Main container
        main_container = tk.Frame(self.inventory_report_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(main_container, 
                        text="Inventory Value Report",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=10)
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Category filter
        tk.Label(filter_frame, 
               text="Filter by Category:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, padx=5, pady=5)
        
        self.inventory_category_var = tk.StringVar(value="All Categories")
        self.category_combo = ttk.Combobox(filter_frame, 
                                        textvariable=self.inventory_category_var,
                                        font=FONTS["regular"],
                                        width=20,
                                        state="readonly")
        self.category_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Sort by
        tk.Label(filter_frame, 
               text="Sort By:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=2, padx=5, pady=5)
        
        self.inventory_sort_var = tk.StringVar(value="Value (High to Low)")
        sort_options = ["Value (High to Low)", "Quantity (High to Low)", "Product Name"]
        sort_combo = ttk.Combobox(filter_frame, 
                                textvariable=self.inventory_sort_var,
                                values=sort_options,
                                font=FONTS["regular"],
                                width=20,
                                state="readonly")
        sort_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Generate button
        generate_btn = tk.Button(filter_frame,
                               text="Generate Report",
                               font=FONTS["regular"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=2,
                               cursor="hand2",
                               command=self.load_inventory_report)
        generate_btn.grid(row=0, column=4, padx=15, pady=5)
        
        # Export button
        export_btn = tk.Button(filter_frame,
                             text="Export",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=2,
                             cursor="hand2",
                             command=self.export_inventory_report)
        export_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Results frame
        self.inventory_results_frame = tk.Frame(main_container, bg=COLORS["bg_white"])
        self.inventory_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Load categories
        self.load_product_categories()
        
        # Load initial data
        self.load_inventory_report()
    
    def load_product_categories(self):
        """Load product categories for dropdown"""
        # Query for unique categories
        query = """
            SELECT DISTINCT category FROM products
            WHERE category IS NOT NULL AND category != ''
            ORDER BY category
        """
        categories = self.controller.db.fetchall(query)
        
        # Format for dropdown
        category_list = ["All Categories"] + [cat[0] for cat in categories]
        
        # Update dropdown values
        self.category_combo["values"] = category_list
    
    def load_inventory_report(self):
        """Load and display inventory report data"""
        # Get filter values
        category = self.inventory_category_var.get()
        sort_option = self.inventory_sort_var.get()
        
        # Build query based on filters
        params = []
        query = """
            SELECT 
                p.id,
                p.name,
                p.category,
                p.wholesale_price,
                p.selling_price,
                SUM(i.quantity) as total_quantity,
                SUM(i.quantity * p.wholesale_price) as total_cost,
                SUM(i.quantity * p.selling_price) as total_value
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
        """
        
        # Add category filter if needed
        if category != "All Categories":
            query += " WHERE p.category = ?"
            params.append(category)
        
        # Group by clause
        query += " GROUP BY p.id, p.name, p.category, p.wholesale_price, p.selling_price"
        
        # Add sorting
        if sort_option == "Value (High to Low)":
            query += " ORDER BY total_value DESC"
        elif sort_option == "Quantity (High to Low)":
            query += " ORDER BY total_quantity DESC"
        else:  # Product Name
            query += " ORDER BY p.name ASC"
        
        # Clear existing content
        for widget in self.inventory_results_frame.winfo_children():
            widget.destroy()
        
        # Execute query
        inventory_data = self.controller.db.fetchall(query, params)
        
        if not inventory_data:
            # No data for selected filters
            no_data_label = tk.Label(self.inventory_results_frame,
                                   text="No inventory data available for the selected filters.",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_white"],
                                   fg=COLORS["text_secondary"])
            no_data_label.pack(expand=True)
            return
        
        # Convert to pandas DataFrame
        columns = ["ID", "Product", "Category", "Cost Price", "Selling Price", 
                 "Quantity", "Total Cost", "Total Value"]
        self.inventory_df = pd.DataFrame(inventory_data, columns=columns)
        
        # Create treeview
        treeview_frame = tk.Frame(self.inventory_results_frame, bg=COLORS["bg_white"])
        treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        inventory_tree = ttk.Treeview(treeview_frame, 
                                    columns=("Product", "Category", "Qty", "Cost", "Value", "Profit"),
                                    show="headings",
                                    yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=inventory_tree.yview)
        
        # Define columns
        inventory_tree.heading("Product", text="Product")
        inventory_tree.heading("Category", text="Category")
        inventory_tree.heading("Qty", text="Quantity")
        inventory_tree.heading("Cost", text="Total Cost")
        inventory_tree.heading("Value", text="Retail Value")
        inventory_tree.heading("Profit", text="Potential Profit")
        
        # Set column widths
        inventory_tree.column("Product", width=250)
        inventory_tree.column("Category", width=150)
        inventory_tree.column("Qty", width=80, anchor="e")
        inventory_tree.column("Cost", width=120, anchor="e")
        inventory_tree.column("Value", width=120, anchor="e")
        inventory_tree.column("Profit", width=120, anchor="e")
        
        inventory_tree.pack(fill=tk.BOTH, expand=True)
        
        # Insert data
        total_quantity = 0
        total_cost = 0
        total_value = 0
        
        for row in inventory_data:
            _, name, category, _, _, quantity, cost, value = row
            
            # Skip products with no inventory
            if quantity is None or quantity == 0:
                continue
                
            # Calculate potential profit
            profit = value - cost
            
            # Update totals
            total_quantity += quantity
            total_cost += cost
            total_value += value
            
            # Format display values
            if category is None:
                category = ""
                
            inventory_tree.insert("", "end", values=(
                name,
                category,
                int(quantity),
                f"₹{cost:.2f}",
                f"₹{value:.2f}",
                f"₹{profit:.2f}"
            ))
        
        # Add total row
        inventory_tree.insert("", "end", values=(
            "TOTAL",
            "",
            int(total_quantity),
            f"₹{total_cost:.2f}",
            f"₹{total_value:.2f}",
            f"₹{total_value - total_cost:.2f}"
        ), tags=('total',))
        
        # Configure tag for total row
        inventory_tree.tag_configure('total', font=FONTS["regular_bold"])
        
        # Add summary section
        summary_frame = tk.Frame(self.inventory_results_frame, bg=COLORS["bg_white"], pady=10)
        summary_frame.pack(fill=tk.X, padx=10)
        
        # Summary tiles in a row
        total_products = len([row for row in inventory_data if row[5] is not None and row[5] > 0])
        
        # Create summary tiles
        summary_tiles = [
            {"label": "Total Products", "value": str(total_products)},
            {"label": "Total Items", "value": str(int(total_quantity))},
            {"label": "Total Cost Value", "value": f"₹{total_cost:.2f}"},
            {"label": "Total Retail Value", "value": f"₹{total_value:.2f}"},
            {"label": "Potential Profit", "value": f"₹{total_value - total_cost:.2f}"}
        ]
        
        # Create tiles with different colors
        colors = [COLORS["primary"], COLORS["success"], COLORS["info"], 
                COLORS["warning"], COLORS["secondary"]]
        
        for i, tile in enumerate(summary_tiles):
            frame = tk.Frame(summary_frame, bg=colors[i % len(colors)], padx=15, pady=15, width=150)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            frame.pack_propagate(False)
            
            tk.Label(frame, 
                   text=tile["label"],
                   font=FONTS["regular_bold"],
                   bg=colors[i % len(colors)],
                   fg=COLORS["text_white"]).pack(anchor="w")
            
            tk.Label(frame, 
                   text=tile["value"],
                   font=FONTS["subheading"],
                   bg=colors[i % len(colors)],
                   fg=COLORS["text_white"]).pack(anchor="w", pady=5)
    
    def export_inventory_report(self):
        """Export inventory report data to Excel"""
        if not hasattr(self, 'inventory_df') or self.inventory_df.empty:
            messagebox.showinfo("Export", "No data available to export.")
            return
        
        # Create filename
        category = self.inventory_category_var.get().replace(" ", "_")
        filename = f"Inventory_Report_{category}.xlsx"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return  # User cancelled
        
        # Export the data
        try:
            # Create a writer and export the DataFrame
            export_to_excel(self.inventory_df, file_path, sheet_name="Inventory Report")
            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def on_show(self):
        """Called when frame is shown"""
        # Set default dates
        today = datetime.date.today()
        start_of_month = today.replace(day=1)
        
        # Sales summary tab
        self.sales_date_range_var.set("This Month")
        self.toggle_custom_date_range()
        
        # Product sales tab
        self.product_date_range_var.set("This Month")
        self.toggle_product_custom_date_range()
        
        # Payment methods tab
        self.payment_start_date_var.set(start_of_month.strftime("%Y-%m-%d"))
        self.payment_end_date_var.set(today.strftime("%Y-%m-%d"))
        
        # Tax report tab
        self.tax_start_date_var.set(start_of_month.strftime("%Y-%m-%d"))
        self.tax_end_date_var.set(today.strftime("%Y-%m-%d"))
        
        # Update data in current tab
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Sales Summary
            self.load_sales_summary()
        elif current_tab == 1:  # Sales by Product
            self.load_sales_by_product()
        elif current_tab == 2:  # Payment Methods
            self.load_payment_methods()
        elif current_tab == 3:  # Tax Report
            self.load_tax_report()
        elif current_tab == 4:  # Inventory Report
            self.load_product_categories()
            self.load_inventory_report()
