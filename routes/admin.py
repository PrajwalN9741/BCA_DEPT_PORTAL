import os
from io import BytesIO
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import (
    db, Admin, Student, Admission, Faculty, Event, EventRegistration, 
    Payment, Receipt, Placement, Alumni, Gallery, Download, News, ContactMessage, WebsiteSetting, AuditLog,
    Course, CareerOpportunity, HigherEducation, StudentProject
)
from utils import save_uploaded_file, allowed_file
from config import Config
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

admin_bp = Blueprint('admin', __name__)

# Admin access check decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
            flash("Admin login required to view this page.", "danger")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def log_audit(action, details=None):
    """Log admin actions."""
    try:
        admin_id = int(current_user.get_id().split('_')[1])
        admin = Admin.query.get(admin_id)
        log = AuditLog(
            user_type='Admin',
            user_id=admin_id,
            username=admin.username,
            action=action,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.get_id().startswith('admin_'):
            return redirect(url_for('admin.dashboard'))
        logout_user() # Logout student
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash(f"Welcome Admin {admin.username}!", "success")
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Invalid administrator credentials.", "danger")
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@admin_required
def logout():
    log_audit("Logout", "Logged out from system")
    logout_user()
    flash("Administrator session logged out.", "success")
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Fetch Counts
    total_students = Student.query.count()
    total_admissions = Admission.query.count()
    approved_admissions = Admission.query.filter_by(status='Approved').count()
    pending_admissions = Admission.query.filter_by(status='Paid').count()
    total_events = Event.query.count()
    
    # Revenue Calculations
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(payment_status='Success').scalar() or 0.0
    admission_revenue = db.session.query(db.func.sum(Payment.amount)).filter(Payment.payment_status=='Success', Payment.type=='Admission').scalar() or 0.0
    event_revenue = db.session.query(db.func.sum(Payment.amount)).filter(Payment.payment_status=='Success', Payment.type=='Event').scalar() or 0.0
    
    # Chart Data Preps
    # Admissions by Status
    status_counts = db.session.query(Admission.status, db.func.count(Admission.id)).group_by(Admission.status).all()
    status_chart = {status: count for status, count in status_counts}
    
    # Registrations per Event
    event_counts = db.session.query(Event.name, db.func.count(EventRegistration.id)).join(EventRegistration).group_by(Event.id).all()
    event_chart = {name: count for name, count in event_counts}
    
    # Audits
    recent_audits = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(3).all()
    
    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_admissions=total_admissions,
        approved_admissions=approved_admissions,
        pending_admissions=pending_admissions,
        total_events=total_events,
        total_revenue=total_revenue,
        admission_revenue=admission_revenue,
        event_revenue=event_revenue,
        status_chart=status_chart,
        event_chart=event_chart,
        recent_audits=recent_audits,
        recent_messages=recent_messages
    )

@admin_bp.route('/website', methods=['GET', 'POST'])
@admin_required
def website_content():
    if request.method == 'POST':
        for key, value in request.form.items():
            setting = WebsiteSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                db.session.add(WebsiteSetting(key=key, value=value))
        db.session.commit()
        log_audit("Update Website Settings", "Modified Home/About website details")
        flash("Website settings updated successfully!", "success")
        return redirect(url_for('admin.website_content'))
        
    settings = {s.key: s.value for s in WebsiteSetting.query.all()}
    return render_template('admin/website.html', settings=settings)

# FACULTY CRUD
@admin_bp.route('/faculty', methods=['GET', 'POST'])
@admin_required
def faculty():
    if request.method == 'POST':
        name = request.form.get('name')
        qual = request.form.get('qualification')
        desig = request.form.get('designation')
        exp = request.form.get('experience')
        spec = request.form.get('specialization')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        linkedin = request.form.get('linkedin')
        
        photo = request.files.get('photo')
        
        photo_path = None
        if photo and photo.filename != '':
            if allowed_file(photo.filename, 'images'):
                photo_path = save_uploaded_file(photo, Config.FACULTY_FOLDER)
            else:
                flash("Invalid image format.", "danger")
                return redirect(url_for('admin.faculty'))
                
        new_fac = Faculty(
            name=name,
            qualification=qual,
            designation=desig,
            experience=int(exp) if exp else 0,
            specialization=spec,
            email=email,
            mobile=mobile,
            linkedin=linkedin,
            photo_path=photo_path
        )
        db.session.add(new_fac)
        db.session.commit()
        log_audit("Add Faculty", f"Added faculty member: {name}")
        flash("Faculty added successfully!", "success")
        return redirect(url_for('admin.faculty'))
        
    faculties = Faculty.query.all()
    return render_template('admin/faculty.html', faculties=faculties)

@admin_bp.route('/faculty/edit/<int:fac_id>', methods=['POST'])
@admin_required
def edit_faculty(fac_id):
    fac = Faculty.query.get_or_404(fac_id)
    fac.name = request.form.get('name')
    fac.qualification = request.form.get('qualification')
    fac.designation = request.form.get('designation')
    fac.experience = int(request.form.get('experience'))
    fac.specialization = request.form.get('specialization')
    fac.email = request.form.get('email')
    fac.mobile = request.form.get('mobile')
    fac.linkedin = request.form.get('linkedin')
    
    photo = request.files.get('photo')
    if photo and photo.filename != '':
        if allowed_file(photo.filename, 'images'):
            fac.photo_path = save_uploaded_file(photo, Config.FACULTY_FOLDER)
            
    db.session.commit()
    log_audit("Edit Faculty", f"Modified details of faculty: {fac.name}")
    flash("Faculty updated successfully!", "success")
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/faculty/delete/<int:fac_id>', methods=['POST'])
@admin_required
def delete_faculty(fac_id):
    fac = Faculty.query.get_or_404(fac_id)
    log_audit("Delete Faculty", f"Deleted faculty member: {fac.name}")
    db.session.delete(fac)
    db.session.commit()
    flash("Faculty deleted successfully!", "success")
    return redirect(url_for('admin.faculty'))

# EVENTS CRUD
@admin_bp.route('/events', methods=['GET', 'POST'])
@admin_required
def events():
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        venue = request.form.get('venue')
        fee = float(request.form.get('registration_fee', 0))
        date_str = request.form.get('date')
        deadline_str = request.form.get('deadline')
        
        poster = request.files.get('poster')
        
        poster_path = None
        if poster and poster.filename != '':
            if allowed_file(poster.filename, 'images'):
                poster_path = save_uploaded_file(poster, Config.EVENTS_FOLDER)
                
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash("Invalid date/deadline formats.", "danger")
            return redirect(url_for('admin.events'))
            
        new_event = Event(
            name=name,
            description=desc,
            venue=venue,
            registration_fee=fee,
            date=date,
            deadline=deadline,
            poster_path=poster_path
        )
        db.session.add(new_event)
        db.session.commit()
        log_audit("Create Event", f"Scheduled new event: {name}")
        flash("Event scheduled successfully!", "success")
        return redirect(url_for('admin.events'))
        
    events = Event.query.all()
    return render_template('admin/events.html', events=events)

@admin_bp.route('/events/edit/<int:event_id>', methods=['POST'])
@admin_required
def edit_event(event_id):
    evt = Event.query.get_or_404(event_id)
    evt.name = request.form.get('name')
    evt.description = request.form.get('description')
    evt.venue = request.form.get('venue')
    evt.registration_fee = float(request.form.get('registration_fee', 0))
    
    date_str = request.form.get('date')
    deadline_str = request.form.get('deadline')
    
    try:
        evt.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        evt.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('admin.events'))
        
    poster = request.files.get('poster')
    if poster and poster.filename != '':
        if allowed_file(poster.filename, 'images'):
            evt.poster_path = save_uploaded_file(poster, Config.EVENTS_FOLDER)
            
    db.session.commit()
    log_audit("Edit Event", f"Modified details of event: {evt.name}")
    flash("Event updated successfully!", "success")
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/delete/<int:event_id>', methods=['POST'])
@admin_required
def delete_event(event_id):
    evt = Event.query.get_or_404(event_id)
    log_audit("Delete Event", f"Deleted scheduled event: {evt.name}")
    db.session.delete(evt)
    db.session.commit()
    flash("Event deleted successfully!", "success")
    return redirect(url_for('admin.events'))

# ADMISSION APPROVAL SYSTEM
@admin_bp.route('/admissions')
@admin_required
def admissions():
    adms = Admission.query.order_by(Admission.created_at.desc()).all()
    return render_template('admin/admissions.html', admissions=adms)

@admin_bp.route('/admissions/approve/<int:adm_id>', methods=['POST'])
@admin_required
def approve_admission(adm_id):
    adm = Admission.query.get_or_404(adm_id)
    student = Student.query.get(adm.student_id)
    
    # Generate dynamic USN if they don't have one
    if not student.usn:
        # Generate USN like NCB26BCA1001
        year_suffix = datetime.now().strftime('%y')
        count = Student.query.filter(Student.usn.isnot(None)).count() + 1
        generated_usn = f"NCB{year_suffix}BCA{count:03d}"
        student.usn = generated_usn
        
    adm.status = 'Approved'
    db.session.commit()
    log_audit("Approve Admission", f"Approved admission application of student: {adm.full_name}. USN: {student.usn}")
    flash(f"Admission application of {adm.full_name} approved! USN assigned: {student.usn}.", "success")
    return redirect(url_for('admin.admissions'))

@admin_bp.route('/admissions/reject/<int:adm_id>', methods=['POST'])
@admin_required
def reject_admission(adm_id):
    adm = Admission.query.get_or_404(adm_id)
    adm.status = 'Rejected'
    db.session.commit()
    log_audit("Reject Admission", f"Rejected admission application of student: {adm.full_name}")
    flash(f"Admission application of {adm.full_name} rejected.", "info")
    return redirect(url_for('admin.admissions'))

# PAYMENTS
@admin_bp.route('/payments')
@admin_required
def payments():
    txs = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', transactions=txs)

# GALLERY CRUD
@admin_bp.route('/gallery', methods=['GET', 'POST'])
@admin_required
def gallery():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        file = request.files.get('file')
        
        if not file or file.filename == '':
            flash("Please choose a file.", "danger")
            return redirect(url_for('admin.gallery'))
            
        file_type = 'images'
        if file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS.get('videos'):
            file_type = 'videos'
            
        if not allowed_file(file.filename, file_type):
            flash("Unsupported media format.", "danger")
            return redirect(url_for('admin.gallery'))
            
        rel_path = save_uploaded_file(file, Config.GALLERY_FOLDER)
        
        new_media = Gallery(
            title=title,
            category=category,
            type='Photo' if file_type == 'images' else 'Video',
            file_path=rel_path
        )
        db.session.add(new_media)
        db.session.commit()
        log_audit("Upload Gallery Media", f"Uploaded media: {title}")
        flash("Media uploaded to gallery!", "success")
        return redirect(url_for('admin.gallery'))
        
    items = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('admin/gallery.html', items=items)

@admin_bp.route('/gallery/delete/<int:item_id>', methods=['POST'])
@admin_required
def delete_gallery_item(item_id):
    item = Gallery.query.get_or_404(item_id)
    log_audit("Delete Gallery Media", f"Deleted gallery item: {item.title}")
    db.session.delete(item)
    db.session.commit()
    flash("Gallery item deleted.", "success")
    return redirect(url_for('admin.gallery'))

# DOWNLOADS CRUD
@admin_bp.route('/downloads', methods=['GET', 'POST'])
@admin_required
def downloads():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        file = request.files.get('file')
        
        if not file or file.filename == '':
            flash("Please choose a file.", "danger")
            return redirect(url_for('admin.downloads'))
            
        if not allowed_file(file.filename, 'documents') and not allowed_file(file.filename, 'images'):
            flash("Unsupported document format.", "danger")
            return redirect(url_for('admin.downloads'))
            
        rel_path = save_uploaded_file(file, Config.DOWNLOADS_FOLDER)
        
        new_doc = Download(
            title=title,
            category=category,
            file_path=rel_path
        )
        db.session.add(new_doc)
        db.session.commit()
        log_audit("Upload Download File", f"Uploaded attachment: {title}")
        flash("Document uploaded successfully!", "success")
        return redirect(url_for('admin.downloads'))
        
    docs = Download.query.order_by(Download.upload_date.desc()).all()
    return render_template('admin/downloads.html', docs=docs)

@admin_bp.route('/downloads/delete/<int:doc_id>', methods=['POST'])
@admin_required
def delete_download(doc_id):
    doc = Download.query.get_or_404(doc_id)
    log_audit("Delete Download File", f"Deleted attachment: {doc.title}")
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted.", "success")
    return redirect(url_for('admin.downloads'))

# USER MANAGEMENT
@admin_bp.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    # Enforce Super Admin Check
    admin_id = int(current_user.get_id().split('_')[1])
    current_admin = Admin.query.get(admin_id)
    if current_admin.role != 'super_admin':
        flash("Only Super Administrators can access user management.", "danger")
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'staff')
        
        if Admin.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('admin.users'))
            
        new_admin = Admin(
            username=username,
            email=email,
            role=role
        )
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        log_audit("Create Admin User", f"Created admin account: {username}")
        flash(f"Administrator {username} created successfully!", "success")
        return redirect(url_for('admin.users'))
        
    admins_list = Admin.query.all()
    return render_template('admin/users.html', admins=admins_list)

@admin_bp.route('/users/reset-password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    current_admin_id = int(current_user.get_id().split('_')[1])
    current_admin = Admin.query.get(current_admin_id)
    if current_admin.role != 'super_admin':
        flash("Unauthorized action.", "danger")
        return redirect(url_for('admin.dashboard'))
        
    target_admin = Admin.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    target_admin.set_password(new_password)
    db.session.commit()
    log_audit("Reset Admin Password", f"Reset password for administrator: {target_admin.username}")
    flash(f"Password for {target_admin.username} reset successfully.", "success")
    return redirect(url_for('admin.users'))

# REPORTS AND EXPORTS
@admin_bp.route('/reports')
@admin_required
def reports():
    return render_template('admin/reports.html')

@admin_bp.route('/reports/export/<format_type>/<report_category>')
@admin_required
def export_report(format_type, report_category):
    # Fetch Data
    data = []
    columns = []
    filename = f"{report_category}_report_{datetime.now().strftime('%Y%m%d')}"
    
    if report_category == 'admissions':
        items = Admission.query.all()
        columns = ['ID', 'Student Name', 'Email', 'Mobile', 'District', 'State', '10th %', '12th %', 'Status', 'Applied Date']
        data = [[
            i.id, i.full_name, i.email, i.mobile, i.district, i.state, 
            i.tenth_percentage, i.twelfth_percentage, i.status, 
            i.created_at.strftime('%Y-%m-%d')
        ] for i in items]
        
    elif report_category == 'events':
        items = EventRegistration.query.all()
        columns = ['Reg ID', 'Event Name', 'Student Name', 'USN', 'Semester', 'Email', 'Payment Status', 'Amt Paid', 'Date']
        data = [[
            i.id, i.event.name, i.name, i.usn, i.semester, i.email, 
            i.payment_status, i.amount_paid, i.registered_at.strftime('%Y-%m-%d')
        ] for i in items]
        
    elif report_category == 'revenue':
        items = Payment.query.filter_by(payment_status='Success').all()
        columns = ['Payment ID', 'Type', 'Ref ID', 'Transaction ID', 'Amount (Rs)', 'Method', 'Payment Date']
        data = [[
            i.id, i.type, i.reference_id, i.transaction_id, i.amount, 
            i.payment_method, i.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ] for i in items]
        
    elif report_category == 'placements':
        items = Placement.query.all()
        columns = ['ID', 'Student Name', 'Company Name', 'Package (LPA)', 'Designation', 'Graduation Year']
        data = [[
            i.id, i.student_name, i.company_name, i.package_lpa, i.designation, i.graduation_year
        ] for i in items]
        
    elif report_category == 'students':
        items = Student.query.all()
        columns = ['ID', 'Username', 'Email', 'Name', 'USN', 'Semester', 'Registered Date']
        data = [[
            i.id, i.username, i.email, i.full_name or 'N/A', i.usn or 'N/A', 
            i.semester, i.created_at.strftime('%Y-%m-%d')
        ] for i in items]
        
    else:
        flash("Invalid report category specified.", "danger")
        return redirect(url_for('admin.reports'))

    # Process Format Type
    if format_type == 'excel':
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Report'
        
        # Write headers
        ws.append(columns)
        
        # Write data rows
        for row in data:
            ws.append(row)
            
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"{filename}.xlsx"
        )
        
    elif format_type == 'pdf':
        output = BytesIO()
        # Landscape orientation for wide tables
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor("#0f4c81"),
            spaceAfter=15,
            alignment=1
        )
        
        table_text_style = ParagraphStyle(
            'TableText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10
        )
        
        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.white,
            leading=10
        )
        
        story = []
        story.append(Paragraph(f"BCA Department - {report_category.capitalize()} Report", title_style))
        story.append(Paragraph(f"Generated Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Prepare structured data tables
        table_data = []
        # Header Row
        table_data.append([Paragraph(col, table_header_style) for col in columns])
        
        # Content Rows
        for row in data:
            row_data = []
            for cell in row:
                row_data.append(Paragraph(str(cell), table_text_style))
            table_data.append(row_data)
            
        report_table = Table(table_data)
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f4c81")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ]))
        
        story.append(report_table)
        doc.build(story)
        output.seek(0)
        
        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{filename}.pdf"
        )
        
    else:
        flash("Unsupported report format.", "danger")
        return redirect(url_for('admin.reports'))

# COURSES (SYLLABUS) CRUD
@admin_bp.route('/courses', methods=['GET', 'POST'])
@admin_required
def courses():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        credits = int(request.form.get('credits', 4))
        outcomes = request.form.get('outcomes')
        semester = int(request.form.get('semester', 1))
        
        if Course.query.filter_by(code=code).first():
            flash("Course code already exists.", "danger")
            return redirect(url_for('admin.courses'))
            
        new_course = Course(
            code=code,
            name=name,
            credits=credits,
            outcomes=outcomes,
            semester=semester
        )
        db.session.add(new_course)
        db.session.commit()
        log_audit("Add Course", f"Added course {code}: {name}")
        flash("Course added successfully!", "success")
        return redirect(url_for('admin.courses'))
        
    courses_list = Course.query.order_by(Course.semester.asc(), Course.code.asc()).all()
    return render_template('admin/courses.html', courses=courses_list)

@admin_bp.route('/courses/edit/<int:course_id>', methods=['POST'])
@admin_required
def edit_course(course_id):
    c = Course.query.get_or_404(course_id)
    c.code = request.form.get('code')
    c.name = request.form.get('name')
    c.credits = int(request.form.get('credits', 4))
    c.outcomes = request.form.get('outcomes')
    c.semester = int(request.form.get('semester', 1))
    
    db.session.commit()
    log_audit("Edit Course", f"Modified details of course: {c.code}")
    flash("Course updated successfully!", "success")
    return redirect(url_for('admin.courses'))

@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@admin_required
def delete_course(course_id):
    c = Course.query.get_or_404(course_id)
    log_audit("Delete Course", f"Deleted course: {c.code}")
    db.session.delete(c)
    db.session.commit()
    flash("Course deleted successfully!", "success")
    return redirect(url_for('admin.courses'))

# CAREERS CRUD
@admin_bp.route('/careers', methods=['GET', 'POST'])
@admin_required
def careers():
    if request.method == 'POST':
        action_type = request.form.get('action_type') # opportunity or education
        
        if action_type == 'opportunity':
            title = request.form.get('title')
            desc = request.form.get('description')
            demand = request.form.get('demand', 'High')
            
            new_opp = CareerOpportunity(title=title, description=desc, demand=demand)
            db.session.add(new_opp)
            db.session.commit()
            log_audit("Add Career Opportunity", f"Added job profile: {title}")
            flash("Career opportunity added!", "success")
            
        elif action_type == 'education':
            name = request.form.get('name')
            dur = request.form.get('duration', '2 Years')
            desc = request.form.get('description')
            
            new_edu = HigherEducation(name=name, duration=dur, description=desc)
            db.session.add(new_edu)
            db.session.commit()
            log_audit("Add Higher Education", f"Added pg path: {name}")
            flash("Higher education program added!", "success")
            
        return redirect(url_for('admin.careers'))
        
    opps = CareerOpportunity.query.order_by(CareerOpportunity.id.asc()).all()
    edu = HigherEducation.query.order_by(HigherEducation.id.asc()).all()
    return render_template('admin/careers.html', opportunities=opps, higher_edu=edu)

@admin_bp.route('/careers/opportunity/edit/<int:opp_id>', methods=['POST'])
@admin_required
def edit_opportunity(opp_id):
    opp = CareerOpportunity.query.get_or_404(opp_id)
    opp.title = request.form.get('title')
    opp.description = request.form.get('description')
    opp.demand = request.form.get('demand')
    
    db.session.commit()
    log_audit("Edit Career Opportunity", f"Modified job profile: {opp.title}")
    flash("Career opportunity updated!", "success")
    return redirect(url_for('admin.careers'))

@admin_bp.route('/careers/opportunity/delete/<int:opp_id>', methods=['POST'])
@admin_required
def delete_opportunity(opp_id):
    opp = CareerOpportunity.query.get_or_404(opp_id)
    log_audit("Delete Career Opportunity", f"Deleted job profile: {opp.title}")
    db.session.delete(opp)
    db.session.commit()
    flash("Career opportunity deleted.", "success")
    return redirect(url_for('admin.careers'))

@admin_bp.route('/careers/education/edit/<int:edu_id>', methods=['POST'])
@admin_required
def edit_education(edu_id):
    edu = HigherEducation.query.get_or_404(edu_id)
    edu.name = request.form.get('name')
    edu.duration = request.form.get('duration')
    edu.description = request.form.get('description')
    
    db.session.commit()
    log_audit("Edit Higher Education", f"Modified pg path: {edu.name}")
    flash("Higher education program updated!", "success")
    return redirect(url_for('admin.careers'))

@admin_bp.route('/careers/education/delete/<int:edu_id>', methods=['POST'])
@admin_required
def delete_education(edu_id):
    edu = HigherEducation.query.get_or_404(edu_id)
    log_audit("Delete Higher Education", f"Deleted pg path: {edu.name}")
    db.session.delete(edu)
    db.session.commit()
    flash("Higher education program deleted.", "success")
    return redirect(url_for('admin.careers'))

# STUDENT PROJECTS CRUD
@admin_bp.route('/projects', methods=['GET', 'POST'])
@admin_required
def projects():
    if request.method == 'POST':
        title = request.form.get('title')
        tech = request.form.get('tech')
        desc = request.form.get('description')
        github = request.form.get('github_url')
        
        new_proj = StudentProject(
            title=title,
            tech=tech,
            description=desc,
            github_url=github
        )
        db.session.add(new_proj)
        db.session.commit()
        log_audit("Add Student Project", f"Registered project: {title}")
        flash("Student project registered successfully!", "success")
        return redirect(url_for('admin.projects'))
        
    projects_list = StudentProject.query.order_by(StudentProject.created_at.desc()).all()
    return render_template('admin/projects.html', student_projects=projects_list)

@admin_bp.route('/projects/edit/<int:proj_id>', methods=['POST'])
@admin_required
def edit_project(proj_id):
    proj = StudentProject.query.get_or_404(proj_id)
    proj.title = request.form.get('title')
    proj.tech = request.form.get('tech')
    proj.description = request.form.get('description')
    proj.github_url = request.form.get('github_url')
    
    db.session.commit()
    log_audit("Edit Student Project", f"Modified project: {proj.title}")
    flash("Student project updated successfully!", "success")
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/delete/<int:proj_id>', methods=['POST'])
@admin_required
def delete_project(proj_id):
    proj = StudentProject.query.get_or_404(proj_id)
    log_audit("Delete Student Project", f"Deleted project registry: {proj.title}")
    db.session.delete(proj)
    db.session.commit()
    flash("Student project record deleted.", "success")
    return redirect(url_for('admin.projects'))
