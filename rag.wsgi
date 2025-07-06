import sys
import os

# Add your project directory to the Python path
# Replace 'myflaskapp' with the actual name of your Flask app directory
project_home = u'/var/www/usarag'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate the virtual environment
# Replace 'venv' with the actual name of your virtual environment directory
activate_this = os.path.join(project_home, '.venv/bin/activate')
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

# Import your Flask application instance
# Replace 'app' with the actual name of your Flask application instance
# (e.g., if your app is in 'my_app.py' and the instance is 'app', use 'from my_app import app')
from rag import app as application # Assuming your Flask app instance is named 'app' in 'app.py'
