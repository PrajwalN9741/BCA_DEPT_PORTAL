import os
import uuid
import qrcode
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from config import Config

def allowed_file(filename, file_type='documents'):
    """Check if the uploaded file has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS.get(file_type, set())

def save_uploaded_file(file_data, category_folder, custom_name=None):
    """Save an uploaded file and return its relative path."""
    if not file_data or file_data.filename == '':
        return None
        
    filename = secure_filename(file_data.filename)
    # Generate unique filename to avoid overwrites
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'bin'
    
    if custom_name:
        saved_filename = f"{secure_filename(custom_name)}.{ext}"
    else:
        saved_filename = f"{uuid.uuid4().hex}.{ext}"
        
    os.makedirs(category_folder, exist_ok=True)
    full_path = os.path.join(category_folder, saved_filename)
    file_data.save(full_path)
    
    # Return relative path for saving in database (starting with static/)
    # For example: static/uploads/documents/filename.pdf
    rel_path = os.path.relpath(full_path, start=os.path.dirname(Config.UPLOAD_FOLDER))
    # Replace windows backslash with forward slash
    return rel_path.replace('\\', '/')

def generate_qr_code_path(data_string, receipt_number):
    """Generate a QR code image for verification and return its relative path."""
    qr_filename = f"qr_{receipt_number}.png"
    os.makedirs(Config.RECEIPTS_FOLDER, exist_ok=True)
    full_path = os.path.join(Config.RECEIPTS_FOLDER, qr_filename)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    qr.add_data(data_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(full_path)
    
    rel_path = os.path.relpath(full_path, start=os.path.dirname(Config.UPLOAD_FOLDER))
    return rel_path.replace('\\', '/')

def generate_receipt_pdf(receipt_number, payer_name, item_name, amount, payment_method, transaction_id, payment_date):
    """Generate a clean, professional PDF receipt using ReportLab."""
    pdf_filename = f"receipt_{receipt_number}.pdf"
    os.makedirs(Config.RECEIPTS_FOLDER, exist_ok=True)
    full_path = os.path.join(Config.RECEIPTS_FOLDER, pdf_filename)
    
    # Create the document
    doc = SimpleDocTemplate(
        full_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor("#1e3d59")
    secondary_color = colors.HexColor("#17b978")
    dark_neutral = colors.HexColor("#222831")
    light_neutral = colors.HexColor("#f5f5f5")
    
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'ReceiptSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        spaceAfter=20
    )
    
    normal_style = ParagraphStyle(
        'ReceiptNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=dark_neutral,
        leading=14
    )
    
    bold_style = ParagraphStyle(
        'ReceiptBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=dark_neutral,
        leading=14
    )
    
    header_style = ParagraphStyle(
        'ReceiptHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.white,
        alignment=0
    )
    
    story = []
    
    # Header Section
    story.append(Paragraph("BCA DEPARTMENT", title_style))
    story.append(Paragraph("National College Bagepalli BCA Dept | Admission & Events Portal", subtitle_style))
    
    # Divider line
    story.append(Spacer(1, 10))
    
    # Generate QR Code
    verify_url = f"http://127.0.0.1:5000/verify-receipt/{receipt_number}"
    qr_rel_path = generate_qr_code_path(verify_url, receipt_number)
    qr_full_path = os.path.join(os.path.dirname(Config.UPLOAD_FOLDER), qr_rel_path)
    
    # Metadata Table (Receipt No, Date, Transaction ID, Payment Method)
    meta_data = [
        [Paragraph("<b>Receipt Number:</b>", normal_style), Paragraph(receipt_number, bold_style), 
         Image(qr_full_path, width=1.2*inch, height=1.2*inch) if os.path.exists(qr_full_path) else Paragraph("[QR Code]", normal_style)],
        [Paragraph("<b>Date:</b>", normal_style), Paragraph(payment_date, normal_style), ""],
        [Paragraph("<b>Transaction ID:</b>", normal_style), Paragraph(transaction_id, normal_style), ""],
        [Paragraph("<b>Payment Method:</b>", normal_style), Paragraph(payment_method, normal_style), ""]
    ]
    
    # Spans QR code across 4 rows
    meta_table = Table(meta_data, colWidths=[2.0*inch, 2.5*inch, 2.0*inch])
    meta_table.setStyle(TableStyle([
        ('SPAN', (2, 0), (2, 3)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 25))
    
    # Payer details
    story.append(Paragraph("<b>Receipt Issued To:</b>", bold_style))
    story.append(Paragraph(f"Name: {payer_name}", normal_style))
    story.append(Spacer(1, 15))
    
    # Invoice details table
    invoice_headers = [
        Paragraph("Description", header_style),
        Paragraph("Quantity", header_style),
        Paragraph("Amount (INR)", header_style)
    ]
    
    invoice_row = [
        Paragraph(item_name, normal_style),
        Paragraph("1", normal_style),
        Paragraph(f"Rs. {amount:,.2f}", normal_style)
    ]
    
    total_row = [
        Paragraph("<b>Total Paid</b>", normal_style),
        "",
        Paragraph(f"<b>Rs. {amount:,.2f}</b>", bold_style)
    ]
    
    table_data = [invoice_headers, invoice_row, total_row]
    invoice_table = Table(table_data, colWidths=[4.0*inch, 1.0*inch, 1.5*inch])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), light_neutral),
        ('SPAN', (0, -1), (1, -1)),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 40))
    
    # Footer notice
    footer_text = (
        "This is an electronically generated document. No signature is required. "
        "For any queries regarding this transaction, contact the BCA Department administration "
        "at support@collegebca.edu."
    )
    story.append(Paragraph(footer_text, ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)))
    
    # Build PDF
    doc.build(story)
    
    # Return path relative to app root directory
    pdf_rel_path = os.path.relpath(full_path, start=os.path.dirname(Config.UPLOAD_FOLDER))
    return pdf_rel_path.replace('\\', '/')
