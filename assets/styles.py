"""
Style definitions for the POS system
Contains color schemes, fonts, and common styles
"""

# Light theme color scheme
LIGHT_THEME = {
    # Primary colors
    "primary": "#2780e3",  # Main blue color (updated to match)
    "primary_light": "#4a96e8",
    "primary_dark": "#1a66c7",
    
    # Secondary colors
    "secondary": "#7E8081",  # Gray color (updated to match)
    "secondary_dark": "#6a6d6e",
    
    # Background colors
    "bg_primary": "#F8F9FA",  # Light background (updated to match)
    "bg_secondary": "#eaecf4",  # Slightly darker gray
    "bg_white": "#ffffff",
    "bg": "#ffffff",  # Added to match format
    "bg_light": "#F8F9FA",  # Very light gray
    
    # Text colors
    "text_primary": "#373a3c",  # Main text color (updated to match fg)
    "text_secondary": "#7E8081",  # Secondary text color (updated)
    "text_white": "#ffffff",
    "fg": "#373a3c",  # Added to match format
    
    # Status/Alert colors
    "success": "#3fb618",  # Green (updated to match)
    "danger": "#ff0039",   # Red (updated to match)
    "warning": "#ff7518",  # Orange (updated to match)
    "info": "#9954bb",     # Purple (updated to match)
    
    # Border and highlight colors
    "border": "#ced4da",   # Border color (updated to match)
    
    # Input colors (added to match format)
    "inputfg": "#373a3c",
    "inputbg": "#fdfdfe",
    
    # Select colors (added to match format)
    "selectbg": "#7e8081",
    "selectfg": "#ffffff",
    
    # Light and dark (added to match format)
    "light": "#F8F9FA",
    "dark": "#373A3C",
    
    # Additional status colors (light versions)
    "success_light": "#e6fff5",
    "danger_light": "#fff5f5",
    "warning_light": "#fff9e6",
    "info_light": "#e6f9ff"
}

# Dark theme color scheme
DARK_THEME = {
    # Primary colors
    "primary": "#2780e3",  # Keep consistent with light theme
    "primary_light": "#4a96e8",
    "primary_dark": "#1a66c7",
    
    # Secondary colors
    "secondary": "#7E8081",  # Keep consistent with light theme
    "secondary_dark": "#6a6d6e",
    
    # Background colors
    "bg_primary": "#1e1e2d",  # Dark background
    "bg_secondary": "#2a2a3c",  # Slightly lighter dark
    "bg_white": "#2a2a3c",
    "bg": "#1e1e2d",  # Added to match format
    "bg_light": "#24243a",  # Light dark background
    
    # Text colors
    "text_primary": "#e0e0e0",  # Light text color
    "text_secondary": "#b0b0b0",  # Secondary light text color
    "text_white": "#ffffff",
    "fg": "#e0e0e0",  # Added to match format
    
    # Status/Alert colors
    "success": "#3fb618",  # Keep consistent with light theme
    "danger": "#ff0039",   # Keep consistent with light theme
    "warning": "#ff7518",  # Keep consistent with light theme
    "info": "#9954bb",     # Keep consistent with light theme
    
    # Border and highlight colors
    "border": "#3a3a50",   # Dark border color
    
    # Input colors (added to match format)
    "inputfg": "#e0e0e0",
    "inputbg": "#24243a",
    
    # Select colors (added to match format)
    "selectbg": "#7e8081",
    "selectfg": "#ffffff",
    
    # Light and dark (added to match format)
    "light": "#24243a",
    "dark": "#1e1e2d",
    
    # Additional status colors (light versions)
    "success_light": "#132218",
    "danger_light": "#2d1414",
    "warning_light": "#2d2411",
    "info_light": "#112125"
}

# Default to light theme
COLORS = LIGHT_THEME.copy()

# Function to switch themes
def set_theme(theme_name="light"):
    """
    Set the application theme
    
    Args:
        theme_name (str): Either 'light' or 'dark'
    
    Returns:
        dict: The new color scheme
    """
    global COLORS
    
    if theme_name.lower() == "dark":
        COLORS.update(DARK_THEME)
    else:  # Default to light theme
        COLORS.update(LIGHT_THEME)
        
    return COLORS

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
    "regular_small": ("Arial", 11),  # Added smaller regular font
    
    # Small text
    "small": ("Arial", 10),
    "small_bold": ("Arial", 10, "bold"),
    "small_italic": ("Arial", 10, "italic"),
    
    # Navigation
    "nav_title": ("Arial", 12, "bold"),
    "nav_item": ("Arial", 11)
}

# Common styles for widgets
STYLES = {
    # Button styles
    "button_primary": {
        "bg": COLORS["primary"],
        "fg": COLORS["text_white"],
        "activebackground": COLORS["primary_dark"],
        "activeforeground": COLORS["text_white"],
        "font": FONTS["regular"],
        "cursor": "hand2",
        "relief": "flat",
        "padx": 15,
        "pady": 5
    },
    
    "button_secondary": {
        "bg": COLORS["secondary"],
        "fg": COLORS["text_white"],
        "activebackground": COLORS["secondary_dark"],
        "activeforeground": COLORS["text_white"],
        "font": FONTS["regular"],
        "cursor": "hand2",
        "relief": "flat",
        "padx": 15,
        "pady": 5
    },
    
    "button_danger": {
        "bg": COLORS["danger"],
        "fg": COLORS["text_white"],
        "activebackground": "#c0392b",  # Darker red
        "activeforeground": COLORS["text_white"],
        "font": FONTS["regular"],
        "cursor": "hand2",
        "relief": "flat",
        "padx": 15,
        "pady": 5
    },
    
    # Entry field styles
    "entry_normal": {
        "font": FONTS["regular"],
        "relief": "solid",
        "borderwidth": 1
    },
    
    # Label styles
    "label_title": {
        "font": FONTS["heading"],
        "bg": COLORS["bg_primary"],
        "fg": COLORS["text_primary"],
        "padx": 10,
        "pady": 10
    },
    
    "label_normal": {
        "font": FONTS["regular"],
        "bg": COLORS["bg_primary"],
        "fg": COLORS["text_primary"]
    }
}