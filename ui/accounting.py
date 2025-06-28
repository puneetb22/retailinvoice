"""
Accounting UI for POS system
Basic accounting module for profit/loss tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import calendar
import traceback
from decimal import Decimal

from assets.styles import COLORS, FONTS, STYLES
from utils.helpers import format_currency, parse_currency
from utils.export import export_to_excel

class AccountingFrame(tk.Frame):
    """Accounting frame for basic financial tracking"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Accounting",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        self.profit_loss_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.cash_flow_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.expenses_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.ledger_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        
        self.notebook.add(self.profit_loss_tab, text="Profit & Loss")
        self.notebook.add(self.cash_flow_tab, text="Cash Flow")
        self.notebook.add(self.expenses_tab, text="Expenses")
        self.notebook.add(self.ledger_tab, text="Ledgers")
        
        # Setup tabs
        self.setup_profit_loss_tab()
        self.setup_cash_flow_tab()
        self.setup_expenses_tab()
        self.setup_ledger_tab()
    
    def setup_profit_loss_tab(self):
        """Setup profit & loss tab with an improved UI"""
        # Main container
        container = tk.Frame(self.profit_loss_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top panel - Controls
        top_panel = tk.Frame(container, bg=COLORS["bg_secondary"], pady=15)
        top_panel.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Date range row with better spacing and layout
        date_controls_frame = tk.Frame(top_panel, bg=COLORS["bg_secondary"])
        date_controls_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Date range label
        date_label = tk.Label(date_controls_frame, 
                           text="Report Period:",
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_secondary"],
                           fg=COLORS["text_primary"])
        date_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Date range options in a more compact layout
        self.pl_date_range_var = tk.StringVar(value="this_month")
        
        # Create a horizontal frame for quick date options
        quick_dates_frame = tk.Frame(date_controls_frame, bg=COLORS["bg_secondary"])
        quick_dates_frame.pack(side=tk.LEFT)
        
        # Create radio buttons in a more visually appealing layout
        date_ranges = [
            ("This Month", "this_month"), 
            ("Last Month", "last_month"), 
            ("This Quarter", "this_quarter"), 
            ("Last Quarter", "last_quarter"), 
            ("This Year", "this_year"), 
            ("Last Year", "last_year"),
            ("Custom", "custom")
        ]
        
        # Use a modern button-like approach for date selection
        for i, (text, value) in enumerate(date_ranges):
            date_btn = tk.Frame(quick_dates_frame, 
                             bg=COLORS["bg_primary"],
                             padx=10, 
                             pady=5,
                             highlightbackground=COLORS["primary"],
                             highlightthickness=1 if value == "this_month" else 0)
            date_btn.pack(side=tk.LEFT, padx=3)
            
            rb = tk.Radiobutton(date_btn, 
                              text=text,
                              variable=self.pl_date_range_var,
                              value=value,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.toggle_pl_custom_date_range,
                              indicatoron=False,
                              bd=0,
                              padx=5,
                              pady=2)
            rb.pack(fill=tk.BOTH)
        
        # Create a separate frame for custom date range options
        self.pl_custom_date_frame = tk.Frame(top_panel, bg=COLORS["bg_secondary"], padx=20, pady=10)
        
        # Use a grid layout for better alignment of date inputs
        tk.Label(self.pl_custom_date_frame, 
               text="Start Date:",
               font=FONTS["regular"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.pl_start_date_var = tk.StringVar()
        
        # Use a nicer looking date entry with calendar icon
        start_date_frame = tk.Frame(self.pl_custom_date_frame, bg=COLORS["bg_secondary"])
        start_date_frame.grid(row=0, column=1, padx=(0, 20), sticky="ew")
        
        start_date_entry = tk.Entry(start_date_frame, 
                                  textvariable=self.pl_start_date_var,
                                  font=FONTS["regular"],
                                  width=12,
                                  bd=1,
                                  relief=tk.SOLID)
        start_date_entry.pack(side=tk.LEFT)
        
        # Calendar icon/button for start date
        cal_icon_start = tk.Label(start_date_frame, 
                                text="📅",
                                font=FONTS["regular"],
                                bg=COLORS["bg_secondary"],
                                fg=COLORS["primary"],
                                cursor="hand2")
        cal_icon_start.pack(side=tk.LEFT, padx=(5, 0))
        
        # End date with similar styling
        tk.Label(self.pl_custom_date_frame, 
               text="End Date:",
               font=FONTS["regular"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=0, column=2, padx=(0, 10), sticky="w")
        
        self.pl_end_date_var = tk.StringVar()
        
        end_date_frame = tk.Frame(self.pl_custom_date_frame, bg=COLORS["bg_secondary"])
        end_date_frame.grid(row=0, column=3, sticky="ew")
        
        end_date_entry = tk.Entry(end_date_frame, 
                                textvariable=self.pl_end_date_var,
                                font=FONTS["regular"],
                                width=12,
                                bd=1,
                                relief=tk.SOLID)
        end_date_entry.pack(side=tk.LEFT)
        
        # Calendar icon/button for end date
        cal_icon_end = tk.Label(end_date_frame, 
                              text="📅",
                              font=FONTS["regular"],
                              bg=COLORS["bg_secondary"],
                              fg=COLORS["primary"],
                              cursor="hand2")
        cal_icon_end.pack(side=tk.LEFT, padx=(5, 0))
        
        # Action buttons in a horizontal layout
        actions_frame = tk.Frame(top_panel, bg=COLORS["bg_secondary"], pady=10)
        actions_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Generate report button using theme properties
        generate_btn = tk.Button(actions_frame,
                               text="Generate Report",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               activebackground=COLORS["primary_light"],
                               activeforeground=COLORS["text_white"],
                               padx=15,
                               pady=8,
                               relief=tk.FLAT,
                               cursor="hand2",
                               command=self.load_profit_loss)
        generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button using theme properties
        export_btn = tk.Button(actions_frame,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             activebackground=COLORS["secondary_dark"],
                             activeforeground=COLORS["text_white"],
                             padx=15,
                             pady=8,
                             relief=tk.FLAT,
                             cursor="hand2",
                             command=self.export_profit_loss)
        export_btn.pack(side=tk.LEFT)
        
        # Initial state - hide custom date frame
        self.toggle_pl_custom_date_range()
        
        # Report area with card-like styling
        report_container = tk.Frame(container, bg=COLORS["bg_white"], bd=1, relief=tk.SOLID)
        report_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create scrollable frame for report with improved styling
        canvas = tk.Canvas(report_container, bg=COLORS["bg_white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(report_container, orient="vertical", command=canvas.yview)
        
        self.pl_report_frame = tk.Frame(canvas, bg=COLORS["bg_white"], padx=20, pady=20)
        self.pl_report_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.pl_report_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_pl_custom_date_range(self):
        """Show/hide custom date range inputs for profit & loss tab"""
        # Simpler approach for highlighting selected button
        if self.pl_date_range_var.get() == "custom":
            # Set default date range (last 30 days)
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            self.pl_start_date_var.set(thirty_days_ago.strftime("%Y-%m-%d"))
            self.pl_end_date_var.set(today.strftime("%Y-%m-%d"))
            
            # Show custom date frame
            self.pl_custom_date_frame.pack(fill=tk.X, pady=10)
        else:
            # Hide custom date frame
            self.pl_custom_date_frame.pack_forget()
    
    def get_pl_date_range(self):
        """Get start and end dates for profit & loss report"""
        date_range = self.pl_date_range_var.get()
        today = datetime.date.today()
        
        if date_range == "this_month":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        
        elif date_range == "last_month":
            start_of_this_month = today.replace(day=1)
            end_of_last_month = start_of_this_month - datetime.timedelta(days=1)
            start_of_last_month = end_of_last_month.replace(day=1)
            return start_of_last_month, end_of_last_month
        
        elif date_range == "this_quarter":
            current_quarter = (today.month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start_of_quarter = today.replace(month=start_month, day=1)
            return start_of_quarter, today
        
        elif date_range == "last_quarter":
            current_quarter = (today.month - 1) // 3 + 1
            last_quarter = current_quarter - 1
            last_quarter_year = today.year
            
            if last_quarter == 0:
                last_quarter = 4
                last_quarter_year -= 1
                
            start_month = (last_quarter - 1) * 3 + 1
            end_month = start_month + 2
            
            start_of_quarter = datetime.date(last_quarter_year, start_month, 1)
            end_of_quarter = datetime.date(last_quarter_year, end_month, 1)
            end_of_quarter = end_of_quarter.replace(day=calendar.monthrange(end_of_quarter.year, end_of_quarter.month)[1])
            
            return start_of_quarter, end_of_quarter
        
        elif date_range == "this_year":
            start_of_year = today.replace(month=1, day=1)
            return start_of_year, today
        
        elif date_range == "last_year":
            start_of_last_year = datetime.date(today.year-1, 1, 1)
            end_of_last_year = datetime.date(today.year-1, 12, 31)
            return start_of_last_year, end_of_last_year
        
        elif date_range == "custom":
            try:
                start_date = datetime.datetime.strptime(self.pl_start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.pl_end_date_var.get(), "%Y-%m-%d").date()
                
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
    
    def load_profit_loss(self):
        """Load and display profit & loss report with enhanced visual elements"""
        # Get date range
        start_date, end_date = self.get_pl_date_range()
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing report
        for widget in self.pl_report_frame.winfo_children():
            widget.destroy()
        
        # Create header with better design
        header_frame = tk.Frame(self.pl_report_frame, bg=COLORS["bg_white"], pady=15)
        header_frame.pack(fill=tk.X)
        
        # Add title with more impressive styling
        title_frame = tk.Frame(header_frame, bg=COLORS["primary"], padx=20, pady=10)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(title_frame,
                       text="PROFIT & LOSS STATEMENT",
                       font=FONTS["heading"],
                       bg=COLORS["primary"],
                       fg=COLORS["text_white"])
        title.pack()
        
        # Add date range with better styling
        date_label = tk.Label(header_frame,
                            text=f"Reporting Period: {start_date_str} to {end_date_str}",
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_white"],
                            fg=COLORS["text_primary"])
        date_label.pack(pady=(0, 20))
        
        # Get revenue data
        revenue_query = """
            SELECT 
                SUM(total_amount) as total_revenue,
                SUM(discount_amount) as total_discount,
                SUM(tax_amount) as total_tax
            FROM invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
        """
        revenue_data = self.controller.db.fetchone(revenue_query, (start_date_str, end_date_str))
        
        # Get cost of goods sold
        cogs_query = """
            SELECT 
                SUM(ii.quantity * p.wholesale_price) as total_cogs
            FROM 
                invoice_items ii
            JOIN 
                invoices i ON ii.invoice_id = i.id
            JOIN 
                products p ON ii.product_id = p.id
            WHERE 
                DATE(i.invoice_date) BETWEEN ? AND ?
        """
        cogs_data = self.controller.db.fetchone(cogs_query, (start_date_str, end_date_str))
        
        # Get expense data
        expense_query = """
            SELECT 
                SUM(amount) as total_expenses
            FROM expenses
            WHERE DATE(expense_date) BETWEEN ? AND ?
        """
        expense_data = self.controller.db.fetchone(expense_query, (start_date_str, end_date_str))
        
        # Extract values (handle None values)
        total_revenue = revenue_data[0] if revenue_data and revenue_data[0] else 0
        total_discount = revenue_data[1] if revenue_data and revenue_data[1] else 0
        total_tax = revenue_data[2] if revenue_data and revenue_data[2] else 0
        total_cogs = cogs_data[0] if cogs_data and cogs_data[0] else 0
        total_expenses = expense_data[0] if expense_data and expense_data[0] else 0
        
        # Calculate net revenue
        net_revenue = total_revenue
        
        # Calculate gross profit
        gross_profit = net_revenue - total_cogs
        
        # Calculate net profit
        net_profit = gross_profit - total_expenses
        
        # Calculate profit margin
        profit_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0
        
        # Add summary cards at the top for key metrics
        summary_frame = tk.Frame(self.pl_report_frame, bg=COLORS["bg_white"])
        summary_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Create a row of 3 key metric cards
        metrics = [
            {"label": "Net Revenue", "value": net_revenue, "color": COLORS["primary"]},
            {"label": "Gross Profit", "value": gross_profit, "color": COLORS["secondary"]},
            {"label": "Net Profit", "value": net_profit, "color": COLORS["success"] if net_profit > 0 else COLORS["danger"]}
        ]
        
        for i, metric in enumerate(metrics):
            # Card frame with colored top border
            card = tk.Frame(summary_frame, 
                          bg=COLORS["bg_white"], 
                          bd=1, 
                          relief=tk.SOLID,
                          width=180,
                          height=100)
            card.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)
            card.pack_propagate(False)  # Keep fixed size
            
            # Colored top bar
            top_bar = tk.Frame(card, bg=metric["color"], height=5)
            top_bar.pack(fill=tk.X)
            
            # Metric label
            label = tk.Label(card,
                           text=metric["label"],
                           font=FONTS["regular"],
                           bg=COLORS["bg_white"],
                           fg=COLORS["text_primary"])
            label.pack(pady=(15, 5))
            
            # Metric value
            value_color = COLORS["success"] if metric["value"] > 0 else COLORS["danger"]
            if metric["label"] == "Net Revenue":
                value_color = COLORS["text_primary"]
                
            value = tk.Label(card,
                          text=format_currency(metric["value"]),
                          font=FONTS["subheading"],
                          bg=COLORS["bg_white"],
                          fg=value_color)
            value.pack(pady=5)
        
        # Create report sections
        self.create_pl_section(self.pl_report_frame, "Revenue", [
            {"label": "Gross Revenue", "value": total_revenue},
            {"label": "Tax Collected", "value": total_tax, "indent": True},
            {"label": "Discounts Given", "value": total_discount, "indent": True, "negative": True},
            {"label": "Net Revenue", "value": net_revenue, "bold": True}
        ])
        
        self.create_pl_section(self.pl_report_frame, "Cost of Goods Sold", [
            {"label": "Total Cost of Goods", "value": total_cogs, "negative": True},
            {"label": "Gross Profit", "value": gross_profit, "bold": True}
        ])
        
        self.create_pl_section(self.pl_report_frame, "Operating Expenses", [
            {"label": "Total Expenses", "value": total_expenses, "negative": True}
        ])
        
        self.create_pl_section(self.pl_report_frame, "Net Profit", [
            {"label": "Net Profit", "value": net_profit, "bold": True},
            {"label": "Profit Margin", "value": f"{profit_margin:.2f}%", "is_percent": True}
        ])
        
        # Add a Footer with generation date
        footer_frame = tk.Frame(self.pl_report_frame, bg=COLORS["bg_secondary"], padx=20, pady=10)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
        
        current_time = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        footer_label = tk.Label(footer_frame,
                           text=f"Report generated on {current_time}",
                           font=FONTS["regular_small"],
                           bg=COLORS["bg_secondary"],
                           fg=COLORS["text_primary"])
        footer_label.pack(side=tk.RIGHT)
        
        # Store for export
        self.pl_report_data = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "total_revenue": total_revenue,
            "total_discount": total_discount,
            "total_tax": total_tax,
            "net_revenue": net_revenue,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": profit_margin
        }
    
    def create_pl_section(self, parent, section_title, items):
        """Create a section in the profit & loss report with more modern styling"""
        # Create a card-like frame with slight elevation styling
        section_card = tk.Frame(parent, 
                             bg=COLORS["bg_white"], 
                             padx=5, 
                             pady=5,
                             relief=tk.GROOVE,
                             bd=1)
        section_card.pack(fill=tk.X, padx=20, pady=10)
        
        # Inner section frame with padding
        section_frame = tk.Frame(section_card, bg=COLORS["bg_white"], padx=15, pady=10)
        section_frame.pack(fill=tk.X, expand=True)
        
        # Add section title with a colored background highlight
        title_frame = tk.Frame(section_frame, bg=COLORS["primary_light"], padx=15, pady=8)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = tk.Label(title_frame,
                       text=section_title,
                       font=FONTS["subheading"],
                       bg=COLORS["primary_light"],
                       fg=COLORS["text_white"])
        title.pack(anchor="w")
        
        # Add section items with enhanced styling
        for item in items:
            # Different background for summary items
            bg_color = COLORS.get("bg_light", COLORS["bg_secondary"]) if item.get("bold", False) else COLORS["bg_white"]
            
            item_frame = tk.Frame(section_frame, bg=bg_color, padx=5, pady=8)
            item_frame.pack(fill=tk.X, pady=2)
            
            # Label
            label_font = FONTS["regular_bold"] if item.get("bold", False) else FONTS["regular"]
            padx = 20 if item.get("indent", False) else 0
            
            label = tk.Label(item_frame,
                           text=item["label"],
                           font=label_font,
                           bg=bg_color,
                           fg=COLORS["text_primary"])
            label.pack(side=tk.LEFT, padx=(padx, 0))
            
            # Value with enhanced styling
            if item.get("is_percent", False):
                value_text = item["value"]
            else:
                if item.get("negative", False) and float(item["value"]) > 0:
                    value_text = f"-{format_currency(item['value'])}"
                else:
                    value_text = format_currency(item["value"])
            
            # Use more visual color coding for important values
            value_color = COLORS["danger"] if item.get("negative", False) else COLORS["text_primary"]
            if item.get("bold", False):
                if float(item["value"]) < 0:
                    value_color = COLORS["danger"]
                else:
                    value_color = COLORS["success"]
                    
                # Add a colored pill/bubble for key metrics
                value_frame = tk.Frame(item_frame, 
                                    bg=value_color,
                                    padx=10,
                                    pady=3,
                                    relief=tk.FLAT)
                value_frame.pack(side=tk.RIGHT)
                
                value = tk.Label(value_frame,
                               text=value_text,
                               font=label_font,
                               bg=value_color,
                               fg=COLORS["text_white"])
                value.pack()
            else:
                # Regular item value
                value = tk.Label(item_frame,
                               text=value_text,
                               font=label_font,
                               bg=bg_color,
                               fg=value_color)
                value.pack(side=tk.RIGHT)
        
        # No need for a separator with our new card-based design
    
    def export_profit_loss(self):
        """Export profit & loss report to Excel"""
        # Check if report has been generated
        if not hasattr(self, 'pl_report_data'):
            messagebox.showinfo("Export", "Please generate a report first.")
            return
        
        # Get date range for filename
        start_date = self.pl_report_data["start_date"]
        end_date = self.pl_report_data["end_date"]
        
        # Prepare data for Excel
        data = {
            "Category": [
                "Gross Revenue",
                "Tax Collected",
                "Discounts Given",
                "Net Revenue",
                "Cost of Goods Sold",
                "Gross Profit",
                "Operating Expenses",
                "Net Profit",
                "Profit Margin (%)"
            ],
            "Amount": [
                self.pl_report_data["total_revenue"],
                self.pl_report_data["total_tax"],
                -self.pl_report_data["total_discount"],
                self.pl_report_data["net_revenue"],
                -self.pl_report_data["total_cogs"],
                self.pl_report_data["gross_profit"],
                -self.pl_report_data["total_expenses"],
                self.pl_report_data["net_profit"],
                self.pl_report_data["profit_margin"]
            ]
        }
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"Profit_Loss_{start_date}_to_{end_date}.xlsx"
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, "Profit & Loss"):
            messagebox.showinfo("Export", "Report exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export report.")
    
    def setup_cash_flow_tab(self):
        """Setup cash flow tab"""
        # Main container
        container = tk.Frame(self.cash_flow_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(container, bg=COLORS["bg_primary"], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)  # Don't shrink
        
        # Right panel - Report
        right_panel = tk.Frame(container, bg=COLORS["bg_white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Date range controls
        date_frame = tk.LabelFrame(left_panel, 
                                 text="Date Range",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range options
        date_ranges = [
            "This Month", 
            "Last Month", 
            "This Quarter", 
            "Custom Range"
        ]
        
        # Create radio buttons for date ranges
        self.cf_date_range_var = tk.StringVar(value="This Month")
        
        for date_range in date_ranges:
            rb = tk.Radiobutton(date_frame, 
                              text=date_range,
                              variable=self.cf_date_range_var,
                              value=date_range,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"],
                              command=self.toggle_cf_custom_date_range)
            rb.pack(anchor="w", padx=10, pady=2)
        
        # Custom date range frame
        self.cf_custom_date_frame = tk.Frame(date_frame, bg=COLORS["bg_primary"], padx=10)
        
        # Start date
        start_label = tk.Label(self.cf_custom_date_frame, 
                             text="Start Date (YYYY-MM-DD):",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        start_label.pack(anchor="w", pady=(10, 5))
        
        self.cf_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(self.cf_custom_date_frame, 
                                  textvariable=self.cf_start_date_var,
                                  font=FONTS["regular"],
                                  width=15)
        start_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # End date
        end_label = tk.Label(self.cf_custom_date_frame, 
                           text="End Date (YYYY-MM-DD):",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        end_label.pack(anchor="w", pady=(0, 5))
        
        self.cf_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(self.cf_custom_date_frame, 
                                textvariable=self.cf_end_date_var,
                                font=FONTS["regular"],
                                width=15)
        end_date_entry.pack(fill=tk.X)
        
        # Generate report button
        generate_btn = tk.Button(left_panel,
                               text="Generate Report",
                               font=FONTS["regular_bold"],
                               bg=COLORS["primary"],
                               fg=COLORS["text_white"],
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.load_cash_flow)
        generate_btn.pack(padx=10, pady=15)
        
        # Export button
        export_btn = tk.Button(left_panel,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.export_cash_flow)
        export_btn.pack(padx=10, pady=5)
        
        # Initial state - hide custom date frame
        self.toggle_cf_custom_date_range()
        
        # Create scrollable frame for report
        canvas = tk.Canvas(right_panel, bg=COLORS["bg_white"])
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        
        self.cf_report_frame = tk.Frame(canvas, bg=COLORS["bg_white"])
        self.cf_report_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.cf_report_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_cf_custom_date_range(self):
        """Show/hide custom date range inputs for cash flow tab"""
        if self.cf_date_range_var.get() == "Custom Range":
            # Set default date range (last 30 days)
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            self.cf_start_date_var.set(thirty_days_ago.strftime("%Y-%m-%d"))
            self.cf_end_date_var.set(today.strftime("%Y-%m-%d"))
            
            # Show custom date frame
            self.cf_custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            # Hide custom date frame
            self.cf_custom_date_frame.pack_forget()
    
    def get_cf_date_range(self):
        """Get start and end dates for cash flow report"""
        date_range = self.cf_date_range_var.get()
        today = datetime.date.today()
        
        if date_range == "This Month":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        
        elif date_range == "Last Month":
            start_of_this_month = today.replace(day=1)
            end_of_last_month = start_of_this_month - datetime.timedelta(days=1)
            start_of_last_month = end_of_last_month.replace(day=1)
            return start_of_last_month, end_of_last_month
        
        elif date_range == "This Quarter":
            current_quarter = (today.month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start_of_quarter = today.replace(month=start_month, day=1)
            return start_of_quarter, today
        
        elif date_range == "Custom Range":
            try:
                start_date = datetime.datetime.strptime(self.cf_start_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.cf_end_date_var.get(), "%Y-%m-%d").date()
                
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
    
    def load_cash_flow(self):
        """Load and display cash flow report"""
        # Get date range
        start_date, end_date = self.get_cf_date_range()
        
        # Format dates for SQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Clear existing report
        for widget in self.cf_report_frame.winfo_children():
            widget.destroy()
        
        # Add title
        title = tk.Label(self.cf_report_frame,
                       text=f"Cash Flow Statement",
                       font=FONTS["heading"],
                       bg=COLORS["bg_white"],
                       fg=COLORS["text_primary"])
        title.pack(pady=(20, 5))
        
        # Add date range
        date_label = tk.Label(self.cf_report_frame,
                            text=f"From {start_date_str} to {end_date_str}",
                            font=FONTS["regular_italic"],
                            bg=COLORS["bg_white"],
                            fg=COLORS["text_primary"])
        date_label.pack(pady=(0, 20))
        
        # Get cash inflow data
        cash_inflow_query = """
            SELECT 
                SUM(cash_amount) as cash_sales,
                SUM(upi_amount) as upi_sales,
                COUNT(*) as num_transactions
            FROM invoices
            WHERE 
                DATE(invoice_date) BETWEEN ? AND ? AND
                payment_status = 'PAID'
        """
        cash_inflow_data = self.controller.db.fetchone(cash_inflow_query, (start_date_str, end_date_str))
        
        # Get cash outflow data
        cash_outflow_query = """
            SELECT 
                SUM(amount) as total_expenses,
                COUNT(*) as num_expenses
            FROM expenses
            WHERE DATE(expense_date) BETWEEN ? AND ?
        """
        cash_outflow_data = self.controller.db.fetchone(cash_outflow_query, (start_date_str, end_date_str))
        
        # Extract values (handle None values)
        cash_sales = cash_inflow_data[0] if cash_inflow_data and cash_inflow_data[0] else 0
        upi_sales = cash_inflow_data[1] if cash_inflow_data and cash_inflow_data[1] else 0
        num_transactions = cash_inflow_data[2] if cash_inflow_data and cash_inflow_data[2] else 0
        
        total_expenses = cash_outflow_data[0] if cash_outflow_data and cash_outflow_data[0] else 0
        num_expenses = cash_outflow_data[1] if cash_outflow_data and cash_outflow_data[1] else 0
        
        # Calculate totals
        total_inflow = cash_sales + upi_sales
        net_cash_flow = total_inflow - total_expenses
        
        # Create report sections
        self.create_cf_section(self.cf_report_frame, "Cash Inflows", [
            {"label": "Cash Sales", "value": cash_sales},
            {"label": "UPI Sales", "value": upi_sales},
            {"label": "Total Sales Transactions", "value": num_transactions, "is_count": True},
            {"label": "Total Cash Inflow", "value": total_inflow, "bold": True}
        ])
        
        self.create_cf_section(self.cf_report_frame, "Cash Outflows", [
            {"label": "Total Expenses", "value": total_expenses, "negative": True},
            {"label": "Number of Expenses", "value": num_expenses, "is_count": True},
            {"label": "Total Cash Outflow", "value": total_expenses, "bold": True, "negative": True}
        ])
        
        self.create_cf_section(self.cf_report_frame, "Net Cash Flow", [
            {"label": "Net Cash Flow", "value": net_cash_flow, "bold": True}
        ])
        
        # Store for export
        self.cf_report_data = {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "cash_sales": cash_sales,
            "upi_sales": upi_sales,
            "num_transactions": num_transactions,
            "total_inflow": total_inflow,
            "total_expenses": total_expenses,
            "num_expenses": num_expenses,
            "net_cash_flow": net_cash_flow
        }
    
    def create_cf_section(self, parent, section_title, items):
        """Create a section in the cash flow report"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_white"], padx=20, pady=10)
        section_frame.pack(fill=tk.X)
        
        # Add section title
        title = tk.Label(section_frame,
                       text=section_title,
                       font=FONTS["subheading"],
                       bg=COLORS["bg_white"],
                       fg=COLORS["text_primary"])
        title.pack(anchor="w", pady=(0, 10))
        
        # Add section items
        for item in items:
            item_frame = tk.Frame(section_frame, bg=COLORS["bg_white"])
            item_frame.pack(fill=tk.X, pady=2)
            
            # Label
            label_font = FONTS["regular_bold"] if item.get("bold", False) else FONTS["regular"]
            
            label = tk.Label(item_frame,
                           text=item["label"],
                           font=label_font,
                           bg=COLORS["bg_white"],
                           fg=COLORS["text_primary"])
            label.pack(side=tk.LEFT)
            
            # Value
            if item.get("is_count", False):
                value_text = str(int(item["value"]))
            else:
                if item.get("negative", False) and float(item["value"]) > 0:
                    value_text = f"-{format_currency(item['value'])}"
                else:
                    value_text = format_currency(item["value"])
            
            value_color = COLORS["danger"] if item.get("negative", False) else COLORS["text_primary"]
            if item.get("bold", False):
                if float(item["value"]) < 0:
                    value_color = COLORS["danger"]
                elif float(item["value"]) > 0:
                    value_color = COLORS["success"]
            
            value = tk.Label(item_frame,
                           text=value_text,
                           font=label_font,
                           bg=COLORS["bg_white"],
                           fg=value_color)
            value.pack(side=tk.RIGHT)
        
        # Add separator
        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill=tk.X, padx=20, pady=10)
    
    def export_cash_flow(self):
        """Export cash flow report to Excel"""
        # Check if report has been generated
        if not hasattr(self, 'cf_report_data'):
            messagebox.showinfo("Export", "Please generate a report first.")
            return
        
        # Get date range for filename
        start_date = self.cf_report_data["start_date"]
        end_date = self.cf_report_data["end_date"]
        
        # Prepare data for Excel
        data = {
            "Category": [
                "Cash Sales",
                "UPI Sales",
                "Total Sales Transactions",
                "Total Cash Inflow",
                "Total Expenses",
                "Number of Expenses",
                "Total Cash Outflow",
                "Net Cash Flow"
            ],
            "Amount": [
                self.cf_report_data["cash_sales"],
                self.cf_report_data["upi_sales"],
                self.cf_report_data["num_transactions"],
                self.cf_report_data["total_inflow"],
                -self.cf_report_data["total_expenses"],
                self.cf_report_data["num_expenses"],
                -self.cf_report_data["total_expenses"],
                self.cf_report_data["net_cash_flow"]
            ]
        }
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"Cash_Flow_{start_date}_to_{end_date}.xlsx"
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, "Cash Flow"):
            messagebox.showinfo("Export", "Report exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export report.")
    
    def setup_expenses_tab(self):
        """Setup expenses management tab"""
        # Main container with two frames side by side
        main_container = tk.Frame(self.expenses_tab, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Expense list
        left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Add/Edit expense
        right_panel = tk.Frame(main_container, bg=COLORS["bg_secondary"], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_panel.pack_propagate(False)  # Don't shrink
        
        # Setup expenses list
        self.setup_expense_list(left_panel)
        
        # Setup expense form
        self.setup_expense_form(right_panel)
    
    def setup_expense_list(self, parent):
        """Setup the expense list panel"""
        # Top controls frame
        controls_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Title
        title = tk.Label(controls_frame, 
                       text="Expenses",
                       font=FONTS["subheading"],
                       bg=COLORS["bg_primary"],
                       fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=10)
        
        # Search field
        search_frame = tk.Frame(controls_frame, bg=COLORS["bg_primary"])
        search_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(search_frame, 
               text="Search:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(0, 5))
        
        self.expense_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                              textvariable=self.expense_search_var,
                              font=FONTS["regular"],
                              width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", lambda event: self.search_expenses())
        
        search_btn = tk.Button(search_frame,
                             text="Search",
                             font=FONTS["regular"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=5,
                             pady=2,
                             cursor="hand2",
                             command=self.search_expenses)
        search_btn.pack(side=tk.LEFT)
        
        # Treeview frame
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
        
        # Create treeview for expenses
        self.expense_tree = ttk.Treeview(tree_frame, 
                                      columns=("id", "date", "category", "amount", "description"),
                                      show="headings",
                                      yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.expense_tree.yview)
        
        # Define columns
        self.expense_tree.heading("id", text="ID")
        self.expense_tree.heading("date", text="Date")
        self.expense_tree.heading("category", text="Category")
        self.expense_tree.heading("amount", text="Amount")
        self.expense_tree.heading("description", text="Description")
        
        # Set column widths
        self.expense_tree.column("id", width=50)
        self.expense_tree.column("date", width=100)
        self.expense_tree.column("category", width=150)
        self.expense_tree.column("amount", width=100)
        self.expense_tree.column("description", width=300)
        
        self.expense_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to edit
        self.expense_tree.bind("<Double-1>", self.edit_expense)
        # Bind right-click for context menu
        self.expense_tree.bind("<Button-3>", self.show_expense_context_menu)
        
        # Bottom controls frame
        bottom_frame = tk.Frame(parent, bg=COLORS["bg_primary"], pady=5)
        bottom_frame.pack(fill=tk.X)
        
        # Add expense button
        add_btn = tk.Button(bottom_frame,
                          text="Add New Expense",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          padx=15,
                          pady=5,
                          cursor="hand2",
                          command=self.add_expense)
        add_btn.pack(side=tk.LEFT, padx=10)
        
        # Delete expense button
        delete_btn = tk.Button(bottom_frame,
                             text="Delete Expense",
                             font=FONTS["regular_bold"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.delete_expense)
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        # Export button
        export_btn = tk.Button(bottom_frame,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.export_expenses)
        export_btn.pack(side=tk.RIGHT, padx=10)
    
    def setup_expense_form(self, parent):
        """Setup the expense form panel"""
        # Title
        title = tk.Label(parent, 
                       text="Expense Details",
                       font=FONTS["subheading"],
                       bg=COLORS["bg_secondary"],
                       fg=COLORS["text_primary"])
        title.pack(pady=(20, 10))
        
        # Form frame
        form_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], padx=20, pady=10)
        form_frame.pack(fill=tk.X)
        
        # Date
        tk.Label(form_frame, 
               text="Date:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", pady=10)
        
        self.expense_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(form_frame, 
                            textvariable=self.expense_date_var,
                            font=FONTS["regular"],
                            width=15)
        date_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Category
        tk.Label(form_frame, 
               text="Category:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", pady=10)
        
        # Get categories from database or use defaults
        expense_categories = self.get_expense_categories()
        
        self.expense_category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, 
                                     textvariable=self.expense_category_var,
                                     values=expense_categories,
                                     font=FONTS["regular"],
                                     width=20)
        category_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Amount
        tk.Label(form_frame, 
               text="Amount:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", pady=10)
        
        self.expense_amount_var = tk.StringVar()
        amount_entry = tk.Entry(form_frame, 
                              textvariable=self.expense_amount_var,
                              font=FONTS["regular"],
                              width=15)
        amount_entry.grid(row=2, column=1, sticky="w", pady=10)
        
        # Description
        tk.Label(form_frame, 
               text="Description:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_secondary"],
               fg=COLORS["text_primary"]).grid(row=3, column=0, sticky="w", pady=10)
        
        self.expense_description_var = tk.StringVar()
        description_entry = tk.Entry(form_frame, 
                                   textvariable=self.expense_description_var,
                                   font=FONTS["regular"],
                                   width=25)
        description_entry.grid(row=3, column=1, sticky="w", pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(parent, bg=COLORS["bg_secondary"], pady=20)
        btn_frame.pack()
        
        # Save button
        self.save_expense_btn = tk.Button(btn_frame,
                                      text="Save Expense",
                                      font=FONTS["regular_bold"],
                                      bg=COLORS["primary"],
                                      fg=COLORS["text_white"],
                                      padx=15,
                                      pady=5,
                                      cursor="hand2",
                                      command=self.save_expense)
        self.save_expense_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        self.cancel_expense_btn = tk.Button(btn_frame,
                                         text="Cancel",
                                         font=FONTS["regular"],
                                         bg=COLORS["bg_white"],
                                         fg=COLORS["text_primary"],
                                         padx=15,
                                         pady=5,
                                         cursor="hand2",
                                         command=self.reset_expense_form)
        self.cancel_expense_btn.pack(side=tk.LEFT, padx=5)
        
        # Store the expense ID for editing (None for new expense)
        self.current_expense_id = None
    
    def get_expense_categories(self):
        """Get list of expense categories from database"""
        # First, get categories from existing expenses
        query = """
            SELECT DISTINCT category 
            FROM expenses 
            ORDER BY category
        """
        categories = [row[0] for row in self.controller.db.fetchall(query) if row[0]]
        
        # Add default categories if not enough
        default_categories = [
            "Rent", 
            "Utilities", 
            "Salaries", 
            "Supplies", 
            "Maintenance", 
            "Transport",
            "Marketing",
            "Miscellaneous"
        ]
        
        for category in default_categories:
            if category not in categories:
                categories.append(category)
        
        return categories
    
    def load_expenses(self):
        """Load expenses into the treeview"""
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Get expenses from database
        query = """
            SELECT 
                id,
                expense_date,
                category,
                amount,
                description
            FROM 
                expenses
            ORDER BY 
                expense_date DESC
        """
        expenses = self.controller.db.fetchall(query)
        
        # Insert into treeview
        for expense in expenses:
            expense_id, date_str, category, amount, description = expense
            
            # Format date
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                date_formatted = date_str
            
            self.expense_tree.insert("", "end", values=(
                expense_id,
                date_formatted,
                category,
                format_currency(amount),
                description or ""
            ))
    
    def search_expenses(self):
        """Search expenses based on search term"""
        search_term = self.expense_search_var.get().strip()
        
        if not search_term:
            # If search is empty, load all expenses
            self.load_expenses()
            return
        
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Search expenses
        query = """
            SELECT 
                id,
                expense_date,
                category,
                amount,
                description
            FROM 
                expenses
            WHERE 
                category LIKE ? OR
                description LIKE ?
            ORDER BY 
                expense_date DESC
        """
        search_pattern = f"%{search_term}%"
        expenses = self.controller.db.fetchall(query, (search_pattern, search_pattern))
        
        # Insert into treeview
        for expense in expenses:
            expense_id, date_str, category, amount, description = expense
            
            # Format date
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                date_formatted = date_str
            
            self.expense_tree.insert("", "end", values=(
                expense_id,
                date_formatted,
                category,
                format_currency(amount),
                description or ""
            ))
    
    def add_expense(self):
        """Prepare form for adding a new expense"""
        # Reset form
        self.reset_expense_form()
        
        # Set current expense ID to None (new expense)
        self.current_expense_id = None
        
        # Update button text
        self.save_expense_btn.config(text="Add Expense")
    
    def edit_expense(self, event=None):
        """Load selected expense for editing"""
        selection = self.expense_tree.selection()
        if not selection:
            return
        
        # Get expense data
        expense_values = self.expense_tree.item(selection[0], "values")
        expense_id = expense_values[0]
        
        # Get expense details from database
        query = """
            SELECT 
                expense_date,
                category,
                amount,
                description
            FROM 
                expenses
            WHERE 
                id = ?
        """
        expense = self.controller.db.fetchone(query, (expense_id,))
        
        if not expense:
            messagebox.showerror("Error", "Expense not found.")
            return
        
        # Set form values
        self.expense_date_var.set(expense[0])
        self.expense_category_var.set(expense[1])
        self.expense_amount_var.set(str(expense[2]))
        self.expense_description_var.set(expense[3] or "")
        
        # Set current expense ID
        self.current_expense_id = expense_id
        
        # Update button text
        self.save_expense_btn.config(text="Update Expense")
    
    def save_expense(self):
        """Save or update expense with improved validation and error handling"""
        try:
            # Validate date
            date_str = self.expense_date_var.get().strip()
            if not date_str:
                messagebox.showerror("Required Field", "Date is required.")
                return
                
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # Validate date is not in the future
                if date_obj > datetime.datetime.now().date():
                    if not messagebox.askyesno("Date Validation", 
                                             "The date is in the future. Are you sure you want to continue?"):
                        return
                        
                date_str = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
                return
            
            # Validate category
            category = self.expense_category_var.get().strip()
            if not category:
                messagebox.showerror("Required Field", "Category is required.")
                return
                
            # Prevent category values that are too long
            if len(category) > 50:
                messagebox.showerror("Invalid Category", "Category name is too long (maximum 50 characters).")
                return
            
            # Validate amount with better error messages
            amount_str = self.expense_amount_var.get().strip()
            if not amount_str:
                messagebox.showerror("Required Field", "Amount is required.")
                return
                
            try:
                # Try to handle different number formats
                amount_str = amount_str.replace(',', '')  # Remove commas
                
                # Remove currency symbol if present
                for symbol in ['₹', '$', '€', '£', '¥']:
                    amount_str = amount_str.replace(symbol, '')
                
                # Remove any whitespace
                amount_str = amount_str.strip()
                    
                # Parse the amount using decimal.Decimal for precise handling
                from decimal import Decimal
                amount = Decimal(amount_str)
                
                # Convert to float for storage in SQLite
                # This is because SQLite doesn't directly support Decimal type
                amount_float = float(amount)
                
                # Validate amount is positive
                if amount_float <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be greater than zero.")
                    return
                    
                # Validate amount is not unusually large (basic sanity check)
                if amount_float > 1000000:  # 10 lakh rupees
                    if not messagebox.askyesno("Amount Validation", 
                                             f"The amount ₹{amount_float:,.2f} is very large. Are you sure this is correct?"):
                        return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid amount (numbers only).")
                return
            
            # Get description
            description = self.expense_description_var.get().strip()
            
            # Limit description length
            if len(description) > 200:
                description = description[:200]
                messagebox.showwarning("Description Truncated", 
                                     "The description has been truncated to 200 characters.")
            
            # Prepare expense data
            expense_data = {
                "expense_date": date_str,
                "category": category,
                "amount": amount_float,  # Use the float value for storage
                "description": description
            }
            
            # Check if expenses table exists
            try:
                check_table = self.controller.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
                if not check_table.fetchone():
                    # Create the table if it doesn't exist
                    self.controller.db.execute("""
                        CREATE TABLE IF NOT EXISTS expenses (
                            id INTEGER PRIMARY KEY,
                            expense_date DATE NOT NULL,
                            category TEXT NOT NULL,
                            amount REAL NOT NULL,
                            description TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    self.controller.db.commit()
            except Exception as e:
                print(f"Error checking/creating expenses table: {e}")
                # Continue with insert attempt
            
            # Perform database operation in a try-except block
            try:
                if self.current_expense_id is None:
                    # Add new expense
                    expense_data["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result = self.controller.db.insert("expenses", expense_data)
                    
                    if result:
                        messagebox.showinfo("Success", "Expense added successfully.")
                    else:
                        messagebox.showerror("Error", "Failed to add expense.")
                        return
                else:
                    # Update existing expense
                    # Check if the expense still exists
                    check = self.controller.db.fetchone("SELECT id FROM expenses WHERE id = ?", (self.current_expense_id,))
                    if not check:
                        messagebox.showerror("Error", "This expense no longer exists in the database. It may have been deleted.")
                        self.reset_expense_form()
                        self.load_expenses()
                        return
                        
                    # Proceed with update
                    result = self.controller.db.update("expenses", expense_data, f"id = {self.current_expense_id}")
                    
                    if result:
                        messagebox.showinfo("Success", "Expense updated successfully.")
                    else:
                        messagebox.showerror("Error", "Failed to update expense.")
                        return
            except Exception as db_error:
                # Handle database errors specifically
                error_msg = str(db_error)
                if "no such table" in error_msg.lower():
                    messagebox.showerror("Database Error", "The expenses table does not exist. Please contact support.")
                elif "constraint failed" in error_msg.lower():
                    messagebox.showerror("Validation Error", "One of the values violates database constraints.")
                else:
                    messagebox.showerror("Database Error", f"An error occurred while saving: {error_msg}")
                return
            
            # Reset form
            self.reset_expense_form()
            
            # Reload expenses
            self.load_expenses()
            
        except Exception as e:
            # Log the full error for debugging
            print(f"Expense save error: {str(e)}")
            print(f"Error details: {traceback.format_exc()}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def delete_expense(self):
        """Delete selected expense with improved error handling"""
        try:
            selection = self.expense_tree.selection()
            if not selection:
                messagebox.showinfo("Select Expense", "Please select an expense to delete.")
                return
            
            # Get expense values from tree
            tree_values = self.expense_tree.item(selection[0], "values")
            if not tree_values or len(tree_values) < 1:
                messagebox.showerror("Error", "Could not retrieve expense information.")
                return
            
            # Get expense ID
            try:
                expense_id = int(tree_values[0])
            except (ValueError, TypeError):
                messagebox.showerror("Error", "Invalid expense ID.")
                return
            
            # Get expense details for confirmation
            try:
                expense_query = "SELECT expense_date, category, amount FROM expenses WHERE id = ?"
                expense_details = self.controller.db.fetchone(expense_query, (expense_id,))
                
                if not expense_details:
                    messagebox.showerror("Error", "This expense no longer exists in the database.")
                    self.load_expenses()  # Refresh the list
                    return
                    
                expense_date, category, amount = expense_details
                
                # Confirm deletion with details
                if not messagebox.askyesno("Confirm Delete", 
                                        f"Are you sure you want to delete this expense?\n\n"
                                        f"Date: {expense_date}\n"
                                        f"Category: {category}\n"
                                        f"Amount: ₹{amount:,.2f}"):
                    return
            except Exception as e:
                # If we can't get details, use a simpler confirmation
                print(f"Error fetching expense details: {e}")
                if not messagebox.askyesno("Confirm Delete", 
                                        "Are you sure you want to delete this expense?"):
                    return
            
            # Delete expense with proper error handling
            try:
                result = self.controller.db.delete("expenses", f"id = {expense_id}")
                
                if result:
                    messagebox.showinfo("Success", "Expense deleted successfully.")
                    
                    # Reset form if the deleted expense was being edited
                    if self.current_expense_id == expense_id:
                        self.reset_expense_form()
                        
                    # Reload expenses
                    self.load_expenses()
                else:
                    messagebox.showerror("Error", "Failed to delete expense.")
            except Exception as db_error:
                error_msg = str(db_error)
                if "no such table" in error_msg.lower():
                    messagebox.showerror("Database Error", "The expenses table does not exist.")
                elif "constraint failed" in error_msg.lower():
                    messagebox.showerror("Constraint Error", 
                                      "Cannot delete this expense because it is referenced by other records.")
                else:
                    messagebox.showerror("Database Error", f"Failed to delete expense: {error_msg}")
        except Exception as e:
            # Catch any unexpected errors
            print(f"Unexpected error in delete_expense: {e}")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def reset_expense_form(self):
        """Reset expense form to default values"""
        self.expense_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.expense_category_var.set("")
        self.expense_amount_var.set("")
        self.expense_description_var.set("")
        
        # Reset current expense ID
        self.current_expense_id = None
        
        # Update button text
        self.save_expense_btn.config(text="Save Expense")
    
    def show_expense_context_menu(self, event):
        """Show context menu for expense treeview"""
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit Expense", command=self.edit_expense)
        menu.add_command(label="Delete Expense", command=self.delete_expense)
        
        # Display menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def export_expenses(self):
        """Export expenses to Excel"""
        # Get all expenses
        query = """
            SELECT 
                id,
                expense_date,
                category,
                amount,
                description,
                created_at
            FROM 
                expenses
            ORDER BY 
                expense_date DESC
        """
        expenses = self.controller.db.fetchall(query)
        
        if not expenses:
            messagebox.showinfo("Export", "No expenses to export.")
            return
        
        # Prepare data for Excel
        data = {
            "ID": [],
            "Date": [],
            "Category": [],
            "Amount": [],
            "Description": [],
            "Created At": []
        }
        
        for expense in expenses:
            data["ID"].append(expense[0])
            data["Date"].append(expense[1])
            data["Category"].append(expense[2])
            data["Amount"].append(expense[3])
            data["Description"].append(expense[4] or "")
            data["Created At"].append(expense[5])
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="Expenses_Report.xlsx"
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, "Expenses"):
            messagebox.showinfo("Export", "Expenses exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export expenses.")
    
    def setup_ledger_tab(self):
        """Setup customer/supplier ledger tab"""
        # Main container
        container = tk.Frame(self.ledger_tab, bg=COLORS["bg_primary"])
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top controls frame
        controls_frame = tk.Frame(container, bg=COLORS["bg_primary"])
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Label
        tk.Label(controls_frame, 
               text="Select Ledger Type:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Ledger type selection
        self.ledger_type_var = tk.StringVar(value="customer")
        
        customer_rb = tk.Radiobutton(controls_frame, 
                                   text="Customer Ledger",
                                   variable=self.ledger_type_var,
                                   value="customer",
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   selectcolor=COLORS["bg_primary"],
                                   command=self.load_ledger_entities)
        customer_rb.pack(side=tk.LEFT, padx=10)
        
        supplier_rb = tk.Radiobutton(controls_frame, 
                                   text="Supplier Ledger",
                                   variable=self.ledger_type_var,
                                   value="supplier",
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   selectcolor=COLORS["bg_primary"],
                                   command=self.load_ledger_entities)
        supplier_rb.pack(side=tk.LEFT, padx=10)
        
        # Entity selection frame
        entity_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        entity_frame.pack(fill=tk.X)
        
        tk.Label(entity_frame, 
               text="Select Entity:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Entity dropdown
        self.entity_var = tk.StringVar()
        self.entity_dropdown = ttk.Combobox(entity_frame, 
                                          textvariable=self.entity_var,
                                          font=FONTS["regular"],
                                          width=30,
                                          state="readonly")
        self.entity_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Load button
        load_btn = tk.Button(entity_frame,
                           text="Load Ledger",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=10,
                           pady=2,
                           cursor="hand2",
                           command=self.load_ledger)
        load_btn.pack(side=tk.LEFT, padx=10)
        
        # Date range frame
        date_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=5)
        date_frame.pack(fill=tk.X)
        
        tk.Label(date_frame, 
               text="Date Range:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Start date
        tk.Label(date_frame, 
               text="From:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(10, 5))
        
        self.ledger_start_date_var = tk.StringVar()
        # Set default to 3 months ago
        start_date = datetime.date.today().replace(day=1) - datetime.timedelta(days=90)
        self.ledger_start_date_var.set(start_date.strftime("%Y-%m-%d"))
        
        start_date_entry = tk.Entry(date_frame, 
                                  textvariable=self.ledger_start_date_var,
                                  font=FONTS["regular"],
                                  width=12)
        start_date_entry.pack(side=tk.LEFT)
        
        # End date
        tk.Label(date_frame, 
               text="To:",
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(10, 5))
        
        self.ledger_end_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        end_date_entry = tk.Entry(date_frame, 
                                textvariable=self.ledger_end_date_var,
                                font=FONTS["regular"],
                                width=12)
        end_date_entry.pack(side=tk.LEFT)
        
        # Ledger treeview frame
        tree_frame = tk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for ledger
        self.ledger_tree = ttk.Treeview(tree_frame, 
                                     columns=("date", "ref", "description", "debit", "credit", "balance"),
                                     show="headings",
                                     yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.ledger_tree.yview)
        
        # Define columns
        self.ledger_tree.heading("date", text="Date")
        self.ledger_tree.heading("ref", text="Reference")
        self.ledger_tree.heading("description", text="Description")
        self.ledger_tree.heading("debit", text="Debit")
        self.ledger_tree.heading("credit", text="Credit")
        self.ledger_tree.heading("balance", text="Balance")
        
        # Set column widths
        self.ledger_tree.column("date", width=100)
        self.ledger_tree.column("ref", width=100)
        self.ledger_tree.column("description", width=300)
        self.ledger_tree.column("debit", width=100)
        self.ledger_tree.column("credit", width=100)
        self.ledger_tree.column("balance", width=100)
        
        self.ledger_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bottom controls frame
        bottom_frame = tk.Frame(container, bg=COLORS["bg_primary"], pady=10)
        bottom_frame.pack(fill=tk.X)
        
        # Summary frame
        summary_frame = tk.Frame(bottom_frame, bg=COLORS["bg_primary"])
        summary_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(summary_frame, 
               text="Total Debit:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", padx=5)
        
        self.total_debit_label = tk.Label(summary_frame, 
                                        text="₹0.00",
                                        font=FONTS["regular"],
                                        bg=COLORS["bg_primary"],
                                        fg=COLORS["text_primary"])
        self.total_debit_label.grid(row=0, column=1, sticky="w", padx=5)
        
        tk.Label(summary_frame, 
               text="Total Credit:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=1, column=0, sticky="w", padx=5)
        
        self.total_credit_label = tk.Label(summary_frame, 
                                         text="₹0.00",
                                         font=FONTS["regular"],
                                         bg=COLORS["bg_primary"],
                                         fg=COLORS["text_primary"])
        self.total_credit_label.grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(summary_frame, 
               text="Current Balance:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).grid(row=2, column=0, sticky="w", padx=5)
        
        self.current_balance_label = tk.Label(summary_frame, 
                                           text="₹0.00",
                                           font=FONTS["regular_bold"],
                                           bg=COLORS["bg_primary"],
                                           fg=COLORS["text_primary"])
        self.current_balance_label.grid(row=2, column=1, sticky="w", padx=5)
        
        # Export button
        export_btn = tk.Button(bottom_frame,
                             text="Export to Excel",
                             font=FONTS["regular"],
                             bg=COLORS["secondary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=5,
                             cursor="hand2",
                             command=self.export_ledger)
        export_btn.pack(side=tk.RIGHT, padx=10)
        
        # Load initial data
        self.load_ledger_entities()
    
    def load_ledger_entities(self):
        """Load entities (customers or suppliers) into dropdown"""
        ledger_type = self.ledger_type_var.get()
        
        if ledger_type == "customer":
            # Load customers
            query = "SELECT id, name FROM customers ORDER BY name"
            entities = self.controller.db.fetchall(query)
            
            # Format for dropdown
            entity_list = [f"{name} (ID: {id})" for id, name in entities]
            
            # Update dropdown
            self.entity_dropdown["values"] = entity_list
            
            if entity_list:
                self.entity_dropdown.current(0)
        else:
            # Load vendors from database
            try:
                query = "SELECT id, name FROM vendors ORDER BY name"
                entities = self.controller.db.fetchall(query)
                
                # Format for dropdown
                entity_list = [f"{name} (ID: {id})" for id, name in entities]
                
                # Update dropdown
                self.entity_dropdown["values"] = entity_list
                
                if entity_list:
                    self.entity_dropdown.current(0)
                else:
                    # If no vendors found, show a placeholder
                    self.entity_dropdown["values"] = ["No vendors available"]
                    self.entity_dropdown.current(0)
            except Exception as e:
                print(f"Error loading vendors: {e}")
                # Fallback to empty list
                self.entity_dropdown["values"] = ["No vendors available"]
                self.entity_dropdown.current(0)
    
    def load_ledger(self):
        """Load ledger for selected entity"""
        entity = self.entity_var.get()
        if not entity:
            messagebox.showinfo("Select Entity", "Please select an entity.")
            return
            
        if entity == "No vendors available":
            messagebox.showinfo("No Vendors", "Please add vendors first in Inventory Management.")
            return
        
        # Clear existing items
        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)
        
        # Get entity ID (for both customer and vendor)
        entity_id = None
        try:
            # Extract ID from dropdown text (ID: X)
            entity_id = int(entity.split("(ID: ")[1].split(")")[0])
        except:
            # If parsing fails, show error
            messagebox.showerror("Error", "Invalid entity selection.")
            return
        
        # Get date range
        try:
            start_date = datetime.datetime.strptime(self.ledger_start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(self.ledger_end_date_var.get(), "%Y-%m-%d").date()
            
            # Validate dates
            if start_date > end_date:
                messagebox.showerror("Date Error", "Start date cannot be after end date.")
                return
                
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
        except ValueError:
            messagebox.showerror("Date Error", "Please enter valid dates in YYYY-MM-DD format.")
            return
        
        # Load ledger data based on type
        if self.ledger_type_var.get() == "customer":
            self.load_customer_ledger(entity_id, start_date_str, end_date_str)
        else:
            self.load_supplier_ledger(entity_id, start_date_str, end_date_str)
    
    def load_customer_ledger(self, customer_id, start_date, end_date):
        """Load customer ledger data"""
        # Get opening balance (all transactions before start date)
        opening_balance_query = """
            SELECT 
                COALESCE(SUM(CASE WHEN payment_status IN ('PAID', 'FULLY_PAID') THEN 0 ELSE credit_amount END), 0) as opening_balance 
            FROM 
                invoices 
            WHERE 
                customer_id = ? AND 
                DATE(invoice_date) < ? AND
                credit_amount > 0
        """
        opening_balance_data = self.controller.db.fetchone(opening_balance_query, (customer_id, start_date))
        opening_balance = opening_balance_data[0] if opening_balance_data and opening_balance_data[0] else 0
        
        # Add opening balance row
        self.ledger_tree.insert("", "end", values=(
            start_date,
            "",
            "Opening Balance",
            "",
            "",
            format_currency(opening_balance)
        ))
        
        # Get ledger transactions
        transactions_query = """
            SELECT 
                DATE(invoice_date) as date,
                invoice_number as reference,
                CASE 
                    WHEN payment_status = 'PAID' THEN 'Payment received'
                    ELSE 'Invoice generated' 
                END as description,
                0 as debit,
                credit_amount as credit
            FROM 
                invoices 
            WHERE 
                customer_id = ? AND 
                DATE(invoice_date) BETWEEN ? AND ? AND
                credit_amount > 0
            
            UNION ALL
            
            -- Add payments made by customer
            SELECT 
                DATE(transaction_date) as date,
                reference_id as reference,
                'Payment received' as description,
                amount as debit,
                0 as credit
            FROM 
                credit_payments
            WHERE 
                customer_id = ? AND 
                DATE(transaction_date) BETWEEN ? AND ?
            
            ORDER BY 
                date, reference
        """
        
        # Improved transactions query to handle both credit invoices and credit payments
        transactions_query = """
            -- Get credit sales from invoices (both full credit and split payment with credit)
            SELECT 
                DATE(invoice_date) as date,
                invoice_number as reference,
                CASE 
                    WHEN payment_method = 'SPLIT' THEN 'Split payment with credit' 
                    ELSE 'Credit sale'
                END as description,
                0 as debit,
                credit_amount as credit
            FROM 
                invoices 
            WHERE 
                customer_id = ? AND 
                DATE(invoice_date) BETWEEN ? AND ? AND
                credit_amount > 0
                
            UNION ALL
            
            -- Add payments made by customer for credit
            SELECT 
                DATE(ct.transaction_date) as date,
                'PMT-' || ct.id as reference,
                'Payment received' as description,
                ct.amount as debit,
                0 as credit
            FROM 
                customer_transactions ct
            WHERE 
                ct.customer_id = ? AND 
                ct.transaction_type = 'CREDIT_PAYMENT' AND
                DATE(ct.transaction_date) BETWEEN ? AND ?
                
            ORDER BY 
                date, reference
        """
        
        transactions = self.controller.db.fetchall(transactions_query, (customer_id, start_date, end_date, customer_id, start_date, end_date))
        
        # Initialize running balance and totals
        balance = opening_balance
        total_debit = 0
        total_credit = 0
        
        # Add transactions to treeview
        for date, reference, description, debit, credit in transactions:
            # Update running balance
            balance = balance - debit + credit
            
            # Update totals
            total_debit += debit
            total_credit += credit
            
            # Add to treeview
            self.ledger_tree.insert("", "end", values=(
                date,
                reference,
                description,
                format_currency(debit) if debit else "",
                format_currency(credit) if credit else "",
                format_currency(balance)
            ))
        
        # Add closing balance row
        self.ledger_tree.insert("", "end", values=(
            end_date,
            "",
            "Closing Balance",
            "",
            "",
            format_currency(balance)
        ))
        
        # Update summary labels
        self.total_debit_label.config(text=format_currency(total_debit))
        self.total_credit_label.config(text=format_currency(total_credit))
        self.current_balance_label.config(text=format_currency(balance))
        
        # Set color for balance
        if balance > 0:
            self.current_balance_label.config(fg=COLORS["danger"])
        else:
            self.current_balance_label.config(fg=COLORS["text_primary"])
        
        # Store for export
        self.ledger_data = {
            "entity": self.entity_var.get(),
            "type": "Customer",
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "transactions": transactions,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": balance
        }
    
    def load_supplier_ledger(self, vendor_id, start_date, end_date):
        """Load supplier ledger data"""
        # Get vendor name for display
        vendor_query = "SELECT name FROM vendors WHERE id = ?"
        vendor_result = self.controller.db.fetchone(vendor_query, (vendor_id,))
        vendor_name = vendor_result[0] if vendor_result else f"Vendor ID: {vendor_id}"
        
        # Check if we have transaction data for this vendor
        has_transactions = False
        try:
            check_query = "SELECT COUNT(*) FROM supplier_transactions WHERE vendor_id = ?"
            count_result = self.controller.db.fetchone(check_query, (vendor_id,))
            has_transactions = count_result and count_result[0] > 0
        except Exception as e:
            # Table might not exist yet
            print(f"Error checking transactions: {str(e)}")
            
        # If we have transactions, load them; otherwise, create sample entry points
        if has_transactions:
            # Get opening balance (all transactions before start date)
            opening_balance_query = """
                SELECT 
                    SUM(credit) - SUM(debit) as opening_balance 
                FROM 
                    supplier_transactions 
                WHERE 
                    vendor_id = ? AND 
                    DATE(transaction_date) < ?
            """
            opening_balance_data = self.controller.db.fetchone(opening_balance_query, (vendor_id, start_date))
            opening_balance = opening_balance_data[0] if opening_balance_data and opening_balance_data[0] is not None else 0
            
            # Get transactions within date range
            transactions_query = """
                SELECT 
                    transaction_date,
                    reference_no,
                    description,
                    debit,
                    credit
                FROM 
                    supplier_transactions 
                WHERE 
                    vendor_id = ? AND 
                    DATE(transaction_date) BETWEEN ? AND ?
                ORDER BY 
                    transaction_date, id
            """
            transactions = self.controller.db.fetchall(transactions_query, (vendor_id, start_date, end_date))
        else:
            # Create entry points for recording supplier transactions
            opening_balance = 0
            transactions = []
            
            # Add some sample entry points for transactions
            self._add_supplier_transaction_entries(vendor_id)
            
        # Add opening balance row
        self.ledger_tree.insert("", "end", values=(
            start_date,
            "",
            "Opening Balance",
            "",
            "",
            format_currency(opening_balance)
        ))
        
        # Initialize running balance and totals
        balance = opening_balance
        total_debit = 0
        total_credit = 0
        
        # Add transactions to treeview
        for date, reference, description, debit, credit in transactions:
            # Update running balance
            balance = balance - debit + credit
            
            # Update totals
            total_debit += debit
            total_credit += credit
            
            # Add to treeview
            self.ledger_tree.insert("", "end", values=(
                date,
                reference if reference else "",
                description if description else "",
                format_currency(debit) if debit else "",
                format_currency(credit) if credit else "",
                format_currency(balance)
            ))
        
        # If there are no transactions, show a message in the tree
        if not transactions and not has_transactions:
            self.ledger_tree.insert("", "end", values=(
                "-",
                "-",
                "No transactions found. Use 'Record Transaction' to add entries.",
                "-",
                "-",
                "-"
            ))
        
        # Add closing balance row
        self.ledger_tree.insert("", "end", values=(
            end_date,
            "",
            "Closing Balance",
            "",
            "",
            format_currency(balance)
        ))
        
        # Update summary labels
        self.total_debit_label.config(text=format_currency(total_debit))
        self.total_credit_label.config(text=format_currency(total_credit))
        self.current_balance_label.config(text=format_currency(balance))
        
        # Set color for balance
        if balance > 0:
            self.current_balance_label.config(fg=COLORS["danger"])
        else:
            self.current_balance_label.config(fg=COLORS["text_primary"])
        
        # Add transaction recording button
        self._add_supplier_transaction_button(vendor_id, vendor_name)
        
        # Store for export
        self.ledger_data = {
            "entity": vendor_name,
            "type": "Supplier",
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "transactions": transactions,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": balance
        }
    
    def _add_supplier_transaction_entries(self, vendor_id):
        """Add initial transaction entries to the supplier_transactions table"""
        try:
            # Create the table if it doesn't exist
            self.controller.db.execute("""
                CREATE TABLE IF NOT EXISTS supplier_transactions (
                    id INTEGER PRIMARY KEY,
                    vendor_id INTEGER NOT NULL,
                    transaction_date DATE NOT NULL,
                    reference_no TEXT,
                    description TEXT,
                    debit REAL DEFAULT 0,
                    credit REAL DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
                )
            """)
            self.controller.db.commit()
        except Exception as e:
            print(f"Error creating supplier_transactions table: {str(e)}")
    
    def _add_supplier_transaction_button(self, vendor_id, vendor_name):
        """Add a button to record supplier transactions"""
        # Check if button already exists
        if hasattr(self, 'transaction_button_frame') and self.transaction_button_frame.winfo_exists():
            self.transaction_button_frame.destroy()
        
        # Create a frame for the button
        button_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        # Store a reference to identify the button frame later
        self.transaction_button_frame = button_frame
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, before=self.notebook)
        
        # Create the button
        record_btn = tk.Button(button_frame,
                             text="Record Supplier Transaction",
                             font=FONTS["regular"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             padx=15,
                             pady=8,
                             cursor="hand2",
                             relief=tk.FLAT,
                             command=lambda: self._record_supplier_transaction(vendor_id, vendor_name))
        record_btn.pack(side=tk.RIGHT, padx=5)
    
    def _record_supplier_transaction(self, vendor_id, vendor_name):
        """Open dialog to record a supplier transaction"""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Record Transaction - {vendor_name}")
        dialog.geometry("500x400")
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
                       text=f"Record Transaction for {vendor_name}",
                       font=FONTS["heading"],
                       bg=COLORS["bg_primary"],
                       fg=COLORS["text_primary"],
                       wraplength=460)
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Transaction type
        type_label = tk.Label(form_frame, 
                            text="Transaction Type:",
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        type_label.grid(row=0, column=0, sticky="w", pady=8)
        
        type_var = tk.StringVar(value="purchase")
        
        type_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        type_frame.grid(row=0, column=1, sticky="w", pady=8)
        
        purchase_rb = tk.Radiobutton(type_frame, 
                                   text="Purchase (Credit)",
                                   variable=type_var, 
                                   value="purchase",
                                   font=FONTS["regular"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"],
                                   selectcolor=COLORS["bg_primary"])
        purchase_rb.pack(side=tk.LEFT, padx=(0, 10))
        
        payment_rb = tk.Radiobutton(type_frame, 
                                  text="Payment (Debit)",
                                  variable=type_var, 
                                  value="payment",
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["text_primary"],
                                  selectcolor=COLORS["bg_primary"])
        payment_rb.pack(side=tk.LEFT)
        
        # Transaction date
        date_label = tk.Label(form_frame, 
                            text="Date:",
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        date_label.grid(row=1, column=0, sticky="w", pady=8)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        date_var = tk.StringVar(value=today)
        date_entry = tk.Entry(form_frame, 
                            textvariable=date_var,
                            font=FONTS["regular"],
                            width=15)
        date_entry.grid(row=1, column=1, sticky="w", pady=8)
        
        # Reference number
        ref_label = tk.Label(form_frame, 
                           text="Reference #:",
                           font=FONTS["regular"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
        ref_label.grid(row=2, column=0, sticky="w", pady=8)
        
        ref_var = tk.StringVar()
        ref_entry = tk.Entry(form_frame, 
                           textvariable=ref_var,
                           font=FONTS["regular"],
                           width=20)
        ref_entry.grid(row=2, column=1, sticky="w", pady=8)
        
        # Description
        desc_label = tk.Label(form_frame, 
                            text="Description:",
                            font=FONTS["regular"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        desc_label.grid(row=3, column=0, sticky="w", pady=8)
        
        desc_var = tk.StringVar()
        desc_entry = tk.Entry(form_frame, 
                            textvariable=desc_var,
                            font=FONTS["regular"],
                            width=30)
        desc_entry.grid(row=3, column=1, sticky="w", pady=8)
        
        # Amount
        amount_label = tk.Label(form_frame, 
                              text="Amount (₹):",
                              font=FONTS["regular_bold"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        amount_label.grid(row=4, column=0, sticky="w", pady=8)
        
        amount_var = tk.StringVar(value="0.00")
        amount_entry = tk.Entry(form_frame, 
                              textvariable=amount_var,
                              font=FONTS["regular_bold"],
                              width=15)
        amount_entry.grid(row=4, column=1, sticky="w", pady=8)
        
        # Notes
        notes_label = tk.Label(form_frame, 
                             text="Notes:",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        notes_label.grid(row=5, column=0, sticky="nw", pady=8)
        
        notes_text = tk.Text(form_frame, 
                           font=FONTS["regular"],
                           width=30,
                           height=3)
        notes_text.grid(row=5, column=1, sticky="w", pady=8)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=COLORS["bg_primary"], pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20)
        
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
        
        def save_transaction():
            try:
                # Validate
                transaction_date = date_var.get().strip()
                if not transaction_date:
                    messagebox.showerror("Error", "Date is required.")
                    return
                
                # Validate amount
                try:
                    amount = float(amount_var.get().strip() or 0)
                    if amount <= 0:
                        messagebox.showerror("Error", "Amount must be greater than zero.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Amount must be a valid number.")
                    return
                    
                # Get transaction type and prepare data
                transaction_type = type_var.get()
                
                # Set debit/credit based on transaction type
                debit = amount if transaction_type == "payment" else 0
                credit = amount if transaction_type == "purchase" else 0
                
                # Get description
                description = desc_var.get().strip()
                if not description:
                    description = "Payment to Supplier" if transaction_type == "payment" else "Purchase from Supplier"
                
                # Get reference
                reference = ref_var.get().strip()
                
                # Get notes
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Prepare data for database
                transaction_data = {
                    "vendor_id": vendor_id,
                    "transaction_date": transaction_date,
                    "reference_no": reference,
                    "description": description,
                    "debit": debit,
                    "credit": credit,
                    "notes": notes
                }
                
                # Insert into database
                inserted = self.controller.db.insert("supplier_transactions", transaction_data)
                
                if inserted:
                    messagebox.showinfo("Success", "Transaction recorded successfully!")
                    dialog.destroy()
                    
                    # Refresh the ledger
                    self.load_ledger()
                else:
                    messagebox.showerror("Error", "Failed to record transaction.")
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        save_btn = tk.Button(button_frame,
                           text="Save Transaction",
                           font=FONTS["regular"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           command=save_transaction)
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def export_ledger(self):
        """Export ledger to Excel"""
        # Check if ledger has been loaded
        if not hasattr(self, 'ledger_data'):
            messagebox.showinfo("Export", "Please load a ledger first.")
            return
        
        # Prepare data for Excel
        data = {
            "Date": [],
            "Reference": [],
            "Description": [],
            "Debit": [],
            "Credit": [],
            "Balance": []
        }
        
        # Add opening balance row
        data["Date"].append(self.ledger_data["start_date"])
        data["Reference"].append("")
        data["Description"].append("Opening Balance")
        data["Debit"].append("")
        data["Credit"].append("")
        data["Balance"].append(self.ledger_data["opening_balance"])
        
        # Add transaction rows
        balance = self.ledger_data["opening_balance"]
        for transaction in self.ledger_data["transactions"]:
            date, reference, description, debit, credit = transaction
            balance = balance - debit + credit
            
            data["Date"].append(date)
            data["Reference"].append(reference)
            data["Description"].append(description)
            data["Debit"].append(debit if debit else "")
            data["Credit"].append(credit if credit else "")
            data["Balance"].append(balance)
        
        # Add closing balance row
        data["Date"].append(self.ledger_data["end_date"])
        data["Reference"].append("")
        data["Description"].append("Closing Balance")
        data["Debit"].append("")
        data["Credit"].append("")
        data["Balance"].append(self.ledger_data["closing_balance"])
        
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Create filename
        entity_name = self.ledger_data["entity"].split("(")[0].strip()
        filename = f"{self.ledger_data['type']}_{entity_name}_Ledger.xlsx"
        
        # Ask user for save location
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if not file_path:
            return
        
        # Export to Excel
        if export_to_excel(df, file_path, f"{self.ledger_data['type']} Ledger"):
            messagebox.showinfo("Export", "Ledger exported successfully.")
        else:
            messagebox.showerror("Export Error", "Failed to export ledger.")
    
    def on_show(self):
        """Called when frame is shown"""
        # Update data in active tab
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Profit & Loss
            self.load_profit_loss()
        elif current_tab == 1:  # Cash Flow
            self.load_cash_flow()
        elif current_tab == 2:  # Expenses
            self.load_expenses()
        elif current_tab == 3:  # Ledgers
            self.load_ledger_entities()