import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db, Admin, Faculty, Event, News, Download, WebsiteSetting, Placement, Alumni, Gallery, Course, CareerOpportunity, HigherEducation, StudentProject

def init_db():
    app = create_app()
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created successfully.")

        # 1. Create Upload Directories
        upload_dirs = [
            app.config['FACULTY_FOLDER'],
            app.config['DOCUMENTS_FOLDER'],
            app.config['EVENTS_FOLDER'],
            app.config['GALLERY_FOLDER'],
            app.config['DOWNLOADS_FOLDER'],
            app.config['RECEIPTS_FOLDER']
        ]
        for directory in upload_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"Directory verified: {directory}")

        # 2. Seed Website Settings
        settings = {
            'welcome_title': 'Welcome to the BCA Department',
            'welcome_text': 'Empowering students with theoretical foundations and practical skills in computer applications, programming, and emerging digital technologies.',
            'vision_statement': 'To be a premier center of computer applications education, fostering innovation, analytical thinking, and ethical professional values to meet global industrial demands.',
            'mission_statement': 'To provide state-of-the-art infrastructure and high-quality computer applications education. To bridge the gap between academia and industry through hands-on practice, workshops, and internship collaborations. To instil professional ethics, leadership qualities, and lifelong learning capabilities.',
            'department_highlights': '100% Placement assistance with top MNC partners. State-of-the-art computer labs with high-speed internet. Industry-aligned curriculum with specializations in AI/ML, Cloud, and Cybersecurity. Dynamic student development programs and technical fests.',
            'contact_email': 'bca.admissions@college.edu',
            'contact_phone': '+91 80 4123 4567',
            'contact_address': 'Department of Computer Applications, Block C, Main Campus, Palace Road, Bengaluru, Karnataka - 560001',
            'google_maps_url': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3887.9268686616086!2d77.5875!3d12.975!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae1670c9b44e6d%3A0xf612b719468504!2sBengaluru%2C%20Karnataka!5e0!3m2!1sen!2sin!4v1620000000000!5m2!1sen!2sin',
            'admission_fee': '45000.00'
        }
        
        for k, v in settings.items():
            if not WebsiteSetting.query.filter_by(key=k).first():
                db.session.add(WebsiteSetting(key=k, value=v))
        
        # 3. Seed Super Admin User
        if not Admin.query.filter_by(username='admin').first():
            super_admin = Admin(
                username='admin',
                email='admin@college.edu',
                role='super_admin'
            )
            super_admin.set_password('adminpassword')
            db.session.add(super_admin)
            print("Default admin user created (admin / adminpassword).")

        # 4. Seed Faculty Members
        if Faculty.query.count() == 0:
            faculties = [
                Faculty(
                    name="Dr. Raghavendra Rao",
                    qualification="Ph.D in Computer Science, M.Tech (CS)",
                    designation="Professor & Head of Department",
                    experience=18,
                    specialization="Artificial Intelligence, Machine Learning & Database Systems",
                    email="hod.bca@college.edu",
                    mobile="9876543210",
                    linkedin="https://linkedin.com/in/dummy-hod-bca",
                    photo_path="static/uploads/faculty/faculty1.jpg"
                ),
                Faculty(
                    name="Dr. Shalini Kumari",
                    qualification="Ph.D in Cybersecurity, MCA",
                    designation="Associate Professor",
                    experience=12,
                    specialization="Cybersecurity, Cryptography, and Computer Networks",
                    email="shalini.k@college.edu",
                    mobile="9876543211",
                    linkedin="https://linkedin.com/in/dummy-shalini-bca",
                    photo_path="static/uploads/faculty/faculty2.jpg"
                ),
                Faculty(
                    name="Prof. Praveen Kumar",
                    qualification="M.Tech in Software Engineering, B.E (CSE)",
                    designation="Assistant Professor",
                    experience=8,
                    specialization="Full Stack Web Technologies, Java, and Software Engineering",
                    email="praveen.k@college.edu",
                    mobile="9876543212",
                    linkedin="https://linkedin.com/in/dummy-praveen-bca",
                    photo_path="static/uploads/faculty/faculty3.jpg"
                )
            ]
            db.session.add_all(faculties)
            
            # Write dummy text files as placeholders for faculty pictures
            for i, f in enumerate(faculties, 1):
                f_photo = os.path.join(app.config['BASE_DIR'], f.photo_path)
                os.makedirs(os.path.dirname(f_photo), exist_ok=True)
                with open(f_photo, "w") as fp:
                    fp.write(f"Faculty Photo {i}")
            print("Faculty seeded.")

        # 5. Seed Events
        if Event.query.count() == 0:
            now = datetime.utcnow()
            events = [
                Event(
                    name="National Level BCA Hackathon 2026",
                    description="An intense 24-hour coding hackathon focusing on solving real-world challenges in healthcare, education, and finance. Win attractive cash prizes up to Rs. 50,000!",
                    date=now + timedelta(days=15),
                    venue="BCA Seminar Hall & Main CS Lab",
                    registration_fee=250.0,
                    deadline=now + timedelta(days=12),
                    poster_path="static/uploads/events/hackathon.jpg"
                ),
                Event(
                    name="Workshop on Full-Stack Next.js Applications",
                    description="Hands-on workshop detailing React server components, API routing, Tailwind CSS integrations, and deployment on Vercel.",
                    date=now + timedelta(days=25),
                    venue="Advanced Computing Lab",
                    registration_fee=0.0,  # Free
                    deadline=now + timedelta(days=22),
                    poster_path="static/uploads/events/nextjs_workshop.jpg"
                )
            ]
            db.session.add_all(events)
            
            # Write dummy event poster files
            for e in events:
                e_poster = os.path.join(app.config['BASE_DIR'], e.poster_path)
                os.makedirs(os.path.dirname(e_poster), exist_ok=True)
                with open(e_poster, "w") as fp:
                    fp.write("Event Poster Placeholder")
            print("Events seeded.")

        # 6. Seed News & Announcements
        if News.query.count() == 0:
            news_items = [
                News(
                    title="BCA Odd Semester Main Examinations June 2026 - Time Table Released",
                    content="The examination timetable for 1st, 3rd, and 5th-semester students has been officially declared. Exams start on June 22, 2026. Hall tickets can be collected from the department coordinator from June 15, 2026 onwards.",
                    category="Exam"
                ),
                News(
                    title="Campus Placement Drive by Amazon India for BCA Graduates",
                    content="Amazon is organizing a placement drive for final-year BCA students. Profile: Associate Software Developer. Highest salary package is up to Rs. 8.5 LPA. Register before June 15 on the placement portal.",
                    category="Placement"
                ),
                News(
                    title="Orientation Program for Newly Admitted BCA Students (Batch 2026-29)",
                    content="The welcome orientation and departmental tour for newly admitted BCA batch is scheduled on August 1, 2026 at the College auditorium. Parents are welcome.",
                    category="Announcement"
                )
            ]
            db.session.add_all(news_items)
            print("News/Announcements seeded.")

        # 7. Seed Placement Records
        if Placement.query.count() == 0:
            placements = [
                Placement(student_name="Rahul Roy", company_name="Infosys", package_lpa=4.2, designation="Systems Associate", graduation_year=2025),
                Placement(student_name="Sneha M.", company_name="Amazon", package_lpa=8.5, designation="Cloud Operations Intern", graduation_year=2025),
                Placement(student_name="Karthik N.", company_name="Cognizant", package_lpa=4.0, designation="Programmer Analyst Trainee", graduation_year=2025),
                Placement(student_name="Maria Joseph", company_name="Wipro", package_lpa=3.8, designation="Scholar Trainee (WIMS)", graduation_year=2024),
                Placement(student_name="Arjun V.", company_name="TCS", package_lpa=3.6, designation="Graduate Engineer", graduation_year=2024)
            ]
            db.session.add_all(placements)
            print("Placement stats seeded.")

        # 8. Seed Alumni Testimonials
        if Alumni.query.count() == 0:
            alumni_records = [
                Alumni(
                    name="Rohan Gupta",
                    company="Google",
                    position="Software Engineer",
                    graduation_year=2022,
                    testimonial="The BCA program provided a solid base. The hands-on project work in my final year paved the path for my coding interview success. The faculty support was exceptional.",
                    photo_path="static/uploads/gallery/alumni1.jpg"
                ),
                Alumni(
                    name="Deepika Sharma",
                    company="Deloitte",
                    position="Technology Consultant",
                    graduation_year=2023,
                    testimonial="Dynamic guest lectures and tech fests in the department built my communication skills and boosted my confidence. Truly the best phase of my academic career.",
                    photo_path="static/uploads/gallery/alumni2.jpg"
                )
            ]
            db.session.add_all(alumni_records)
            
            # Write dummy alumni images
            for al in alumni_records:
                al_img = os.path.join(app.config['BASE_DIR'], al.photo_path)
                os.makedirs(os.path.dirname(al_img), exist_ok=True)
                with open(al_img, "w") as fp:
                    fp.write("Alumni photo placeholder")
            print("Alumni seeded.")

        # 9. Seed Downloadable documents
        if Download.query.count() == 0:
            downloads = [
                Download(title="BCA 2026-2029 Syllabus & Credits", category="Syllabus", file_path="static/uploads/downloads/bca_syllabus_2026.pdf"),
                Download(title="Academic Calendar 2026 (Odd Semester)", category="Academic Calendar", file_path="static/uploads/downloads/academic_calendar_2026.pdf"),
                Download(title="BCA 4th & 6th Sem Exam Time Table June 2026", category="Time Table", file_path="static/uploads/downloads/timetable_june2026.pdf")
            ]
            db.session.add_all(downloads)
            
            # Write dummy download files
            for dl in downloads:
                dl_file = os.path.join(app.config['BASE_DIR'], dl.file_path)
                os.makedirs(os.path.dirname(dl_file), exist_ok=True)
                with open(dl_file, "w") as fp:
                    fp.write(f"This is the official downloaded document content for {dl.title}.")
            print("Downloads seeded.")

        # 10. Seed Photo Gallery
        if Gallery.query.count() == 0:
            gallery_items = [
                Gallery(title="BCA Coding Competition 2025", category="Activity", file_path="static/uploads/gallery/g1.jpg"),
                Gallery(title="AI & Deep Learning Seminar", category="Workshop", file_path="static/uploads/gallery/g2.jpg"),
                Gallery(title="Department Annual Fest (Bytes 2025)", category="Cultural", file_path="static/uploads/gallery/g3.jpg")
            ]
            db.session.add_all(gallery_items)
            
            # Write dummy gallery files
            for g in gallery_items:
                g_file = os.path.join(app.config['BASE_DIR'], g.file_path)
                os.makedirs(os.path.dirname(g_file), exist_ok=True)
                with open(g_file, "w") as fp:
                    fp.write("Gallery image placeholder")
            print("Gallery seeded.")

        # 11. Seed Syllabus Courses
        if Course.query.count() == 0:
            courses = [
                # Semester 1
                Course(code="BCA101T", name="Programming in C", credits=4, semester=1, outcomes="Understand structural programming logic and basic data types."),
                Course(code="BCA102T", name="Digital Electronics", credits=4, semester=1, outcomes="Understand logic gates, Boolean algebra and sequential circuits."),
                Course(code="BCA103T", name="Mathematics", credits=4, semester=1, outcomes="Master matrix algebra, calculus and logical relations."),
                Course(code="BCA104T", name="Communication Skills", credits=2, semester=1, outcomes="Express technical details eloquently in written and oral forms."),
                # Semester 2
                Course(code="BCA201T", name="Data Structures", credits=4, semester=2, outcomes="Design algorithms using arrays, stacks, queues, trees and graphs."),
                Course(code="BCA202T", name="Operating Systems", credits=4, semester=2, outcomes="Learn process scheduling, memory virtualization, and file allocation."),
                Course(code="BCA203T", name="Database Management Systems", credits=4, semester=2, outcomes="Learn database design, normalizations, and transaction management via SQL."),
                # Semester 3
                Course(code="BCA301T", name="Java Programming", credits=4, semester=3, outcomes="Master OOP principles, multi-threading, exceptions and GUI designs in Java."),
                Course(code="BCA302T", name="Computer Networks", credits=4, semester=3, outcomes="Understand OSI/TCP layers, routing, and data communication security."),
                Course(code="BCA303T", name="Web Technologies", credits=4, semester=3, outcomes="Build responsive frontend UIs using HTML, CSS, JavaScript, and Bootstrap."),
                # Semester 4
                Course(code="BCA401T", name="Python Programming", credits=4, semester=4, outcomes="Gain hands-on experience in scripting, file parsing, OOP, and data analytics."),
                Course(code="BCA402T", name="Software Engineering", credits=4, semester=4, outcomes="Study agile lifecycles, UML modeling, modular styling, and software testing."),
                Course(code="BCA403T", name="Open Source Tools", credits=2, semester=4, outcomes="Acquire familiarity with Git, Linux environments, shell commands, and docker."),
                # Semester 5
                Course(code="BCA501T", name="Machine Learning", credits=4, semester=5, outcomes="Analyze classifications, linear regressions, and clustering algorithms using scikit-learn."),
                Course(code="BCA502T", name="Cloud Computing", credits=4, semester=5, outcomes="Learn about virtualization, AWS services, storage architectures, and SaaS configs."),
                Course(code="BCA503T", name="Cyber Security", credits=4, semester=5, outcomes="Explore network threat modeling, firewalls, and application level security."),
                # Semester 6
                Course(code="BCA601P", name="Project Work", credits=6, semester=6, outcomes="Apply complete SDLC methodologies to construct a full-scale working prototype."),
                Course(code="BCA602P", name="Internship", credits=4, semester=6, outcomes="Acquire exposure to collaborative development environments and industrial routines."),
                Course(code="BCA603T", name="Emerging Technologies", credits=2, semester=6, outcomes="Review developments in Blockchain, Generative AI, IoT, and Web3.")
            ]
            db.session.add_all(courses)
            print("Syllabus Courses seeded.")

        # 12. Seed Career Opportunities & Higher Education
        if CareerOpportunity.query.count() == 0:
            opps = [
                CareerOpportunity(title="Software Developer", description="Write and maintain robust applications across diverse hardware targets.", demand="High"),
                CareerOpportunity(title="Python Developer", description="Develop backend server architectures, data scraper scripts, and automation pipelines.", demand="Very High"),
                CareerOpportunity(title="Java Developer", description="Construct high-availability enterprise backend architectures using Spring Boot.", demand="High"),
                CareerOpportunity(title="Web Developer", description="Design user-friendly client web dashboards using modern frameworks.", demand="High"),
                CareerOpportunity(title="Full Stack Developer", description="Own end-to-end features spanning databases, backend routes, and frontend views.", demand="Critical"),
                CareerOpportunity(title="Data Analyst", description="Extract mathematical business insights and draw charts using Pandas and SQL.", demand="High"),
                CareerOpportunity(title="Database Administrator", description="Ensure high availability, schema structure performance, and backup security.", demand="Medium"),
                CareerOpportunity(title="Network Engineer", description="Manage routing tables, domain controllers, subnet structures, and secure gateways.", demand="Medium"),
                CareerOpportunity(title="Cyber Security Analyst", description="Probe software setups for bugs, monitor server access, and defend infrastructure.", demand="Critical"),
                CareerOpportunity(title="Cloud Engineer", description="Maintain scalable AWS/GCP resources, Kubernetes nodes, and container systems.", demand="Very High"),
                CareerOpportunity(title="AI/ML Engineer", description="Train, tune, and deploy deep learning models to process computer vision and text.", demand="Critical"),
                CareerOpportunity(title="DevOps Engineer", description="Manage CI/CD build scripts, automated unit checks, and web server runtimes.", demand="Very High"),
                CareerOpportunity(title="UI/UX Developer", description="Draft interactive user mockups and style systems based on usability guidelines.", demand="High"),
                CareerOpportunity(title="Mobile App Developer", description="Build responsive native and cross-platform layouts for iOS and Android.", demand="High")
            ]
            db.session.add_all(opps)
            print("Career opportunities seeded.")
            
        if HigherEducation.query.count() == 0:
            edu = [
                HigherEducation(name="MCA (Master of Computer Applications)", duration="2 Years", description="The natural progression offering specialization in advanced software frameworks."),
                HigherEducation(name="MBA (Master of Business Administration)", duration="2 Years", description="Fuses technical expertise with marketing, project management, and startup operations."),
                HigherEducation(name="M.Sc Computer Science", duration="2 Years", description="Research-oriented path focus on algorithmic math and deep scientific computation."),
                HigherEducation(name="PG Diploma Programs", duration="1 Year", description="Short vocational paths specializing in specific branches like Cyber Security or Data Science.")
            ]
            db.session.add_all(edu)
            print("Higher Education paths seeded.")

        # 13. Seed Student Projects
        if StudentProject.query.count() == 0:
            projects = [
                StudentProject(title="Student Performance Prediction", tech="Machine Learning (Python, Scikit-learn)", description="Predicts semester marks based on demographic, class attendance, and study hours details.", github_url="https://github.com/dummy/student-perf"),
                StudentProject(title="College Website Management System", tech="Flask, SQLite, HTML5, JavaScript", description="CMS system enabling academic deans to publish updates and manage syllabus dynamic models.", github_url="https://github.com/dummy/college-web"),
                StudentProject(title="Event Management System", tech="React, Node.js, MongoDB", description="College events scheduler with ticketing integration, QR checkpoints, and venue allocation algorithms.", github_url="https://github.com/dummy/event-mgr"),
                StudentProject(title="Healthcare Management System", tech="Java Spring Boot, MySQL, Thymeleaf", description="Hospital record system supporting patient appointment booking, doctor schedules, and billing.", github_url="https://github.com/dummy/health-sys"),
                StudentProject(title="ShareWeb Social Media Platform", tech="Django, Postgres, React", description="Collaborative social system where computer graduates share projects, reviews, and host chats.", github_url="https://github.com/dummy/share-web"),
                StudentProject(title="E-Commerce Website", tech="MERN Stack", description="Online storefront with product catalogs, shopping cart logic, search indexes, and Stripe gateway.", github_url="https://github.com/dummy/ecommerce"),
                StudentProject(title="Train Simulator Project", tech="C++, OpenGL", description="Computer graphics emulation of a rail transit line displaying physical movement and day/night shaders.", github_url="https://github.com/dummy/train-sim"),
                StudentProject(title="Student Portal Management System", tech="Flask, MySQL, CSS3", description="Comprehensive tracking board enabling students to inspect credits, mark sheets, and assignments.", github_url="https://github.com/dummy/stud-portal")
            ]
            db.session.add_all(projects)
            print("Student Projects seeded.")

        db.session.commit()
        print("All database records seeded successfully!")

if __name__ == '__main__':
    init_db()
