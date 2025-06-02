
import os
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def format_currency(amount, symbol='Rs.'):
    """Format currency with proper symbol"""
    try:
        return f"{symbol}{float(amount):.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"

def get_shop_info():
    """Get shop information from database"""
    try:
        conn = sqlite3.connect('./pos_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all settings
        cursor.execute("SELECT key, value FROM settings")
        settings = dict(cursor.fetchall())
        
        shop_info = {
            'name': settings.get('shop_name', 'Shop Name'),
            'address': settings.get('shop_address', 'Shop Address'),
            'phone': settings.get('shop_phone', 'Phone Number'),
            'email': settings.get('shop_email', 'email@example.com'),
            'gstin': settings.get('shop_gstin', 'GSTIN Number'),
            'license': settings.get('shop_license', 'License Number'),
            'state': settings.get('shop_state', 'Maharashtra'),
            'state_code': settings.get('shop_state_code', '27')
        }
        
        conn.close()
        return shop_info
        
    except Exception as e:
        print(f"Error getting shop info: {e}")
        return {
            'name': 'Agritech Shop',
            'address': 'Shop Address',
            'phone': 'Phone Number',
            'email': 'email@example.com',
            'gstin': 'GSTIN Number',
            'license': 'License Number',
            'state': 'Maharashtra',
            'state_code': '27'
        }

def get_invoice_items(invoice_id):
    """Get items for an invoice from database"""
    try:
        conn = sqlite3.connect('./pos_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"DEBUG: Looking for items for invoice_id: '{invoice_id}' (type: {type(invoice_id)})")
        
        # If invoice_id is empty or None, try to find by invoice number
        if not invoice_id or invoice_id == '':
            print("DEBUG: invoice_id is empty, trying to find by invoice_number")
            # Get invoice_id from sales table using invoice_number
            cursor.execute("SELECT id FROM sales WHERE invoice_number = ?", (invoice_id,))
            result = cursor.fetchone()
            if result:
                invoice_id = result['id']
                print(f"DEBUG: Found invoice_id {invoice_id} for invoice_number {invoice_id}")
            else:
                print("DEBUG: Could not find invoice_id from invoice_number")
                conn.close()
                return []
        
        # Get schema information for debugging
        cursor.execute("PRAGMA table_info(invoice_items)")
        invoice_items_schema = [row[1] for row in cursor.fetchall()]
        print(f"DEBUG: invoice_items schema: {invoice_items_schema}")
        
        cursor.execute("PRAGMA table_info(sale_items)")
        sale_items_schema = [row[1] for row in cursor.fetchall()]
        print(f"DEBUG: sale_items schema: {sale_items_schema}")
        
        # Try to get items from invoice_items table
        cursor.execute("""
            SELECT ii.*, p.product_name, p.hsn_code, p.unit
            FROM invoice_items ii
            LEFT JOIN products p ON ii.product_id = p.id
            WHERE ii.invoice_id = ?
        """, (invoice_id,))
        invoice_items = cursor.fetchall()
        
        # Try to get items from sale_items table
        cursor.execute("""
            SELECT * FROM sale_items WHERE sale_id = ?
        """, (invoice_id,))
        sale_items = cursor.fetchall()
        
        print(f"DEBUG: Found {len(invoice_items)} items in invoice_items, {len(sale_items)} items in sale_items")
        
        items = []
        
        # Process invoice_items if available
        if invoice_items:
            for item in invoice_items:
                items.append({
                    'name': item.get('product_name', 'Unknown Product'),
                    'hsn': item.get('hsn_code', ''),
                    'batch': item.get('batch_number', ''),
                    'quantity': item.get('quantity', 0),
                    'unit': item.get('unit', 'pcs'),
                    'price': item.get('price_per_unit', 0),
                    'discount': item.get('discount_percentage', 0),
                    'total': item.get('total_price', 0)
                })
        
        # Process sale_items if available and no invoice_items found
        elif sale_items:
            for item in sale_items:
                items.append({
                    'name': item.get('product_name', 'Unknown Product'),
                    'hsn': item.get('hsn_code', ''),
                    'batch': '',  # sale_items might not have batch info
                    'quantity': item.get('quantity', 0),
                    'unit': 'pcs',  # default unit
                    'price': item.get('price', 0),
                    'discount': item.get('discount_percent', 0),
                    'total': item.get('total', 0)
                })
        
        # If no items found, try alternative query approach
        if not items:
            print("DEBUG: No items found, trying alternative query approach")
            cursor.execute("""
                SELECT * FROM invoice_data WHERE invoice_id = ? OR id = ?
            """, (invoice_id, invoice_id))
            invoice_data = cursor.fetchall()
            
            if invoice_data:
                print(f"DEBUG: Found {len(invoice_data)} items in invoice_data")
                for item in invoice_data:
                    items.append({
                        'name': item.get('product_name', 'Unknown Product'),
                        'hsn': item.get('hsn_code', ''),
                        'batch': item.get('batch_number', ''),
                        'quantity': item.get('quantity', 0),
                        'unit': item.get('unit', 'pcs'),
                        'price': item.get('price', 0),
                        'discount': item.get('discount', 0),
                        'total': item.get('total', 0)
                    })
            else:
                print("DEBUG: No items found in invoice_data either")
        
        conn.close()
        
        print(f"DEBUG: Retrieved {len(items)} items for processing")
        return items
        
    except Exception as e:
        print(f"Error getting invoice items: {e}")
        return []

def generate_invoice(invoice_data, output_path):
    """Generate PDF invoice"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Get shop information
        shop_info = get_shop_info()
        
        # Header with shop info
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=10,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(shop_info['name'], header_style))
        story.append(Paragraph(f"{shop_info['address']}", styles['Normal']))
        story.append(Paragraph(f"Phone: {shop_info['phone']} | Email: {shop_info['email']}", styles['Normal']))
        story.append(Paragraph(f"GSTIN: {shop_info['gstin']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Invoice title
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("TAX INVOICE", title_style))
        
        # Invoice details
        invoice_info = [
            ['Invoice No:', invoice_data.get('invoice_number', 'N/A')],
            ['Date:', invoice_data.get('date', datetime.now().strftime('%d/%m/%Y'))],
            ['Time:', invoice_data.get('time', datetime.now().strftime('%H:%M:%S'))]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[2*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 20))
        
        # Customer details
        customer = invoice_data.get('customer', {})
        customer_info = [
            ['Bill To:'],
            [f"Name: {customer.get('name', 'N/A')}"],
            [f"Phone: {customer.get('phone', 'N/A')}"],
            [f"Address: {customer.get('address', 'N/A')}"]
        ]
        
        if customer.get('email'):
            customer_info.append([f"Email: {customer.get('email')}"])
        if customer.get('gstin'):
            customer_info.append([f"GSTIN: {customer.get('gstin')}"])
        
        customer_table = Table(customer_info, colWidths=[5*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 20))
        
        # Items table
        # Get items from database
        items = get_invoice_items(invoice_data.get('invoice_id', ''))
        
        # Prepare items data
        items_data = [
            ['No', 'Description', 'Company', 'HSN', 'Batch', 'Expiry', 'Qty', 'Unit', 'Rate', 'Disc', 'Amount']
        ]
        
        if not items:
            print("WARNING: No formatted items found, creating placeholder")
            items_data.append(['1', 'No items found', '', '', '', '', '0', '', 'Rs.0.00', '', 'Rs.0.00'])
        else:
            # Group items by product to avoid duplicate entries
            grouped_items = {}
            for item in items:
                key = (item.get('name', 'Unknown'), item.get('batch', ''))
                if key in grouped_items:
                    # Add quantities for same product and batch
                    grouped_items[key]['quantity'] += item.get('quantity', 0)
                    grouped_items[key]['total'] += item.get('total', 0)
                else:
                    grouped_items[key] = item.copy()
            
            for i, item in enumerate(grouped_items.values(), 1):
                row_data = [
                    str(i),
                    str(item.get('name', 'Unknown Product')),
                    '',  # Company name
                    str(item.get('hsn', '')),
                    str(item.get('batch', '')),
                    '',  # Expiry
                    str(item.get('quantity', '0')),
                    str(item.get('unit', '')),
                    format_currency(item.get('price', 0), symbol='Rs.'),
                    str(item.get('discount', '')),
                    format_currency(item.get('total', 0), symbol='Rs.')
                ]
                items_data.append(row_data)
        
        print(f"DEBUG: Created {len(items_data)-1} rows for items table")
        if len(items_data) > 1:
            print(f"DEBUG: First row data: {items_data[1]}")
        
        # Column widths
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
        
        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Payment summary
        payment = invoice_data.get('payment', {})
        
        # Calculate totals from items
        subtotal = sum(item.get('total', 0) for item in items)
        if subtotal == 0:
            subtotal = payment.get('subtotal', 0)
        
        discount = payment.get('discount', 0)
        cgst = payment.get('cgst', 0)
        sgst = payment.get('sgst', 0)
        total_tax = cgst + sgst
        total_amount = subtotal - discount + total_tax
        
        summary_data = [
            ['', '', 'Subtotal:', format_currency(subtotal)],
            ['', '', 'Discount:', format_currency(discount)],
            ['', '', 'Central Tax (CGST):', format_currency(cgst)],
            ['', '', 'State Tax (SGST):', format_currency(sgst)],
            ['', '', 'Total Tax Amount:', format_currency(total_tax)],
            ['', '', 'Total Amount:', format_currency(total_amount)]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (2, -1), (3, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Payment method
        payment_method = payment.get('method', 'Cash')
        if isinstance(payment_method, (int, float)):
            payment_method = 'Cash'
        
        payment_info = [
            [f"Payment Method: {payment_method}"],
            [f"Payment Status: {payment.get('status', 'PAID')}"]
        ]
        
        payment_table = Table(payment_info, colWidths=[5*inch])
        payment_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Thank you for your business!", footer_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"Invoice generated successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        return False
