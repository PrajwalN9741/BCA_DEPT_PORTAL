import os
import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Student, Event, EventRegistration, Payment, Receipt
from utils import generate_receipt_pdf

event_bp = Blueprint('event', __name__)

@event_bp.route('/')
@event_bp.route('/list')
def list_events():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('event/list.html', events=events)

@event_bp.route('/detail/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check registration if logged in
    is_registered = False
    reg_details = None
    if current_user.is_authenticated and current_user.get_id().startswith('student_'):
        student_id = int(current_user.get_id().split('_')[1])
        reg_details = EventRegistration.query.filter_by(event_id=event_id, student_id=student_id).first()
        if reg_details:
            is_registered = True
            
    return render_template('event/detail.html', event=event, is_registered=is_registered, reg_details=reg_details)

@event_bp.route('/register/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register(event_id):
    if not current_user.get_id().startswith('student_'):
        flash("Only student accounts can register for events.", "warning")
        return redirect(url_for('student.login'))
        
    event = Event.query.get_or_404(event_id)
    student_id = int(current_user.get_id().split('_')[1])
    student = Student.query.get(student_id)
    
    # Check if registration deadline has passed
    if datetime.utcnow() > event.deadline:
        flash("Registration deadline for this event has passed.", "danger")
        return redirect(url_for('event.detail', event_id=event.id))
        
    # Check if already registered
    existing_reg = EventRegistration.query.filter_by(event_id=event_id, student_id=student_id).first()
    if existing_reg:
        flash("You are already registered for this event.", "info")
        return redirect(url_for('event.detail', event_id=event.id))
        
    if request.method == 'POST':
        name = request.form.get('name')
        usn = request.form.get('usn')
        semester = request.form.get('semester')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        
        if not name or not usn or not semester or not email or not mobile:
            flash("All fields are mandatory.", "danger")
            return render_template('event/register.html', event=event, student=student)
            
        # Create event registration
        reg = EventRegistration(
            event_id=event.id,
            student_id=student.id,
            name=name,
            usn=usn,
            semester=int(semester),
            email=email,
            mobile=mobile,
            payment_status='Pending'
        )
        db.session.add(reg)
        db.session.commit()
        
        # Link USN to Student profile if not already set
        if not student.usn:
            student.usn = usn
            db.session.commit()
            
        # If registration fee is zero, process free registration directly
        if event.registration_fee == 0:
            reg.payment_status = 'Paid'
            reg.amount_paid = 0.0
            
            # Generate Receipt Number
            receipt_num = f"EVT2026{reg.id:05d}"
            reg.receipt_number = receipt_num
            
            # Record $0 Payment
            tx_id = f"FREE{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
            payment = Payment(
                type='Event',
                reference_id=reg.id,
                transaction_id=tx_id,
                amount=0.0,
                payment_method='Free Event',
                payment_status='Success'
            )
            db.session.add(payment)
            db.session.flush()
            
            # Render PDF receipt
            generate_receipt_pdf(
                receipt_number=receipt_num,
                payer_name=name,
                item_name=f"Event Ticket: {event.name}",
                amount=0.0,
                payment_method="Free Registration",
                transaction_id=tx_id,
                payment_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            receipt = Receipt(
                receipt_number=receipt_num,
                payment_id=payment.id,
                qrcode_path=f"static/uploads/receipts/qr_{receipt_num}.png"
            )
            db.session.add(receipt)
            db.session.commit()
            
            flash("Registration successful! (Free Event)", "success")
            return redirect(url_for('event.receipt_view', registration_id=reg.id))
            
        # Redirect to payment portal
        return redirect(url_for('event.pay_fee', registration_id=reg.id))
        
    return render_template('event/register.html', event=event, student=student)

@event_bp.route('/pay/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def pay_fee(registration_id):
    reg = EventRegistration.query.get_or_404(registration_id)
    event = Event.query.get(reg.event_id)
    student_id = int(current_user.get_id().split('_')[1])
    
    if reg.student_id != student_id:
        flash("Unauthorized payment request.", "danger")
        return redirect(url_for('student.dashboard'))
        
    if reg.payment_status == 'Paid':
        flash("Payment already processed.", "info")
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        tx_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        reg.payment_status = 'Paid'
        reg.payment_method = payment_method
        reg.amount_paid = event.registration_fee
        
        receipt_num = f"EVT2026{reg.id:05d}"
        reg.receipt_number = receipt_num
        
        payment = Payment(
            type='Event',
            reference_id=reg.id,
            transaction_id=tx_id,
            amount=event.registration_fee,
            payment_method=payment_method,
            payment_status='Success'
        )
        db.session.add(payment)
        db.session.flush()
        
        generate_receipt_pdf(
            receipt_number=receipt_num,
            payer_name=reg.name,
            item_name=f"Event Registration: {event.name}",
            amount=event.registration_fee,
            payment_method=payment_method,
            transaction_id=tx_id,
            payment_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        receipt = Receipt(
            receipt_number=receipt_num,
            payment_id=payment.id,
            qrcode_path=f"static/uploads/receipts/qr_{receipt_num}.png"
        )
        db.session.add(receipt)
        db.session.commit()
        
        flash(f"Payment successful! Registered for {event.name}.", "success")
        return redirect(url_for('event.receipt_view', registration_id=reg.id))
        
    return render_template('event/pay_fee.html', reg=reg, event=event)

@event_bp.route('/receipt/<int:registration_id>')
@login_required
def receipt_view(registration_id):
    reg = EventRegistration.query.get_or_404(registration_id)
    event = Event.query.get(reg.event_id)
    student_id = int(current_user.get_id().split('_')[1])
    
    if reg.student_id != student_id:
        flash("Unauthorized receipt request.", "danger")
        return redirect(url_for('student.dashboard'))
        
    if reg.payment_status != 'Paid':
        flash("Payment has not been completed yet.", "warning")
        return redirect(url_for('event.pay_fee', registration_id=reg.id))
        
    receipt_filename = f"receipt_{reg.receipt_number}.pdf"
    receipt_url = f"static/uploads/receipts/{receipt_filename}"
    
    return render_template('event/receipt.html', reg=reg, event=event, receipt_url=receipt_url)
