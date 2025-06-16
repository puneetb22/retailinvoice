"""
Auto-login screen for POS system with company branding
"""

import tkinter as tk
from tkinter import ttk
import time
from assets.styles import COLORS, FONTS, STYLES

class AutoLoginFrame(tk.Frame):
    """Auto login frame that automatically logs in as shopkeeper after showing company details"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Make sure the frame expands to fill the entire space
        self.pack_propagate(False)
        
        # Central container for login elements
        container = tk.Frame(self, bg=COLORS["bg_primary"], padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Shop name
        shop_name = self.controller.config.get('shop_name', 'Agritech Products Shop')
        title = tk.Label(container, 
                         text=shop_name,
                         font=FONTS["heading"], 
                         bg=COLORS["bg_primary"],
                         fg=COLORS["text_primary"])
        title.pack(pady=(0, 30))
        
        # Logo and company branding
        logo_frame = tk.Frame(container, bg=COLORS["primary"], 
                             width=200, height=200)
        logo_frame.pack(pady=10)
        logo_frame.pack_propagate(False)
        
        logo_label = tk.Label(logo_frame, text="BBS", 
                             font=("Arial", 48, "bold"),
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"])
        logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Company name
        company_name = tk.Label(container, 
                              text="Baviskar Business Softwares",
                              font=FONTS["heading"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["primary"])
        company_name.pack(pady=(20, 5))
        
        # Welcome message
        welcome_msg = tk.Label(container, 
                              text="Welcome to Point of Sale System",
                              font=FONTS["subheading"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        welcome_msg.pack(pady=(5, 5))
        
        # Developer info
        developer_info = tk.Label(container, 
                                text="Developed by: Punit Sanjay Baviskar",
                                font=FONTS["regular_bold"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"])
        developer_info.pack(pady=(20, 5))
        
        # Contact info
        contact_info = tk.Label(container, 
                              text="Contact: puneetbaviskar@gmail.com",
                              font=FONTS["regular"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        contact_info.pack(pady=(0, 20))
        
        # Auto login message
        self.login_msg = tk.Label(container, 
                                 text="Loading system...",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_secondary"])
        self.login_msg.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(container, 
                                       orient="horizontal", 
                                       length=400, 
                                       mode="determinate")
        self.progress.pack(pady=20)
        
        # Style the progress bar to match the theme
        style = ttk.Style()
        style.configure("TProgressbar", thickness=20, 
                       background=COLORS["primary"], 
                       troughcolor=COLORS["bg_secondary"])
        
        # Version info at bottom
        version = self.controller.config.get('version', '1.0.0')
        version_label = tk.Label(self, 
                                text=f"Version {version}", 
                                font=FONTS["small"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_secondary"])
        version_label.pack(side=tk.BOTTOM, pady=10)
    
    def on_show(self):
        """Called when frame is shown"""
        # Reset progress
        self.progress["value"] = 0
        self.login_msg.config(text="Loading system...")
        
        # Simulate login process with 15 second duration
        self.start_login_sequence()
    
    def start_login_sequence(self):
        """Simulate login process with progress bar animation lasting 15 seconds"""
        if self.progress["value"] < 100:
            # Increase by small increments to make it last ~15 seconds
            # 100 / 2 = 50 steps, 15000ms / 50 = 300ms per step
            self.progress["value"] += 2
            
            # Update message based on progress
            if self.progress["value"] < 20:
                self.login_msg.config(text="Loading system modules...")
            elif self.progress["value"] < 40:
                self.login_msg.config(text="Connecting to database...")
            elif self.progress["value"] < 60:
                self.login_msg.config(text="Loading product catalog...")
            elif self.progress["value"] < 80:
                self.login_msg.config(text="Preparing dashboard...")
            else:
                # Set user information in controller
                self.controller.current_user = {
                    "id": 1,
                    "name": "Shopkeeper",
                    "role": "admin"
                }
                self.login_msg.config(text="Welcome, Shopkeeper!")
                
            # Continue animation (300ms per increment for ~15 seconds total)
            self.after(300, self.start_login_sequence)
        else:
            # Login complete, show dashboard
            self.after(500, self.controller.show_dashboard)
