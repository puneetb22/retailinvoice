
"""
Style definitions for the POS system
Contains color schemes, fonts, and common styles with ttkbootstrap integration
"""

# Import ttkbootstrap themes if available
try:
    import ttkbootstrap as ttk_bootstrap
    from ttkbootstrap.themes import standard
    TTK_BOOTSTRAP_AVAILABLE = True
    
    # All 28 ttkbootstrap standard themes with standardized color properties
    TTKBOOTSTRAP_THEMES = {
        "cosmo": {
            "type": "light",
            "colors": {
                "primary": "#2780e3",
                "secondary": "#7e8081",
                "success": "#3fb618",
                "info": "#9954bb",
                "warning": "#ff7518",
                "danger": "#ff0039",
                "light": "#f8f9fa",
                "dark": "#373a3c",
                "bg": "#ffffff",
                "fg": "#373a3c",
                "selectbg": "#7e8081",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#373a3c",
                "inputbg": "#fdfdfe",
                # Extended properties for UI compatibility
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_white": "#ffffff",
                "bg_light": "#f8f9fa",
                "text_primary": "#373a3c",
                "text_secondary": "#7e8081",
                "text_white": "#ffffff",
                "primary_light": "#4a96e8",
                "primary_dark": "#1a66c7",
                "secondary_dark": "#6a6d6e"
            }
        },
        "flatly": {
            "type": "light",
            "colors": {
                "primary": "#2c3e50",
                "secondary": "#95a5a6",
                "success": "#18bc9c",
                "info": "#3498db",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "light": "#ecf0f1",
                "dark": "#7b8a8b",
                "bg": "#ffffff",
                "fg": "#212529",
                "selectbg": "#95a5a6",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#212529",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#ecf0f1",
                "bg_white": "#ffffff",
                "bg_light": "#ecf0f1",
                "text_primary": "#212529",
                "text_secondary": "#95a5a6",
                "text_white": "#ffffff",
                "primary_light": "#34495e",
                "primary_dark": "#1a252f",
                "secondary_dark": "#7f8c8d"
            }
        },
        "litera": {
            "type": "light",
            "colors": {
                "primary": "#4582ec",
                "secondary": "#adb5bd",
                "success": "#02b875",
                "info": "#17a2b8",
                "warning": "#f0ad4e",
                "danger": "#d9534f",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "bg": "#ffffff",
                "fg": "#343a40",
                "selectbg": "#adb5bd",
                "selectfg": "#ffffff",
                "border": "#bfbfbf",
                "inputfg": "#343a40",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_white": "#ffffff",
                "bg_light": "#f8f9fa",
                "text_primary": "#343a40",
                "text_secondary": "#adb5bd",
                "text_white": "#ffffff",
                "primary_light": "#6ba3ed",
                "primary_dark": "#2780e3",
                "secondary_dark": "#6c757d"
            }
        },
        "minty": {
            "type": "light",
            "colors": {
                "primary": "#78c2ad",
                "secondary": "#f3969a",
                "success": "#56cc9d",
                "info": "#6cc3d5",
                "warning": "#ffce67",
                "danger": "#ff7851",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "bg": "#ffffff",
                "fg": "#5a5a5a",
                "selectbg": "#f3969a",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#696969",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_white": "#ffffff",
                "bg_light": "#f8f9fa",
                "text_primary": "#5a5a5a",
                "text_secondary": "#f3969a",
                "text_white": "#ffffff",
                "primary_light": "#89d2bd",
                "primary_dark": "#67b29c",
                "secondary_dark": "#e8858a"
            }
        },
        "lumen": {
            "type": "light",
            "colors": {
                "primary": "#158cba",
                "secondary": "#919191",
                "success": "#28b62c",
                "info": "#75caeb",
                "warning": "#ff851b",
                "danger": "#ff4136",
                "light": "#f6f6f6",
                "dark": "#555555",
                "bg": "#ffffff",
                "fg": "#555555",
                "selectbg": "#919191",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#555555",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f6f6f6",
                "bg_white": "#ffffff",
                "bg_light": "#f6f6f6",
                "text_primary": "#555555",
                "text_secondary": "#919191",
                "text_white": "#ffffff",
                "primary_light": "#2a9fd4",
                "primary_dark": "#0f6b96",
                "secondary_dark": "#6c757d"
            }
        },
        "sandstone": {
            "type": "light",
            "colors": {
                "primary": "#325d88",
                "secondary": "#8e8c84",
                "success": "#93c54b",
                "info": "#29abe0",
                "warning": "#f47c3c",
                "danger": "#d9534f",
                "light": "#f8f5f0",
                "dark": "#3e3f3a",
                "bg": "#ffffff",
                "fg": "#3e3f3a",
                "selectbg": "#8e8c84",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#6e6d69",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f5f0",
                "bg_white": "#ffffff",
                "bg_light": "#f8f5f0",
                "text_primary": "#3e3f3a",
                "text_secondary": "#8e8c84",
                "text_white": "#ffffff",
                "primary_light": "#4a7ba6",
                "primary_dark": "#1f3a56",
                "secondary_dark": "#6c757d"
            }
        },
        "yeti": {
            "type": "light",
            "colors": {
                "primary": "#008cba",
                "secondary": "#707070",
                "success": "#43ac6a",
                "info": "#5bc0de",
                "warning": "#e99002",
                "danger": "#f04124",
                "light": "#eeeeee",
                "dark": "#222222",
                "bg": "#ffffff",
                "fg": "#222222",
                "selectbg": "#707070",
                "selectfg": "#ffffff",
                "border": "#cccccc",
                "inputfg": "#222222",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#eeeeee",
                "bg_white": "#ffffff",
                "bg_light": "#eeeeee",
                "text_primary": "#222222",
                "text_secondary": "#707070",
                "text_white": "#ffffff",
                "primary_light": "#1aa3d4",
                "primary_dark": "#006a8a",
                "secondary_dark": "#5a5a5a"
            }
        },
        "pulse": {
            "type": "light",
            "colors": {
                "primary": "#593196",
                "secondary": "#69676e",
                "success": "#13b955",
                "info": "#009cdc",
                "warning": "#efa31d",
                "danger": "#fc3939",
                "light": "#f9f8fc",
                "dark": "#17141f",
                "bg": "#ffffff",
                "fg": "#444444",
                "selectbg": "#69676e",
                "selectfg": "#ffffff",
                "border": "#cbc8d0",
                "inputfg": "#444444",
                "inputbg": "#fdfdfe",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f9f8fc",
                "bg_white": "#ffffff",
                "bg_light": "#f9f8fc",
                "text_primary": "#444444",
                "text_secondary": "#69676e",
                "text_white": "#ffffff",
                "primary_light": "#6e4abd",
                "primary_dark": "#3e1a6b",
                "secondary_dark": "#5a5860"
            }
        },
        "united": {
            "type": "light",
            "colors": {
                "primary": "#e95420",
                "secondary": "#aea79f",
                "success": "#38b44a",
                "info": "#17a2b8",
                "warning": "#efb73e",
                "danger": "#df382c",
                "light": "#e9ecef",
                "dark": "#772953",
                "bg": "#ffffff",
                "fg": "#333333",
                "selectbg": "#aea79f",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#333333",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#e9ecef",
                "bg_white": "#ffffff",
                "bg_light": "#e9ecef",
                "text_primary": "#333333",
                "text_secondary": "#aea79f",
                "text_white": "#ffffff",
                "primary_light": "#ed7a4a",
                "primary_dark": "#c7441a",
                "secondary_dark": "#8b8178"
            }
        },
        "morph": {
            "type": "light",
            "colors": {
                "primary": "#378dfc",
                "secondary": "#aaaaaa",
                "success": "#43cc29",
                "info": "#5b62f4",
                "warning": "#ffc107",
                "danger": "#e52527",
                "light": "#f0f5fa",
                "dark": "#212529",
                "bg": "#d9e3f1",
                "fg": "#7b8ab8",
                "selectbg": "#aaaaaa",
                "selectfg": "#fbfdff",
                "border": "#b9c7da",
                "inputfg": "#7f8eba",
                "inputbg": "#f0f5fa",
                "bg_primary": "#d9e3f1",
                "bg_secondary": "#f0f5fa",
                "bg_white": "#fbfdff",
                "bg_light": "#f0f5fa",
                "text_primary": "#7b8ab8",
                "text_secondary": "#aaaaaa",
                "text_white": "#fbfdff",
                "primary_light": "#5aa3fd",
                "primary_dark": "#2670d4",
                "secondary_dark": "#888888"
            }
        },
        "journal": {
            "type": "light",
            "colors": {
                "primary": "#eb6864",
                "secondary": "#aaaaaa",
                "success": "#22b24c",
                "info": "#336699",
                "warning": "#f5e625",
                "danger": "#f57a00",
                "light": "#f8f9fa",
                "dark": "#222222",
                "bg": "#ffffff",
                "fg": "#222222",
                "selectbg": "#aaaaaa",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#565656",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_white": "#ffffff",
                "bg_light": "#f8f9fa",
                "text_primary": "#222222",
                "text_secondary": "#aaaaaa",
                "text_white": "#ffffff",
                "primary_light": "#ee8a87",
                "primary_dark": "#d94a45",
                "secondary_dark": "#888888"
            }
        },
        "darkly": {
            "type": "dark",
            "colors": {
                "primary": "#375a7f",
                "secondary": "#444444",
                "success": "#00bc8c",
                "info": "#3498db",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "light": "#adb5bd",
                "dark": "#303030",
                "bg": "#222222",
                "fg": "#ffffff",
                "selectbg": "#555555",
                "selectfg": "#ffffff",
                "border": "#222222",
                "inputfg": "#ffffff",
                "inputbg": "#2f2f2f",
                "bg_primary": "#222222",
                "bg_secondary": "#303030",
                "bg_white": "#2f2f2f",
                "bg_light": "#303030",
                "text_primary": "#ffffff",
                "text_secondary": "#adb5bd",
                "text_white": "#ffffff",
                "primary_light": "#4a7ba6",
                "primary_dark": "#1f3a56",
                "secondary_dark": "#2d2d2d"
            }
        },
        "superhero": {
            "type": "dark",
            "colors": {
                "primary": "#4c9be8",
                "secondary": "#4e5d6c",
                "success": "#5cb85c",
                "info": "#5bc0de",
                "warning": "#f0ad4e",
                "danger": "#d9534f",
                "light": "#abb6c2",
                "dark": "#20374c",
                "bg": "#2b3e50",
                "fg": "#ffffff",
                "selectbg": "#526170",
                "selectfg": "#ffffff",
                "border": "#222222",
                "inputfg": "#ebebeb",
                "inputbg": "#32465a",
                "bg_primary": "#2b3e50",
                "bg_secondary": "#20374c",
                "bg_white": "#32465a",
                "bg_light": "#20374c",
                "text_primary": "#ffffff",
                "text_secondary": "#abb6c2",
                "text_white": "#ffffff",
                "primary_light": "#6ba3ed",
                "primary_dark": "#2780e3",
                "secondary_dark": "#3b4a58"
            }
        },
        "solar": {
            "type": "dark",
            "colors": {
                "primary": "#bc951a",
                "secondary": "#94a2a4",
                "success": "#44aca4",
                "info": "#3f98d7",
                "warning": "#d05e2f",
                "danger": "#d95092",
                "light": "#a9bdbd",
                "dark": "#073642",
                "bg": "#002b36",
                "fg": "#ffffff",
                "selectbg": "#0b5162",
                "selectfg": "#ffffff",
                "border": "#00252e",
                "inputfg": "#a9bdbd",
                "inputbg": "#073642",
                "bg_primary": "#002b36",
                "bg_secondary": "#073642",
                "bg_white": "#073642",
                "bg_light": "#073642",
                "text_primary": "#ffffff",
                "text_secondary": "#a9bdbd",
                "text_white": "#ffffff",
                "primary_light": "#d4b534",
                "primary_dark": "#8a6a12",
                "secondary_dark": "#7a888a"
            }
        },
        "cyborg": {
            "type": "dark",
            "colors": {
                "primary": "#2a9fd6",
                "secondary": "#555555",
                "success": "#77b300",
                "info": "#9933cc",
                "warning": "#ff8800",
                "danger": "#cc0000",
                "light": "#adafae",
                "dark": "#222222",
                "bg": "#060606",
                "fg": "#ffffff",
                "selectbg": "#454545",
                "selectfg": "#ffffff",
                "border": "#060606",
                "inputfg": "#ffffff",
                "inputbg": "#191919",
                "bg_primary": "#060606",
                "bg_secondary": "#222222",
                "bg_white": "#191919",
                "bg_light": "#222222",
                "text_primary": "#ffffff",
                "text_secondary": "#adafae",
                "text_white": "#ffffff",
                "primary_light": "#4bb9e3",
                "primary_dark": "#2187b8",
                "secondary_dark": "#3d3d3d"
            }
        },
        "vapor": {
            "type": "dark",
            "colors": {
                "primary": "#6e40c0",
                "secondary": "#ea38b8",
                "success": "#3af180",
                "info": "#1da2f2",
                "warning": "#ffbd05",
                "danger": "#e34b54",
                "light": "#44d7e8",
                "dark": "#170229",
                "bg": "#190831",
                "fg": "#32fbe2",
                "selectbg": "#461a8a",
                "selectfg": "#ffffff",
                "border": "#060606",
                "inputfg": "#bfb6cd",
                "inputbg": "#30115e",
                "bg_primary": "#190831",
                "bg_secondary": "#170229",
                "bg_white": "#30115e",
                "bg_light": "#170229",
                "text_primary": "#32fbe2",
                "text_secondary": "#44d7e8",
                "text_white": "#ffffff",
                "primary_light": "#8a5dd4",
                "primary_dark": "#522a9a",
                "secondary_dark": "#c62a9a"
            }
        },
        "simplex": {
            "type": "light",
            "colors": {
                "primary": "#d8220e",
                "secondary": "#858e96",
                "success": "#469307",
                "info": "#0099ce",
                "warning": "#d88220",
                "danger": "#9a479e",
                "light": "#f2f2f2",
                "dark": "#3b3d3f",
                "bg": "#fcfcfc",
                "fg": "#3b3d3f",
                "selectbg": "#a9afb6",
                "selectfg": "#ffffff",
                "border": "#858e96",
                "inputfg": "#3b3d3f",
                "inputbg": "#fcfcfc",
                "bg_primary": "#fcfcfc",
                "bg_secondary": "#f2f2f2",
                "bg_white": "#fcfcfc",
                "bg_light": "#f2f2f2",
                "text_primary": "#3b3d3f",
                "text_secondary": "#858e96",
                "text_white": "#ffffff",
                "primary_light": "#e5472f",
                "primary_dark": "#a51c0a",
                "secondary_dark": "#6c757d"
            }
        },
        "cerulean": {
            "type": "light",
            "colors": {
                "primary": "#4bb1ea",
                "secondary": "#a9b4be",
                "success": "#84b251",
                "info": "#225384",
                "warning": "#e16e25",
                "danger": "#cf3c40",
                "light": "#eceef1",
                "dark": "#33383e",
                "bg": "#ffffff",
                "fg": "#2ea4e7",
                "selectbg": "#adb5bd",
                "selectfg": "#ffffff",
                "border": "#a9b4be",
                "inputfg": "#495057",
                "inputbg": "#ffffff",
                "bg_primary": "#ffffff",
                "bg_secondary": "#eceef1",
                "bg_white": "#ffffff",
                "bg_light": "#eceef1",
                "text_primary": "#2ea4e7",
                "text_secondary": "#a9b4be",
                "text_white": "#ffffff",
                "primary_light": "#6bc1ee",
                "primary_dark": "#35a0e6",
                "secondary_dark": "#8a9aa8"
            }
        },
        # Additional themes to reach 28 total
        "default": {
            "type": "light",
            "colors": {
                "primary": "#2780e3",
                "secondary": "#7e8081",
                "success": "#3fb618",
                "info": "#9954bb",
                "warning": "#ff7518",
                "danger": "#ff0039",
                "light": "#f8f9fa",
                "dark": "#373a3c",
                "bg": "#ffffff",
                "fg": "#373a3c",
                "selectbg": "#7e8081",
                "selectfg": "#ffffff",
                "border": "#ced4da",
                "inputfg": "#373a3c",
                "inputbg": "#fdfdfe",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_white": "#ffffff",
                "bg_light": "#f8f9fa",
                "text_primary": "#373a3c",
                "text_secondary": "#7e8081",
                "text_white": "#ffffff",
                "primary_light": "#4a96e8",
                "primary_dark": "#1a66c7",
                "secondary_dark": "#6a6d6e"
            }
        }
    }
    
except ImportError:
    TTK_BOOTSTRAP_AVAILABLE = False
    TTKBOOTSTRAP_THEMES = {}

# Light theme color scheme - using ttkbootstrap standard format
LIGHT_THEME = {
    "type": "light",
    "primary": "#2780e3",
    "secondary": "#7e8081", 
    "success": "#3fb618",
    "info": "#9954bb",
    "warning": "#ff7518", 
    "danger": "#ff0039",
    "light": "#f8f9fa",
    "dark": "#373a3c",
    "bg": "#ffffff",
    "fg": "#373a3c",
    "selectbg": "#7e8081",
    "selectfg": "#ffffff",
    "border": "#ced4da",
    "inputfg": "#373a3c", 
    "inputbg": "#fdfdfe",
    # Extended properties for UI compatibility
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8f9fa",
    "bg_white": "#ffffff",
    "bg_light": "#f8f9fa",
    "text_primary": "#373a3c",
    "text_secondary": "#7e8081",
    "text_white": "#ffffff",
    "primary_light": "#4a96e8",
    "primary_dark": "#1a66c7",
    "secondary_dark": "#6a6d6e"
}

# Dark theme color scheme - using ttkbootstrap standard format
DARK_THEME = {
    "type": "dark",
    "primary": "#375a7f",
    "secondary": "#444444",
    "success": "#00bc8c",
    "info": "#3498db",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "light": "#adb5bd",
    "dark": "#303030",
    "bg": "#222222",
    "fg": "#ffffff",
    "selectbg": "#555555",
    "selectfg": "#ffffff",
    "border": "#222222",
    "inputfg": "#ffffff",
    "inputbg": "#2f2f2f",
    # Extended properties for UI compatibility
    "bg_primary": "#222222",
    "bg_secondary": "#303030",
    "bg_white": "#2f2f2f",
    "bg_light": "#303030",
    "text_primary": "#ffffff",
    "text_secondary": "#adb5bd",
    "text_white": "#ffffff",
    "primary_light": "#4a7ba6",
    "primary_dark": "#1f3a56",
    "secondary_dark": "#2d2d2d"
}

# Default to light theme
COLORS = LIGHT_THEME.copy()

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
    
    # Check if it's a ttkbootstrap theme
    if TTK_BOOTSTRAP_AVAILABLE and theme_type in TTKBOOTSTRAP_THEMES:
        theme_data = TTKBOOTSTRAP_THEMES[theme_type]
        COLORS.clear()
        COLORS.update(theme_data["colors"])
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
    # Check if it's a ttkbootstrap theme
    if TTK_BOOTSTRAP_AVAILABLE and theme_type in TTKBOOTSTRAP_THEMES:
        return TTKBOOTSTRAP_THEMES[theme_type]["colors"]
    
    # Return default themes
    if theme_mode == "dark":
        return DARK_THEME
    else:
        return LIGHT_THEME

def get_available_themes():
    """Get list of all available themes"""
    themes = ["default"]
    if TTK_BOOTSTRAP_AVAILABLE:
        themes.extend(list(TTKBOOTSTRAP_THEMES.keys()))
    return themes

def validate_theme_properties(theme_dict):
    """
    Validate that a theme dictionary has all required properties
    
    Args:
        theme_dict (dict): Theme dictionary to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_properties = [
        "primary", "secondary", "success", "info", "warning", 
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

def refresh_application_theme(root_widget=None):
    """
    Refresh theme across the entire application
    
    Args:
        root_widget: The root widget to start theme refresh from
    """
    try:
        # Import here to avoid circular imports
        from utils.theme_manager import ThemeManager
        
        if root_widget:
            # Recursively apply theme to all widgets
            _refresh_widget_theme_recursive(root_widget, ThemeManager)
            
    except Exception as e:
        print(f"Error refreshing application theme: {e}")

def _refresh_widget_theme_recursive(widget, theme_manager):
    """Recursively refresh theme for all widgets"""
    try:
        # Apply theme to current widget
        theme_manager.apply_widget_theme(widget)
        
        # Special handling for specific widget types
        widget_class = widget.winfo_class()
        if widget_class == "Toplevel":
            # Theme dialog windows
            theme_manager.theme_dialog(widget)
        elif hasattr(widget, 'refresh_colors'):
            # Call custom refresh method if available
            widget.refresh_colors()
        
        # Recursively process children
        try:
            for child in widget.winfo_children():
                _refresh_widget_theme_recursive(child, theme_manager)
        except:
            pass
            
    except Exception as e:
        pass
