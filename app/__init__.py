from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.models import db 
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

load_dotenv()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config.from_object(Config)
    csrf = CSRFProtect(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.student import student_bp
    from app.routes.admin import admin_bp 
    from app.routes.main import main_bp
    
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)

    @app.route('/')
    def home():
        return "<h1>PUPBC Synapse is Running!</h1><a href='/student/register'>Go to Registration</a>"

    with app.app_context():
        db.create_all()

    return app

