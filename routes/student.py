from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Student, Admission, EventRegistration, Payment, Receipt
from utils import save_uploaded_file, allowed_file
from config import Config

student_bp = Blueprint('student', __name__)

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Check if current user is admin or student
        if current_user.get_id().startswith('admin_'):
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('student/register.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('student/register.html')
            
        if Student.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return render_template('student/register.html')
            
        if Student.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template('student/register.html')
            
        new_student = Student(username=username, email=email)
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('student.login'))
        
    return render_template('student/register.html')

@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.get_id().startswith('admin_'):
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        student = Student.query.filter_by(username=username).first()
        if student and student.check_password(password):
            login_user(student)
            flash(f"Welcome back, {student.username}!", "success")
            return redirect(url_for('student.dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('student/login.html')

@student_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('main.home'))

@student_bp.route('/dashboard')
@login_required
def dashboard():
    # Enforce that current user is a student
    if not current_user.get_id().startswith('student_'):
        flash("Unauthorized access. Admin must log in through the admin portal.", "danger")
        logout_user()
        return redirect(url_for('student.login'))
        
    student = Student.query.get(int(current_user.get_id().split('_')[1]))
    
    # Get admission applications (should be max 1)
    admission = Admission.query.filter_by(student_id=student.id).order_by(Admission.created_at.desc()).first()
    
    # Get registrations
    registrations = EventRegistration.query.filter_by(student_id=student.id).all()
    
    # Payment History
    admission_ids = [adm.id for adm in student.admissions]
    registration_ids = [reg.id for reg in student.registrations]
    
    payments = []
    if admission_ids:
        adm_payments = Payment.query.filter(Payment.type == 'Admission', Payment.reference_id.in_(admission_ids)).all()
        payments.extend(adm_payments)
    if registration_ids:
        evt_payments = Payment.query.filter(Payment.type == 'Event', Payment.reference_id.in_(registration_ids)).all()
        payments.extend(evt_payments)
        
    # Sort payments by date
    payments.sort(key=lambda p: p.created_at, reverse=True)
    
    return render_template(
        'student/dashboard.html',
        student=student,
        admission=admission,
        registrations=registrations,
        payments=payments
    )

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.get_id().startswith('student_'):
        return redirect(url_for('main.home'))
        
    student = Student.query.get(int(current_user.get_id().split('_')[1]))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile')
        semester = request.form.get('semester')
        
        profile_file = request.files.get('profile_photo')
        
        student.full_name = full_name
        student.mobile = mobile
        if semester:
            student.semester = int(semester)
            
        if profile_file and profile_file.filename != '':
            if allowed_file(profile_file.filename, 'images'):
                photo_path = save_uploaded_file(profile_file, Config.FACULTY_FOLDER, f"student_{student.id}")
                student.profile_photo = photo_path
            else:
                flash("Invalid image format. Supported formats: PNG, JPG, JPEG, GIF", "danger")
                return redirect(url_for('student.profile'))
                
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('student.dashboard'))
        
    return render_template('student/profile.html', student=student)
