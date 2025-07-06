#!/usr/bin/python3
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, '/var/www/usarag')

# Activate virtual environment
activate_this = '/var/www/usarag/.venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))
else:
    # Alternative method if activate_this.py doesn't exist
    sys.path.insert(0, '/var/www/usarag/.venv/lib/python3.12/site-packages')

# Import your Flask application
from rag import app as application

if __name__ == "__main__":
    application.run(debug=True)