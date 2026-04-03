from app import create_app, db
from app.models import * # Ensure all models have been imported.

# Create an application instance
app = create_app()

# Execute database operations within the application context
# with app.app_context():
#     # Remove all migration logic and directly create or update database tables.
#     db.drop_all() 
#     db.create_all()
#     print("Database tables created or updated successfully.")
