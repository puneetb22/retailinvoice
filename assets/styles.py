
"""
Style definitions for the POS system
Contains color schemes, fonts, and common styles
"""

# Light theme color scheme - aligned with standard format
LIGHT_THEME = {
    # Theme type
    "type": "light",
    
    # Core colors matching the standard format
    "primary": "#2780e3",
    "secondary": "#7E8081", 
    "success": "#3fb618",
    "info": "#9954bb",
    "warning": "#ff7518", 
    "danger": "#ff0039",
    "light": "#F8F9FA",
    "dark": "#373A3C",
    
    # Background and foreground
    "bg": "#ffffff",
    "fg": "#373a3c",
    
    # Selection colors
    "selectbg": "#7e8081",
    "selectfg": "#ffffff",
    
    # Border colors
    "border": "#ced4da",
    
    # Input colors
    "inputfg": "#373a3c", 
    "inputbg": "#fdfdfe",
    
    # Additional colors for compatibility
    "primary_light": "#4a96e8",
    "primary_dark": "#1a66c7",
    "secondary_dark": "#6a6d6e",
    "bg_primary": "#ffffff",
    "bg_secondary": "#F8F9FA",
    "bg_white": "#ffffff",
    "bg_light": "#F8F9FA",
    "text_primary": "#373a3c",
    "text_secondary": "#7E8081", 
    "text_white": "#ffffff",
    "success_light": "#e6fff5",
    "danger_light": "#fff5f5",
    "warning_light": "#fff9e6",
    "info_light": "#f3e8ff"
}

# Dark theme color scheme - aligned with standard format
DARK_THEME = {
    # Theme type
    "type": "dark",
    
    # Core colors matching the standard format
    "primary": "#4a96e8",
    "secondary": "#9a9b9c",
    "success": "#5fc73a", 
    "info": "#b970d6",
    "warning": "#ff9548",
    "danger": "#ff335a",
    "light": "#24243a",
    "dark": "#1e1e2d",
    
    # Background and foreground
    "bg": "#1e1e2d",
    "fg": "#e0e0e0",
    
    # Selection colors
    "selectbg": "#7e8081",
    "selectfg": "#ffffff",
    
    # Border colors
    "border": "#3a3a50",
    
    # Input colors
    "inputfg": "#e0e0e0",
    "inputbg": "#24243a",
    
    # Additional colors for compatibility
    "primary_light": "#6ba3ed",
    "primary_dark": "#2780e3",
    "secondary_dark": "#6a6d6e",
    "bg_primary": "#1e1e2d",
    "bg_secondary": "#2a2a3c",
    "bg_white": "#2a2a3c",
    "bg_light": "#24243a",
    "text_primary": "#e0e0e0",
    "text_secondary": "#b0b0b0",
    "text_white": "#ffffff", 
    "success_light": "#132218",
    "danger_light": "#2d1414",
    "warning_light": "#2d2411",
    "info_light": "#1f1428"
}

# Additional theme variants for extended customization
THEME_VARIANTS = {
    "modern_light": {
        "type": "light",
        "primary": "#6366f1",
        "secondary": "#64748b", 
        "success": "#10b981",
        "info": "#3b82f6",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "light": "#f8fafc",
        "dark": "#1e293b",
        "bg": "#ffffff",
        "fg": "#1e293b",
        "selectbg": "#64748b",
        "selectfg": "#ffffff",
        "border": "#e2e8f0",
        "inputfg": "#1e293b",
        "inputbg": "#f8fafc"
    },
    
    "modern_dark": {
        "type": "dark", 
        "primary": "#818cf8",
        "secondary": "#94a3b8",
        "success": "#34d399",
        "info": "#60a5fa",
        "warning": "#fbbf24", 
        "danger": "#f87171",
        "light": "#374151",
        "dark": "#111827",
        "bg": "#111827",
        "fg": "#f9fafb",
        "selectbg": "#94a3b8",
        "selectfg": "#ffffff",
        "border": "#374151",
        "inputfg": "#f9fafb",
        "inputbg": "#1f2937"
    },
    
    "corporate_light": {
        "type": "light",
        "primary": "#2c3e50",
        "secondary": "#95a5a6",
        "success": "#27ae60",
        "info": "#3498db", 
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "light": "#ecf0f1",
        "dark": "#2c3e50",
        "bg": "#ffffff",
        "fg": "#2c3e50",
        "selectbg": "#95a5a6",
        "selectfg": "#ffffff", 
        "border": "#bdc3c7",
        "inputfg": "#2c3e50",
        "inputbg": "#ecf0f1"
    },
    
    "corporate_dark": {
        "type": "dark",
        "primary": "#34495e", 
        "secondary": "#bdc3c7",
        "success": "#2ecc71",
        "info": "#3498db",
        "warning": "#f1c40f",
        "danger": "#e67e22",
        "light": "#34495e",
        "dark": "#2c3e50",
        "bg": "#2c3e50",
        "fg": "#ecf0f1",
        "selectbg": "#bdc3c7",
        "selectfg": "#2c3e50",
        "border": "#34495e", 
        "inputfg": "#ecf0f1",
        "inputbg": "#34495e"
    }
}

# Default to light theme
COLORS = LIGHT_THEME.copy()

# Function to switch themes
def set_theme(theme_name="light", theme_type="default"):
    """
    Set the application theme
    
    Args:
        theme_name (str): Theme mode ('light' or 'dark')
        theme_type (str): Theme type/variant
    
    Returns:
        dict: The new color scheme
    """
    global COLORS
    
    # Get the appropriate theme colors
    if theme_type != "default" and theme_type in ["modern", "corporate"]:
        variant_key = f"{theme_type}_{theme_name}"
        if variant_key in THEME_VARIANTS:
            COLORS.clear()
            COLORS.update(THEME_VARIANTS[variant_key])
        else:
            # Fallback to base themes
            if theme_name.lower() == "dark":
                COLORS.clear()
                COLORS.update(DARK_THEME)
            else:
                COLORS.clear()
                COLORS.update(LIGHT_THEME)
    else:
        # Use base themes
        if theme_name.lower() == "dark":
            COLORS.clear()
            COLORS.update(DARK_THEME)
        else:
            COLORS.clear()
            COLORS.update(LIGHT_THEME)
    
    # Update all dynamic styles
    update_styles()
    
    return COLORS

def get_theme_colors(theme_type, theme_mode):
    """
    Get colors for a specific theme type and mode
    
    Args:
        theme_type (str): Type of theme
        theme_mode (str): 'light' or 'dark'
    
    Returns:
        dict: Color scheme for the theme
    """
    # Check if it's a predefined theme variant
    variant_key = f"{theme_type}_{theme_mode}"
    if variant_key in THEME_VARIANTS:
        return THEME_VARIANTS[variant_key]
    
    # Return default themes
    if theme_mode == "dark":
        return DARK_THEME
    else:
        return LIGHT_THEME

def validate_theme_properties(theme_dict):
    """
    Validate that a theme dictionary has all required properties
    
    Args:
        theme_dict (dict): Theme dictionary to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_properties = [
        "type", "primary", "secondary", "success", "info", "warning", 
        "danger", "light", "dark", "bg", "fg", "selectbg", "selectfg",
        "border", "inputfg", "inputbg"
    ]
    
    return all(prop in theme_dict for prop in required_properties)

# Font definitions
FONTS = {
    # Headings
    "heading": ("Arial", 18, "bold"),
    "heading_light": ("Arial", 18, "bold"),
    "heading2": ("Arial", 16, "bold"),
    "subheading": ("Arial", 14, "bold"),
    
    # Regular text
    "regular": ("Arial", 12),
    "regular_bold": ("Arial", 12, "bold"),
    "regular_italic": ("Arial", 12, "italic"),
    "regular_light": ("Arial", 12),
    "regular_small": ("Arial", 11),
    
    # Small text
    "small": ("Arial", 10),
    "small_bold": ("Arial", 10, "bold"),
    "small_italic": ("Arial", 10, "italic"),
    
    # Navigation
    "nav_title": ("Arial", 12, "bold"),
    "nav_item": ("Arial", 11)
}

# Common styles for widgets - automatically updated with theme changes
def get_button_styles():
    """Get button styles based on current theme"""
    return {
        "button_primary": {
            "bg": COLORS["primary"],
            "fg": COLORS["text_white"] if "text_white" in COLORS else "#ffffff",
            "activebackground": COLORS.get("primary_dark", COLORS["primary"]),
            "activeforeground": COLORS["text_white"] if "text_white" in COLORS else "#ffffff",
            "font": FONTS["regular"],
            "cursor": "hand2",
            "relief": "flat",
            "padx": 15,
            "pady": 5
        },
        
        "button_secondary": {
            "bg": COLORS["secondary"],
            "fg": COLORS["text_white"] if "text_white" in COLORS else "#ffffff",
            "activebackground": COLORS.get("secondary_dark", COLORS["secondary"]),
            "activeforeground": COLORS["text_white"] if "text_white" in COLORS else "#ffffff",
            "font": FONTS["regular"],
            "cursor": "hand2",
            "relief": "flat",
            "padx": 15,
            "pady": 5
        },
        
        "button_danger": {
            "bg": COLORS["danger"],
            "fg": COLORS["text_white"] if "text_white" in COLORS else "#ffffff",
            "activebackground": COLORS.get("danger_dark", "#c0392b"),
            "activeforeground": COLORS["text_white"] if "text_white" in COLORS else "#ffffff",
            "font": FONTS["regular"],
            "cursor": "hand2",
            "relief": "flat",
            "padx": 15,
            "pady": 5
        }
    }

def get_widget_styles():
    """Get widget styles based on current theme"""
    return {
        # Entry field styles
        "entry_normal": {
            "font": FONTS["regular"],
            "relief": "solid",
            "borderwidth": 1,
            "bg": COLORS["inputbg"],
            "fg": COLORS["inputfg"],
            "insertbackground": COLORS["fg"]
        },
        
        # Label styles
        "label_title": {
            "font": FONTS["heading"],
            "bg": COLORS.get("bg_primary", COLORS["bg"]),
            "fg": COLORS.get("text_primary", COLORS["fg"]),
            "padx": 10,
            "pady": 10
        },
        
        "label_normal": {
            "font": FONTS["regular"],
            "bg": COLORS.get("bg_primary", COLORS["bg"]),
            "fg": COLORS.get("text_primary", COLORS["fg"])
        }
    }

# Dynamic styles that update with theme changes
STYLES = get_widget_styles()

def update_styles():
    """Update all styles when theme changes"""
    global STYLES
    STYLES.update(get_widget_styles())
    STYLES.update(get_button_styles())
