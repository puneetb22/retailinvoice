"""
Database handler for POS system
Manages SQLite connection and common operations
"""

import os
import sqlite3
import datetime
from pathlib import Path
from database.schema import DB_SCHEMA, INITIAL_DATA

class DBHandler:
    """SQLite database handler class for POS system"""

    def __init__(self, db_path="./pos_data.db"):
        """Initialize database connection and setup if needed"""
        self.db_path = db_path
        self.is_initialized = False
        self.conn = None
        self.cursor = None

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        # Initialize database
        try:
            self._initialize_db()
            self.is_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")
            self.is_initialized = False

    def _initialize_db(self):
        """Create database and tables if they don't exist"""
        db_exists = os.path.exists(self.db_path)

        # Connect to database
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Create cursor
        self.cursor = self.conn.cursor()

        # Create tables if database is new
        if not db_exists:
            for table_name, table_schema in DB_SCHEMA.items():
                self.cursor.execute(table_schema)

            # Insert initial data
            for table, rows in INITIAL_DATA.items():
                for row in rows:
                    placeholders = ", ".join(["?"] * len(row))
                    columns = ", ".join(row.keys())
                    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(sql, list(row.values()))

            # Commit changes
            self.conn.commit()

        # Always check for schema updates needed - even for new databases
        # This ensures any future schema changes are automatically applied
        self._check_and_update_schema()

    def execute(self, query, params=None):
        """Execute a query with parameters"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def fetchone(self, query, params=None):
        """Execute query and fetch a single row"""
        cursor = self.execute(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def fetchall(self, query, params=None):
        """Execute query and fetch all rows"""
        cursor = self.execute(query, params)
        if cursor:
            return cursor.fetchall()
        return []

    def insert(self, table, data):
        """Insert a new row into the specified table"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        # Convert decimal.Decimal values to float for SQLite compatibility
        values = []
        for value in data.values():
            if hasattr(value, '__module__') and value.__module__ == 'decimal':
                values.append(float(value))
            else:
                values.append(value)

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Insert error: {e}")
            return None

    def update(self, table, data, condition):
        """Update rows in the specified table"""
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

        # Convert decimal.Decimal values to float for SQLite compatibility
        values = []
        for value in data.values():
            if hasattr(value, '__module__') and value.__module__ == 'decimal':
                values.append(float(value))
            else:
                values.append(value)

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Update error: {e}")
            return 0

    def delete(self, table, condition):
        """Delete rows from the specified table"""
        query = f"DELETE FROM {table} WHERE {condition}"

        try:
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Delete error: {e}")
            return 0

    def commit(self):
        """Commit changes to the database"""
        self.conn.commit()

    def begin(self):
        """Begin a transaction
        SQLite automatically begins a transaction when needed,
        but we include this method for API completeness and to make code more readable
        """
        pass  # SQLite automatically starts a transaction when needed

    def rollback(self):
        """Rollback changes"""
        self.conn.rollback()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def backup_database(self, backup_path):
        """Create a backup of the database"""
        try:
            # Create a new database connection for backup
            backup_conn = sqlite3.connect(backup_path)
            # Backup current database to the new file
            self.conn.backup(backup_conn)
            backup_conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Backup error: {e}")
            return False

    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            # Close existing connection
            self.close()

            # Open backup database
            backup_conn = sqlite3.connect(backup_path)

            # Connect to the target database
            self.conn = sqlite3.connect(self.db_path)

            # Restore from backup
            backup_conn.backup(self.conn)

            # Close backup connection
            backup_conn.close()

            # Reinitialize cursor
            self.cursor = self.conn.cursor()

            return True
        except sqlite3.Error as e:
            print(f"Restore error: {e}")
            return False

    def _check_and_update_schema(self):
        """Check for required schema updates and apply them"""
        try:
            # Get the list of columns in the sales table
            columns_info = self.fetchall("PRAGMA table_info(sales)")
            column_names = [col[1] for col in columns_info]

            # Check if cgst, sgst columns exist in sales table
            if 'cgst' not in column_names:
                print("Adding cgst column to sales table...")
                self.execute("ALTER TABLE sales ADD COLUMN cgst REAL DEFAULT 0")

            if 'sgst' not in column_names:
                print("Adding sgst column to sales table...")
                self.execute("ALTER TABLE sales ADD COLUMN sgst REAL DEFAULT 0")

            # Get the list of columns in the sale_items table
            columns_info = self.fetchall("PRAGMA table_info(sale_items)")
            column_constraints = {col[1]: col[3] for col in columns_info}  # col[3] is NOT NULL constraint (0 or 1)

            # Check if important tables exist
            tables = self.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [table[0] for table in tables]

            # Check for suspended_bills table
            if 'suspended_bills' not in table_names:
                print("Creating suspended_bills table...")
                self.execute("""
                    CREATE TABLE suspended_bills (
                        id INTEGER PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        bill_data TEXT NOT NULL,
                        discount REAL DEFAULT 0,
                        discount_type TEXT DEFAULT 'amount',
                        notes TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers(id)
                    )
                """)

            # Check for stock_log table
            if 'stock_log' not in table_names:
                print("Creating stock_log table...")
                self.execute("""
                    CREATE TABLE stock_log (
                        id INTEGER PRIMARY KEY,
                        batch_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL,
                        quantity_change INTEGER NOT NULL,
                        quantity_before INTEGER NOT NULL,
                        quantity_after INTEGER NOT NULL,
                        reference_type TEXT,
                        reference_id INTEGER,
                        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (batch_id) REFERENCES batches(id),
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    )
                """)

            # Check for categories table
            if 'categories' not in table_names:
                print("Creating categories table...")
                self.execute(DB_SCHEMA["categories"])
                # Insert initial data
                if "categories" in INITIAL_DATA:
                    for row in INITIAL_DATA["categories"]:
                        placeholders = ", ".join(["?"] * len(row))
                        columns = ", ".join(row.keys())
                        sql = f"INSERT INTO categories ({columns}) VALUES ({placeholders})"
                        self.execute(sql, list(row.values()))
                    print("Added initial category data")

            # Check for hsn_codes table
            if 'hsn_codes' not in table_names:
                print("Creating hsn_codes table...")
                self.execute(DB_SCHEMA["hsn_codes"])
                # Insert initial data
                if "hsn_codes" in INITIAL_DATA:
                    for row in INITIAL_DATA["hsn_codes"]:
                        placeholders = ", ".join(["?"] * len(row))
                        columns = ", ".join(row.keys())
                        sql = f"INSERT INTO hsn_codes ({columns}) VALUES ({placeholders})"
                        self.execute(sql, list(row.values()))
                    print("Added initial HSN codes data")

            # Fix tax_rate references in sale_items to be consistent with the rest of the app
            # which uses tax_percentage naming convention
            columns_info = self.fetchall("PRAGMA table_info(sale_items)")
            column_names = [col[1] for col in columns_info]

            if 'tax_rate' in column_names and 'tax_percentage' not in column_names:
                print("Updating sale_items table: renaming tax_rate to tax_percentage...")
                # SQLite doesn't support direct column renaming, so we need to create a temporary table
                self.execute("ALTER TABLE sale_items RENAME TO sale_items_old")

                # Create new table with correct column name
                self.execute("""
                    CREATE TABLE sale_items (
                        id INTEGER PRIMARY KEY,
                        sale_id INTEGER NOT NULL,
                        product_id INTEGER,
                        product_name TEXT NOT NULL,
                        hsn_code TEXT,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        discount_percent REAL DEFAULT 0,
                        tax_percentage REAL DEFAULT 0,
                        tax_amount REAL DEFAULT 0,
                        total REAL NOT NULL,
                        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    )
                """)

                # Copy data from old table to new table
                self.execute("""
                    INSERT INTO sale_items (id, sale_id, product_id, product_name, hsn_code, 
                                            quantity, price, discount_percent, tax_percentage, 
                                            tax_amount, total)
                    SELECT id, sale_id, product_id, product_name, hsn_code, 
                           quantity, price, discount_percent, tax_rate, 
                           tax_amount, total
                    FROM sale_items_old
                """)

                # Drop old table
                self.execute("DROP TABLE sale_items_old")
                print("Successfully renamed tax_rate to tax_percentage in sale_items table")

            # Check if selling_price column exists in batches table
            try:
                self.execute("SELECT selling_price FROM batches LIMIT 1")
            except:
                # Column doesn't exist, add it
                print("Adding selling_price column to batches table...")
                self.execute("ALTER TABLE batches ADD COLUMN selling_price REAL DEFAULT 0")

                # Copy selling price from products to existing batches
                self.execute("""
                    UPDATE batches 
                    SET selling_price = (
                        SELECT selling_price 
                        FROM products 
                        WHERE products.id = batches.product_id
                    )
                    WHERE selling_price = 0 OR selling_price IS NULL
                """)
                self.commit()

            # Commit all schema changes
            self.commit()
            print("Schema update completed successfully")
        except sqlite3.Error as e:
            print(f"Schema update error: {e}")
            self.rollback()