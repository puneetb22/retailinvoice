"""
Settings UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from assets.styles import COLORS, FONTS, STYLES, set_theme
from utils.config import save_config
from utils.theme_manager import ThemeManager
try:
    import ttkbootstrap as ttk_bootstrap
    from ttkbootstrap.themes import standard
    TTK_BOOTSTRAP_AVAILABLE = True
except ImportError:
    TTK_BOOTSTRAP_AVAILABLE = False

class SettingsFrame(tk.Frame):
    """Settings frame for configuring application preferences"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller

        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(header_frame, 
                        text="Settings",
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
        self.shop_info_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.invoice_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])
        self.system_tab = tk.Frame(self.notebook, bg=COLORS["bg_primary"])

        self.notebook.add(self.shop_info_tab, text="Shop Information")
        self.notebook.add(self.invoice_tab, text="Invoice Settings")
        self.notebook.add(self.system_tab, text="System Settings")

        # Setup tabs
        self.setup_shop_info_tab()
        self.setup_invoice_tab()
        self.setup_system_tab()

    def setup_shop_info_tab(self):
        """Setup the shop information tab"""
        # Use Canvas and Scrollbar for scrollable content
        shop_canvas = tk.Canvas(self.shop_info_tab, bg=COLORS["bg_primary"])
        scrollbar = ttk.Scrollbar(self.shop_info_tab, orient=tk.VERTICAL, command=shop_canvas.yview)
        shop_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        shop_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Form frame inside canvas
        form_frame = tk.Frame(shop_canvas, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame_window = shop_canvas.create_window((0, 0), window=form_frame, anchor=tk.NW)

        # Configure canvas scroll area
        def on_frame_configure(event):
            shop_canvas.configure(scrollregion=shop_canvas.bbox("all"))
        form_frame.bind("<Configure>", on_frame_configure)

        # Basic Info Section
        basic_info_frame = tk.LabelFrame(form_frame, text="Basic Shop Information", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        basic_info_frame.pack(fill=tk.X, pady=10)

        # Create basic form fields
        basic_fields = [
            {"name": "shop_name", "label": "Shop Name:", "default": self.controller.config.get("shop_name", "")},
            {"name": "shop_address", "label": "Address:", "default": self.controller.config.get("shop_address", "")},
            {"name": "shop_phone", "label": "Phone Number:", "default": self.controller.config.get("shop_phone", "")},
            {"name": "shop_email", "label": "Email:", "default": self.controller.config.get("shop_email", "")},
            {"name": "shop_gst", "label": "GST Number:", "default": self.controller.config.get("shop_gst", "")}
        ]

        # Variables to store entry values
        self.shop_info_vars = {}

        # Create labels and entries for basic fields
        for i, field in enumerate(basic_fields):
            # Label
            label = tk.Label(basic_info_frame, 
                           text=field["label"],
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=5)

            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var

            entry = tk.Entry(basic_info_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=10)

        # State Information Section
        state_info_frame = tk.LabelFrame(form_frame, text="State Information", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        state_info_frame.pack(fill=tk.X, pady=10)

        # Create state info fields
        state_fields = [
            {"name": "state_name", "label": "State Name:", "default": self.controller.config.get("state_name", "Maharashtra")},
            {"name": "state_code", "label": "State Code:", "default": self.controller.config.get("state_code", "27")}
        ]

        # Create labels and entries for state fields
        for i, field in enumerate(state_fields):
            # Label
            label = tk.Label(state_info_frame, 
                           text=field["label"],
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=5)

            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var

            entry = tk.Entry(state_info_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=10)

        # License Information Section
        license_info_frame = tk.LabelFrame(form_frame, text="License Information", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        license_info_frame.pack(fill=tk.X, pady=10)

        # Create license info fields
        license_fields = [
            {"name": "shop_laid_no", "label": "LAID Number:", "default": self.controller.config.get("shop_laid_no", "")},
            {"name": "shop_lcsd_no", "label": "LCSD Number:", "default": self.controller.config.get("shop_lcsd_no", "")},
            {"name": "shop_lfrd_no", "label": "LFRD Number:", "default": self.controller.config.get("shop_lfrd_no", "")}
        ]

        # Create labels and entries for license fields
        for i, field in enumerate(license_fields):
            # Label
            label = tk.Label(license_info_frame, 
                           text=field["label"],
                           font=FONTS["regular_bold"],
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=5)

            # Entry
            var = tk.StringVar(value=field["default"])
            self.shop_info_vars[field["name"]] = var

            entry = tk.Entry(license_info_frame, 
                          textvariable=var,
                          font=FONTS["regular"],
                          width=40)
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=10)

        # Terms & Conditions Section
        terms_frame = tk.LabelFrame(form_frame, text="Invoice Terms & Conditions", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        terms_frame.pack(fill=tk.X, pady=10)

        # Label
        terms_label = tk.Label(terms_frame, 
                             text="Terms & Conditions:",
                             font=FONTS["regular_bold"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        terms_label.grid(row=0, column=0, sticky="w", pady=5)

        # Create a Text widget for multiline text
        terms_text = tk.Text(terms_frame, font=FONTS["regular"], width=40, height=4)
        terms_text.grid(row=0, column=1, sticky="w", pady=5, padx=10)

        # Insert default text
        default_terms = self.controller.config.get("terms_conditions", "Goods once sold cannot be returned. Payment due within 30 days.")
        terms_text.insert(tk.END, default_terms)

        # Store the text widget reference
        self.terms_text = terms_text

        # Save button using theme properties
        save_btn = tk.Button(form_frame,
                          text="Save Shop Information",
                          font=FONTS["regular_bold"],
                          bg=COLORS["primary"],
                          fg=COLORS["text_white"],
                          activebackground=COLORS["primary_light"],
                          activeforeground=COLORS["text_white"],
                          padx=20,
                          pady=8,
                          cursor="hand2",
                          command=self.save_shop_info)
        save_btn.pack(pady=20)

    def setup_invoice_tab(self):
        """Setup the invoice settings tab"""
        # Form frame
        form_frame = tk.Frame(self.invoice_tab, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Create form fields
        fields = [
            {"name": "invoice_prefix", "label": "Invoice Prefix:", "default": self.controller.config.get("invoice_prefix", "")}
        ]

        # Variables to store entry values
        self.invoice_vars = {}

        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                            text=field["label"],
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=10)

            # Entry
            var = tk.StringVar(value=field["default"])
            self.invoice_vars[field["name"]] = var

            entry = tk.Entry(form_frame, 
                           textvariable=var,
                           font=FONTS["regular"],
                           width=20)
            entry.grid(row=i, column=1, sticky="w", pady=10, padx=10)

        # Invoice template
        template_label = tk.Label(form_frame, 
                               text="Invoice Template:",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        template_label.grid(row=len(fields), column=0, sticky="w", pady=10)

        # Template options
        self.template_var = tk.StringVar(value=self.controller.config.get("invoice_template", "default"))
        templates = ["default", "compact", "detailed", "shop_bill"]

        template_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        template_frame.grid(row=len(fields), column=1, sticky="w", pady=10, padx=10)

        for template in templates:
            rb = tk.Radiobutton(template_frame, 
                              text=template.capitalize(),
                              variable=self.template_var,
                              value=template,
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"])
            rb.pack(side=tk.LEFT, padx=10)

        # Add preferred invoice format option
        format_label = tk.Label(form_frame, 
                             text="Preferred Format:",
                             font=FONTS["regular_bold"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"])
        format_label.grid(row=len(fields)+1, column=0, sticky="w", pady=10)

        # Format options
        self.format_var = tk.StringVar(value=self.controller.config.get("invoice_format", "pdf"))

        format_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"])
        format_frame.grid(row=len(fields)+1, column=1, sticky="w", pady=10, padx=10)

        # PDF format radio button
        pdf_rb = tk.Radiobutton(format_frame, 
                             text="PDF",
                             variable=self.format_var,
                             value="pdf",
                             font=FONTS["regular"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"],
                             selectcolor=COLORS["bg_primary"])
        pdf_rb.pack(side=tk.LEFT, padx=10)

        # Excel format radio button
        excel_rb = tk.Radiobutton(format_frame, 
                              text="Excel",
                              variable=self.format_var,
                              value="excel",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              selectcolor=COLORS["bg_primary"])
        excel_rb.pack(side=tk.LEFT, padx=10)

        # Save button using theme properties
        save_btn = tk.Button(form_frame,
                           text="Save Invoice Settings",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           activebackground=COLORS["primary_light"],
                           activeforeground=COLORS["text_white"],
                           padx=20,
                           pady=8,
                           cursor="hand2",
                           command=self.save_invoice_settings)
        save_btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)

    def setup_system_tab(self):
        """Setup the system settings tab"""
        # Form frame
        form_frame = tk.Frame(self.system_tab, bg=COLORS["bg_primary"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Create form fields
        fields = [
            {"name": "low_stock_threshold", "label": "Low Stock Threshold:", "default": self.controller.config.get("low_stock_threshold", "10")}
        ]

        # Variables to store entry values
        self.system_vars = {}

        # Create labels and entries
        for i, field in enumerate(fields):
            # Label
            label = tk.Label(form_frame, 
                            text=field["label"],
                            font=FONTS["regular_bold"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
            label.grid(row=i, column=0, sticky="w", pady=10)

            # Entry
            var = tk.StringVar(value=field["default"])
            self.system_vars[field["name"]] = var

            entry = tk.Entry(form_frame, 
                           textvariable=var,
                           font=FONTS["regular"],
                           width=10)
            entry.grid(row=i, column=1, sticky="w", pady=10, padx=10)

        # Theme settings section
        theme_section_frame = tk.LabelFrame(form_frame, text="Theme Settings", bg=COLORS["bg_primary"], fg=COLORS["text_primary"], font=FONTS["regular_bold"], padx=10, pady=10)
        theme_section_frame.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=10)

        # Theme type selection
        theme_type_label = tk.Label(theme_section_frame, 
                                   text="Theme Type:",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"])
        theme_type_label.grid(row=0, column=0, sticky="w", pady=5)

        # Get all available themes from styles.py
        from assets.styles import get_available_themes
        self.available_theme_types = get_available_themes()

        self.theme_type_var = tk.StringVar(value=self.controller.config.get("theme_type", "default"))

        theme_type_dropdown = ttk.Combobox(theme_section_frame,
                                         textvariable=self.theme_type_var,
                                         values=self.available_theme_types,
                                         state="readonly",
                                         width=15)
        theme_type_dropdown.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        theme_type_dropdown.bind("<<ComboboxSelected>>", self.on_theme_type_change)

        # Theme mode selection (Light/Dark)
        theme_mode_label = tk.Label(theme_section_frame, 
                                   text="Theme Mode:",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"])
        theme_mode_label.grid(row=1, column=0, sticky="w", pady=5)

        self.theme_mode_var = tk.StringVar(value=self.controller.config.get("app_theme", "light"))

        theme_mode_frame = tk.Frame(theme_section_frame, bg=COLORS["bg_primary"])
        theme_mode_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        # Light theme radio button
        light_rb = tk.Radiobutton(theme_mode_frame, 
                                text="Light",
                                variable=self.theme_mode_var,
                                value="light",
                                font=FONTS["regular"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"],
                                selectcolor=COLORS["bg_primary"],
                                command=self.on_theme_mode_change)
        light_rb.pack(side=tk.LEFT, padx=10)

        # Dark theme radio button
        dark_rb = tk.Radiobutton(theme_mode_frame, 
                               text="Dark",
                               variable=self.theme_mode_var,
                               value="dark",
                               font=FONTS["regular"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"],
                               selectcolor=COLORS["bg_primary"],
                               command=self.on_theme_mode_change)
        dark_rb.pack(side=tk.LEFT, padx=10)

        # Theme preview frame
        preview_frame = tk.Frame(theme_section_frame, bg=COLORS["bg_primary"])
        preview_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        preview_label = tk.Label(preview_frame,
                               text="Preview:",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        preview_label.pack(side=tk.LEFT, padx=5)

        # Preview color swatches
        self.preview_colors_frame = tk.Frame(preview_frame, bg=COLORS["bg_primary"])
        self.preview_colors_frame.pack(side=tk.LEFT, padx=10)

        self.update_theme_preview()

        # Theme action buttons frame
        theme_buttons_frame = tk.Frame(theme_section_frame, bg=COLORS["bg_primary"])
        theme_buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # Apply theme button using theme properties
        apply_theme_btn = tk.Button(theme_buttons_frame,
                                  text="Apply Theme",
                                  font=FONTS["regular"],
                                  bg=COLORS["primary"],
                                  fg=COLORS["text_white"],
                                  activebackground=COLORS["primary_light"],
                                  activeforeground=COLORS["text_white"],
                                  padx=15,
                                  pady=5,
                                  cursor="hand2",
                                  command=self.apply_theme)
        apply_theme_btn.pack(side=tk.LEFT, padx=5)

        # TTK Creator button (only show if ttkbootstrap is available)
        if TTK_BOOTSTRAP_AVAILABLE:
            ttk_creator_btn = tk.Button(theme_buttons_frame,
                                      text="Open Theme Creator",
                                      font=FONTS["regular"],
                                      bg=COLORS["info"],
                                      fg=COLORS["text_white"],
                                      activebackground=COLORS["info"],
                                      activeforeground=COLORS["text_white"],
                                      padx=15,
                                      pady=5,
                                      cursor="hand2",
                                      command=self.open_theme_creator)
            ttk_creator_btn.pack(side=tk.LEFT, padx=5)

            # Reload themes button using theme properties
            reload_themes_btn = tk.Button(theme_buttons_frame,
                                        text="Reload Themes",
                                        font=FONTS["regular"],
                                        bg=COLORS["secondary"],
                                        fg=COLORS["text_white"],
                                        activebackground=COLORS["secondary_dark"],
                                        activeforeground=COLORS["text_white"],
                                        padx=15,
                                        pady=5,
                                        cursor="hand2",
                                        command=self.reload_themes)
            reload_themes_btn.pack(side=tk.LEFT, padx=5)

        # Add keyboard shortcuts button using theme properties
        shortcuts_btn = tk.Button(form_frame,
                                text="View Keyboard Shortcuts",
                                font=FONTS["regular"],
                                bg=COLORS["primary_light"],
                                fg=COLORS["text_white"],
                                activebackground=COLORS["primary"],
                                activeforeground=COLORS["text_white"],
                                padx=10,
                                pady=5,
                                cursor="hand2",
                                command=self.show_keyboard_shortcuts)
        shortcuts_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=10, sticky="w")

        # Version information
        version_frame = tk.Frame(form_frame, bg=COLORS["bg_primary"], pady=10)
        version_frame.grid(row=len(fields)+2, column=0, columnspan=2, sticky="w", pady=10)

        version = self.controller.config.get('version', '1.0.0')
        version_label = tk.Label(version_frame, 
                               text=f"Application Version: {version}",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        version_label.pack(anchor="w")

        # Save button using theme properties
        save_btn = tk.Button(form_frame,
                           text="Save System Settings",
                           font=FONTS["regular_bold"],
                           bg=COLORS["primary"],
                           fg=COLORS["text_white"],
                           activebackground=COLORS["primary_light"],
                           activeforeground=COLORS["text_white"],
                           padx=20,
                           pady=8,
                           cursor="hand2",
                           command=self.save_system_settings)
        save_btn.grid(row=len(fields)+3, column=0, columnspan=2, pady=20)

    def save_shop_info(self):
        """Save shop information settings"""
        # Update config
        for key, var in self.shop_info_vars.items():
            self.controller.config[key] = var.get()

        # Make sure specific shop_bill template fields are properly stored with correct keys
        # Map license field keys to the expected field names in invoice_generator
        field_mapping = {
            "shop_laid_no": "laid_no",
            "shop_lcsd_no": "lcsd_no", 
            "shop_lfrd_no": "lfrd_no"
        }

        # Map fields to expected keys to ensure compatibility with invoice_generator.py
        for ui_key, config_key in field_mapping.items():
            if ui_key in self.shop_info_vars:
                self.controller.config[config_key] = self.shop_info_vars[ui_key].get()

        # Save terms and conditions from text widget
        terms_content = self.terms_text.get("1.0", tk.END).strip()
        self.controller.config["terms_conditions"] = terms_content

        # Save to file
        config_saved = save_config(self.controller.config)

        # Also save to database for invoice generator
        db_saved = self._save_to_database()

        if config_saved and db_saved:
            messagebox.showinfo("Settings", "Shop information saved successfully!")
        else:
            messagebox.showerror("Settings Error", "Failed to save shop information.")

    def _save_to_database(self):
        """Save shop information to database settings table for invoice generation"""
        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            cursor = conn.cursor()

            # Save all shop information fields to the settings table
            for key, var in self.shop_info_vars.items():
                value = var.get()

                # Skip empty values
                if not value:
                    continue

                # Check if setting already exists
                cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", (key,))
                if cursor.fetchone()[0] > 0:
                    # Update existing setting
                    cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
                else:
                    # Insert new setting
                    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))

            # Save terms and conditions
            terms_content = self.terms_text.get("1.0", tk.END).strip()
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", ("terms_conditions",))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (terms_content, "terms_conditions"))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("terms_conditions", terms_content))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving settings to database: {e}")
            return False

    def save_invoice_settings(self):
        """Save invoice settings"""
        # Update config
        for key, var in self.invoice_vars.items():
            self.controller.config[key] = var.get()

        # Save template
        self.controller.config["invoice_template"] = self.template_var.get()

        # Save preferred format
        self.controller.config["invoice_format"] = self.format_var.get()

        # Save to file
        config_saved = save_config(self.controller.config)

        # Also save to database for invoice generator
        db_saved = self._save_invoice_settings_to_database()

        if config_saved and db_saved:
            messagebox.showinfo("Settings", "Invoice settings saved successfully!")
        else:
            messagebox.showerror("Settings Error", "Failed to save invoice settings.")

    def _save_invoice_settings_to_database(self):
        """Save invoice settings to database settings table"""
        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            cursor = conn.cursor()

            # Save invoice prefix
            for key, var in self.invoice_vars.items():
                value = var.get()

                # Skip empty values
                if not value:
                    continue

                # Check if setting already exists
                cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", (key,))
                if cursor.fetchone()[0] > 0:
                    # Update existing setting
                    cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
                else:
                    # Insert new setting
                    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))

            # Save template
            template = self.template_var.get()
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", ("invoice_template",))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (template, "invoice_template"))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("invoice_template", template))

            # Save format
            format_value = self.format_var.get()
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", ("invoice_format",))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (format_value, "invoice_format"))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("invoice_format", format_value))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving invoice settings to database: {e}")
            return False

    def save_system_settings(self):
        """Save system settings"""
        # Validate low stock threshold
        try:
            threshold = int(self.system_vars["low_stock_threshold"].get())
            if threshold < 0:
                raise ValueError("Threshold must be positive")

            # Update config
            self.controller.config["low_stock_threshold"] = threshold

            # Update theme settings
            theme_mode = self.theme_mode_var.get()
            theme_type = self.theme_type_var.get()

            self.controller.config["app_theme"] = theme_mode
            self.controller.config["theme_type"] = theme_type

            # Apply theme immediately
            set_theme(theme_mode, theme_type)
            self.update_application_theme()

            # Save to file
            config_saved = save_config(self.controller.config)

            # Also save to database for invoice generator and other modules
            db_saved = self._save_system_settings_to_database()

            if config_saved and db_saved:
                messagebox.showinfo("Settings", "System settings saved and theme applied successfully!")
            else:
                messagebox.showerror("Settings Error", "Failed to save system settings.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Low stock threshold must be a positive number.")

    def _save_system_settings_to_database(self):
        """Save system settings to database settings table"""
        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            cursor = conn.cursor()

            # Save low stock threshold
            threshold = int(self.system_vars["low_stock_threshold"].get())
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", ("low_stock_threshold",))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (str(threshold), "low_stock_threshold"))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("low_stock_threshold", str(threshold)))

            # Save theme mode setting
            theme_mode = self.theme_mode_var.get()
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", ("app_theme",))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (theme_mode, "app_theme"))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("app_theme", theme_mode))

            # Save theme type setting
            theme_type = self.theme_type_var.get()
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", ("theme_type",))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (theme_type, "theme_type"))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("theme_type", theme_type))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving system settings to database: {e}")
            return False

    def on_theme_type_change(self, event=None):
        """Handle theme type change"""
        self.update_theme_preview()

    def on_theme_mode_change(self):
        """Handle theme mode change"""
        self.update_theme_preview()

    def update_theme_preview(self):
        """Update the theme preview colors"""
        try:
            # Clear existing preview
            for widget in self.preview_colors_frame.winfo_children():
                widget.destroy()

            # Get the current theme selection
            theme_type = self.theme_type_var.get()
            theme_mode = self.theme_mode_var.get()

            # Get theme colors from styles
            from assets.styles import get_theme_colors
            colors = get_theme_colors(theme_mode, theme_type)

            # Create color swatches
            color_names = ['primary', 'secondary', 'success', 'danger', 'warning', 'info']
            for i, color_name in enumerate(color_names):
                if color_name in colors:
                    color_frame = tk.Frame(self.preview_colors_frame, 
                                         bg=colors[color_name], 
                                         width=30, 
                                         height=20,
                                         relief="solid",
                                         borderwidth=1)
                    color_frame.pack(side=tk.LEFT, padx=2)

                    # Create tooltip
                    def create_tooltip(widget, text):
                        def on_enter(event):
                            tooltip = tk.Toplevel()
                            tooltip.wm_overrideredirect(True)
                            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                            label = tk.Label(tooltip, text=text, background="lightyellow")
                            label.pack()
                        def on_leave(event):
                            for child in widget.winfo_toplevel().winfo_children():
                                if isinstance(child, tk.Toplevel):
                                    child.destroy()
                        widget.bind("<Enter>", on_enter)
                        widget.bind("<Leave>", on_leave)

                    create_tooltip(color_frame, f"{color_name}: {colors[color_name]}")

        except Exception as e:
            print(f"Error updating theme preview: {e}")

    def apply_theme(self):
        """Apply the selected theme"""
        try:
            theme_mode = self.theme_mode_var.get()
            theme_type = self.theme_type_var.get()

            # Apply theme
            from assets.styles import set_theme
            set_theme(theme_mode, theme_type)

            # Update application theme
            self.update_application_theme()

            messagebox.showinfo("Theme Applied", f"Theme '{theme_type}' in '{theme_mode}' mode has been applied successfully!")

        except Exception as e:
            messagebox.showerror("Theme Error", f"Failed to apply theme: {e}")

    def update_application_theme(self):
        """Update the application theme across all components"""
        try:
            # Get the main controller and update all frames
            if hasattr(self.controller, 'frames'):
                for frame_name, frame in self.controller.frames.items():
                    if hasattr(frame, 'update_theme'):
                        frame.update_theme()

            # Force refresh of current frame
            self.controller.show_frame("SettingsFrame")

        except Exception as e:
            print(f"Error updating application theme: {e}")

    def open_theme_creator(self):
        """Open the ttkbootstrap TTK Creator"""
        try:
            if TTK_BOOTSTRAP_AVAILABLE:
                import subprocess
                import sys
                subprocess.Popen([sys.executable, "-m", "ttkbootstrap.ttkcreator"])
            else:
                messagebox.showerror("TTK Creator", "ttkbootstrap is not available. Please install it first.")
        except Exception as e:
            messagebox.showerror("TTK Creator Error", f"Failed to open TTK Creator: {e}")

    def reload_themes(self):
        """Reload available themes from styles"""
        try:
            # Reload the styles module
            import importlib
            import assets.styles
            importlib.reload(assets.styles)

            # Update available themes
            from assets.styles import get_available_themes
            self.available_theme_types = get_available_themes()

            # Update the dropdown
            theme_type_dropdown = None
            for child in self.winfo_children():
                if isinstance(child, tk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Notebook):
                            for tab in subchild.tabs():
                                tab_frame = subchild.nametowidget(tab)
                                for widget in tab_frame.winfo_children():
                                    if isinstance(widget, tk.Frame):
                                        for subwidget in widget.winfo_children():
                                            if isinstance(subwidget, tk.LabelFrame):
                                                for labelframe_child in subwidget.winfo_children():
                                                    if isinstance(labelframe_child, ttk.Combobox):
                                                        theme_type_dropdown = labelframe_child
                                                        break

            if theme_type_dropdown:
                theme_type_dropdown['values'] = self.available_theme_types

            messagebox.showinfo("Themes Reloaded", "Available themes have been reloaded successfully!")

        except Exception as e:
            messagebox.showerror("Reload Error", f"Failed to reload themes: {e}")

    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        # Create a new window for shortcuts
        shortcuts_window = tk.Toplevel(self)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("600x400")
        shortcuts_window.configure(bg=COLORS["bg_primary"])

        # Make it modal
        shortcuts_window.transient(self)
        shortcuts_window.grab_set()

        # Header
        header_label = tk.Label(shortcuts_window,
                              text="Keyboard Shortcuts",
                              font=FONTS["heading"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        header_label.pack(pady=20)

        # Create a frame for shortcuts list
        shortcuts_frame = tk.Frame(shortcuts_window, bg=COLORS["bg_primary"])
        shortcuts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Shortcuts data
        shortcuts_data = [
            ("F1", "Dashboard"),
            ("F2", "Sales"),
            ("F3", "Inventory Management"),
            ("F4", "Customer Management"),
            ("F5", "Reports"),
            ("F6", "Accounting"),
            ("F7", "Settings"),
            ("F8", "Backup"),
            ("Ctrl+N", "New Sale"),
            ("Ctrl+S", "Save Current Form"),
            ("Ctrl+F", "Search/Find"),
            ("Ctrl+P", "Print Invoice"),
            ("Ctrl+Q", "Quit Application"),
            ("Escape", "Cancel Current Operation"),
            ("Enter", "Confirm Selection"),
            ("Tab", "Navigate to Next Field")
        ]

        # Create headers
        shortcut_header = tk.Label(shortcuts_frame,
                                 text="Shortcut",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        shortcut_header.grid(row=0, column=0, sticky="w", padx=20, pady=5)

        action_header = tk.Label(shortcuts_frame,
                               text="Action",
                               font=FONTS["regular_bold"],
                               bg=COLORS["bg_primary"],
                               fg=COLORS["text_primary"])
        action_header.grid(row=0, column=1, sticky="w", padx=20, pady=5)

        # Add separator
        separator = tk.Frame(shortcuts_frame, height=2, bg=COLORS["primary"])
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=5)

        # Add shortcuts
        for i, (shortcut, action) in enumerate(shortcuts_data, start=2):
            shortcut_label = tk.Label(shortcuts_frame,
                                    text=shortcut,
                                    font=FONTS["regular"],
                                    bg=COLORS["bg_primary"],
                                    fg=COLORS["primary"])
            shortcut_label.grid(row=i, column=0, sticky="w", padx=20, pady=2)

            action_label = tk.Label(shortcuts_frame,
                                  text=action,
                                  font=FONTS["regular"],
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["text_primary"])
            action_label.grid(row=i, column=1, sticky="w", padx=20, pady=2)

        # Close button using theme properties
        close_btn = tk.Button(shortcuts_window,
                            text="Close",
                            font=FONTS["regular"],
                            bg=COLORS["primary"],
                            fg=COLORS["text_white"],
                            activebackground=COLORS["primary_light"],
                            activeforeground=COLORS["text_white"],
                            padx=20,
                            pady=5,
                            cursor="hand2",
                            command=shortcuts_window.destroy)
        close_btn.pack(pady=20)

        # Center the window
        shortcuts_window.update_idletasks()
        x = (shortcuts_window.winfo_screenwidth() // 2) - (shortcuts_window.winfo_width() // 2)
        y = (shortcuts_window.winfo_screenheight() // 2) - (shortcuts_window.winfo_height() // 2)
        shortcuts_window.geometry(f"+{x}+{y}")
else:
    print("Settings frame initialization completed successfully.")