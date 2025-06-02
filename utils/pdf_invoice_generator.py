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

        # Format date
        date_obj = datetime.datetime.now()
        try:
            if 'date' in invoice_data:
                if isinstance(invoice_data['date'], str):
                    # Support multiple date formats
                    try:
                        date_obj = datetime.datetime.strptime(invoice_data['date'], '%d/%m/%Y')
                    except ValueError:
                        try:
                            date_obj = datetime.datetime.strptime(invoice_data['date'], '%d-%m-%Y')
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
        if payment_method.upper() == "CREDIT":
            outstanding_amount = total
        elif payment_method.upper() == "SPLIT" and payment_data.get('split'):
            split_data = payment_data.get('split', {})
            try:
                outstanding_amount = float(split_data.get('credit_amount', 0))
            except (ValueError, TypeError):
                outstanding_amount = 0

        # If payment is partially paid, try to get the pending amount
        if payment_status.upper() in ["PARTIALLY_PAID", "PARTIAL"]:
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
                Paragraph(f"{invoice_date}{invoice_time}", styles['InvoiceInfoRight'])
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
            doc.width*0.17,   # Description
            doc.width*0.13,   # Company name
            doc.width*0.07,   # HSN
            doc.width*0.08,   # Batch
            doc.width*0.1,    # Expiry
            doc.width*0.06,   # Qty
            doc.width*0.07,   # Unit
            doc.width*0.09,   # Rate
            doc.width*0.08,   # Disc
            doc.width*0.12    # Amount
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

        # Get items with proper schema mapping
        items = []
        total_qty = 0
        formatted_items = []

        try:
            import sqlite3
            conn = sqlite3.connect('./pos_data.db')
            cursor = conn.cursor()

            # First, check what tables and columns we actually have
            print(f"DEBUG: Looking for items for invoice_id: {invoice_id}")

            # Debug: Check table schemas
            cursor.execute("PRAGMA table_info(invoice_items)")
            ii_schema = cursor.fetchall()
            print(f"DEBUG: invoice_items schema: {[col[1] for col in ii_schema]}")
            
            cursor.execute("PRAGMA table_info(sale_items)")
            si_schema = cursor.fetchall()
            print(f"DEBUG: sale_items schema: {[col[1] for col in si_schema]}")

            # Check if we should query invoice_items or sale_items
            # First try invoice_items table
            cursor.execute("SELECT COUNT(*) FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            invoice_items_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sale_items WHERE sale_id = ?", (invoice_id,))
            sale_items_count = cursor.fetchone()[0]
            
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
                # Query from invoice_items table
                cursor.execute("""
                    SELECT 
                        COALESCE(p.name, 'Unknown Product') as product_name,
                        COALESCE(p.manufacturer, '') as company_name,
                        COALESCE(ii.hsn_code, p.hsn_code, '') as hsn_code,
                        COALESCE(ii.batch_number, '') as batch_number,
                        COALESCE(
                            (SELECT expiry_date FROM batches WHERE product_id = ii.product_id 
                             AND (batch_number = ii.batch_number OR ii.batch_number IS NULL) 
                             ORDER BY expiry_date DESC LIMIT 1), 
                            ''
                        ) as expiry_date,
                        ii.quantity,
                        COALESCE(p.unit, '') as unit,
                        ii.price_per_unit as rate,
                        COALESCE(ii.discount_percentage, 0) as discount,
                        ii.total_price as amount
                    FROM invoice_items ii
                    LEFT JOIN products p ON ii.product_id = p.id
                    WHERE ii.invoice_id = ?
                    ORDER BY ii.id
                """, (invoice_id,))
                items = cursor.fetchall()
                
            elif sale_items_count > 0:
                # Query from sale_items table
                cursor.execute("""
                    SELECT 
                        si.product_name,
                        COALESCE(p.manufacturer, '') as company_name,
                        COALESCE(si.hsn_code, '') as hsn_code,
                        '' as batch_number,
                        COALESCE(
                            (SELECT expiry_date FROM batches WHERE product_id = si.product_id 
                             ORDER BY expiry_date DESC LIMIT 1), 
                            ''
                        ) as expiry_date,
                        si.quantity,
                        COALESCE(p.unit, '') as unit,
                        si.price as rate,
                        COALESCE(si.discount_percent, 0) as discount,
                        si.total as amount
                    FROM sale_items si
                    LEFT JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                    ORDER BY si.id
                """, (invoice_id,))
                items = cursor.fetchall()
            
            # If still no items, try alternative approach
            if not items:
                print(f"DEBUG: No items found, trying alternative query approach")
                # Try getting items from the invoices data passed in
                items_from_data = invoice_data.get('items', [])
                if items_from_data:
                    # Convert the passed items to the expected format
                    items = []
                    for item_data in items_from_data:
                        items.append((
                            item_data.get('name', 'Unknown Product'),
                            item_data.get('company', ''),
                            item_data.get('hsn_code', ''),
                            item_data.get('batch_no', ''),
                            item_data.get('expiry_date', ''),
                            item_data.get('quantity', 0),
                            item_data.get('unit', ''),
                            item_data.get('price', 0),
                            item_data.get('discount', 0),
                            item_data.get('total', 0)
                        ))

            print(f"DEBUG: Retrieved {len(items)} items for processing")
            if items:
                print(f"DEBUG: First item data: {items[0]}")

        except Exception as e:
            print(f"Error fetching invoice items: {e}")
            import traceback
            traceback.print_exc()

        # Format items with proper field mapping
        formatted_items = []
        subtotal = 0.0
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
                unit = str(item[6]) if item[6] else ""
                price = float(item[7]) if item[7] is not None else 0
                discount = float(item[8]) if item[8] is not None else 0
                total = float(item[9]) if item[9] is not None else 0

                # Add to total quantity
                total_qty += quantity

                # Format quantity and discount for display
                qty_str = str(int(quantity)) if quantity == int(quantity) else str(quantity)
                discount_str = ""
                if discount > 0:
                    discount_str = f"{int(discount)}" if discount == int(discount) else f"{discount:.1f}"
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
                    'total': total
                })

                print(f"DEBUG: Processed item {i+1}: {name}, Qty: {qty_str}, Price: {price}, Total: {total}")

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
                    'unit': "",
                    'price': 0,
                    'discount': "",
                    'total': 0
                })
                continue


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
                str(i),                                                    # Serial number
                str(item.get('name', 'Unknown Product'))[:30],            # Product name (truncated)
                str(item.get('company', ''))[:15],                        # Company name (truncated)
                str(item.get('hsn_code', '')),                            # HSN code
                str(item.get('batch_no', '')),                            # Batch number
                str(item.get('expiry_date', '')),                         # Expiry date
                str(item.get('quantity', '0')),                           # Quantity
                str(item.get('unit', '')),                                # Unit
                format_currency(item.get('price', 0), symbol='Rs.'),     # Rate
                str(item.get('discount', '')),                            # Discount
                format_currency(item.get('total', 0), symbol='Rs.')      # Amount
            ]
            items_data.append(row_data)
            
        print(f"DEBUG: Created {len(items_data)} rows for items table")
        if items_data:
            print(f"DEBUG: First row data: {items_data[0]}")

        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No column centered
            ('ALIGN', (6, 0), (7, -1), 'CENTER'),  # Qty and Unit columns centered
            ('ALIGN', (8, 0), (8, -1), 'RIGHT'),   # Rate column right aligned
            ('ALIGN', (9, 0), (9, -1), 'CENTER'),  # Disc column centered
            ('ALIGN', (10, 0), (10, -1), 'RIGHT'), # Amount column right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        # Total row
        try:
            qty_display = str(int(total_qty)) if total_qty == int(total_qty) else str(total_qty)
            total_formatted = format_currency(total, symbol='Rs.')
        except (ValueError, TypeError):
            qty_display = "0"
            total_formatted = "Rs. 0.00"
            print("Error formatting total values - using defaults")

        total_row_data = [
            ["", "", "", "", "", "", qty_display, "", "", "Total", total_formatted]
        ]

        total_row_table = Table(total_row_data, colWidths=col_widths)
        total_row_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (6, 0), (6, 0), 'CENTER'),  # total qty centered
            ('ALIGN', (9, 0), (9, 0), 'RIGHT'),   # "Total" right aligned
            ('ALIGN', (10, 0), (10, 0), 'RIGHT'), # Amount right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (9, 0), (10, 0), 'Helvetica-Bold'),  # "Total" and amount in bold
        ]))

        # Amount in words row
        try:
            total_for_words = float(total)
            amount_in_words = num_to_words_indian(total_for_words)
        except (ValueError, TypeError):
            amount_in_words = "Zero Rupees Only"

        amount_words_data = [
            [Paragraph(f"{amount_in_words.upper()}", styles['AmountWords'])]
        ]

        amount_words_table = Table(amount_words_data, colWidths=[doc.width])
        amount_words_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))

        # ------ TAX AND PAYMENT DETAILS SECTION ------
        # Create tax table that exactly matches the format shown in the reference image
        # This table has: Taxable Value | Central Tax (CGST) [Rate|Amount] | State Tax (SGST) [Rate|Amount] | Total Tax Amount

        # Define paragraphs with explicit style to ensure proper formatting and consistent labels
        taxable_para = Paragraph("Taxable\nValue", styles['TableHeader'])
        cgst_para = Paragraph("Central Tax (CGST)", styles['TableHeader'])
        sgst_para = Paragraph("State Tax (SGST)", styles['TableHeader'])  # Explicitly labeled as State Tax per requirement
        total_tax_para = Paragraph("Total\nTax Amount", styles['TableHeader'])

        rate_para = Paragraph("Rate", styles['TableHeader'])
        amount_para = Paragraph("Amount", styles['TableHeader'])

        # Create the tax table header as paragraphs with explicit styling
        tax_table_header = [
            [taxable_para, cgst_para, sgst_para, total_tax_para],
            ["", rate_para, amount_para, rate_para, amount_para, ""]
        ]

        # Calculate SGST (same as CGST for simplicity)
        sgst_rate = cgst_rate
        sgst = cgst

        tax_table_data = [
            [format_currency(taxable_value, symbol='Rs.'), 
             f"{cgst_rate}%", 
             format_currency(cgst, symbol='Rs.'),
             f"{sgst_rate}%",
             format_currency(sgst, symbol='Rs.'),
             format_currency(cgst + sgst, symbol='Rs.')],
            ["", "", format_currency(cgst, symbol='Rs.'), "", format_currency(sgst, symbol='Rs.'), format_currency(cgst + sgst, symbol='Rs.')]
        ]

        # Define column widths to match the template exactly
        tax_col_widths = [
            doc.width*0.25,      # Taxable value
            doc.width*0.10,      # CGST rate
            doc.width*0.15,      # CGST amount
            doc.width*0.10,      # SGST rate
            doc.width*0.15,      # SGST amount
            doc.width*0.25       # Total tax
        ]

        # Combine header and data
        tax_table_content = tax_table_header + tax_table_data

        # Create tax table with style exactly matching the sample image
        tax_table = Table(tax_table_content, colWidths=tax_col_widths)
        tax_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (0, 1)),    # Taxable Value header spans 2 rows
            ('SPAN', (1, 0), (2, 0)),    # Central Tax header spans 2 columns
            ('SPAN', (3, 0), (4, 0)),    # State Tax header spans 2 columns
            ('SPAN', (5, 0), (5, 1)),    # Total Tax Amount header spans 2 rows
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Headers centered
            ('ALIGN', (0, 2), (0, 3), 'RIGHT'),    # Taxable value right aligned
            ('ALIGN', (1, 2), (1, 3), 'CENTER'),   # CGST rate centered
            ('ALIGN', (2, 2), (2, 3), 'RIGHT'),    # CGST amount right aligned
            ('ALIGN', (3, 2), (3, 3), 'CENTER'),   # SGST rate centered
            ('ALIGN', (4, 2), (4, 3), 'RIGHT'),    # SGST amount right aligned
            ('ALIGN', (5, 2), (5, 3), 'RIGHT'),    # Total tax right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),  # Headers in bold
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        # Create the payment breakdown section (left side)
        payment_section_data = [
            [Paragraph("Payment Breakdown", styles['TableHeaderLeft']), ""],
            [Paragraph("Outstanding Amnt.", styles['TableHeaderLeft']), Paragraph(format_currency(outstanding_amount, symbol='Rs.'), styles['RightAligned'])]
        ]

        payment_section_table = Table(payment_section_data, colWidths=[doc.width*0.25*0.6, doc.width*0.25*0.4])
        payment_section_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Line below Payment Breakdown
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, 1), 'RIGHT'),  # Outstanding amount right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        # Combine payment and tax sections in a row
        payment_tax_data = [
            [payment_section_table, tax_table]
        ]

        payment_tax_row = Table(payment_tax_data, colWidths=[doc.width*0.25, doc.width*0.75])
        payment_tax_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        # ------ SIGNATURE SECTION ------
        # Create terms and signature section
        terms = invoice_data.get('terms', "1. Goods once sold will not be taken back or exchanged.\n2. All disputes are subject to local jurisdiction only.")

        signature_data = [
            [Paragraph("Customer Signature", styles['CustomerInfo']), 
             Paragraph(terms, styles['Terms']), 
             Paragraph(f"For                 {shop_name}", styles['RightAligned'])],
            ["", "", Paragraph("Authorised signatory", styles['RightAligned'])]
        ]

        signature_table = Table(signature_data, colWidths=[doc.width*0.25, doc.width*0.5, doc.width*0.25])
        signature_table.setStyle(TableStyle([
('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('SPAN', (1, 0), (1, 1)),  # Terms spans both rows
        ]))

        # Subject line
        subject_data = [
            [Paragraph("SUBJECT TO JURIDICTION", styles['Subject'])]
        ]

        subject_table = Table(subject_data, colWidths=[doc.width])
        subject_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))

        # ------ PAYMENT HISTORY SECTION ------
        # Add payment history section if available
        payment_history_tables = []

        if 'payment_history' in payment_data or 'payments' in payment_data:
            payment_history_header = [
                [Paragraph("Invoice payment Records", styles['PaymentRecordsHeader'])]
            ]

            payment_header_table = Table(payment_history_header, colWidths=[doc.width])
            payment_header_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ]))

            payment_history_tables.append(payment_header_table)

            # Payment records column headers
            payment_record_headers = [
                ["Sr.no", "Invoice No", "Amount", "Depositor Name", "Date", "time", "Mode of Pay", "Remaining Amount", "Note", "Invoice Status"]
            ]

            payment_col_widths = [
                doc.width*0.05,   # Sr.no
                doc.width*0.1,    # Invoice No
                doc.width*0.1,    # Amount
                doc.width*0.15,   # Depositor Name
                doc.width*0.1,    # Date
                doc.width*0.07,   # time
                doc.width*0.1,    # Mode of Pay
                doc.width*0.13,   # Remaining Amount
                doc.width*0.1,    # Note
                doc.width*0.1     # Invoice Status
            ]

            payment_headers_table = Table(payment_record_headers, colWidths=payment_col_widths)
            payment_headers_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))

            payment_history_tables.append(payment_headers_table)

            # Extract payments data
            payments = payment_data.get('payments', [])

            # If no payments list but has payment_history string, try to parse it
            if not payments and 'payment_history' in payment_data:
                # This is a simplified parser assuming format: "1. date: amount via method"
                history_text = payment_data['payment_history']
                history_lines = [line.strip() for line in history_text.split('\n') if line.strip()]

                # Skip first line if it's just "Payment History:"
                start_idx = 1 if history_lines and history_lines[0].lower() == 'payment history:' else 0

                for i, line in enumerate(history_lines[start_idx:], 1):
                    # Try to extract payment details from each line
                    try:
                        # Extract parts after the line number
                        parts = line.split('. ', 1)[1] if '. ' in line else line

                        # Split into date and amount parts
                        date_part, amount_part = parts.split(': ', 1) if ': ' in parts else (date_obj.strftime('%d/%m/%Y'), parts)

                        # Extract amount and method
                        amount = "0.0"
                        method = "Unknown"
                        if ' via ' in amount_part:
                            amount_str, method = amount_part.split(' via ', 1)
                            # Clean up the amount string, removing "Rs. " and any commas
                            amount = amount_str.replace('Rs. ', '').replace(',', '')

                            # Remove any reference part
                            if ' (Ref: ' in method:
                                reference = method.split(' (Ref: ')[1].rstrip(')')
                                method = method.split(' (Ref: ')[0]

                                # Add to payments list
                                payments.append({
                                    'date': date_part,
                                    'amount': amount,
                                    'method': method,
                                    'reference': reference,
                                    'depositor': 'Customer'  # Default depositor
                                })
                            else:
                                # Add to payments list without reference
                                payments.append({
                                    'date': date_part,
                                    'amount': amount,
                                    'method': method,
                                    'depositor': 'Customer'  # Default depositor
                                })
                    except:
                        # Skip unparseable lines
                        continue

            # Format payment rows - each payment gets a row
            payment_rows = []
            remaining = total

            for i, payment in enumerate(payments, 1):
                # Get payment details with safe defaults
                try:
                    payment_amount = float(payment.get('amount', 0))
                except (ValueError, TypeError):
                    payment_amount = 0.0

                payment_date = payment.get('date', '')
                payment_time = payment.get('time', '')
                payment_method = payment.get('method', '')
                payment_depositor = payment.get('depositor', 'Customer')
                payment_note = payment.get('note', '')

                # Calculate remaining amount if not provided
                if 'remaining' in payment:
                    try:
                        remaining = float(payment.get('remaining', 0))
                    except (ValueError, TypeError):
                        remaining -= payment_amount
                else:
                    remaining -= payment_amount

                # Get status (default based on remaining)
                if remaining <= 0:
                    status = 'PAID'
                elif remaining < total:
                    status = 'PARTIALLY_PAID'
                else:
                    status = 'UNPAID'

                payment_status = payment.get('status', status)

                payment_rows.append([
                    str(i),
                    invoice_number,
                    format_currency(payment_amount, symbol='Rs.'),
                    payment_depositor,
                    payment_date,
                    payment_time,
                    payment_method,
                    format_currency(remaining, symbol='Rs.'),
                    payment_note,
                    payment_status
                ])

            # If no payment rows, add a blank one for the template
            if not payment_rows:
                payment_rows = [["", invoice_number, "", "", "", "", "", "", "", ""]]

            # Create payments table
            payments_table = Table(payment_rows, colWidths=payment_col_widths)
            payments_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Sr.no centered
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Amount right aligned
                ('ALIGN', (7, 0), (7, -1), 'RIGHT'),   # Remaining Amount right aligned
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))

            payment_history_tables.append(payments_table)

        # ------ COMBINE ALL SECTIONS INTO FINAL DOCUMENT ------
        # Create contents for the main invoice (without payment history)
        invoice_content = []
        invoice_content.append(shop_name_table)
        invoice_content.append(shop_info_table)
        invoice_content.append(customer_info_table)
        invoice_content.append(items_header_table)
        invoice_content.append(items_table)
        invoice_content.append(total_row_table)
        invoice_content.append(amount_words_table)
        invoice_content.append(payment_tax_row)
        invoice_content.append(signature_table)
        invoice_content.append(subject_table)

        # Create a single FlowFrame that will contain all the invoice elements
        invoice_frame = Frame(
            doc.leftMargin, 
            doc.bottomMargin, 
            doc.width, 
            doc.height - 10,
            leftPadding=5, 
            rightPadding=5, 
            topPadding=5, 
            bottomPadding=5,
            showBoundary=1  # This gives us the main border around everything
        )

        # Create a final elements list
        elements = []

        # Add all invoice content elements
        for item in invoice_content:
            elements.append(item)

        # Add payment history tables if any
        for table in payment_history_tables:
            elements.append(table)

        # Build the document with the frame that adds the main border
        doc.addPageTemplates([PageTemplate(frames=[invoice_frame])])
        doc.build(elements)

        return True

    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        return False

def view_invoice(file_path):
    """Open an invoice file with the appropriate application"""
    try:
        if not os.path.exists(file_path):
            return False

        if platform.system() == 'Windows':
            subprocess.call(['start', '', file_path], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux
            subprocess.call(['xdg-open', file_path])
        return True
    except Exception as e:
        print(f"Error opening invoice: {e}")
        return False