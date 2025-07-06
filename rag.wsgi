#!/var/www/usarag/.venv/bin/python3
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, '/var/www/usarag')

# Add virtual environment's site-packages to Python path
venv_site_packages = '/var/www/usarag/.venv/lib/python3.12/site-packages'
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Set the virtual environment path
os.environ['VIRTUAL_ENV'] = '/var/www/usarag/.venv'

# Import your Flask application
from rag import app as application

if __name__ == "__main__":
    application.run()