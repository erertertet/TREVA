import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
model_dir = parent_dir / 'model'
sys.path.append(str(model_dir))

from utils import *
from sliding_window import *
