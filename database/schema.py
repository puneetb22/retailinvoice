"""
Database schema for POS system
Defines table structure and initial data
"""

import datetime

# Define table schemas
DB_SCHEMA = {
    "settings": """
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        )
    """,

    "categories": """
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    "vendors": """
        CREATE TABLE vendors (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            gstin TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    "hsn_codes": """
        CREATE TABLE hsn_codes (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            tax_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    "products": """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            product_code TEXT UNIQUE,
            name TEXT NOT NULL,
            vendor TEXT,
            hsn_code TEXT,
            category TEXT,
            description TEXT,
            wholesale_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            tax_percentage REAL DEFAULT 0,
            manufacturer TEXT,
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    "inventory": """
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            manufacturing_date DATE,
            expiry_date DATE,
            purchase_date DATE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """,

    "customers": """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            village TEXT,
            gstin TEXT,
            credit_limit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    "invoices": """
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            subtotal REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'PAID',
            cash_amount REAL DEFAULT 0,
            upi_amount REAL DEFAULT 0,
            upi_reference TEXT,
            credit_amount REAL DEFAULT 0,
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """,

    "invoice_items": """
        CREATE TABLE invoice_items (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            discount_percentage REAL DEFAULT 0,
            tax_percentage REAL DEFAULT 0,
            total_price REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """,

    "expenses": """
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY,
            expense_date DATE NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    "supplier_transactions": """
        CREATE TABLE supplier_transactions (
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
    """,

    "inventory_transactions": """
        CREATE TABLE inventory_transactions (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            reference_id INTEGER,
            notes TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """,

    "batches": """
        CREATE TABLE batches (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_number TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            manufacturing_date DATE,
            expiry_date DATE,
            purchase_date DATE DEFAULT CURRENT_TIMESTAMP,
            cost_price REAL NOT NULL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """,

    "inventory_movements": """
        CREATE TABLE inventory_movements (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            batch_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            reference_id INTEGER,
            movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (batch_id) REFERENCES batches(id)
        )
    """,

    "sales": """
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            invoice_number TEXT UNIQUE NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            cgst REAL DEFAULT 0,
            sgst REAL DEFAULT 0,
            total REAL NOT NULL,
            payment_type TEXT NOT NULL,
            payment_reference TEXT,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """,

    "sale_items": """
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            hsn_code TEXT,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            tax_rate REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """,

    "payment_splits": """
        CREATE TABLE payment_splits (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER NOT NULL,
            cash_amount REAL DEFAULT 0,
            upi_amount REAL DEFAULT 0,
            upi_reference TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
        )
    """,

    "customer_transactions": """
        CREATE TABLE customer_transactions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            reference_id INTEGER,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """,

    "customer_payments": """
        CREATE TABLE customer_payments (
            id INTEGER PRIMARY KEY, 
            customer_id INTEGER NOT NULL, 
            invoice_id INTEGER NOT NULL, 
            amount REAL NOT NULL, 
            payment_method TEXT NOT NULL, 
            reference_number TEXT, 
            depositor_name TEXT,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """,

    "stock_log": """
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
    """
}

# Initial data to populate the database
INITIAL_DATA = {
    "settings": [
        {"key": "shop_name", "value": "Agritech Products Shop"},
        {"key": "shop_address", "value": "Main Road, Maharashtra"},
        {"key": "shop_phone", "value": "+91 1234567890"},
        {"key": "shop_gst", "value": "27AABCU9603R1ZX"},
        {"key": "shop_email", "value": "contact@agritech.com"},
        {"key": "state_name", "value": "Maharashtra"},
        {"key": "state_code", "value": "27"},
        {"key": "shop_laid_no", "value": "L12345"},
        {"key": "shop_lcsd_no", "value": "C67890"},
        {"key": "shop_lfrd_no", "value": "F54321"},
        {"key": "invoice_prefix", "value": "AGT"},
        {"key": "invoice_template", "value": "shop_bill"},
        {"key": "terms_conditions", "value": "Goods once sold cannot be returned. Payment due within 30 days."},
        {"key": "low_stock_threshold", "value": "10"},
        {"key": "version", "value": "1.0.0"},
        {"key": "product_categories", "value": "Fertilizers,Pesticides,Seeds,Equipment,Other"}, 
        {"key": "vendors", "value": "Mahindra Agri,IFFCO,Rallis India,UPL Limited,Syngenta,Bayer CropScience,Godrej Agrovet"}
    ],

    "categories": [
        {"name": "Fertilizers", "description": "Chemical and organic fertilizers for crops"},
        {"name": "Pesticides", "description": "Insecticides, fungicides, and other crop protection chemicals"},
        {"name": "Seeds", "description": "Crop seeds, vegetable seeds, and plant seeds"},
        {"name": "Equipment", "description": "Farming tools and equipment"},
        {"name": "Other", "description": "Miscellaneous agricultural products"}
    ],

    "vendors": [
        {"name": "Mahindra Agri", "contact_person": "Rajesh Kumar", "phone": "9898989898", "email": "rajesh@mahindraagri.com", "address": "Mumbai, Maharashtra", "gstin": "27AAECS1234F1Z5"},
        {"name": "IFFCO", "contact_person": "Sanjay Verma", "phone": "9787878787", "email": "sanjay@iffco.in", "address": "Delhi, India", "gstin": "07AAACI5432A1Z3"},
        {"name": "Rallis India", "contact_person": "Priya Sharma", "phone": "9676767676", "email": "priya@rallis.co.in", "address": "Pune, Maharashtra", "gstin": "27AABCR7654B1Z8"},
        {"name": "UPL Limited", "contact_person": "Amit Patel", "phone": "9565656565", "email": "amit@upl.com", "address": "Mumbai, Maharashtra", "gstin": "27AAACU8765C1Z6"},
        {"name": "Syngenta", "contact_person": "Neeraj Singh", "phone": "9454545454", "email": "neeraj@syngenta.com", "address": "Bengaluru, Karnataka", "gstin": "29AADCS9876D1Z4"},
        {"name": "Bayer CropScience", "contact_person": "Vikram Desai", "phone": "9343434343", "email": "vikram@bayer.com", "address": "Hyderabad, Telangana", "gstin": "36AAACB0987E1Z2"},
        {"name": "Godrej Agrovet", "contact_person": "Meera Reddy", "phone": "9232323232", "email": "meera@godrej.com", "address": "Mumbai, Maharashtra", "gstin": "27AAACG2109F1Z0"}
    ],

    "hsn_codes": [
        {"code": "0701-0714", "description": "Edible vegetables and certain roots and tubers (e.g., potatoes, onions, beans)", "tax_rate": 5.0},
        {"code": "0801-0814", "description": "Edible fruits and nuts (e.g., mangoes, bananas, citrus fruits, cashew nuts)", "tax_rate": 5.0},
        {"code": "0901-0910", "description": "Coffee, tea, mate, and spices", "tax_rate": 5.0},
        {"code": "1001-1006", "description": "Cereals (wheat, rice, maize, barley, oats, rye)", "tax_rate": 5.0},
        {"code": "1201-1214", "description": "Oil seeds, oleaginous fruits, industrial or medicinal plants", "tax_rate": 5.0},
        {"code": "1301-1302", "description": "Lac, gums, resins, and other vegetable saps and extracts", "tax_rate": 12.0},
        {"code": "1507-1518", "description": "Animal or vegetable fats and oils", "tax_rate": 5.0},
        {"code": "1701", "description": "Cane or beet sugar and chemically pure sucrose", "tax_rate": 5.0},
        {"code": "2301-2309", "description": "Residues and waste from the food industries; prepared animal fodder", "tax_rate": 5.0},
        {"code": "3105", "description": "Mineral or chemical fertilizers containing nitrogen, phosphorus, potassium (NPK fertilizers)", "tax_rate": 5.0},
        {"code": "310590", "description": "Other fertilizers", "tax_rate": 5.0},
        {"code": "3808", "description": "Insecticides, rodenticides, fungicides, herbicides, anti-sprouting products, plant-growth regulators, disinfectants", "tax_rate": 12.0},
        {"code": "8432", "description": "Agricultural, horticultural or forestry machinery for soil preparation or cultivation (e.g., ploughs, harrows)", "tax_rate": 18.0},
        {"code": "84322100", "description": "Disc harrows", "tax_rate": 18.0},
        {"code": "8436", "description": "Other agricultural, horticultural, forestry, poultry-keeping or bee-keeping machinery", "tax_rate": 18.0}
    ],

    "customers": [
        {
            "name": "Walk-in Customer",
            "phone": "",
            "email": "",
            "address": "",
            "village": "",
            "gstin": "",
            "credit_limit": 0
        },
        {
            "name": "Prakash Bhosle",
            "phone": "9876543210",
            "email": "prakash@example.com",
            "address": "123 Farmer's Colony",
            "village": "Nashik",
            "gstin": "27ABCPB1234A1Z5",
            "credit_limit": 5000
        },
        {
            "name": "Sanjay Patil",
            "phone": "8765432109",
            "email": "sanjay@example.com",
            "address": "456 Agriculture Road",
            "village": "Nanded",
            "gstin": "27AADCP5678B1Z7",
            "credit_limit": 2000
        }
    ],

    "products": [
        {
            "product_code": "FERT001",
            "name": "Urea Fertilizer",
            "category": "Fertilizers",
            "vendor": "IFFCO",
            "hsn_code": "3102",
            "description": "Nitrogen-rich fertilizer",
            "wholesale_price": 450,
            "selling_price": 500,
            "tax_percentage": 5
        },
        {
            "product_code": "PEST001",
            "name": "General Insecticide",
            "category": "Pesticides",
            "vendor": "Rallis India",
            "hsn_code": "3808",
            "description": "Broad-spectrum insecticide",
            "wholesale_price": 320,
            "selling_price": 380,
            "tax_percentage": 12
        },
        {
            "product_code": "SEED001",
            "name": "BT Cotton Seeds",
            "category": "Seeds",
            "vendor": "Mahindra Agri",
            "hsn_code": "1207",
            "description": "High yield cotton seeds (1 kg package)",
            "wholesale_price": 850,
            "selling_price": 950,
            "tax_percentage": 5
        },
        {
            "product_code": "EQUIP001",
            "name": "Hand Sprayer",
            "category": "Equipment",
            "vendor": "UPL Limited",
            "hsn_code": "8424",
            "description": "Manual pesticide sprayer",
            "wholesale_price": 750,
            "selling_price": 900,
            "tax_percentage": 18
        }
    ],

    "batches": [
        {
            "product_id": 1,
            "batch_number": "F001B001",
            "quantity": 50,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
            "cost_price": 450,
            "selling_price": 500
        },
        {
            "product_id": 2,
            "batch_number": "P001B001",
            "quantity": 30,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=730)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=20)).strftime('%Y-%m-%d'),
            "cost_price": 320,
            "selling_price": 380
        },
        {
            "product_id": 3,
            "batch_number": "S001B001",
            "quantity": 15,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=120)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365*2)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=15)).strftime('%Y-%m-%d'),
            "cost_price": 850,
            "selling_price": 950
        },
        {
            "product_id": 4,
            "batch_number": "E001B001",
            "quantity": 10,
            "manufacturing_date": (datetime.datetime.now() - datetime.timedelta(days=180)).strftime('%Y-%m-%d'),
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365*5)).strftime('%Y-%m-%d'),
            "purchase_date": (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d'),
            "cost_price": 750,
            "selling_price": 900
        }
    ]
}

def update_schema(db):
    """Update database schema to latest version"""
    print("Creating stock_log table...")

    # Check if stock_log table exists
    result = db.fetchone("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='stock_log'
    """)

    if not result:
        # Create stock_log table
        db.execute("""
            CREATE TABLE stock_log (
                id INTEGER PRIMARY KEY,
                batch_id INTEGER,
                product_id INTEGER,
                transaction_type TEXT NOT NULL,
                quantity_change INTEGER NOT NULL,
                quantity_before INTEGER,
                quantity_after INTEGER,
                reference_type TEXT,
                reference_id INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        db.commit()

    # Check if selling_price column exists in batches table
    try:
        db.execute("SELECT selling_price FROM batches LIMIT 1")
    except:
        # Column doesn't exist, add it
        print("Adding selling_price column to batches table...")
        db.execute("ALTER TABLE batches ADD COLUMN selling_price REAL DEFAULT 0")

        # Copy selling price from products to existing batches
        db.execute("""
            UPDATE batches 
            SET selling_price = (
                SELECT selling_price 
                FROM products 
                WHERE products.id = batches.product_id
            )
            WHERE selling_price = 0 OR selling_price IS NULL
        """)
        db.commit()

    print("Schema update completed successfully")