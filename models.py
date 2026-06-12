from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')  # super_admin, staff
    permissions = db.Column(db.Text, nullable=True)     # comma separated permissions e.g., 'edit_home,edit_faculty'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_id(self):
        return f"admin_{self.id}"

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    usn = db.Column(db.String(20), unique=True, nullable=True)
    semester = db.Column(db.Integer, default=1)
    mobile = db.Column(db.String(15), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admissions = db.relationship('Admission', backref='student', lazy=True)
    registrations = db.relationship('EventRegistration', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_id(self):
        return f"student_{self.id}"

class Admission(db.Model):
    __tablename__ = 'admissions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Personal Info
    full_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    aadhaar_number = db.Column(db.String(12), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    
    # Address
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    
    # Academic Info
    tenth_percentage = db.Column(db.Float, nullable=False)
    twelfth_percentage = db.Column(db.Float, nullable=False)
    board_details = db.Column(db.String(100), nullable=False)
    previous_degree = db.Column(db.String(50), nullable=True) # e.g. 12th/PUC/Diploma
    course = db.Column(db.String(50), default='BCA')
    
    # Document Uploads (Paths)
    photo_path = db.Column(db.String(255), nullable=False)
    signature_path = db.Column(db.String(255), nullable=False)
    aadhaar_path = db.Column(db.String(255), nullable=False)
    tenth_marks_path = db.Column(db.String(255), nullable=False)
    twelfth_marks_path = db.Column(db.String(255), nullable=False)
    tc_path = db.Column(db.String(255), nullable=False)
    
    # Status & Payment
    status = db.Column(db.String(30), default='Pending Payment') # Pending Payment, Paid, Approved, Rejected
    transaction_id = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    amount_paid = db.Column(db.Float, default=0.0)
    receipt_number = db.Column(db.String(50), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False) # In years
    specialization = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    linkedin = db.Column(db.String(255), nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster_path = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    registration_fee = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Registration Info
    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    
    # Payment Info
    payment_status = db.Column(db.String(20), default='Pending') # Pending, Paid
    payment_method = db.Column(db.String(50), nullable=True)
    transaction_id = db.Column(db.String(100), nullable=True)
    amount_paid = db.Column(db.Float, default=0.0)
    receipt_number = db.Column(db.String(50), unique=True, nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False) # Admission, Event
    reference_id = db.Column(db.Integer, nullable=False) # admission_id or event_registration_id
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # UPI, Debit Card, Credit Card, Net Banking
    payment_status = db.Column(db.String(20), default='Success')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    qrcode_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    payment = db.relationship('Payment', backref=db.backref('receipts', lazy=True))

class Placement(db.Model):
    __tablename__ = 'placements'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    package_lpa = db.Column(db.Float, nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    placement_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alumni(db.Model):
    __tablename__ = 'alumni'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    testimonial = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Gallery(db.Model):
    __tablename__ = 'gallery'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), default='Photo') # Photo, Video
    category = db.Column(db.String(50), nullable=False) # Activity, Workshop, Cultural, Event
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Download(db.Model):
    __tablename__ = 'downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Syllabus, Time Table, Academic Calendar, Notes, Question Paper, Form, Placement
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False) # Circular, Notice, Exam, Placement, Announcement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Unread') # Read, Unread
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WebsiteSetting(db.Model):
    __tablename__ = 'website_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20), nullable=False) # Admin, Student, Guest
    user_id = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(100), nullable=False) # e.g. Login, Update Course, Approve Admission
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=4)
    outcomes = db.Column(db.Text, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CareerOpportunity(db.Model):
    __tablename__ = 'career_opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    demand = db.Column(db.String(50), nullable=False, default='High') # High, Very High, Critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HigherEducation(db.Model):
    __tablename__ = 'higher_education'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    duration = db.Column(db.String(50), nullable=False, default='2 Years')
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentProject(db.Model):
    __tablename__ = 'student_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    tech = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    github_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
