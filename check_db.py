import os
import sqlite3
from app import create_app
from models import db, News

app = create_app()
with app.app_context():
    print("SQLALCHEMY_DATABASE_URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("Database exists:", os.path.exists(os.path.join(app.config['BASE_DIR'], 'instance', 'bca_dept.db')))
    
    # Try connecting directly via sqlite3 to check tables
    db_path = os.path.join(app.config['BASE_DIR'], 'instance', 'bca_dept.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", tables)
        conn.close()
    else:
        print("Database file not found at expected path.")
