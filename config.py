import os

class Config:
    # Basic settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bca_dept_secure_secret_key_12984712')
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database setting - Default SQLite
    db_path = os.path.join(BASE_DIR, 'instance', 'bca_dept.db').replace('\\', '/')
    db_uri = os.environ.get('DATABASE_URL', f"sqlite:///{db_path}")
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload limits - 16 MB max upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Upload folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    
    # Specific upload sub-folders
    FACULTY_FOLDER = os.path.join(UPLOAD_FOLDER, 'faculty')
    DOCUMENTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'documents')
    EVENTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'events')
    GALLERY_FOLDER = os.path.join(UPLOAD_FOLDER, 'gallery')
    DOWNLOADS_FOLDER = os.path.join(UPLOAD_FOLDER, 'downloads')
    RECEIPTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'receipts')
    
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {
        'images': {'png', 'jpg', 'jpeg', 'gif'},
        'documents': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'},
        'videos': {'mp4', 'mov', 'avi'}
    }
