"""
The code has been modified to fix duplicate item entries in invoices and to correctly fetch the customer's email address.
"""
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
        print(
            "Error: ReportLab library is not available. PDF invoice generation not possible."
        )
        return False

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # Create the PDF document in landscape orientation
        doc = SimpleDocTemplate(
            save_path,
            pagesize=landscape(A4),  # Use landscape orientation
            rightMargin=0.5 * cm,
            leftMargin=0.5 * cm,
            topMargin=0.5 * cm,
            bottomMargin=0.5 * cm)

        # Get styles
        styles = getSampleStyleSheet()

        # Create custom styles that match exactly the shop_bill.pdf template
        styles.add(
            ParagraphStyle(name='ShopName',
                           fontName='Helvetica-Bold',
                           fontSize=12,
                           alignment=TA_LEFT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='ShopInfo',
                           fontSize=9,
                           alignment=TA_LEFT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='StateName',
                           fontSize=8,
                           alignment=TA_LEFT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='CustomerInfo',
                           fontSize=9,
                           alignment=TA_LEFT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='OriginalCopy',
                           fontSize=9,
                           alignment=TA_CENTER,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='RightAligned',
                           fontSize=9,
                           alignment=TA_RIGHT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='InvoiceLabel',
                           fontSize=9,
                           alignment=TA_LEFT,
                           fontName='Helvetica-Bold',
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='InvoiceInfo',
                           fontSize=9,
                           alignment=TA_LEFT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='AmountWords',
                           fontSize=9,
                           alignment=TA_CENTER,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='ItemData',
                           fontSize=8,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='TableHeader',
                           fontSize=8,
                           fontName='Helvetica-Bold',
                           alignment=TA_CENTER,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='TableHeaderLeft',
                           fontSize=8,
                           fontName='Helvetica-Bold',
                           alignment=TA_LEFT,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='Terms',
                           fontSize=7,
                           alignment=TA_CENTER,
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='Subject',
                           fontSize=9,
                           alignment=TA_CENTER,
                           fontName='Helvetica-Bold',
                           spaceAfter=0,
                           spaceBefore=0))

        styles.add(
            ParagraphStyle(name='PaymentRecordsHeader',
                           fontSize=9,
                           alignment=TA_CENTER,
                           fontName='Helvetica-Bold',
                           spaceAfter=0,
                           spaceBefore=0))

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
                print(
                    f"  ID: {row['id']}, Key: {row['key']}, Value: {row['value']}"
                )

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

        # Format date
        date_obj = datetime.datetime.now()
        try:
            if 'date' in invoice_data:
                if isinstance(invoice_data['date'], str):
                    # Support multiple date formats
                    try:
                        date_obj = datetime.datetime.strptime(
                            invoice_data['date'], '%d/%m/%Y')
                    except ValueError:
                        try:
                            date_obj = datetime.datetime.strptime(
                                invoice_data['date'], '%d-%m-%Y')
                        except ValueError:
                            pass
        except:
            pass

        invoice_date = date_obj.strftime('%d/%m/%Y')
        invoice_time = invoice_data.get('time', date_obj.strftime('%I:%M %p'))

        # Customer information
        customer_name = customer_data.get('name', 'Walk-in Customer')
        customer_phone = customer_data.get('phone', '')
        customer_address = customer_data.get('address', '')
        customer_village = customer_data.get('village', '')
        if customer_village and not customer_village in customer_address:
            customer_address = f"{customer_address}, {customer_village}"
        customer_email = customer_data.get('email', '')
        customer_gstin = customer_data.get('gstin', '')

        # Payment information
        payment_data = invoice_data.get('payment', {})
        payment_method = payment_data.get('method', 'Cash')

        # Ensure payment_method is a string
        if not isinstance(payment_method, str):
            payment_method = str(
                payment_method) if payment_method is not None else 'Cash'

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
        payment_method_upper = payment_method.upper() if isinstance(
            payment_method, str) else str(payment_method).upper()

        if payment_method_upper == "CREDIT":
            outstanding_amount = total
        elif payment_method_upper == "SPLIT" and payment_data.get('split'):
            split_data = payment_data.get('split', {})
            try:
                outstanding_amount = float(split_data.get('credit_amount', 0))
            except (ValueError, TypeError):
                outstanding_amount = 0

        # If payment is partially paid, try to get the pending amount
        payment_status_upper = payment_status.upper() if isinstance(
            payment_status, str) else str(payment_status).upper()
        if payment_status_upper in ["PARTIALLY_PAID", "PARTIAL"]:
            # Get sum of all payments made
            try:
                payment_made = sum([
                    float(p.get('amount', 0))
                    for p in payment_data.get('payments', [])
                ])
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
            rowHeights=[20])
        shop_name_table.setStyle(
            TableStyle([
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
                Paragraph(f"State Name: {state_name}, Code : {state_code}",
                          styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LAID           {shop_laid_no}",
                          styles['RightAligned'])
            ],
            [
                Paragraph(f"Contact : {shop_phone}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LCSD           {shop_lcsd_no}",
                          styles['RightAligned'])
            ],
            [
                Paragraph(f"E-mail: {shop_email}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LFRD           {shop_lfrd_no}",
                          styles['RightAligned'])
            ]
        ]

        shop_info_table = Table(
            shop_info_data,
            colWidths=[doc.width * 0.4, doc.width * 0.3, doc.width * 0.3])
        shop_info_table.setStyle(
            TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('SPAN', (0, 0), (0, 0)),  # Shop address spans
            ]))

        # ------ CUSTOMER SECTION ------
        # Create right-aligned style for invoice info
        styles.add(
            ParagraphStyle(name='InvoiceInfoRight',
                           parent=styles['Normal'],
                           fontName='Helvetica',
                           fontSize=8,
                           leading=10,
                           alignment=2))  # Right alignment (TA_RIGHT)

        # Match the sample bill layout exactly as shown in the image
        customer_info_data = [[
            Paragraph(f"Customer name - {customer_name}",
                      styles['CustomerInfo']),
            Paragraph(f"Contact - {customer_phone}", styles['CustomerInfo']),
            Paragraph("Date", styles['InvoiceLabel']),
            Paragraph(f"{invoice_date}{invoice_time}",
                      styles['InvoiceInfoRight'])
        ],
                              [
                                  Paragraph(f"Add : {customer_address}",
                                            styles['CustomerInfo']),
                                  Paragraph(f"Email - {customer_email}",
                                            styles['CustomerInfo']),
                                  Paragraph("Invoice No.",
                                            styles['InvoiceLabel']),
                                  Paragraph(f"{invoice_number}",
                                            styles['InvoiceInfoRight'])
                              ],
                              [
                                  Paragraph("", styles['CustomerInfo']),
                                  Paragraph("", styles['CustomerInfo']),
                                  Paragraph("Mode of Pay",
                                            styles['InvoiceLabel']),
                                  Paragraph(f"{payment_method}",
                                            styles['InvoiceInfoRight'])
                              ]]

        # Equal columns for customer info, with right-most columns for invoice details
        customer_info_table = Table(customer_info_data,
                                    colWidths=[
                                        doc.width * 0.3, doc.width * 0.3,
                                        doc.width * 0.15, doc.width * 0.25
                                    ])
        customer_info_table.setStyle(
            TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1),
                 'RIGHT'),  # Right align all invoice values
            ]))

        # ------ ITEMS TABLE ------
        # Prepare column headers
        items_header_data = [[
            Paragraph("No", styles['TableHeader']),
            Paragraph("Description of Good", styles['TableHeader']),
            Paragraph("Company\nname", styles['TableHeader']),
            Paragraph("HSN", styles['TableHeader']),
            Paragraph("Batch NO", styles['TableHeader']),
            Paragraph("Expiry Date", styles['TableHeader']),
            Paragraph("Qty", styles['TableHeader']),
            Paragraph("Unit", styles['TableHeader']),
            Paragraph("Rate", styles['TableHeader']),
            Paragraph("Disc", styles['TableHeader']),
            Paragraph("Amount", styles['TableHeader'])
        ]]

        # Calculate column widths for items table based on A4 landscape
        col_widths = [
            doc.width * 0.03,  # No
            doc.width * 0.17,  # Description
            doc.width * 0.13,  # Company name
            doc.width * 0.07,  # HSN
            doc.width * 0.08,  # Batch
            doc.width * 0.1,  # Expiry
            doc.width * 0.06,  # Qty
            doc.width * 0.07,  # Unit
            doc.width * 0.09,  # Rate
            doc.width * 0.08,  # Disc
            doc.width * 0.12  # Amount
        ]

        # Create items header table
        items_header_table = Table(items_header_data, colWidths=col_widths)
        items_header_table.setStyle(
            TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))

        # Get items with proper schema mapping
        items = []
        total_qty = 0
        formatted_items = []

        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            cursor = conn.cursor()

            # First, check what tables and columns we actually have
            print(
                f"DEBUG: Looking for items for invoice_id: '{invoice_id}' (type: {type(invoice_id)})"
            )

            # If invoice_id is empty, try to get it from invoice_number
            if not invoice_id or invoice_id == '':
                print(
                    "DEBUG: invoice_id is empty, trying to find by invoice_number"
                )
                if invoice_number:
                    # Try to find invoice_id from invoices table
                    cursor.execute(
                        "SELECT id FROM invoices WHERE invoice_number = ?",
                        (invoice_number, ))
                    result = cursor.fetchone()
                    if result:
                        invoice_id = result[0]
                        print(
                            f"DEBUG: Found invoice_id {invoice_id} for invoice_number {invoice_number}"
                        )
                    else:
                        # Try to find from sales table
                        cursor.execute(
                            "SELECT id FROM sales WHERE invoice_number = ?",
                            (invoice_number, ))
                    result = cursor.fetchone()
                    if result:
                        invoice_id = result[0]
                        print(
                            f"DEBUG: Found sale_id {invoice_id} for invoice_number {invoice_number}"
                        )

            # Debug: Check table schemas
            cursor.execute("PRAGMA table_info(invoice_items)")
            ii_schema = cursor.fetchall()
            print(
                f"DEBUG: invoice_items schema: {[col[1] for col in ii_schema]}"
            )

            cursor.execute("PRAGMA table_info(sale_items)")
            si_schema = cursor.fetchall()
            print(f"DEBUG: sale_items schema: {[col[1] for col in si_schema]}")

            # Check if we should query invoice_items or sale_items
            invoice_items_count = 0
            sale_items_count = 0

            if invoice_id:
                # First try invoice_items table
                cursor.execute(
                    "SELECT COUNT(*) FROM invoice_items WHERE invoice_id = ?",
                    (invoice_id, ))
                invoice_items_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM sale_items WHERE sale_id = ?",
                    (invoice_id, ))
                sale_items_count = cursor.fetchone()[0]

                # Also try cross-referencing through sales table if no direct items found
                if invoice_items_count == 0 and sale_items_count == 0:
                    # Try to find sale_id that corresponds to this invoice
                    cursor.execute(
                        "SELECT id FROM sales WHERE invoice_number = ?",
                        (invoice_number, ))
                    sale_result = cursor.fetchone()
                    if sale_result:
                        sale_id = sale_result[0]
                        print(
                            f"DEBUG: Found sale_id {sale_id} for invoice_number {invoice_number}"
                        )
                        cursor.execute(
                            "SELECT COUNT(*) FROM sale_items WHERE sale_id = ?",
                            (sale_id, ))
                        sale_items_count = cursor.fetchone()[0]
                        if sale_items_count > 0:
                            # Update invoice_id to use sale_id for querying sale_items
                            print(
                                f"DEBUG: Using sale_id {sale_id} instead of invoice_id {invoice_id} for item lookup"
                            )
                            invoice_id = sale_id

            print(
                f"DEBUG: Found {invoice_items_count} items in invoice_items, {sale_items_count} items in sale_items"
            )

            # Debug: Show actual data in tables
            if invoice_items_count > 0:
                cursor.execute(
                    "SELECT * FROM invoice_items WHERE invoice_id = ? LIMIT 1",
                    (invoice_id, ))
                sample_ii = cursor.fetchone()
                print(f"DEBUG: Sample invoice_items data: {sample_ii}")

            if sale_items_count > 0:
                cursor.execute(
                    "SELECT * FROM sale_items WHERE sale_id = ? LIMIT 1",
                    (invoice_id, ))
                sample_si = cursor.fetchone()
                print(f"DEBUG: Sample sale_items data: {sample_si}")

            if invoice_items_count > 0:
                # Query from invoice_items table
                query = """
                    SELECT 
                        COALESCE(p.name, 'Unknown Product') as product_name,
                        COALESCE(p.manufacturer, '') as company_name,
                        COALESCE(ii.hsn_code, p.hsn_code, '') as hsn_code,
                        COALESCE(ii.batch_number, 
                            (SELECT batch_number FROM batches WHERE product_id = ii.product_id 
                             ORDER BY expiry_date ASC LIMIT 1), 
                            '') as batch_number,
                        COALESCE((SELECT expiry_date FROM batches WHERE product_id = ii.product_id 
                                 ORDER BY expiry_date ASC LIMIT 1), 
                            ''
                        ) as expiry_date,
                        ii.quantity,
                        COALESCE(p.unit, 'pcs') as unit,
                        ii.price_per_unit as rate,
                        COALESCE(ii.discount_percentage, 0) as discount,
                        ii.total_price as amount
                    FROM invoice_items ii
                    LEFT JOIN products p ON ii.product_id = p.id
                    WHERE ii.invoice_id = ?
                    ORDER BY ii.id
                """
                print(f"DEBUG: Executing invoice_items query with invoice_id: {invoice_id}")
                cursor.execute(query, (invoice_id,))
                items = cursor.fetchall()
                print(f"DEBUG: Query returned {len(items)} items from invoice_items")

            elif sale_items_count > 0:
                # Query from sale_items table without JOIN to batches to avoid duplicates
                query = """
                    SELECT 
                        si.product_name,
                        COALESCE(p.manufacturer, '') as company_name,
                        COALESCE(si.hsn_code, '') as hsn_code,
                        COALESCE((SELECT batch_number FROM batches WHERE product_id = si.product_id 
                                 ORDER BY expiry_date ASC LIMIT 1), '') as batch_number,
                        COALESCE((SELECT expiry_date FROM batches WHERE product_id = si.product_id 
                                 ORDER BY expiry_date ASC LIMIT 1), '') as expiry_date,
                        si.quantity,
                        COALESCE(p.unit, 'pcs') as unit,
                        si.price as rate,
                        COALESCE(si.discount_percent, 0) as discount,
                        si.total as amount
                    FROM sale_items si
                    LEFT JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                    ORDER BY si.id
                """
                print(f"DEBUG: Executing sale_items query with sale_id: {invoice_id}")
                cursor.execute(query, (invoice_id,))
                items = cursor.fetchall()
                print(f"DEBUG: Query returned {len(items)} items from sale_items")

            # If still no items, try alternative approach
            if not items:
                print(
                    f"DEBUG: No items found, trying alternative query approach"
                )
                # Try getting items from the invoices data passed in
                items_from_data = invoice_data.get('items', [])
                if items_from_data:
                    print(
                        f"DEBUG: Found {len(items_from_data)} items in invoice_data"
                    )
                    # Convert the passed items to the expected format
                    items = []
                    for item_data in items_from_data:
                        items.append(
                            (item_data.get('name', 'Unknown Product'),
                             item_data.get('company',
                                           ''), item_data.get('hsn_code', ''),
                             item_data.get('batch_no', ''),
                             item_data.get('expiry_date',
                                           ''), item_data.get('quantity', 0),
                             item_data.get('unit',
                                           ''), item_data.get('price', 0),
                             item_data.get('discount',
                                           0), item_data.get('total', 0)))
                else:
                    print("DEBUG: No items found in invoice_data either")
                    # If we still have no items but have an invoice_number, try one more approach
                    if invoice_number and not invoice_id:
                        print(
                            f"DEBUG: Trying to find any sales data for invoice_number: {invoice_number}"
                        )
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
                # Map fields from query results with better error handling
                name = str(item[0]) if item[0] else "Unknown Product"
                company = str(item[1]) if item[1] else ""
                hsn_code = str(item[2]) if item[2] else ""
                batch_no = str(item[3]) if item[3] else ""

                # Handle expiry date formatting
                expiry_date = ""
                if item[4]:
                    expiry_str = str(item[4])
                    # Extract just the date part if it's a datetime
                    if ' ' in expiry_str:
                        expiry_date = expiry_str.split()[0]
                    else:
                        expiry_date = expiry_str

                quantity = float(item[5]) if item[5] is not None else 0
                unit = str(item[6]) if item[6] else "pcs"
                price = float(item[7]) if item[7] is not None else 0
                discount = float(item[8]) if item[8] is not None else 0
                item_total = float(item[9]) if item[9] is not None else 0

                # Add to totals
                total_qty += quantity
                items_subtotal += item_total  # Use actual item total for subtotal calculation

                # Format quantity and discount for display
                qty_str = str(int(quantity)) if quantity == int(
                    quantity) else str(quantity)
                discount_str = ""
                if discount > 0:
                    discount_str = f"{int(discount)}" if discount == int(
                        discount) else f"{discount:.1f}"
                    discount_str += "%"

                formatted_items.append({
                    'name': name,
                    'company': company,
                    'hsn_code': hsn_code,
                    'batch_no': batch_no,
                    'expiry_date': expiry_date,
                    'quantity': qty_str,
                    'unit': unit,
                    'price': price,
                    'discount': discount_str,
                    'total': item_total
                })

                print(
                    f"DEBUG: Processed item {i+1}: {name}, Batch: {batch_no}, Qty: {qty_str}, Price: {price}, Total: {item_total}"
                )

            except Exception as e:
                print(f"Error processing item {i}: {str(e)}")
                # Add a placeholder item to avoid completely empty table
                formatted_items.append({
                    'name': f"Item {i+1} (Error)",
                    'company': "",
                    'hsn_code': "",
                    'batch_no': "",
                    'expiry_date': "",
                    'quantity': "0",
                    'unit': "pcs",
                    'price': 0,
                    'discount': "",
                    'total': 0
                })
                continue

        # Use calculated subtotal from items instead of payment data
        subtotal = items_subtotal

        items_data = []

        # Always ensure we have some items to display
        if not formatted_items:
            print("WARNING: No formatted items found, creating placeholder")
            # Create at least one placeholder item
            formatted_items = [{
                'name': 'No items found',
                'company': '',
                'hsn_code': '',
                'batch_no': '',
                'expiry_date': '',
                'quantity': '0',
                'unit': '',
                'price': 0,
                'discount': '',
                'total': 0
            }]

        for i, item in enumerate(formatted_items, 1):
            # Ensure all values are properly formatted
            row_data = [
                str(i),  # Serial number
                str(item.get(
                    'name',
                    'Unknown Product'))[:30],  # Product name (truncated)
                str(item.get('company', ''))[:15],  # Company name (truncated)
                str(item.get('hsn_code', '')),  # HSN code
                str(item.get('batch_no', '')),  # Batch number
                str(item.get('expiry_date', '')),  # Expiry date
                str(item.get('quantity', '0')),  # Quantity
                str(item.get('unit', '')),  # Unit
                format_currency(```python
item.get('price', 0), symbol='Rs.'),  # Rate
                str(item.get('discount', '')),  # Discount
                format_currency(item.get('total', 0), symbol='Rs.')  # Amount
            ]
            items_data.append(row_data)

        print(f"DEBUG: Created {len(items_data)} rows for items table")
        if items_data:
            print(f"DEBUG: First row data: {items_data[0]}")

        # Fill empty rows to maintain table height
        min_rows = 6  # Minimum rows to show
        while len(items_data) < min_rows:
            empty_row = ["", "", "", "", "", "", "", "", "", "", ""]
            items_data.append(empty_row)

        # Create items table
        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(
            TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No column center
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Description left
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),  # Company left
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # HSN center
                ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Batch center
                ('ALIGN', (5, 0), (5, -1), 'CENTER'),  # Expiry center
                ('ALIGN', (6, 0), (6, -1), 'CENTER'),  # Qty center
                ('ALIGN', (7, 0), (7, -1), 'CENTER'),  # Unit center
                ('ALIGN', (8, 0), (8, -1), 'RIGHT'),  # Rate right
                ('ALIGN', (9, 0), (9, -1), 'CENTER'),  # Disc center
                ('ALIGN', (10, 0), (10, -1), 'RIGHT'),  # Amount right
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

        # ------ FINANCIAL SUMMARY TABLE ------
        # Create financial summary that matches the template layout exactly

        # Calculate total amount directly from formatted_items
        total_amount = sum(item.get('total', 0) for item in formatted_items)

        # If we have payment data, use those values instead
        if payment_data:
            if 'total' in payment_data:
                total_amount = float(payment_data.get('total', total_amount))
            if 'subtotal' in payment_data:
                subtotal = float(payment_data.get('subtotal', subtotal))

        # Calculate tax amounts based on subtotal and tax rates
        if cgst == 0 and sgst == 0:
            # If tax amounts are not provided, calculate based on taxable value and tax rates
            cgst = (taxable_value * cgst_rate / 100) if cgst_rate > 0 else 0
            sgst = (taxable_value * sgst_rate / 100) if sgst_rate > 0 else 0

        # Create amounts in words 
        try:
            amount_words = num_to_words_indian(total_amount)
        except:
            amount_words = "Amount calculation error"

        # Financial summary data with proper formatting
        financial_data = [
            [
                Paragraph(f"Total Qty : {int(total_qty)}", styles['CustomerInfo']),
                Paragraph("Amount", styles['InvoiceLabel']),
                Paragraph(format_currency(subtotal, symbol='Rs.'), styles['RightAligned'])
            ],
            [
                Paragraph(f"Amount Chargeable (in words) <br/><b>{amount_words}</b>", styles['AmountWords']),
                Paragraph("Discount", styles['InvoiceLabel']),
                Paragraph(format_currency(discount, symbol='Rs.'), styles['RightAligned'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Taxable Value", styles['InvoiceLabel']),
                Paragraph(format_currency(taxable_value, symbol='Rs.'), styles['RightAligned'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph(f"Central Tax (CGST) @ {cgst_rate}%", styles['InvoiceLabel']),
                Paragraph(format_currency(cgst, symbol='Rs.'), styles['RightAligned'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph(f"State Tax (SGST) @ {sgst_rate}%", styles['InvoiceLabel']),
                Paragraph(format_currency(sgst, symbol='Rs.'), styles['RightAligned'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Total Tax Amount", styles['InvoiceLabel']),
                Paragraph(format_currency(cgst + sgst, symbol='Rs.'), styles['RightAligned'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Total Amount", styles['InvoiceLabel']),
                Paragraph(format_currency(total_amount, symbol='Rs.'), styles['RightAligned'])
            ]
        ]

        # If there's outstanding amount, add it to the summary
        if outstanding_amount > 0:
            financial_data.append([
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Outstanding Amount", styles['InvoiceLabel']),
                Paragraph(format_currency(outstanding_amount, symbol='Rs.'), styles['RightAligned'])
            ])

        financial_table = Table(financial_data, colWidths=[
            doc.width * 0.5,  # Amount in words section (left)
            doc.width * 0.25,  # Labels (center)
            doc.width * 0.25   # Values (right)
        ])
        financial_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),    # Amount in words left
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Labels left
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Values right
            ('SPAN', (0, 1), (0, 1)),  # Span amount in words cell
        ]))

        # ------ TERMS AND CONDITIONS SECTION ------
        terms_data = [[
            Paragraph(
                "Terms and Conditions:<br/>"
                "1. Goods once sold will not be taken back<br/>"
                "2. Interest @ 18% p.a. will be charged if the payment is not received within 30 days<br/>"
                "3. Subject to Maharashtra Jurisdiction only", 
                styles['Terms']
            )
        ]]

        terms_table = Table(terms_data, colWidths=[doc.width])
        terms_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))

        # ------ SIGNATURE SECTION ------
        signature_data = [[
            Paragraph("Customer's Signature", styles['Terms']),
            Paragraph(f"for {shop_name}<br/>Authorised Signatory", styles['Terms'])
        ]]

        signature_table = Table(signature_data, colWidths=[doc.width*0.5, doc.width*0.5])
        signature_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),  # Add some space for actual signatures
        ]))

        # Assemble all elements
        elements.append(shop_name_table)
        elements.append(shop_info_table)
        elements.append(customer_info_table)
        elements.append(items_header_table)
        elements.append(items_table)
        elements.append(financial_table)
        elements.append(terms_table)
        elements.append(signature_table)

        # Build the PDF
        doc.build(elements)

        return True

    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        return False