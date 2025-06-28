
import tkinter as tk
from tkinter import ttk
from assets.styles import COLORS, FONTS

class ThemeManager:
    """Centralized theme management for all UI components"""
    
    @staticmethod
    def apply_widget_theme(widget, widget_type="default", context="normal"):
        """
        Apply theme to a specific widget
        
        Args:
            widget: The tkinter widget to theme
            widget_type: Type of widget styling (default, primary, secondary, danger, etc.)
            context: Context of the widget (normal, active, disabled, etc.)
        """
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == "Frame":
                ThemeManager._theme_frame(widget, widget_type, context)
            elif widget_class == "Label":
                ThemeManager._theme_label(widget, widget_type, context)
            elif widget_class == "Button":
                ThemeManager._theme_button(widget, widget_type, context)
            elif widget_class == "Entry":
                ThemeManager._theme_entry(widget, widget_type, context)
            elif widget_class == "Text":
                ThemeManager._theme_text(widget, widget_type, context)
            elif widget_class == "Listbox":
                ThemeManager._theme_listbox(widget, widget_type, context)
            elif widget_class == "Canvas":
                ThemeManager._theme_canvas(widget, widget_type, context)
            elif widget_class in ["Checkbutton", "Radiobutton"]:
                ThemeManager._theme_checkradio(widget, widget_type, context)
            elif widget_class == "Scale":
                ThemeManager._theme_scale(widget, widget_type, context)
            elif widget_class == "Scrollbar":
                ThemeManager._theme_scrollbar(widget, widget_type, context)
                
        except Exception as e:
            print(f"Error applying theme to {widget_class}: {e}")
    
    @staticmethod
    def _theme_frame(widget, widget_type, context):
        """Theme Frame widgets"""
        if widget_type == "header":
            widget.configure(bg=COLORS["primary"])
        elif widget_type == "sidebar":
            widget.configure(bg=COLORS["bg_secondary"])
        elif widget_type == "content":
            widget.configure(bg=COLORS.get("bg_white", COLORS["bg_primary"]))
        else:
            widget.configure(bg=COLORS["bg_primary"])
    
    @staticmethod
    def _theme_label(widget, widget_type, context):
        """Theme Label widgets"""
        if widget_type == "header":
            widget.configure(
                bg=COLORS["primary"],
                fg=COLORS["text_white"],
                font=FONTS["heading"]
            )
        elif widget_type == "title":
            widget.configure(
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                font=FONTS["heading2"]
            )
        elif widget_type == "subtitle":
            widget.configure(
                bg=COLORS["bg_primary"],
                fg=COLORS["text_secondary"],
                font=FONTS["subheading"]
            )
        else:
            widget.configure(
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                font=FONTS["regular"]
            )
    
    @staticmethod
    def _theme_button(widget, widget_type, context):
        """Theme Button widgets"""
        base_config = {
            "font": FONTS["regular"],
            "cursor": "hand2",
            "relief": "flat",
            "padx": 15,
            "pady": 5
        }
        
        if widget_type == "primary":
            widget.configure(
                bg=COLORS["primary"],
                fg=COLORS.get("text_white", "#ffffff"),
                activebackground=COLORS.get("primary_dark", COLORS["primary"]),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
        elif widget_type == "secondary":
            widget.configure(
                bg=COLORS["secondary"],
                fg=COLORS.get("text_white", "#ffffff"),
                activebackground=COLORS.get("secondary_dark", COLORS["secondary"]),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
        elif widget_type == "danger":
            widget.configure(
                bg=COLORS["danger"],
                fg=COLORS.get("text_white", "#ffffff"),
                activebackground=COLORS.get("danger", "#c0392b"),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
        elif widget_type == "success":
            widget.configure(
                bg=COLORS["success"],
                fg=COLORS.get("text_white", "#ffffff"),
                activebackground=COLORS.get("success", "#27ae60"),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
        elif widget_type == "warning":
            widget.configure(
                bg=COLORS["warning"],
                fg=COLORS.get("text_white", "#ffffff"),
                activebackground=COLORS.get("warning", "#f57c00"),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
        elif widget_type == "info":
            widget.configure(
                bg=COLORS["info"],
                fg=COLORS.get("text_white", "#ffffff"),
                activebackground=COLORS.get("info", "#1976D2"),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
        elif widget_type == "nav":
            widget.configure(
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_primary"],
                activebackground=COLORS.get("primary_light", COLORS["primary"]),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                font=FONTS["nav_item"],
                anchor="w",
                relief="flat",
                bd=0
            )
        elif widget_type == "nav_selected":
            widget.configure(
                bg=COLORS["primary"],
                fg="#ffeb3b",  # Yellow for selected nav items
                activebackground=COLORS.get("primary_light", COLORS["primary"]),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                font=(FONTS["nav_item"][0], FONTS["nav_item"][1], "bold"),
                anchor="w",
                relief="flat",
                bd=0
            )
        else:
            widget.configure(
                bg=COLORS.get("bg_secondary", COLORS["bg_primary"]),
                fg=COLORS["text_primary"],
                activebackground=COLORS.get("primary_light", COLORS["primary"]),
                activeforeground=COLORS.get("text_white", "#ffffff"),
                **base_config
            )
    
    @staticmethod
    def _theme_entry(widget, widget_type, context):
        """Theme Entry widgets"""
        widget.configure(
            bg=COLORS["inputbg"],
            fg=COLORS["inputfg"],
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["selectbg"],
            selectforeground=COLORS["selectfg"],
            font=FONTS["regular"],
            relief="solid",
            borderwidth=1
        )
    
    @staticmethod
    def _theme_text(widget, widget_type, context):
        """Theme Text widgets"""
        widget.configure(
            bg=COLORS["inputbg"],
            fg=COLORS["inputfg"],
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["selectbg"],
            selectforeground=COLORS["selectfg"],
            font=FONTS["regular"]
        )
    
    @staticmethod
    def _theme_listbox(widget, widget_type, context):
        """Theme Listbox widgets"""
        widget.configure(
            bg=COLORS["inputbg"],
            fg=COLORS["inputfg"],
            selectbackground=COLORS["selectbg"],
            selectforeground=COLORS["selectfg"],
            font=FONTS["regular"]
        )
    
    @staticmethod
    def _theme_canvas(widget, widget_type, context):
        """Theme Canvas widgets"""
        widget.configure(
            bg=COLORS["bg_primary"],
            highlightthickness=0
        )
    
    @staticmethod
    def _theme_checkradio(widget, widget_type, context):
        """Theme Checkbutton and Radiobutton widgets"""
        widget.configure(
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_primary"],
            activebackground=COLORS["bg_primary"],
            activeforeground=COLORS["text_primary"],
            font=FONTS["regular"]
        )
    
    @staticmethod
    def _theme_scale(widget, widget_type, context):
        """Theme Scale widgets"""
        widget.configure(
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            troughcolor=COLORS["bg_secondary"],
            activebackground=COLORS["primary"]
        )
    
    @staticmethod
    def _theme_scrollbar(widget, widget_type, context):
        """Theme Scrollbar widgets"""
        widget.configure(
            bg=COLORS["bg_secondary"],
            troughcolor=COLORS["bg_primary"],
            activebackground=COLORS["primary"]
        )
    
    @staticmethod
    def theme_dialog(dialog_window, title="Dialog"):
        """Theme a dialog window"""
        dialog_window.configure(bg=COLORS["bg_primary"])
        
        # Update all child widgets
        ThemeManager._theme_dialog_recursive(dialog_window)
    
    @staticmethod
    def _theme_dialog_recursive(widget):
        """Recursively theme dialog widgets"""
        try:
            ThemeManager.apply_widget_theme(widget)
            
            for child in widget.winfo_children():
                ThemeManager._theme_dialog_recursive(child)
        except:
            pass
    
    @staticmethod
    def theme_treeview(treeview):
        """Theme Treeview widgets"""
        try:
            style = ttk.Style()
            
            # Configure treeview style
            style.configure("Themed.Treeview",
                background=COLORS["inputbg"],
                foreground=COLORS["inputfg"],
                fieldbackground=COLORS["inputbg"],
                borderwidth=1,
                font=FONTS["regular"]
            )
            
            style.configure("Themed.Treeview.Heading",
                background=COLORS["bg_secondary"],
                foreground=COLORS["text_primary"],
                font=FONTS["regular_bold"]
            )
            
            style.map("Themed.Treeview",
                background=[("selected", COLORS["selectbg"])],
                foreground=[("selected", COLORS["selectfg"])]
            )
            
            style.map("Themed.Treeview.Heading",
                background=[("active", COLORS["primary"])],
                foreground=[("active", COLORS["text_white"])]
            )
            
            # Apply the style
            treeview.configure(style="Themed.Treeview")
            
        except Exception as e:
            print(f"Error theming treeview: {e}")
    
    @staticmethod
    def theme_notebook(notebook):
        """Theme Notebook widgets"""
        try:
            style = ttk.Style()
            
            style.configure("Themed.TNotebook",
                background=COLORS["bg_primary"],
                borderwidth=0
            )
            
            style.configure("Themed.TNotebook.Tab",
                background=COLORS["bg_secondary"],
                foreground=COLORS["text_primary"],
                padding=[10, 5],
                font=FONTS["regular"]
            )
            
            style.map("Themed.TNotebook.Tab",
                background=[("selected", COLORS["primary"])],
                foreground=[("selected", COLORS["text_white"])]
            )
            
            # Apply the style
            notebook.configure(style="Themed.TNotebook")
            
        except Exception as e:
            print(f"Error theming notebook: {e}")
    
    @staticmethod
    def create_themed_dialog(parent, title, geometry="400x300"):
        """Create a pre-themed dialog window"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry(geometry)
        dialog.configure(bg=COLORS["bg_primary"])
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        return dialog
    
    @staticmethod
    def refresh_all_themes(root_widget):
        """
        Refresh all themes across the entire application
        
        Args:
            root_widget: The root application widget
        """
        try:
            # Recursively update all widgets
            ThemeManager._refresh_widget_recursive(root_widget)
        except Exception as e:
            print(f"Error refreshing themes: {e}")
    
    @staticmethod
    def _refresh_widget_recursive(widget):
        """Recursively refresh theme for all widgets"""
        try:
            widget_class = widget.winfo_class()
            
            # Apply appropriate theming based on widget type
            if widget_class == "Frame":
                widget.configure(bg=COLORS.get("bg_primary", "#ffffff"))
            elif widget_class == "Label":
                widget.configure(
                    bg=COLORS.get("bg_primary", "#ffffff"),
                    fg=COLORS.get("text_primary", "#000000")
                )
            elif widget_class == "Button":
                # Try to maintain existing button styling while updating colors
                current_bg = widget.cget("bg")
                if current_bg in ["#4CAF50", "#45a049"]:  # Success colors
                    ThemeManager._theme_button(widget, "success", "normal")
                elif current_bg in ["#f44336", "#d32f2f"]:  # Danger colors
                    ThemeManager._theme_button(widget, "danger", "normal")
                elif current_bg in ["#2196F3", "#1976D2"]:  # Info colors
                    ThemeManager._theme_button(widget, "info", "normal")
                elif current_bg in ["#ff9800", "#f57c00"]:  # Warning colors
                    ThemeManager._theme_button(widget, "warning", "normal")
                else:
                    ThemeManager._theme_button(widget, "primary", "normal")
            elif widget_class == "Entry":
                ThemeManager._theme_entry(widget, "default", "normal")
            elif widget_class == "Text":
                ThemeManager._theme_text(widget, "default", "normal")
            
            # Process children
            for child in widget.winfo_children():
                ThemeManager._refresh_widget_recursive(child)
                
        except Exception as e:
            # Silently continue if widget is destroyed or inaccessible
            pass
