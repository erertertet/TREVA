import sys
import os
# Get the parent directory path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from model import utils
from model import sliding_window
