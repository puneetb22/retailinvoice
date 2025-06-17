Applying the provided changes to the original code to ensure correct invoice generation with batch-specific pricing.
```

```python
"""
PDF Invoice Generator for POS system
Generates invoices matching exactly the shop_bill.pdf template
"""

import os
import datetime
import io
import platform
import subprocess
from decimal import Decimal, InvalidOperation
from utils.helpers import format_currency, num_to_words_indian

# Import ReportLab for PDF generation
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Frame, PageTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("ReportLab not available - PDF invoice generation will not work")
    REPORTLAB_AVAILABLE = False

def generate_invoice(invoice_data, save_path):
    """
    Generate a PDF invoice that exactly matches the shop_bill.pdf template

    Args:
        invoice_data: Dictionary containing invoice details
        save_path: Path to save the PDF invoice

    Returns:
        bool: True if successful, False otherwise
    """
    if not REPORTLAB_AVAILABLE:
        print("Error: ReportLab library is not available. PDF invoice generation not possible.")
        return False

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # Create the PDF document in landscape orientation
        doc = SimpleDocTemplate(
            save_path,
            pagesize=landscape(A4),  # Use landscape orientation
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Create custom styles that match exactly the shop_bill.pdf template
        styles.add(ParagraphStyle(
            name='ShopName',
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='ShopInfo',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='StateName',
            fontSize=8,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='CustomerInfo',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='OriginalCopy',
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='RightAligned',
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='InvoiceLabel',
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='InvoiceInfo',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='AmountWords',
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='ItemData',
            fontSize=8,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='TableHeader',
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='TableHeaderLeft',
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='Terms',
            fontSize=7,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='Subject',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0
        ))

        styles.add(ParagraphStyle(
            name='PaymentRecordsHeader',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0
        ))

        # Create elements list to build PDF
        elements = []

        # First try to get shop info from the settings table in the database
        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            conn.row_factory = sqlite3.Row  # Set row factory to access by column name
            cursor = conn.cursor()

            # Print all settings first for debugging
            cursor.execute("SELECT * FROM settings")
            all_settings = cursor.fetchall()
            print("All settings in database:")
            for row in all_settings:
                print(f"  ID: {row['id']}, Key: {row['key']}, Value: {row['value']}")

            # Query the settings table for shop information using the correct column names (key, value)
            cursor.execute("SELECT key, value FROM settings")
            all_db_settings = cursor.fetchall()
            print("All retrieved settings:")
            for row in all_db_settings:
                print(f"  Key: {row['key']}, Value: {row['value']}")

            # Create a dictionary from all settings
            store_info = {}
            for row in all_db_settings:
                store_info[row['key']] = row['value']

            # Close the database connection
            conn.close()

            # Print the store info we're using
            print("Store info being used for invoice:")
            for key, value in store_info.items():
                print(f"  {key}: {value}")

        except Exception as e:
            print(f"Error fetching shop info from database: {e}")
            # Fall back to the provided store_info
            store_info = invoice_data.get('store_info', {})
            print("Using fallback store_info from invoice_data due to error")

        # Shop information fields - match exactly to the keys in the settings table
        shop_name = store_info.get('shop_name', 'Agritech Products Shop')
        shop_address = store_info.get('shop_address', 'Main Road, Maharashtra')
        shop_phone = store_info.get('shop_phone', '+91 1234567890')
        shop_gst = store_info.get('shop_gst', '27AABCU9603R1ZX')
        shop_email = store_info.get('shop_email', '')

        # Special license fields
        shop_laid_no = store_info.get('shop_laid_no', '')
        shop_lcsd_no = store_info.get('shop_lcsd_no', '')
        shop_lfrd_no = store_info.get('shop_lfrd_no', '')

        # State info
        state_name = store_info.get('state_name', 'Maharashtra')
        state_code = store_info.get('state_code', '27')

        # Extract customer data
        customer_data = invoice_data.get('customer', {})
        invoice_number = invoice_data.get('invoice_number', '')
        invoice_id = invoice_data.get('invoice_id', '')

        # Format date - Use provided date or fallback to current date
        date_obj = None
        if 'date' in invoice_data and invoice_data['date']:
            date_str = invoice_data['date']
            # Try different date formats
            date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
            for date_format in date_formats:
                try:
                    date_obj = datetime.datetime.strptime(date_str, date_format)
                    break
                except ValueError:
                    continue

        # Only use current date if no valid date was provided
        if date_obj is None:
            date_obj = datetime.datetime.now()

        # Always format the date in DD/MM/YYYY format for consistency
        invoice_date = date_obj.strftime('%d/%m/%Y')
        # Format time with proper spacing
        invoice_time = invoice_data.get('time', date_obj.strftime('%I:%M %p'))
        if not invoice_time.startswith(' '):
            invoice_time = ' ' + invoice_time

        # Print debug information
        print(f"Debug - Invoice date from data: {invoice_data.get('date')}")
        print(f"Debug - Parsed date object: {date_obj}")
        print(f"Debug - Final invoice date: {invoice_date}")
        print(f"Debug - Final invoice time: {invoice_time}")

        # Customer information - Fixed to properly fetch email
        customer_name = customer_data.get('name', 'Walk-in Customer')
        customer_phone = customer_data.get('phone', '')
        customer_address = customer_data.get('address', '')
        customer_village = customer_data.get('village', '')
        if customer_village and not customer_village in customer_address:
            customer_address = f"{customer_address}, {customer_village}"
        # Fix: Properly fetch customer email
        customer_email = customer_data.get('email', '')
        customer_gstin = customer_data.get('gstin', '')

        # Payment information
        payment_data = invoice_data.get('payment', {})
        payment_method = payment_data.get('method', 'Cash')

        # Ensure payment_method is a string
        if not isinstance(payment_method, str):
            payment_method = str(payment_method) if payment_method is not None else 'Cash'

        payment_status = payment_data.get('status', 'PAID')

        # Extract financial data
        try:
            subtotal = float(payment_data.get('subtotal', 0))
        except (ValueError, TypeError):
            subtotal = 0.0

        try:
            discount = float(payment_data.get('discount', 0))
        except (ValueError, TypeError):
            discount = 0.0

        # Set default tax rates
        cgst_rate = 9.0  # Default CGST rate
        sgst_rate = 9.0  # Default SGST rate

        # Get tax rates from the invoice data if available
        if 'cgst_rate' in payment_data:
            try:
                cgst_rate = float(payment_data.get('cgst_rate', 9.0))
            except (ValueError, TypeError):
                cgst_rate = 9.0

        if 'sgst_rate' in payment_data:
            try:
                sgst_rate = float(payment_data.get('sgst_rate', 2.5))
            except (ValueError, TypeError):
                sgst_rate = 9.0

        try:
            cgst = float(payment_data.get('cgst', 0))
        except (ValueError, TypeError):
            cgst = 0.0

        try:
            sgst = float(payment_data.get('sgst', 0))
        except (ValueError, TypeError):
            sgst = 0.0

        try:
            total = float(payment_data.get('total', 0))
        except (ValueError, TypeError):
            total = 0.0

        # Calculate taxable value (subtotal - discount)
        taxable_value = subtotal - discount

        # Calculate outstanding amount based on payment method
        outstanding_amount = 0
        payment_method_upper = payment_method.upper() if isinstance(payment_method, str) else str(payment_method).upper()

        if payment_method_upper == "CREDIT":
            outstanding_amount = total
        elif payment_method_upper == "SPLIT" and payment_data.get('split'):
            split_data = payment_data.get('split', {})
            try:
                outstanding_amount = float(split_data.get('credit_amount', 0))
            except (ValueError, TypeError):
                outstanding_amount = 0

        # If payment is partially paid, try to get the pending amount
        payment_status_upper = payment_status.upper() if isinstance(payment_status, str) else str(payment_status).upper()
        if payment_status_upper in ["PARTIALLY_PAID", "PARTIAL"]:
            # Get sum of all payments made
            try:
                payment_made = sum([float(p.get('amount', 0)) for p in payment_data.get('payments', [])])
                outstanding_amount = total - payment_made
            except:
                # If error in calculation, leave as is
                pass

        # -------------------------------------------------------------
        # Create the EXACT shop_bill.pdf layout with proper tables and borders
        # -------------------------------------------------------------

        # ------ HEADER SECTION ------
        # Shop Name in its own bordered cell
        shop_name_table = Table(
            [[Paragraph(f"{shop_name}", styles['ShopName'])]],
            colWidths=[doc.width],
            rowHeights=[20]
        )
        shop_name_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        # Shop info row
        shop_info_data = [
            [
                Paragraph(f"{shop_address}", styles['ShopInfo']),
                Paragraph("(Original For Recipeint)", styles['OriginalCopy']),
                Paragraph(f"GSTIN -        {shop_gst}", styles['RightAligned'])
            ],
            [
                Paragraph(f"State Name: {state_name}, Code : {state_code}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LAID           {shop_laid_no}", styles['RightAligned'])
            ],
            [
                Paragraph(f"Contact : {shop_phone}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LCSD           {shop_lcsd_no}", styles['RightAligned'])
            ],
            [
                Paragraph(f"E-mail: {shop_email}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LFRD           {shop_lfrd_no}", styles['RightAligned'])
            ]
        ]

        shop_info_table = Table(shop_info_data, colWidths=[doc.width*0.4, doc.width*0.3, doc.width*0.3])
        shop_info_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('SPAN', (0, 0), (0, 0)), # Shop address spans
        ]))

        # ------ CUSTOMER SECTION ------
        # Create right-aligned style for invoice info
        styles.add(ParagraphStyle(name='InvoiceInfoRight',
                                 parent=styles['Normal'],
                                 fontName='Helvetica',
                                 fontSize=8,
                                 leading=10,
                                 alignment=2))  # Right alignment (TA_RIGHT)

        # Match the sample bill layout exactly as shown in the image
        customer_info_data = [
            [
                Paragraph(f"Customer name - {customer_name}", styles['CustomerInfo']),
                Paragraph(f"Contact - {customer_phone}", styles['CustomerInfo']),
                Paragraph("Date", styles['InvoiceLabel']),
                Paragraph(f"{invoice_date} {invoice_time.strip()}", styles['InvoiceInfoRight'])
            ],
            [
                Paragraph(f"Add : {customer_address}", styles['CustomerInfo']),
                Paragraph(f"Email - {customer_email}", styles['CustomerInfo']),
                Paragraph("Invoice No.", styles['InvoiceLabel']),
                Paragraph(f"{invoice_number}", styles['InvoiceInfoRight'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Mode of Pay", styles['InvoiceLabel']),
                Paragraph(f"{payment_method}", styles['InvoiceInfoRight'])
            ]
        ]

        # Equal columns for customer info, with right-most columns for invoice details
        customer_info_table = Table(customer_info_data, colWidths=[doc.width*0.3, doc.width*0.3, doc.width*0.15, doc.width*0.25])
        customer_info_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Right align all invoice values
        ]))

        # ------ ITEMS TABLE ------
        # Prepare column headers        
        items_header_data = [
            [Paragraph("No", styles['TableHeader']), 
             Paragraph("Description of Good", styles['TableHeader']), 
             Paragraph("Company\nname", styles['TableHeader']),
             Paragraph("HSN", styles['TableHeader']),
             Paragraph("Batch NO", styles['TableHeader']),
             Paragraph("Expiry Date", styles['TableHeader']),
             Paragraph("Qty", styles['TableHeader']),
             Paragraph("Unit", styles['TableHeader']),
             Paragraph("Rate", styles['TableHeader']),
             Paragraph("Disc", styles['TableHeader']),
             Paragraph("Amount", styles['TableHeader'])]
        ]

        # Calculate column widths for items table based on A4 landscape
        col_widths = [
            doc.width*0.03,   # No
            doc.width*0.20,   # Description
            doc.width*0.13,   # Company name
            doc.width*0.07,   # HSN
            doc.width*0.09,   # Batch
            doc.width*0.1,    # Expiry
            doc.width*0.04,   # Qty
            doc.width*0.05,   # Unit
            doc.width*0.09,   # Rate
            doc.width*0.06,   # Disc
            doc.width*0.14    # Amount
        ]

        # Create items header table
        items_header_table = Table(items_header_data, colWidths=col_widths)
        items_header_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))

        # Get items with proper schema mapping and aggregation
        items = []
        total_qty = 0
        formatted_items = []

        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            cursor = conn.cursor()

            # First, check what tables and columns we actually have
            print(f"DEBUG: Looking for items for invoice_id: '{invoice_id}' (type: {type(invoice_id)})")

            # If invoice_id is empty, try to get it from invoice_number
            if not invoice_id or invoice_id == '':
                print("DEBUG: invoice_id is empty, trying to find by invoice_number")
                if invoice_number:
                    # Try to find invoice_id from invoices table
                    cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", (invoice_number,))
                    result = cursor.fetchone()
                    if result:
                        invoice_id = result[0]
                        print(f"DEBUG: Found invoice_id {invoice_id} for invoice_number {invoice_number}")
                    else:
                        # Try to find from sales table
                        cursor.execute("SELECT id FROM sales WHERE invoice_number = ?", (invoice_number,))
                        result = cursor.fetchone()
                        if result:
                            invoice_id = result[0]
                            print(f"DEBUG: Found sale_id {invoice_id} for invoice_number {invoice_number}")

            # Debug: Check table schemas
            cursor.execute("PRAGMA table_info(invoice_items)")
            ii_schema = cursor.fetchall()
            print(f"DEBUG: invoice_items schema: {[col[1] for col in ii_schema]}")

            cursor.execute("PRAGMA table_info(sale_items)")
            si_schema = cursor.fetchall()
            print(f"DEBUG: sale_items schema: {[col[1] for col in si_schema]}")

            # Check if we should query invoice_items or sale_items
            invoice_items_count = 0
            sale_items_count = 0

            if invoice_id:
                # First try invoice_items table
                cursor.execute("SELECT COUNT(*) FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
                invoice_items_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM sale_items WHERE sale_id = ?", (invoice_id,))
                sale_items_count = cursor.fetchone()[0]

                # Also try cross-referencing through sales table if no direct items found
                if invoice_items_count == 0 and sale_items_count == 0:
                    # Try to find sale_id that corresponds to this invoice
                    cursor.execute("SELECT id FROM sales WHERE invoice_number = ?", (invoice_number,))
                    sale_result = cursor.fetchone()
                    if sale_result:
                        sale_id = sale_result[0]
                        print(f"DEBUG: Found sale_id {sale_id} for invoice_number {invoice_number}")
                        cursor.execute("SELECT COUNT(*) FROM sale_items WHERE sale_id = ?", (sale_id,))
                        sale_items_count = cursor.fetchone()[0]
                        if sale_items_count > 0:
                            # Update invoice_id to use sale_id for querying sale_items
                            print(f"DEBUG: Using sale_id {sale_id} instead of invoice_id {invoice_id} for item lookup")
                            invoice_id = sale_id

            print(f"DEBUG: Found {invoice_items_count} items in invoice_items, {sale_items_count} items in sale_items")

            # Debug: Show actual data in tables
            if invoice_items_count > 0:
                cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ? LIMIT 1", (invoice_id,))
                sample_ii = cursor.fetchone()
                print(f"DEBUG: Sample invoice_items data: {sample_ii}")

            if sale_items_count > 0:
                cursor.execute("SELECT * FROM sale_items WHERE sale_id = ? LIMIT 1", (invoice_id,))
                sample_si = cursor.fetchone()
                print(f"DEBUG: Sample sale_items data: {sample_si}")

            if invoice_items_count > 0:
                # Query from invoice_items table WITHOUT aggregation to preserve individual batch details
                # First check what columns exist in invoice_items
                try:
                    cursor.execute("PRAGMA table_info(invoice_items)")
                    invoice_items_cols = {col[1] for col in cursor.fetchall()}
                    print(f"DEBUG: Available invoice_items columns: {invoice_items_cols}")
                except Exception as e:
                    print(f"DEBUG: Error checking invoice_items schema: {e}")
                    invoice_items_cols = set()

                # Build HSN code selection based on available columns
                hsn_selection = ""
                if 'hsn_code' in invoice_items_cols:
                    hsn_selection = "COALESCE(ii.hsn_code, p.hsn_code, '') as hsn_code"
                else:
                    hsn_selection = "COALESCE(p.hsn_code, '') as hsn_code"

                query = f"""
                    SELECT 
                        COALESCE(p.name, 'Unknown Product') as product_name,
                        COALESCE(p.manufacturer, '') as company_name,
                        {hsn_selection},
                        COALESCE(ii.batch_number, '') as batch_number,
                        COALESCE(
                            (SELECT expiry_date FROM batches WHERE product_id = ii.product_id 
                             AND batch_number = ii.batch_number LIMIT 1),
                            ''
                        ) as expiry_date,
                        ii.quantity as quantity,
                        COALESCE(p.unit, 'pcs') as unit,
                        ii.price_per_unit as rate,
                        COALESCE(ii.discount_percentage, 0) as discount,
                        ii.total_price as amount,
                        ii.product_id
                    FROM invoice_items ii
                    LEFT JOIN products p ON ii.product_id = p.id
                    WHERE ii.invoice_id = ?
                    ORDER BY ii.id
                """
                print(f"DEBUG: Executing individual invoice_items query with invoice_id: {invoice_id}")
                cursor.execute(query, (invoice_id,))
                items = cursor.fetchall()
                print(f"DEBUG: Query returned {len(items)} individual items from invoice_items")

            elif sale_items_count > 0:
                # Query from sale_items table - each sale_item represents one actual transaction
                # Show exactly what was sold with correct batch information
                query = """
                    SELECT 
                        si.product_name,
                        COALESCE(p.manufacturer, '') as company_name,
                        COALESCE(si.hsn_code, p.hsn_code, '') as hsn_code,
                        COALESCE(si.batch_number, '') as batch_number,
                        COALESCE(si.expiry_date, '') as expiry_date,
                        si.quantity,
                        COALESCE(p.unit, 'pcs') as unit,
                        si.price as rate,
                        COALESCE(si.discount_percent, 0) as discount,
                        si.total as amount,
                        si.product_id
                    FROM sale_items si
                    LEFT JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                    ORDER BY si.id
                """
                print(f"DEBUG: Executing individual sale_items query with sale_id: {invoice_id}")
                cursor.execute(query, (invoice_id,))
                items = cursor.fetchall()
                print(f"DEBUG: Query returned {len(items)} individual items from sale_items")

                # Debug: Print the actual data for first item
                if items:
                    print(f"DEBUG: First sale_items row: {items[0]}")
                    print(f"DEBUG: Batch number from sale_items: '{items[0][3] if len(items[0]) > 3 else 'N/A'}'")
                    print(f"DEBUG: Expiry date from sale_items: '{items[0][4] if len(items[0]) > 4 else 'N/A'}')")

            # If still no items, try alternative approach
            if not items:
                print(f"DEBUG: No items found, trying alternative query approach")
                # Try getting items from the invoices data passed in
                items_from_data = invoice_data.get('items', [])
                if items_from_data:
                    print(f"DEBUG: Found {len(items_from_data)} items in invoice_data")
                    # Convert the passed items to the expected format and aggregate by product
                    product_aggregation = {}
                    for item_data in items_from_data:
                        product_key = (
                            item_data.get('product_id', 0),
                            item_data.get('name', 'Unknown Product'),
                            item_data.get('price', 0),
                            item_data.get('discount', 0),
                            item_data.get('batch_no', '')
                        )

                        if product_key in product_aggregation:
                            # Aggregate quantity and total
                            product_aggregation[product_key]['quantity'] += item_data.get('quantity', 0)
                            product_aggregation[product_key]['total'] += item_data.get('total', 0)
                        else:
                            product_aggregation[product_key] = {
                                'name': item_data.get('name', 'Unknown Product'),
                                'company': item_data.get('company', ''),
                                'hsn_code': item_data.get('hsn_code', ''),
                                'batch_no': item_data.get('batch_no', ''),
                                'expiry_date': item_data.get('expiry_date', ''),
                                'quantity': item_data.get('quantity', 0),
                                'unit': item_data.get('unit', ''),
                                'price': item_data.get('price', 0),
                                'discount': item_data.get('discount', 0),
                                'total': item_data.get('total', 0)
                            }

                    # Convert aggregated items back to list format
                    items = []
                    for product_key, aggregated_item in product_aggregation.items():
                        items.append((
                            aggregated_item['name'],
                            aggregated_item['company'],
                            aggregated_item['hsn_code'],
                            aggregated_item['batch_no'],
                            aggregated_item['expiry_date'],
                            aggregated_item['quantity'],
                            aggregated_item['unit'],
                            aggregated_item['price'],
                            aggregated_item['discount'],
                            aggregated_item['total']
                        ))
                else:
                    print("DEBUG: No items found in invoice_data either")
                    # If we still have no items but have an invoice_number, try one more approach
                    if invoice_number and not invoice_id:
                        print(f"DEBUG: Trying to find any sales data for invoice_number: {invoice_number}")
                        cursor.execute("""
                            SELECT 'Placeholder Item' as name, '' as company, '' as hsn, '' as batch, 
                                   '' as expiry, 1 as qty, 'pcs' as unit, 0 as price, 0 as discount, 0 as total
                        """)
                        placeholder_result = cursor.fetchone()
                        if placeholder_result:
                            items = [placeholder_result]

            print(f"DEBUG: Retrieved {len(items)} items for processing")
            if items:
                print(f"DEBUG: First item data: {items[0]}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error fetching invoice items: {e}")
            import traceback
            traceback.print_exc()

        # Format items with proper field mapping
        formatted_items = []
        items_subtotal = 0.0  # Calculate actual subtotal from items
        tax_total = 0.0
        total_qty = 0

        for i, item in enumerate(items):
            try:
                # Map fields from sale_items query results
                # sale_items fields: id, sale_id, product_id, product_name, hsn_code, batch_number, expiry_date, quantity, price, discount_percent, tax_percentage, tax_amount, total
                item_id = item[0]
                sale_id = item[1] 
                product_id = item[2]
                name = str(item[3]) if item[3] else "Unknown Product"
                hsn_code = str(item[4]) if item[4] else ""
                batch_no = str(item[5]) if item[5] else ""
                expiry_date = str(item[6]) if item[6] else ""
                quantity = float(item[7]) if item[7] is not None else 0
                price = float(item[8]) if item[8] is not None else 0  # This is the stored sale price
                discount = float(item[9]) if item[9] is not None else 0
                tax_percentage = float(item[10]) if item[10] is not None else 0
                tax_amount = float(item[11]) if item[11] is not None else 0
                item_total = float(item[12]) if item[12] is not None else 0

                # Get additional fields from the JOIN
                resolved_hsn_code = str(item[13]) if len(item) > 13 and item[13] else hsn_code
                manufacturer = str(item[14]) if len(item) > 14 and item[14] else ""
                unit = str(item[15]) if len(item) > 15 and item[15] else "pcs"

                # Use resolved HSN code
                hsn_code = resolved_hsn_code