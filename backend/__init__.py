from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from flask_cors import CORS
from backend.config import Config
from backend.models import db


def create_app():
    # Project ke root folder ka path nikalo
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # ... baki ka code waisa hi rahega ...
    
    # Extensions Initialize
    CORS(app)
    JWTManager(app)
    db.init_app(app)

    
    # 1. Sabse pehle MAp ko explicitly force-import karo taaki tables register ho jayein
    from backend import models
    
    # 2. Uske baad routes ko register karo
    
    # 3. App context ke andar fresh database Tables banao
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
        # Programmatic Admin setup (If not exists)
        from backend.models import User
        from werkzeug.security import generate_password_hash
        admin_exists = User.query.filter_by(role='Admin').first()
        if not admin_exists:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='Admin',
                contact_details='admin@trekking.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("Programmatic Admin account created successfully! (User: admin / Pass: admin123)")
            
    return app