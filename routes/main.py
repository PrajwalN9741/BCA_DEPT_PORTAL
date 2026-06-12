import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from models import db, Faculty, Event, News, Placement, Alumni, Gallery, Download, ContactMessage, Course, CareerOpportunity, HigherEducation, StudentProject

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    # Load data for homepage components
    latest_news = News.query.order_by(News.created_at.desc()).limit(3).all()
    upcoming_events = Event.query.order_by(Event.date.asc()).limit(2).all()
    placements = Placement.query.order_by(Placement.created_at.desc()).limit(5).all()
    testimonials = Alumni.query.order_by(Alumni.created_at.desc()).limit(3).all()
    gallery_preview = Gallery.query.order_by(Gallery.created_at.desc()).limit(6).all()
    
    # Static facts (can also be read from site_settings)
    stats = {
        'students': 450,
        'faculty': 12,
        'placements': 92,
        'labs': 4
    }
    
    return render_template(
        'main/home.html',
        latest_news=latest_news,
        upcoming_events=upcoming_events,
        placements=placements,
        testimonials=testimonials,
        gallery_preview=gallery_preview,
        stats=stats
    )

@main_bp.route('/about')
def about():
    # Highlights list can be split by lines
    achievements = [
        "Recipient of best technical department award 2025.",
        "Over 50 research publications by faculty members in standard journals.",
        "100% of final year students underwent corporate internships in 2025."
    ]
    return render_template('main/about.html', achievements=achievements)

@main_bp.route('/faculty')
def faculty_list():
    faculties = Faculty.query.all()
    return render_template('main/faculty.html', faculties=faculties)

@main_bp.route('/courses')
def courses():
    courses_list = Course.query.order_by(Course.semester.asc(), Course.code.asc()).all()
    curriculum = {}
    for c in courses_list:
        if c.semester not in curriculum:
            curriculum[c.semester] = []
        curriculum[c.semester].append({
            "code": c.code,
            "name": c.name,
            "credits": c.credits,
            "outcomes": c.outcomes
        })
    return render_template('main/courses.html', curriculum=curriculum)

@main_bp.route('/careers')
def careers():
    opportunities = CareerOpportunity.query.order_by(CareerOpportunity.id.asc()).all()
    higher_edu = HigherEducation.query.order_by(HigherEducation.id.asc()).all()
    return render_template('main/careers.html', opportunities=opportunities, higher_edu=higher_edu)

@main_bp.route('/projects')
def projects():
    student_projects = StudentProject.query.order_by(StudentProject.created_at.desc()).all()
    return render_template('main/projects.html', student_projects=student_projects)

@main_bp.route('/gallery')
def gallery():
    gallery_items = Gallery.query.order_by(Gallery.created_at.desc()).all()
    categories = list(set([item.category for item in gallery_items]))
    return render_template('main/gallery.html', gallery_items=gallery_items, categories=categories)

@main_bp.route('/downloads')
def downloads():
    download_files = Download.query.order_by(Download.upload_date.desc()).all()
    return render_template('main/downloads.html', download_files=download_files)

@main_bp.route('/downloads/<int:file_id>')
def download_file(file_id):
    dl = Download.query.get_or_404(file_id)
    # Get base directory
    base_dir = os.path.dirname(current_app.config['UPLOAD_FOLDER'])
    file_path = os.path.join(base_dir, dl.file_path)
    
    if os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        flash("Request file not found on server.", "danger")
        return redirect(url_for('main.downloads'))

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not name or not email or not subject or not message:
            flash("All fields are mandatory.", "danger")
            return redirect(url_for('main.contact'))
            
        new_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()
        
        flash("Your message has been submitted successfully! We will contact you shortly.", "success")
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html')
