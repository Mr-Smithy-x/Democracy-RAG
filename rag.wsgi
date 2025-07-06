#!/var/www/usarag/.venv/bin/python3
import sys
import os

# Add your project directory to the Python path
# Replace 'myflaskapp' with the actual name of your Flask app directory
project_home = u'/var/www/usarag'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# --- START: Updated Virtual Environment Activation ---
# Determine the Python version in the virtual environment
# This helps in locating the correct site-packages directory
python_version = 'python' + sys.version[:3] # e.g., 'python3.8' or 'python3.9'

# Path to the site-packages directory within your virtual environment
# Replace 'venv' with the actual name of your virtual environment directory
site_packages_path = os.path.join(project_home, '.venv/lib', python_version, 'site-packages')

# Add the site-packages directory to the Python path
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)
# --- END: Updated Virtual Environment Activation ---

# Import your Flask application instance
# Replace 'app' with the actual name of your Flask application instance
# (e.g., if your app is in 'my_app.py' and the instance is 'app', use 'from my_app import app')
from rag import app as application # Assuming your Flask app instance is named 'app' in 'app.py'
