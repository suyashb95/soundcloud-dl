import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from config import client_id
except ImportError:
    print('API key is not set. Please set it using the --set-api-key option')
    sys.exit(0)