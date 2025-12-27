import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# --- Database Configuration ---
# All credentials now come from environment variables
db_server = os.getenv('DB_SERVER')  # Default matches your service name
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')  # No default - required from environment
db_name = os.getenv('DB_NAME')

# --- Globally initialize extensions ---
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Validate that required environment variables are set
    if not db_password:
        raise ValueError("DB_PASSWORD environment variable is required")

    # --- Database Connection String ---
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mssql+pyodbc://{db_user}:{db_password}@{db_server}:1433/{db_name}?'
        f'driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- SECRET KEY ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # --- Connect the extensions to the app ---
    db.init_app(app)
    migrate.init_app(app, db)

    # --- Import models ---
    with app.app_context():
        import models

    # --- Import and register routes ---
    from routes import register_routes
    register_routes(app, db)

    with app.app_context():
        try:
            print("🔄 Setting up database tables...")
            print(f"🔗 Connecting to database: {db_server}/{db_name} as {db_user}")

            # Create all tables
            db.create_all()

            # Create admin user if it doesn't exist
            from models import User
            if not User.query.filter_by(username='admin').first():
                admin_user = User(username='admin', email='admin@library.com', role='admin')
                admin_user.set_password('password123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created successfully!")
                print("   Username: admin")
                print("   Password: password123")
            else:
                print("ℹ️ Admin user already exists")

            print("✅ Database setup completed!")

        except Exception as e:
            print(f"❌ Database error: {e}")
            db.session.rollback()
            # Re-raise the exception to see the full traceback
            raise

    return app
