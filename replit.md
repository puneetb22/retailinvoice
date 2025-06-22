# POS Application - Replit Migration

## Project Overview
This is a comprehensive Point of Sale (POS) system built with Python and Tkinter, featuring:
- Sales transactions with cart management
- Product and inventory management
- Customer management
- Invoice generation (PDF)
- Sales reporting and analytics
- Accounting features
- Database backup functionality

## Recent Changes
- **2024-01-XX**: Migrated from Replit Agent to Replit environment
- Fixed syntax errors in ui/sales.py (removed XML tags)
- Installed required dependencies via pyproject.toml
- Successfully launched application in Replit workflow

## Project Architecture
- **Frontend**: Tkinter-based GUI with multiple screens
- **Backend**: SQLite database with custom DBHandler
- **Structure**:
  - `main.py` - Application entry point
  - `ui/` - All UI components (dashboard, sales, products, etc.)
  - `database/` - Database handler and schema
  - `utils/` - Helper utilities (invoice generation, backup, etc.)
  - `assets/` - Styling and assets

## User Preferences
- Prefers quick fixes over feature additions
- Focus on maintaining existing functionality
- Application is 90% complete, minimal changes needed

## Technical Notes
- Uses Python 3.11 with Tkinter for GUI
- SQLite database for data storage
- ReportLab for PDF invoice generation
- Supports batch inventory management
- Multi-payment methods (cash, UPI, split payments)