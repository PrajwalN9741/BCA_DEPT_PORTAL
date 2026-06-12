import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from models import db, Admin, Student

def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    if config_override:
        app.config.update(config_override)
        
    # Ensure the instance folder exists before initializing the DB
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize SQLAlchemy database
    db.init_app(app)
    
    # Configure Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'student.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None
        parts = user_id.split('_', 1)
        if len(parts) == 2:
            role_type, raw_id = parts
            try:
                pk = int(raw_id)
                if role_type == 'admin':
                    return Admin.query.get(pk)
                elif role_type == 'student':
                    return Student.query.get(pk)
            except ValueError:
                return None
        return None

    # Register Blueprints
    from routes.main import main_bp
    from routes.student import student_bp
    from routes.admission import admission_bp
    from routes.event import event_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admission_bp, url_prefix='/admission')
    app.register_blueprint(event_bp, url_prefix='/event')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Custom Context Processor to inject dynamic homepage/about configurations
    @app.context_processor
    def inject_settings():
        from models import WebsiteSetting
        settings_dict = {}
        try:
            # We fetch all settings from DB if the table exists
            settings_list = WebsiteSetting.query.all()
            for s in settings_list:
                settings_dict[s.key] = s.value
        except Exception:
            # Fallback if DB table is not yet initialized
            pass
        return dict(site_settings=settings_dict)

    # Route to verify receipt QR codes
    @app.route('/verify-receipt/<receipt_number>')
    def verify_receipt(receipt_number):
        from models import Admission, EventRegistration
        # Check admissions first
        adm = Admission.query.filter_by(receipt_number=receipt_number).first()
        if adm:
            return render_template('receipt_verification.html', type='Admission', data=adm)
            
        # Check event registrations next
        evt_reg = EventRegistration.query.filter_by(receipt_number=receipt_number).first()
        if evt_reg:
            return render_template('receipt_verification.html', type='Event Registration', data=evt_reg)
            
        flash("Receipt number not found or invalid QR code verification.", "danger")
        return redirect(url_for('main.home'))
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Ensure database file exists
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
