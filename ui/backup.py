"""
Backup & Restore UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import datetime
from assets.styles import COLORS, FONTS, STYLES
from utils.backup import create_backup, restore_backup, list_backups

class BackupFrame(tk.Frame):
    """Backup and restore frame for database management"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Backup & Restore",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Main container with two frames side by side
        main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Backup list
        left_panel = tk.Frame(main_container, bg=COLORS["bg_primary"], width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Actions
        right_panel = tk.Frame(main_container, bg=COLORS["bg_secondary"], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_panel.pack_propagate(False)  # Don't shrink
        
        # Setup left panel (backup list)
        self.setup_backup_list(left_panel)
        
        # Setup right panel (actions)
        self.setup_actions_panel(right_panel)
    
    def setup_backup_list(self, parent):
        """Setup the backup list panel"""
        # Label
        list_label = tk.Label(parent, 
                            text="Available Backups",
                            font=FONTS["subheading"],
                            bg=COLORS["bg_primary"],
                            fg=COLORS["text_primary"])
        list_label.pack(anchor="w", pady=(0, 10))
        
        # Treeview frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
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
        self.backup_tree = ttk.Treeview(tree_frame, 
                                     columns=("Filename", "Date", "Size"),
                                     show="headings",
                                     yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.backup_tree.yview)
        
        # Define columns
        self.backup_tree.heading("Filename", text="Backup File")
        self.backup_tree.heading("Date", text="Date Created")
        self.backup_tree.heading("Size", text="Size")
        
        # Set column widths
        self.backup_tree.column("Filename", width=250)
        self.backup_tree.column("Date", width=150)
        self.backup_tree.column("Size", width=100)
        
        self.backup_tree.pack(fill=tk.BOTH, expand=True)
        
        # Info label at bottom
        info_label = tk.Label(parent, 
                             text="Select a backup and use buttons on the right to restore",
                             font=FONTS["small_italic"],
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_secondary"])
        info_label.pack(side=tk.BOTTOM, pady=5)
    
    def setup_actions_panel(self, parent):
        """Setup the actions panel"""
        # Title
        title = tk.Label(parent, 
                        text="Backup Actions",
                        font=FONTS["subheading"],
                        bg=COLORS["bg_secondary"],
                        fg=COLORS["text_primary"])
        title.pack(pady=(20, 30))
        
        # Create new backup using theme properties
        backup_btn = tk.Button(parent,
                             text="Create New Backup",
                             font=FONTS["regular_bold"],
                             bg=COLORS["primary"],
                             fg=COLORS["text_white"],
                             activebackground=COLORS["primary_light"],
                             activeforeground=COLORS["text_white"],
                             padx=20,
                             pady=10,
                             cursor="hand2",
                             command=self.create_new_backup)
        backup_btn.pack(pady=10, fill=tk.X, padx=20)
        
        # Restore selected backup using theme properties
        restore_btn = tk.Button(parent,
                              text="Restore Selected Backup",
                              font=FONTS["regular"],
                              bg=COLORS["secondary"],
                              fg=COLORS["text_white"],
                              activebackground=COLORS["secondary_dark"],
                              activeforeground=COLORS["text_white"],
                              padx=20,
                              pady=10,
                              cursor="hand2",
                              command=self.restore_selected_backup)
        restore_btn.pack(pady=10, fill=tk.X, padx=20)
        
        # Refresh list using theme properties
        refresh_btn = tk.Button(parent,
                              text="Refresh List",
                              font=FONTS["regular"],
                              bg=COLORS["info"],
                              fg=COLORS["text_white"],
                              activebackground=COLORS["info"],
                              activeforeground=COLORS["text_white"],
                              padx=20,
                              pady=10,
                              cursor="hand2",
                              command=self.load_backups)
        refresh_btn.pack(pady=10, fill=tk.X, padx=20)
        
        # Import backup using theme properties
        import_btn = tk.Button(parent,
                             text="Import Backup File",
                             font=FONTS["regular"],
                             bg=COLORS["bg_white"],
                             fg=COLORS["text_primary"],
                             activebackground=COLORS["bg_primary"],
                             activeforeground=COLORS["text_primary"],
                             padx=20,
                             pady=10,
                             cursor="hand2",
                             command=self.import_backup)
        import_btn.pack(pady=10, fill=tk.X, padx=20)
        
        # Export backup using theme properties
        export_btn = tk.Button(parent,
                             text="Export Selected Backup",
                             font=FONTS["regular"],
                             bg=COLORS["bg_white"],
                             fg=COLORS["text_primary"],
                             activebackground=COLORS["bg_primary"],
                             activeforeground=COLORS["text_primary"],
                             padx=20,
                             pady=10,
                             cursor="hand2",
                             command=self.export_backup)
        export_btn.pack(pady=10, fill=tk.X, padx=20)
        
        # Delete backup using theme properties
        delete_btn = tk.Button(parent,
                             text="Delete Selected Backup",
                             font=FONTS["regular"],
                             bg=COLORS["danger"],
                             fg=COLORS["text_white"],
                             activebackground=COLORS["danger"],
                             activeforeground=COLORS["text_white"],
                             padx=20,
                             pady=10,
                             cursor="hand2",
                             command=self.delete_backup)
        delete_btn.pack(pady=10, fill=tk.X, padx=20)
    
    def load_backups(self):
        """Load backups into the treeview"""
        # Clear current items
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        # Get backups
        backups = list_backups()
        
        if not backups:
            # No backups found
            self.backup_tree.insert("", "end", values=("No backups found", "", ""))
            return
        
        # Insert into treeview
        for backup in backups:
            date_str = backup["date"].strftime("%Y-%m-%d %H:%M:%S")
            size_str = f"{backup['size_mb']} MB"
            
            self.backup_tree.insert("", "end", values=(
                backup["filename"],
                date_str,
                size_str
            ), tags=(backup["path"],))
    
    def create_new_backup(self):
        """Create a new database backup"""
        # Show confirmation dialog
        if messagebox.askyesno("Backup", "Create a new backup of the database?"):
            # Create backup
            success = create_backup(self.controller.db)
            
            if success:
                messagebox.showinfo("Backup", "Backup created successfully!")
                # Refresh list
                self.load_backups()
            else:
                messagebox.showerror("Backup Error", "Failed to create backup. Please check permissions.")
    
    def restore_selected_backup(self):
        """Restore the selected backup"""
        # Get selected backup
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showinfo("Restore", "Please select a backup to restore.")
            return
        
        # Get backup path from tags
        item_tags = self.backup_tree.item(selection[0], "tags")
        if not item_tags:
            messagebox.showinfo("Restore", "Invalid backup selection.")
            return
        
        backup_path = item_tags[0]
        
        # Show warning and confirmation
        if messagebox.askyesno("Restore", 
                             "WARNING: Restoring a backup will replace all current data! Continue?",
                             icon="warning"):
            # Restore backup
            success = restore_backup(self.controller.db, backup_path)
            
            if success:
                messagebox.showinfo("Restore", "Backup restored successfully!")
            else:
                messagebox.showerror("Restore Error", "Failed to restore backup.")
    
    def import_backup(self):
        """Import a backup file from external location"""
        # Ask for file
        file_path = filedialog.askopenfilename(
            title="Import Backup File",
            filetypes=[("SQLite Database", "*.db")]
        )
        
        if not file_path:
            return
        
        # Check if valid backup
        if not os.path.exists(file_path):
            messagebox.showerror("Import Error", "Invalid file path.")
            return
        
        # Copy to backups directory
        try:
            backup_dir = "./backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate new filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"pos_backup_{timestamp}.db")
            
            # Copy file
            import shutil
            shutil.copy2(file_path, backup_path)
            
            messagebox.showinfo("Import", "Backup file imported successfully!")
            # Refresh list
            self.load_backups()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import backup: {e}")
    
    def export_backup(self):
        """Export the selected backup to external location"""
        # Get selected backup
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showinfo("Export", "Please select a backup to export.")
            return
        
        # Get backup path from tags
        item_tags = self.backup_tree.item(selection[0], "tags")
        if not item_tags:
            messagebox.showinfo("Export", "Invalid backup selection.")
            return
        
        backup_path = item_tags[0]
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Export Backup File",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")]
        )
        
        if not file_path:
            return
        
        # Copy file
        try:
            import shutil
            shutil.copy2(backup_path, file_path)
            messagebox.showinfo("Export", "Backup exported successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export backup: {e}")
    
    def delete_backup(self):
        """Delete the selected backup"""
        # Get selected backup
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showinfo("Delete", "Please select a backup to delete.")
            return
        
        # Get backup path from tags
        item_tags = self.backup_tree.item(selection[0], "tags")
        if not item_tags:
            messagebox.showinfo("Delete", "Invalid backup selection.")
            return
        
        backup_path = item_tags[0]
        
        # Show confirmation
        if messagebox.askyesno("Delete", "Are you sure you want to delete this backup?"):
            try:
                # Delete file
                os.remove(backup_path)
                messagebox.showinfo("Delete", "Backup deleted successfully!")
                # Refresh list
                self.load_backups()
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete backup: {e}")
    
    def on_show(self):
        """Called when frame is shown"""
        # Load backups
        self.load_backups()