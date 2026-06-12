import os
import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, Student, Admission, Payment, Receipt, WebsiteSetting
from utils import save_uploaded_file, allowed_file, generate_receipt_pdf
from config import Config

admission_bp = Blueprint('admission', __name__)

@admission_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if not current_user.get_id().startswith('student_'):
        flash("You must be logged in as a student to apply.", "warning")
        return redirect(url_for('student.login'))
        
    student_id = int(current_user.get_id().split('_')[1])
    
    # Check if already applied
    existing_admission = Admission.query.filter_by(student_id=student_id).first()
    if existing_admission:
        flash("You have already submitted an admission application.", "info")
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        # Personal Info
        full_name = request.form.get('full_name')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        dob_str = request.form.get('dob')
        gender = request.form.get('gender')
        aadhaar_number = request.form.get('aadhaar_number')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        
        # Address
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        district = request.form.get('district')
        pin_code = request.form.get('pin_code')
        
        # Academics
        tenth_pct = request.form.get('tenth_percentage')
        twelfth_pct = request.form.get('twelfth_percentage')
        board_details = request.form.get('board_details')
        prev_degree = request.form.get('previous_degree')
        
        # Document Uploads
        f_photo = request.files.get('photo')
        f_sig = request.files.get('signature')
        f_aadhaar = request.files.get('aadhaar')
        f_tenth = request.files.get('tenth_marks')
        f_twelfth = request.files.get('twelfth_marks')
        f_tc = request.files.get('tc')
        
        # Required Validation
        required_fields = [full_name, father_name, mother_name, dob_str, gender, aadhaar_number, mobile, email,
                           address, city, state, district, pin_code, tenth_pct, twelfth_pct, board_details]
        if any(f is None or f == '' for f in required_fields):
            flash("Please fill in all mandatory text fields.", "danger")
            return render_template('admission/apply.html')
            
        required_files = [f_photo, f_sig, f_aadhaar, f_tenth, f_twelfth, f_tc]
        if any(f is None or f.filename == '' for f in required_files):
            flash("Please upload all mandatory documents.", "danger")
            return render_template('admission/apply.html')
            
        # File type validation
        file_valid = True
        if not allowed_file(f_photo.filename, 'images'): file_valid = False
        if not allowed_file(f_sig.filename, 'images'): file_valid = False
        for f in [f_aadhaar, f_tenth, f_twelfth, f_tc]:
            if not allowed_file(f.filename, 'documents') and not allowed_file(f.filename, 'images'):
                file_valid = False
                
        if not file_valid:
            flash("Invalid file formats uploaded. Photos & signatures must be images. Documents must be images or PDFs.", "danger")
            return render_template('admission/apply.html')
            
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format for Date of Birth.", "danger")
            return render_template('admission/apply.html')
            
        # Save documents
        p_photo = save_uploaded_file(f_photo, Config.DOCUMENTS_FOLDER, f"std_{student_id}_photo")
        p_sig = save_uploaded_file(f_sig, Config.DOCUMENTS_FOLDER, f"std_{student_id}_sig")
        p_aadhaar = save_uploaded_file(f_aadhaar, Config.DOCUMENTS_FOLDER, f"std_{student_id}_aadhaar")
        p_tenth = save_uploaded_file(f_tenth, Config.DOCUMENTS_FOLDER, f"std_{student_id}_tenth")
        p_twelfth = save_uploaded_file(f_twelfth, Config.DOCUMENTS_FOLDER, f"std_{student_id}_twelfth")
        p_tc = save_uploaded_file(f_tc, Config.DOCUMENTS_FOLDER, f"std_{student_id}_tc")
        
        # Save Student Admission in Database
        admission = Admission(
            student_id=student_id,
            full_name=full_name,
            father_name=father_name,
            mother_name=mother_name,
            dob=dob,
            gender=gender,
            aadhaar_number=aadhaar_number,
            mobile=mobile,
            email=email,
            address=address,
            city=city,
            state=state,
            district=district,
            pin_code=pin_code,
            tenth_percentage=float(tenth_pct),
            twelfth_percentage=float(twelfth_pct),
            board_details=board_details,
            previous_degree=prev_degree,
            photo_path=p_photo,
            signature_path=p_sig,
            aadhaar_path=p_aadhaar,
            tenth_marks_path=p_tenth,
            twelfth_marks_path=p_twelfth,
            tc_path=p_tc,
            status='Pending Payment'
        )
        
        db.session.add(admission)
        db.session.commit()
        
        # Link name and mobile to Student account if empty
        student = Student.query.get(student_id)
        if not student.full_name:
            student.full_name = full_name
        if not student.mobile:
            student.mobile = mobile
        db.session.commit()
        
        flash("Application saved successfully! Please proceed to fee payment.", "success")
        return redirect(url_for('admission.pay_fee', admission_id=admission.id))
        
    return render_template('admission/apply.html')

@admission_bp.route('/pay/<int:admission_id>', methods=['GET', 'POST'])
@login_required
def pay_fee(admission_id):
    admission = Admission.query.get_or_404(admission_id)
    student_id = int(current_user.get_id().split('_')[1])
    
    # Security check: Student can only pay for their own application
    if admission.student_id != student_id:
        flash("Unauthorized payment request.", "danger")
        return redirect(url_for('student.dashboard'))
        
    if admission.status != 'Pending Payment':
        flash("Fee already paid or application processed.", "info")
        return redirect(url_for('student.dashboard'))
        
    # Get fee from settings
    fee_setting = WebsiteSetting.query.filter_by(key='admission_fee').first()
    fee_amount = float(fee_setting.value) if fee_setting else 45000.00
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method') # UPI, Credit Card, Debit Card, Net Banking
        
        # Simulate payment gateway routing
        tx_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # Update admission status
        admission.status = 'Paid'
        admission.transaction_id = tx_id
        admission.payment_method = payment_method
        admission.amount_paid = fee_amount
        
        # Generate dynamic receipt number ADM202600001 format
        receipt_num = f"ADM2026{admission.id:05d}"
        admission.receipt_number = receipt_num
        
        # Record payment transaction
        payment = Payment(
            type='Admission',
            reference_id=admission.id,
            transaction_id=tx_id,
            amount=fee_amount,
            payment_method=payment_method,
            payment_status='Success'
        )
        db.session.add(payment)
        db.session.flush() # Flushes payment to db to get payment.id
        
        # Generate QR-code and receipt PDF
        pdf_path = generate_receipt_pdf(
            receipt_number=receipt_num,
            payer_name=admission.full_name,
            item_name="BCA Course Admission Fee",
            amount=fee_amount,
            payment_method=payment_method,
            transaction_id=tx_id,
            payment_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save receipt record
        receipt = Receipt(
            receipt_number=receipt_num,
            payment_id=payment.id,
            qrcode_path=f"static/uploads/receipts/qr_{receipt_num}.png"
        )
        db.session.add(receipt)
        db.session.commit()
        
        flash("Payment successful! Admission application submitted.", "success")
        return redirect(url_for('admission.receipt_view', admission_id=admission.id))
        
    return render_template('admission/pay_fee.html', admission=admission, fee_amount=fee_amount)

@admission_bp.route('/receipt/<int:admission_id>')
@login_required
def receipt_view(admission_id):
    admission = Admission.query.get_or_404(admission_id)
    student_id = int(current_user.get_id().split('_')[1])
    
    if admission.student_id != student_id:
        flash("Unauthorized receipt request.", "danger")
        return redirect(url_for('student.dashboard'))
        
    if admission.status == 'Pending Payment':
        flash("Payment has not been completed yet.", "warning")
        return redirect(url_for('admission.pay_fee', admission_id=admission.id))
        
    receipt_filename = f"receipt_{admission.receipt_number}.pdf"
    receipt_url = f"static/uploads/receipts/{receipt_filename}"
    
    return render_template('admission/receipt.html', admission=admission, receipt_url=receipt_url)
