import os
import unittest
from datetime import datetime
from app import create_app
from models import db, Student, Admin, WebsiteSetting
from utils import allowed_file, generate_receipt_pdf

class BCASystemTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.client = self.app.test_client()
        
        # Establish app context and create tables
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_main_routes_status(self):
        """Test if public pages respond successfully."""
        routes = ['/', '/home', '/about', '/faculty', '/courses', '/careers', '/projects', '/gallery', '/downloads', '/contact']
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed to respond with 200 OK.")

    def test_student_model_auth(self):
        """Test password hashing and verification."""
        student = Student(username='test_student', email='test@college.edu')
        student.set_password('mysecretpass123')
        db.session.add(student)
        db.session.commit()

        queried_student = Student.query.filter_by(username='test_student').first()
        self.assertIsNotNone(queried_student)
        self.assertTrue(queried_student.check_password('mysecretpass123'))
        self.assertFalse(queried_student.check_password('wrongpass'))

    def test_file_uploader_validations(self):
        """Test allowed extension checker."""
        self.assertTrue(allowed_file('myphoto.png', 'images'))
        self.assertTrue(allowed_file('signature.jpg', 'images'))
        self.assertTrue(allowed_file('resume.pdf', 'documents'))
        self.assertFalse(allowed_file('hack.exe', 'documents'))
        self.assertFalse(allowed_file('report.docx', 'images'))

    def test_pdf_invoice_generation(self):
        """Test if ReportLab generates the PDF receipt file correctly."""
        receipt_num = "ADM2026TEST01"
        pdf_path = generate_receipt_pdf(
            receipt_number=receipt_num,
            payer_name="Test Student",
            item_name="BCA Testing Fee",
            amount=500.00,
            payment_method="UPI Checkout",
            transaction_id="TXNTEST9999",
            payment_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        # Verify file is created in workspace
        full_pdf_path = os.path.join(os.path.dirname(self.app.config['UPLOAD_FOLDER']), pdf_path)
        self.assertTrue(os.path.exists(full_pdf_path), "PDF invoice receipt file was not created.")
        
        # Clean up PDF file
        if os.path.exists(full_pdf_path):
            os.remove(full_pdf_path)

    def test_admin_crud_flows(self):
        """Test Admin CRUD routes for Syllabus, Careers, and Projects."""
        # 1. Create a test admin user
        admin = Admin(username='test_admin', email='test_admin@college.edu')
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()

        # Log in
        login_resp = self.client.post('/admin/login', data={
            'username': 'test_admin',
            'password': 'adminpass123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome Admin test_admin!', login_resp.data)

        # A. Courses (Syllabus) CRUD
        # Create
        add_course_resp = self.client.post('/admin/courses', data={
            'code': 'BCA999',
            'name': 'Test Devops Course',
            'semester': 6,
            'credits': 4,
            'outcomes': 'Mastering testing and CD'
        }, follow_redirects=True)
        self.assertIn(b'Course added successfully!', add_course_resp.data)

        # Edit
        edit_course_resp = self.client.post('/admin/courses/edit/1', data={
            'code': 'BCA999',
            'name': 'Test DevOps Edited',
            'semester': 6,
            'credits': 5,
            'outcomes': 'Mastering testing and CD with edits'
        }, follow_redirects=True)
        self.assertIn(b'Course updated successfully!', edit_course_resp.data)

        # B. Careers CRUD
        # Create Opportunity
        add_opp_resp = self.client.post('/admin/careers', data={
            'action_type': 'opportunity',
            'title': 'Test QA Automation Engineer',
            'demand': 'Very High',
            'description': 'Responsible for automation scripting'
        }, follow_redirects=True)
        self.assertIn(b'Career opportunity added!', add_opp_resp.data)

        # Edit Opportunity
        edit_opp_resp = self.client.post('/admin/careers/opportunity/edit/1', data={
            'title': 'Test QA Automation Edited',
            'demand': 'Critical',
            'description': 'Responsible for automation scripting and testing'
        }, follow_redirects=True)
        self.assertIn(b'Career opportunity updated!', edit_opp_resp.data)

        # Create Higher Education pg Program
        add_edu_resp = self.client.post('/admin/careers', data={
            'action_type': 'education',
            'name': 'Test MBA in CS',
            'duration': '2 Years',
            'description': 'Focus on tech leadership'
        }, follow_redirects=True)
        self.assertIn(b'Higher education program added!', add_edu_resp.data)

        # Edit Higher Education
        edit_edu_resp = self.client.post('/admin/careers/education/edit/1', data={
            'name': 'Test MBA in CS Edited',
            'duration': '1.5 Years',
            'description': 'Focus on tech leadership edited'
        }, follow_redirects=True)
        self.assertIn(b'Higher education program updated!', edit_edu_resp.data)

        # C. Student Projects CRUD
        # Create
        add_proj_resp = self.client.post('/admin/projects', data={
            'title': 'Test Smart Attendance System',
            'tech': 'Python, SQLite',
            'description': 'A python program for QR attendance',
            'github_url': 'https://github.com/test/attendance'
        }, follow_redirects=True)
        self.assertIn(b'Student project registered successfully!', add_proj_resp.data)

        # Edit
        edit_proj_resp = self.client.post('/admin/projects/edit/1', data={
            'title': 'Test Smart Attendance Edited',
            'tech': 'Python, SQLite, Flask',
            'description': 'A python program for QR attendance edited',
            'github_url': 'https://github.com/test/attendance-edit'
        }, follow_redirects=True)
        self.assertIn(b'Student project updated successfully!', edit_proj_resp.data)

        # Delete operations
        del_course_resp = self.client.post('/admin/courses/delete/1', follow_redirects=True)
        self.assertIn(b'Course deleted successfully!', del_course_resp.data)

        del_opp_resp = self.client.post('/admin/careers/opportunity/delete/1', follow_redirects=True)
        self.assertIn(b'Career opportunity deleted.', del_opp_resp.data)

        del_edu_resp = self.client.post('/admin/careers/education/delete/1', follow_redirects=True)
        self.assertIn(b'Higher education program deleted.', del_edu_resp.data)

        del_proj_resp = self.client.post('/admin/projects/delete/1', follow_redirects=True)
        self.assertIn(b'Student project record deleted.', del_proj_resp.data)

if __name__ == '__main__':
    unittest.main()
