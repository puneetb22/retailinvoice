
import os
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import traceback

def generate_invoice(invoice_data, file_path):
    """
    Generate a PDF invoice using ReportLab
    
    Args:
        invoice_data: Dictionary containing invoice details
        file_path: Path where the PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"DEBUG: Starting invoice generation for file: {file_path}")
        print(f"DEBUG: Invoice data keys: {invoice_data.keys()}")
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Company header
        company_name = invoice_data.get('company_name', 'Company Name')
        company_address = invoice_data.get('company_address', '')
        company_phone = invoice_data.get('company_phone', '')
        company_email = invoice_data.get('company_email', '')
        company_gst = invoice_data.get('company_gst', '')
        
        # Title
        elements.append(Paragraph(company_name, title_style))
        elements.append(Spacer(1, 12))
        
        # Company details
        if company_address:
            elements.append(Paragraph(f"Address: {company_address}", styles['Normal']))
        if company_phone:
            elements.append(Paragraph(f"Phone: {company_phone}", styles['Normal']))
        if company_email:
            elements.append(Paragraph(f"Email: {company_email}", styles['Normal']))
        if company_gst:
            elements.append(Paragraph(f"GST No: {company_gst}", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Invoice header with customer details
        invoice_header_data = [
            ['Invoice No:', invoice_data.get('invoice_number', ''), 'Date:', invoice_data.get('date', '')],
            ['Customer:', invoice_data.get('customer_name', 'Walk-in Customer'), 'Phone:', invoice_data.get('customer_phone', 'N/A')]
        ]
        
        invoice_header_table = Table(invoice_header_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
        invoice_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(invoice_header_table)
        elements.append(Spacer(1, 20))
        
        # Items table header
        items_data = [['No', 'Description of Good', 'Company name', 'HSN', 'Batch NO', 'Expiry Date', 'Qty', 'Unit', 'Rate', 'Disc', 'Amount']]
        
        # Add items to the table
        items = invoice_data.get('items', [])
        print(f"DEBUG: Processing {len(items)} items")
        
        total_amount = 0
        for i, item in enumerate(items, 1):
            print(f"DEBUG: Item {i}: {item}")
            
            # Extract item details with defaults
            description = item.get('name', item.get('description', 'N/A'))
            company_name_item = item.get('company_name', item.get('brand', 'N/A'))
            hsn_code = item.get('hsn_code', 'N/A')
            batch_number = item.get('batch_number', 'N/A')
            expiry_date = item.get('expiry_date', 'N/A')
            quantity = item.get('quantity', 1)
            unit = item.get('unit', 'pcs')
            rate = float(item.get('price', item.get('rate', 0)))
            discount = item.get('discount', 0)
            amount = float(item.get('total', quantity * rate))
            
            # Format expiry date if it exists
            if expiry_date and expiry_date != 'N/A':
                try:
                    if isinstance(expiry_date, str) and expiry_date.count('-') == 2:
                        # Assume YYYY-MM-DD format
                        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    pass  # Keep original format if parsing fails
            
            total_amount += amount
            
            items_data.append([
                str(i),
                str(description),
                str(company_name_item),
                str(hsn_code),
                str(batch_number),
                str(expiry_date),
                str(quantity),
                str(unit),
                f"Rs.{rate:.2f}",
                str(discount) if discount else '',
                f"Rs.{amount:.2f}"
            ])
        
        # Create items table
        items_table = Table(items_data, colWidths=[0.4*inch, 1.5*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.4*inch, 0.4*inch, 0.8*inch, 0.5*inch, 0.8*inch])
        items_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Right align numeric columns
            ('ALIGN', (6, 1), (6, -1), 'CENTER'),  # Qty
            ('ALIGN', (8, 1), (8, -1), 'RIGHT'),   # Rate
            ('ALIGN', (10, 1), (10, -1), 'RIGHT'), # Amount
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        # Total section
        subtotal = invoice_data.get('subtotal', total_amount)
        tax_amount = invoice_data.get('tax_amount', 0)
        total = invoice_data.get('total', subtotal + tax_amount)
        
        # Convert total to words
        def number_to_words(num):
            """Convert number to words (simplified version)"""
            if num == 0:
                return "ZERO RUPEES ONLY"
            
            # Simple conversion for demonstration
            units = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
            teens = ["TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
            tens = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
            
            if num < 10:
                return f"{units[int(num)]} RUPEES ONLY"
            elif num < 100:
                if num < 20:
                    return f"{teens[int(num) - 10]} RUPEES ONLY"
                else:
                    return f"{tens[int(num) // 10]} {units[int(num) % 10]}".strip() + " RUPEES ONLY"
            elif num < 1000:
                hundreds = int(num) // 100
                remainder = int(num) % 100
                result = f"{units[hundreds]} HUNDRED"
                if remainder > 0:
                    if remainder < 10:
                        result += f" {units[remainder]}"
                    elif remainder < 20:
                        result += f" {teens[remainder - 10]}"
                    else:
                        result += f" {tens[remainder // 10]} {units[remainder % 10]}".strip()
                return result + " RUPEES ONLY"
            else:
                # For larger numbers, use a simplified approach
                return f"{int(total)} RUPEES ONLY"
        
        total_in_words = number_to_words(total)
        
        # Total table
        total_data = [
            ['', '', '', '', '', '', '', '', '', 'Total', f'Rs.{total:.2f}']
        ]
        
        total_table = Table(total_data, colWidths=[0.4*inch, 1.5*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.4*inch, 0.4*inch, 0.8*inch, 0.5*inch, 0.8*inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (9, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (9, 0), (-1, 0), colors.black),
            ('ALIGN', (9, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (9, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (9, 0), (-1, 0), 10),
            ('GRID', (9, 0), (-1, 0), 1, colors.black)
        ]))
        
        elements.append(total_table)
        elements.append(Spacer(1, 12))
        
        # Total in words
        elements.append(Paragraph(f"<b>Total Amount in Words:</b> {total_in_words}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Terms and conditions
        elements.append(Paragraph("<b>Terms & Conditions:</b>", styles['Normal']))
        elements.append(Paragraph("1. Goods once sold will not be taken back.", styles['Normal']))
        elements.append(Paragraph("2. Interest @ 18% p.a. will be charged on bills not paid within 30 days.", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Footer
        elements.append(Paragraph("Thank you for your business!", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        print(f"DEBUG: Invoice generated successfully at: {file_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to generate invoice: {e}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return False

def generate_pdf_invoice(invoice_data, output_buffer):
    """
    Generate PDF invoice and write to buffer
    
    Args:
        invoice_data: Dictionary containing invoice details
        output_buffer: BytesIO buffer to write PDF data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use the same generation logic but with buffer
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Use the same elements generation as the file version
        # For now, create a temporary file and read it back
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            success = generate_invoice(invoice_data, temp_file.name)
            if success:
                with open(temp_file.name, 'rb') as f:
                    output_buffer.write(f.read())
                os.unlink(temp_file.name)
                return True
            else:
                os.unlink(temp_file.name)
                return False
                
    except Exception as e:
        print(f"ERROR: Failed to generate PDF invoice to buffer: {e}")
        return False
