# myapp.wsgi
import sys
sys.path.insert(0, '/var/www/usarag/public') # Adjust path
from myapp import app as application # Assuming your Flask app is named 'app' in 'myapp.py'
